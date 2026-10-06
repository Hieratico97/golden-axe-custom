"""Observe the actual H40 sprite list, including off-screen fetch widths."""
import ctypes as C,hashlib,json
from emulate import Emulator,ROOT
from playtest import fight_keys


def swapped(raw):
    result=bytearray(len(raw));result[::2]=raw[1::2];result[1::2]=raw[::2];return bytes(result)


class SpriteAudit:
    def __init__(self,em):
        self.em=em
        em.core.retro_serialize_size.restype=C.c_size_t
        em.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t]
        self.size=em.core.retro_serialize_size();self.buffer=C.create_string_buffer(self.size)
        self.signature=swapped((ROOT/'assets/custom/city-tiles.bin').read_bytes()[32:288]);self.base=None
    def read_vram(self):
        assert self.em.core.retro_serialize(self.buffer,self.size)
        state=self.buffer.raw
        if self.base is None:
            found=state.find(self.signature);assert found>=32 and state.find(self.signature,found+1)==-1
            self.base=found-32
        return swapped(state[self.base:self.base+65536])
    def sample(self,trim_transparent=False):
        vram=self.read_vram();sat=vram[0xA800:0xAA80]
        counts=[0]*224;widths=[0]*224;seen=set();link=0
        while True:
            assert link<80 and link not in seen,('Invalid native SAT link',link,len(seen))
            seen.add(link);entry=sat[link*8:link*8+8]
            y=(int.from_bytes(entry[:2],'big')&511)-128
            size=entry[2];w=8*((size>>2&3)+1);h=8*((size&3)+1)
            tile=int.from_bytes(entry[4:6],'big')&2047
            xpos=(int.from_bytes(entry[6:8],'big')&511)-128
            actor=any(base<=tile<base+64 for base in (0x580,0x5C0,0x500,0x280)) and tile%16==0
            if trim_transparent and ((size==15 and actor) or trim_transparent=='all'):
                stride=h//8
                filled=[any(vram[(tile+c*stride)*32:(tile+c*stride+stride)*32]) for c in range(w//8)]
                columns=[c for c,opaque in enumerate(filled) if opaque]
                if not columns:y=-128;w=8
                else:
                    left=min(columns);right=w//8-max(columns)-1
                    xpos+=(right if int.from_bytes(entry[4:6],'big')&0x800 else left)*8
                    w=(max(columns)-min(columns)+1)*8
            if trim_transparent and (xpos+w<=0 or xpos>=320):y=-128
            for line in range(max(0,y),min(224,y+h)):
                counts[line]+=1;widths[line]+=w
            link=entry[3]&127
            if not link:break
        return dict(entries=len(seen),max_sprites_per_line=max(counts),max_pixels_per_line=max(widths),
            overflow_lines=sum(n>20 or w>320 for n,w in zip(counts,widths)))

    def entries(self,vram):
        sat=vram[0xA800:0xAA80];seen=set();link=0;rows=[]
        while True:
            assert link<80 and link not in seen,('Invalid SAT link',link)
            seen.add(link);entry=sat[link*8:link*8+8]
            attr=int.from_bytes(entry[4:6],'big');size=entry[2]
            rows.append(dict(index=link,y=(int.from_bytes(entry[:2],'big')&511)-128,
                x=(int.from_bytes(entry[6:8],'big')&511)-128,
                w=8*((size>>2&3)+1),h=8*((size&3)+1),tile=attr&2047,flip=bool(attr&0x800)))
            link=entry[3]&127
            if not link:return rows


def main():
    em=Emulator(ROOT/'build/custom/golden-axe.bin');rows=[];max_entries=0;max_count=0;max_width=0;overflow_frames=0
    try:
        em.run(330);audit=SpriteAudit(em)
        for frame in range(15000):
            em.run(1,fight_keys(em,True))
            if frame%3==0:
                row=audit.sample();max_entries=max(max_entries,row['entries'])
                max_count=max(max_count,row['max_sprites_per_line']);max_width=max(max_width,row['max_pixels_per_line'])
                if row['overflow_lines']:
                    overflow_frames+=1
                    if len(rows)<30:rows.append(dict(frame=frame,jutsu=em.word(0xF164),timer=em.word(0xF160),**row))
            if em.word(0xF10A):break
        assert em.word(0xF10A),'Budget observation did not finish actual level'
        report=dict(ram_modified=False,victory=True,sampled_frames=frame//3+1,
            max_entries=max_entries,max_sprites_per_line=max_count,max_pixels_per_line=max_width,
            overflow_frames=overflow_frames,examples=rows,
            architecture_limits=dict(entries=80,sprites_per_line=20,pixels_per_line=320),
            sources=['https://github.com/libretro/Genesis-Plus-GX/blob/master/core/vdp_render.c',
                'https://github.com/libretro/Genesis-Plus-GX/blob/master/core/vdp_ctrl.c'],
            rom_sha256=hashlib.sha256((ROOT/'build/custom/golden-axe.bin').read_bytes()).hexdigest())
        (ROOT/'build/checks/sprite-budget-review.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report))
    finally:em.close()


if __name__=='__main__':main()
