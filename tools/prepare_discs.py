"""Prepare local original or checksum-validated English discs. Never modifies inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import wave

SYNC = bytes.fromhex('00ffffffffffffffffffff00')


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def extract_mode1(source: Path, destination: Path) -> int:
    size = source.stat().st_size
    if not size or size % 2352:
        raise ValueError('MODE1 input must contain complete 2352-byte sectors')
    # Exclusive creation is deliberately outside cleanup: existing files stay untouched.
    out = destination.open('xb')
    try:
        with source.open('rb') as inp, out:
            for index in range(size // 2352):
                raw = inp.read(2352)
                if len(raw) != 2352 or raw[:12] != SYNC or raw[15] != 1:
                    raise ValueError(f'Invalid MODE1 sector {index}')
                out.write(raw[16:2064])
    except BaseException:
        out.close()
        destination.unlink(missing_ok=True)
        raise
    return size // 2352


def parse_two_track_cue(cue: Path) -> tuple[Path, Path, int]:
    """Read the supplied two-file Redump layout; reject unsupported ambiguity."""
    files = []
    tracks = []
    audio_start = None
    for raw in cue.read_text(encoding='utf-8-sig').splitlines():
        line = raw.strip()
        match = re.fullmatch(r'FILE "([^"]+)" BINARY', line, re.I)
        if match:
            path = (cue.parent / match[1]).resolve()
            if not path.is_relative_to(cue.parent.resolve()):
                raise ValueError('CUE file must remain inside its directory')
            if not path.is_file():
                raise FileNotFoundError(path)
            files.append(path)
            continue
        match = re.fullmatch(r'TRACK (\d+) (\S+)', line, re.I)
        if match:
            tracks.append((int(match[1]), match[2].upper(), len(files)))
            continue
        match = re.fullmatch(r'INDEX 01 (\d+):(\d+):(\d+)', line, re.I)
        if match and tracks:
            minutes, seconds, frames = map(int, match.groups())
            if seconds >= 60 or frames >= 75:
                raise ValueError('Invalid CUE index')
            index = (minutes * 60 + seconds) * 75 + frames
            if tracks[-1][0] == 1 and index:
                raise ValueError('Data track must begin at file offset zero')
            if tracks[-1][0] == 2:
                audio_start = index
        elif line.upper().startswith(('PREGAP', 'POSTGAP')):
            raise ValueError('Only the supplied embedded-pregap input CUE is supported')
    if len(files) != 2 or tracks != [(1, 'MODE1/2352', 1), (2, 'AUDIO', 2)] or audio_start is None:
        raise ValueError('Expected two-file MODE1/2352 + AUDIO CUE')
    return files[0], files[1], audio_start


def write_audio_wav(source: Path, destination: Path, pregap: int) -> None:
    size = source.stat().st_size
    if size % 2352 or pregap < 0 or pregap * 2352 >= size:
        raise ValueError('Invalid audio sector count or pregap')
    # Saturn CD audio sectors store signed 16-bit little-endian stereo PCM.
    with source.open('rb') as inp, destination.open('xb') as out:
        inp.seek(pregap * 2352)
        with wave.open(out, 'wb') as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(44100)
            for block in iter(lambda: inp.read(1024 * 2352), b''):
                wav.writeframesraw(block)


def prepare_disc(cue: Path, patch: Path, output: Path, xdelta: Path) -> dict:
    if output.exists():
        raise FileExistsError(f'Refusing to overwrite {output}')
    cue, patch, output, xdelta = (p.resolve() for p in (cue, patch, output, xdelta))
    data, audio, pregap = parse_two_track_cue(cue)
    for p in (patch, xdelta):
        if not p.is_file():
            raise FileNotFoundError(p)
    template = patch.with_suffix('.cue')
    if not template.is_file():
        raise FileNotFoundError(template)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Temporaries share a volume with output so final directory publication is atomic.
    with tempfile.TemporaryDirectory(prefix='.prepare-', dir=output.parent) as scratch:
        temporary = Path(scratch)
        original = temporary / 'original.iso'
        print(f'Extracting {cue.name}', flush=True)
        count = extract_mode1(data, original)
        prepared = temporary / 'prepared'
        prepared.mkdir()
        patched = prepared / 'Track 01.iso'
        print('Applying xdelta with output checksums enabled', flush=True)
        result = subprocess.run([str(xdelta), '-d', '-s', str(original), str(patch), str(patched)],
                                capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(f'xdelta rejected the image: {result.stderr.strip()}')
        if patched.stat().st_size % 2048:
            raise ValueError('Patched image is not sector aligned')
        print('Preserving audio and writing manifest', flush=True)
        write_audio_wav(audio, prepared / 'Track 02.wav', pregap)
        shutil.copyfile(template, prepared / 'game.cue')
        with patched.open('rb') as f:
            header = f.read(512)
        if header[:16] != b'SEGA SEGASATURN ':
            raise ValueError('Patched output has no Saturn header')
        manifest = {
            'schema': 1, 'translation': 'supplied-v2_1',
            'inputs': {p.name: sha256(p) for p in (cue, data, audio, patch, template)},
            'input_data_sectors': count,
            'output_data_sectors': patched.stat().st_size // 2048,
            'removed_embedded_audio_pregap_sectors': pregap,
            'product': header[32:42].decode('ascii').strip(),
            'version': header[42:48].decode('ascii').strip(),
            'disc': header[56:64].decode('ascii').strip(),
            'ra_hash': hashlib.md5(header).hexdigest(),
            'xdelta_sha256': sha256(xdelta),
            'xdelta_output_checksums_verified': True,
            'outputs': {p.name: sha256(p) for p in prepared.iterdir()},
        }
        (prepared / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        # On Windows os.rename fails rather than replacing an existing destination directory.
        if output.exists():
            raise FileExistsError(output)
        os.rename(prepared, output)
        return manifest


def prepare_original(cue: Path, output: Path) -> dict:
    """An unpatched profile with the original data and embedded audio-gap timing."""
    if output.exists():
        raise FileExistsError(f'Refusing to overwrite {output}')
    cue, output = cue.resolve(), output.resolve()
    data, audio, pregap = parse_two_track_cue(cue)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.prepare-', dir=output.parent) as scratch:
        prepared = Path(scratch) / 'prepared'
        prepared.mkdir()
        image = prepared / 'Track 01.iso'
        count = extract_mode1(data, image)
        with image.open('rb') as f:
            header = f.read(512)
        if header[:16] != b'SEGA SEGASATURN ':
            raise ValueError('Original output has no Saturn header')
        write_audio_wav(audio, prepared / 'Track 02.wav', pregap)
        gap = f'{pregap // 4500:02}:{pregap // 75 % 60:02}:{pregap % 75:02}'
        (prepared / 'game.cue').write_text(
            'FILE "Track 01.iso" BINARY\n  TRACK 01 MODE1/2048\n    INDEX 01 00:00:00\n'
            f'FILE "Track 02.wav" WAVE\n  TRACK 02 AUDIO\n    PREGAP {gap}\n    INDEX 01 00:00:00\n',
            encoding='utf-8')
        manifest = {
            'schema': 1, 'translation': 'none',
            'inputs': {p.name: sha256(p) for p in (cue, data, audio)},
            'input_data_sectors': count, 'output_data_sectors': count,
            'removed_embedded_audio_pregap_sectors': pregap,
            'product': header[32:42].decode('ascii').strip(),
            'version': header[42:48].decode('ascii').strip(),
            'disc': header[56:64].decode('ascii').strip(),
            'ra_hash': hashlib.md5(header).hexdigest(),
            'outputs': {p.name: sha256(p) for p in prepared.iterdir()},
        }
        (prepared / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        if output.exists():
            raise FileExistsError(output)
        os.rename(prepared, output)
        return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cue', type=Path, required=True)
    variant = parser.add_mutually_exclusive_group(required=True)
    variant.add_argument('--patch', type=Path)
    variant.add_argument('--original', action='store_true', help='prepare unpatched Japanese data')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--xdelta', type=Path)
    args = parser.parse_args()
    if args.original:
        manifest = prepare_original(args.cue, args.output)
    else:
        if not args.xdelta:
            parser.error('--xdelta is required with --patch')
        manifest = prepare_disc(args.cue, args.patch, args.output, args.xdelta)
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
