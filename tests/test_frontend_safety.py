"""Build small original fixtures against the actual native frontend helpers."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
PREFIX=Path('C:/msys64/clang64')
DEP=ROOT/'local/deps/satrecomp'


@unittest.skipUnless(sys.platform=='win32' and (PREFIX/'bin/clang++.exe').is_file()
                     and (DEP/'port/integer_viewport.h').is_file(),
                     'requires the locally patched Windows SDL/Clang dependency')
class FrontendTests(unittest.TestCase):
    def test_preloaded_rows_reveal_only_matching_native_cells(self):
        self.fixture('dialogue_reveal')

    def test_dialogue_preload_bounds_seals_and_requires_exact_native_table(self):
        self.fixture('dialogue_preload')

    def test_disc_file_read_is_bounded_and_discards_partial_output(self):
        self.fixture('disc_files_bounded',[DEP/'port/disc_files.cpp',DEP/'port/disc_image.cpp'])

    def test_first_movie_phase_preserves_other_scene_and_unknown_sprite_frames(self):
        self.fixture('movie_phase')
    def test_choice_text_requires_complete_owned_panel(self):
        self.fixture('choice_text')
    def test_tactical_menu_recognition_rejects_unknown_or_ambiguous_groups(self):
        self.fixture('tactical_menu')
    def test_glyph_saved_under_preserves_bevel_and_invalidates_overwrites(self):
        self.fixture('glyph_plate',[DEP/'video'/name for name in ('renderer.cpp','layers.cpp','raster.cpp','regs.cpp','vdp1.cpp')])

    def test_vdp2_color_snapshots_and_extended_map_preserve_native_frame(self):
        self.fixture('vdp2_color',[DEP/'video'/name for name in ('renderer.cpp','layers.cpp','raster.cpp','regs.cpp','vdp1.cpp')])
    def test_tactical_extension_follows_camera_and_preserves_foreground(self):
        self.fixture('tactical_extension')
    def test_english_dialogue_tables_preserve_ids_offsets_and_reject_truncation(self):
        self.fixture('dialogue_catalog')
    def fixture(self,name,extra=()):
        with tempfile.TemporaryDirectory(dir=ROOT/'local') as directory:
            folder=Path(directory).resolve()
            self.assertTrue(folder.is_relative_to((ROOT/'local').resolve()))
            exe=folder/(name+'.exe')
            command=[str(PREFIX/'bin/clang++.exe'),'-std=c++20',str(ROOT/'tests'/('test_'+name+'.cpp')),
                     *map(str,extra),'-I',str(DEP/'port'),'-I',str(DEP/'recomp-common'),
                     '-I',str(DEP/'recomp-common/launcher/src'),'-I',str(DEP/'video'),'-I',str(PREFIX/'include'),
                     '-L',str(PREFIX/'lib'),'-lSDL3','-lz','-o',str(exe)]
            result=subprocess.run(command,capture_output=True,text=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stderr)
            env=os.environ.copy()
            env['PATH']=str(PREFIX/'bin')+os.pathsep+env.get('PATH','')
            result=subprocess.run([str(exe),str(folder)],env=env,capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_m30_profiles_detect_both_families_and_preserve_user_bindings(self):
        self.fixture('controller_profiles')

    def test_prepared_hd_receipt_rejects_wrong_hashes_and_invalid_extents(self):
        self.fixture('prepared_hd')

    def test_integer_scaling_native_modes_and_all_window_shapes(self):
        self.fixture('integer_viewport')

    def test_launch_ready_requires_complete_atomic_acknowledgement(self):
        self.fixture('launch_ready')

    def test_modern_menu_view_preserves_existing_actions_and_selection(self):
        self.fixture('menu_view',[DEP/'recomp-common/menu.cpp'])

    def test_map_crossfade_keeps_integer_phase_and_rejects_unproven_edges(self):
        self.fixture('map_crossfade')

    def test_panel_blending_keeps_hardware_truncation_and_screen_space_flowers(self):
        self.fixture('panel_compositing')

    def test_presentation_keeps_subtitles_overhang_and_integer_cover(self):
        self.fixture('presentation_layout')

    def test_disc_cache_bounds_concurrent_reads_and_reopen_invalidation(self):
        self.fixture('disc_cache',[DEP/'port/disc_image.cpp'])

    def test_glyph_decoder_rejects_unknown_atlas_and_ambiguous_tiles(self):
        self.fixture('glyph_text')

    def test_narrative_text_respects_ink_bounds_and_integer_viewports(self):
        self.fixture('text_layout')

    def test_portrait_frames_match_exact_bytes_and_infer_patch_placement(self):
        self.fixture('portrait_match')

    def test_portrait_pack_rejects_bad_counts_paths_hashes_and_truncation(self):
        self.fixture('portrait_pack',[DEP/'recomp-common/settings.cpp'])

    def test_kabe_decoder_validates_tiles_and_palette(self):
        self.fixture('kabe')

    def test_background_import_uses_one_grid_and_native_palette(self):
        self.fixture('backdrop')

    def test_background_cache_validates_payload_and_atomic_replacement(self):
        self.fixture('background_cache')

    def test_compact_background_storage_is_lossless_and_bounds_checked(self):
        self.fixture('background_codec')

    def test_background_workers_bound_cancel_join_and_isolate_failures(self):
        self.fixture('background_workers')

    def test_palette_acceleration_preserves_exact_colors_and_tie_order(self):
        self.fixture('palette_match')

    def test_pc_sprite_decoder_colors_and_corrupt_input(self):
        self.fixture('pc_spr')

    def test_pc_background_grid_palette_and_explicit_identity(self):
        self.fixture('pc_backdrop')

    def test_launcher_child_outlives_observer_without_freed_memory_access(self):
        self.fixture('launcher_lifetime',[DEP/'recomp-common/launcher/src/game_process.cpp'])

    def test_launcher_disc_detection_trailing_separator_and_revision(self):
        self.fixture('launcher_disc',[DEP/'recomp-common/settings.cpp'])


if __name__=='__main__':
    unittest.main()
