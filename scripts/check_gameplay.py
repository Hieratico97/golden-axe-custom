from playtest import start_game
"""Traverse the expanded solo stage, then restart through controller input."""
import json
from emulate import Emulator,ROOT
from playtest import fight_keys
em=Emulator(ROOT/'build/custom/golden-axe.bin')
try:
 start_game(em);em.save(ROOT/'build/checks/custom-first.png');max_scroll=0;types=set()
 for frame in range(12000):
  em.run(1,fight_keys(em,magic=True))
  max_scroll=max(max_scroll,em.word(0xC210))
  assert em.word(0xF100)==0 and em.word(0xF106)==0,'Old assist state active'
  for slot in (0xD100,0xD180):
   if em.byte(slot)&128:types.add(em.byte(slot)&127)
  if frame in (1000,2000,3000,4000):em.save(ROOT/f'build/checks/stage-{frame}.png')
  if em.word(0xF10A):break
 assert em.word(0xF10A) and max_scroll>=2016,(frame,max_scroll)
 assert {0x31,0x32,0x33}<=types,types
 em.run(10);em.save(ROOT/'build/checks/custom-victory.png')
 casts=em.word(0xF184);broken=em.word(0xF1E6);collected=em.word(0xF1E8)
 assert casts>0 and broken>0 and collected>0,(casts,broken,collected)
 em.run(1,[3]);start_game(em)
 assert em.word(0xC210)==0 and not em.word(0xF10A) and em.word(0xF180)==120
 report=dict(result='pass',ram_modified=False,supports=False,victory=True,restart=True,frames=frame+1,max_scroll=max_scroll,jutsu_casts=casts,objects_broken=broken,scrolls_collected=collected)
 (ROOT/'build/checks/gameplay-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
finally:em.close()
