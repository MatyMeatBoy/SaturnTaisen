"""Read-only SDK/version/symbol inventory of owner-supplied MODE1/2048 Saturn ISOs.

Outputs metadata, never original files or source listings. Version strings are
evidence of embedded components, not proof that a named function was executed.
"""
import argparse
import hashlib
import json
import mmap
from pathlib import Path
import re
import struct

VERSION=re.compile(rb'(?:GFS_[A-Z]+|STM_[A-Z]+|CPK|SGL|SBL) Version [0-9.]+ [0-9-]+')
SYMBOL=re.compile(rb'([0-9a-fA-F]{8})[ \t]+\.text[ \t]+([0-9a-fA-F]{8})[ \t]+(_[A-Za-z][A-Za-z_0-9]+)')


def files(data,require_saturn=True):
    def extent(record):
        if len(record)<34: raise ValueError('Short ISO directory record')
        lba,size=struct.unpack_from('<I',record,2)[0],struct.unpack_from('<I',record,10)[0]
        if (lba,size)!=(struct.unpack_from('>I',record,6)[0],struct.unpack_from('>I',record,14)[0]):
            raise ValueError('ISO endian copies disagree')
        return lba,size
    if (require_saturn and data[:16]!=b'SEGA SEGASATURN ') or data[32768:32775]!=b'\x01CD001\x01':
        raise ValueError('Expected prepared Saturn MODE1/2048 ISO')
    root=data[32768+156:32768+156+data[32768+156]]
    visited=set()
    def walk(record,parent,depth):
        if depth>32: raise ValueError('Directory nesting limit')
        lba,size=extent(record)
        if lba*2048+size>len(data):raise ValueError('Directory extent exceeds data track')
        if (lba,size) in visited:return
        visited.add((lba,size));directory=data[lba*2048:lba*2048+size]
        at=0
        while at<len(directory):
            length=directory[at]
            if not length:at=(at//2048+1)*2048;continue
            entry=directory[at:at+length];at+=length
            if len(entry)!=length or length<34:raise ValueError('Invalid directory record')
            name=entry[33:33+entry[32]]
            if name in (b'\0',b'\1'):continue
            name=name.decode('ascii').split(';')[0]
            if '/' in name or '\\' in name or name in ('.','..'):raise ValueError('Invalid ISO name')
            path=parent+'/'+name
            child_lba,child_size=extent(entry)
            if entry[25]&2:yield from walk(entry,path,depth+1)
            else:yield path,child_lba,child_size
    yield from walk(root,'',0)


def audit(path):
    rows=[];external=[]
    with path.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        for name,lba,size in files(data):
            if lba*2048+size>len(data):
                external.append({'file':name,'lba':lba,'bytes':size,'reason':'outside data track; not read'})
                continue
            if size>16*1024*1024:continue
            content=data[lba*2048:lba*2048+size]
            versions=[{'file_offset':hex(m.start()),'version':m.group().decode('ascii')} for m in VERSION.finditer(content)]
            symbols=[{'object_offset':m[1].decode(),'address':m[2].decode(),'name':m[3].decode()} for m in SYMBOL.finditer(content)]
            if versions or symbols:
                rows.append({'file':name,'lba':lba,'bytes':size,'sha256':hashlib.sha256(content).hexdigest(),
                             'versions':versions,'text_symbols':symbols,
                             'execution_confirmed':False})
    return {'profile':path.parent.name,'components':rows,'external_extents':external}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso',type=Path,nargs='+')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    report={'method':'read-only ISO9660 version strings and .text symbol listings; no execution inference',
            'profiles':[audit(path) for path in args.iso]}
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    for profile in report['profiles']:
        print(profile['profile'],[(c['file'],len(c['versions']),len(c['text_symbols'])) for c in profile['components']])


if __name__=='__main__':main()
