"""Add byte-verified, runtime-attributed overlays to a private AOT candidate DB."""
import argparse
import hashlib
import json
import mmap
from pathlib import Path
import subprocess

if __package__:
    from .audit_sdk import files
    from .discover_battle_overlays import ROOT,MAX_BLOCK,read_seed,merge_candidates,analyze_with_sdk
else:
    from audit_sdk import files
    from discover_battle_overlays import ROOT,MAX_BLOCK,read_seed,merge_candidates,analyze_with_sdk

REGISTRY={
    'ENDING_DISC2_EN': dict(file='/SAKURA1/ENDING.BIN', base=0x06080000, bytes=178968,
                            sha256='f85eff4cef05796bcbaedb29099795dcc9ebd61bf24d81d8fb819899eb4b1553',
                            observed_ranges='ending-aot-ranges.json',
                            evidence='English disc 2 Sakura ending entry and credits through Fin'),
    'SLG_RELOCATED':dict(file='/SAKURA2/0SLG.BIN',base=0x06002000,bytes=309844,
                 sha256='7ca7dda97d17f704e7e687b4fc04170fb39c731ed1a4372fafc3e50b3aed41b8',
                 slice_offset=0x47B14,slice_bytes=206,
                 evidence='Chapter1 postbattle: function06032B00 copies103 words from0604BB14 to06002000; exact206 bytes match WATCH_PC dump at missing PC06002042'),
    'MAIN_RELOCATED':dict(file='/SAKURA',base=0x06002000,bytes=391712,
                 sha256='f9fc1dd16e3684558b22e857c876b682ad65a7c6b9416d453cd4304453021197',
                 slice_offset=0x4F5D8,slice_bytes=238,
                 evidence='Chapter1 postbattle: function06005C58 copies119 words from060535D8 to06002000; all238 bytes match state before missing PC06002042'),
    'EVT02':dict(file='/SAKURA2/EVT02.BIN',base=0x00204000,bytes=76180,
                 sha256='701d68ab48e67eabce1e1eb89bd4a8b790aa0f6a40ff68bbfa0600489b97c660',
                 evidence='Episode2 cold load: all 76180 bytes equal LowRAM at 00204000 in strict/interpreter state frame6688; strict first missing PC00204000'),
    'EVT06':dict(file='/SAKURA2/EVT06.BIN',base=0x00204000,bytes=77716,
                 sha256='3214506d26f1b9fbec18190e993acf4ef5502532522790d7a327efe7125c89e5',
                 evidence='Episode4 cold load: all 77716 bytes equal LowRAM at 00204000 in states6677-6680; strict first missing PC00204000 after6678 complete frames'),
    'EVT01':dict(file='/SAKURA2/EVT01.BIN',base=0x00204000,bytes=76636,
                 sha256='99405f5252d4f5d9e31771489864532b3c5e7ba4eb97067e1a86a0fcc814e1d9',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT03':dict(file='/SAKURA2/EVT03.BIN',base=0x00204000,bytes=77268,
                 sha256='32cd2bedf1942a61efbb211e40daaa249c486d42bdfc2de3e83fb29e22618818',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT04':dict(file='/SAKURA2/EVT04.BIN',base=0x00204000,bytes=77224,
                 sha256='93fb524dc7b64b1af5b576bd56fdf67d9624eea0cdf5006537ec339acb37ceaa',
                 evidence='Chapter3 battle 2 cold load: all 77224 bytes equal LowRAM at 00204000 in strict state frame 6678; strict first missing PC00204000 at frame 6680'),
    'EVT05':dict(file='/SAKURA2/EVT05.BIN',base=0x00204000,bytes=76672,
                 sha256='0253c98ff7cb2bd3078875ae1e9a5d64d9e99357069930ccf4d7c2fbbb72bb4a',
                 evidence='Chapter3 battle 3 cold load: all 76672 bytes equal LowRAM at 00204000 in strict state frame 6678; strict first missing PC00204000 at frame 6679'),
    'EVT07':dict(file='/SAKURA2/EVT07.BIN',base=0x00204000,bytes=77492,
                 sha256='04e7347e362a00e6cdbee7f14f9753a0558028096b991ff9bab46fb68efb0bba',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT08':dict(file='/SAKURA2/EVT08.BIN',base=0x00204000,bytes=77140,
                 sha256='bdfcfc20be561237740ede35150955cd4a313d52979da46f5e8754655bcf293c',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT09':dict(file='/SAKURA2/EVT09.BIN',base=0x00204000,bytes=75324,
                 sha256='71f6b81c234ec6f030a70a85b8756c371efd22e9503a8000cf5a412d0e8517b1',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT10':dict(file='/SAKURA2/EVT10.BIN',base=0x00204000,bytes=75508,
                 sha256='d34f7476fbf14af32b5961d6eedfaaad900e3b281c53a45b98e924e7d4a81051',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT11':dict(file='/SAKURA2/EVT11.BIN',base=0x00204000,bytes=75960,
                 sha256='b6617590b439ba580f1706200c6812385b1ddcff60676a101e80c11faaa49da9',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT21':dict(file='/SAKURA2/EVT21.BIN',base=0x00204000,bytes=75364,
                 sha256='ee4180e542c543a6af6d68cea487f788695c757e72ee060a8c973017df104afc',
                 evidence='Episode 4 disc-1 continuation: all 75364 bytes match low WRAM at 00204000 in the interpreter boundary state after cold frame 15859. The strict baseline stops on master SH-2 PC 00204000 after that frame'),
    'EVT22':dict(file='/SAKURA2/EVT22.BIN',base=0x00204000,bytes=76840,
                 sha256='4f6a32f410c1f7da6ffbedc878a3929e1c5092e92dd85caad6e0fd4fcb8529b3',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT27':dict(file='/SAKURA2/EVT27.BIN',base=0x00204000,bytes=76976,
                 sha256='17a9e2477be51fbce0a7076ad8c61902ec901b7b51a5ca34be3d415e7dcdabf0',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT12':dict(file='/SAKURA2/EVT12.BIN',base=0x00204000,bytes=75984,
                 sha256='0d7a561da50c9a209157bf61b645b49b0ef37c70c5db409e8f8a1ea4cf02f11d',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT13':dict(file='/SAKURA2/EVT13.BIN',base=0x00204000,bytes=75280,
                 sha256='cf7a5a275d4f5df853360da7c4d26ba48afc5d7037892205a42cdea79f1cbb67',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT14':dict(file='/SAKURA2/EVT14.BIN',base=0x00204000,bytes=77656,
                 sha256='c03c34b20d2800a8316bd3683fba9d09bda04f4b133d744853c20b41c610c10e',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT15':dict(file='/SAKURA2/EVT15.BIN',base=0x00204000,bytes=77316,
                 sha256='d56eb172d8ac8250cc3ec45f70b62595a8b4c05c734c9f86f5c36366508ace89',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT16':dict(file='/SAKURA2/EVT16.BIN',base=0x00204000,bytes=77764,
                 sha256='300a92c2cd5dd3ba8b6b57350684b47a1074142a8eb1a83d869bad0acf51ea7f',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT17':dict(file='/SAKURA2/EVT17.BIN',base=0x00204000,bytes=77332,
                 sha256='710fe550d47fdc092c51585fddb45e07fcb1aa8ea3f8254621e8dfa85d08afa4',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT18':dict(file='/SAKURA2/EVT18.BIN',base=0x00204000,bytes=79136,
                 sha256='143cf5319000e9928e3f2042924763defa4eb6d4a87167b1bc8dacfdeae29f78',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT19':dict(file='/SAKURA2/EVT19.BIN',base=0x00204000,bytes=76596,
                 sha256='1e5f8f4d3f67590895328f0db31aca90760f17330afdd55688f76da3de481246',
                 evidence='Chapter10 battle 2 and final battle cold loads (disc2): all 76596 bytes equal LowRAM at 00204000 in strict state frame 6684; strict first missing PC00204000 at frame 6685'),
    'EVT20':dict(file='/SAKURA2/EVT20.BIN',base=0x00204000,bytes=76968,
                 sha256='05f35d5ec81583a52f198c75fe147df511937fbdb2ecae69b029f6955e1dd591',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT23':dict(file='/SAKURA2/EVT23.BIN',base=0x00204000,bytes=78396,
                 sha256='c1cd00589c9976b384554642e046febb433fb48cc9a93ba5e4b4b5ab838edff6',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT24':dict(file='/SAKURA2/EVT24.BIN',base=0x00204000,bytes=76616,
                 sha256='649877afbffb4862996e387980686614bf9932272a03d621bb0a6d503c138b4f',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT25':dict(file='/SAKURA2/EVT25.BIN',base=0x00204000,bytes=77776,
                 sha256='88f671a05d2abf27fd25c9e83041c13fc4621d32295a1780556f65ad16e3dbd5',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
    'EVT26':dict(file='/SAKURA2/EVT26.BIN',base=0x00204000,bytes=77492,
                 sha256='1afa1aad2c02599b82b47de23b45f4b9da1944dc5d9a3755f6fd3b47585ab238',
                 evidence='EVT family inference: observed overlays EVT01,02,04,05,06,19 load at 00204000 with exact byte equality; base inferred for this file, never executed. Strict AOT compares block code with memory before running, so a wrong inference cannot execute wrong code'),
}


REGISTRY['EVT04_MAP04'] = dict(
    REGISTRY['EVT04'], observed_ranges='evt04-map04-aot-ranges.json',
    evidence='Disc 1 Chapter 3 second battle, the 180-frame MAP04 camera witness')
REGISTRY['EVT16_MAP15'] = dict(
    REGISTRY['EVT16'], observed_ranges='evt16-map15-aot-ranges.json',
    evidence='Disc 2 Chapter 9 theater defense, the 540-field MAP15 movement witness')


def registered_module(name,raw,profile,registry=REGISTRY):
    spec=registry.get(name)
    if spec is None:raise ValueError('Overlay has no verified registry entry: '+name)
    if len(raw)!=spec['bytes'] or hashlib.sha256(raw).hexdigest()!=spec['sha256']:
        raise ValueError('Overlay bytes differ from the witnessed version: '+name)
    if 'slice_offset' in spec or 'slice_bytes' in spec:
        offset,size=spec.get('slice_offset'),spec.get('slice_bytes')
        if (not isinstance(offset,int) or not isinstance(size,int) or offset<0 or size<=0 or
                offset%2 or size%2 or offset+size>len(raw)):
            raise ValueError('Invalid registered copied region: '+name)
        fragment=raw[offset:offset+size]
        return dict(spec,profile=profile,source_bytes=len(raw),source_sha256=spec['sha256'],
                    bytes=len(fragment),sha256=hashlib.sha256(fragment).hexdigest(),raw=fragment)
    return dict(spec,profile=profile,raw=raw)



def observed_candidates(module, ranges):
    """Read only witnessed instruction extents from a byte-verified module."""
    base = module['base']
    raw = module['raw']
    if base % 2 or base < 0 or base + len(raw) > 0x100000000:
        raise ValueError('Invalid observed module address')
    if not isinstance(ranges, list) or not ranges:
        raise ValueError('Missing observed variant ranges')
    selected = set()
    for extent in ranges:
        if not isinstance(extent, list) or len(extent) != 2:
            raise ValueError('Invalid observed variant extent')
        offset, size = extent
        if (type(offset) is not int or type(size) is not int or offset < 0 or offset % 2 or
                not 0 < size <= MAX_BLOCK or size % 2 or offset + size > len(raw)):
            raise ValueError('Invalid observed variant extent')
        selected.add((base + offset, raw[offset:offset + size]))
    if len(selected) != len(ranges):
        raise ValueError('Duplicate observed variant extent')
    return selected


def build(image,names,seed,output,sdk):
    expected=json.loads((ROOT/'config/dependencies.json').read_text(encoding='utf-8'))['satrecomp']['commit']
    revision=subprocess.check_output(['git','-C',str(sdk),'rev-parse','HEAD'],text=True).strip()
    if revision!=expected:raise ValueError('Use the pinned SDK revision')
    if not names or len(set(names))!=len(names) or any(name not in REGISTRY for name in names):
        raise ValueError('Select distinct registered overlays')
    paths = {}
    for name in names:
        paths.setdefault(REGISTRY[name]['file'], []).append(name)
    modules = []
    with image.open('rb') as source,mmap.mmap(source.fileno(),0,access=mmap.ACCESS_READ) as data:
        image_hash=hashlib.sha256(data).hexdigest();seen=set()
        for path,lba,size in files(data):
            if path not in paths:continue
            if path in seen or lba*2048+size>len(data):raise ValueError('Invalid registered overlay extent')
            seen.add(path)
            raw = bytes(data[lba*2048:lba*2048+size])
            for name in paths[path]:
                if size != REGISTRY[name]['bytes']:
                    raise ValueError('Registered overlay extent size changed')
                module = registered_module(name, raw, 'owner-disc')
                module['lba'] = lba
                modules.append(module)
    if seen!=set(paths):raise ValueError('Registered overlay absent from image')
    before = read_seed(seed)
    static = [module for module in modules if 'observed_ranges' not in module]
    extra, rows = analyze_with_sdk(static, sdk) if static else (set(), [])
    for module in modules:
        if 'observed_ranges' not in module:
            continue
        index = Path(__file__).resolve().parents[1] / 'config' / module['observed_ranges']
        candidates = observed_candidates(module, json.loads(index.read_text(encoding='utf-8')))
        extra.update(candidates)
        row = {key: value for key, value in module.items() if key != 'raw'}
        row.update(base=f"{module['base']:08X}", candidate_blocks=len(candidates), strategy='observed extents')
        rows.append(row)
    merged = merge_candidates(before, extra)
    output.mkdir(parents=True,exist_ok=False);database=output/'blocks.txt'
    with database.open('x',encoding='ascii',newline='\n') as stream:
        stream.write('# Owner-derived AOT candidates; keep local.\n')
        for pc,code in sorted(merged):stream.write(f'{pc:08X} {code.hex().upper()}\n')
    report=dict(schema=1,scope='local candidates from registered overlays; see per-module evidence',
                sdk_commit=revision,opcode_sha256=hashlib.sha256((sdk/'machine/sh2_ops.h').read_bytes()).hexdigest(),
                iso_sha256=image_hash,seed_sha256=hashlib.sha256(seed.read_bytes()).hexdigest(),
                profiles=rows,before=len(before),after=len(merged),added=len(merged)-len(before),
                candidate_database_sha256=hashlib.sha256(database.read_bytes()).hexdigest())
    (output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image',type=Path,required=True)
    parser.add_argument('--module',action='append',choices=sorted(REGISTRY),required=True)
    parser.add_argument('--seed-blocks',type=Path,required=True)
    parser.add_argument('--sdk-root',type=Path,default=ROOT/'local/deps/satrecomp')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();output=args.output.resolve()
    if (ROOT/'local/work').resolve() not in output.parents or output.exists():
        parser.error('--output must be a new directory under local/work')
    try:report=build(args.image,args.module,args.seed_blocks,output,args.sdk_root)
    except (OSError,ValueError,subprocess.SubprocessError) as error:parser.exit(1,str(error)+'\n')
    print(json.dumps({key:report[key] for key in ('before','after','added')},indent=2))


if __name__=='__main__':main()
