"""Observe anticipation, charged-hand alignment and caster protection in real fights."""
import hashlib,json
from emulate import Emulator,ROOT
from playtest import select_jutsu,JUTSUS
from check_jutsu_helpers import reach_boss,cast_keys


def positions(em):
    return [em.word(a) for a in (0xD01C,0xD020,0xD11C,0xD120,0xD19C,0xD1A0,
        0xD21C,0xD220,0xF22C,0xF2F6)]


rows=[]
for index,name in enumerate(JUTSUS):
    em=Emulator(ROOT/'build/custom/golden-axe.bin')
    try:
        reach_boss(em);select_jutsu(em,index)
        for frame in range(1600):
            em.run(1,cast_keys(em,index,frame))
            if em.word(0xF160):break
        assert em.word(0xF160),'Cast did not begin: '+name
        paused=[];charge_offsets=[];health=[];contacts=em.word(0xF3E8)
        for frame in range(200):
            timer=em.word(0xF160);stop=em.word(0xF150);before=positions(em)
            hp=em.byte(0xFE7E);em.run(1)
            if stop:
                assert positions(em)==before,(name,'Anticipation/impact moved actors')
                assert em.word(0xF160)==timer,(name,'Animation moved while physics stopped')
                if timer>=70:paused.append(frame)
            if em.word(0xF160)>=16:
                assert em.byte(0xFE7E)>=hp,(name,'Caster hurt during release',frame)
                health.append(em.byte(0xFE7E))
            if index in (0,2) and 56<em.word(0xF160)<=64 and em.byte(0xD700):
                offset=em.word(0xD71C)-em.word(0xD01C)
                assert abs(offset)==16,(name,'Charge detached from hand',offset)
                charge_offsets.append(offset)
            if not em.word(0xF160):break
        assert len(paused)>=4,(name,'No visible anticipation',paused)
        assert em.word(0xF3E8)>contacts,(name,'Release never contacted an enemy')
        if index in (0,2):assert charge_offsets,(name,'No hand-charge display')
        rows.append(dict(jutsu=name,anticipation_frames=len(paused),
            protected_samples=len(health),charge_offsets=sorted(set(charge_offsets)),
            contacts=em.word(0xF3E8)-contacts))
        print(name+' anticipation and release passed',flush=True)
    finally:em.close()
report=dict(result='pass',ram_modified=False,techniques=rows,
    rom_sha256=hashlib.sha256((ROOT/'build/custom/golden-axe.bin').read_bytes()).hexdigest())
(ROOT/'build/checks/jutsu-spectacle-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
