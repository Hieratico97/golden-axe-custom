"""Trace clone health transitions in an otherwise controller-free boss window."""
import json
from emulate import Emulator,ROOT
from playtest import start_game,fight_keys,dismiss_story

def actor(em,s):
    return dict(kind=em.byte(s),hp=em.byte(s+0x64),state=em.byte(s+0x42),
        attack=em.byte(s+0x43),flags=em.byte(s+3),x=em.word(s+0x1C),y=em.word(s+0x20),
        owner=hex((em.word(s+0x38)<<16)|em.word(s+0x3A)))

em=Emulator(ROOT/'build/custom/golden-axe.bin')
try:
    start_game(em)
    for _ in range(12000):
        em.run(1,fight_keys(em,True))
        if em.word(0xF220):break
    dismiss_story(em);em.run(480)
    for _ in range(12000):
        em.run(1,fight_keys(em,True))
        if em.word(0xF284):break
    assert em.word(0xF204);dismiss_story(em)
    rows=[]
    for frame in range(2100):
        before={hex(s):actor(em,s) for s in (0xD000,0xD100,0xD180,0xD200)}
        contacts=em.word(0xF156);em.run(1)
        after={hex(s):actor(em,s) for s in (0xD000,0xD100,0xD180,0xD200)}
        for s in (0xD180,0xD200):
            key=hex(s)
            if before[key]['kind']&128 and after[key]['kind']&128 and before[key]['hp']!=after[key]['hp']:
                rows.append(dict(frame=frame,slot=key,before=before,after=after,
                    jutsu=em.word(0xF160),melee_before=contacts,melee_after=em.word(0xF156),
                    friendly_rejected=em.word(0xF324)))
    (ROOT/'build/checks/friendly-damage-review.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps(rows))
finally:em.close()
