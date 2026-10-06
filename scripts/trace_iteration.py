from emulate import Emulator,ROOT
from playtest import start_game
em=Emulator(ROOT/'build/custom/golden-axe.bin')
try:
 start_game(em);em.save(ROOT/'build/checks/iteration14-start.png')
 last=6;seen=set()
 for n in range(500):
  em.run(1,[7,0]);seen.add(em.word(0xD070))
  hp=em.byte(0xD164)
  if hp<last:
   print(dict(frame=n,hp=hp,attack=hex(em.word(0xD042)),pose=em.word(0xD070),enemy_state=hex(em.word(0xD142)),vy=hex(em.word(0xD134)),vx=hex(em.word(0xD12C))))
   em.save(ROOT/f'build/checks/iteration14-hit-{n}.png')
  last=hp
 print('poses',sorted(seen))
finally:em.close()
