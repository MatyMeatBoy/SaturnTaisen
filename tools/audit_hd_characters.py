"""Inventory owner PC character resources against Saturn disc files, without images.

Matching names are candidates, never a claim of compatible animation indices or masks.
"""
import argparse
import hashlib
import json
import mmap
from pathlib import Path
import re
from audit_pc_sprites import inspect
from audit_sdk import files


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pc-root',type=Path,required=True,help='extracted resource root containing SAKURA1')
    parser.add_argument('--disc',type=Path,action='append',required=True,help='prepared Saturn ISO, repeat for disc 2')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();native={};special=[]
    for number,iso in enumerate(args.disc,1):
        with iso.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
            for name,lba,length in files(data):
                stem=Path(name).stem
                if not re.fullmatch(r'NC\d+',stem) and stem!='NCOBJ':continue
                if length>64*1024*1024 or lba*2048+length>len(data):raise ValueError('Invalid native resource extent')
                row=dict(disc=number,path=name,bytes=length,
                         sha256=hashlib.sha256(data[lba*2048:lba*2048+length]).hexdigest())
                if stem=='NCOBJ':special.append(row)
                else:native.setdefault(stem,[]).append(row)
    entries=[]
    for file in sorted((args.pc_root/'SAKURA1/NC').glob('*.SPR')):
        if file.stat().st_size>64*1024*1024:raise ValueError('PC character input exceeds budget')
        data=file.read_bytes()
        row=dict(id=file.stem,pc_path=file.relative_to(args.pc_root).as_posix(),bytes=len(data),
                 sha256=hashlib.sha256(data).hexdigest(),saturn=native.get(file.stem,[]))
        try:row['images']=inspect(data)
        except ValueError as error:row['error']=str(error)
        entries.append(row)
    if not entries:raise ValueError('No character SPR files found under SAKURA1/NC')
    portraits=[]
    for relative in ('SAKURA1/SYSTEM/KAO.SPR','SAKURA1/ICATCH/KAO_P.SPR'):
        file=args.pc_root/relative
        if not file.is_file():continue
        data=file.read_bytes()
        portraits.append(dict(path=relative,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),images=inspect(data)))
    names={row['id'] for row in entries}
    report=dict(schema=1,scope='Saturn HD character candidates; header inventory only; no import/mapping inferred',
                pc_files=len(entries),pc_image_entries=sum(len(row.get('images',[])) for row in entries),
                pc_header_errors=sum('error' in row for row in entries),
                matching_names=len(names & native.keys()),saturn_only=sorted(native.keys()-names),
                pc_only=sorted(names-native.keys()),native_auxiliary=special,
                portraits=portraits,characters=entries)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f"{report['pc_files']} PC character files; {report['pc_image_entries']} nonempty images; {report['matching_names']} native name matches")


if __name__=='__main__':main()
