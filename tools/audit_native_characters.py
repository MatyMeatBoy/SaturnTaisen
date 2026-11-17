"""Read-only native NC inventory and byte-exact links to observed VDP1 bodies."""
import argparse,hashlib,json,mmap,struct
from pathlib import Path
from audit_sdk import files

HEADER=bytes.fromhex('00020000000000000000000000000000')
def inspect_native_character(data):
    if len(data)<0x610 or bytes(data[:16])!=HEADER:raise ValueError('Unknown/truncated Saturn NC resource')
    count=data[16]
    if 17+count*9>0x410:raise ValueError('Invalid NC table extent')
    parts=[]
    for index in range(count):
        at=17+index*9
        parts.append(dict(index=index,sheet=data[at],coordinates=list(struct.unpack_from('>4h',data,at+1))))
    return dict(part_count=count,parts=parts,palette_offset=0x410,palette_bytes=512,
                palette_sha256=hashlib.sha256(data[0x410:0x610]).hexdigest(),pixel_offset=0x610,pixel_bytes=len(data)-0x610)

def state_vectors(data):
    if len(data)<44 or struct.unpack_from('<II',data)!=(0x53525354,9) or data[8:15]!=b'sakura\0' or struct.unpack_from('<I',data,40)[0]!=0x4D414348:
        raise ValueError('Requires Sakura state version9')
    offset=44;result=[]
    for expected in (0x100000,0x100000,0x80000,0x80000,0x40000,0x40000,0x80000,0x1000):
        if offset+8>len(data):raise ValueError('Truncated state')
        length=struct.unpack_from('<Q',data,offset)[0];offset+=8
        if length!=expected or offset+length>len(data):raise ValueError('Invalid state memory extent')
        result.append(data[offset:offset+length]);offset+=length
    return result

def observed_bodies(data):
    vectors=state_vectors(data);vram=vectors[3];address=0;visited=set();stack=[];result=[]
    for _ in range(4096):
        if address in visited or address+32>len(vram):break
        visited.add(address);words=struct.unpack_from('>16H',vram,address)
        if words[0]&0x8000:break
        kind=words[0]&15;jump=(words[0]>>12)&7
        if jump<4 and kind==0 and words[2]==0xA0:
            width=((words[5]>>8)&63)*8;height=words[5]&255;start=words[4]*8;length=width*height
            if width and height>=80 and start+length<=len(vram):
                result.append(dict(command=address,width=width,height=height,pixels=vram[start:start+length]))
        if jump in (0,4):address+=32
        elif jump in (1,5):address=words[1]*8
        elif jump in (2,6):stack.append(address+32);address=words[1]*8
        elif stack:address=stack.pop()
        else:break
    return result,vectors[7]

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--disc',type=Path,action='append',required=True)
    parser.add_argument('--state',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();bodies,cram=observed_bodies(args.state.read_bytes()) if args.state else ([],b'');rows=[]
    for number,path in enumerate(args.disc,1):
        with path.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as iso:
            for name,lba,size in files(iso):
                stem=Path(name).stem
                if not stem.startswith('NC') or not stem[2:].isdigit():continue
                if size>16*1024*1024 or lba*2048+size>len(iso):raise ValueError('Invalid NC file extent')
                raw=iso[lba*2048:lba*2048+size];row=inspect_native_character(raw)
                row.update(disc=number,path=name,bytes=size,sha256=hashlib.sha256(raw).hexdigest(),observed=[])
                for body in bodies:
                    offset=raw.find(body['pixels'],0x610)
                    if offset>=0:
                        palettes=[bank for bank in range(8) if raw[0x410:0x610]==cram[bank*512:(bank+1)*512]]
                        row['observed'].append(dict(command=body['command'],width=body['width'],height=body['height'],offset=offset,palette_banks=palettes))
                rows.append(row)
    report=dict(schema=1,scope='native metadata; sheet sizes and PC pose mapping not inferred',files=rows,
                unique_names=len({row['path'] for row in rows}),observed_matches=sum(len(row['observed']) for row in rows))
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f"{report['unique_names']} native identities; {report['observed_matches']} byte-exact body matches")
if __name__=='__main__':main()
