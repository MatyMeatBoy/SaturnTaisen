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
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _rutas import OWNER, distinct_output, private_path, write_bytes  # noqa: E402



def disc_settings(ini: str, disc: Path) -> str:
    section = re.search(r'(?m)^\s*\[game\][ \t]*$', ini)
    if not section:
        return ini.rstrip('\n') + f'\n[game]\ndisc={disc}\n'
    next_section = re.search(r'(?m)^[ \t]*\[', ini[section.end():])
    end = section.end() + next_section.start() if next_section else len(ini)
    game = ini[section.end():end]
    game, replaced = re.subn(r'(?m)^[ \t]*disc[ \t]*=.*$', lambda _: f'disc={disc}', game)
    if not replaced:
        game = f'\ndisc={disc}\n' + game.lstrip('\n')
    return ini[:section.end()] + game + ini[end:]


def launcher_shortcut(profile: Path, app: Path) -> bytes:
    def quote(path):
        return str(path).replace('%', '%%')

    return ('@chcp 65001 >nul\r\n@echo off\r\nsetlocal DisableDelayedExpansion\r\n'
            f'set "SATURN_TAISEN_FIRST_HOME={quote(profile)}"\r\n'
            'set "SATRECOMP_STRICT_NATIVE=1"\r\n'
            f'start "" /d "{quote(app)}" "{quote(app / "SaturnTaisenFirst.exe")}" --play\r\n').encode('utf-8')

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base', type=Path, required=True, help='existing launcher profile folder to copy settings from')
    p.add_argument('--app', type=Path, required=True, help='release folder containing SaturnTaisenFirst.exe')
    p.add_argument('--perfil', type=Path, default=OWNER / 'local/profiles/espanol')
    a = p.parse_args()
    disc = (OWNER / 'local/prepared/disc1-es/game.cue').resolve()
    if not disc.is_file():
        raise SystemExit(f'falta {disc}: ejecuta antes tools/es/construir_disco_es.py')
    base, app = a.base.resolve(), a.app.resolve()
    if not (app / 'SaturnTaisenFirst.exe').is_file():
        raise SystemExit(f'no hay SaturnTaisenFirst.exe en {app}')
    try:
        profile = private_path(a.perfil, OWNER)
        distinct_output(profile, base)
        ini_src, settings_src = base / 'launcher.ini', base / 'settings.ini'
        ini_dst, settings_dst = profile / 'launcher.ini', profile / 'settings.ini'
        bat = OWNER / 'Jugar en español.bat'
        for output in (ini_dst, settings_dst, bat):
            distinct_output(output, ini_src, settings_src, disc)
        template = ini_dst if ini_dst.is_file() else ini_src
        ini = template.read_text(encoding='utf-8-sig') if template.is_file() else '[game]\n'
        shortcut = launcher_shortcut(profile, app)
        data = disc_settings(ini, disc).encode('utf-8')
        settings = settings_src.read_bytes() if settings_src.is_file() and not settings_dst.exists() else None
        write_bytes(ini_dst, data)
        if settings is not None:
            write_bytes(settings_dst, settings)
        write_bytes(bat, shortcut)
    except (OSError, ValueError) as error:
        raise SystemExit(str(error)) from error
    print('perfil español:', profile)
    print('acceso:', bat)


if __name__ == '__main__':
    main()
