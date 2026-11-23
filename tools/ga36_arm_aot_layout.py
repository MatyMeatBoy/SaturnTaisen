"""Keep the ARMv7 unwind index in range of both halves of Saturn's AOT code."""

import argparse
from pathlib import Path
import re
import shlex


def make_layout(objects: list[Path]) -> str:
    generated = [path for path in objects if re.fullmatch(r'blocks_\d+\.cpp\.o', path.name)]
    if len(generated) < 2:
        raise ValueError('Expected generated Saturn SH-2 objects')
    lengths = [path.stat().st_size for path in generated]
    halfway = sum(lengths) // 2
    first_half = []
    size = 0
    for path, length in zip(generated, lengths):
        if size >= halfway:
            break
        first_half.append(f'    "{path.resolve().as_posix()}"(.text .text.*)')
        size += length

    # R_ARM_PREL31 reaches ±1 GiB. LLD sorts the generated index entries by code address.
    return (
        'SECTIONS {\n  .text.ga36.before : {\n' + '\n'.join(first_half) +
        '\n  }\n  .ARM.exidx : { *(.ARM.exidx*) }\n}\nINSERT BEFORE .text;\n'
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('response', type=Path, help='Linker response file with object paths')
    parser.add_argument('layout', type=Path, help='Output LLD script to pass with -T')
    args = parser.parse_args()
    objects = [Path(value) for value in shlex.split(args.response.read_text(encoding='utf-8'))]
    args.layout.write_text(make_layout(objects), encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
