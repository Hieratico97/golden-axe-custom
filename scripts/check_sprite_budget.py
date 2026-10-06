"""Exhaustive art preservation plus actual SAT widths during controller play."""
import hashlib,json
import numpy as np
from PIL import Image
from emulate import Emulator,ROOT
from review_sprite_budget import SpriteAudit
from record_gameplay import choose_keys
from playtest import fight_keys,JUTSUS


def tile(raw):
    a=np.frombuffer(raw,dtype=np.uint8)
    out=np.empty(64,dtype=np.uint8);out[::2]=a>>4;out[1::2]=a&15
    return out.reshape(8,8)


def piece(raw,first,width):
    out=np.zeros((32,width*8),dtype=np.uint8)
    for col in range(width):
        for row in range(4):
            p=(first+col*4+row)*32
            out[row*8:row*8+8,col*8:col*8+8]=tile(raw[p:p+32])
    return out


def verify_metadata():
    total=0
    for name in ('kakashi','ninja','anbu','renegado','itachi'):
        raw=(ROOT/f'assets/custom/{name}-tiles.bin').read_bytes()
        metas=(ROOT/f'assets/custom/actor-trim-meta-{name}.bin').read_bytes()
        count=len(raw)//2048;assert len(metas)==count*48
        for pose in range(count):
            data=raw[pose*2048:(pose+1)*2048];original=np.zeros((64,64),dtype=np.uint8)
            for n in range(4):
                original[(n//2)*32:(n//2+1)*32,(n%2)*32:(n%2+1)*32]=piece(data,n*16,4)
            for flip in range(2):
                meta=metas[pose*48+flip*24:pose*48+flip*24+24];render=np.zeros((64,64),dtype=np.uint8)
                for n in range(meta[0]+1):
                    y,size,hi,lo,x=meta[1+n*5:6+n*5]
                    x=(x-256 if x>=128 else x)+32;y=(y-256 if y>=128 else y)+64
                    attr=hi*256+lo;width=(size>>2&3)+1
                    art=piece(data,attr&2047,width)
                    if attr&0x800:art=art[:,::-1]
                    assert size&3==3 and 0<=x<=64-width*8 and y in (0,32)
                    render[y:y+32,x:x+width*8]=art
                assert np.array_equal(render,original[:,::-1] if flip else original),(name,pose,flip,'Opaque pixels lost')
                total+=1
    return total


def verify_unions():
    cases=0
    for name in ('kakashi','ninja','anbu','renegado','itachi'):
        raw=(ROOT/f'assets/custom/{name}-tiles.bin').read_bytes();count=len(raw)//2048
        metas=(ROOT/f'assets/custom/actor-trim-union-{name}.bin').read_bytes()
        assert len(metas)==(count+1)*count*48
        occupied=[[np.array(Image.open(ROOT/f'assets/custom/{name}-{p:02}.png'))[n//2*32:(n//2+1)*32,n%2*32:(n%2+1)*32]!=0 for n in range(4)] for p in range(count)]
        for old in range(count+1):
            for new in range(count):
                for flip in range(2):
                    meta=metas[(old*count+new)*48+flip*24:(old*count+new)*48+flip*24+24];seen=set()
                    for n in range(meta[0]+1):
                        y,size,hi,lo,x=meta[1+n*5:6+n*5];attr=hi*256+lo;first=attr&2047
                        number=first//16;left=first%16//4;width=(size>>2&3)+1
                        assert size&3==3 and first%4==0 and number<4 and left+width<=4
                        assert y==((number//2)*32-64)&255
                        xpos=number%2*32-32+left*8
                        assert x==((-xpos-width*8 if flip else xpos)&255) and bool(attr&0x800)==bool(flip)
                        for p in ({new} if old==count else {new,old}):
                            assert not occupied[p][number][:,:left*8].any() and not occupied[p][number][:,(left+width)*8:].any(),(name,old,new,number,'Unsafe union')
                        seen.add(number)
                    for number in set(range(4))-seen:
                        assert not occupied[new][number].any()
                        if old<count:assert not occupied[old][number].any()
                    cases+=1
    return cases


def render_packed(raw,meta,width,height,center):
    canvas=np.zeros((height+16,width+16),dtype=np.uint8)
    for n in range(meta[0]+1):
        y,size,hi,lo,x=meta[3+n*5:8+n*5];attr=hi*256+lo;w=(size>>2&3)+1;h=(size&3)+1
        art=np.zeros((h*8,w*8),dtype=np.uint8)
        for col in range(w):
            for row in range(h):
                p=((attr&2047)+col*h+row)*32
                art[row*8:row*8+8,col*8:col*8+8]=tile(raw[p:p+32])
        if attr&0x800:art=art[:,::-1]
        x=(x-256 if x>=128 else x)+center;y=(y-256 if y>=128 else y)+height
        assert x>=-8 and y>=-8 and x+w*8<=width+8 and y+h*8<=height+8
        canvas[y+8:y+8+h*8,x+8:x+8+w*8]=art
    assert not canvas[:8,:].any() and not canvas[:, :8].any()
    assert not canvas[height+8:,:].any() and not canvas[:,width+8:].any()
    return canvas[8:height+8,8:width+8]


def verify_packed_effects_and_props():
    from prepare_custom import indexed,SP,BP
    preview=Image.open(ROOT/'assets/custom/jutsu-preview.png');cases=0
    for family in range(7):
        raw=(ROOT/f'assets/custom/jutsu-{family}-tiles.bin').read_bytes()
        metadata=(ROOT/f'assets/custom/jutsu-{family}-meta.bin').read_bytes()
        for pose in range(4):
            original=np.array(indexed(preview.crop((pose*96,family*64,(pose+1)*96,(family+1)*64)),BP if family in (3,5,6) else SP,True))
            for flip in range(2):
                p=pose*128+flip*64;rendered=render_packed(raw[pose*3072:(pose+1)*3072],metadata[p:p+64],96,64,48)
                assert np.array_equal(rendered,original[:,::-1] if flip else original),('Jutsu pixels changed',family,pose,flip)
                cases+=1
    raw=(ROOT/'assets/custom/props-tiles.bin').read_bytes();metadata=(ROOT/'assets/custom/props-meta.bin').read_bytes()
    for kind in range(6):
        original=np.array(Image.open(ROOT/f'assets/custom/prop-{kind}.png'))
        rendered=render_packed(raw[kind*768:(kind+1)*768],metadata[kind*16:(kind+1)*16],32,48,16)
        assert np.array_equal(rendered,original),('Prop pixels changed',kind)
        cases+=1
    return cases


def main():
    metadata_cases=verify_metadata();union_cases=verify_unions();packed_cases=verify_packed_effects_and_props();em=Emulator(ROOT/'build/custom/golden-axe.bin')
    maximum=dict(entries=0,sprites_per_line=0,pixels_per_line=0);checked=0;trimmed=0;culled=0;facings=set();families=set();overflow=[];worst=None;overflow_count=0;deferred_frames=0;deferred_pieces=0
    try:
        em.run(350);audit=SpriteAudit(em);casts=set();framed=set();story={};boss={};last_cast=0
        for frame in range(18000):
            wave=min(9,em.word(0xC210)//224)
            em.run(1,choose_keys(em,frame,casts,framed,story,boss))
            if em.word(0xF184)!=last_cast:
                casts.add(wave);last_cast=em.word(0xF184)
            vram=audit.read_vram();entries=audit.entries(vram);counts=[0]*224;widths=[0]*224
            deferred=em.word(0xF36C);deferred_frames+=bool(deferred);deferred_pieces+=deferred
            for e in entries:
                for line in range(max(0,e['y']),min(224,e['y']+e['h'])):
                    counts[line]+=1;widths[line]+=e['w']
                if e['y']==-128 and (e['x']+e['w']<=0 or e['x']>=320):culled+=1
                base=next((b for b in (0x580,0x5C0,0x500,0x280) if b<=e['tile']<b+64),None)
                if base is None or e['h']!=32:continue
                relative=e['tile']-base;left=(relative%16)//4;w=e['w']//8
                assert relative%4==0 and left+w<=4,('Invalid actor stride',e)
                origin=(base+(relative//16)*16)*32
                for col in (*range(left),*range(left+w,4)):
                    assert not any(vram[origin+col*128:origin+(col+1)*128]),('Clipped opaque actor column',frame,e,col)
                trimmed+=w<4;checked+=1;facings.add(int(e['flip']))
                if base!=0x580:families.add(em.byte({0x5C0:0xD100,0x500:0xD180,0x280:0xD200}[base])&127)
            maximum['entries']=max(maximum['entries'],len(entries))
            maximum['sprites_per_line']=max(maximum['sprites_per_line'],max(counts))
            if max(widths)>maximum['pixels_per_line']:
                line=max(range(224),key=lambda l:widths[l]);worst=dict(frame=frame,jutsu=em.word(0xF164),timer=em.word(0xF160),line=line,width=widths[line],entries=[e for e in entries if e['y']<=line<e['y']+e['h']])
            maximum['pixels_per_line']=max(maximum['pixels_per_line'],max(widths))
            if max(counts)>20 or max(widths)>320:
                overflow_count+=1
                if len(overflow)<12:
                    line=max(range(224),key=lambda l:widths[l]);overflow.append(dict(frame=frame,jutsu=em.word(0xF164),timer=em.word(0xF160),line=line,width=widths[line],entries=[e for e in entries if e['y']<=line<e['y']+e['h']]))
            if em.word(0xF10A):break
        assert em.word(0xF10A),'SAT audit did not win actual level'
        assert all(em.word(0xF190+i*2)>0 for i in range(7)),'Missing real jutsu contact'
        assert facings=={0,1} and checked>1000 and trimmed>1000 and culled>0
        report=dict(result='fail' if overflow else 'pass',ram_modified=False,metadata_render_cases=metadata_cases,
            union_metadata_cases=union_cases,packed_effect_and_prop_cases=packed_cases,
            controller_frames=frame+1,actual_actor_piece_checks=checked,trimmed_piece_samples=trimmed,
            offscreen_cull_samples=culled,maximum=maximum,limits=dict(entries=80,sprites_per_line=20,pixels_per_line=320),
            overflow_frames=overflow_count,worst=worst,overflow_examples=overflow,facings=sorted(facings),enemy_families=sorted(families),
            optional_piece_deferral_frames=deferred_frames,optional_pieces_deferred=deferred_pieces,elemental_fire_counters=em.word(0xF368),
            all_jutsu_contacts=True,victory=True,rom_sha256=hashlib.sha256((ROOT/'build/custom/golden-axe.bin').read_bytes()).hexdigest())
        (ROOT/'build/checks/sprite-budget-check.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({k:v for k,v in report.items() if k not in ('worst','overflow_examples')}));assert not overflow,'Actual VDP sprite fetch overflow'
    finally:em.close()


if __name__=='__main__':main()
