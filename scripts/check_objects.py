from playtest import start_game
"""Verify street collision, a real melee break, loot and jumping via input only."""
import json
from emulate import Emulator,ROOT
from playtest import select_jutsu

em=Emulator(ROOT/'build/custom/golden-axe.bin')
world=lambda:em.word(0xD01C)+em.word(0xC210)-128
try:
    start_game(em);em.run(32,[7])
    assert 112<=world()<=116 and em.word(0xF1A0)==0,('crate collision',world())
    em.save(ROOT/'build/checks/object-intact.png')
    debris=False;poses=set()
    for frame in range(48):
        em.run(1,[0]);poses.add(em.word(0xD070))
        if em.word(0xF1E0):
            debris=True;em.save(ROOT/'build/checks/object-break.png')
        if em.word(0xF1A0)==1:break
    assert em.word(0xF1A0)==1 and debris,('melee break',poses)
    assert poses & {8,9,10,13},('missing punch or native dash-kick pose',poses)
    em.run(12,[7]);em.run(40)
    assert em.word(0xF1A0)==1 and em.word(0xF180)==120,'Full chakra consumed the scroll'
    em.save(ROOT/'build/checks/object-scroll.png')
    # Leave the scroll, spend chakra, and return. Inspect the actual pickup delta.
    em.run(36,[6]);em.run(30);select_jutsu(em,1)
    for attempt in range(120):
        em.run(1,[1]);em.run(1)
        if em.word(0xF160):break
    assert em.word(0xF160) and em.word(0xF180)<120,('cast from idle',hex(em.word(0xD042)))
    em.run(76)
    pickup=None
    for frame in range(100):
        before=em.word(0xF180);em.run(1,[7])
        if em.word(0xF1A0)==2:
            pickup=(before,em.word(0xF180));break
    assert pickup and pickup[1]>=min(120,pickup[0]+40),('chakra pickup',pickup)
    assert em.word(0xF1E8)==1
    em.save(ROOT/'build/checks/object-collected.png')
    em.core.retro_reset();start_game(em)
    for attempt in range(30):
        em.run(1,[5,0]);em.run(100)
        if not em.byte(0xD164):break
    em.run(120);assert not em.word(0xC26C),'Ninja still interferes with jump check'
    assert em.word(0xF1A0)==0
    em.run(32,[7])
    em.run(1,[8,7]);air=False;furthest=world()
    for frame in range(40):
        em.run(1,[7]);air|=bool(em.byte(0xD003)&32)
        furthest=max(furthest,world())
    assert air and furthest>142 and em.word(0xF1A0)==0,('jump obstacle',furthest)
    report=dict(result='pass',ram_modified=False,solid_collision=True,
                melee_break=True,debris=True,full_chakra_preserves_loot=True,
                pickup=pickup,jump_over_intact_object=True,objects=13,breakable=11)
    (ROOT/'build/checks/objects-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
finally:em.close()
