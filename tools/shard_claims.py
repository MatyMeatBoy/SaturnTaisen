"""Claims on the shard rows of docs/PENDIENTES.md, and the release of stale ones (owner rule, 2026-11-19: a shard nobody has worked on for
30 minutes goes back to the pool).

A worker claims a row in a first small PR:

    python tools/shard_claims.py --claim TW1 --who <name> --branch pendientes/<branch>

which puts `CLAIM[<name>|<branch>|<UTC time>]` at the start of the row's status cell. The claim stays valid while the branch has a commit (local
or on origin) newer than the limit, or the claim itself is newer than the limit. The coordinator (or any worker) runs

    python tools/shard_claims.py --release-stale [--minutes 30] [--dry-run]

and every claim older than the limit with no newer commit becomes `open · released (stale claim of <name>, <time>)`. `--list` shows the
claims and their age. Only rows whose first cell is an ID are touched.
"""
import argparse, datetime, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE = ROOT / 'docs/PENDIENTES.md'
CLAIM = re.compile(r'CLAIM\[([^|\]]+)\|([^|\]]*)\|([0-9T:\-]+Z)\]')
FORMAT = '%Y-%m-%dT%H:%M:%SZ'


def parse_time(text):
    return datetime.datetime.strptime(text, FORMAT).replace(tzinfo=datetime.timezone.utc)


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc)


def row_cells(line):
    """(id, [cells]) of a queue row, or None."""
    if not line.startswith('| '):
        return None
    cells = [c.strip() for c in line.strip().strip('|').split('|')]
    if len(cells) < 4 or not re.fullmatch(r'T[A-Za-z0-9]+', cells[0]):
        return None
    return cells[0], cells


def add_claim(lines, row_id, who, branch, when):
    """Puts the claim at the start of the status cell of the row; refuses a row that is already claimed."""
    out, done = [], False
    for line in lines:
        parsed = row_cells(line)
        if parsed and parsed[0] == row_id and not done:
            if CLAIM.search(line):
                raise ValueError('%s is already claimed: %s' % (row_id, CLAIM.search(line).group(0)))
            token = 'CLAIM[%s|%s|%s] ' % (who, branch, when.strftime(FORMAT))
            parts = line.split('|')
            # parts: ['', id, P, type, status, ...]: the status cell is the fourth one after the id
            index = 4
            parts[index] = ' ' + token + parts[index].lstrip()
            line = '|'.join(parts)
            done = True
        out.append(line)
    if not done:
        raise ValueError('row %s not found' % row_id)
    return out


def last_activity(branch, claim_time, commit_time):
    """Latest of the claim time and the last commit of the branch (None if the branch has none)."""
    return max(claim_time, commit_time) if commit_time else claim_time


def release_stale(lines, now, minutes, commit_time_of):
    """(new lines, [released (row id, who, branch, age minutes)])."""
    limit = datetime.timedelta(minutes=minutes)
    out, released = [], []
    for line in lines:
        parsed = row_cells(line)
        match = CLAIM.search(line) if parsed else None
        if match:
            who, branch, text = match.groups()
            since = last_activity(branch, parse_time(text), commit_time_of(branch))
            if now - since > limit:
                line = line.replace(match.group(0), 'open · released (stale claim of %s, %s)' % (who, text), 1)
                released.append((parsed[0], who, branch, int((now - since).total_seconds() // 60)))
        out.append(line)
    return out, released


def git_commit_time(branch):
    """Committer time of the newest commit on the branch, local or origin; None if the branch does not exist."""
    best = None
    for ref in (branch, 'origin/' + branch):
        result = subprocess.run(['git', 'log', '-1', '--format=%ct', ref], cwd=ROOT, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            stamp = datetime.datetime.fromtimestamp(int(result.stdout.strip()), datetime.timezone.utc)
            best = stamp if best is None else max(best, stamp)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--claim'); ap.add_argument('--who'); ap.add_argument('--branch', default='')
    ap.add_argument('--release-stale', action='store_true'); ap.add_argument('--list', action='store_true')
    ap.add_argument('--minutes', type=int, default=30); ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    text = QUEUE.read_text(encoding='utf-8')
    newline = '\r\n' if '\r\n' in text else '\n'
    lines = text.split(newline)
    if a.claim:
        if not a.who:
            sys.exit('--who is required')
        lines = add_claim(lines, a.claim, a.who, a.branch, now_utc())
        print('claimed', a.claim, 'for', a.who)
    elif a.release_stale:
        lines, released = release_stale(lines, now_utc(), a.minutes, git_commit_time)
        for row, who, branch, age in released:
            print('released %s (%s, %s, idle %d min)' % (row, who, branch or 'no branch', age))
        if not released:
            print('no stale claims')
    else:
        for line in lines:
            parsed = row_cells(line)
            match = CLAIM.search(line) if parsed else None
            if match:
                who, branch, stamp = match.groups()
                since = last_activity(branch, parse_time(stamp), git_commit_time(branch))
                print('%s: %s on %s, idle %d min' % (parsed[0], who, branch or '-', (now_utc() - since).total_seconds() // 60))
        return
    if not a.dry_run:
        QUEUE.write_text(newline.join(lines), encoding='utf-8', newline='')


if __name__ == '__main__':
    main()
