from emulate import Emulator,ROOT
from playtest import start_game,fight_keys,dismiss_story
em=Emulator(ROOT/'build/custom/golden-axe.bin')
try:
 start_game(em)
 for f in range(15000):
  em.run(1,fight_keys(em,True))
  if em.word(0xF220):break
 dismiss_story(em)
 for f in range(500):
  em.run(1)
  if em.byte(0xD180) and (f%60==0 or f<160 and f%5==0):
   print(f, {hex(s):{hex(o):hex(em.word(s+o)) for o in (0,0x18,0x1C,0x20,0x24,0x28,0x2C,0x34,0x42,0x46,0x4C,0x60,0x64)} for s in (0xD000,0xD100,0xD180)})
   if f%60==0:em.save(ROOT/f'build/checks/clone-inspect-{f}.png')
finally:em.close()
