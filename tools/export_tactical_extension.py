"""Export only the approved generated stage01 band; never the native map context."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def export(source,output):
    source=Path(source);output=Path(output)
    approved=json.loads((source/'approved.json').read_text(encoding='utf-8'))
    if approved.get('status')!='approved-preliminary' or approved.get('protected_columns')!=[0,814] or approved.get('replace_columns')!=[814,896] or approved.get('logical_density')!=2 or approved.get('max_aspect')!='16:9':
        raise ValueError('Unrecognized approved extension geometry')
    file=source/'composite-v2.png'
    if file.is_symlink() or digest(file)!=approved.get('files',{}).get(file.name):raise ValueError('Modified approved composition')
    with Image.open(file) as image:
        if image.size!=(940,448):raise ValueError('Unexpected source density/extent')
        # GPU reference:940 output columns represented438 native columns.
        # Pixel-pattern calibration found world origin277,24 (8825 matches).
        # The approved generated band maps to native world x656..694.
        band=image.convert('RGBA').crop((814,0,896,448)).resize((39,224),Image.Resampling.NEAREST)
    output.mkdir(parents=True,exist_ok=False)
    target=output/'STAGE01-right-v1.png';band.save(target)
    report=dict(schema=1,generated_only=True,original_map_context_included=False,max_aspect='16:9',
        stage_map_signature='1CAF3218B4B0F9F0',world_origin=[656,24],logical_size=[39,224],
        reference_output_size=[940,448],reference_native_size=[438,224],reference_world_origin=[277,24],
        approved_composition_sha256=approved['files'][file.name],
        files=[dict(path=target.name,bytes=target.stat().st_size,sha256=digest(target))])
    report['backgrounds']=[dict(file=target.name,sha256=digest(target))]
    report['source_pixels_included']=False
    (output/'provenance.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(export(args.source,args.output),indent=2))
