"""T105: EVE and scrolling-picture tables (no game data) and the crop-window geometry used by the runtime (synthetic)."""
import json, pathlib, re, shutil, subprocess, sys, tempfile, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'config/hd-eve-bg-map.json').read_text(encoding='utf-8'))
PATCH = ROOT / 'patches/0090-sakura-eve-scroll-runtime.patch'


def patch_file(name):
    """Added file `name` out of the patch (lines starting with '+')."""
    text = PATCH.read_text(encoding='utf-8').replace('\r\n', '\n')
    section = text.split('diff --git a/%s b/%s\n' % (name, name))[1].split('\ndiff --git ')[0]
    body = section.split('@@\n', 1)[1].split('\n')
    return '\n'.join(line[1:] for line in body if line.startswith('+')) + '\n'


class Tables(unittest.TestCase):
    def render(self):
        sys.path.insert(0, str(ROOT / 'tools'))
        import gen_eve_bg_table
        return gen_eve_bg_table.render(CONFIG)[0]

    def test_only_witnessed_eve_are_enabled(self):
        enabled = {e['eve'] for e in CONFIG['eve'] if e['enabled']}
        self.assertEqual(enabled, {'EVE0101', 'EVE202'})
        for e in CONFIG['eve']:
            self.assertEqual(bool(e['window']), e['enabled'], e['eve'])
            self.assertEqual(bool(e['witness']), e['enabled'], e['eve'])
        self.assertEqual(len(CONFIG['eve']), 9)

    def test_header_has_two_rows_and_matches_the_witnessed_palettes(self):
        text = self.render()
        self.assertEqual(re.findall(r'0x([0-9A-F]{16})ull,"SAKURA2/BG/BBG', text),
                         ['0D97B7C3CC0B3C31', 'D3C319A0279AEDB3'])
        self.assertIn('{-16,-16,648,346},"EVE0101"', text)

    def test_eve_palettes_do_not_collide_with_scene_or_scroll_tables(self):
        with tempfile.TemporaryDirectory() as folder:
            target = pathlib.Path(folder) / 'scene.h'
            subprocess.run([sys.executable, str(ROOT / 'tools/gen_scene_bg_table.py'),
                            str(ROOT / 'config/hd-scene-bg-map.json'), str(target)], check=True, capture_output=True)
            scene = set(re.findall(r'\{0x([0-9A-F]{16})ull,"', target.read_text()))
        eve = {e['palette'] for e in CONFIG['eve']}
        self.assertEqual(len({e['palette'] for e in CONFIG['eve']}), 9)
        self.assertFalse(eve & scene)
        self.assertFalse(eve & {s['palette'] for s in CONFIG['scroll']})

    def test_scroll_entries_are_never_drawn(self):
        self.assertTrue(CONFIG['scroll'])
        self.assertFalse([s for s in CONFIG['scroll'] if s['draw']])
        names = {s['file'] for s in CONFIG['scroll']}
        self.assertIn('SAKURA1/BG2252.BIN', names)
        by_palette = {}
        for s in CONFIG['scroll']:
            by_palette.setdefault(s['palette'], set()).add(s['file'])
        # BG2247 and BG2252 share a palette: recognition by palette alone is ambiguous, so it is report-only.
        self.assertEqual(by_palette['524ED18124B313CB'], {'SAKURA1/BG2247.BIN', 'SAKURA1/BG2252.BIN'})


@unittest.skipUnless(shutil.which('clang++') and PATCH.exists(), 'needs clang++ and the patch')
class Geometry(unittest.TestCase):
    def test_window_clip_and_static_layer(self):
        main = r'''
#include "scroll_eve.h"
#include <cassert>
#include <cmath>
using namespace port;
static bool near(float a,float b){return std::fabs(a-b)<1e-3f;}
int main(){
    const FRect inset{100,50,864,432};              // 288x144 at 3x
    {   // window inside the picture: the whole inset, source = the window
        int w[4]={10,20,576,288};auto c=ClipWindowToPicture(w,800,400,inset);
        assert(c.valid && near(c.source.x,10)&&near(c.source.y,20)&&near(c.source.w,576)&&near(c.source.h,288));
        assert(near(c.target.x,100)&&near(c.target.y,50)&&near(c.target.w,864)&&near(c.target.h,432));}
    {   // overhang left and top by 16 on a 648x346 window: the corner is black, the rest is shifted proportionally
        int w[4]={-16,-16,648,346};auto c=ClipWindowToPicture(w,576,320,inset);
        assert(c.valid && near(c.source.x,0)&&near(c.source.y,0)&&near(c.source.w,576)&&near(c.source.h,320));
        assert(near(c.target.x,100+16*864.0f/648)&&near(c.target.y,50+16*432.0f/346));
        assert(near(c.target.w,576*864.0f/648)&&near(c.target.h,320*432.0f/346));
        assert(c.target.x+c.target.w<=inset.x+inset.w+1e-2f);}
    {   int w[4]={700,0,100,100};assert(!ClipWindowToPicture(w,576,320,inset).valid);}   // outside
    {   int w[4]={0,0,0,10};assert(!ClipWindowToPicture(w,576,320,inset).valid);}        // degenerate
    assert(LayerIsStatic({}));
    assert(!LayerIsStatic({0,6,0x100,0x100,false}));        // BG2252 pan
    assert(!LayerIsStatic({0,0,0x200,0x100,false}));         // zoom
    assert(!LayerIsStatic({0,0,0x100,0x100,true}));          // line effects
    return 0;}
'''
        with tempfile.TemporaryDirectory() as folder:
            folder = pathlib.Path(folder)
            (folder / 'scroll_eve.h').write_text(patch_file('port/scroll_eve.h'))
            (folder / 'main.cpp').write_text(main)
            exe = folder / 'geometry.exe'
            subprocess.run(['clang++', '-std=c++20', '-I', str(folder), str(folder / 'main.cpp'), '-o', str(exe)],
                           check=True, capture_output=True)
            subprocess.run([str(exe)], check=True)


if __name__ == '__main__':
    unittest.main()
