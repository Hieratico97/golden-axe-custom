from playtest import start_game
import json
from emulate import Emulator,ROOT
em=Emulator(ROOT/'build/custom/golden-axe.bin');start_game(em)
for i in range(600):
 em.run(1,[7,0])
 if em.word(0xF156)==1:break
for i in range(60):
 em.run(1,[7])
 if em.byte(0xD014)>=2 and em.word(0xF150)==0:break
em.run(1,[7,0]);buffered=em.word(0xF15C);print('buffer',buffered);assert buffered>0
em.run(40,[7]);print('hits after release',em.word(0xF156));assert em.word(0xF156)>=2
report=dict(result='pass',ram_modified=False,buffer_frames=buffered,contacts_after_release=em.word(0xF156))
(ROOT/'build/checks/combo-buffer-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
em.close()
