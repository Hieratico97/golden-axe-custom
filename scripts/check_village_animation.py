"""Check real NPC tile pixels, control cadence, reverse scroll and freezing."""
import ctypes as C
import hashlib,json,struct
from PIL import Image,ImageDraw
from emulate import Emulator,ROOT
from playtest import start_game,fight_keys


def swapped(raw):
    result=bytearray(len(raw));result[::2]=raw[1::2];result[1::2]=raw[::2];return bytes(result)


class VillageAudit:
    def __init__(self,em):
        self.em=em;self.meta=json.loads((ROOT/'assets/custom/scene-npc-report.json').read_text())
        self.tiles=(ROOT/'assets/custom/scene-npc-tiles.bin').read_bytes();self.n=self.meta['tiles_per_frame']
        self.prefix=swapped((ROOT/'assets/custom/city-tiles.bin').read_bytes())[32:288]
        em.core.retro_serialize_size.restype=C.c_size_t
        em.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t]
        self.size=em.core.retro_serialize_size();self.buffer=C.create_string_buffer(self.size)
        self.base=None;self.checked=0;self.phases={str(i):set() for i in range(4)}
    def sample(self):
        em=self.em;assert em.core.retro_serialize(self.buffer,self.size)
        state=self.buffer.raw
        if self.base is None:
            p=state.find(self.prefix);assert p>=32 and state.find(self.prefix,p+1)==-1;self.base=p-32
        vram=swapped(state[self.base:self.base+65536])
        phase=em.word(0xD962);assert phase in range(4)
        camera=em.word(0xF2E2)
        assert em.word(0xF1FC)<=4096
        for tile in self.meta['tiles']:
            if not camera-1<=tile['column']<=camera+41:continue
            pos=(phase*self.n+tile['index'])*32;slot=tile['slot']
            assert vram[slot*32:(slot+1)*32]==self.tiles[pos:pos+32],('NPC pixels',tile,phase,camera)
            self.checked+=1
            if camera<=tile['column']<=camera+39:self.phases[str(tile['npc'])].add(phase)


em=Emulator(ROOT/'build/custom/golden-axe.bin')
try:
    start_game(em);audit=VillageAudit(em);cadence=0;held=0;maxbytes=0;maxgroups=0;native_holds=[];recent_paints=[];last_dialogue=-100;dialogue_exit_holds=[]
    hero_lag=0;maximum_hero_lag=0
    for frame in range(12000):
        before=em.word(0xC17A);stop=em.word(0xF150)
        age=em.word(0xD960);phase=em.word(0xD962)
        paint=em.word(0xD964);cast=em.word(0xF160);dialogue=em.word(0xF204)
        if dialogue:last_dialogue=frame
        em.run(1,fight_keys(em,True))
        hero_lag=hero_lag+1 if em.word(0xD070)!=em.word(0xD072) and not em.word(0xF160) and not em.word(0xF204) else 0
        maximum_hero_lag=max(maximum_hero_lag,hero_lag)
        if paint!=em.word(0xD964) and em.word(0xD966):recent_paints.append(frame)
        delta=(em.word(0xC17A)-before)&65535
        if delta!=1:
            # v0.20 already has brief native holds during streamed jutsus.
            # A village transfer must not add one in its frame or the next.
            assert not any(frame-1<=p<=frame for p in recent_paints),('NPC transfer delayed input',frame)
            # v0.24 splits the panel erase and HUD rebuild. The old allowance
            # for a hold immediately after dialogue is intentionally removed.
            assert cast or dialogue or em.word(0xF160) or em.word(0xF204),('New hold outside native effects',frame)
            if not(cast or dialogue or em.word(0xF160) or em.word(0xF204)):dialogue_exit_holds.append(frame)
            native_holds.append(frame)
        cadence+=1
        if stop:
            assert age==em.word(0xD960) and phase==em.word(0xD962),'NPC moved in hit-stop'
            held+=1
        maxbytes=max(maxbytes,em.word(0xD968));maxgroups=max(maxgroups,em.word(0xD96C))
        if frame%9==0:audit.sample()
        if em.word(0xF10A):break
    assert em.word(0xF10A),'Village animation playthrough did not win'
    assert all(p=={0,1,2,3} for p in audit.phases.values()),audit.phases
    assert held>20 and 0<maxbytes<=2048 and maxgroups<30
    phases={k:sorted(v) for k,v in audit.phases.items()}
    late_actor_windows=em.word(0xF378)
    assert late_actor_windows<cadence//10,'Actor transfers were routinely deferred'
    assert maximum_hero_lag<=4,('Hero pose stalled',maximum_hero_lag)
    # Restart clears the shadow's animation cache; actual reverse streaming
    # must restore animated source pixels at the current resident phase.
    em.run(1,[3]);start_game(em);audit.sample()
    assert em.word(0xD960)<100 and em.word(0xD964)<4,'Animation cache survived restart'
    for frame in range(1200):
        em.run(1,fight_keys(em))
        if not em.word(0xC26C):break
    assert not em.word(0xC26C)
    frames=[];seen=set()
    for frame in range(600):
        before=em.word(0xC17A);em.run(1)
        assert ((em.word(0xC17A)-before)&65535)==1
        audit.sample()
        phase=em.word(0xD962)
        if phase not in seen and frame<160:
            seen.add(phase);frames.append((phase,em.frame.copy()))
        if frame<160 and frame%8==0:frames.append((phase,em.frame.copy()))
    assert seen=={0,1,2,3},seen
    frames[0][1].resize((960,672),0).save(ROOT/'build/checks/village-idle-v21.gif',save_all=True,
        append_images=[im.resize((960,672),0) for _,im in frames[1:]],duration=130,loop=0)
    unique={}
    for phase,im in frames:unique.setdefault(phase,im)
    contact=Image.new('RGB',(1280,248),'#152233');draw=ImageDraw.Draw(contact)
    for phase,im in sorted(unique.items()):
        contact.paste(im,(phase*320,24));draw.text((phase*320+8,6),f'NPC frame {phase}',fill='white')
    contact.save(ROOT/'build/checks/village-idle-v21-contact.png')
    em.run(1,[3]);em.run(3);assert em.byte(0xC175)
    age=em.word(0xD960);phase=em.word(0xD962);paints=em.word(0xD964)
    em.run(120,[7,0,1]);audit.sample()
    assert (age,phase,paints)==(em.word(0xD960),em.word(0xD962),em.word(0xD964))
    em.run(1,[3]);em.run(4);assert not em.byte(0xC175)
    for frame in range(250):
        em.run(1,[7]);audit.sample()
        if em.word(0xC210)>120:break
    assert em.word(0xC210)>80
    right_world=em.word(0xD01C)+em.word(0xC210)
    for frame in range(250):
        em.run(1,[6]);audit.sample()
    left_world=em.word(0xD01C)+em.word(0xC210)
    assert left_world<right_world-100,'Hero did not walk back through the arena'
    # Golden Axe locks the camera behind each cleared encounter. Verify the
    # reversible allocator separately; do not pretend controls rewound it.
    scene=(ROOT/'assets/custom/scene-events.bin').read_bytes()
    offsets=struct.unpack('>281I',(ROOT/'assets/custom/scene-event-offsets.bin').read_bytes())
    display=struct.unpack('>8960H',(ROOT/'assets/custom/scene-display.bin').read_bytes())
    logical=struct.unpack('>8960H',(ROOT/'assets/custom/scene-logical.bin').read_bytes())
    resident=[0]*640
    for q in range(9):resident[q]=q
    for y in range(28):
        for x in range(42):resident[display[y*320+x]&2047]=logical[y*320+x]
    initial=resident.copy();reversed_events=0
    for column in range(1,281):
        pos=offsets[column];count=struct.unpack_from('>H',scene,pos)[0]
        for i in range(count):
            slot,new,old=struct.unpack_from('>3H',scene,pos+2+i*6)
            assert resident[slot]==old,('Forward lifetime mismatch',column,slot,new,old)
            resident[slot]=new
    for column in range(280,0,-1):
        pos=offsets[column];count=struct.unpack_from('>H',scene,pos)[0]
        for i in range(count):
            slot,new,old=struct.unpack_from('>3H',scene,pos+2+i*6)
            assert resident[slot]==new,('Reverse lifetime mismatch',column,slot,new,old)
            resident[slot]=old;reversed_events+=1
    assert resident==initial,'Reverse stream did not reconstruct initial residency'
    report=dict(result='pass',ram_modified=False,version='0.21',victory=True,restart=True,pause_freezes=True,
        hitstop_samples=held,playthrough_frames=cadence,native_jutsu_or_dialogue_holds=len(native_holds),
        npc_transfer_frame_holds=0,dialogue_exit_hold_frames=dialogue_exit_holds,idle_controller_frames_without_drops=600,npc_phases=phases,
        animated_tile_pixels_checked=audit.checked,maximum_npc_bytes=maxbytes,maximum_npc_dma_runs=maxgroups,
        backtracking_within_arena=True,reversible_allocator_events=reversed_events,
        native_camera_rewind_tested=False,rom_sha256=hashlib.sha256((ROOT/'build/custom/golden-axe.bin').read_bytes()).hexdigest())
    report.update(late_actor_transfer_windows=late_actor_windows,maximum_hero_pose_lag_frames=maximum_hero_lag)
    (ROOT/'build/checks/village-animation-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
finally:em.close()
