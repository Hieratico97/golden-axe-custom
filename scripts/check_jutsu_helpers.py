"""Controller-only approach used by focused jutsu checks."""
from playtest import start_game,fight_keys,dismiss_story


def reach_boss(em):
    start_game(em)
    for frame in range(12000):
        em.run(1,fight_keys(em,True))
        if em.word(0xF220):break
    assert em.word(0xF220);dismiss_story(em);em.run(30)


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
