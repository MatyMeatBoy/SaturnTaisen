"""Join local Saturn scene evidence with tracked HD catalogs using asset metadata only."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
IC_TABLE_IDS = {row['id'] for row in json.loads((ROOT / 'config/hd-ic-table.json').read_text(encoding='utf-8'))['entries']}
IC_CONTROLLED_IDS = {'IC02', 'IC04', 'IC0502', 'IC06', 'IC07', 'IC08', 'IC09',
                     'IC1001', 'IC1002', 'IC1003', 'IC1004', 'IC1005', 'IC1006'}
sys.path.insert(0, str(ROOT / 'tools'))
import gen_item_table  # noqa: E402
CHAPTERS = range(1, 11)
CATEGORIES = (
    'scene-pictures', 'bodies', 'portraits', 'film',
    'tactical-maps', 'tactical-units', 'menus-hud',
)
BODY_REPORT = 'docs/research/saturn-bg-format.md'
BODY_FACE_EVIDENCE = {
    (1, '/SAKURA1/NC25.BIN'): 'docs/research/nc25-baked-eyes.md',
    (1, '/SAKURA1/NC50.BIN'): 'docs/research/nc50-registered-faces.md',
    (1, '/SAKURA1/NC55.BIN'): 'docs/research/nc55-registered-faces.md',
}
CAMPAIGN_REPORT = 'docs/research/coverage-campaign-v026.md'
PORTRAIT_REPORT = 'docs/research/portrait-animation-coverage.md'
CHAPTER2_FACE_REPORT = 'docs/research/hd-chapter-2.md#stage-02-tactical-portraits'
CHAPTER2_FACE_RUNTIME_REPORT = 'docs/research/hd-chapter-2.md#face02-pc-runtime'
CHAPTER2_FACE_BANK = '1:/SAKURA2/FACE02.BIN:253500278286bc8a8d6e7c28bdee4d7ee199cc3b48f5b61c18ebab517ada49bb'
CHAPTER2_FACE_BASE_PAIRS = {0: 10, 30: 208, 31: 209}
IRIS_COMMAND_ROOM_REPORT = PORTRAIT_REPORT + '#iris-00a1-command-room-portrait'
EMBLEM_LETTER_REPORT = PORTRAIT_REPORT + '#pc-emblem-0169-in-the-letter-scene'
CHAPTER3_PORTRAIT_REPORT = 'docs/research/th3-native-attribution.md#witnessed-0301fce-portrait-bases'
CHAPTER3_PORTRAIT_DRAWS = ('0068', '00fe', '0116', '013d')
MARIA_STRIP_REPORT = PORTRAIT_REPORT + '#maria-0176-natural-strip-verification'
YONEDA_STORAGE_REPORT = PORTRAIT_REPORT + '#yoneda-00e9-storage-portrait'

RESIDUAL_PORTRAIT_REPORT = PORTRAIT_REPORT + '#residual-portraits-00a1-and-0169'
NATIVE_PORTRAIT_DECISIONS = {}
SWEEP_REPORT = 'docs/research/chapter-sweep.md'
BG1285_REPORT = 'docs/research/bg1285-pan.md'
BG1207_REPORT = 'docs/research/bg1207-pan.md'
BG2248_REPORT = 'docs/research/bg2248-pan.md'
SCROLL_REPORT = 'docs/research/scroll-table.md'
SCROLL_UNVERIFIED = {(2, 'BG2290')}
STAGE01_REPORT = 'docs/research/stage01-pc-ground.md'
CHAPTER1_ROUTE_REPORT = 'docs/research/hd-chapter-1.md#observations-from-the-full-cold-route'
# The replay identifies active donors. BG2004 shares native cells and palette
# with other variants, so this trace cannot attribute its BIN.
CHAPTER1_ROUTE_SCENES = (
    'BG1001 BG1002 BG1006 BG1007 BG1011 BG1012 BG1017 BG1021 BG1030 BG1045 BG1046 '
    'BG1058 BG1070 BG1116 BG1119 BG1193 BG1209 BG1216 BG2034 BG2039 BG2159 BG2173 '
    'BG2250 BG2251 BG2535'
).split()
CHAPTER1_ROUTE_BODIES = (
    'NC10 NC11 NC12 NC20 NC21 NC25 NC30 NC3004 NC32 NC3250 NC50 NC51 NC55 NC56 '
    'NC81 NC82 NC95 NC96 NC97'
).split()
CHAPTER1_ROUTE_PORTRAITS = (
    '0001 0002 0003 0004 0005 0006 0007 0009 000a 000b 000f 0013 0014 0015 0016 '
    '0017 0018 001a 001c 001d 0023 0040 0041 0043 0045 0047 004a 0064 0065 006e '
    '0091 0092 0093 0094 0095 0096 009b 009c 00e2 00e3 00e4 00e5 00e9 0134 0136 '
    '013a 013c 0142 0148 0149 015e 015f 0161 0163 0166 0168 0176 0177 0179 017a '
    '017b 017c'
).split()
CHAPTER1_ROUTE_FILMS = {23695360: 'MOVIE001', 45410304: 'MOVIE002', 56039424: 'MOVIE003'}
STAGE01_MAP = (1, '/SAKURA2/MAP01.BIN')
TH2_GROUND = (1, '/SAKURA2/MAP02.BIN')
TH2_UNITS = (1, '/SAKURA2/UNIT02.BIN')
TH2_REPORT = 'docs/research/hd-chapter-2.md'
STAGE21_REPORT = 'docs/research/stage21-pc-ground.md'
STAGE21_MAP = (1, '/SAKURA2/MAP21.BIN')
CHAPTER4_TACTICAL_REPORT = 'docs/research/hd-chapter-4.md#first-tactical-map-and-work-ram'
STAGE04_MAP = (1, '/SAKURA2/MAP04.BIN')
STAGE05_MAP = (1, '/SAKURA2/MAP05.BIN')
STAGE05_REPORT = 'docs/research/map05-pc-ground.md'
STAGE06_MAP = (1, '/SAKURA2/MAP06.BIN')
STAGE12_MAP = (2, '/SAKURA2/MAP12.BIN')
STAGE12_REPORT = 'docs/research/tactical-pairing.md#live-map12-pc-ground'
STAGE13_MAP = (2, '/SAKURA2/MAP13.BIN')
STAGE13_REPORT = 'docs/research/tactical-pairing.md#live-map13-pc-ground'
STAGE14_MAP = (2, '/SAKURA2/MAP14.BIN')
STAGE14_REPORT = 'docs/research/tactical-pairing.md#live-map14-pc-ground'
STAGE15_MAP = (2, '/SAKURA2/MAP15.BIN')
STAGE15_REPORT = 'docs/research/tactical-pairing.md#live-map15-ground-review'
STAGE16_MAP = (2, '/SAKURA2/MAP16.BIN')
STAGE16_REPORT = 'docs/research/tactical-pairing.md#live-map16-pc-ground'
CHAPTER5_ROUTE_REPORT = 'docs/research/hd-chapter-5.md#native-opening-observations'
CHAPTER5_ROUTE_FILES = {
    'BG1031', 'BG1198', 'BG1243', 'BG2058', 'BG2132', 'BG2133', 'BG3132', 'BG3133',
    'NC60', 'NC90', 'NC3058', 'BG2156',
}
TH5_TRACE_REPORT = 'docs/research/hd-chapter-5.md#traced-attribution-th5'
CHAPTER5_ROUTE_PORTRAITS = {'00ff', '010f', '0169', '016a'}
CHAPTER5_PORTRAIT_DRAWS = ('010f', '016a')
CHAPTER5_PORTRAIT_REPORT = 'docs/research/hd-chapter-5.md#verified-0501fce-portrait-bases'
TH6_TRACE_REPORT = 'docs/research/hd-chapter-6.md#traced-attribution-th6'
# Re-attribution with the isolated EVT overlay build (docs/research/evt-overlay-registry.md): files read by the chapter traces. The finale stopped early; see Chapter 10 evidence.
REATTR_TRACE = {
    7: (1, 'docs/research/hd-chapter-7.md#re-attribution-with-the-evt-overlay-build',
        ('BG1178', 'BG1181', 'BG2014', 'BG2160', 'BG4017', 'NC3014', 'NC3126', 'NC70')),
    8: (2, 'docs/research/hd-chapter-8.md#re-attribution-with-the-evt-overlay-build',
        ('BG1001', 'BG1195', 'BG2004', 'BG2007', 'BG4053', 'ITEM72', 'NC10', 'NC11', 'NC30', 'NC3004', 'NC3007', 'NC42')),
    9: (2, 'docs/research/hd-chapter-9.md#re-attribution-with-the-evt-overlay-build',
        ('BG1143', 'BG2017', 'BG2021', 'BG2031', 'BG2091', 'BG2092', 'BG2156', 'BG2160', 'BG2236', 'BG3091',
         'NC12', 'NC20', 'NC21', 'NC3017', 'NC3021', 'NC3031', 'NC32', 'NC34', 'NC41', 'NC50', 'NC51')),
    10: (2, 'docs/research/hd-chapter-10.md#re-attribution-with-the-evt-overlay-build',
         ('BG1284', 'BG1292', 'BG1293', 'BG2020', 'BG2023', 'BG2025', 'BG2026', 'BG2046', 'BG2057', 'BG2111',
          'BG2163', 'BG2164', 'BG2165', 'BG2166', 'BG2167', 'BG2168', 'BG2248', 'BG2284', 'BG2285', 'BG2286',
          'BG3020', 'BG3026', 'BG3046', 'BG3163', 'BG3164', 'BG3165', 'NC3023', 'NC3025', 'BBG218', 'UNIT19', 'WKL19')),
}
CHAPTER9_ROUTE_REPORT = 'docs/research/hd-chapter-9.md#native-route-observations'
CHAPTER9_ROUTE_FILES = {'BG1072', 'BG1076', 'BG1176', 'BG2098', 'BG2100', 'NC81', 'NC3018'}
NATIVE_ROUTE_FILES = {
    1: ({'NC95'}, CHAPTER1_ROUTE_REPORT),
    3: ({'BG1198'}, 'docs/research/th3-native-attribution.md'),
    5: (CHAPTER5_ROUTE_FILES, CHAPTER5_ROUTE_REPORT),
    6: ({'BG1008', 'BG1021', 'NC97'}, TH6_TRACE_REPORT),
    9: (CHAPTER9_ROUTE_FILES, CHAPTER9_ROUTE_REPORT),
}
NATIVE_ROUTE_PORTRAITS = {
    3: ({name: '1:/SAKURA1/0301FCE.BIN' for name in CHAPTER3_PORTRAIT_DRAWS}, CHAPTER3_PORTRAIT_REPORT),
    5: ({name: '1:/SAKURA1/0501FCE.BIN' for name in CHAPTER5_ROUTE_PORTRAITS}, CHAPTER5_ROUTE_REPORT),
    9: ({
        '0001': '2:/SAKURA1/0900FCE.BIN',
        '00e9': '2:/SAKURA1/0901FCE.BIN',
        '00fa': '2:/SAKURA1/0900FCE.BIN',
        '00fb': '2:/SAKURA1/0900FCE.BIN',
        '0104': '2:/SAKURA1/0900FCE.BIN',
    }, CHAPTER9_ROUTE_REPORT),
}
CHAPTER_FILE_RESIDENCIES = {
    '1:/SAKURA1/0102FCE.BIN:a92e1f3e10355f51c2d54061df38a5688502133d5d0fc3ba9522e1edcfed6992':
        (1, IRIS_COMMAND_ROOM_REPORT),
    '2:/SAKURA1/1001FCE.BIN:fa55a01f09bc3a43956bf9507fae1b0ec08c002b9d36bdd16aac3486ca76ae49': (10, 'docs/research/th10-native-attribution.md'),
    '2:/SAKURA1/0901FCE.BIN:bad07425e09a84a31c5b578fda68f9b685d2380328f3a0e5991faa33647bb522':
        (9, CHAPTER9_ROUTE_REPORT),
    '1:/SAKURA2/UNIT10.BIN:0f44592f6e4323a8b977622fcb69f9d42da29e5f81e285d09f817a1bc4438496': (7, 'docs/research/th7-native-attribution.md'),
    '1:/SAKURA2/WKL10.BIN:7b4dae276347d0e295392eeb42e181276638be1e626825d99a63394e2f2ed453': (7, 'docs/research/th7-native-attribution.md'),
    '1:/SAKURA2/WKL06.BIN:f9306a073a1c603658e7b6c132b6ef36e889086e990f2c8856e056db1c14af4b':
        (4, CHAPTER4_TACTICAL_REPORT),
    '1:/SAKURA2/WKL21.BIN:60fed250c11dab1d28df048763315fc62b159a0cee502a73b473a63cef2734f3':
        (4, CHAPTER4_TACTICAL_REPORT),
}
BBG204_INSET = (1, '/SAKURA2/BBG204.BIN')
TACTICAL_PAIRING_REPORT = 'docs/research/tactical-pairing.md'
BBG204_REPORT = 'docs/research/bbg204-tactical-inset.md'
BBG_INSET_REPORT = 'docs/research/disc1-battle-insets.md'
BBG_INSET_PAIRS = {'BBG002', 'BBG003', 'BBG004', 'BBG005', 'BBG006', 'BBG007', 'BBG008', 'BBG103', 'BBG104', 'BBG106', 'BBG205', 'BBG235'}
EVE0101_REPORT = 'docs/research/eve0101-registered-inset.md'
EVE002_REPORT = 'docs/research/eve002-tactical-inset.md'
EVE202_REPORT = 'docs/research/eve202-tactical-inset.md'
EVE0116_REPORT = 'docs/research/eve0116-tactical-inset.md'
EVE0118_REPORT = 'docs/research/eve0118-tactical-inset.md'
EVE_PAIRS = {
    'EVE002': 'BBG002', 'EVE0101': 'BBG001', 'EVE0116': 'BBG201',
    'EVE0118': 'BBG101', 'EVE102': 'BBG102', 'EVE105': 'BBG105',
    'EVE202': 'BBG202', 'EVE205': 'BBG205', 'EVE207': 'BBG207',
}
EVE_CONTROLLED_INSETS = {'EVE102', 'EVE105', 'EVE205', 'EVE207'}
EVE_CONTROLLED_REPORT = 'docs/research/disc1-battle-insets.md#controlled-eve-plate-replays'
# Menu/HUD pictures the runtime draws from the SYSTEM census (docs/research/pc-menu-hud-inventory.json), as
# (PC file, image index): evidence. Only pieces whose table or patch was read are listed; everything else stays open.
MENU_REPORT = 'docs/research/pc-menu-hud-inventory.md'
SYSTEM_HUD_DRAWS = {
    ('SAKURA1/SYSTEM/SISTEM.SPR', 2): ('patch 0213, port/frontend_sdl.cpp: save and load confirmation banner rails', MENU_REPORT + '#hd-save-and-load-confirmation-controls'),
    ('SAKURA1/SYSTEM/SISTEM.SPR', 5): ('patch 0213, port/frontend_sdl.cpp: three-button save management rails', MENU_REPORT + '#hd-save-and-load-confirmation-controls'),
    ('SAKURA1/SYSTEM/OPTION.SPR', 1): ('patch 0209, port/frontend_sdl.cpp: inventory panel rail strips', MENU_REPORT + '#hd-controls-and-inventory-panel-rails'),
    ('SAKURA1/SYSTEM/SISTEM.SPR', 12): ('patch 0209, port/frontend_sdl.cpp: controller-binding panel rails', MENU_REPORT + '#hd-controls-and-inventory-panel-rails'),
    ('SAKURA1/SYSTEM/SISTEM.SPR', 1): ('patch 0206, port/frontend_sdl.cpp: Load-menu title banner rails', MENU_REPORT + '#hd-load-menu-banner-and-control-rails'),
    ('SAKURA1/SYSTEM/SISTEM.SPR', 4): ('patch 0206, port/frontend_sdl.cpp: Load-menu two-button frame rails', MENU_REPORT + '#hd-load-menu-banner-and-control-rails'),
    ('SAKURA1/SYSTEM/SISTEM.SPR', 11): ('patch 0205, port/frontend_sdl.cpp: Options panel rails', MENU_REPORT + '#hd-options-and-system-panel-rails'),
    ('SAKURA1/SYSTEM/SISTEM.SPR', 14): ('patch 0205, port/frontend_sdl.cpp: System panel rails', MENU_REPORT + '#hd-options-and-system-panel-rails'),
    ('SAKURA1/SYSTEM/WINDOW.SPR', 0): ('patch 0202, port/frontend_sdl.cpp: timed LIPS choice rails', MENU_REPORT + '#hd-timed-lips-and-dialogue-window-rails'),
    ('SAKURA1/SYSTEM/WINDOW.SPR', 1): ('patch 0202, port/frontend_sdl.cpp: dialogue box rails', MENU_REPORT + '#hd-timed-lips-and-dialogue-window-rails'),
    ('SAKURA1/SYSTEM/WINDOW.SPR', 2): ('patch 0198, port/frontend_sdl.cpp: Long Day room choice rails', MENU_REPORT + '#hd-long-day-room-choice-frame'),
    ('SAKURA1/SYSTEM/TUIKA_W.SPR', 0): ('patch 0197, port/frontend_sdl.cpp: save confirmation frame border', MENU_REPORT + '#hd-save-confirmation-frame'),
    ('SAKURA1/SYSTEM/SISTEM.SPR', 8): ('patch 0150, port/system_brackets.h: left load selector arrow', MENU_REPORT + '#load-menu-selection-arrows'),
    ('SAKURA1/SYSTEM/SISTEM.SPR', 9): ('patch 0150, port/system_brackets.h: right load selector arrow', MENU_REPORT + '#load-menu-selection-arrows'),
    ('SAKURA1/SYSTEM/FONT_CSL.SPR', 0): ('patch 0093, port/system_brackets.h: left inventory bracket', MENU_REPORT + '#t110a-inventory-brackets-in-game'),
    ('SAKURA1/SYSTEM/FONT_CSL.SPR', 1): ('patch 0093, port/system_brackets.h: right inventory bracket', MENU_REPORT + '#t110a-inventory-brackets-in-game'),
    ('SAKURA1/SYSTEM/SIS_ICON.SPR', 2): ('patch 0112, port/load_disc_icon.h: CD-1 load emblem', MENU_REPORT + '#t110b-cd-1-emblem-in-the-load-menu'),
    ('SAKURA1/SYSTEM/SIS_ICON.SPR', 3): ('patch 0146, port/load_disc_icon.h: CD-2 load emblem in the top slot', MENU_REPORT + '#t110c-cd-2-emblem-in-the-load-menu'),
}
# SYSTEM files that belong to another category and must not be counted twice in hud-menus.
SYSTEM_HUD_EXCLUDED = {
    'SAKURA1/SYSTEM/KAO.SPR': 'portrait atlas (394 faces): counted in the portraits category through the FCE recipe and portrait pack',
}
MENU_CENSUS = 'docs/research/pc-menu-hud-inventory.json'
# The documented draws include partial native faces and conditional fallbacks.
BODY_DRAWS = {'NC10', 'NC11', 'NC20', 'NC25', 'NC30', 'NC50', 'NC55', 'NC82', 'NC97', 'NC3250'}  # NC10, NC50, NC3250: docs/research/coverage-campaign-v026.md
# Draw evidence applies to the exact disc, resource, and chapter observed.
NARRATIVE_CUTOUT_DRAWS = {
    (1, f'/SAKURA1/{name}.BIN'): (5, 'docs/research/narrative-foreground-cutouts.md')
    for name in ('BG3132', 'BG3133')
} | {
    (disc, f'/SAKURA1/{name}.BIN'): (chapter, 'docs/research/narrative-foreground-followup.md')
    for disc, chapter, name in (
        (1, 3, 'BG3289'),
        (1, 6, 'BG4059'),
        (1, 6, 'BG4119'),
        (2, 8, 'BG4187'),
    )
} | {
    (2, f'/SAKURA1/{name}.BIN'): (8, 'docs/research/iris-route-foregrounds.md')
    for name in ('BG3081', 'BG3082', 'BG3083', 'BG3086', 'BG3140', 'BG3523')
} | {
    (1, f'/SAKURA1/{name}.BIN'): (chapter, 'docs/research/chapter-one-cutout-followup.md')
    for chapter, name in ((1, 'BG4088'), (1, 'BG4165'), (1, 'BG4171'), (3, 'BG4114'))
} | {
    (disc, f'/SAKURA1/{name}.BIN'): (chapter, 'docs/research/iris-other-cutouts.md')
    for disc, chapter, name in ((2, 9, 'BG3036'), (2, 9, 'BG4093'), (2, 8, 'BG3139'), (1, 5, 'BG4084'))
} | {
    (disc, f'/SAKURA1/{name}.BIN'): (chapter, 'docs/research/bg3034-wide-cutout.md')
    for disc, chapter, name in ((1, 1, 'BG3034'),)
} | {
    (1, '/SAKURA1/BG4370.BIN'): (1, 'docs/research/chapter-one-cutout-followup.md#bg4370-sortie-foreground'),
}

SCENE_DRAWS = {
    (2, '/SAKURA1/BG2111.BIN'): (10, 'docs/research/hd-chapter-10.md#bg2111-final-battle'),
    (2, '/SAKURA1/BG1284.BIN'): (10, 'docs/research/t55-sweep-draws.md#verified-scene-draws-from-the-t55-sweep'),
    (2, '/SAKURA1/BG1292.BIN'): (10, 'docs/research/hd-chapter-10.md#bg1292-on-the-1001-route'),
    (2, '/SAKURA1/BG2020.BIN'): (10, 'docs/research/t55-sweep-draws.md#verified-scene-draws-from-the-t55-sweep'),
    (2, '/SAKURA1/BG2025.BIN'): (10, 'docs/research/hd-chapter-10.md#bg2025-in-the-ending-route'),
    (2, '/SAKURA1/BG2023.BIN'): (10, 'docs/research/hd-chapter-10.md#bg2023-under-bg3020'),
    (2, '/SAKURA1/BG2026.BIN'): (10, 'docs/research/hd-chapter-10.md#bg2026-under-bg3026'),
    (1, '/SAKURA1/BG1181.BIN'): (7, 'docs/research/t55-sweep-draws.md#verified-scene-draws-from-the-t55-sweep'),
    (1, '/SAKURA1/BG1178.BIN'): (7, 'docs/research/t55-sweep-draws.md#verified-scene-draws-from-the-t55-sweep'),
    (1, '/SAKURA1/BG2160.BIN'): (7, 'docs/research/hd-chapter-7.md#verified-bg2160-on-the-episode-7-route'),
    (1, '/SAKURA1/BG2014.BIN'): (7, 'docs/research/hd-chapter-7.md#bg2014-behind-nc3014'),
    (2, '/SAKURA1/BG1195.BIN'): (8, 'docs/research/t55-sweep-draws.md#verified-scene-draws-from-the-t55-sweep'),
    (2, '/SAKURA1/BG2160.BIN'): (9, 'docs/research/t55-sweep-draws.md#verified-scene-draws-from-the-t55-sweep'),
    (2, '/SAKURA1/BG2092.BIN'): (9, 'docs/research/hd-chapter-9.md#bg2092-mist-transition'),
    (2, '/SAKURA1/BG2166.BIN'): (10, 'docs/research/t55-sweep-draws.md#verified-scene-draws-from-the-t55-sweep'),
    (2, '/SAKURA1/BG2167.BIN'): (10, 'docs/research/t55-sweep-draws.md#verified-scene-draws-from-the-t55-sweep'),
    (2, '/SAKURA1/BG2163.BIN'): (10, 'docs/research/t55-sweep-draws.md#verified-scene-draws-from-the-t55-sweep'),
    (2, '/SAKURA1/BG2164.BIN'): (10, 'docs/research/t55-sweep-draws.md#verified-scene-draws-from-the-t55-sweep'),
    (2, '/SAKURA1/BG2165.BIN'): (10, 'docs/research/t55-sweep-draws.md#verified-scene-draws-from-the-t55-sweep'),
    (2, '/SAKURA1/BG2168.BIN'): (10, 'docs/research/t55-sweep-draws.md#verified-scene-draws-from-the-t55-sweep'),
    (2, '/SAKURA1/BG2284.BIN'): (10, 'docs/research/t55-sweep-draws.md#verified-scene-draws-from-the-t55-sweep'),
    (2, '/SAKURA1/BG1062.BIN'): (9, 'docs/research/t55-sweep-draws.md#verified-scene-draws-from-the-t55-sweep'),
    (2, '/SAKURA1/BG2097.BIN'): (9, 'docs/research/t55-sweep-draws.md#verified-scene-draws-from-the-t55-sweep'),
    (2, '/SAKURA1/BG2110.BIN'): (9, 'docs/research/t55-sweep-draws.md#verified-scene-draws-from-the-t55-sweep'),
    (2, '/SAKURA1/BG1293.BIN'): (10, 'docs/research/t55-sweep-draws.md#verified-scene-draws-from-the-t55-sweep'),
    (2, '/SAKURA1/BG1072.BIN'): (9, 'docs/research/hd-chapter-9.md#verified-bg1072-before-0901'),
    (2, '/SAKURA1/BG2057.BIN'): (10, 'docs/research/hd-chapter-10.md#bg2057-behind-nc3057'),
    (2, '/SAKURA1/BG2517.BIN'): (9, 'docs/research/nc3517-route-evidence.md#bg2517-bedroom-scene'),
    (2, '/SAKURA1/BG2046.BIN'): (10, 'docs/research/hd-chapter-10.md#bg2046-ending-scene'),
    (2, '/SAKURA1/BG1174.BIN'): (9, 'docs/research/hd-chapter-9.md#iris-0903-street-and-warehouse-alias'),
    (2, '/SAKURA1/BG1180.BIN'): (9, 'docs/research/hd-chapter-9.md#iris-0903-street-and-warehouse-alias'),
    (2, '/SAKURA1/BG2103.BIN'): (9, 'docs/research/hd-chapter-9.md#iris-0903-street-and-warehouse-alias'),
    (2, '/SAKURA1/BG2101.BIN'): (9, 'docs/research/hd-chapter-9.md#iris-warehouse-backgrounds'),
    (2, '/SAKURA1/BG2102.BIN'): (9, 'docs/research/hd-chapter-9.md#iris-warehouse-backgrounds'),
    (2, '/SAKURA1/BG2021.BIN'): (9, 'docs/research/hd-chapter-9.md#bg2021-on-the-earned-iris-route'),
    (1, '/SAKURA1/BG1064.BIN'): (6, 'docs/research/hd-chapter-6.md#verified-bg1064-upstairs-draw'),
    (1, '/SAKURA1/BG1003.BIN'): (6, 'docs/research/hd-chapter-6.md#verified-bg1003-draw'),
    (1, '/SAKURA1/BG1047.BIN'): (6, 'docs/research/hd-chapter-6.md#verified-bg1047-draw'),
    (2, '/SAKURA1/BG2140.BIN'): (8, 'docs/research/th8-native-attribution.md#covered-0801-and-0802-backgrounds'),
    (2, '/SAKURA1/BG2523.BIN'): (8, 'docs/research/th8-native-attribution.md#covered-0801-and-0802-backgrounds'),
    (2, '/SAKURA1/BG2139.BIN'): (8, 'docs/research/th8-native-attribution.md#bg2139-ambush-draw'),
    (2, '/SAKURA1/BG2244.BIN'): (10, 'docs/research/th10-native-attribution.md#verified-1001-monitor-draws'),
    (2, '/SAKURA1/BG2245.BIN'): (10, 'docs/research/th10-native-attribution.md#verified-1001-monitor-draws'),
    (2, '/SAKURA1/BG2246.BIN'): (10, 'docs/research/th10-native-attribution.md#verified-1001-monitor-draws'),
    (1, '/SAKURA1/BG1055.BIN'): (1, 'docs/research/hd-chapter-1.md#additional-night-patrol-doors'),
    (1, '/SAKURA1/BG1036.BIN'): (1, 'docs/research/hd-chapter-1.md#additional-night-patrol-doors'),
    (1, '/SAKURA1/BG1059.BIN'): (1, 'docs/research/hd-chapter-1.md#additional-night-patrol-doors'),
    (1, '/SAKURA1/BG1043.BIN'): (1, 'docs/research/hd-chapter-1.md#night-patrol-scene-draws'),
    (1, '/SAKURA1/BG1057.BIN'): (1, 'docs/research/hd-chapter-1.md#night-patrol-scene-draws'),
    (1, '/SAKURA1/BG1010.BIN'): (1, 'docs/research/hd-chapter-1.md#night-patrol-scene-draws'),
    (1, '/SAKURA1/BG2156.BIN'): (6, 'docs/research/th6-native-attribution.md#bg2156-hd-continuation-draw'),
    (2, '/SAKURA1/BG1016.BIN'): (8, 'docs/research/th8-native-attribution.md#verified-scene-draws-on-0801-and-early-0802'),
    (2, '/SAKURA1/BG1087.BIN'): (8, 'docs/research/th8-native-attribution.md#verified-scene-draws-on-0801-and-early-0802'),
    (2, '/SAKURA1/BG1112.BIN'): (8, 'docs/research/th8-native-attribution.md#verified-scene-draws-on-0801-and-early-0802'),
    (2, '/SAKURA1/BG1276.BIN'): (8, 'docs/research/th8-native-attribution.md#verified-scene-draws-on-0801-and-early-0802'),
    (2, '/SAKURA1/BG1238.BIN'): (8, 'docs/research/th8-native-attribution.md#verified-scene-draws-on-0801-and-early-0802'),
    (1, '/SAKURA1/BG1022.BIN'): (3, 'docs/research/th3-native-attribution.md#verified-chapter-3-scene-draws'),
    (1, '/SAKURA1/BG1008.BIN'): (3, 'docs/research/th3-native-attribution.md#verified-chapter-3-scene-draws'),
    (1, '/SAKURA1/BG1132.BIN'): (3, 'docs/research/th3-native-attribution.md#verified-chapter-3-scene-draws'),
    (1, '/SAKURA1/BG2381.BIN'): (3, 'docs/research/th3-native-attribution.md#verified-chapter-3-scene-draws'),
    (1, '/SAKURA1/BG1160.BIN'): (3, 'docs/research/th3-native-attribution.md#verified-chapter-3-scene-draws'),
    (2, '/SAKURA1/BG1071.BIN'): (8, 'docs/research/th8-native-attribution.md#verified-scene-draws-on-the-0804-iris-route'),
    (2, '/SAKURA1/BG1125.BIN'): (8, 'docs/research/th8-native-attribution.md#verified-scene-draws-on-the-0804-iris-route'),
    (2, '/SAKURA1/BG1013.BIN'): (8, 'docs/research/th8-native-attribution.md#verified-scene-draws-on-the-0804-iris-route'),
    (2, '/SAKURA1/BG1019.BIN'): (8, 'docs/research/th8-native-attribution.md#verified-scene-draws-on-the-0804-iris-route'),
    (2, '/SAKURA1/BG2084.BIN'): (8, 'docs/research/th8-native-attribution.md#verified-scene-draws-on-the-0804-iris-route'),
    (2, '/SAKURA1/BG1278.BIN'): (8, 'docs/research/th8-native-attribution.md#verified-scene-draws-on-the-0804-iris-route'),
    (2, '/SAKURA1/BG2086.BIN'): (8, 'docs/research/th8-native-attribution.md#verified-scene-draws-on-the-0804-iris-route'),
    (2, '/SAKURA1/BG2162.BIN'): (10, 'docs/research/th10-native-attribution.md#verified-scene-draws-on-the-archived-ending-route'),
    (2, '/SAKURA1/BG2288.BIN'): (10, 'docs/research/th10-native-attribution.md#verified-scene-draws-on-the-archived-ending-route'),
    (2, '/SAKURA1/BG2287.BIN'): (10, 'docs/research/th10-native-attribution.md#verified-scene-draws-on-the-archived-ending-route'),
    (2, '/SAKURA1/BG1236.BIN'): (8, 'docs/research/th8-native-attribution.md#verified-festival-scene-draws-on-0802'),
    (2, '/SAKURA1/BG1237.BIN'): (8, 'docs/research/th8-native-attribution.md#verified-festival-scene-draws-on-0802'),
    (2, '/SAKURA1/BG2033.BIN'): (8, 'docs/research/th8-native-attribution.md#verified-festival-scene-draws-on-0802'),
    (2, '/SAKURA1/BG2081.BIN'): (8, 'docs/research/th8-native-attribution.md#verified-festival-scene-draws-on-0802'),
    (2, '/SAKURA1/BG2082.BIN'): (8, 'docs/research/th8-native-attribution.md#verified-festival-scene-draws-on-0802'),
    (2, '/SAKURA1/BG2083.BIN'): (8, 'docs/research/th8-native-attribution.md#verified-festival-scene-draws-on-0802'),
    (1, '/SAKURA1/BG1101.BIN'): (1, 'docs/research/scene-spot-check.md#isolated-donor-witnesses-for-iriss-room-and-the-chapter-9-opening'),
    (2, '/SAKURA1/BG2018.BIN'): (9, 'docs/research/scene-spot-check.md#isolated-donor-witnesses-for-iriss-room-and-the-chapter-9-opening'),
    (2, '/SAKURA1/BG1061.BIN'): (9, 'docs/research/hd-chapter-9.md#verified-lower-scene-plates-on-the-natural-0904-route'),
    (2, '/SAKURA1/BG1066.BIN'): (9, 'docs/research/hd-chapter-9.md#verified-lower-scene-plates-on-the-natural-0904-route'),
    (2, '/SAKURA1/BG1075.BIN'): (9, 'docs/research/hd-chapter-9.md#verified-lower-scene-plates-on-the-natural-0904-route'),
    (2, '/SAKURA1/BG1077.BIN'): (9, 'docs/research/hd-chapter-9.md#verified-lower-scene-plates-on-the-natural-0904-route'),
    (2, '/SAKURA1/BG1100.BIN'): (9, 'docs/research/hd-chapter-9.md#verified-lower-scene-plates-on-the-natural-0904-route'),
    (2, '/SAKURA1/BG1101.BIN'): (9, 'docs/research/hd-chapter-9.md#verified-lower-scene-plates-on-the-natural-0904-route'),
    (2, '/SAKURA1/BG1325.BIN'): (9, 'docs/research/hd-chapter-9.md#verified-lower-scene-plates-on-the-natural-0904-route'),
    (2, '/SAKURA1/BG2036.BIN'): (9, 'docs/research/hd-chapter-9.md#verified-lower-scene-plates-on-the-natural-0904-route'),
    (1, '/SAKURA1/BG1267.BIN'): (7, 'docs/research/th7-native-attribution.md#verified-chapter-7-scene-draws'),
    (1, '/SAKURA1/BG2126.BIN'): (7, 'docs/research/th7-native-attribution.md#verified-chapter-7-scene-draws'),
    (1, '/SAKURA1/BG2019.BIN'): (7, 'docs/research/th7-native-attribution.md#verified-chapter-7-scene-draws'),
    (1, '/SAKURA1/BG1266.BIN'): (7, 'docs/research/th7-native-attribution.md#verified-chapter-7-scene-draws'),
    (2, '/SAKURA1/BG1076.BIN'): (9, 'docs/research/hd-chapter-9.md#verified-chapter-9-scene-draws'),
    (2, '/SAKURA1/BG1176.BIN'): (9, 'docs/research/hd-chapter-9.md#verified-chapter-9-scene-draws'),
    (2, '/SAKURA1/BG2098.BIN'): (9, 'docs/research/hd-chapter-9.md#verified-chapter-9-scene-draws'),
    (2, '/SAKURA1/BG2100.BIN'): (9, 'docs/research/hd-chapter-9.md#verified-chapter-9-scene-draws'),
    (1, '/SAKURA1/BG1243.BIN'): (5, 'docs/research/hd-chapter-5.md#verified-chapter-5-lower-scene-plates'),
    (1, '/SAKURA1/BG2132.BIN'): (5, 'docs/research/hd-chapter-5.md#verified-chapter-5-lower-scene-plates'),
    (1, '/SAKURA1/BG2133.BIN'): (5, 'docs/research/hd-chapter-5.md#verified-chapter-5-lower-scene-plates'),
    **NARRATIVE_CUTOUT_DRAWS,
    (1, '/SAKURA1/BG1198.BIN'): (5, 'docs/research/hd-chapter-5.md#verified-bg1198-replacement'),
    (1, '/SAKURA1/BG1031.BIN'): (3, 'docs/research/scene-spot-check.md#bg1031-and-bg1076-on-english-disc-1'),
    (1, '/SAKURA1/BG1076.BIN'): (3, 'docs/research/scene-spot-check.md#bg1031-and-bg1076-on-english-disc-1'),
    (1, '/SAKURA1/BG1171.BIN'): (3, 'docs/research/scene-spot-check.md#bg1171-on-english-disc-1'),
    (1, '/SAKURA1/BG2172.BIN'): (3, 'docs/research/scroll-table.md#bg2172-on-english-disc-1'),
    (2, '/SAKURA1/BG1282.BIN'): (9, 'docs/research/scroll-table.md#bg1282-bg2077-and-bg2176-on-english-disc-2'),
    (2, '/SAKURA1/BG2077.BIN'): (8, 'docs/research/scroll-table.md#bg1282-bg2077-and-bg2176-on-english-disc-2'),
    (2, '/SAKURA1/BG2176.BIN'): (8, 'docs/research/scroll-table.md#bg1282-bg2077-and-bg2176-on-english-disc-2'),
    BBG204_INSET: (4, BBG204_REPORT),
    **{(1, f'/SAKURA1/BG{number}.BIN'): (1, BODY_REPORT) for number in (1011, 1012, 1017)},
    **{(1, f'/SAKURA1/BG{number}.BIN'): (1, CAMPAIGN_REPORT) for number in (1001, 1006, 1045, 1209, 2159, 2250, 2251)},
    (2, '/SAKURA1/BG2236.BIN'): (9, 'docs/research/t55-sweep-draws.md#bg2236-opaque-and-translucent-phases'),
    (1, '/SAKURA1/BG1016.BIN'): (1, 'docs/research/thd01-episode1-backgrounds.md#bg1016-hd-en-el-fundido-floral'),
    (1, '/SAKURA1/BG1120.BIN'): (1, 'docs/research/thd01-episode1-backgrounds.md#bg1120-hd-con-la-iluminacion-nocturna'),
    (1, '/SAKURA1/BG1021.BIN'): (1, 'docs/research/scene-spot-check.md#bg1021-on-disc-1'),
    (1, '/SAKURA1/BG1119.BIN'): (1, CHAPTER1_ROUTE_REPORT),
    (1, '/SAKURA1/BG2034.BIN'): (1, 'docs/research/scene-spot-check.md#bg2034-on-disc-1'),
    **{(1, f'/SAKURA1/BG{number}.BIN'): (1, 'docs/research/scene-spot-check.md#bg1007-bg1046-and-bg1058-on-disc-1')
       for number in (1007, 1046, 1058)},
    **{(1, f'/SAKURA1/BG{number}.BIN'): (1, 'docs/research/scene-spot-check.md#bg1070-and-bg2039-on-disc-1')
       for number in (1070, 2039)},
    **{(1, f'/SAKURA1/BG{number}.BIN'): (1, 'docs/research/scene-spot-check.md#bg1002-and-bg1116-on-disc-1')
       for number in (1002, 1116)},
    **{(1, f'/SAKURA1/BG{number}.BIN'): (1, 'docs/research/scene-spot-check.md#late-chapter-1-backgrounds-on-disc-1')
       for number in (1030, 1193, 2173, 2535)},
    **{(1, f'/SAKURA1/BG{number}.BIN'): (1, 'docs/research/scene-spot-check.md#bg1143-and-bg2004-on-disc-1')
       for number in (1143, 2004)},
    (1, '/SAKURA1/BG1216.BIN'): (1, CHAPTER1_ROUTE_REPORT),
    (2, '/SAKURA1/BG2159.BIN'): (8, 'docs/research/bg2159-disc2-visual.md'),
    (2, '/SAKURA1/BG2053.BIN'): (9, 'docs/research/scene-spot-check.md#bg2053-on-disc-2'),
    (2, '/SAKURA1/BG1160.BIN'): (10, 'docs/research/th10-native-attribution.md#bg1160-hd-draw'),
    **{(1, f'/SAKURA1/{name}.BIN'): (6, 'docs/research/th6-native-attribution.md#hd-background-draws')
       for name in ('BG1199', 'BG1025')},
    **{(1, f'/SAKURA1/{name}.BIN'): (7, 'docs/research/th7-native-attribution.md#hd-background-draws')
       for name in ('BG1268', 'BG2080')},
    (2, '/SAKURA1/BG1050.BIN'): (8, 'docs/research/th8-native-attribution.md#hd-room-draw'),
    (2, '/SAKURA1/BG2238.BIN'): (9, 'docs/research/bg2238-still.md'),
}
# Exact file witnesses with a documented chapter. Shared disc residency and
# the sequence of files in a cold run are insufficient for chapter placement.
NATIVE_ROUTE_DRAWS = {
    (1, 1, '/SAKURA1/NC95.BIN'): 'docs/research/thd11-episode1-bodies.md#nc95-on-the-episode-1-upstairs-route',
}

EXACT_BODY_DRAWS = {
    (1, '/SAKURA1/NC81.BIN'): (1, 'docs/research/thd11-episode1-bodies.md#nc81-on-the-episode-1-late-theater-route'),
    (1, '/SAKURA1/NC3004.BIN'): (1, 'docs/research/thd11-episode1-bodies.md#nc3004-at-the-episode-1-hanami'),
    (2, '/SAKURA1/NC3021.BIN'): (9, 'docs/research/hd-chapter-9.md#nc3021-face-registration-witness'),
    (1, '/SAKURA1/NC24.BIN'): (6, 'docs/research/hd-chapter-6.md#verified-nc24-and-nc42-in-0602'),
    (1, '/SAKURA1/NC42.BIN'): (6, 'docs/research/hd-chapter-6.md#verified-nc24-and-nc42-in-0602'),
    (1, '/SAKURA1/NC26.BIN'): (6, 'docs/research/hd-chapter-6.md#verified-nc26-body-in-0602'),
    (1, '/SAKURA1/NC95.BIN'): (6, 'docs/research/hd-chapter-6.md#verified-nc95-upstairs-body'),
    (1, '/SAKURA1/NC3173.BIN'): (1, 'docs/research/nc3173-nc3285-cutout-1440p.md'),
    (2, '/SAKURA1/NC3285.BIN'): (10, 'docs/research/nc3173-nc3285-cutout-1440p.md'),
    (2, '/SAKURA1/NC3286.BIN'): (10, 'docs/research/nc3286-ending-cutout.md'),
    (2, '/SAKURA1/NC3057.BIN'): (10, 'docs/research/nc3057-ending-faces.md'),
    (1, '/SAKURA1/NC99.BIN'): (3, 'docs/research/nc99-nc91-registered-faces.md'),
    (2, '/SAKURA1/NC91.BIN'): (8, 'docs/research/nc99-nc91-registered-faces.md'),
    (2, '/SAKURA1/NC94.BIN'): (8, 'docs/research/nc91-nc94-additional-faces.md'),
    (2, '/SAKURA1/NC15.BIN'): (8, 'docs/research/nc11-nc15-nc22-registered-faces.md'),
    (2, '/SAKURA1/NC22.BIN'): (8, 'docs/research/nc11-nc15-nc22-registered-faces.md'),
    (1, '/SAKURA1/NC40.BIN'): (6, 'docs/research/hd-chapter-6.md#verified-nc40-body-draw'),
    (2, '/SAKURA1/NC40.BIN'): (8, 'docs/research/nc40-nc71-registered-faces.md'),
    (2, '/SAKURA1/NC71.BIN'): (8, 'docs/research/nc40-nc71-registered-faces.md'),
    (2, '/SAKURA1/NC80.BIN'): (8, 'docs/research/nc80-nc81-registered-faces.md'),
    (2, '/SAKURA1/NC31.BIN'): (9, 'docs/research/nc31-nc62-nc70-registered-faces.md'),
    (2, '/SAKURA1/NC62.BIN'): (9, 'docs/research/nc31-nc62-nc70-registered-faces.md'),
    (2, '/SAKURA1/NC70.BIN'): (9, 'docs/research/nc31-nc62-nc70-registered-faces.md'),
    (2, '/SAKURA1/NC36.BIN'): (8, 'docs/research/nc36-nc72-registered-faces.md'),
    (2, '/SAKURA1/NC72.BIN'): (9, 'docs/research/nc36-nc72-registered-faces.md'),
    (2, '/SAKURA1/NC24.BIN'): (9, 'docs/research/nc24-nc3250-mouth-placement.md'),
    (2, '/SAKURA1/NC60.BIN'): (9, 'docs/research/nc60-nc61-nc3038-registered-faces.md'),
    (2, '/SAKURA1/NC61.BIN'): (9, 'docs/research/nc60-nc61-nc3038-registered-faces.md'),
    (2, '/SAKURA1/NC3038.BIN'): (9, 'docs/research/nc60-nc61-nc3038-registered-faces.md'),
}

CHAPTER_WITNESSES = {
    (2, '/SAKURA1/NC3517.BIN'): (9, 'docs/research/nc3517-route-evidence.md#natural-0904-body-and-faces'),
    (2, '/SAKURA1/BG1360.BIN'): (9, 'docs/research/hd-chapter-9.md#bg1360-door-variant'),
    **EXACT_BODY_DRAWS,
    (1, '/SAKURA1/BG4351.BIN'): (6, 'docs/research/hd-chapter-6.md#west-staircase-and-file-0602'),
    (2, '/SAKURA1/IC08.BIN'): (8, 'docs/research/ic-intermission-table.md#ic08-on-english-disc-2'),
    (2, '/SAKURA1/NC3018.BIN'): (9, CHAPTER9_ROUTE_REPORT),
    (1, '/SAKURA1/NC90.BIN'): (5, CHAPTER5_ROUTE_REPORT),
    (2, '/SAKURA1/NC81.BIN'): (9, CHAPTER9_ROUTE_REPORT),
    (1, '/SAKURA2/MAP10.BIN'): (7, 'docs/research/tactical-pairing.md#live-map10-and-map19-ground-review'),
    (2, '/SAKURA2/MAP19.BIN'): (10, 'docs/research/tactical-pairing.md#live-map10-and-map19-ground-review'),
    (1, '/SAKURA1/IC03.BIN'): (3, 'docs/research/ic03-intermission-witness.md'),
    (2, '/SAKURA1/IC06.BIN'): (9, 'docs/research/ic06-intermission-witness.md'),
    (1, '/SAKURA1/IC0501.BIN'): (5, 'docs/research/ic0501-intermission-witness.md'),
    (1, '/SAKURA1/NC3058.BIN'): (5, CHAPTER5_ROUTE_REPORT),
    **{(1, f'/SAKURA1/{name}.BIN'): (5, TH5_TRACE_REPORT)
       for name in ('BG1051', 'BG2258', 'NC91', 'NC92', 'NC4182')},
    (2, '/SAKURA1/BG2247.BIN'): (8, 'docs/research/bg2247-native-pan.md'),
    (2, '/SAKURA1/BG2093.BIN'): (9, 'docs/research/bg2093-dream-transition.md'),
    (2, '/SAKURA1/BG1213.BIN'): (10, 'docs/research/th10-native-attribution.md'),
    (2, '/SAKURA1/BG1160.BIN'): (10, 'docs/research/th10-native-attribution.md'),
    (2, '/SAKURA1/BG4055.BIN'): (10, 'docs/research/th10-native-attribution.md'),
    (2, '/SAKURA1/BG1050.BIN'): (8, 'docs/research/th8-native-attribution.md'),
    (2, '/SAKURA1/BG1212.BIN'): (8, 'docs/research/th8-native-attribution.md'),
    (2, '/SAKURA1/BG4187.BIN'): (8, 'docs/research/th8-native-attribution.md'),
    (2, '/SAKURA1/TITLE8.BIN'): (8, 'docs/research/th8-native-attribution.md'),
    (1, '/SAKURA1/BG1267.BIN'): (7, 'docs/research/th7-native-attribution.md'),
    (1, '/SAKURA1/BG1268.BIN'): (7, 'docs/research/th7-native-attribution.md'),
    (1, '/SAKURA1/BG2080.BIN'): (7, 'docs/research/th7-native-attribution.md'),
    (1, '/SAKURA1/TITLE6.BIN'): (6, 'docs/research/th6-native-attribution.md'),
    (1, '/SAKURA1/BG1199.BIN'): (6, 'docs/research/th6-native-attribution.md'),
    (1, '/SAKURA1/BG4119.BIN'): (6, 'docs/research/th6-native-attribution.md'),
    (1, '/SAKURA1/BG1025.BIN'): (6, 'docs/research/th6-native-attribution.md'),
    (1, '/SAKURA1/BG4059.BIN'): (6, 'docs/research/th6-native-attribution.md'),
    **{(1, f'/SAKURA1/{name}.BIN'): (6, TH6_TRACE_REPORT)
       for name in ('BG1003', 'BG1047', 'NC40')},
    (1, '/SAKURA1/TITLE3.BIN'): (3, 'docs/research/th3-native-attribution.md'),
    **{(1, f'/SAKURA1/{name}.BIN'): (3, 'docs/research/bg2290-native-pan.md')
       for name in ('BG2123', 'BG3123', 'BG2289', 'BG3289', 'BG2290')},
    (1, '/SAKURA1/NC3290.BIN'): (3, 'docs/research/nc3290-stage-wing.md'),
    STAGE04_MAP: (3, 'docs/research/th3-native-attribution.md'),
    STAGE05_MAP: (3, STAGE05_REPORT),
    STAGE12_MAP: (8, STAGE12_REPORT),
    STAGE13_MAP: (8, STAGE13_REPORT),
    STAGE14_MAP: (8, STAGE14_REPORT),
    STAGE15_MAP: (9, STAGE15_REPORT),
    STAGE16_MAP: (9, STAGE16_REPORT),
    (1, '/SAKURA2/UNIT04.BIN'): (3, 'docs/research/th3-native-attribution.md'),
    (1, '/SAKURA1/NC31.BIN'): (3, 'docs/research/th3-native-attribution.md#cold-replay-trace'),
    (1, '/SAKURA2/WKL04.BIN'): (3, 'docs/research/th3-native-attribution.md#cold-replay-trace'),
    (1, '/SAKURA2/WKL05.BIN'): (3, 'docs/research/th3-native-attribution.md#cold-replay-trace'),
    (1, '/SAKURA2/UNIT05.BIN'): (3, 'docs/research/th3-native-attribution.md#cold-replay-trace'),
    **{(1, f'/SAKURA1/{name}.BIN'): (1, CHAPTER1_ROUTE_REPORT)
       for name in CHAPTER1_ROUTE_SCENES + CHAPTER1_ROUTE_BODIES},
    **SCENE_DRAWS,
    (1, '/SAKURA1/NC95.BIN'): EXACT_BODY_DRAWS[(1, '/SAKURA1/NC95.BIN')],
    (1, '/SAKURA1/NC20.BIN'): (1, BODY_REPORT),
    (1, '/SAKURA1/NC30.BIN'): (1, BODY_REPORT),
    (2, '/SAKURA1/BG1285.BIN'): (10, BG1285_REPORT),
    (1, '/SAKURA1/BG1207.BIN'): (1, BG1207_REPORT),
    (1, '/SAKURA1/BG2248.BIN'): (1, BG2248_REPORT),
    (1, '/SAKURA1/BG2533.BIN'): (5, 'docs/research/bg2533-pan.md'),
    (1, '/SAKURA2/EVE0101.BIN'): (1, EVE0101_REPORT),
    (1, '/SAKURA2/EVE0116.BIN'): (1, EVE0116_REPORT),
    (1, '/SAKURA2/EVE0118.BIN'): (1, EVE0118_REPORT),
    (1, '/SAKURA2/EVE202.BIN'): (2, EVE202_REPORT),
    (1, '/SAKURA2/EVE002.BIN'): (2, EVE002_REPORT),
    STAGE01_MAP: (1, STAGE01_REPORT),
    TH2_GROUND: (2, TH2_REPORT),
    TH2_UNITS: (2, TH2_REPORT),
    (1, '/SAKURA2/WKL02.BIN'): (2, TH2_REPORT),
    STAGE21_MAP: (4, STAGE21_REPORT),
    STAGE06_MAP: (4, CHAPTER4_TACTICAL_REPORT),
    (1, '/SAKURA2/UNIT06.BIN'): (4, 'docs/research/hd-chapter-4.md#cold-replay-trace'),
    (1, '/SAKURA2/UNIT21.BIN'): (4, 'docs/research/hd-chapter-4.md#cold-replay-trace'),
}

for chapter, (disc, report, names) in REATTR_TRACE.items():
    for name in names:
        directory = 'SAKURA2' if name.startswith(('BBG', 'UNIT', 'WKL')) else 'SAKURA1'
        CHAPTER_WITNESSES.setdefault((disc, f'/{directory}/{name}.BIN'), (chapter, report))



def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def disc_for(chapter):
    return 1 if chapter <= 7 else 2


def asset_category(path):
    name = Path(path).name
    for pattern, category in (
        (r'(?:BG(?:\d+|HANA|KOIKOI|MAIGO|RYORI|SLOT|SOUJI|SWIM|SYATE)|BBG\d+|EVE\d+|'
         r'(?!LIPS_)\w+_CG|CG\d+|TITLE\d+|IC\d+)\.BIN', 'scene-pictures'),
        (r'NC\d+\.BIN', 'bodies'),
        (r'\d{4}FCE\.BIN', 'portraits'),
        (r'MAP\d+\.BIN', 'tactical-maps'),
        (r'UNIT\d+\.BIN', 'tactical-units'),
        (r'(?:WKL\d+|WALL\d+|ITEM\d+|LOAD|OMAKE|TMAP|LIPS_CG)\.BIN', 'menus-hud'),
    ):
        if re.fullmatch(pattern, name):
            return category
    return None


def indexed_chapter(path):
    name = Path(path).name
    atlas = re.fullmatch(r'(\d{2})\d{2}(?:FCE|TBL)\.BIN', name)
    title = re.fullmatch(r'TITLE(\d+)\.BIN', name)
    if atlas or title:
        chapter = int((atlas or title)[1])
        if chapter in CHAPTERS:
            return chapter
    return None


def film_key(resource, offset):
    return resource['disc'], 150 + resource['lba'] + offset // 2048


def pairs(data):
    return {'/' + row['saturn_file']: row for row in data['pairs']}


def runtime_bg_entries(root):
    with TemporaryDirectory() as temp:
        header = Path(temp) / 'scene_bg.h'
        subprocess.run([
            sys.executable, str(root / 'tools/gen_scene_bg_table.py'),
            str(root / 'config/hd-scene-bg-map.json'), str(header),
        ], check=True, capture_output=True, text=True)
        text = header.read_text(encoding='utf-8')
        first = {palette: (file, index) for palette, file, index in re.findall(
            r'\{0x([0-9A-F]+)ull,"([^"]+)",(\d+)\}', text)}
        cells = {(palette, fnv): (file, index) for palette, fnv, file, index in re.findall(
            r'\{0x([0-9A-F]+)ull,0x([0-9A-F]+)ull,"([^"]+)",(\d+)\}', text)}
        return first, cells


def fce_atlas_row(identities, recipes):
    """TP6: attribute an FCE atlas file to the portrait identities it holds."""
    native = [i for i in identities if i in NATIVE_PORTRAIT_DECISIONS]
    uncovered = [i for i in identities if i not in recipes and i not in NATIVE_PORTRAIT_DECISIONS]
    if not identities:
        return {'status': 'excluded', 'identities': [],
                'reason': 'empty atlas (160-byte zero header): no portrait identity to replace',
                'evidence': PORTRAIT_REPORT}
    has_hd = any(i in recipes for i in identities)
    row = {'status': 'unknown' if uncovered else 'hd' if has_hd else 'excluded',
           'identities': identities, 'evidence': 'config/hd-portrait-recipe.json'}
    if native:
        row['native_by_design'] = native
        row['decision_evidence'] = RESIDUAL_PORTRAIT_REPORT
    if uncovered:
        row['uncovered'] = uncovered
        row['reason'] = 'the uncovered identities still need a replacement or native decision (T52)'
    return row


ENDING_REPORT = 'docs/research/ending-bank-pairs.md'
ENDING_PHOTO_RECORDS = (6, 7)


def runtime_ending_photo_keys(root):
    """Palette fingerprints the ending-photo draw of patch 0137 tests (records 6 and 7)."""
    text = (root / 'patches/0137-sakura-ending-photos.patch').read_text(encoding='utf-8')
    return set(re.findall(r'\{[67], [23], 0x[0-9A-F]+, 0x([0-9A-F]{16})ull,', text))


def ending_bank_row(bank, disc, photo_keys, verified):
    """Describe the canonical group photographs and any verified unique route photographs."""
    base = {'pc': bank['pc_file'], 'scope': 'ending-bank subimages', 'decision_evidence': ENDING_REPORT}
    general = verified.get('general_ending')
    if general and bank['saturn_file'] == general['saturn_file']:
        indices = [r['pc_image_index'] for r in bank['records'] if r['saturn_record'] in general['records']]
        if len(indices) != len(general['records']):
            raise ValueError(f'Missing general ending records for {bank["saturn_file"]}')
        if disc != verified['disc']:
            return {**base, 'pc_image_indices': indices, 'status': 'paired-not-wired',
                    'reason': 'The general ending composition is supported on disc 2.'}
        return {**base, 'pc_image_indices': indices, 'status': 'hd', 'verified_in_game': False,
                'runtime_patch': general['runtime_patch'], 'fixture_evidence': general['evidence']}
    photos = [r for r in bank['records'] if r['saturn_record'] in ENDING_PHOTO_RECORDS]
    if len(photos) == 2 and all(r['palette_fnv'] in photo_keys for r in photos):
        base['pc_image_indices'] = [r['pc_image_index'] for r in photos]
        if disc != verified['disc']:
            return {**base, 'status': 'paired-not-wired',
                    'reason': ('The photograph draw is limited to disc 2 and the English ENDING module; '
                               'disc 1 has no ending witness.')}
        extra = {'native_records': [r['saturn_record'] for r in bank['records'] if r['saturn_record'] not in ENDING_PHOTO_RECORDS],
                 'native_reason': 'The PC redraws change the artwork. The native compositions stay in use.',
                 'runtime_patch': 'patches/0137-sakura-ending-photos.patch'}
        if unique := verified.get('unique_routes', {}).get(bank['saturn_file']):
            selected = [record for record in bank['records'] if record['saturn_record'] in unique['records']]
            if len(selected) != len(unique['records']):
                raise ValueError(f'Missing verified ending records for {bank["saturn_file"]}')
            controlled = unique.get('controlled', False)
            return {**base, **extra, 'status': 'hd', 'verified_in_game': not controlled,
                    'pc_image_indices': [record['pc_image_index'] for record in selected],
                    'native_records': [n for n in extra['native_records'] if n not in unique['records']],
                    'runtime_patch': unique['runtime_patch'],
                    ('fixture_evidence' if controlled else 'runtime_evidence'): unique['evidence'],
                    'shared_runtime_donor': verified['donor'], 'shared_pc_image_indices': base['pc_image_indices']}
        if bank['saturn_file'] == verified['saturn_file']:
            return {**base, **extra, 'status': 'hd', 'verified_in_game': True, 'runtime_evidence': ENDING_REPORT}
        return {**base, **extra, 'status': 'wired-unverified',
                'reason': ('The photograph records have the same palette and cell keys as the verified Sakura '
                           'bank, so the draw is tried when they appear; no replay of this route was recorded.')}
    return {**base, 'pc_image_indices': [r['pc_image_index'] for r in bank['records']],
            'status': 'paired-not-wired',
            'reason': ('The four GE pictures are whole-screen theatre variants; the ending viewport, fade and '
                       'overlay layers have no live witness, so no replacement is selected.')}


def build(root, index_dir, portrait_audit):
    def config(name):
        return load(root / 'config' / (name + '.json'))

    inventory = load(index_dir / 'resource-inventory.json')
    index = load(index_dir / 'scene-index.json')
    portrait_report = load(portrait_audit)
    if portrait_report.get('errors'):
        raise ValueError('The portrait audit reports errors')
    portraits = portrait_report['rows']
    fce_atlases = portrait_report.get('fce_atlases', {})
    recipes = {r['id']: r['pc_index'] for r in config('hd-portrait-recipe')['portraits']}
    films = {(r['disc'], r['fad']): r for r in config('film-fad-map')['streams']}
    bounded_films = {(edit['disc'], edit['movie']): edit['spans']
                     for edit in config('film-video-spans')['edits']}
    bg = pairs(config('hd-scene-bg-map'))
    minigame_backgrounds = pairs(config('hd-minigame-bg-pairs'))
    bg_review = config('hd-scene-bg-review')
    native_bg_aliases = {}
    for alias, canonical in bg_review.get('exact_native_aliases', {}).items():
        alias_path, canonical_path = (f'/SAKURA1/{name}.BIN' for name in (alias, canonical))
        source, target = bg[alias_path], bg[canonical_path]
        exact_keys = ('palette_fnv', 'cells_fnv', 'cells_sha256')
        if (
            source['size'] != [288, 144] or target['size'] != source['size']
            or any(not source.get(key) or source[key] != target.get(key) for key in exact_keys)
            or any(name[2:3] in '34' or name in bg_review['rejected'] for name in (alias, canonical))
            or target.get('tier') != 'content'
        ):
            raise ValueError(f'Invalid exact native background alias {alias} -> {canonical}')
        native_bg_aliases[alias_path] = (canonical, target)
    scroll_rows = {row['name'] for row in config('hd-scroll-pictures')['rows']}
    bg_table, bg_cell_table = runtime_bg_entries(root)
    scene_alias_candidates = {}
    donor_hashes = {
        (row['pc_file'], str(row['pc_image_index'])): row.get('pc_sha256')
        for row in bg.values() if row.get('pc_file') and 'pc_image_index' in row
    }
    tactical_maps = {r['saturn']: r for r in config('hd-tactical-map-pairs')['maps']}
    screens = pairs(config('hd-screen-map'))
    endings = pairs(config('hd-ending-bank-map'))
    ending_photo_keys = runtime_ending_photo_keys(root)
    ending_verified = config('hd-ending-bank-map')['verified_runtime']
    bodies = pairs(config('hd-body-map'))
    body_review = config('hd-body-review')
    # Match tools/gen_body_table.py, including reviewed cut-outs with a candidate-tier pair.
    confirmed_bodies = set(body_review['eye_confirmed_candidates']) | set(body_review.get('cutout', {}))
    body_runtime = {
        Path(path).stem for path, pair in bodies.items()
        if Path(path).stem not in body_review['rejected']
        and (pair['tier'] == 'content' or Path(path).stem in confirmed_bodies)
    }
    items = pairs(config('hd-item-map'))
    item_review = pairs(config('hd-item-review'))
    # Same selection as tools/gen_item_table.py: the palettes that the runtime item-card table (patch 0090) holds.
    item_runtime = {palette for palette, _ in gen_item_table.build_rows(
        config('hd-item-map'), config('hd-item-review')['pairs'])} & set(config('hd-item-texture-fingerprints'))
    cold_bg = {
        '/' + row['pc_file'].replace('/BG/', '/').replace('.SPR', '.BIN'): row['evidence_frame']
        for row in config('hd-scene-bg-pairs')['pairs']
    }
    chapters = {
        n: {'chapter': n, 'disc': disc_for(n), 'resources': {c: {} for c in CATEGORIES}}
        for n in CHAPTERS
    }
    unassigned = {c: {} for c in CATEGORIES}
    by_id = {r['resource_id']: r for r in inventory}

    # Explicit runtime observations can identify a resource or establish RAM
    # residency. Selection shots establish the chapter, not an asset identity.
    observed = {}
    resident = {}
    for row in index:
        if row['certainty'] != 'observed':
            continue
        chapter = row.get('observed_episode')
        report = SWEEP_REPORT
        if chapter is None and row['scene_id'] == '1:observation:intermission-pause':
            chapter = 1
            report = 'docs/research/chapter1-wide-transitions.md'
        if chapter not in CHAPTERS:
            continue
        if row['disc'] != disc_for(chapter):
            raise ValueError(f"Observed episode {chapter} on unexpected disc {row['disc']}")
        key = (row.get('resource_id'), row.get('stream_offset'))
        if key[0] is not None:
            observed[key] = (chapter, report)
        for resource_id in row.get('resident_resource_ids', []):
            if asset_category(by_id[resource_id]['iso_path']):
                resident[resource_id] = (chapter, report)

    def add(category, key, row, chapter=None, association='unknown', evidence=None):
        item = dict(row, association=association)
        if evidence:
            item['evidence'] = evidence
        target = chapters[chapter]['resources'] if chapter else unassigned
        target[category][key] = item

    for resource in inventory:
        disc, path, ident = (resource[k] for k in ('disc', 'iso_path', 'resource_id'))
        kind = asset_category(path)
        name = Path(path).stem
        chapter, report = observed.get((ident, None), (None, None))
        association = 'observed' if chapter else 'unknown'
        if chapter is None:
            residency = resident.get(ident) or CHAPTER_FILE_RESIDENCIES.get(ident)
            if residency:
                chapter, report = residency
                association = 'resident'
        if chapter is None:
            candidate = indexed_chapter(path)
            if candidate and disc == disc_for(candidate):
                chapter, association = candidate, 'inferred'
        if (disc, path) in CHAPTER_WITNESSES:
            chapter, report = CHAPTER_WITNESSES[(disc, path)]
            association = 'observed'
        row = {'status': 'unknown'}
        if (disc, path) == STAGE01_MAP:
            row = {
                'status': 'hd',
                'verified_in_game': True,
                'runtime_evidence': STAGE01_REPORT,
                'pc': 'SAKURA2/MAP/MAP01/MAP01_A.SPR',
                'scope': 'source-4 ground only',
                'extension': 'STAGE01-right-v1.png',
            }
        elif (disc, path) == (1, '/SAKURA2/WKL02.BIN'):
            row = {
                'status': 'unknown',
                'verified_components': [
                    {'pc': 'SAKURA2/SYSTEM/SLGSYS02.SPR', 'pc_image_index': index,
                      'scope': 'vertical command submenu shell', 'runtime_evidence': 'docs/research/hd-chapter-2.md#verified-wkl02-command-submenus'}
                    for index in (2, 4)
                ] + [
                    {'pc': 'SAKURA2/SYSTEM/SLGSYS02.SPR', 'pc_image_index': index,
                      'scope': 'horizontal command shell', 'runtime_evidence': 'docs/research/hd-chapter-2.md#verified-horizontal-wkl02-command-frames'}
                    for index in (0, 1)
                ],
            }
        elif (disc, path) == TH2_GROUND:
            row = {
                'status': 'hd',
                'verified_in_game': True,
                'runtime_evidence': 'docs/research/map02-pc-ground.md',
                'pc': 'SAKURA2/MAP/MAP02/MAP02_A.SPR',
                'scope': 'source-4 ground only',
            }
        elif (disc, path) == STAGE21_MAP:
            row = {
                'status': 'hd',
                'pc': 'SAKURA2/MAP/MAP21/MAP21_A.SPR',
                'scope': 'source-4 ground only',
                'verified_in_game': True,
                'runtime_evidence': STAGE21_REPORT,
            }
        elif (disc, path) == (1, '/SAKURA2/MAP03.BIN'):
            row = {
                'status': 'hd',
                'verified_in_game': True,
                'runtime_evidence': 'docs/research/tactical-ground-table.md#map03-at-1440p',
                'pc': 'SAKURA2/MAP/MAP03/MAP03_A.SPR',
                'scope': 'source-4 ground only',
            }
        elif (disc, path) == (1, '/SAKURA2/MAP07.BIN'):
            row = {
                'status': 'hd',
                'verified_in_game': True,
                'runtime_evidence': 'docs/research/tactical-ground-table.md#map07-at-1440p',
                'pc': 'SAKURA2/MAP/MAP07/MAP07_A.SPR',
                'scope': 'source-4 ground only',
            }
        elif (disc, path) == STAGE04_MAP:
            row = {
                'status': 'hd',
                'verified_in_game': True,
                'runtime_evidence': 'docs/research/map04-pc-ground.md',
                'pc': 'SAKURA2/MAP/MAP04/MAP04_A.SPR',
                'scope': 'source-4 ground only',
            }
        elif (disc, path) == STAGE05_MAP:
            row = {
                'status': 'hd',
                'verified_in_game': True,
                'runtime_evidence': STAGE05_REPORT,
                'pc': 'SAKURA2/MAP/MAP05/MAP05_A.SPR',
                'scope': 'source-4 ground only',
            }
        elif (disc, path) == STAGE06_MAP:
            row = {
                'status': 'hd',
                'verified_in_game': True,
                'runtime_evidence': 'docs/research/map06-pc-ground.md',
                'pc': 'SAKURA2/MAP/MAP06/MAP06_A.SPR',
                'scope': 'source-4 ground only',
                'pairing_evidence': CHAPTER4_TACTICAL_REPORT,
            }
        elif (disc, path) in (STAGE12_MAP, STAGE13_MAP, STAGE14_MAP, STAGE15_MAP, STAGE16_MAP):
            stage = Path(path).stem
            report = {STAGE12_MAP: STAGE12_REPORT, STAGE13_MAP: STAGE13_REPORT,
                      STAGE14_MAP: STAGE14_REPORT, STAGE15_MAP: STAGE15_REPORT,
                      STAGE16_MAP: STAGE16_REPORT}[(disc, path)]
            row = {
                'status': 'hd',
                'verified_in_game': True,
                'runtime_evidence': report,
                'pc': f'SAKURA2/MAP/{stage}/{stage}_A.SPR',
                'scope': 'source-4 ground only',
            }
        elif kind == 'tactical-maps' and tactical_maps.get(f'{disc}:{path}', {}).get('status') == 'paired':
            pair = tactical_maps[f'{disc}:{path}']
            row = {
                'status': 'paired-not-wired',
                'pc': pair['pc_ground'],
                'pairing_evidence': TACTICAL_PAIRING_REPORT,
                'reason': ('PC MAP BIN is byte-identical to the Saturn BIN and its TAB names this ground, but the '
                           'runtime has no pattern-name fingerprint or ground sampler for this map'
                           + ('; the ground holds %d images (tiles or frames) and needs an assembler' % pair['ground_image_count']
                              if pair.get('ground_layout') == 'tiles' else '')),
            }
            if (disc, path) == (1, '/SAKURA2/MAP10.BIN'):
                row['reason'] = ('The PC facades and terrace require different offsets, and the PC roof '
                                 'has a keyed span with a different boundary. Keep the native ground.')
            elif (disc, path) == (2, '/SAKURA2/MAP19.BIN'):
                row['reason'] = ('The PC ground places lamps and rails differently at the witnessed camera. '
                                 'Keep the native ground.')
        elif (disc, path) == (1, '/SAKURA2/BBG203.BIN'):
            row = {'status': 'paired-not-wired', 'pc': 'SAKURA2/BG/BBG203.SPR',
                   'pairing_evidence': BBG_INSET_REPORT + '#bbg203-partial-pc-coverage',
                   'reason': 'The PC donor omits the right and bottom of the native artwork. A live inset witness is needed to register the shared region.'}
        elif (disc, path) == BBG204_INSET:
            row = {'status': 'hd', 'pc': 'SAKURA2/BG/BBG204.SPR',
                   'verified_in_game': True, 'runtime_evidence': BBG204_REPORT}
        elif title := re.fullmatch(r'/SAKURA1/(TITLE(?:[1-9]|10))\.BIN', path):
            row = {
                'status': 'excluded',
                'pc': f'SAKURA1/TITLE/{title[1]}.SPR',
                'reason': 'Japanese lettering is baked into the PC image. The approved episode cards use localized centers.',
                'decision_evidence': 'docs/research/episode-title-pc-pairings.md',
            }
        elif disc == 1 and name in BBG_INSET_PAIRS and path == f'/SAKURA2/{name}.BIN':
            row = {'status': 'hd', 'pc': f'SAKURA2/BG/{name}.SPR', 'pairing_evidence': BBG_INSET_REPORT}
        elif disc == 1 and name in EVE_CONTROLLED_INSETS and path == f'/SAKURA2/{name}.BIN':
            row = {'status': 'hd', 'pc': f'SAKURA2/BG/{EVE_PAIRS[name]}.SPR',
                   'verified_in_game': False, 'fixture_evidence': EVE_CONTROLLED_REPORT}
        elif path in endings:
            bank = endings[path]
            row = ending_bank_row(bank, disc, ending_photo_keys, ending_verified)
            if disc == 2 and path == '/SAKURA1/SU_CG.BIN' and row.get('verified_in_game'):
                chapter, association, report = 10, 'observed', 'docs/research/ending-bank-pairs.md#natural-sumire-ending-and-unique-pc-photographs'
        elif path in minigame_backgrounds and resource['sha256'] == minigame_backgrounds[path]['saturn_sha256']:
            pair = minigame_backgrounds[path]
            row = {'status': 'paired-not-wired', 'pc': pair['pc_file'], 'pc_image_index': pair['pc_image_index'],
                   'pairing_evidence': 'docs/research/saturn-bg-format.md#minigame-background-pages',
                   'reason': 'The minigame layer viewport and transform still need an in-game witness.'}
            if runtime_evidence := pair.get('runtime_evidence'):
                row.pop('reason')
                witnessed = disc in pair['verified_discs']
                row.update(status='hd' if witnessed else 'wired-unverified',
                           verified_in_game=witnessed, runtime_evidence=runtime_evidence)
        elif path in bg:
            alias, pair = native_bg_aliases.get(path, (None, bg[path]))
            accepted = name not in bg_review['rejected'] and (
                pair.get('tier') == 'content' or name in bg_review['eye_confirmed_number_tier']
            )
            if accepted:
                key = (pair['palette_fnv'], pair['pc_file'], str(pair['pc_image_index']))
                donor = bg_table.get(key[0]) or bg_cell_table.get((key[0], pair.get('cells_fnv')))
                same_image = donor == key[1:] or (
                    donor is not None and pair.get('pc_sha256') and donor[1] == key[2] and
                    donor_hashes.get(donor) == pair['pc_sha256'] and pair['size'] == [288, 144] and
                    path.startswith(('/SAKURA1/', '/SAKURA2/EVE', '/SAKURA2/BBG')) and name[2:3] not in '34') or (
                    donor is not None and name in bg_review.get('shared_cell_choice', {}) and pair['size'] == [288, 144])
                row = {'status': 'hd' if same_image else 'paired-not-wired',
                       'pc': donor[0] if same_image else pair['pc_file']}
                if (same_image and donor[0] != pair['pc_file'] and pair.get('pc_sha256')
                        and donor_hashes.get(donor) == pair['pc_sha256'] and donor[1] == key[2]):
                    scene_alias_candidates.setdefault(pair['pc_file'], set()).add(donor[0])
                if alias:
                    row['native_alias_of'] = alias
                if (disc, path) == (1, '/SAKURA1/BG2533.BIN'):
                    row['status'] = 'hd'
                    row['runtime_evidence'] = 'docs/research/bg2533-pan.md'
                elif path == '/SAKURA2/EVE0101.BIN':
                    row['status'] = 'hd'
                    if disc == 1:
                        row.update(verified_in_game=True, runtime_evidence=EVE0101_REPORT)
                elif (disc, path) == (1, '/SAKURA2/EVE202.BIN'):
                    row.update(status='hd', verified_in_game=True, runtime_evidence=EVE202_REPORT)
                elif (disc, path) in NARRATIVE_CUTOUT_DRAWS:
                    row.update(status='hd', verified_in_game=True, runtime_evidence=NARRATIVE_CUTOUT_DRAWS[(disc, path)][1])
                elif path == '/SAKURA1/BG2295.BIN' or name in bg_review.get('guarded_viewport', []):
                    row['status'] = 'hd'
                elif path == '/SAKURA1/BG1285.BIN':
                    row['status'] = 'hd'
                    if disc == 2:
                        row.update(verified_in_game=True, runtime_evidence=BG1285_REPORT)
                elif path == '/SAKURA1/BG1207.BIN':
                    row['status'] = 'hd'
                    if disc == 1:
                        row.update(verified_in_game=True, runtime_evidence=BG1207_REPORT)
                elif path == '/SAKURA1/BG2248.BIN':
                    row['status'] = 'hd'
                    if disc == 1:
                        row.update(verified_in_game=True, runtime_evidence=BG2248_REPORT)
                elif path == '/SAKURA1/BG2238.BIN':
                    row['status'] = 'hd'
                    if (disc, path) in SCENE_DRAWS:
                        row.update(verified_in_game=True, runtime_evidence=SCENE_DRAWS[(disc, path)][1])
                elif (disc, path) == (2, '/SAKURA1/BG2093.BIN'):
                    row.update(status='hd', verified_in_game=True, runtime_evidence='docs/research/bg2093-dream-transition.md')
                elif name in scroll_rows:
                    # TP2: a row of the scroll-picture table (config/hd-scroll-pictures.json) is drawn by the runtime's table path.
                    row['status'] = 'wired-unverified' if (disc, name) in SCROLL_UNVERIFIED else 'hd'
                    row.setdefault('runtime_evidence', SCROLL_REPORT)
                    if (disc, name) == (1, 'BG2290'):
                        row.update(verified_in_game=True, runtime_evidence='docs/research/bg2290-native-pan.md#enhanced-donor-fade')
                    elif (disc, path) in SCENE_DRAWS:
                        row.update(verified_in_game=True, runtime_evidence=SCENE_DRAWS[(disc, path)][1])
                elif row['status'] == 'hd' and (disc, path) in SCENE_DRAWS:
                    row['verified_in_game'] = True
                    row['runtime_evidence'] = SCENE_DRAWS[(disc, path)][1]
                elif (disc, path) == (1, '/SAKURA2/EVE0116.BIN'):
                    row.update(status='hd', verified_in_game=True, runtime_evidence=EVE0116_REPORT)
                elif (disc, path) == (1, '/SAKURA2/EVE002.BIN'):
                    row.update(status='hd', verified_in_game=True, runtime_evidence=EVE002_REPORT)
                elif (disc, path) == (1, '/SAKURA2/EVE0118.BIN'):
                    row.update(status='hd', verified_in_game=True, runtime_evidence=EVE0118_REPORT)
                elif row['status'] != 'hd':
                    if name in {'BG1257', 'BG1280', 'BG2247'}:
                        row.update(status='excluded',
                                   reason='The PC composition does not follow the native camera.',
                                   decision_evidence='docs/research/scroll-table.md#remaining-dispositions-tp2a12')
                    elif name[2:3] in '34' or name == 'BG0000':
                        # Character cut-outs on a key colour and the blank picture are never replaced (tools/gen_scene_bg_table.py).
                        row['status'] = 'excluded'
                        row['reason'] = 'cut-out on a key colour or blank picture, not replaced by design'
                    elif pair.get('size') != [288, 144] or not path.startswith(('/SAKURA1/', '/SAKURA2/EVE')):
                        # The runtime draws a 288x144 picture only; wide and tall ones need scroll support (T105c).
                        row['status'] = 'unsupported-size'
                        row['reason'] = 'size %s, the runtime draws 288x144 pictures only' % (pair.get('size'),)
                        if (disc, path) == (1, '/SAKURA1/BG2290.BIN'):
                            row['reason'] = 'The live pan holds at x=0, where the tested PC crop misses the native composition before the aligned portion.'
                    else:
                        row['reason'] = 'palette shared with a picture that maps to another PC file (ambiguous)'
            elif name in bg_review['rejected'] or pair.get('tier') == 'missing':
                row['status'] = 'unpaired'
        elif path in screens and screens[path]['tier'] == 'content':
            row = {'status': 'paired-not-wired', 'pc': screens[path]['pc_file']}
            if path == '/SAKURA1/IC01.BIN':
                row['status'] = 'hd'
                row['verified_in_game'] = disc == 1
                if disc == 1:
                    row['runtime_evidence'] = 'docs/research/ic01-hd-intermission.md'
            elif (disc, path) == (1, '/SAKURA1/IC03.BIN'):
                row.update(status='hd', verified_in_game=True, runtime_evidence='docs/research/ic03-intermission-witness.md')
            elif (disc, path) == (1, '/SAKURA1/IC0501.BIN'):
                row.update(status='hd', verified_in_game=True,
                           runtime_evidence='docs/research/ic0501-intermission-witness.md#enhanced-presentation')
            elif (disc, path) == (2, '/SAKURA1/IC06.BIN'):
                row.update(status='hd', verified_in_game=True, runtime_evidence='docs/research/ic06-intermission-witness.md')
            elif (disc, path) == (2, '/SAKURA1/IC08.BIN'):
                row.update(status='hd', verified_in_game=True,
                           runtime_evidence='docs/research/ic-intermission-table.md#ic08-on-english-disc-2')
            elif (disc, path) == (2, '/SAKURA1/IC09.BIN'):
                row.update(status='hd', verified_in_game=False,
                           fixture_evidence='docs/research/ic-intermission-table.md#controlled-ic09-on-disc-2')
            elif disc == 1 and name in IC_TABLE_IDS:
                row.update(status='wired-unverified', verified_in_game=False,
                           runtime_table='config/hd-ic-table.json')
                if name in IC_CONTROLLED_IDS:
                    row.update(status='hd',
                               fixture_evidence='docs/research/ic-intermission-table.md#controlled-disc-1-runtime-verification')
                else:
                    row['reason'] = 'The disc-1 runtime IC table contains this plate. A displayed draw awaits verification.'
            else:
                row['reason'] = ('no saved state or route reaches this intermission, so its palette key, '
                                 'menu layers, darkening and anchor are unwitnessed; see docs/research/ic01-hd-intermission.md')
        elif name in EVE_PAIRS:
            row = {'status': 'paired-not-wired', 'pc': 'SAKURA2/BG/' + EVE_PAIRS[name] + '.SPR'}
        elif kind == 'bodies' and name in body_review.get('registered_silhouettes', {}):
            row = {
                'status': 'hd',
                'pc': f'SAKURA1/NC/{name}.SPR',
                'native_face_fallback': True,
            }
            proof = body_review['registered_silhouettes'][name]
            if name in ('NC3290', 'NC3517'):
                if disc == (1 if name == 'NC3290' else 2):
                    row.update(verified_in_game=True, runtime_evidence=proof)
            else:
                row['fixture_evidence'] = proof
        elif kind == 'bodies' and name in body_review.get('paired_not_wired', {}):
            row = {
                'status': 'paired-not-wired',
                'pc': f'SAKURA1/NC/{name}.SPR',
                'reason': body_review['paired_not_wired'][name],
                'pairing_evidence': 'docs/research/saturn-bg-format.md#tp5a-bounded-body-crops',
            }
        elif path in bodies:
            pair = bodies[path]
            if name in body_review['rejected']:
                row['status'] = 'unpaired'
            elif name in body_runtime:
                row = {'status': 'hd',
                       'pc': 'SAKURA1/NC/' + (pair['best_pc'] if pair['tier'] == 'content' else pair['same_name_pc'])}
                if (disc, path) == (1, '/SAKURA1/NC3058.BIN'):
                    row.update(verified_in_game=True, native_face_fallback=True,
                               runtime_evidence='docs/research/nc3058-cutout-1440p.md')
                elif (disc, path) in EXACT_BODY_DRAWS:
                    row.update(verified_in_game=True, runtime_evidence=EXACT_BODY_DRAWS[(disc, path)][1])
                elif (disc, path) == (2, '/SAKURA1/NC81.BIN'):
                    row.update(verified_in_game=True, native_face_fallback=True, runtime_evidence='docs/research/nc81-nc90-1440p.md')
                elif (disc, path) == (1, '/SAKURA1/NC90.BIN'):
                    row.update(verified_in_game=True, runtime_evidence='docs/research/nc81-nc90-1440p.md')
                elif (disc, path) == (1, '/SAKURA1/NC56.BIN'):
                    row.update(verified_in_game=True, runtime_evidence='docs/research/nc56-registered-faces.md')
                elif (disc, path) == (1, '/SAKURA1/NC51.BIN'):
                    row.update(verified_in_game=True, native_face_fallback=True, runtime_evidence='docs/research/nc51-registered-faces.md')
                elif (disc, path) == (1, '/SAKURA1/NC96.BIN'):
                    row.update(verified_in_game=True, runtime_evidence='docs/research/nc96-registered-faces.md')
                elif (disc, path) == (1, '/SAKURA1/NC21.BIN'):
                    row.update(verified_in_game=True, native_face_fallback=True, runtime_evidence='docs/research/nc21-registered-faces.md')
                elif (disc, path) == (1, '/SAKURA1/NC32.BIN'):
                    row.update(verified_in_game=True, native_face_fallback=True, runtime_evidence='docs/research/nc32-registered-faces.md')
                elif (disc, path) == (1, '/SAKURA1/NC12.BIN'):
                    row.update(verified_in_game=True, native_face_fallback=True, runtime_evidence='docs/research/nc12-registered-faces.md')
                elif (disc, path) == (2, '/SAKURA1/NC3018.BIN'):
                    row.update(verified_in_game=True, runtime_evidence='docs/research/nc3018-registered-faces.md')
                else:
                    row['verified_in_game'] = name in BODY_DRAWS
                if name in BODY_DRAWS:
                    row['native_face_fallback'] = True
                    row['runtime_evidence'] = BODY_FACE_EVIDENCE.get((disc, path), BODY_REPORT)
        elif path in items:
            pair = items[path]
            if pair['tier'] == 'content' or item_review.get(path, {}).get('verdict') == 'confirmed':
                row = {'status': 'paired-not-wired', 'pc': pair['pc_file'], 'pc_image_index': pair['pc_image_index']}
                if pair['palette_fnv'].upper() in item_runtime:
                    anchor = '#item09-hair-ornament' if name == 'ITEM09' else '#item-detail-sprite-witness-t109'
                    row.update(status='hd', runtime_evidence=MENU_REPORT + anchor)
                    if name in ('ITEM03', 'ITEM12', 'ITEM27'):
                        row['runtime_evidence'] = MENU_REPORT + '#item03-item12-and-item27'
                    if (disc, name) == (1, 'ITEM12'):
                        row['verified_in_game'] = True
            elif path in item_review:
                row['status'] = 'unpaired'
        if kind == 'portraits' and f'{disc}:{path}' in fce_atlases and row['status'] == 'unknown':
            row.update(fce_atlas_row(fce_atlases[f'{disc}:{path}'], recipes))
        if path in cold_bg and disc == 1:
            row['cold_run_frame'] = cold_bg[path]
        if ident == CHAPTER2_FACE_BANK:
            key = f'{disc}:{path}'
            add('portraits', key, {'status': 'unknown', 'scope': 'tactical portrait bank'},
                2, 'resident', CHAPTER2_FACE_REPORT)
            for slot, pc_index in CHAPTER2_FACE_BASE_PAIRS.items():
                add('portraits', f'{key}#{slot}', {
                    'status': 'hd',
                    'scope': 'tactical portrait base only',
                    'verified_in_game': True,
                    'runtime_evidence': CHAPTER2_FACE_RUNTIME_REPORT,
                    'pc': 'SAKURA2/SYSTEM/KAOSLG.SPR',
                    'pc_index': pc_index,
                }, 2, 'observed', CHAPTER2_FACE_REPORT)
        if kind:
            key = f'{disc}:{path}'
            witnesses = [
                (episode, evidence) for episode, (files, evidence) in NATIVE_ROUTE_FILES.items()
                if disc == disc_for(episode) and path == f'/SAKURA1/{name}.BIN' and name in files
            ]
            if chapter is not None or not witnesses:
                add(kind, key, row, chapter, association, report)
            for episode, evidence in witnesses:
                if chapter != episode:
                    occurrence = {k: v for k, v in row.items() if k != 'runtime_evidence'}
                    proof = NATIVE_ROUTE_DRAWS.get((episode, disc, path))
                    if proof:
                        occurrence.update(verified_in_game=True, runtime_evidence=proof)
                    elif 'verified_in_game' in occurrence:
                        occurrence['verified_in_game'] = False
                    add(kind, key, occurrence, episode, 'observed', evidence)

        for stream in resource['video_streams']:
            offset = stream['offset']
            _, fad = film_key(resource, offset)
            film = films.get((disc, fad))
            row = {'status': 'unknown', 'fad': fad}
            if film and film['file'] == path:
                row['status'] = 'unpaired'
                if movie := film.get('movie'):
                    spans = bounded_films.get((disc, movie))
                    row.update(status='bounded' if spans else 'excluded' if film['alternate_cut'] else 'hd',
                               pc=movie, alternate_cut=film['alternate_cut'])
                    if spans:
                        row.update(pc_video_spans=spans, audio='saturn')
                    elif film['alternate_cut']:
                        row['reason'] = 'alternate PC edit stays native to preserve the Saturn timing'
                elif path == '/SAKURA1/OPSAKURA.CPK' and 0 < film.get('duration', 0) < 0.5:
                    row.update(status='excluded', reason='short native transition without a PC clip')
            chapter, report = observed.get((ident, offset), (None, None))
            if (disc == 1 and path == '/SAKURA4' and offset in CHAPTER1_ROUTE_FILMS
                    and row.get('pc') == CHAPTER1_ROUTE_FILMS[offset]):
                chapter, report = 1, CHAPTER1_ROUTE_REPORT
            if (disc, path, fad, row.get('pc')) == (1, '/SAKURA4', 80874, 'MOVIE019'):
                chapter, report = 7, 'docs/research/th7-native-attribution.md'
            if path == '/SAKURA4' and row['status'] == 'bounded':
                if (disc, row['pc']) == (1, 'MOVIE004'):
                    chapter, report = 1, 'docs/research/bounded-film-video-spans.md#movie004'
                elif (disc, row['pc']) == (1, 'MOVIE011'):
                    chapter, report = 3, 'docs/research/bounded-film-video-spans.md#movie011'
                if row['pc'] in ('MOVIE004', 'MOVIE011') and report:
                    row.update(verified_in_game=True, runtime_evidence=report)
            add('film', f'{disc}:{path}+{offset}', row, chapter,
                'observed' if chapter else 'unknown', report)
    census = load(root / MENU_CENSUS)
    for file in census['menus']:
        name = file['pc_path']
        if name in SYSTEM_HUD_EXCLUDED:
            unassigned['menus-hud']['pc:' + name] = {
                'status': 'excluded', 'pc': name, 'images': len(file['images']), 'association': 'unknown',
                'reason': SYSTEM_HUD_EXCLUDED[name]}
        for image in file['images']:
            if (name, image['index']) in SYSTEM_HUD_DRAWS:
                note, evidence = SYSTEM_HUD_DRAWS[(name, image['index'])]
                row = {
                    'status': 'hd', 'pc': name, 'pc_image_index': image['index'], 'association': 'unknown',
                    'draw': note, 'runtime_evidence': evidence}
                if (name, image['index']) in {
                    ('SAKURA1/SYSTEM/SISTEM.SPR', 8), ('SAKURA1/SYSTEM/SISTEM.SPR', 9),
                    ('SAKURA1/SYSTEM/TUIKA_W.SPR', 0),
                    ('SAKURA1/SYSTEM/WINDOW.SPR', 0),
                    ('SAKURA1/SYSTEM/WINDOW.SPR', 1),
                    ('SAKURA1/SYSTEM/SISTEM.SPR', 11),
                    ('SAKURA1/SYSTEM/SISTEM.SPR', 14),
                    ('SAKURA1/SYSTEM/SISTEM.SPR', 1),
                    ('SAKURA1/SYSTEM/SISTEM.SPR', 4),
                    ('SAKURA1/SYSTEM/OPTION.SPR', 1),
                    ('SAKURA1/SYSTEM/SISTEM.SPR', 12),
                    ('SAKURA1/SYSTEM/SISTEM.SPR', 2),
                    ('SAKURA1/SYSTEM/SISTEM.SPR', 5),
                    ('SAKURA1/SYSTEM/WINDOW.SPR', 2),
                }:
                    row['verified_in_game'] = True
                unassigned['menus-hud'][f"pc:{name}#{image['index']}"] = row
    hud_census = {
        'system_images': sum(len(file['images']) for file in census['menus']),
        'item_images': len({(p['pc_file'], p['pc_image_index']) for p in config('hd-item-map')['pairs']}),
    }
    for portrait in portraits:
        ident = portrait['id']
        if not re.fullmatch('[0-9a-f]{4}', ident):
            raise ValueError(f'Invalid portrait identity {ident!r}')
        sources = sorted(portrait.get('chapter1_sources', []))
        for source in sources:
            disc, _, path = source.partition(':')
            if disc not in ('1', '2') or indexed_chapter(path) != 1:
                raise ValueError(f'Invalid chapter 1 portrait source for {ident}')
        row = {'status': 'hd', 'pc_index': recipes[ident]} if ident in recipes else {'status': 'unpaired'}
        if ident not in recipes and ident in NATIVE_PORTRAIT_DECISIONS:
            row.update(NATIVE_PORTRAIT_DECISIONS[ident], pairing_evidence=RESIDUAL_PORTRAIT_REPORT)
        if sources:
            row['atlases'] = sources
        if ident == '00a1':
            occurrence = dict(row, verified_in_game=True, runtime_evidence=IRIS_COMMAND_ROOM_REPORT)
            add('portraits', ident, occurrence, 1, 'observed', IRIS_COMMAND_ROOM_REPORT)
        elif ident == '0169':
            occurrence = dict(row, verified_in_game=True, runtime_evidence=EMBLEM_LETTER_REPORT)
            add('portraits', ident, occurrence, 1, 'observed', EMBLEM_LETTER_REPORT)
        elif ident in CHAPTER1_ROUTE_PORTRAITS:
            chapter1_portrait = row
            if ident == '0176':
                chapter1_portrait = dict(row, verified_in_game=True, runtime_evidence=MARIA_STRIP_REPORT)
            add('portraits', ident, chapter1_portrait, 1, 'observed', CHAPTER1_ROUTE_REPORT)
        elif sources or not any(ident in atlases for atlases, _ in NATIVE_ROUTE_PORTRAITS.values()):
            add('portraits', ident, row, 1 if sources else None,
                'inferred' if sources else 'unknown', PORTRAIT_REPORT if sources else None)
        for episode, (atlases, evidence) in NATIVE_ROUTE_PORTRAITS.items():
            if ident in atlases:
                occurrence = dict(row, atlases=[atlases[ident]])
                if episode == 3 and ident in CHAPTER3_PORTRAIT_DRAWS:
                    occurrence.update(verified_in_game=True, runtime_evidence=CHAPTER3_PORTRAIT_REPORT)
                elif episode == 5 and ident in CHAPTER5_PORTRAIT_DRAWS:
                    occurrence.update(verified_in_game=True, runtime_evidence=CHAPTER5_PORTRAIT_REPORT)
                elif episode == 9 and ident == '00e9':
                    occurrence.update(verified_in_game=True, runtime_evidence=YONEDA_STORAGE_REPORT)
                add('portraits', ident, occurrence, episode, 'observed', evidence)

    map02_event_report = 'docs/research/tactical-pairing.md#prueba-aislada-en-el-renderizador'
    add('scene-pictures', '1:/SAKURA2/EVS02100.BIN#36', {
        'status': 'hd', 'pc': 'SAKURA2/EVENT/MAP00/EV00S24.SPR', 'pc_index': 0,
        'verified_in_game': True, 'runtime_evidence': map02_event_report,
    }, 2, 'observed', map02_event_report)

    add('scene-pictures', 'pc:SAKURA1/ICATCH/KAO_P.SPR', {
        'status': 'excluded',
        'pc': 'SAKURA1/ICATCH/KAO_P.SPR',
        'reason': 'All 25 bases are exact copies of KAO.SPR base regions counted as portraits.',
    }, evidence='docs/research/ic-intermission-table.md#remaining-icatch-file-roles')

    for heroine in ('AI', 'KA', 'KO', 'MA', 'SA', 'SU'):
        staff = f'SAKURA1/ENDING/STAFF_{heroine}.SPR'
        add('scene-pictures', 'pc:' + staff, {
            'status': 'excluded',
            'pc': staff,
            'reason': 'PC-specific precomposed credits omit native credits and change the copyright line.',
        }, evidence='docs/research/ending-bank-pairs.md#staff-banks-and-native-credits')

    duplicate_groups = config('hd-scene-file-duplicates')['groups']
    duplicate_identities = {path: min(group) for group in duplicate_groups for path in group}
    for resources in [unassigned, *(chapter['resources'] for chapter in chapters.values())]:
        for row in resources['scene-pictures'].values():
            if (identity := duplicate_identities.get(row.get('pc'))) is not None:
                row['pc_identity'] = identity

    scene_files = {
        row['pc']
        for group in [unassigned, *(chapter['resources'] for chapter in chapters.values())]
        for row in group['scene-pictures'].values() if row.get('pc')
    }
    scene_aliases = {source: next(iter(targets))
                     for source, targets in scene_alias_candidates.items()
                     if source not in scene_files and len(targets) == 1}
    return {
        'schema': 1,
        'status': {
            'hd': 'Implemented: the runtime table holds it and the runtime draws it when it appears (for a body, a documented draw sets verified_in_game). Seeing it in a replay is separate.',
            'wired-unverified': 'In the runtime table and tried whenever it appears, but nobody has recorded seeing it in game. The work is verification, not wiring.',
            'paired-not-wired': 'Accepted counterpart that is genuinely not in the runtime table (for example an ambiguous palette). Check `reason` first.',
            'bounded': 'Aligned PC picture spans on the Saturn timing, with native picture in their gaps and Saturn audio throughout.',
            'excluded': 'Native by design (key-colour cut-outs, blank pictures, alternate film edits or native transitions).',
            'unsupported-size': 'Accepted counterpart whose size the runtime cannot draw yet (not 288x144): needs scroll or size support (T105c).',
            'unpaired': 'The catalog records a rejected or absent counterpart.',
            'unknown': 'Pairing or integration is not established by the input catalogs.',
        },
        'association': {
            'observed': 'The resource is identified in runtime evidence for this chapter.',
            'resident': 'The resource matches in RAM during the chapter, without evidence it was drawn.',
            'inferred': 'Episode file numbering or chapter 1 atlas membership provides a candidate.',
            'unknown': 'No chapter attribution in the inputs.',
        },
        'hud_census': hud_census,
        'scene_file_aliases': scene_aliases,
        'scene_file_duplicate_groups': duplicate_groups,
        'pc_body_alternates': {row['saturn']: row['alternate_pc']
                               for row in config('hd-body-alternates')['alternate_files']},
        'chapters': list(chapters.values()),
        'unassigned': unassigned,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', type=Path, required=True, help='directory generated by build_scene_index.py')
    parser.add_argument('--portrait-audit', type=Path, required=True, help='portrait-coverage.json from audit_portrait_coverage.py')
    parser.add_argument('--output', type=Path, default=ROOT / 'config/hd-chapter-coverage.json')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        result = build(ROOT, args.index, args.portrait_audit)
        expected = json.dumps(result, indent=2, sort_keys=True) + '\n'
        if args.check:
            if args.output.read_text(encoding='utf-8') != expected:
                parser.exit(1, 'Regenerate the HD chapter coverage JSON.\n')
        else:
            args.output.write_text(expected, encoding='utf-8', newline='\n')
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
