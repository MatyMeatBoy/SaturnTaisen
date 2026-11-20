"""Claims on the shard rows of docs/PENDIENTES.md.

A worker reserves a row on its branch before starting:

    python tools/shard_claims.py --claim THD38 --who <name> --branch pendientes/<branch>

which puts `CLAIM[<name>|<branch>|<UTC time>]` at the start of the row's status cell. The claim stays valid while the branch has a commit (local
or on origin) newer than the limit, or the claim itself is newer than the limit. The coordinator (or any worker) runs

    python tools/shard_claims.py --release-stale [--minutes 30] [--dry-run]

and every claim older than the limit with no newer commit returns to its
previous status. The release is printed with the owner and age.
"""
import argparse, datetime, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE = ROOT / 'docs/PENDIENTES.md'
CLAIM = re.compile(r'CLAIM\[([^|\\\]]+)\\?\|([^|\\\]]*)\\?\|([0-9T:\-]+Z)\]')
SHARD_ID = re.compile(r'\bT[A-Za-z0-9]*\d[A-Za-z0-9]*\b')
FORMAT = '%Y-%m-%dT%H:%M:%SZ'


def parse_time(text):
    return datetime.datetime.strptime(text, FORMAT).replace(tzinfo=datetime.timezone.utc)


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc)


def queue_row(line):
    """Return the shard ID and the parts around its status cell."""
    if not line.startswith('| '):
        return None
    columns = line.split('|', 3)
    if len(columns) < 4:
        return None
    _, row_id, second, _ = columns
    row_id = row_id.strip()
    if not SHARD_ID.fullmatch(row_id):
        return None
    if re.fullmatch(r'P\d+', second.strip()):
        status_index = 4
    elif row_id.startswith('THD'):
        status_index = 2
    else:
        return None
    parts = line.split('|', status_index)
    if len(parts) <= status_index:
        return None
    prefix = '|'.join(parts[:status_index]) + '|'
    tail = parts[status_index].lstrip()
    match = CLAIM.match(tail)
    token = match.group(0) if match else ''
    status, separator, rest = tail[len(token):].lstrip().partition('|')
    if not separator:
        return None
    return row_id, prefix, match, status, separator + rest


def add_claim(lines, row_id, who, branch, when):
    """Puts the claim at the start of the status cell of the row; refuses a row that is already claimed."""
    if not CLAIM.fullmatch(f'CLAIM[{who}|{branch}|{when.strftime(FORMAT)}]') or any(
        char in who + branch for char in '\r\n'
    ):
        raise ValueError('invalid claim owner or branch')
    out, done = [], False
    for line in lines:
        parsed = queue_row(line)
        if parsed and parsed[0] == row_id and not done:
            _, prefix, match, status, rest = parsed
            if match:
                raise ValueError('%s is already claimed: %s' % (row_id, match.group(0)))
            if status.strip() not in ('open', 'free') and not status.startswith('open · released (stale claim of '):
                raise ValueError(f'{row_id} is not available: {status.strip()}')
            token = r'CLAIM[%s\|%s\|%s] ' % (who, branch, when.strftime(FORMAT))
            line = prefix + ' ' + token + status + rest
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
        parsed = queue_row(line)
        match = parsed[2] if parsed else None
        if match:
            who, branch, text = match.groups()
            since = last_activity(branch, parse_time(text), commit_time_of(branch))
            if now - since > limit:
                _, prefix, _, status, rest = parsed
                line = prefix + ' ' + status + rest
                released.append((parsed[0], who, branch, int((now - since).total_seconds() // 60)))
        out.append(line)
    return out, released


def git_commit_time(branch):
    """Committer time of the newest commit on the branch, local or origin; None if the branch does not exist."""
    if not branch:
        return None
    best = None
    for ref in ('refs/heads/' + branch, 'refs/remotes/origin/' + branch):
        result = subprocess.run(['git', 'log', '-1', '--format=%ct', ref, '--'], cwd=ROOT, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            stamp = datetime.datetime.fromtimestamp(int(result.stdout.strip()), datetime.timezone.utc)
            best = stamp if best is None else max(best, stamp)
    return best


def open_prs():
    result = subprocess.check_output(
        ['gh', 'pr', 'list', '--limit', '200', '--json', 'number,title,headRefName,headRefOid'],
        cwd=ROOT, encoding='utf-8')
    return json.loads(result)


def open_pr_claims(prs):
    """Read claims from open PR heads, including those not merged into the queue."""
    for pr in prs:
        oid = pr['headRefOid']
        if subprocess.run(['git', 'cat-file', '-e', oid], cwd=ROOT, capture_output=True).returncode:
            subprocess.run(['git', 'fetch', '--no-tags', 'origin', f"refs/pull/{pr['number']}/head"],
                           cwd=ROOT, check=True, capture_output=True)
        stamp = subprocess.check_output(['git', 'show', '-s', '--format=%ct', oid], cwd=ROOT, text=True)
        commit = datetime.datetime.fromtimestamp(int(stamp), datetime.timezone.utc)
        result = subprocess.run(['git', 'show', f'{oid}:docs/PENDIENTES.md'], cwd=ROOT,
                                capture_output=True, encoding='utf-8')
        if result.returncode:
            continue
        for line in result.stdout.splitlines():
            parsed = queue_row(line)
            match = parsed[2] if parsed else None
            if match and match[2] == pr['headRefName']:
                yield parsed[0], match[1], pr['number'], max(commit, parse_time(match[3]))


def available_hd(lines, reserved):
    """List unclaimed HD work in priority order and preserve queue order within each priority."""
    rows = []
    for line in lines:
        parsed = queue_row(line)
        if not parsed:
            continue
        row, prefix, claim, status, description = parsed
        if (row.startswith('THD') and row not in reserved and not claim
                and (status.strip() == 'open' or status.startswith('open · released (stale claim of '))):
            priority = prefix.split('|')[2].strip()
            rows.append((int(priority[1:]) if priority.startswith('P') and priority[1:].isdigit() else 1,
                         row, description.split('|')[1].strip()))
    return sorted(rows, key=lambda row: row[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--claim'); ap.add_argument('--who'); ap.add_argument('--branch', default='')
    ap.add_argument('--release-stale', action='store_true'); ap.add_argument('--list', action='store_true')
    ap.add_argument('--list-pr-claims', action='store_true', help='report active and stale claims on open PR heads')
    ap.add_argument('--available-hd', action='store_true', help='list open HD shards without a corresponding open PR')
    ap.add_argument('--minutes', type=int, default=30); ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    if a.list_pr_claims:
        now = now_utc()
        for row, who, number, stamp in sorted(open_pr_claims(open_prs())):
            age = (now - stamp).total_seconds() / 60
            state = 'stale' if age > a.minutes else 'active'
            print(f'{row}: {state}, {who}, PR #{number}, idle {int(age)} min')
        return
    text = QUEUE.read_text(encoding='utf-8')
    newline = '\r\n' if '\r\n' in text else '\n'
    lines = text.split(newline)
    if a.available_hd:
        sys.stdout.reconfigure(errors='backslashreplace')
        prs = open_prs()
        reserved = {row for pr in prs
                    for field in ('title', 'headRefName') for row in SHARD_ID.findall(pr[field].upper())}
        reserved.update(row for row, *_ in open_pr_claims(prs))
        for priority, row, description in available_hd(lines, reserved):
            print(f'P{priority} {row} {description}')
        return
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
            parsed = queue_row(line)
            match = parsed[2] if parsed else None
            if match:
                who, branch, stamp = match.groups()
                since = last_activity(branch, parse_time(stamp), git_commit_time(branch))
                print('%s: %s on %s, idle %d min' % (parsed[0], who, branch or '-', (now_utc() - since).total_seconds() // 60))
        return
    if not a.dry_run:
        QUEUE.write_text(newline.join(lines), encoding='utf-8', newline='')


if __name__ == '__main__':
    main()
