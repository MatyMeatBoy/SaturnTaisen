"""Create a Spanish launcher profile and a local shortcut, without touching the owner's profile.

  python -X utf8 tools/es/perfil_es.py --base local/profiles/chapter1-preview --app local/releases/<build>

The launcher reads its disc from launcher.ini ([game] disc=...). The Spanish profile is a copy of
--base with that key pointing at local/prepared/disc1-es/game.cue, so saves, logs and settings of the
Spanish mode stay separate. Writes «Jugar en español.bat» next to the owner checkout (not tracked).
Until the launcher has its own language option (docs/research/traduccion-espanol.md), this is the
supported way to play in Spanish.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _rutas import OWNER  # noqa: E402


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base', type=Path, required=True, help='existing launcher profile folder to copy settings from')
    p.add_argument('--app', type=Path, required=True, help='release folder containing SaturnTaisenFirst.exe')
    p.add_argument('--perfil', type=Path, default=OWNER / 'local/profiles/espanol')
    a = p.parse_args()
    disc = (OWNER / 'local/prepared/disc1-es/game.cue').resolve()
    if not disc.is_file():
        raise SystemExit(f'falta {disc}: ejecuta antes tools/es/construir_disco_es.py')
    base, profile, app = a.base.resolve(), a.perfil.resolve(), a.app.resolve()
    if not (app / 'SaturnTaisenFirst.exe').is_file():
        raise SystemExit(f'no hay SaturnTaisenFirst.exe en {app}')
    profile.mkdir(parents=True, exist_ok=True)
    ini = (base / 'launcher.ini').read_text(encoding='utf-8') if (base / 'launcher.ini').is_file() else '[game]\n'
    if re.search(r'(?m)^disc=', ini):
        ini = re.sub(r'(?m)^disc=.*$', lambda _: f'disc={disc}', ini)
    else:
        ini = ini.replace('[game]\n', f'[game]\ndisc={disc}\n') if '[game]' in ini else ini + f'\n[game]\ndisc={disc}\n'
    (profile / 'launcher.ini').write_text(ini, encoding='utf-8')
    if (base / 'settings.ini').is_file() and not (profile / 'settings.ini').exists():
        shutil.copy2(base / 'settings.ini', profile / 'settings.ini')
    bat = OWNER / 'Jugar en español.bat'
    bat.write_text('@echo off\r\nsetlocal\r\n'
                   f'set "SATURN_TAISEN_FIRST_HOME={profile}"\r\n'
                   'set "SATRECOMP_STRICT_NATIVE=1"\r\n'
                   f'start "" /d "{app}" "{app}\\SaturnTaisenFirst.exe" --play\r\n', encoding='cp1252')
    print('perfil español:', profile)
    print('acceso:', bat)


if __name__ == '__main__':
    main()
