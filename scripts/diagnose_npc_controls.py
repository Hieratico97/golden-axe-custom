from emulate import Emulator,ROOT
from playtest import start_game
em=Emulator(ROOT/'build/custom/golden-axe.bin')
try:
 start_game(em)
 em.save(ROOT/'build/checks/npc-control-debug.png')
 print('boot',[(hex(a),hex(em.word(a))) for a in (0xC170,0xC172,0xF200,0xF204,0xF300,0xF30E,0xD000,0xFE7E)])
 for frame in range(240):
  em.run(1,[7])
  if abs(em.word(0xD11C)-em.word(0xD01C))<88 and (em.byte(0xD042)&127)==0:break
 print('ready',frame,em.word(0xD01C),em.word(0xD11C))
 for keys in ([],[1],[],[],[],[],[1],[],[],[]):
  before=em.word(0xC17A);em.run(1,keys)
  print(keys,'ticks',before,em.word(0xC17A),'input',em.byte(0xC176),em.byte(0xF2B0),'gesture',em.word(0xF2BA),'cast',em.word(0xF160),'state',hex(em.word(0xD042)),'age',em.word(0xD960),'npcframe',em.word(0xD962),'bytes',em.word(0xD966),'all',em.word(0xF1FC))
finally:em.close()
