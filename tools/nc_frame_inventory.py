"""List the data that follows an NC body bitmap, split into candidate face frames (T106/T19).

Offline and Saturn-only: reads NC*.BIN from a disc image, finds the body bitmap end (0x610 + stride*144, see
decode_saturn_bg.decode_nc) and reports, for the rest of the file, the byte count, the divisors that give a
VDP1-legal frame (width multiple of 8) and the opaque-pixel share of every block for a given frame size.
Used to check which frame sizes the VDP1 trace sizes (patch0063/0065 logs) explain.

  python tools/nc_frame_inventory.py --iso "local/prepared/disc1/Track 01.iso" NC30 NC20 [--frame 512 --frame 384]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decode_saturn_bg as saturn  # noqa: E402


def inventory(data, frame_sizes):
    stride = saturn.nc_stride(data)
    start = 0x610 + stride * 144
    rest = len(data) - start
    out = {'stride': stride, 'body_end': start, 'rest': rest, 'frames': {}}
    for size in frame_sizes:
        blocks = []
        for offset in range(start, len(data) - size + 1, size):
            block = data[offset:offset + size]
            blocks.append((offset, round(1 - block.count(0) / size, 2)))
        out['frames'][size] = {'fit_from_body_end': rest % size == 0, 'remainder': rest % size, 'blocks': blocks}
    out['divisors'] = [(w, rest // w) for w in range(8, 129, 8) if rest % w == 0 and rest // w <= 64]
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--iso', required=True)
    parser.add_argument('--frame', type=int, action='append', default=[], help='frame size in bytes (repeatable)')
    parser.add_argument('names', nargs='+')
    args = parser.parse_args()
    iso = saturn.Iso(args.iso)
    files = dict(iso.files('SAKURA1'))
    for name in args.names:
        data = iso.content(files[name + '.BIN'])
        info = inventory(data, args.frame)
        print(name, len(data), 'stride', info['stride'], 'body_end', info['body_end'], 'rest', info['rest'])
        for size, f in info['frames'].items():
            print('  frame', size, 'bytes: remainder', f['remainder'], 'blocks', len(f['blocks']))
            print('   ', ' '.join('%d:%.2f' % b for b in f['blocks'][:40]))


if __name__ == '__main__':
    main()
