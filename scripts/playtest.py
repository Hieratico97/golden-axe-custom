"""Controller navigation shared by integration checks; never writes game RAM."""

JUTSUS=('raikiri','kamui','chidori','katon','suiton','doton','ninken')


def dismiss_story(em):
    for _ in range(240):
        if not em.word(0xF204):return
        keys=[] if em.word(0xF206) or 0 in em.keys else [0]
        em.run(1,keys)
    raise AssertionError('Dialogue did not advance')


def start_game(em):
    em.run(330)
    # Asset decompression can change boot duration. Wait for the actual intro
    # instead of mistaking an uninitialized F204 for a finished dialogue.
    for _ in range(240):
        if em.word(0xF204) and not em.word(0xF200):break
        em.run(1)
    assert em.word(0xF204) and not em.word(0xF200),'Intro did not initialize'
    dismiss_story(em);em.run(24)
    assert em.word(0xF200)==1 and not em.word(0xF204),'Intro did not finish'


def fight_keys(em,magic=False):
    if em.word(0xF204):
        return [] if em.word(0xF206) or 0 in em.keys else [0]
    targets=[s for s in (0xD100,0xD180,0xD200) if em.byte(s)&128 and (em.byte(s)&127) in (0x31,0x32,0x33) and em.byte(s+0x64)>0]
    keys=[]
    if targets:
        slot=min(targets,key=lambda s:abs(em.word(s+0x1C)-em.word(0xD01C)))
        dx=em.word(slot+0x1C)-em.word(0xD01C);dy=em.word(slot+0x20)-em.word(0xD020)
        direction=7 if dx>=0 else 6
        if abs(dy)>5:
            keys.append(5 if dy>0 else 4)
            if abs(dx)>45:keys.append(direction)
        elif abs(dx)>30:
            # Use the native 36px reach when the viewport clamp prevents
            # stepping closer to an enemy at its opposite screen edge.
            edge=(dx>0 and em.word(0xD01C)>=400) or (dx<0 and em.word(0xD01C)<=176)
            if edge and abs(dx)<=36 and (em.byte(0xD044)&1)==(dx<0):keys.append(0)
            else:keys.append(direction)
        elif (em.byte(0xD044)&1)!=(dx<0):
            keys.append(direction)
        else:keys.append(0)
        if magic and not em.word(0xF162) and not em.word(0xF160) and abs(dx)<100:
            # Release a plain A tap to cast; a held chord selects only.
            keys=[] if 1 in em.keys else [1]
    else:
        dy=172-em.word(0xD020)
        if abs(dy)>3:keys.append(5 if dy>0 else 4)
        else:
            x=em.word(0xD01C)+em.word(0xC210)-128
            wood=((0,128,172),(1,288,196),(3,688,172),(4,912,196),(6,1328,172),(7,1536,192),(9,1888,172),(10,2080,196),(11,2304,172))
            close=any(em.word(0xF1A0+i*2)==0 and 0<=px-x<=26 and abs(py-em.word(0xD020))<=18 for i,px,py in wood)
            if close and not(em.byte(0xD044)&1):keys.append(0)
            else:keys.append(7)
    return keys


def select_jutsu(em,index):
    while em.word(0xF182)!=index:
        em.run(1,[4,1]);em.run(1)


def begin_jutsu(em,index):
    select_jutsu(em,index)
    for frame in range(240):
        em.run(1,[7])
        if abs(em.word(0xD11C)-em.word(0xD01C))<88 and (em.byte(0xD042)&127)==0:
            break
    em.run(1)
    em.run(1,[1])
    em.run(1)
    assert em.word(0xF160)>0,(JUTSUS[index],'not activated',hex(em.word(0xD042)))
