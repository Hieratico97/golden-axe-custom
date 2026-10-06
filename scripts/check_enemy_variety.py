from playtest import start_game
"""Traverse all waves using controls and verify costume banks and movement."""
import json
from emulate import Emulator,ROOT
from playtest import fight_keys
em=Emulator(ROOT/'build/custom/golden-axe.bin')
seen={};speeds={};shots=[];saved=set()
try:
 start_game(em)
 for frame in range(15000):
  em.run(1,fight_keys(em))
  for slot in (0xD100,0xD180):
   kind=em.byte(slot)&127
   if kind not in (0x31,0x32,0x33) or not(em.byte(slot)&128):continue
   bank=(em.word(slot+0x74)<<16)|em.word(slot+0x76)
   if bank:seen.setdefault(kind,set()).add(bank)
   velocity=(em.word(slot+0x2C)<<16)|em.word(slot+0x2E)
   if velocity&0x80000000:velocity-=0x100000000
   if em.byte(slot+0x43)<=2 and not(em.byte(slot+0x46)&64) and velocity:
    speeds.setdefault(kind,set()).add(abs(velocity))
   # Actor screen coordinates include the native 128px sprite-table bias.
   # Capture a living actor after its requested pose reached VRAM. A ninja
   # may enter the screen jumping or attacking, without a grounded walk pose.
   if kind not in saved and em.byte(slot+0x64)>0 and 144<em.word(slot+0x1C)<=432 and em.word(slot+0x70)==em.word(slot+0x72) and 140<em.word(slot+0x18)<340:
    em.save(ROOT/f'build/checks/enemy-{kind:02x}.png');saved.add(kind)
  if frame%20==0:shots.append(em.frame.resize((640,448),0))
  if em.word(0xF10A):break
 assert set(seen)=={0x31,0x32,0x33},seen
 assert saved==set(seen),('Missing fresh costume screenshot',saved)
 assert len(set.union(*seen.values()))==4,seen
 assert len(seen[0x31])==1 and len(seen[0x33])==2,seen
 assert 0x14000 in speeds.get(0x32,set()),speeds
 assert 0xC000 in speeds.get(0x33,set()),speeds
 assert em.word(0xF10A),'Cannot finish using melee only'
 shots[0].save(ROOT/'build/checks/enemy-variety.gif',save_all=True,append_images=shots[1:],duration=333,loop=0)
 report=dict(ram_modified=False,types={hex(k):[hex(v) for v in sorted(values)] for k,values in seen.items()},walk_speeds={hex(k):[round(v/65536,2) for v in sorted(values)] for k,values in speeds.items()},victory=True,frames=frame+1,result='pass')
 (ROOT/'build/checks/enemy-variety-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
finally:em.close()
