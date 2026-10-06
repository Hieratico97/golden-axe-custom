"""Exercise directional remates against surviving opponents using controls."""
import json,hashlib
from emulate import Emulator,ROOT
from playtest import start_game,fight_keys,dismiss_story

def fixed(em,address):
    value=(em.word(address)<<16)|em.word(address+2)
    return (value-0x100000000 if value&0x80000000 else value)/65536

results=[]
for route,name in enumerate(('neutral','lunge','sweep','uppercut')):
    em=Emulator(ROOT/'build/custom/golden-axe.bin')
    try:
        start_game(em)
        for frame in range(15000):
            em.run(1,fight_keys(em,True))
            if em.word(0xF220):break
        assert em.word(0xF220),'Boss not reached'
        dismiss_story(em);em.run(80)
        initial=em.word(0xF2D8+route*2);poses=set();contacts=[]
        for frame in range(4500):
            keys=fight_keys(em)
            if 0 in keys:
                if route==3:keys=[0,4]
                elif route in (1,2) and em.word(0xF152)>=2:
                    forward=6 if em.byte(0xD044)&1 else 7
                    keys=[0,forward if route==1 else 13-forward]
            before=em.word(0xF2D8+route*2)
            em.run(1,keys)
            if em.word(0xF2D4)==route:poses.add(em.word(0xD070))
            if em.word(0xF2D8+route*2)>before:
                alive=[s for s in (0xD100,0xD180) if em.byte(s)&128 and em.byte(s+0x64)>0]
                contacts.append(dict(frame=frame,alive=[dict(slot=hex(s),hp=em.byte(s+0x64),vx=fixed(em,s+0x2C),vy=fixed(em,s+0x34)) for s in alive]))
                em.save(ROOT/f'build/checks/combo-{name}-v14.png')
                # A finishing blow can kill a clone. ComboHitMotion deliberately
                # leaves dead actors to native death physics; require a later
                # contact against a survivor before checking the route impulse.
                impulse=any(abs(t['vx'])>=4 for t in contacts[-1]['alive']) if route==1 else any(-2<t['vy']<0 for t in contacts[-1]['alive']) if route==2 else any(t['vy']<-4 for t in contacts[-1]['alive']) if route==3 else True
                if impulse and (len(contacts)>=2 or route in (1,2)):break
        assert contacts,(name,'No confirmed contact')
        if route:assert any(p>=45 for p in poses),(name,'No new attack drawing',poses)
        if route==1:assert any(abs(t['vx'])>=4 for c in contacts for t in c['alive']),contacts
        if route==2:assert any(-2<t['vy']<0 for c in contacts for t in c['alive']),contacts
        if route==3:assert any(t['vy']<-4 for c in contacts for t in c['alive']),contacts
        results.append(dict(route=name,poses=sorted(poses),contacts=contacts))
    finally:em.close()
report=dict(result='pass',ram_modified=False,routes=results,rom_sha256=hashlib.sha256((ROOT/'build/custom/golden-axe.bin').read_bytes()).hexdigest())
(ROOT/'build/checks/combo-variety-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
