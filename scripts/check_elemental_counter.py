"""Cross real boss fire with released techniques using controller input only."""
import hashlib,json
from emulate import Emulator,ROOT
from playtest import select_jutsu,dismiss_story,fight_keys,JUTSUS
from check_jutsu_helpers import reach_boss


rows=[]
for index in (0,2,3,4):
    em=Emulator(ROOT/'build/custom/golden-axe.bin')
    try:
        reach_boss(em);select_jutsu(em,index)
        observed=[];casts=em.word(0xF184)
        for frame in range(4500):
            if em.word(0xF204):dismiss_story(em)
            before=em.word(0xF368);timer=em.word(0xF160)
            fires_before=em.word(0xF23A);boss_x=em.word(0xD11C);boss_lane=em.word(0xD120)
            seal_timer=em.word(0xF224);pattern=em.word(0xF226)
            shots=[dict(timer=em.word(life),x=em.word(x),lane=em.word(y),velocity=em.word(v),
                        kind=em.word(0xF232) if life==0xF22A else 2,life=life)
                   for life,x,y,v in ((0xF22A,0xF22C,0xF22E,0xF230),(0xF2F4,0xF2F6,0xF2F8,0xF2FA))]
            field=em.word(0xF168);lane=em.word(0xF16C);camera=em.word(0xC210)
            keys=[]
            if not timer:
                # Respond to the real hand seals early enough for Kakashi's
                # anticipation; striking clones creates a safe casting window.
                if em.word(0xF226)==2 and 45<em.word(0xF224)<=60 and not em.word(0xF162):
                    dx=em.word(0xD11C)-em.word(0xD01C)
                    dy=em.word(0xD120)-em.word(0xD020)
                    if (em.byte(0xD044)&1)!=(dx<0):keys=[6 if dx<0 else 7]
                    elif abs(dy)>5:keys=[5 if dy>0 else 4]
                    else:keys=[] if 1 in em.keys else [1]
                else:keys=fight_keys(em)
            em.run(1,keys)
            if em.word(0xF368)>before:
                cancelled=[s for s in shots if s['timer']>1 and s['kind']!=1 and not em.word(s['life'])]
                if em.word(0xF23A)>fires_before and not em.word(0xF22A):
                    assert pattern==2 and seal_timer==41,'Unexpected fire spawn'
                    cancelled.append(dict(timer=72,x=boss_x,lane=boss_lane,velocity=em.word(0xF230),
                        kind=2,life=0xF22A,spawned_this_frame=True))
                assert cancelled and 16<=timer<=56,('Counter outside released overlap',index,timer,shots)
                for shot in cancelled:
                    velocity=shot['velocity']-65536 if shot['velocity']&32768 else shot['velocity']
                    distance=abs(shot['x']+(0 if shot.get('spawned_this_frame') else velocity)+camera-field)
                    assert distance<=80 and abs(shot['lane']-lane)<=40,(shot,field,lane,distance)
                assert em.word(0xF36A)>0 and em.word(0xF3E4)>0,'Counter has no release accent'
                observed.append(dict(frame=frame,release_timer=timer,shots=cancelled,
                    field_world_x=field,field_lane=lane,accent=em.word(0xF36A)))
                em.save(ROOT/f'build/checks/counter-{JUTSUS[index]}-v26.png')
                break
        assert observed,('Technique never countered real fire',JUTSUS[index],em.word(0xF184)-casts)
        rows.append(dict(jutsu=JUTSUS[index],casts=em.word(0xF184)-casts,counters=observed))
        print(JUTSUS[index]+' real fire counter passed',flush=True)
    finally:em.close()
report=dict(result='pass',ram_modified=False,techniques=rows,
    rom_sha256=hashlib.sha256((ROOT/'build/custom/golden-axe.bin').read_bytes()).hexdigest())
(ROOT/'build/checks/elemental-counter-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
