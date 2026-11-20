"""Prepare the game on the player's PC from their own files; shipped as preparar-juego.exe.

The player supplies only their own files: the two Sakura Taisen Saturn discs and, optionally, the PC
edition for the HD mod. Everything else is in the release.

  discs   each disc is identified by the SHA-256 of its data track, whatever the container:
            .cue with its tracks (one or two files), a single .bin/.img/.mdf, a plain .iso,
            a folder or a .zip holding any of those
          the original Japanese disc -> "Ingles v0.1 Taisen" (xdelta) -> "Espanol v0.1 Taisen" (xdelta);
          a disc already patched with the English translation v2.1 is recognized and used as the English
          base as it is. Every step is checked by SHA-256. Output: <program>/game/discN and discN-es.
  hd      the PC edition as a disc image (read in place, no mounting), a folder with its cabinets, or an
          installed/extracted game folder. Only the 19 decorative backgrounds and the portrait archive
          are read; the prepared pack goes to <program>/hd-resources and no original file is kept.
  profile <home>/launcher.ini points at the disc of the chosen language.

Nothing is rebuilt needlessly: a prepared disc whose receipt matches this release is kept, the Spanish disc
is rebuilt from the prepared English one when only the Spanish layer changed, and the HD pack is kept
while it matches the release's recipe.

  preparar-juego.exe scan --folder DIR
  preparar-juego.exe prepare [--rom PATH]... [--folder DIR] [--language es|en] [--force]
  preparar-juego.exe language --language es|en
  preparar-juego.exe info
  preparar-juego.exe frontend [--rom PATH]... [--language es|en] [--fullscreen] [--widescreen off|16:9|fit]

`frontend` is what SaturnTaisen.exe runs for a frontend's flags (RecompLauncher / Easy Setup).
Inputs are only read. Progress lines start with "PROGRESO <percent> "; the last line is "OK ..." or
"ERROR <message>".
"""
from __future__ import annotations

import argparse
import configparser
import hashlib
import io
import json
import mmap
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import wave
import zipfile
from pathlib import Path

FROZEN = getattr(sys, 'frozen', False)
PROGRAM = Path(sys.executable).resolve().parent if FROZEN else Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_sdk import files as iso_files  # noqa: E402

CUE = ('FILE "Track 01.iso" BINARY\n  TRACK 01 MODE1/2048\n      INDEX 01 00:00:00\n      POSTGAP 00:02:00\n'
       'FILE "Track 02.wav" WAVE\n  TRACK 02 AUDIO\n    PREGAP 00:02:00\n    INDEX 01 00:00:00\n')
LANGUAGES = {'en': '', 'es': '-es'}
# Japanese is the player's original disc as it is (no layer). It can only be kept when the original was given
# (not an already-translated disc), so it is optional: preparation never fails for want of it.
OPTIONAL_LANGUAGES = {'ja': '-ja'}
ALL_LANGUAGES = {**LANGUAGES, **OPTIONAL_LANGUAGES}
LAYERS = {'en': 'english', 'es': 'spanish'}
PALETTE_HASH = 12829369761668915482  # CRAM bank the reviewed portrait identities were matched under
SYNC = bytes.fromhex('00ffffffffffffffffffff00')
SATURN = b'SEGA SEGASATURN '
PRODUCT = 'GS-9037'
NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
IMAGE_SUFFIXES = ('.cue', '.iso', '.bin', '.img', '.mdf')
CABINETS = ('DATA1.CAB', 'DATA1.HDR', 'DATA2.CAB')
_recomplauncher_progress = False


class SetupError(Exception):
    pass


def say(percent: int, message: str) -> None:
    if _recomplauncher_progress:
        print(f'progress {percent / 100:.2f} {message}', flush=True)
    else:
        print(f'PROGRESO {percent} {message}', flush=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def fnv64(data: bytes) -> int:
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return value


def run(command, extra_env=None, **kwargs):
    env = os.environ.copy()
    env.update(extra_env or {})
    bundled = getattr(sys, '_MEIPASS', None)
    if bundled:  # the frozen helper carries the C runtime the bundled tools were built against
        env['PATH'] = bundled + os.pathsep + env.get('PATH', '')
    return subprocess.run([str(part) for part in command], capture_output=True, creationflags=NO_WINDOW, env=env,
                          **kwargs)


def discs_folder(program: Path) -> Path:
    """The player's folder: roms/ at the release root (the program is in data/), or the earlier discos/."""
    for folder in (program.parent / 'roms', program / 'roms', program.parent / 'discos', program / 'discos'):
        if folder.is_dir():
            return folder
    return program.parent / 'roms'


def launch_manifest(program: Path) -> Path:
    """recomp-launcher.json sits at the release root, beside the only visible executable."""
    for folder in (program, program.parent):
        if (folder / 'recomp-launcher.json').is_file():
            return folder / 'recomp-launcher.json'
    return program / 'recomp-launcher.json'


def default_home(program: Path) -> Path:
    """The player's folder as the launcher resolves it in portable mode (the launcher passes --home itself).

    SATURN_TAISEN_FIRST_HOME wins; a profile kept directly in user/ by an earlier release is still used;
    otherwise it is user/SaturnTaisen, where the launcher keeps it beside portable.txt."""
    env = os.environ.get('SATURN_TAISEN_FIRST_HOME')
    if env:
        return Path(env).resolve()
    if (program / 'user' / 'launcher.ini').is_file():
        return program / 'user'
    return program / 'user' / 'SaturnTaisen'


class Paths:
    """Where the release keeps its parts; every one can be overridden for tests and the source tree."""

    def __init__(self, args):
        program = Path(args.program).resolve() if args.program else PROGRAM
        self.program = program
        local = program / 'local'

        def pick(given, *candidates):
            if given:
                return Path(given).resolve()
            for candidate in candidates:
                if candidate.exists():
                    return candidate
            return candidates[0]

        self.patches = pick(args.patches, program / 'parches')
        self.xdelta = pick(args.xdelta, program / 'herramientas/xdelta3.exe',
                           local / 'tools/xdelta3-3.2.2/xdelta3-3.2.2-windows-x86_64/xdelta3.exe')
        self.unshield = pick(args.unshield, program / 'herramientas/unshield.exe',
                             local / 'build/unshield/src/unshield.exe')
        self.runtime = pick(args.runtime, program / 'sakura.exe', local / 'build/sakura/sakura.exe')
        self.recipe = pick(args.recipe, program / 'config/hd-portrait-recipe.json')
        self.provenance = pick(args.provenance, program / 'art/pc-backgrounds/provenance.json',
                               program / 'assets/generated/pc-backgrounds/provenance.json')
        self.game = Path(args.output).resolve() if args.output else program / 'game'
        self.hd = Path(args.hd_output).resolve() if args.hd_output else program / 'hd-resources'
        self.home = Path(args.home).resolve() if args.home else default_home(program)


# ---- reading the player's discs ---------------------------------------------------------------------

def saturn_header(track: Path) -> bytes:
    try:
        with track.open('rb') as f:
            head = f.read(16 + 256)
    except OSError:
        return b''
    for offset in (0, 16):
        if head[offset:offset + 16] == SATURN:
            return head[offset:offset + 256]
    return b''


def cue_files(cue: Path) -> list[Path]:
    """The files a .cue names, in order, when they are beside it."""
    try:
        text = cue.read_text(encoding='utf-8-sig', errors='replace')
    except OSError:
        return []
    found = []
    for name in re.findall(r'^\s*FILE\s+"([^"]+)"', text, re.I | re.M):
        file = cue.parent / Path(name).name
        if file.is_file():
            found.append(file)
    return found


def cue_audio_index(cue: Path) -> int | None:
    """Sectors to skip in the second file of a two-file .cue (its INDEX 01), or None."""
    try:
        text = cue.read_text(encoding='utf-8-sig', errors='replace')
    except OSError:
        return None
    parts = re.split(r'^\s*FILE\s+', text, flags=re.I | re.M)
    if len(parts) < 3:
        return None
    match = re.search(r'INDEX\s+01\s+(\d+):(\d+):(\d+)', parts[2], re.I)
    if not match:
        return 0
    minutes, seconds, frames = map(int, match.groups())
    return (minutes * 60 + seconds) * 75 + frames


class Disc:
    """One of the player's Saturn discs, whatever its container. Only read."""

    def __init__(self, path: Path):
        self.given = path
        self.audio: Path | None = None
        self.audio_skip = 0
        files = cue_files(path) if path.suffix.lower() == '.cue' else [path]
        if not files:
            raise SetupError(f'{path.name}: sus pistas no están junto al archivo .cue.')
        self.data = files[0]
        if len(files) > 1:
            self.audio = files[1]
            self.audio_skip = cue_audio_index(path) or 0
        header = saturn_header(self.data)
        if not header:
            raise SetupError(f'{path.name} no es un disco de Sega Saturn.')
        with self.data.open('rb') as f:
            self.raw = f.read(12) == SYNC
        self.product = header[0x20:0x2A].decode('ascii', 'replace').strip()
        self.version = header[0x2A:0x30].decode('ascii', 'replace').strip()
        self.number = int(chr(header[0x3B])) if chr(header[0x3B]) in '12' else 0

    def extract(self, target: Path) -> int:
        """Write the data track as 2048-byte sectors; returns how many sectors of the file it used."""
        if not self.raw:
            shutil.copyfile(self.data, target)
            return target.stat().st_size // 2048
        count = 0
        with self.data.open('rb') as inp, target.open('wb') as out:
            while True:
                sector = inp.read(2352)
                if len(sector) < 2352 or sector[:12] != SYNC or sector[15] != 1:
                    break
                out.write(sector[16:2064])
                count += 1
        return count

    def write_audio(self, target: Path, data_sectors: int, expected_bytes: int) -> bool:
        """The audio track as a WAV; False when the disc image has none (the caller writes silence)."""
        if self.audio and self.audio.suffix.lower() == '.wav':
            shutil.copyfile(self.audio, target)
            return True
        frames = expected_bytes - 44
        if self.audio:
            source, start = self.audio, self.audio_skip * 2352
        elif self.raw and self.data.stat().st_size >= data_sectors * 2352 + frames:
            source, start = self.data, self.data.stat().st_size - frames  # one file: the audio is its tail
        else:
            return False
        if source.stat().st_size - start <= 0:
            return False
        with source.open('rb') as inp, target.open('wb') as out, wave.open(out, 'wb') as wav:
            inp.seek(start)
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(44100)
            for block in iter(lambda: inp.read(1024 * 2352), b''):
                wav.writeframesraw(block)
        return True


def describe(path: Path) -> dict | None:
    """What a file is among the player's Saturn discs, without hashing it; None for anything else."""
    try:
        disc = Disc(path)
    except (SetupError, OSError, ValueError):
        return None
    if disc.product != PRODUCT or not disc.number:
        return None
    return {'path': str(path), 'disc': disc.number, 'version': disc.version}


def write_silence(target: Path, total_bytes: int) -> None:
    with target.open('wb') as out, wave.open(out, 'wb') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        wav.writeframesraw(bytes(max(0, total_bytes - 44)))


# ---- the PC edition ----------------------------------------------------------------------------------

class Image:
    """A data CD image read in place: plain 2048-byte sectors or raw 2352-byte sectors (mode 1 or 2)."""

    def __init__(self, path: Path):
        self.stream = path.open('rb')
        self.sector, self.skip = 0, 0
        for sector, skip in ((2048, 0), (2352, 16), (2352, 24), (2336, 8)):
            self.stream.seek(16 * sector + skip)
            if self.stream.read(6) == b'\x01CD001':
                self.sector, self.skip = sector, skip
                break
        if not self.sector:
            self.stream.close()
            raise SetupError('La imagen de PC no es un disco de datos legible (.mdf o .iso).')

    def read(self, lba: int, size: int) -> bytes:
        if not self.skip:
            self.stream.seek(lba * 2048)
            return self.stream.read(size)
        out = bytearray()
        while len(out) < size:
            self.stream.seek(lba * self.sector + self.skip)
            out += self.stream.read(2048)
            lba += 1
        return bytes(out[:size])

    def root(self) -> dict:
        volume = self.read(16, 2048)
        lba, size = struct.unpack_from('<I', volume, 158)[0], struct.unpack_from('<I', volume, 166)[0]
        return self.directory(lba, size)

    def folder(self, name: str) -> dict:
        """The entries of a folder at the root of the disc (e.g. MOVIE), or {} when there is none."""
        entry = self.root().get(name.upper())
        return self.directory(*entry) if entry else {}

    def directory(self, lba: int, size: int) -> dict:
        if size > 1024 * 1024:
            raise SetupError('Directorio de la imagen de PC no admitido.')
        directory, at, found = self.read(lba, size), 0, {}
        while at < len(directory):
            length = directory[at]
            if not length:
                at = (at // 2048 + 1) * 2048
                continue
            name = directory[at + 33:at + 33 + directory[at + 32]].decode('ascii', 'replace').split(';')[0]
            if name not in ('\x00', '\x01'):  # (the folder itself and its parent)
                found[name.upper()] = (struct.unpack_from('<I', directory, at + 2)[0],
                                       struct.unpack_from('<I', directory, at + 10)[0])
            at += length
        return found

    def copy(self, lba: int, size: int, target: Path) -> None:
        with target.open('wb') as out:
            left = size
            while left:
                block = self.read(lba, min(left, 2048 * 2048))
                if not block:
                    raise SetupError('La imagen de PC está incompleta.')
                out.write(block)
                lba += len(block) // 2048
                left -= len(block)

    def close(self) -> None:
        self.stream.close()


def is_pc_image(path: Path) -> bool:
    try:
        image = Image(path)
    except (OSError, SetupError):
        return False
    try:
        return all(name in image.root() for name in CABINETS)
    except (OSError, SetupError, struct.error):
        return False
    finally:
        image.close()


def child(folder: Path, name: str) -> Path | None:
    """A direct child by name, ignoring case."""
    try:
        for entry in folder.iterdir():
            if entry.name.upper() == name.upper():
                return entry
    except OSError:
        pass
    return None


def pc_folder_kind(folder: Path) -> str | None:
    """'cabinets' for a folder with the disc's cabinets, 'game' for an installed or extracted game."""
    if all(child(folder, name) for name in CABINETS):
        return 'cabinets'
    game = child(folder, 'SAKURA1')
    if game and child(game, 'WALL') and (system := child(game, 'SYSTEM')) and child(system, 'KAO.SPR'):
        return 'game'
    return None


def describe_pc(path: Path) -> str | None:
    if path.is_dir():
        return pc_folder_kind(path)
    if path.suffix.lower() in ('.mdf', '.iso', '.img', '.bin') and path.stat().st_size > 600 * 1024 * 1024:
        return 'image' if is_pc_image(path) else None
    return None


# ---- finding the player's files ---------------------------------------------------------------------

def walk(folder: Path, depth: int = 4, limit: int = 4000):
    """Folders first, then files, a few levels down; never a whole drive's worth."""
    pending, seen = [(folder, 0)], 0
    while pending:
        current, level = pending.pop(0)
        try:
            entries = sorted(current.iterdir(), key=lambda entry: entry.name.lower())
        except OSError:
            continue
        yield current, True
        for entry in entries:
            seen += 1
            if seen > limit:
                return
            if entry.is_dir():
                if level < depth and not entry.name.startswith(('.', '$')):
                    pending.append((entry, level + 1))
            elif entry.is_file():
                yield entry, False


def scan(folder: Path) -> dict:
    """The player's files in a folder: every Saturn disc candidate per disc number, the PC edition, archives."""
    found = {'discs': {}, 'pc': None, 'archives': []}
    named = set()
    for entry, is_folder in walk(folder):
        if is_folder:
            if found['pc'] is None and pc_folder_kind(entry):
                found['pc'] = str(entry)
            continue
        suffix = entry.suffix.lower()
        if suffix == '.zip':
            found['archives'].append(str(entry))
        elif suffix in IMAGE_SUFFIXES:
            if entry in named:
                continue  # a track a .cue already accounted for
            about = describe(entry)
            if about:
                if suffix == '.cue':
                    named.update(cue_files(entry))
                found['discs'].setdefault(str(about['disc']), []).append(about['path'])
            elif found['pc'] is None and suffix != '.cue' and describe_pc(entry):
                found['pc'] = str(entry)
    for number, paths in found['discs'].items():  # a .cue speaks for the tracks it names
        cues = [path for path in paths if path.lower().endswith('.cue')]
        covered = {str(track) for cue in cues for track in cue_files(Path(cue))}
        found['discs'][number] = [path for path in paths if path not in covered]
    return found


def unpack_archives(archives: list[str], work: Path) -> Path | None:
    """Extract the .zip files that hold disc images; returns the folder, or None when there were none."""
    target = None
    for index, name in enumerate(archives):
        try:
            with zipfile.ZipFile(name) as archive:
                wanted = [item for item in archive.infolist()
                          if not item.is_dir() and Path(item.filename).suffix.lower() in IMAGE_SUFFIXES + ('.wav', '.mds')]
                if not wanted or sum(item.file_size for item in wanted) > 4 * 1024 ** 3:
                    continue
                target = target or work / 'zip'
                folder = target / str(index)
                folder.mkdir(parents=True)
                say(1, f'Descomprimiendo {Path(name).name}…')
                for item in wanted:
                    with archive.open(item) as source, (folder / Path(item.filename).name).open('wb') as out:
                        shutil.copyfileobj(source, out, 4 * 1024 * 1024)
        except (OSError, zipfile.BadZipFile):
            continue
    return target


def gather(given: list[Path], work: Path | None = None) -> tuple[dict[int, list[Path]], Path | None]:
    """Disc candidates by number and the PC edition, from files and folders; neighbours fill what is missing."""
    discs: dict[int, list[Path]] = {}
    pc, folders = None, []

    def take(found: dict) -> None:
        nonlocal pc
        for number, paths in found['discs'].items():
            for path in paths:
                if Path(path) not in discs.setdefault(int(number), []):
                    discs[int(number)].append(Path(path))
        if found['pc'] and pc is None:
            pc = Path(found['pc'])
        if found['archives'] and work is not None and len(discs) < 2:
            unpacked = unpack_archives(found['archives'], work)
            if unpacked:
                take(scan(unpacked) | {'archives': []})

    for path in given:
        path = path.resolve()
        if path.is_dir():
            folders.append(path)
            take(scan(path))
            continue
        if not path.is_file():
            raise SetupError(f'No existe el archivo indicado: {path}')
        folders.extend([path.parent, path.parent.parent])
        if path.suffix.lower() == '.zip':
            take({'discs': {}, 'pc': None, 'archives': [str(path)]})
            continue
        about = describe(path)
        if about:
            discs.setdefault(about['disc'], []).insert(0, path)
        elif describe_pc(path):
            pc = path
        else:
            raise SetupError(f'{path.name} no es un disco de Sakura Taisen para Saturn ni la edición de PC.')
    for folder in folders:
        if len(discs) == 2 and pc is not None:
            break
        if folder.is_dir() and folder.parent != folder:  # never a whole drive
            take(scan(folder))
    return discs, pc


# ---- building the prepared discs --------------------------------------------------------------------

def apply_delta(paths: Paths, source: Path, patch: Path, target: Path, expected: str) -> None:
    result = run([paths.xdelta, '-d', '-f', '-s', source, patch, target])
    if result.returncode:
        target.unlink(missing_ok=True)
        raise SetupError(f'No se pudo aplicar {patch.name}: {result.stderr.decode(errors="replace").strip()}')
    if expected and sha256(target) != expected:
        target.unlink(missing_ok=True)
        raise SetupError(f'{patch.name} produjo un resultado distinto del esperado.')


def copy_range(source: Path, offset: int, size: int, target: Path, target_offset: int | None = None) -> None:
    with source.open('rb') as inp, target.open('r+b' if target_offset is not None else 'wb') as out:
        inp.seek(offset)
        if target_offset is not None:
            out.seek(target_offset)
        left = size
        while left:
            block = inp.read(min(left, 4 * 1024 * 1024))
            if not block:
                raise SetupError('Lectura incompleta del disco.')
            out.write(block)
            left -= len(block)


def blank_range(target: Path, offset: int, size: int) -> None:
    with target.open('r+b') as out:
        out.seek(offset)
        zeros, left = bytes(4 * 1024 * 1024), size
        while left:
            out.write(zeros[:min(left, len(zeros))])
            left -= min(left, len(zeros))


def accepted(layer: dict) -> dict[str, bool]:
    """The data-track hashes a prepared disc of this layer may have: hash -> has subtitled videos."""
    hashes = {layer['output_sha256']: False}
    if layer.get('output_subtitled_sha256'):
        hashes[layer['output_subtitled_sha256']] = True
    return hashes


def finished(folder: Path, layer: dict) -> str | None:
    """The recorded hash of a prepared disc from an earlier run that this release still produces, else None."""
    saved = read_object(folder / 'taisen.json')
    image = folder / 'Track 01.iso'
    try:
        if (saved.get('output_sha256') in accepted(layer) and image.is_file()
                and image.stat().st_size == layer['output_bytes'] and (folder / 'Track 02.wav').is_file()
                and (folder / 'game.cue').is_file()):
            return saved['output_sha256']
    except (OSError, TypeError):
        pass
    return None


def replace_prepared_folder(staged: Path, final: Path) -> None:
    previous = staged.parent / f'previous-{final.name}'
    if final.exists():
        os.replace(final, previous)
    try:
        os.replace(staged, final)
    except OSError:
        if previous.exists():
            os.replace(previous, final)
        raise


def publish(work: Path, final: Path, image: Path, wav: Path, receipt: dict, move_wav: bool) -> None:
    folder = work / ('out-' + final.name)
    folder.mkdir()
    os.replace(image, folder / 'Track 01.iso')
    if move_wav:
        os.replace(wav, folder / 'Track 02.wav')
    else:
        shutil.copyfile(wav, folder / 'Track 02.wav')
    (folder / 'game.cue').write_text(CUE, encoding='ascii', newline='\n')
    (folder / 'taisen.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    replace_prepared_folder(folder, final)


def identify(record: dict, digest: str) -> str | None:
    if digest == record['original_sha256']:
        return 'original'
    for language, layer in LAYERS.items():
        if digest in accepted(record[layer]):
            return language
    return None


def prepare_japanese(paths: Paths, record: dict, candidates: list[Path], number: int, base: int,
                     force: bool = False) -> None:
    """Keep a copy of the player's untouched original disc as the Japanese option, when they gave one."""
    target = paths.game / f'disc{number}-ja'
    if (not force and finished(target, {'output_sha256': record['original_sha256'],
                                       'output_bytes': record['original_bytes']})):
        return
    paths.game.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.preparar-', dir=paths.game) as scratch:
        work = Path(scratch)
        image, wav = work / 'ja.iso', work / 'Track 02.wav'
        for candidate in candidates:
            try:
                disc = Disc(candidate)
                sectors = disc.extract(image)
            except (SetupError, OSError):
                continue
            if sha256(image) != record['original_sha256']:
                continue
            say(base, f'Disco {number}: guardando el original japonés…')
            silent = False
            audio_bytes = record.get('audio_wav_bytes', 5005100)
            if not disc.write_audio(wav, sectors, audio_bytes):
                write_silence(wav, audio_bytes)
                silent = True
            publish(work, target, image, wav, dict(schema=2, disc=number, language='ja', patches=None,
                                                   output_sha256=record['original_sha256'], subtitled_videos=False,
                                                   silent_audio=silent), True)
            return


def prepare_disc(paths: Paths, manifest: dict, candidates: list[Path], number: int, base: int, span: int,
                 force: bool = False, *, invalid: frozenset[str] = frozenset()) -> None:
    record = manifest['discs'][str(number)]
    prepare_japanese(paths, record, candidates, number, base, force or 'ja' in invalid)
    targets = {language: paths.game / f'disc{number}{suffix}' for language, suffix in LANGUAGES.items()}
    videos = paths.patches / record['videos']['patch']
    state = {language: None if force or language in invalid else finished(targets[language], record[LAYERS[language]]) for language in targets}
    subtitled = {language: accepted(record[LAYERS[language]]).get(state[language], False) for language in targets}
    wants_video = videos.is_file()
    if state['en'] and state['es'] and subtitled['en'] == subtitled['es'] and (subtitled['en'] or not wants_video):
        say(base + span, f'Disco {number}: ya estaba preparado.')
        return
    paths.game.mkdir(parents=True, exist_ok=True)
    version = manifest['version']
    with tempfile.TemporaryDirectory(prefix='.preparar-', dir=paths.game) as scratch:
        work = Path(scratch)
        english, wav, silent = work / 'en.iso', work / 'Track 02.wav', False
        if state['en']:  # only what is missing is rebuilt, from the English disc already prepared
            say(base, f'Disco {number}: usando el disco inglés ya preparado…')
            shutil.copyfile(targets['en'] / 'Track 01.iso', english)
            shutil.copyfile(targets['en'] / 'Track 02.wav', wav)
            has_video = subtitled['en']
        else:
            kind, source = None, None
            for index, candidate in enumerate(candidates):
                say(base, f'Disco {number}: leyendo {candidate.name}…')
                try:
                    disc = Disc(candidate)
                    sectors = disc.extract(english)
                except (SetupError, OSError):
                    continue
                kind = identify(record, sha256(english))
                if kind in ('original', 'en'):
                    source = disc
                    break
                if kind == 'es' and index == len(candidates) - 1:
                    source = disc
                    break
                kind = None
            if not source:
                raise SetupError(
                    f'Disco {number}: no se reconoce como Sakura Taisen para Saturn (Japón, GS-9037 V1.005), ni '
                    'original ni con la traducción inglesa v2.1. Usa un volcado sin modificar de tu disco.'
                    if candidates else f'Falta el disco {number} de Sakura Taisen para Saturn.')
            audio_bytes = record.get('audio_wav_bytes', 5005100)
            if not source.write_audio(wav, sectors, audio_bytes):
                write_silence(wav, audio_bytes)
                silent = True
            if kind == 'es':  # a Spanish disc of this release: adopt it; there is no English base to keep
                digest = sha256(english)
                publish(work, targets['es'], english, wav,
                        dict(schema=2, disc=number, language='es', patches=version, output_sha256=digest,
                             subtitled_videos=accepted(record['spanish'])[digest], silent_audio=silent), True)
                say(base + span, f'Disco {number}: disco en español reconocido.')
                return
            if kind == 'original':
                say(base + span * 2 // 10, f'Disco {number}: aplicando Inglés v{version} Taisen…')
                original = work / 'original.iso'
                os.replace(english, original)
                apply_delta(paths, original, paths.patches / record['english']['patch'], english,
                            record['english']['output_sha256'])
                original.unlink()
                has_video = False
            else:
                say(base + span * 2 // 10, f'Disco {number}: traducción inglesa v2.1 reconocida; se usa tal cual.')
                has_video = accepted(record['english'])[sha256(english)]
        saved_spanish = targets['es']
        if (not has_video and not wants_video and (subtitled['es']
                or read_object(saved_spanish / 'taisen.json').get('subtitled_videos') is True)):
            # A repair can rebuild English from Japanese after its ISO was lost.
            # Keep verified subtitles from the older Spanish copy when available.
            spanish_track = saved_spanish / 'Track 01.iso'
            video_end = record['video_offset'] + record['video_bytes']
            if spanish_track.is_file() and spanish_track.stat().st_size >= video_end:
                old_video = work / 'saved-video.bin'
                copy_range(spanish_track, record['video_offset'], record['video_bytes'], old_video)
                if sha256(old_video) == record['video_subtitled_sha256']:
                    copy_range(old_video, 0, record['video_bytes'], english, record['video_offset'])
                    has_video = True
                old_video.unlink()
        if wants_video and not has_video:
            say(base + span * 4 // 10, f'Disco {number}: aplicando vídeos subtitulados…')
            old, new = work / 'video-old.bin', work / 'video-new.bin'
            copy_range(english, record['video_offset'], record['video_bytes'], old)
            if sha256(old) != record['video_original_sha256']:
                raise SetupError(f'Disco {number}: contenedor de vídeo inesperado.')
            apply_delta(paths, old, videos, new, record['video_subtitled_sha256'])
            copy_range(new, 0, record['video_bytes'], english, record['video_offset'])
            old.unlink()
            new.unlink()
            has_video = True
        english_hash = record['english']['output_subtitled_sha256' if has_video else 'output_sha256']
        say(base + span * 6 // 10, f'Disco {number}: aplicando Español v{version} Taisen…')
        blank, spanish = work / 'blank.iso', work / 'es.iso'
        shutil.copyfile(english, blank)
        blank_range(blank, record['video_offset'], record['video_bytes'])
        apply_delta(paths, blank, paths.patches / record['spanish']['patch'], spanish, record['spanish']['blank_sha256'])
        blank.unlink()
        copy_range(english, record['video_offset'], record['video_bytes'], spanish, record['video_offset'])
        spanish_hash = record['spanish']['output_subtitled_sha256' if has_video else 'output_sha256']
        if sha256(spanish) != spanish_hash:
            raise SetupError(f'Disco {number}: el disco en español no coincide con el esperado.')
        say(base + span * 9 // 10, f'Disco {number}: guardando los discos preparados…')
        keep_english = state['en'] == english_hash
        for language, image, digest in (('en', english, english_hash), ('es', spanish, spanish_hash)):
            if language == 'en' and keep_english:
                continue
            publish(work, targets[language], image, wav,
                    dict(schema=2, disc=number, language=language, patches=version, output_sha256=digest,
                         subtitled_videos=has_video, silent_audio=silent), language == 'es')
    say(base + span, f'Disco {number}: listo.' + (' (Tu imagen no trae pista de audio: se dejó en silencio.)' if silent else ''))


def prepared_english(paths: Paths, manifest: dict) -> bool:
    return all(finished(paths.game / f'disc{n}', manifest['discs'][str(n)]['english']) for n in (1, 2))


# ---- HD mod ------------------------------------------------------------------------------------------

def locate_game(folder: Path) -> Path | None:
    for archive in folder.rglob('*'):
        if archive.name.upper() == 'KAO.SPR' and archive.parent.name.upper() == 'SYSTEM' \
                and archive.parent.parent.name.upper() == 'SAKURA1':
            return archive.parent.parent.parent
    return None


def open_pc(paths: Paths, source: Path, work: Path, names: list[str] | None = None) -> tuple[Path, Path | None]:
    """Find SAKURA1 and any separate MOVIE directory without changing the player's input files."""
    kind = describe_pc(source)
    if kind == 'game':
        return source, None
    movies = None
    if kind == 'image':
        image = Image(source)
        try:
            root = image.root()
            cabinets = work / 'cab'
            cabinets.mkdir()
            for name in CABINETS:
                image.copy(*root[name], cabinets / name.lower())
            if names is None:  # the videos are on the disc itself, outside the cabinets
                movies = work / 'movie'
                movies.mkdir()
                for name, (lba, size) in image.folder('MOVIE').items():
                    if name.endswith('.MPG'):
                        image.copy(lba, size, movies / name)
        finally:
            image.close()
        first = cabinets / 'data1.cab'
    elif kind == 'cabinets':
        cabinets, first = None, child(source, 'DATA1.CAB')
    else:
        raise SetupError('No es la edición de PC de Sakura Taisen (imagen del disco, carpeta con data1.cab o '
                         'carpeta del juego instalado).')
    out = work / 'pc'
    out.mkdir()
    result = run([paths.unshield, '-d', out, 'x', first, *(names or [])])
    if cabinets:
        shutil.rmtree(cabinets)
    if result.returncode:
        raise SetupError('No se pudieron extraer los recursos de la edición de PC: '
                         + result.stderr.decode(errors='replace').strip()[:300])
    root = locate_game(out)
    if not root:
        raise SetupError('La edición de PC no contiene SAKURA1/SYSTEM/KAO.SPR.')
    if movies is None and kind == 'cabinets':  # a copy of the disc: MOVIE sits beside the cabinets
        movies = child(source, 'MOVIE')
    return root, movies


def native_portraits(discs: list[Path]) -> dict[int, bytes]:
    """Saturn portrait identities (40x80 indexed cells) from the *FCE.BIN files of the prepared discs."""
    native = {}
    for disc in discs:
        with disc.open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as iso:
            for name, lba, size in iso_files(iso):
                if not name.endswith('FCE.BIN') or size > 1024 * 1024 or size < 160:
                    continue
                data = iso[lba * 2048:lba * 2048 + size]
                ids = []
                for value in struct.unpack_from('>80H', data):
                    if not value:
                        break
                    ids.append(value)
                if len(data) != 160 + len(ids) * 3200:
                    continue
                for index, identity in enumerate(ids):
                    native.setdefault(identity, data[160 + index * 3200:160 + (index + 1) * 3200])
    return native


def build_portraits(paths: Paths, pc_root: Path, discs: list[Path], work: Path, output: Path) -> tuple[int, Path]:
    import hd_matching as matching  # needs Pillow; only the HD step does
    recipe = json.loads(paths.recipe.read_text(encoding='utf-8'))
    archive = child(child(child(pc_root, 'SAKURA1'), 'SYSTEM'), 'KAO.SPR')
    data = archive.read_bytes()
    source = recipe['source']
    if len(data) != source['bytes'] or hashlib.sha256(data).hexdigest() != source['sha256']:
        raise SetupError('El archivo de retratos de tu edición de PC no coincide con la edición admitida.')
    local = work / 'KAO.SPR'  # the runtime names its output after the file; keep the name and an ASCII path
    shutil.copyfile(archive, local)
    sheets = work / 'kao'
    result = run([paths.runtime, '--export-pc-spr', local, sheets], cwd=paths.runtime.parent)
    if result.returncode:
        raise SetupError('No se pudieron leer los retratos de PC: ' + result.stderr.decode(errors='replace')[:300])
    native = native_portraits(discs)
    output.mkdir(parents=True)
    entries, catalogue, images = [], bytearray(), {}
    for row in recipe['portraits']:
        identity = int(row['id'], 16)
        raw = native.get(identity)
        if raw is None or hashlib.sha256(raw).hexdigest() != row['native_raw_sha256']:
            continue  # this identity falls back to the Saturn portrait
        if row['pc_index'] not in images:
            images[row['pc_index']] = matching.load_image(sheets / f'KAO-{row["pc_index"]}.png')
        image = images[row['pc_index']]
        if image.size != (80, 160):
            continue
        variants = []
        for density in (1, 2):
            prepared = matching.prepare_variant(image, raw, density, row['dx'], row['dy'],
                                                swap_strips=row.get('swap_strips', False))
            expected = row.get('variants_rgba_sha256', {}).get(str(density))
            if expected and hashlib.sha256(prepared.tobytes()).hexdigest() != expected:
                variants = None
                break
            buffer = io.BytesIO()
            prepared.save(buffer, format='PNG')
            blob = buffer.getvalue()
            name = hashlib.sha256(blob).hexdigest() + '.png'
            (output / name).write_bytes(blob)
            variants.append((name, fnv64(blob)))
        if not variants:
            continue
        entries.append(dict(id=identity, offset=len(catalogue), raw_hash=fnv64(raw), variants=variants))
        catalogue.extend(raw)
    if not entries:
        raise SetupError('Ningún retrato HD coincide con tus discos; el mod HD de retratos no se preparó.')
    native_name = 'native-' + hashlib.sha256(catalogue).hexdigest() + '.bin'
    (output / native_name).write_bytes(catalogue)
    lines = ['[pack]', 'schema=1', f'source_bytes={len(data)}', f'source_hash={fnv64(data)}',
             f'palette_hash={PALETTE_HASH}', f'count={len(entries)}', f'native_file={native_name}',
             f'native_hash={fnv64(bytes(catalogue))}', '']
    for index, entry in enumerate(entries):
        parts = entry['variants']
        lines.extend([f'[portrait-{index}]', f"native_id={entry['id']}", f"offset={entry['offset']}",
                      f"raw_hash={entry['raw_hash']}", f'file1={parts[0][0]}', f'hash1={parts[0][1]}',
                      f'file2={parts[1][0]}', f'hash2={parts[1][1]}', ''])
    manifest = output / 'manifest.ini'
    manifest.write_text('\n'.join(lines), encoding='utf-8')
    return len(entries), manifest


# Everything the HD mod uses or will use, taken once from the player's PC edition so that a category integrated
# later needs no new preparation: every image (.SPR: backgrounds, scenes, events, CG, endings, titles, eye
# catches, maps, units, large characters, system/menus, items, walls…), the videos and the small tables that
# go with them. Audio (voices, music, effects) is not part of the HD mod.
PC_PACK_VERSION = 'pc-full-1'
PC_PACK_EXTENSIONS = {'.SPR', '.MPG', '.BIN', '.DAT', '.TAB', '.PRI', '.OD', '.BMP', '.PAL'}
PC_PACK_SKIP_FOLDERS = {'VOICE', 'BGM', 'SE'}


def pc_pack_files(root: Path, movies: Path | None = None) -> list[tuple[Path, str]]:
    """(file, path in the pack) for the PC edition's HD material under SAKURA1-3 and MOVIE."""
    picked = []
    folders = sorted(root.iterdir(), key=lambda entry: entry.name.upper())
    if movies is not None and movies.is_dir() and not child(root, 'MOVIE'):
        folders.insert(0, movies)
    for top in folders:
        name = top.name.upper()
        if not top.is_dir() or not (name.startswith('SAKURA') or name == 'MOVIE'):
            continue
        for file in sorted(top.rglob('*')):
            if not file.is_file():
                continue
            relative = file.relative_to(top)
            if any(part.upper() in PC_PACK_SKIP_FOLDERS for part in relative.parts[:-1]):
                continue
            if file.suffix.upper() in PC_PACK_EXTENSIONS:
                picked.append((file, f'{name}/{relative.as_posix().upper()}'))
    return picked


def build_pc_pack(found: Path, target: Path, base: int, span: int, *, movies: Path | None = None) -> dict:
    """Copies the PC edition's HD material into the pack with a manifest (path, size, SHA-256)."""
    files = pc_pack_files(found, movies)
    if not files:
        raise SetupError('Tu edición de PC no tiene las imágenes del juego (SAKURA1/SAKURA2/SAKURA3).')
    total = sum(file.stat().st_size for file, _ in files)
    done, rows, categories = 0, [], {}
    for index, (file, name) in enumerate(files):
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256()
        with file.open('rb') as source, destination.open('wb') as out:
            for block in iter(lambda: source.read(1 << 20), b''):
                digest.update(block)
                out.write(block)
        size = destination.stat().st_size
        rows.append(dict(path=name, bytes=size, sha256=digest.hexdigest()))
        category = '/'.join(name.split('/')[:2]) if name.count('/') > 1 else name.split('/')[0]
        categories[category] = categories.get(category, 0) + 1
        done += size
        if index % 50 == 0:
            say(base + int(span * done / max(total, 1)), f'Mod HD: guardando archivos de tu edición de PC ({index + 1} de {len(files)})…')
    manifest = dict(schema=1, version=PC_PACK_VERSION, files=len(rows), bytes=total, categories=categories,
                    videos=sum(1 for row in rows if row['path'].endswith('.MPG')), entries=rows)
    (target / 'pc-manifest.json').write_text(json.dumps(manifest, indent=1) + '\n', encoding='utf-8')
    return manifest


def hd_stamp(paths: Paths) -> str:
    """What the HD pack is built from in this release; a pack with another stamp is rebuilt."""
    h = hashlib.sha256(PC_PACK_VERSION.encode('ascii'))
    for file in (paths.recipe, paths.provenance):
        h.update(file.read_bytes())
    return h.hexdigest()


def hd_ready(paths: Paths) -> bool:
    try:
        saved = json.loads((paths.hd / 'prepared-manifest.json').read_text(encoding='utf-8'))
        return ((paths.hd / 'hd-pack.stfp').is_file() and (paths.hd / 'pc' / 'pc-manifest.json').is_file()
                and saved.get('stamp') == hd_stamp(paths))
    except (OSError, ValueError):
        return False


def refresh_hd_portraits(paths: Paths, discs: list[Path]) -> bool:
    """Refresh portrait assets from the prepared PC files without recopying the HD pack."""
    pack = paths.hd
    report_file = pack / 'prepared-manifest.json'
    receipt_file = pack / 'hd-pack.stfp'
    pc_root = pack / 'pc'
    archive = pc_root / 'SAKURA1/SYSTEM/KAO.SPR'
    if not (receipt_file.is_file() and archive.is_file()):
        return False
    try:
        report = json.loads(report_file.read_text(encoding='utf-8'))
        receipt = receipt_file.read_bytes()
    except (OSError, ValueError) as error:
        raise SetupError('No se pudo leer el registro del mod HD instalado.') from error
    recipe_hash = sha256(paths.recipe)
    if report.get('stamp') == hd_stamp(paths) or report.get('portrait_recipe_sha256') == recipe_hash:
        return False
    portraits = pack / 'portraits'
    if not (portraits.is_dir() and all(disc.is_file() for disc in discs)):
        raise SetupError('Faltan los retratos instalados o los discos preparados para actualizar el mod HD.')
    header = struct.Struct('<8sIIQQQII')
    if len(receipt) < header.size:
        raise SetupError('El registro del mod HD instalado está incompleto.')
    magic, version, backgrounds, source_size, source_hash, _, _, reserved = header.unpack_from(receipt)
    if magic != b'STFHD01\0' or version != 1 or len(receipt) != header.size + backgrounds * 32:
        raise SetupError('El registro del mod HD instalado no es compatible.')
    archive_data = archive.read_bytes()
    if (len(archive_data), fnv64(archive_data)) != (source_size, source_hash):
        raise SetupError('El archivo de retratos de PC no coincide con el registro del mod HD instalado.')

    say(98, 'Mod HD: actualizando los retratos de tu instalación…')
    with tempfile.TemporaryDirectory(prefix='.actualizar-retratos-', dir=pack.parent) as scratch:
        work = Path(scratch)
        staged = work / 'portraits'
        count, manifest = build_portraits(paths, pc_root, discs, work, staged)
        new_receipt = work / 'hd-pack.stfp'
        new_receipt.write_bytes(header.pack(magic, version, backgrounds, source_size, source_hash,
                                            fnv64(manifest.read_bytes()), count, reserved) + receipt[header.size:])
        previous = work / 'previous-portraits'
        os.replace(portraits, previous)
        try:
            os.replace(staged, portraits)
            os.replace(new_receipt, receipt_file)
        except OSError:
            if portraits.exists():
                os.replace(portraits, staged)
            os.replace(previous, portraits)
            raise
        report.update(portraits=count, portrait_recipe_sha256=recipe_hash)
        staged_report = work / 'prepared-manifest.json'
        staged_report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        os.replace(staged_report, report_file)
    return True


def link_or_copy(source, target):
    try:
        os.link(source, target)
        return target
    except OSError:
        return shutil.copy2(source, target)


def prepare_hd(paths: Paths, source: Path, discs: list[Path], base: int, span: int,
               *, saved_pc: dict | None = None, expected_pc: set[str] | None = None) -> dict:
    rows = json.loads(paths.provenance.read_text(encoding='utf-8'))['backgrounds']
    paths.hd.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.preparar-hd-', dir=paths.hd.parent) as scratch:
        work = Path(scratch)
        say(base, 'Mod HD: leyendo tu edición de PC…')
        found, movies = open_pc(paths, source, work)
        pc_root = work / 'root'  # a private copy with the exact layout the runtime expects
        wall = pc_root / 'SAKURA1/WALL'
        wall.mkdir(parents=True)
        (pc_root / 'SAKURA1/SYSTEM').mkdir()
        game = child(found, 'SAKURA1')
        shutil.copyfile(child(child(game, 'SYSTEM'), 'KAO.SPR'), pc_root / 'SAKURA1/SYSTEM/KAO.SPR')
        for row in rows:
            file = child(child(game, 'WALL'), row['id'] + '.SPR')
            if not file or hashlib.sha256(file.read_bytes()).hexdigest() != row['source_spred_sha256']:
                raise SetupError(f'El fondo {row["id"]} de tu edición de PC no coincide con la edición admitida.')
            shutil.copyfile(file, wall / (row['id'] + '.SPR'))
        say(base + span * 3 // 10, 'Mod HD: preparando los 19 fondos…')
        cache = work / 'cache'
        result = run([paths.runtime, '--prepare-pc-backgrounds', pc_root, cache], cwd=paths.runtime.parent,
                     timeout=900)
        if result.returncode:
            raise SetupError('No se pudieron preparar los fondos HD: '
                             + (result.stderr or result.stdout).decode(errors='replace')[:300])
        staged = work / 'hd-resources'
        (staged / 'backgrounds').mkdir(parents=True)
        entries = []
        for row in rows:
            identity = row['id']
            matches = list(cache.glob(identity + '-pc864-v3-*.stfb'))
            if len(matches) != 1:
                raise SetupError('Falta un fondo preparado: ' + identity)
            blob = matches[0].read_bytes()
            (staged / 'backgrounds' / (identity + '.stfb')).write_bytes(blob)
            source_hash = fnv64((wall / (identity + '.SPR')).read_bytes())
            entries.append(struct.pack('<8sQQQ', identity.encode('ascii'), source_hash, fnv64(blob), len(blob)))
        say(base + span * 6 // 10, 'Mod HD: preparando los retratos…')
        count, manifest = build_portraits(paths, pc_root, discs, work, staged / 'portraits')
        archive = (pc_root / 'SAKURA1/SYSTEM/KAO.SPR').read_bytes()
        receipt = struct.pack('<8sIIQQQII', b'STFHD01\0', 1, len(entries), len(archive), fnv64(archive),
                              fnv64(manifest.read_bytes()), count, 0) + b''.join(entries)
        (staged / 'hd-pack.stfp').write_bytes(receipt)
        if saved_pc is None:
            pc = build_pc_pack(found, staged / 'pc', base + span * 7 // 10, span * 25 // 100, movies=movies)
            if expected_pc and not expected_pc.issubset(item['path'] for item in pc['entries']):
                raise SetupError('La edición de PC indicada no contiene todos los archivos que faltan.')
        else:
            pc = saved_pc
            shutil.copytree(found, staged / 'pc', copy_function=link_or_copy)
        report = dict(schema=2, original_pc_files_included=True, backgrounds=len(entries), portraits=count,
                      pc_files=pc['files'], pc_bytes=pc['bytes'], pc_videos=pc['videos'], pc_categories=pc['categories'],
                      stamp=hd_stamp(paths))
        (staged / 'prepared-manifest.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        replace_prepared_folder(staged, paths.hd)
    say(base + span, f'Mod HD: {report["pc_files"]} archivos de tu edición de PC guardados '
                     f'({report["pc_videos"]} vídeos); {len(rows)} fondos y {count} retratos ya activos.')
    return report


# ---- profile -----------------------------------------------------------------------------------------

DEFAULT_SETTINGS = ('[features]\npreset=custom\nscene_view=1\ntext_style=0\n'
                    'pc_hd_backgrounds=0\npc_hd_portraits=0\nhd_preload=1\npad_profile=0\nrun_ahead=0\n')


def set_values(file: Path, values: dict[tuple[str, str], str]) -> None:
    ini = configparser.ConfigParser(interpolation=None)
    ini.optionxform = str
    if file.is_file():
        ini.read(file, encoding='utf-8')
    for (section, key), value in values.items():
        if not ini.has_section(section):
            ini.add_section(section)
        ini.set(section, key, value)
    file.parent.mkdir(parents=True, exist_ok=True)
    temporary = file.with_name(file.name + '.tmp')
    with temporary.open('w', encoding='utf-8', newline='\n') as out:
        ini.write(out, space_around_delimiters=False)
    os.replace(temporary, file)


def set_language(paths: Paths, language: str) -> Path:
    disc = paths.game / f'disc1{ALL_LANGUAGES[language]}' / 'game.cue'
    if not disc.is_file():
        raise SetupError('Ese idioma aún no está preparado. Prepara el juego primero.')
    set_values(paths.home / 'launcher.ini', {('game', 'disc'): str(disc), ('sakura', 'language'): language})
    return disc


def saved_language(paths: Paths) -> str:
    saved = configparser.ConfigParser(interpolation=None)
    try:
        saved.read(paths.home / 'launcher.ini', encoding='utf-8')
    except configparser.Error:
        return 'es'
    language = saved.get('sakura', 'language', fallback='es')
    return language if language in ALL_LANGUAGES else 'es'


PREVIEW_FILES = {'0': 'presentation-original.png', '1': 'presentation-enhanced.png'}


def make_previews(paths: Paths, disc: Path, force: bool = False,
                  *, repair: set[str] | None = None) -> int:
    """The two pictures of the presentation chooser («Tu aventura, a tu manera»): the player's own title screen
    in Original 4:3 and in Mejorada 16:9, taken by the runtime in a hidden window. They are pictures of the
    game, so they are made here from the player's disc and never shipped. Returns how many were made."""
    art = paths.home / 'art'
    wanted = {mode: art / name for mode, name in PREVIEW_FILES.items()
              if (name in repair if repair is not None else force or not (art / name).is_file())}
    if not wanted or not paths.runtime.is_file() or not disc.is_file():
        return 0
    art.mkdir(parents=True, exist_ok=True)
    made = 0
    with tempfile.TemporaryDirectory(prefix='.vista-', dir=paths.home) as scratch:
        work = Path(scratch)
        (work / 'title.movie').write_text('650 0800 0\n655 0 0\n', encoding='ascii')  # Start: the title screen
        for mode, target in wanted.items():
            settings = work / f'settings-{mode}.ini'
            settings.write_text(f'[features]\npreset=custom\npresentation_mode={mode}\nscene_view=1\n', encoding='ascii')
            shot = work / f'shot-{mode}.png'
            keys = f'1:SIZE=960x540,1480:WINDOWSHOT={shot},1490:QUIT'  # (the finished title, Press Start shown)
            run([paths.runtime, '--disc', disc, '--settings', settings, '--backup', work / f'backup-{mode}.bin',
                 '--video', 'software', '--unthrottled', '--mute', '--frames', '1500', '--movie', work / 'title.movie'],
                extra_env={'SATRECOMP_WINDOW_HIDDEN': '1', 'SATRECOMP_SKIP_CHOOSER': '1', 'SATRECOMP_WINDOW_KEYS': keys},
                cwd=paths.runtime.parent, timeout=300)
            if shot.is_file() and shot.read_bytes()[:8] == b'\x89PNG\r\n\x1a\n':
                os.replace(shot, target)
                made += 1
    return made


def write_default_settings(paths: Paths) -> None:
    """First-run defaults (Mejorada, Zoom, HD preload…). The launcher may already have written settings.ini
    (its preset choice) before the helper runs, so missing keys are filled in; choices already there stay."""
    file = paths.home / 'settings.ini'
    if not file.exists():
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(DEFAULT_SETTINGS, encoding='ascii', newline='\n')
        return
    defaults = configparser.ConfigParser(interpolation=None)
    defaults.optionxform = str
    defaults.read_string(DEFAULT_SETTINGS)
    current = configparser.ConfigParser(interpolation=None)
    current.optionxform = str
    try:
        current.read(file, encoding='utf-8')
    except configparser.Error:
        return
    missing = [(section, key, value) for section in defaults.sections() for key, value in defaults.items(section)
               if not current.has_option(section, key)]
    if not missing:
        return
    for section, key, value in missing:
        if not current.has_section(section):
            current.add_section(section)
        current.set(section, key, value)
    with file.open('w', encoding='utf-8', newline='\n') as output:
        current.write(output, space_around_delimiters=False)


def load_manifest(paths: Paths) -> dict:
    try:
        manifest = json.loads((paths.patches / 'parches.json').read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        raise SetupError('Faltan los parches de la versión (carpeta parches).') from error
    if manifest.get('schema') != 2:
        raise SetupError('Los parches de la carpeta parches son de otra versión del programa.')
    if not paths.xdelta.is_file():
        raise SetupError(f'Falta {paths.xdelta.name} en la carpeta del programa.')
    return manifest


def prepare_spanish_episode_art(paths, *, strict=False):
    art = paths.program / 'art/screen-backgrounds'
    if not art.is_dir():
        art = paths.program / 'assets/generated/screen-backgrounds'
    if not (art / 'EPISODE01-es-lettering-v1.png').is_file():
        if strict and (paths.program / 'manifest.json').is_file():
            raise SetupError('Falta la rotulación de las tarjetas en los archivos de la versión.')
        return []
    from episode_lettering import prepare_episode_centers

    outputs = []
    ready = True
    for disc in (1, 2):
        english = paths.game / f'disc{disc}' / 'Track 01.iso'
        spanish = paths.game / f'disc{disc}-es' / 'Track 01.iso'
        if not (english.is_file() and spanish.is_file()):
            continue
        try:
            outputs.extend(prepare_episode_centers(english, spanish, art, paths.home / 'art/episode-centers'))
        except (OSError, ValueError) as error:
            if strict:
                raise SetupError(f'Disco {disc}: no se pudo actualizar la rotulación de episodios: {error}') from error
            say(98, f'Disco {disc}: no se pudo preparar la rotulación mejorada de episodios: {error}')
            ready = False
    return outputs if ready else None


PREPARED_HEALTH = 'prepared-health.txt'
TRACK_FILES = ('game.cue', 'Track 01.iso', 'Track 02.wav', 'taisen.json')


def read_object(file: Path) -> dict:
    try:
        result = json.loads(file.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}
    return result if isinstance(result, dict) else {}


def complete_pc_inventory(paths: Paths):
    root = paths.hd / 'pc'
    manifest = read_object(root / 'pc-manifest.json')
    entries = manifest.get('entries')
    if (manifest.get('version') != PC_PACK_VERSION or not isinstance(entries, list)
            or not entries or len(entries) != manifest.get('files')):
        return None
    files = [root / 'pc-manifest.json']
    seen = set()
    try:
        for item in entries:
            name = item['path']
            relative = Path(name)
            if (not name or relative.is_absolute() or relative.drive or '..' in relative.parts
                    or not relative.parts or not re.fullmatch(r'(?:SAKURA\d+|MOVIE)', relative.parts[0])
                    or name in seen):
                return None
            seen.add(name)
            file = root / relative
            if not file.is_file() or file.stat().st_size != item['bytes']:
                return None
            files.append(file)
    except (KeyError, OSError, TypeError, ValueError):
        return None
    return (manifest, files) if pc_folder_kind(root) == 'game' else None


def prepared_hd_files(paths: Paths) -> list[Path] | None:
    inventory = complete_pc_inventory(paths)
    if not inventory or not hd_ready(paths):
        return None
    root = paths.hd
    index = root / 'hd-pack.stfp'
    portraits = root / 'portraits'
    portrait_index = portraits / 'manifest.ini'
    try:
        data = index.read_bytes()
        header = struct.Struct('<8sIIQQQII')
        magic, version, backgrounds, _, _, portrait_hash, portrait_count, reserved = header.unpack_from(data)
        if (magic != b'STFHD01\0' or version != 1 or reserved
                or len(data) != header.size + backgrounds * 32):
            return None
        expected_backgrounds = {row['id'] for row in read_object(paths.provenance)['backgrounds']}
        actual_backgrounds = set()
        files = [index, root / 'prepared-manifest.json', portrait_index, *inventory[1]]
        for position in range(header.size, len(data), 32):
            raw_name, _, _, size = struct.unpack_from('<8sQQQ', data, position)
            name = raw_name.decode('ascii')
            if not re.fullmatch(r'KABE\d{4}', name) or name in actual_backgrounds:
                return None
            actual_backgrounds.add(name)
            file = root / 'backgrounds' / (name + '.stfb')
            if not size or file.stat().st_size != size:
                return None
            files.append(file)
        if actual_backgrounds != expected_backgrounds:
            return None
        manifest = portrait_index.read_bytes()
        if fnv64(manifest) != portrait_hash:
            return None
        config = configparser.ConfigParser(interpolation=None)
        config.read_string(manifest.decode('utf-8'))
        if config.getint('pack', 'count') != portrait_count or len(config.sections()) != portrait_count + 1:
            return None
        native = config.get('pack', 'native_file')
        if not re.fullmatch(r'native-[0-9a-f]{64}\.bin', native):
            return None
        if (portraits / native).stat().st_size != portrait_count * 3200:
            return None
        files.append(portraits / native)
        for number in range(portrait_count):
            for variant in ('file1', 'file2'):
                name = config.get(f'portrait-{number}', variant)
                if not re.fullmatch(r'[0-9a-f]{64}\.png', name):
                    return None
                file = portraits / name
                if not file.stat().st_size:
                    return None
                files.append(file)
        return files
    except (OSError, ValueError, KeyError, TypeError, struct.error, configparser.Error):
        return None


def tracked_prepared_files(paths: Paths, centers: list[Path]) -> list[tuple[str, Path, Path]]:
    files = [(kind, paths.program, file) for kind, file in
             [('P', paths.game / f'disc{disc}{suffix}' / name)
              for disc in (1, 2) for suffix in ('', '-es', '-ja') for name in TRACK_FILES]
             if file.is_file()]
    existing_art = set(centers)
    existing_art.update(file for name in PREVIEW_FILES.values()
                        if (file := paths.home / 'art' / name).is_file())
    files.extend(('H', paths.home, file) for file in sorted(existing_art))
    files.extend(('P', paths.program, file) for file in (prepared_hd_files(paths) or []))
    return files


def record_prepared_release(paths: Paths, centers: list[Path]) -> None:
    version_file = paths.program / 'VERSION'
    if not version_file.is_file():
        return
    paths.home.mkdir(parents=True, exist_ok=True)
    marker = paths.home / PREPARED_HEALTH
    lines = [version_file.read_text(encoding='utf-8').strip()]
    for kind, root, file in tracked_prepared_files(paths, centers):
        try:
            relative = file.relative_to(root).as_posix()
        except ValueError:  # overrides are for development and cannot be repaired by the launcher
            continue
        if any(char in relative for char in '\r\n\t'):
            raise SetupError('Un archivo preparado tiene un nombre inválido.')
        lines.append(f'{kind}\t{file.stat().st_size}\t{relative}')
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n',
                                     dir=paths.home, delete=False) as staged:
        temporary = Path(staged.name)
        staged.write('\n'.join(dict.fromkeys(lines)) + '\n')
    try:
        os.replace(temporary, marker)
    finally:
        temporary.unlink(missing_ok=True)


def repair_profile(paths: Paths) -> configparser.ConfigParser:
    profile = configparser.ConfigParser(interpolation=None)
    try:
        profile.read(paths.home / 'launcher.ini', encoding='utf-8')
    except (OSError, ValueError, configparser.Error):
        profile.clear()
    return profile


def previous_files(paths: Paths, kind: str = 'P') -> dict[str, int]:
    try:
        return {parts[2]: int(parts[1])
                for line in (paths.home / PREPARED_HEALTH).read_text(encoding='utf-8').splitlines()[1:]
                if len(parts := line.split('\t', 2)) == 3 and parts[0] == kind}
    except (OSError, ValueError):
        return {}


def atomic_prepared_file(target: Path, write) -> None:
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as stream:
        temporary = Path(stream.name)
    try:
        write(temporary)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def valid_audio(file: Path, expected: int | None = None) -> bool:
    try:
        size = file.stat().st_size
        if size < 44 or (expected is not None and size != expected):
            return False
        with wave.open(str(file), 'rb') as wav:
            return (wav.getnchannels() == 2 and wav.getsampwidth() == 2 and wav.getframerate() == 44100
                    and wav.getnframes() * 4 + 44 <= size)
    except (OSError, ValueError, EOFError, wave.Error):
        return False


def repair_disc_metadata(paths: Paths, record: dict, number: int, previous: dict[str, int]) -> frozenset[str]:
    # Restore the small files around a verified ISO, using any valid sibling audio.
    folders = {language: paths.game / f'disc{number}{suffix}' for language, suffix in ALL_LANGUAGES.items()}
    layers = {language: record[name] for language, name in LAYERS.items()}
    layers['ja'] = {'output_sha256': record['original_sha256'], 'output_bytes': record['original_bytes']}
    audio = {}
    for language, folder in folders.items():
        track = folder / 'Track 02.wav'
        if valid_audio(track, previous.get(f'game/{folder.name}/{track.name}')):
            audio[language] = track
    invalid = set()
    for language, folder in folders.items():
        layer = layers[language]
        image, cue, receipt = (folder / name for name in ('Track 01.iso', 'game.cue', 'taisen.json'))
        try:
            cue_ok = cue.stat().st_size <= 1024 and cue.read_text(encoding='ascii') == CUE
        except (OSError, ValueError):
            cue_ok = False
        recorded = read_object(receipt)
        try:
            current = recorded.get('output_sha256') in accepted(layer)
            if current and cue_ok and language in audio:
                continue
            invalid.add(language)
            if image.stat().st_size != layer['output_bytes']:
                continue
        except (OSError, TypeError):
            continue
        digest = sha256(image)
        if digest not in accepted(layer):
            continue
        if language not in audio:
            if not audio:
                continue
            donor = next(iter(audio.values()))
            atomic_prepared_file(folder / 'Track 02.wav', lambda temporary: shutil.copyfile(donor, temporary))
            donor_receipt = read_object(donor.parent / 'taisen.json')
            recorded['silent_audio'] = donor_receipt.get('silent_audio', False)
        if not cue_ok:
            atomic_prepared_file(cue, lambda temporary: temporary.write_text(CUE, encoding='ascii', newline='\n'))
        recorded.update(schema=2, disc=number, language=language, output_sha256=digest,
                        subtitled_videos=accepted(layer)[digest])
        atomic_prepared_file(receipt, lambda temporary: temporary.write_text(
            json.dumps(recorded, indent=2) + '\n', encoding='utf-8'))
        invalid.discard(language)
    return frozenset(invalid)


def refresh_installed_game(paths: Paths) -> None:
    # Repair managed content without changing language or profile preferences.
    manifest = load_manifest(paths)
    profile = repair_profile(paths)
    previous = previous_files(paths)
    managed_hd = profile.get('sakura', 'pc_assets', fallback='')
    want_hd = (paths.hd.is_dir() or any(name.startswith('hd-resources/') for name in previous)
               or bool(managed_hd and Path(managed_hd).resolve() == paths.hd.resolve()))
    paths.game.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.reparar-', dir=paths.game) as scratch:
        work = Path(scratch)
        sources = None

        def find_sources():
            nonlocal sources
            if sources is None:
                saved = profile.get('sakura', 'setup_source', fallback='')
                selected = Path(saved) if saved else None
                roms = discs_folder(paths.program)
                given = [path for path in (selected, roms) if path is not None and path.exists()]
                try:
                    sources = gather(given, work)
                except SetupError:
                    if selected not in given:
                        raise
                    sources = gather([path for path in given if path != selected], work)
            return sources

        for number in (1, 2):
            record = manifest['discs'][str(number)]
            invalid = repair_disc_metadata(paths, record, number, previous)
            english = paths.game / f'disc{number}'
            japanese = paths.game / f'disc{number}-ja'
            ja_layer = {'output_sha256': record['original_sha256'],
                        'output_bytes': record['original_bytes']}
            ja_valid = 'ja' not in invalid and finished(japanese, ja_layer)
            need_ja = (japanese.is_dir() or f'game/disc{number}-ja/game.cue' in previous) and not ja_valid
            candidates = []
            if 'en' in invalid or not finished(english, record['english']):
                if ja_valid:
                    candidates.append(japanese / 'game.cue')
                else:
                    candidates.extend(find_sources()[0].get(number, []))
            if need_ja and not candidates:
                candidates.extend(find_sources()[0].get(number, []))
            prepare_disc(paths, manifest, candidates, number, 5 + 30 * (number - 1), 30, invalid=invalid)
            if not (finished(english, record['english'])
                    and finished(paths.game / f'disc{number}-es', record['spanish'])
                    and (not need_ja or (finished(japanese, ja_layer)
                                        and valid_audio(japanese / 'Track 02.wav')))
                    and valid_audio(english / 'Track 02.wav')
                    and valid_audio(paths.game / f'disc{number}-es' / 'Track 02.wav')):
                raise SetupError(f'El disco {number} necesita tu imagen original. Añádela en Opciones › Tus archivos.')
        centers = prepare_spanish_episode_art(paths, strict=True)
        if want_hd and not prepared_hd_files(paths):
            tracks = [paths.game / f'disc{n}' / 'Track 01.iso' for n in (1, 2)]
            inventory = complete_pc_inventory(paths)
            if inventory:
                prepare_hd(paths, paths.hd / 'pc', tracks, 70, 27, saved_pc=inventory[0])
            else:
                pc = find_sources()[1]
                if pc is None:
                    raise SetupError('Faltan archivos del mod HD. Añade tu edición de PC en Opciones › Tus archivos.')
                prefix = 'hd-resources/pc/'
                previous_inventory = read_object(paths.hd / 'pc' / 'pc-manifest.json').get('entries', [])
                expected_pc = {name[len(prefix):] for name in previous if name.startswith(prefix)
                               and name != prefix + 'pc-manifest.json'}
                if isinstance(previous_inventory, list):
                    expected_pc.update(item['path'] for item in previous_inventory if isinstance(item, dict)
                                       and isinstance(item.get('path'), str))
                prepare_hd(paths, pc, tracks, 70, 27, expected_pc=expected_pc)
            if not prepared_hd_files(paths):
                raise SetupError('El mod HD no se pudo verificar tras la reparación.')
    prior_art = previous_files(paths, 'H')
    previews = set()
    for name in PREVIEW_FILES.values():
        key = f'art/{name}'
        if key in prior_art:
            try:
                valid = (paths.home / key).stat().st_size == prior_art[key]
            except OSError:
                valid = False
            if not valid:
                previews.add(name)
    if previews:
        language = saved_language(paths)
        disc = paths.game / f'disc1{ALL_LANGUAGES[language]}' / 'game.cue'
        if not disc.is_file():
            disc = paths.game / 'disc1' / 'game.cue'
        if make_previews(paths, disc, repair=previews) != len(previews):
            raise SetupError('No se pudieron restaurar las vistas previas de la presentación.')
    record_prepared_release(paths, centers)
    say(100, 'Contenido preparado actualizado. Ya puedes jugar.')


def prepare(paths: Paths, given: list[Path], language: str, force: bool = False) -> dict:
    """Everything the player's files allow; what is already prepared and current is left alone."""
    manifest = load_manifest(paths)
    paths.game.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.entrada-', dir=paths.game) as scratch:
        discs, pc = gather(given, Path(scratch)) if given else ({}, None)
        ready = prepared_english(paths, manifest) and not force
        if not ready and sorted(discs) != [1, 2]:
            missing = [n for n in (1, 2) if n not in discs]
            raise SetupError('Faltan tus discos de Sakura Taisen para Saturn: '
                             + ' y '.join(f'disco {n}' for n in missing)
                             + '. Elígelos o cópialos en la carpeta «roms».')
        wants_hd = pc is not None and (force or not prepared_hd_files(paths))
        share = 35 if wants_hd else 48
        prepare_disc(paths, manifest, discs.get(1, []), 1, 2, share, force)
        prepare_disc(paths, manifest, discs.get(2, []), 2, 2 + share, share, force)
        hd = None
        if wants_hd:
            if not prepared_english(paths, manifest):
                raise SetupError('El mod HD necesita los discos preparados a partir del original o de la traducción inglesa.')
            hd = prepare_hd(paths, pc, [paths.game / f'disc{n}' / 'Track 01.iso' for n in (1, 2)], 72, 25)
        elif pc is not None:
            say(98, 'Mod HD: ya estaba preparado.')
        refreshed_portraits = False
        if not wants_hd:
            tracks = [paths.game / f'disc{n}' / 'Track 01.iso' for n in (1, 2)]
            refreshed_portraits = refresh_hd_portraits(paths, tracks)
    if not (paths.game / f'disc1{LANGUAGES[language]}' / 'game.cue').is_file():
        language = 'es' if language == 'en' else 'en'
    disc = set_language(paths, language)
    write_default_settings(paths)
    episode_art_ready = prepare_spanish_episode_art(paths)
    try:
        if make_previews(paths, disc):
            say(99, 'Vistas previas de la presentación listas.')
    except (OSError, subprocess.SubprocessError):
        pass  # (the chooser shows plain cards without them; never a reason to fail the setup)
    if refreshed_portraits or hd_ready(paths):  # the profile always points at this install's own pack (a moved or copied profile too)
        set_values(paths.home / 'launcher.ini', {('sakura', 'pc_assets'): str(paths.hd)})
    if (episode_art_ready is not None and prepared_english(paths, manifest)
            and (not paths.hd.is_dir() or prepared_hd_files(paths))):
        record_prepared_release(paths, episode_art_ready)
    return dict(disc=str(disc), language=language, hd=hd, hd_ready=hd_ready(paths))


HELP = """SaturnTaisen - Sakura Wars / Sakura Taisen (Sega Saturn)

SaturnTaisen.exe                    open the launcher (setup, language, HD mod, saves, controllers)
SaturnTaisen.exe --no-launcher      start the game with the saved setup (same as --play)
SaturnTaisen.exe --setup            open the launcher's setup even when the game is ready

--rom PATH             one of your files or a folder with them (repeatable; quote paths with spaces):
                       your two Sakura Taisen Saturn discs (.cue with its tracks, .bin, .img, .iso or a
                       .zip; original Japanese, or already patched with the English translation v2.1)
                       and, optionally, the PC edition (disc image, folder with its cabinets or installed
                       game folder) for the HD mod. Files not given are looked for beside the ones given.
--language es|en       Espanol v0.1 Taisen or Ingles v0.1 Taisen
--fullscreen           start in fullscreen
--widescreen MODE      off (original composition), 16:9 or fit (enhanced, up to 16:9)
--integration-info     print the launch surface and the setup state as JSON
--help                 this text

Example: SaturnTaisen.exe --rom "D:\\My discs" --language es --no-launcher
Your files are only read. Discs, BIOS and game files are never bundled. What is already prepared is kept.
"""


def frontend(paths: Paths, args) -> None:
    language = args.language or saved_language(paths)
    if args.rom:
        prepare(paths, args.rom, language)
    elif args.language:
        set_language(paths, language)
    if args.fullscreen:
        set_values(paths.home / 'launcher.ini', {('video', 'fullscreen'): '1'})
    if args.widescreen:
        write_default_settings(paths)
        set_values(paths.home / 'settings.ini',
                   {('features', 'preset'): 'custom',
                    ('features', 'presentation_mode'): '0' if args.widescreen == 'off' else '1',
                    ('features', 'presentation_chosen'): '1'})
    say(100, 'Configuración guardada.')


def info(paths: Paths) -> dict:
    """The launch surface for frontends (RecompLauncher-style integration info) plus the setup state."""
    manifest = {}
    try:
        manifest = json.loads(launch_manifest(paths.program).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        pass
    prepared = [language for language, suffix in ALL_LANGUAGES.items()
                if (paths.game / f'disc1{suffix}' / 'game.cue').is_file()]
    manifest['state'] = dict(prepared_languages=prepared, language=saved_language(paths),
                             hd_prepared=(paths.hd / 'hd-pack.stfp').is_file(), home=str(paths.home))
    return manifest


def main() -> int:
    global _recomplauncher_progress
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=('scan', 'prepare', 'refresh-prepared', 'language', 'info', 'frontend', 'help'))
    parser.add_argument('--folder', type=Path)
    parser.add_argument('--rom', '--disc', '--pc', dest='rom', type=Path, action='append', default=[])
    parser.add_argument('--language', choices=tuple(ALL_LANGUAGES))
    parser.add_argument('--fullscreen', action='store_true')
    parser.add_argument('--widescreen', choices=('off', '16:9', 'fit'))
    parser.add_argument('--force', action='store_true', help='rebuild even what is already prepared')
    parser.add_argument('--recomplauncher-progress', action='store_true',
                        help='emit progress as a fraction for RecompLauncher')
    parser.add_argument('--home', type=Path)
    for name in ('program', 'patches', 'xdelta', 'unshield', 'runtime', 'recipe', 'provenance', 'output', 'hd-output'):
        parser.add_argument('--' + name, type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    _recomplauncher_progress = args.recomplauncher_progress
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')
    paths = Paths(args)
    try:
        if args.command == 'info':
            print(json.dumps(info(paths), indent=2, ensure_ascii=False))
        elif args.command == 'help':
            print(HELP)
        elif args.command == 'scan':
            print(json.dumps(scan((args.folder or discs_folder(paths.program)).resolve()), ensure_ascii=False))
        elif args.command == 'language':
            print('OK', set_language(paths, args.language or 'es'))
        elif args.command == 'frontend':
            frontend(paths, args)
            print('OK', flush=True)
        elif args.command == 'refresh-prepared':
            refresh_installed_game(paths)
        else:
            given = list(args.rom) + ([args.folder] if args.folder else [])
            if not given and discs_folder(paths.program).is_dir():
                given = [discs_folder(paths.program)]
            result = prepare(paths, given, args.language or saved_language(paths), args.force)
            say(100, 'Todo listo. Ya puedes jugar.')
            print('OK', json.dumps(result, ensure_ascii=False), flush=True)
        return 0
    except SetupError as error:
        print(f'ERROR {error}', flush=True)
        return 1
    except Exception as error:  # an unexpected failure still has to reach the launcher's log as one line
        print(f'ERROR inesperado: {type(error).__name__}: {error}', flush=True)
        return 2


if __name__ == '__main__':
    sys.exit(main())
