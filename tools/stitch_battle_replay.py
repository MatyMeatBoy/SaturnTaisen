"""Compose verified local probe inputs into one replay with no intermediate loads.

This prepares a verification workload; composition alone proves no gameplay.
Original snapshots remain local. The runtime saves a requested state before
running that frame, so each parent contributes frames-1 to the next offset.
"""
import argparse
import hashlib
import json
from pathlib import Path


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def option(command, name):
    if command.count(name) != 1:
        raise ValueError('Missing or repeated probe option: '+name)
    return command[command.index(name)+1]


def read_segment(folder):
    report = json.loads((folder/'run.json').read_text(encoding='utf-8'))
    frames = report['frames']
    if report['exit'] != 0 or type(frames) is not int or frames < 2 or report['state_saved_at_frame'] != frames-1:
        raise ValueError('Unsuccessful or unsupported probe boundary')
    source_spec = option(report['command'], '--state-load')
    if not source_spec.startswith('0:') or ',' in source_spec:
        raise ValueError('Probe must have a single initial state')
    source = Path(source_spec[2:]).resolve()
    if not source.is_file() or sha256(source) != report['source_sha256']:
        raise ValueError('Source state changed: '+str(source))
    movie = Path(option(report['command'], '--movie'))
    events = {}
    previous = -1
    for line in movie.read_text(encoding='utf-8').splitlines():
        line = line.partition('#')[0].strip()
        if not line:
            continue
        fields = line.split()
        if len(fields) != 3:
            raise ValueError('Invalid movie event')
        frame, pad1, pad2 = int(fields[0]), int(fields[1], 16), int(fields[2], 16)
        if frame <= previous or frame < 0 or frame >= frames-1:
            raise ValueError('Unordered event or input on snapshot boundary')
        if not 0 <= pad1 <= 0xFFFF or not 0 <= pad2 <= 0xFFFF:
            raise ValueError('Invalid pad bits')
        events[frame] = (pad1, pad2)
        previous = frame
    if events and events[max(events)] != (0, 0):
        raise ValueError('Input must be released before snapshot boundary')
    return report, source, events


def compose(last_folder):
    folder = Path(last_folder).resolve()
    chain = []
    seen = set()
    while True:
        if folder in seen or len(chain) >= 10000:
            raise ValueError('Cyclic or excessive probe chain')
        seen.add(folder)
        report, source, events = read_segment(folder)
        chain.append((folder, report, source, events))
        if source.name != 'end.state' or not (source.parent/'run.json').is_file():
            break
        folder = source.parent
    chain.reverse()
    combined = {}
    segments = []
    offset = 0
    for folder, report, source, events in chain:
        combined[offset] = (0, 0)
        combined.update({offset+frame: pads for frame, pads in events.items()})
        segments.append(dict(folder=str(folder), offset=offset, frames=report['frames'],
            source_sha256=report['source_sha256'], movie_sha256=sha256(Path(option(report['command'], '--movie')))))
        offset += report['frames']-1
    initial = chain[0][2]
    return dict(schema=1, initial_state=str(initial), initial_state_sha256=sha256(initial), frames=offset+1,
        final_state_at_frame=offset, segments=segments,
        scope='prepared workload only; run continuously and compare before claiming verified progress'), combined


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--last-probe', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='new movie path')
    args = parser.parse_args()
    report, events = compose(args.last_probe)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8', newline='\n') as output:
        for frame, (pad1, pad2) in sorted(events.items()):
            output.write(f'{frame} {pad1:04x} {pad2:04x}\n')
    args.output.with_suffix(args.output.suffix+'.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
