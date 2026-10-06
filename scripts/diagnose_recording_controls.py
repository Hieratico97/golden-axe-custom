"""Fast real-input rehearsal before encoding a complete gameplay recording."""
import hashlib,json
from emulate import Emulator,ROOT
from record_gameplay import choose_keys,JUTSUS

em=Emulator(ROOT/'build/custom/golden-axe.bin')
try:
    em.run(350)
    cast_waves=set();framed_waves=set();story_frames={};boss_frames={};events=[];last_cast=0
    for frame in range(18000):
        wave=min(9,em.word(0xC210)//224)
        em.run(1,choose_keys(em,frame,cast_waves,framed_waves,story_frames,boss_frames))
        if em.word(0xF184)!=last_cast:
            cast_waves.add(wave);events.append(JUTSUS[em.word(0xF164)]);last_cast=em.word(0xF184)
        if em.word(0xF10A):break
    routes={name:em.word(0xF2D8+i*2) for i,name in enumerate(('neutral','lunge','sweep','uppercut'))}
    report=dict(victory=bool(em.word(0xF10A)),frames=frame+1,routes=routes,
                jutsus=sorted(set(events)),ram_modified=False,
                rom_sha256=hashlib.sha256((ROOT/'build/custom/golden-axe.bin').read_bytes()).hexdigest())
    print(json.dumps(report))
    assert report['victory'] and all(routes.values()) and set(events)==set(JUTSUS),report
finally:em.close()
