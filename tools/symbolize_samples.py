"""Turn the file written by tools/vdp_profile_sampler.h (SATRECOMP_SAMPLE=PATH) into a per-function table.

  llvm-nm --defined-only -n -C sakura.exe > syms.txt
  python tools/symbolize_samples.py syms.txt PATH [TOP]

The first sample line is `base <runtime image base> total <samples>`. The executable's symbols are at its preferred
image base (0x140000000), so a sample is mapped by `address - base + 0x140000000`. Samples inside DLLs are
printed as `DLL name +offset` (resolve them with the DLL's own `llvm-nm`).
"""
import bisect
import collections
import sys

PREFERRED_BASE = 0x140000000


def main(symbols_path, samples_path, top=25):
    symbols = []
    with open(symbols_path, errors='replace') as source:
        for line in source:
            parts = line.rstrip('\n').split(' ', 2)
            if len(parts) == 3 and parts[1] in 'Tt':
                symbols.append((int(parts[0], 16), parts[2]))
    addresses = [address for address, _ in symbols]
    with open(samples_path) as source:
        head = source.readline().split()
        base, total = int(head[1], 16), int(head[3])
        counts = collections.Counter()
        for line in source:
            if line.startswith('DLL'):
                _, path, offset, count = line.split()
                counts['DLL ' + path.replace('\\', '/').split('/')[-1] + ' +' + offset] += int(count)
                continue
            address, count = line.split()
            index = bisect.bisect_right(addresses, int(address, 16) - base + PREFERRED_BASE) - 1
            counts[symbols[index][1][:100]] += int(count)
    for name, count in counts.most_common(top):
        print('%5.1f%% %s' % (100 * count / total, name))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 25)
