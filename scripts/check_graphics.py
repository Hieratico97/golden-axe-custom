from playtest import start_game
"""Audit actual VDP tile memory during play, effects, pause and restart.

Controller input only: this catches tile uploads that overwrite scene or actor
art, including the original GO cue. The libretro state stores words swapped.
"""
import ctypes as C
import hashlib
import json
from emulate import Emulator, ROOT
from playtest import fight_keys,select_jutsu,begin_jutsu


def swapped(raw):
    result=bytearray(len(raw))
    result[::2]=raw[1::2];result[1::2]=raw[::2]
    return bytes(result)


class Audit:
    def __init__(self, em):
        self.em=em
        self.rom=(ROOT/'build/custom/golden-axe.bin').read_bytes()
        self.static=[(address, name, swapped((ROOT/f'assets/custom/{name}-tiles.bin').read_bytes()))
                     for address,name in ((0,'city'),(0x9200,'hud'),(0x8000,'props'),
                                          (0x5900,'shadow'),(0x5820,'dust'),(0x5980,'weapons'),(0x9800,'font'),(0x7800,'boss-fx'),(0x5D20,'ui-trim'))]
        self.static[0]=(0,'city-signature',self.static[0][2][:288])
        self.grids=[(a,n,(ROOT/f'assets/custom/{n}.bin').read_bytes()) for a,n in ((0x4000,'city-grid'),(0x5000,'city-height-grid'))]
        self.samples=0;self.actor_samples=0;self.effects=set();self.types=set();self.facings=set();self.icons=set()
        self.pending=[];self.in_flight_uploads=[]
        em.core.retro_serialize_size.restype=C.c_size_t
        em.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t]
        em.core.retro_serialize.restype=C.c_bool
        self.size=em.core.retro_serialize_size()
        self.buffer=C.create_string_buffer(self.size)
        self.base=None

    def run(self,frames,keys=()):
        for _ in range(frames):
            self.em.run(1,keys)
            if not self.pending:continue
            assert self.em.core.retro_serialize(self.buffer,self.size)
            vram=self.buffer.raw[self.base:self.base+65536]
            for pending in self.pending:
                slot,address,source,pose=pending
                assert self.em.word(slot+0x72)==pose,('Actor DMA did not commit next frame',hex(slot),pose)
                assert ((self.em.word(slot+0x74)<<16)|self.em.word(slot+0x76))==source
                expected=swapped(self.rom[source+pose*2048:source+(pose+1)*2048])
                assert vram[address:address+2048]==expected,('Completed actor drawing differs',hex(slot),pose)
            self.pending=[]

    def sample(self):
        em=self.em
        assert em.core.retro_serialize(self.buffer,self.size)
        state=self.buffer.raw
        if self.base is None:
            signature=self.static[0][2][32:288]
            found=state.find(signature)
            assert found>=32,'Could not locate VDP memory in core state'
            assert state.find(signature,found+1)==-1,'Ambiguous VDP signature'
            self.base=found-32
        vram=state[self.base:self.base+65536]
        for address,name,raw in self.static:
            actual=vram[address:address+len(raw)]
            bad=[i//32 for i in range(0,len(raw),32) if actual[i:i+32]!=raw[i:i+32]]
            assert not bad,(name,'overwritten tiles',bad[:12],len(bad),'sample',self.samples,'scroll',em.word(0xC210),'scene',hex(em.word(0xC172)),'victory',em.word(0xF10A),'cast',em.word(0xF160),'chunk',em.word(0xF1F6))
        for slot,address in ((0xD000,0xB000),(0xD100,0xB800),(0xD180,0xA000),(0xD200,0x5000)):
            kind=em.byte(slot)&127
            if not(em.byte(slot)&128) or kind not in (8,0x31,0x32,0x33):continue
            pose=em.word(slot+0x72)
            source=(em.word(slot+0x74)<<16)|em.word(slot+0x76)
            if not source or pose==65535:continue
            assert 0<=pose<(65 if slot==0xD000 else 20),(hex(slot),'invalid pose',pose)
            expected=swapped(self.rom[source+pose*2048:source+(pose+1)*2048])
            actual=vram[address:address+2048]
            if actual!=expected:
                planned=em.word({0xD000:0xF35C,0xD100:0xF35E,0xD180:0xF360,0xD200:0xF362}[slot])
                assert planned==em.word(slot+0x70)==em.word(0xF294) and planned!=pose
                assert em.byte(0xC183)&1 and not em.word(0xF1FC)
                new=swapped(self.rom[source+planned*2048:source+(planned+1)*2048])
                # Require a sequential word transfer from the exact old pose
                # to the exact planned pose, including the VDP first-word fix.
                cuts=[cut for cut in range(0,2049,2) if actual==new[:cut]+expected[cut:]]
                if not cuts and actual[:2]==expected[:2]:
                    cuts=[cut for cut in range(2,2049,2) if actual[2:]==new[2:cut]+expected[cut:]]
                assert cuts,(hex(slot),'actor pixels are not a sequential DMA',pose,planned,self.samples)
                self.pending.append((slot,address,source,planned))
                self.in_flight_uploads.append(dict(slot=hex(slot),old_pose=pose,new_pose=planned,sample=self.samples,
                    transferred_bytes=max(cuts),next_frame_commit_required=True))
            self.actor_samples+=1
            if kind!=8:self.types.add(kind)
            self.facings.add(em.byte(slot+0x44)&1)
        for origin,name,grid in self.grids:
            for row in range(14):
                actual=bytes(em.byte(origin+row*256+col) for col in range(160))
                assert actual==grid[row*160:(row+1)*160],(name,'wrong map row',row)
        if em.word(0xF292) and not em.word(0xF204) and not em.word(0xF10A):
            selected=em.word(0xF2C4)
            assert 0<=selected<7,('HUD cached selection',selected)
            self.icons.add(selected)
            icon=0x8494 if selected==6 else 0x84A8+selected*4
            for i,pos in enumerate((0xCD2A,0xCD2C,0xCDAA,0xCDAC)):
                value=int.from_bytes(vram[pos:pos+2],'little')
                assert value==icon+i,('HUD technique points outside its icon bank',selected,hex(pos),hex(value),hex(icon+i))
        if em.byte(0xD700):
            pose=em.word(0xD772)
            source=(em.word(0xD774)<<16)|em.word(0xD776)
            assert 0<=pose<4,('effect cache',pose)
            address=em.word(0xD708)*32
            assert address in (0x6000,0x6C00),('effect buffer',hex(address))
            assert vram[address:address+3072]==swapped(self.rom[source+pose*3072:source+(pose+1)*3072]),('effect DMA',pose)
            self.effects.add((em.word(0xF164),pose))
        assert em.word(0xF100)==0 and em.word(0xF106)==0,'Assist state active'
        self.samples+=1


em=Emulator(ROOT/'build/custom/golden-axe.bin')
try:
    start_game(em);audit=Audit(em);audit.sample()
    for index in range(7):
        em.core.retro_reset();start_game(em);audit.sample()
        begin_jutsu(em,index)
        for frame in range(80):audit.run(1);audit.sample()
    assert {k for k,p in audit.effects}==set(range(7)),audit.effects
    assert audit.icons==set(range(7)),('Unseen HUD technique icons',audit.icons)
    audit.run(1,[3]);audit.run(3);assert em.byte(0xC175)
    audit.sample();audit.run(60,[7,0,1]);audit.sample()
    audit.run(1,[3]);audit.run(3);assert not em.byte(0xC175);audit.sample()
    # Reset the core and complete every wave, so GO cue transitions are covered.
    em.core.retro_reset();start_game(em);audit.sample()
    for frame in range(12000):
        audit.run(1,fight_keys(em,magic=True))
        if frame%5==0:audit.sample()
        if frame in (0,600,1200,1800,2400):
            em.save(ROOT/f'build/checks/graphics-stage-{frame}.png')
        if em.word(0xF10A):break
    assert em.word(0xF10A),'No victory during graphics audit'
    assert audit.types=={0x31,0x32,0x33},audit.types
    assert audit.facings=={0,1},audit.facings
    audit.run(10);audit.sample()
    audit.run(1,[3]);start_game(em);assert not em.word(0xF10A);audit.sample()
    assert not audit.pending,'Final actor transfer remains unverified'
    report=dict(result='pass',ram_modified=False,static_tile_regions=9,
                samples=audit.samples,actor_dma_samples=audit.actor_samples,
                in_flight_actor_uploads=audit.in_flight_uploads,
                effect_poses=sorted(audit.effects),hud_technique_icons=sorted(audit.icons),supports=False,map_stride=256,stage_width=2560,enemy_types=[hex(k) for k in sorted(audit.types)],
                facings=sorted(audit.facings),victory=True,restart=True,pause=True,
                rom_sha256=hashlib.sha256(audit.rom).hexdigest())
    (ROOT/'build/checks/graphics-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
finally:em.close()
