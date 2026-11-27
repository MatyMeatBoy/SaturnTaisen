# Symbolize stprof samples with the lld map. Usage: symb.py map samples.txt [top]
import sys, bisect, collections, re, pickle, os
mp, smp = sys.argv[1], sys.argv[2]
top = int(sys.argv[3]) if len(sys.argv) > 3 else 40
cache = mp + '.syms.pkl'
if os.path.exists(cache):
    addrs, names, objs = pickle.load(open(cache, 'rb'))
else:
    head = re.compile(r'^ *[0-9a-f]+ +[0-9a-f]+ +[0-9a-f]+ +\d+ ')
    syms = []
    obj = ''
    for line in open(mp, encoding='utf-8', errors='replace'):
        if len(line) < 34 or not head.match(line):
            continue
        tail = line[33:].rstrip('\n')
        ind = len(tail) - len(tail.lstrip(' '))
        text = tail.strip()
        if ind == 8:
            obj = text
            continue
        if ind != 16 or text.startswith('$'):
            continue
        syms.append((int(line[:8], 16), text, obj))
    syms.sort()
    addrs = [s[0] for s in syms]
    names = [s[1] for s in syms]
    objs = [s[2] for s in syms]
    pickle.dump((addrs, names, objs), open(cache, 'wb'))
print('symbols', len(addrs))
if smp == '-':
    sys.exit()
lines = open(smp).read().split('\n')
c = collections.Counter(); co = collections.Counter(); callers = collections.defaultdict(collections.Counter)
total = 0
def look(a):
    i = bisect.bisect_right(addrs, a) - 1
    return (names[i], objs[i]) if i >= 0 else ('?', '?')
def short(o):
    o = re.sub(r'.*[/\\]', '', o.split(':(')[0])
    return 'gen/blocks_*' if o.startswith('blocks_') else o
for l in lines[1:]:
    if not l:
        continue
    pc, lr, tid = l.split()
    pc = int(pc, 16); lr = int(lr, 16)
    total += 1
    if pc > 0x50000000:
        c['<fuera del binario: libc/kernel/SDL>'] += 1; co['<lib>'] += 1
        continue
    n, o = look(pc)
    c[n] += 1; co[short(o)] += 1
    callers[n][look(lr)[0] if lr < 0x50000000 else '<lib>'] += 1
print(lines[0], 'total', total)
print('--- por objeto')
for k, v in co.most_common(25):
    print(f'{100*v/total:6.2f}% {k}')
print('--- por funcion')
for k, v in c.most_common(top):
    cl = ', '.join(f'{x[:50]}:{y}' for x, y in callers[k].most_common(2))
    print(f'{100*v/total:6.2f}% {k[:110]}   <- {cl}')
