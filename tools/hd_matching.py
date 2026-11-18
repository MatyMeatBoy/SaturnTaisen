"""Local HD matching, review projects and integer-density pack compilation.

Pillow is used for analysing and preparing owner-supplied game resources. No
network, AI service or game executable is needed to compare existing catalogues.
"""
import hashlib
import io
import json
import math
import mmap
import os
from pathlib import Path
import struct
from collections import Counter
from PIL import Image, ImageChops, ImageStat

MAX_IMAGE_PIXELS=4096*4096


def fnv64(data):
    value=14695981039346656037
    for byte in data:value=((value^byte)*1099511628211)&0xFFFFFFFFFFFFFFFF
    return value


def workspace_file(root,relative):
    root=Path(root).resolve();path=(root/relative).resolve()
    if not path.is_relative_to(root):raise ValueError('Ruta fuera del proyecto')
    return path


def load_image(path):
    path=Path(path)
    if not path.is_file() or path.stat().st_size>16*1024*1024:raise ValueError('Imagen ausente o demasiado grande')
    with Image.open(path) as image:
        if image.format!='PNG' or not image.width or not image.height or image.width*image.height>MAX_IMAGE_PIXELS:
            raise ValueError('PNG fuera del presupuesto de imágenes')
        return image.convert('RGBA')


def fingerprint(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def descriptor(image):
    # Analysis only. The prepared art below always uses nearest and integer grids.
    return image.convert('RGB').resize((20,40),Image.Resampling.BOX)


def rank_images(native,candidates,limit=5):
    source=descriptor(native);scores=[]
    for index,image in candidates:
        target=image if image.mode=='RGB' and image.size==(20,40) else descriptor(image)
        error=math.sqrt(sum(ImageStat.Stat(ImageChops.difference(source,target)).sum2)/(20*40*3))/255
        scores.append(dict(index=index,error=error))
    return sorted(scores,key=lambda row:(row['error'],row['index']))[:limit]


def safe_suggestion(ranked):
    if not ranked:return False
    if len(ranked)==1:return ranked[0]['error']==0
    return ranked[0]['error']<=0.06 and ranked[1]['error']-ranked[0]['error']>=0.008


def choose_density(viewport_scale):
    if type(viewport_scale) is not int or viewport_scale<1:raise ValueError('Escala entera positiva requerida')
    return 2 if viewport_scale%2==0 else 1


def prepare_variant(pc,indices,density,dx=0,dy=0):
    if density not in (1,2) or type(density) is not int:raise ValueError('Densidad no admitida')
    if type(dx) is not int or type(dy) is not int or abs(dx)>4 or abs(dy)>4:raise ValueError('Ajuste debe ser entero entre -4 y 4')
    if len(indices)!=3200:raise ValueError('Retrato nativo incompleto')
    image=pc.convert('RGBA').resize((40*density,80*density),Image.Resampling.NEAREST)
    if dx or dy:
        # Clamp to edge pixels; keep the fixed native rectangle instead of leaving
        # a strip of the original portrait behind the shifted replacement.
        shifted=Image.new('RGBA',image.size)
        source=image.load();target=shifted.load()
        for y in range(image.height):
            for x in range(image.width):
                target[x,y]=source[min(image.width-1,max(0,x-dx*density)),min(image.height-1,max(0,y-dy*density))]
        image=shifted
    mask=Image.frombytes('L',(40,80),bytes(255 if index else 0 for index in indices))
    mask=mask.resize(image.size,Image.Resampling.NEAREST)
    image.putalpha(ImageChops.multiply(image.getchannel('A'),mask))
    return image


def read_fce_images(data):
    if len(data)<160:raise ValueError('Cabecera FCE truncada')
    ids=[]
    for value in struct.unpack_from('>80H',data):
        if not value:break
        if value in ids:raise ValueError('Identidad FCE repetida')
        ids.append(value)
    if len(data)!=160+len(ids)*3200 or (not ids and any(data)):raise ValueError('Distribución FCE no admitida')
    return {value:data[160+i*3200:160+(i+1)*3200] for i,value in enumerate(ids)}


def decode_state_palette(data,bank):
    if type(bank) is not int or not 0<=bank<8:raise ValueError('Banco de paleta inválido')
    if len(data)<44 or len(data)>64*1024*1024 or struct.unpack_from('<II',data)!=(0x53525354,9):
        raise ValueError('Se requiere un estado local Sakura versión 9')
    if data[8:40]!=b'sakura'+bytes(26) or struct.unpack_from('<I',data,40)[0]!=0x4D414348:
        raise ValueError('Estado de otro juego o máquina')
    at=44;cram=None
    for expected in (0x100000,0x100000,0x80000,0x80000,0x40000,0x40000,0x80000,0x1000):
        if at+8>len(data):raise ValueError('Vector de estado truncado')
        count=struct.unpack_from('<Q',data,at)[0];at+=8
        if count!=expected or at+count>len(data):raise ValueError('Vector de estado no admitido')
        cram=data[at:at+count];at+=count
    raw=cram[bank*512:(bank+1)*512];palette=[]
    for word in struct.unpack('>256H',raw):palette.extend(((word&31)<<3,((word>>5)&31)<<3,((word>>10)&31)<<3))
    return bytes(palette),fnv64(raw)


def atomic_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+f'.{os.getpid()}.tmp')
    try:
        temporary.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8');os.replace(temporary,path)
    finally:temporary.unlink(missing_ok=True)


def prepare_fce_project(discs,palette_state,bank,pc_dir,pc_spr,workspace,output):
    from audit_sdk import files
    root=Path(workspace).resolve();root.mkdir(parents=True,exist_ok=True)
    native_dir=root/'native';raw_dir=root/'raw';target_dir=root/'pc'
    for folder in (native_dir,raw_dir,target_dir):folder.mkdir(exist_ok=True)
    palette,palette_hash=decode_state_palette(Path(palette_state).read_bytes(),bank)
    native={}
    for disc in discs:
        with Path(disc).open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as iso:
            for name,lba,size in files(iso):
                if not name.endswith('FCE.BIN'):continue
                if size>1024*1024 or lba*2048+size>len(iso):raise ValueError('Extensión FCE inválida')
                for identity,raw in read_fce_images(iso[lba*2048:lba*2048+size]).items():
                    if identity in native and native[identity]!=raw:raise ValueError(f'Identidad FCE conflictiva: {identity:04x}')
                    native[identity]=raw
    candidates=[];catalog=[]
    for file in sorted(Path(pc_dir).glob('KAO-*.png')):
        index=int(file.stem.split('-')[-1]);image=load_image(file)
        if image.size!=(80,160):raise ValueError('Catálogo KAO requiere hojas de 80×160')
        target=target_dir/f'{index}.png';image.save(target)
        catalog.append(dict(index=index,path=target.relative_to(root).as_posix(),sha256=fingerprint(target)))
        candidates.append((index,descriptor(image)))
    if not native or not candidates:raise ValueError('Falta el catálogo Saturn o PC')
    rows=[];levels=[min(255,n*255//248) for n in range(256)]*3
    for identity,raw in sorted(native.items()):
        file=native_dir/f'{identity:04x}.png';source=raw_dir/f'{identity:04x}.bin';source.write_bytes(raw)
        image=Image.frombytes('P',(40,80),raw);image.putpalette(palette);image=image.convert('RGB');image.save(file)
        ranked=rank_images(image.point(levels),candidates)
        # A second, independent identifier check guards this verified-format route.
        auto=safe_suggestion(ranked) and ranked[0]['index']==identity-1
        rows.append(dict(id=f'{identity:04x}',path=file.relative_to(root).as_posix(),raw=source.relative_to(root).as_posix(),
                         raw_sha256=fingerprint(source),candidates=ranked,selected=ranked[0]['index'],
                         status='auto' if auto else 'pending',dx=0,dy=0))
    winners=Counter(row['selected'] for row in rows)
    for row in rows:
        if winners[row['selected']]>1 and row['status']=='auto':row['status']='pending'
    source=Path(pc_spr);data=source.read_bytes()
    project=dict(schema=1,kind='sakura-narrative-portraits',output=str(Path(output).resolve()),palette_hash=palette_hash,
                 source=dict(path=str(source.resolve()),bytes=len(data),fnv64=fnv64(data),sha256=hashlib.sha256(data).hexdigest()),
                 candidates=catalog,rows=rows,policy=dict(max_error=.06,min_margin=.008,integer_densities=[1,2]))
    atomic_json(root/'project.json',project);return project


def export_pack(project,workspace):
    if project.get('schema')!=1 or project.get('kind')!='sakura-narrative-portraits':raise ValueError('Proyecto no admitido')
    root=Path(workspace).resolve();output=Path(project['output']).resolve()
    source=project['source'];data=Path(source['path']).read_bytes()
    if len(data)!=source['bytes'] or hashlib.sha256(data).hexdigest()!=source['sha256'] or fnv64(data)!=source['fnv64']:
        raise ValueError('Cambió el recurso PC original; reconstruye el catálogo')
    output.mkdir(parents=True,exist_ok=True);catalog={item['index']:item for item in project['candidates']}
    entries=[];catalogue=bytearray()
    for row in project['rows']:
        if row['status'] not in ('auto','accepted'):continue
        raw_file=workspace_file(root,row['raw']);raw=raw_file.read_bytes()
        if len(raw)!=3200 or fingerprint(raw_file)!=row['raw_sha256']:raise ValueError('Cambió una identidad Saturn')
        if row['selected'] not in catalog:raise ValueError('Candidato fuera del catálogo')
        candidate=catalog[row['selected']];file=workspace_file(root,candidate['path'])
        if fingerprint(file)!=candidate['sha256']:raise ValueError('Cambió una imagen PC; recalcula el matching')
        image=load_image(file);variants=[]
        for density in (1,2):
            prepared=prepare_variant(image,raw,density,row['dx'],row['dy'])
            buffer=io.BytesIO();prepared.save(buffer,format='PNG');blob=buffer.getvalue()
            name=hashlib.sha256(blob).hexdigest()+'.png';path=output/name
            if not path.exists():path.write_bytes(blob)
            variants.append((name,fnv64(blob)))
        entries.append(dict(id=int(row['id'],16),offset=len(catalogue),raw_hash=fnv64(raw),variants=variants))
        catalogue.extend(raw)
    if len(entries)>394:raise ValueError('Demasiados retratos para este formato')
    native_name='native-'+hashlib.sha256(catalogue).hexdigest()+'.bin'
    native_file=output/native_name
    if not native_file.exists():native_file.write_bytes(catalogue)
    lines=['[pack]','schema=1',f"source_bytes={source['bytes']}",f"source_hash={source['fnv64']}",
           f"palette_hash={project['palette_hash']}",f'count={len(entries)}',
           f'native_file={native_name}',f'native_hash={fnv64(catalogue)}','']
    for index,entry in enumerate(entries):
        parts=entry['variants']
        lines.extend([f'[portrait-{index}]',f"native_id={entry['id']}",f"offset={entry['offset']}",
                      f"raw_hash={entry['raw_hash']}",f'file1={parts[0][0]}',f'hash1={parts[0][1]}',
                      f'file2={parts[1][0]}',f'hash2={parts[1][1]}',''])
    manifest=output/'manifest.ini';temporary=output/f'manifest.{os.getpid()}.tmp'
    try:
        temporary.write_text('\n'.join(lines),encoding='utf-8');os.replace(temporary,manifest)
    finally:temporary.unlink(missing_ok=True)
    return dict(portraits=len(entries),entries=len(entries),manifest=str(manifest))
