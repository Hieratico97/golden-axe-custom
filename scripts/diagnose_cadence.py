from emulate import Emulator,ROOT
from playtest import start_game,fight_keys
for tag,path in [('v20',ROOT/'build/v0.20-backup/golden-axe.bin'),('v21',ROOT/'build/custom/golden-axe.bin')]:
 em=Emulator(path)
 try:
  start_game(em);miss=[]
  for frame in range(2000):
   before=em.word(0xC17A);paint=em.word(0xD964);effect=em.word(0xF160)
   em.run(1,fight_keys(em,True))
   delta=(em.word(0xC17A)-before)&65535
   if delta!=1:miss.append((frame,delta,effect,em.word(0xF160),em.word(0xD964)-paint,em.word(0xF1FC),em.word(0xF2E4),em.word(0xF246),em.word(0xF244)))
  print(tag,'miss',len(miss),miss[:25])
 finally:em.close()
