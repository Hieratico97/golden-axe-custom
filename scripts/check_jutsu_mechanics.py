"""Verify technique impulses, pin poses and Kamui absorption with real input."""
import hashlib,json
from emulate import Emulator,ROOT
from playtest import start_game,fight_keys,dismiss_story,select_jutsu,JUTSUS


def fixed(em,address):
    value=(em.word(address)<<16)|em.word(address+2)
    return (value-0x100000000 if value&0x80000000 else value)/65536


def reach_boss(em):
    start_game(em)
    for frame in range(12000):
        em.run(1,fight_keys(em,True))
        if em.word(0xF220):break
    assert em.word(0xF220);dismiss_story(em)
    em.run(30)


def cast_keys(em,index,frame):
    if em.word(0xF160):return []
    if em.word(0xF182)!=index:return [4,1] if frame%2==0 else []
    dx=em.word(0xD11C)-em.word(0xD01C);dy=em.word(0xD120)-em.word(0xD020)
    if abs(dy)>5:return [5 if dy>0 else 4]
    direction=7 if dx>=0 else 6
    if abs(dx)>65:return [direction]
    if (em.byte(0xD044)&1)!=(dx<0):return [direction]
    if em.word(0xF162) or em.byte(0xD042)&127:return []
    return [1] if frame%2==0 else []


rows=[]
for index,name in enumerate(JUTSUS):
    em=Emulator(ROOT/'build/custom/golden-axe.bin')
    try:
        reach_boss(em);select_jutsu(em,index)
        last_contact=em.word(0xF3E8);last_melee=em.word(0xF156);samples=[];seen=set()
        start_dash=em.word(0xF3F6);wall_after_cast=False;stopped=[]
        for frame in range(1600):
            pre_stop=em.word(0xF150);timer=em.word(0xF160)
            active=[s for s in (0xD000,0xD100,0xD180,0xD200) if em.byte(s)&128]
            positions=tuple(em.word(s+0x1C)+em.word(0xC210) for s in active)
            em.run(1,cast_keys(em,index,frame))
            if pre_stop:
                after=tuple(em.word(s+0x1C)+em.word(0xC210) for s in active)
                assert positions==after,('Hit-stop moved actors',name,frame,pre_stop,positions,after)
                assert em.word(0xF160)==timer,'Jutsu animation advanced during hit-stop'
                stopped.append(pre_stop)
            for slot,state in ((0xD100,0xF390),(0xD180,0xF3A0),(0xD200,0xF3B0)):
                if em.byte(slot)&128 and em.byte(slot+0x64)>0:
                    if em.word(state+0xC):seen.add(em.word(slot+0x70))
            if em.word(0xF3E8)>last_contact:
                for slot,state in ((0xD100,0xF390),(0xD180,0xF3A0),(0xD200,0xF3B0)):
                    if not em.byte(slot)&128 or not em.byte(slot+0x64):continue
                    if em.word(state+6)!=(6,4,6,2,3,4,3)[index]:continue
                    samples.append(dict(slot=hex(slot),hp=em.byte(slot+0x64),vx=fixed(em,slot+0x2C),
                        vz=fixed(em,slot+0x34),pin=em.word(state+0xC),pose=em.word(slot+0x70)))
                last_contact=em.word(0xF3E8)
                em.save(ROOT/f'build/checks/jutsu-{name}-contact-v17.png')
            if index==5 and samples and not em.word(0xF160) and em.word(0xF3EE):
                assert em.byte(0xD700) and em.word(0xD772)==1,'Persistent wall lost its solid drawing'
                wall_after_cast=True
            if samples and not em.word(0xF160):break
        assert samples,(name,'No surviving opponent contacted')
        assert em.word(0xF156)==last_melee,(name,'Jutsu falsely added melee contacts')
        assert stopped,(name,'No observed hit-stop')
        if index==0:assert any(abs(s['vx'])>=3.9 and s['vz']<-2 for s in samples),samples
        if index==1:assert any(s['vz']<-4 for s in samples),samples
        if index==2:assert any(s['pin']>=20 for s in samples) and 19 in seen,(samples,seen)
        if index==3:assert any(abs(s['vx'])>=2 and s['vz']<0 for s in samples),samples
        if index==4:assert any(abs(s['vx'])>=5.9 for s in samples),samples
        if index==5:assert wall_after_cast and any(s['vz']<-3 for s in samples),samples
        if index==6:assert any(s['pin']>=80 for s in samples) and 18 in seen,(samples,seen)
        rows.append(dict(jutsu=name,contacts=samples,hit_stop=sorted(set(stopped)),pin_poses=sorted(seen),
            dash_pixels=em.word(0xF3F6)-start_dash,persistent_wall=wall_after_cast))
        print(name+' mechanics passed',flush=True)
    finally:em.close()
em=Emulator(ROOT/'build/custom/golden-axe.bin')
try:
    reach_boss(em);select_jutsu(em,1);absorbed=False;casts=0
    for frame in range(3000):
        keys=[]
        if em.word(0xF160):
            before=em.byte(0xFE7E);em.run(1)
            assert em.byte(0xFE7E)>=before,'Kamui invulnerability failed'
        else:
            if em.word(0xF22A) and not em.word(0xF162):
                keys=[1] if frame%2==0 else []
            else:
                # Evade while waiting for the next real projectile, then cast
                # immediately instead of standing inside the clones' melee.
                if em.word(0xD020)>120:keys=[4]
                else:keys=[6 if frame%300<150 else 7]
            em.run(1,keys)
        casts=em.word(0xF184)
        if em.word(0xF3EA):absorbed=True;break
    assert absorbed,'Kamui never absorbed a real boss projectile'
    absorb=em.word(0xF3EA);em.save(ROOT/'build/checks/kamui-absorption-v17.png')
finally:em.close()
report=dict(result='pass',ram_modified=False,techniques=rows,kamui_absorbed_shots=absorb,
    rom_sha256=hashlib.sha256((ROOT/'build/custom/golden-axe.bin').read_bytes()).hexdigest())
(ROOT/'build/checks/jutsu-mechanics-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
