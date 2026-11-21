"""Smoke-test linked tactical grounds in batches, with full controls for beta testing."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import tactical_ground_probe as probe


QUICK_PROFILES = (('donor', 'donor', 1), ('missing', 'missing', 1))
BETA_PROFILES = QUICK_PROFILES + (
    ('corrupt', 'corrupt', 1),
    ('original-donor', 'donor', 0), ('original-missing', 'missing', 0),
)


def hash_file(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify_case(settings, case, destination):
    relative = probe.ground_file(case['map'])
    source = settings.pc_root / relative
    if hash_file(source) != case['donor_sha256'].lower():
        raise ValueError(f'{relative}: unexpected donor SHA-256')
    args = SimpleNamespace(
        exe=settings.exe, disc=Path(case['disc']).resolve(), state=Path(case['state']).resolve(),
        backup=Path(case['backup']).resolve(), movie=Path(case['movie']).resolve() if case.get('movie') else None,
        pc_assets=settings.pc_root, frames=case.get('frames', 90), timeout=settings.timeout, size=settings.size,
    )
    if args.frames < 8:
        raise ValueError('A replay must contain at least eight frames')
    errors = probe.preflight(SimpleNamespace(**vars(args), map=case['map']))
    if errors:
        raise ValueError('; '.join(errors))
    if args.movie and not args.movie.is_file():
        raise ValueError(f'Replay movie not found: {args.movie}')
    destination.mkdir()
    assets = {name: destination / f'assets-{name}' for name in ('donor', 'missing', 'corrupt')}
    assets['missing'].mkdir()
    donor = assets['donor'] / relative
    donor.parent.mkdir(parents=True)
    shutil.copyfile(source, donor)
    if settings.beta:
        damaged = bytearray(donor.read_bytes())
        damaged[len(damaged) // 2] ^= 1
        corrupt = assets['corrupt'] / relative
        corrupt.parent.mkdir(parents=True)
        corrupt.write_bytes(damaged)

    def replay(profile):
        name, asset_key, mode = profile
        command, env, run, shots = probe.run_once(args, destination / name, assets[asset_key])
        file = run / 'settings.ini'
        file.write_text(file.read_text().replace('presentation_mode=1', f'presentation_mode={mode}'))
        env.update(SATURN_TAISEN_FIRST_HOME=str(run), SDL_AUDIODRIVER='dummy')
        with subprocess.Popen(command, cwd=run, env=env,
                              stdout=subprocess.DEVNULL, stderr=subprocess.PIPE) as process:
            try:
                code, log = probe.finish(process, run, args)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                raise ValueError(f'{name}: replay timed out') from None
        guest = (run / 'guest.hash').read_bytes() if (run / 'guest.hash').is_file() else b''
        if code or not probe.guest_evidence_valid(guest, log, args.frames):
            raise ValueError(f'{name}: replay did not complete in strict AOT, see {run / "stderr.log"}')
        return name, (shots, hashlib.sha256(guest).hexdigest(), hash_file(run / 'backup.bin'))

    profiles = BETA_PROFILES if settings.beta else QUICK_PROFILES
    with ThreadPoolExecutor(max_workers=settings.jobs) as pool:
        results = dict(pool.map(replay, profiles))

    if len({proof[1:] for proof in results.values()}) != 1:
        raise ValueError('Guest trace or final SRAM differs across profiles')
    rect = probe.centre_rect(*probe.parse_size(settings.size))
    counts = {}
    comparisons = [('donor', 'missing', case.get('expect', 'drawn'))]
    if settings.beta:
        comparisons.extend((('corrupt', 'missing', 'not-drawn'),
                            ('original-donor', 'original-missing', 'not-drawn')))
    for left, right, expected in comparisons:
        changes = [probe.region_changes(a, b, rect)
                   for a, b in zip(results[left][0], results[right][0])]
        if any(change is None or change[1] for change in changes) or probe.classify(changes)[0] != expected:
            raise ValueError(f'{left}/{right}: expected {expected} with no changes outside the centre: {changes}')
        counts[left] = changes
    return {'map': case['map'], 'state_sha256': hash_file(args.state), 'frames': args.frames,
            'guest_sha256': results['donor'][1], 'sram_sha256': results['donor'][2], 'rgb_changes': counts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True, help='JSON array of explicitly selected cases')
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--pc-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='new evidence directory')
    parser.add_argument('--size', default='2560x1440')
    parser.add_argument('--timeout', type=int, default=180)
    parser.add_argument('--jobs', type=int, choices=(1, 2), default=2)
    parser.add_argument('--beta', action='store_true', help='also run corrupt and Original controls')
    args = parser.parse_args()
    args.exe, args.pc_root, args.output = args.exe.resolve(), args.pc_root.resolve(), args.output.resolve()
    if args.output.is_relative_to(args.pc_root) or args.timeout < 1:
        parser.error('Use a positive timeout and an output outside the PC extraction')
    try:
        cases = json.loads(args.manifest.read_text(encoding='utf-8-sig'))
        if not isinstance(cases, list) or not cases:
            raise ValueError('The manifest must contain a non-empty array of cases')
        exe_hash = hash_file(args.exe)
        args.output.mkdir(parents=True)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    report = {'exe_sha256': exe_hash, 'size': args.size,
              'mode': 'beta' if args.beta else 'smoke', 'cases': []}
    for index, case in enumerate(cases, 1):
        folder = args.output / f'case-{index:03}'
        try:
            result = {'status': 'passed', **verify_case(args, case, folder)}
        except (KeyError, TypeError, OSError, ValueError) as error:
            result = {'status': 'failed', 'error': str(error)}
        report['cases'].append(result)
        (args.output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        print(f'{folder.name}: {result["status"]}', flush=True)
    return int(any(result['status'] != 'passed' for result in report['cases']))


if __name__ == '__main__':
    raise SystemExit(main())
