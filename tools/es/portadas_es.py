"""Spanish episode title cards (TITLE1..10.BIN of disc 1), drafted by program (T87).

  python -X utf8 tools/es/portadas_es.py [--output DIR]

Each Saturn card is a 320x224 picture (palette, table of cells, 8x8 8 bpp cells; see
docs/research/saturn-bg-format.md). The English lettering is found as the palette indices that are only used
inside the text zone, the sky behind it is filled by diffusion, the Spanish lines are drawn in the card's own
fill and outline colours (Arial Rounded Bold, so it is a draft, not the hand-made lettering) and only the
cells under the lettering are rewritten to the nearest palette colour. The file keeps its size, palette and
table. Output: DIR/SAKURA1/TITLEn.BIN plus a preview sheet; nothing here goes to Git (it derives from game art).
Wire it into a disc with `construir_todo.py --disc 1 --portadas`. The owner asked for generative art for these
cards; this is the fallback, and the Spanish titles are drafts to review.
"""
import argparse
import collections
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import decode_saturn_bg as s  # noqa: E402
from _rutas import OWNER, WORK  # noqa: E402
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageChops

TEXT={1:['Episodio 1:','¡Asalto floral','imperial!'],2:['Episodio 2:','El enemigo es...','¡La Colmena Oscura!'],
3:['Episodio 3:','¿Capitán indigno?'],4:['Episodio 4:','¡Caos! ¡Caos!!','¡El gran estrago!!!'],
5:['Episodio 5:','¡Florece como una flor!','¡Voluntad de doncella!'],6:['Episodio 6:','¿¡La gran caída','de la capital!?'],
7:['Episodio 7:','Batalla decisiva -','¡Vida al límite!'],8:['Episodio 8:','Una cita en días de paz'],
9:['Episodio 9:','El arma definitiva','al descubierto'],10:['Episodio 10:','El juicio final']}
def parse(d):
    pal=[((w&31)*255//31,((w>>5)&31)*255//31,((w>>10)&31)*255//31) for w in struct.unpack_from('>256H',d,0)]
    ent=struct.unpack_from('>1120I',d,512);idx=[[0]*320 for _ in range(224)]
    for c,e in enumerate(ent):
        t=e>>1;b=512+4480+t*64
        for y in range(8):
            for x in range(8):idx[(c//40)*8+y][(c%40)*8+x]=d[b+y*8+x]
    return pal,ent,idx
def nearest(pal,rgb):
    return min(range(256),key=lambda i:sum((pal[i][k]-rgb[k])**2 for k in range(3)))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--output', type=Path, default=WORK / 'builds/es-portadas')
    args = parser.parse_args()
    iso = s.Iso(OWNER / 'local/prepared/disc1/Track 01.iso')
    f = dict(iso.files('SAKURA1'))
    OUT = args.output / 'SAKURA1'
    OUT.mkdir(parents=True, exist_ok=True)
    preview = args.output
    sheet=Image.new('RGB',(640*2,448*5))

    for n in range(1,11):
        d=bytearray(iso.content(f[f'TITLE{n}.BIN']));pal,ent,idx=parse(d)
        zone=(slice(55,170))
        inz=collections.Counter();outz=collections.Counter()
        for y in range(224):
            for x in range(320):
                (inz if 55<=y<170 and 15<=x<310 else outz)[idx[y][x]]+=1
        textidx={i for i,c in inz.items() if c>=12 and outz[i]<=0.02*c}
        mask=Image.new('L',(320,224),0);m=mask.load()
        for y in range(55,170):
            for x in range(15,310):
                if idx[y][x] in textidx:m[x,y]=255
        ys=[y for y in range(224) if any(m[x,y] for x in range(320))];xs=[x for x in range(320) if any(m[x,y] for y in range(224))]
        if not ys:print(n,'no text found');continue
        x0,y0,x1,y1=min(xs),min(ys),max(xs),max(ys)
        rgb=s.decode(bytes(d)).convert('RGB')
        # fill/outline colours: the text colour touching the background is the outline
        dil=mask.filter(ImageFilter.MaxFilter(3));edge=ImageChops.subtract(dil,mask.filter(ImageFilter.MinFilter(3)))
        cnt=collections.Counter();ecnt=collections.Counter();px=rgb.load();ed=edge.load()
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):
                if m[x,y]:
                    cnt[idx[y][x]]+=1
                    if ed[x,y]:ecnt[idx[y][x]]+=1
        cols=[i for i,_ in cnt.most_common(4)]
        outline=max(cols,key=lambda i:ecnt[i]/max(cnt[i],1));fill=[i for i in cols if i!=outline][0] if len(cols)>1 else outline
        # inpaint
        big=mask.filter(ImageFilter.MaxFilter(5));known=ImageChops.invert(big);cur=rgb.copy()
        for it in range(60):cur=Image.composite(rgb,cur.filter(ImageFilter.GaussianBlur(3)),known)
        img=cur.copy();dr=ImageDraw.Draw(img)
        avail=300-x0
        y=y0
        # line tops from the original: label then titles; spacing from original height
        total=len(TEXT[n]);h=y1-y0+1
        lines=TEXT[n];tops=[y0]+[y0+ int(h*0.30)+ k*int(h*0.34) for k in range(len(lines)-1)] if total==3 else [y0,y0+int(h*0.5)]
        sizes=[19]+[26]*(len(lines)-1)
        for i,t in enumerate(lines):
            sz=sizes[i]
            while True:
                fnt=ImageFont.truetype('C:/Windows/Fonts/ARLRDBD.TTF',sz)
                if dr.textlength(t,font=fnt)<=avail or sz<12:break
                sz-=1
            dr.text((x0,tops[i]),t,font=fnt,fill=pal[fill],stroke_width=2 if n not in(2,3,6,9,10) else 2,stroke_fill=pal[outline])
        # write back only inside the repainted zone
        zonebox=big.getbbox();new=img.load();big_l=big.load()
        changed=0
        # re-quantise union of old text zone and new text pixels
        newtext=Image.new('L',(320,224),0);ImageDraw.Draw(newtext)
        diff=ImageChops.difference(img,rgb).convert('L').point(lambda v:255 if v>6 else 0)
        zone_px=ImageChops.lighter(big,diff).filter(ImageFilter.MaxFilter(3)).load()
        for c,e in enumerate(ent):
            t=e>>1;b=512+4480+t*64
            for yy in range(8):
                for xx in range(8):
                    X=(c%40)*8+xx;Y=(c//40)*8+yy
                    if zone_px[X,Y]:
                        d[b+yy*8+xx]=nearest(pal,new[X,Y]);changed+=1
        open(OUT / f'TITLE{n}.BIN','wb').write(bytes(d))
        chk=s.decode(bytes(d)).convert('RGB')
        sheet.paste(rgb.resize((640,448),Image.NEAREST),(0,(n-1)*448))
        sheet.paste(chk.resize((640,448),Image.NEAREST),(640,(n-1)*448))
        print(n,'text idx',len(textidx),'bbox',(x0,y0,x1,y1),'fill',pal[fill],'outline',pal[outline],'cells changed px',changed)
    sheet.crop((0,0,1280,448*5)).save(preview / 'comparacion.png')


if __name__ == '__main__':
    main()
