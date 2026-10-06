from playtest import start_game
"""Solo controls, stage dimensions, depth and update rhythm."""
import json
from emulate import Emulator,ROOT
from playtest import select_jutsu
em=Emulator(ROOT/'build/custom/golden-axe.bin')
try:
 start_game(em);assert em.word(0xC228)==2240
 y=em.word(0xD020);select_jutsu(em,6);assert em.word(0xD020)==y
 em.run(1,[5,1]);em.run(1);assert em.word(0xF182)==5
 em.run(1,[4,1]);em.run(1);assert em.word(0xF182)==6
 x=em.word(0xD01C);em.run(24,[7]);distance=em.word(0xD01C)-x
 assert distance>=35,distance
 em.run(24,[6]);em.run(1,[8]);em.run(8);assert em.word(0xD070)==5
 em.run(80);before=em.word(0xC17A);em.run(600)
 assert (em.word(0xC17A)-before)&65535==600
 em.core.retro_reset();start_game(em);em.run(120,[4]);top=em.word(0xD020)
 em.run(120,[5]);bottom=em.word(0xD020)
 assert bottom-top>=80,(top,bottom)
 assert em.word(0xF100)==0
 report=dict(result='pass',ram_modified=False,stage_width=2560,camera_limit=2240,walk_distance=distance,walk_limits=[top,bottom],selection_without_movement=True,jump=True,updates=600,supports=False)
 (ROOT/'build/checks/polish-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
finally:em.close()
