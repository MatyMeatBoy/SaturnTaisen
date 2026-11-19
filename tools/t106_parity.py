"""T106: guest parity of two runtime executables over the T93 scenarios, with the HD features off and on.

  python tools/t106_parity.py EXE_A EXE_B [SCENARIO...]

Reuses tools/vdp_parity_bench.py (1,200 frames, strict-native, hidden unthrottled window). For each scenario and each
feature set it prints whether the per-frame state hashes are identical, the interpreted-block count of both runs and
whether the frame-1198 window shots have identical bytes. Private owner data stays under local/; nothing is committed.
"""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vdp_parity_bench as bench

FEATURES = {'hd-off': 'pc_hd_portraits=0\npc_hd_backgrounds=0\n', 'hd-on': 'pc_hd_portraits=1\npc_hd_backgrounds=1\n'}


def run(exe, tag, scenario, features):
    original = bench.Path.write_text
    def patched(self, text, *a, **k):
        if self.name == 'settings.ini':
            text = text.replace('pc_hd_portraits=0\npc_hd_backgrounds=0\n', features)
        return original(self, text, *a, **k)
    bench.Path.write_text = patched
    try:
        return bench.run(exe, tag, scenario)
    finally:
        bench.Path.write_text = original


def main():
    exe_a, exe_b = sys.argv[1:3]
    for scenario in sys.argv[3:] or list(bench.SCENARIOS):
        for name, features in FEATURES.items():
            out = {}
            for label, exe in (('A', exe_a), ('B', exe_b)):
                tag = f't106{label}-{name}'
                _, seconds, interpreted = run(exe, tag, scenario, features)
                folder = bench.OUT / f'{tag}-{scenario}'
                hashes = (folder / 'frames.hash').read_bytes()
                shot = hashlib.sha256((folder / 'shot.png').read_bytes()).hexdigest()[:12]
                out[label] = (hashes, shot, interpreted, len(hashes.splitlines()))
            same = out['A'][0] == out['B'][0]
            print(f"{scenario} {name}: frames {out['A'][3]}/{out['B'][3]} hashes-identical {same} "
                  f"interpreted A {out['A'][2]} B {out['B'][2]} shot A {out['A'][1]} B {out['B'][1]}", flush=True)


if __name__ == '__main__':
    main()
