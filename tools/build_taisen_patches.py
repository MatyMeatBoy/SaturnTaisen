"""Build the Taisen patch set the launcher applies on the player's PC (owner machine only).

  python -X utf8 tools/build_taisen_patches.py --output local/work/taisen-parches/v0.1

Layers, per disc N (1, 2), all applied with xdelta3 and its output checksums:

  ingles-v0.1-discN.xdelta    original Japanese data track  ->  English base ("Ingles v0.1 Taisen")
  espanol-v0.1-discN.xdelta   English base                  ->  Spanish ("Espanol v0.1 Taisen")
  videos-en-v0.1-discN.xdelta optional: the original /SAKURA4 video container -> the subtitled one

The English base is the supplied English translation v2.1 rebuilt for this port: identical to it except
that /SAKURA4 (the FILM video container, about 250 MB of re-encoded video per disc) keeps the original
bytes, which is what makes the base small. The optional video layer restores the subtitled container in
place; /SAKURA4 has the same position and size in every variant, so one file serves both languages.

The Spanish layer is encoded between images whose /SAKURA4 extent is zero-filled, and the video bytes are
copied back afterwards. It therefore applies to an English disc with either video container: the player's
own English v2.1 disc is a valid starting point, and a later release can rebuild only the Spanish disc
from the English one already prepared.

Inputs are the owner's prepared discs under SAKURA_OWNER_ROOT/local/prepared (japanese-discN, discN,
discN-es). Nothing here reads or writes Git data; the outputs are release assets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mmap
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from audit_sdk import files  # noqa: E402

VERSION = '0.1'
VIDEO = '/SAKURA4'


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def locate(image: Path, name: str) -> tuple[int, int]:
    with image.open('rb') as s, mmap.mmap(s.fileno(), 0, access=mmap.ACCESS_READ) as iso:
        for path, lba, size in files(iso):
            if path.upper() == name:
                return lba * 2048, size
    raise ValueError(f'{name} is not in {image}')


def copy_range(source: Path, offset: int, size: int, target: Path, target_offset: int | None = None) -> None:
    mode = 'r+b' if target_offset is not None else 'wb'
    with source.open('rb') as inp, target.open(mode) as out:
        inp.seek(offset)
        if target_offset is not None:
            out.seek(target_offset)
        left = size
        while left:
            block = inp.read(min(left, 4 * 1024 * 1024))
            if not block:
                raise ValueError('short read')
            out.write(block)
            left -= len(block)


def blank_range(target: Path, offset: int, size: int) -> None:
    with target.open('r+b') as out:
        out.seek(offset)
        left, zeros = size, bytes(4 * 1024 * 1024)
        while left:
            out.write(zeros[:min(left, len(zeros))])
            left -= min(left, len(zeros))


def encode(xdelta: Path, source: Path, target: Path, patch: Path) -> None:
    subprocess.run([str(xdelta), '-e', '-9', '-f', '-B', '603979776', '-s', str(source), str(target), str(patch)],
                   check=True)
    with tempfile.TemporaryDirectory(dir=patch.parent) as scratch:
        back = Path(scratch) / 'check.bin'
        subprocess.run([str(xdelta), '-d', '-s', str(source), str(patch), str(back)], check=True)
        if sha256(back) != sha256(target):
            raise RuntimeError(f'{patch.name} does not reproduce its target')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    owner = Path(os.environ.get('SAKURA_OWNER_ROOT', ROOT))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--xdelta', type=Path,
                        default=owner / 'local/tools/xdelta3-3.2.2/xdelta3-3.2.2-windows-x86_64/xdelta3.exe')
    parser.add_argument('--work', type=Path, default=owner / 'local/work/taisen-parches/build')
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        raise SystemExit(f'refusing to overwrite {out}')
    prepared = owner / 'local/prepared'
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True)
    manifest = {'schema': 2, 'version': VERSION, 'video_file': VIDEO, 'discs': {}}
    for disc in (1, 2):
        japanese = prepared / f'japanese-disc{disc}/Track 01.iso'
        english = prepared / f'disc{disc}/Track 01.iso'
        spanish = prepared / f'disc{disc}-es/Track 01.iso'
        j_at, j_size = locate(japanese, VIDEO)
        placed = {}
        lite = {}
        for name, full in (('en', english), ('es', spanish)):
            at, size = locate(full, VIDEO)
            if size != j_size:
                raise ValueError('video container size differs')
            placed[name] = at
            lite[name] = work / f'disc{disc}-{name}-lite.iso'
            print(f'disc {disc}: {name} base without re-encoded video', flush=True)
            shutil.copyfile(full, lite[name])
            copy_range(japanese, j_at, j_size, lite[name], at)
        if placed['en'] != placed['es']:
            raise ValueError('video container moved between languages')
        video_old = work / f'disc{disc}-video-original.bin'
        video_new = work / f'disc{disc}-video-subtitled.bin'
        copy_range(japanese, j_at, j_size, video_old)
        copy_range(english, placed['en'], j_size, video_new)
        names = {'english': f'ingles-v{VERSION}-disc{disc}.xdelta', 'spanish': f'espanol-v{VERSION}-disc{disc}.xdelta',
                 'videos': f'videos-en-v{VERSION}-disc{disc}.xdelta'}
        full = {'en': sha256(english), 'es': sha256(spanish)}
        lite_hash = {name: sha256(image) for name, image in lite.items()}
        blank = {}
        for name, image in lite.items():  # the Spanish layer never sees video bytes
            blank[name] = work / f'disc{disc}-{name}-blank.iso'
            shutil.copyfile(image, blank[name])
            blank_range(blank[name], placed['en'], j_size)
        for key, source, target in (('english', japanese, lite['en']), ('spanish', blank['en'], blank['es']),
                                    ('videos', video_old, video_new)):
            print(f'disc {disc}: encoding {names[key]}', flush=True)
            encode(args.xdelta, source, target, out / names[key])
        manifest['discs'][str(disc)] = {
            'original_sha256': sha256(japanese), 'original_bytes': japanese.stat().st_size,
            'video_offset': placed['en'], 'video_bytes': j_size,
            'video_original_sha256': sha256(video_old), 'video_subtitled_sha256': sha256(video_new),
            'english': {'patch': names['english'], 'patch_sha256': sha256(out / names['english']),
                        'output_sha256': lite_hash['en'], 'output_subtitled_sha256': full['en'],
                        'output_bytes': lite['en'].stat().st_size},
            'spanish': {'patch': names['spanish'], 'patch_sha256': sha256(out / names['spanish']),
                        'blank_sha256': sha256(blank['es']),
                        'output_sha256': lite_hash['es'], 'output_subtitled_sha256': full['es'],
                        'output_bytes': lite['es'].stat().st_size},
            'videos': {'patch': names['videos'], 'patch_sha256': sha256(out / names['videos']), 'optional': True},
        }
        for file in (*lite.values(), *blank.values(), video_old, video_new):
            file.unlink()
    (out / 'parches.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    for file in sorted(out.iterdir()):
        print(f'{file.stat().st_size:>12} {file.name}')


if __name__ == '__main__':
    main()
