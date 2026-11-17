"""Read-only SPRED header inventory; extracted owner assets remain local.

This records dimensions and formats, not a claim of Saturn compatibility.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def inspect(data):
    if len(data)<32 or data[:10]!=b'SEGA SPRED':
        raise ValueError('unknown SPRED signature')
    images=[]
    for at in range(16,len(data)-15,16):
        offset,size,index,_=struct.unpack_from('>4I',data,at)
        if not offset or not size:
            break
        if index>=14 or offset>len(data) or size>len(data)-offset:
            raise ValueError('invalid chunk extent')
        if index==2:
            if size<16:
                raise ValueError('short image table')
            count=struct.unpack_from('>H',data,offset)[0]
            table=16+count*16
            if not 1<=count<=4096 or table>size:
                raise ValueError('invalid image count')
            for number in range(count):
                w,h,fmt,bank,relative,length=struct.unpack_from('>4H2I',data,offset+16+number*16)
                if not w or not h or not length:
                    continue
                if table+relative>size or length>size-table-relative:
                    raise ValueError('image exceeds chunk')
                images.append(dict(index=number,width=w,height=h,format=fmt,
                                   palette_bank=bank,stored_bytes=length))
        if at+16>=offset:
            break
    return images


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    root=args.directory.resolve()
    rows=[]
    for file in sorted(root.rglob('*')):
        if not file.is_file() or file.suffix.lower()!='.spr':
            continue
        row=dict(path=file.relative_to(root).as_posix(),bytes=file.stat().st_size)
        try:
            if row['bytes']>64*1024*1024:
                raise ValueError('input exceeds inspection budget')
            data=file.read_bytes()
            row.update(sha256=hashlib.sha256(data).hexdigest(),images=inspect(data))
        except ValueError as error:
            row['error']=str(error)
        rows.append(row)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(dict(schema=1,scope='header-only; no asset mapping inferred',
                                          files=rows),indent=2)+'\n',encoding='utf-8')
    print(f'{len(rows)} SPRED files; {sum("error" in row for row in rows)} header errors')


if __name__=='__main__':
    main()
