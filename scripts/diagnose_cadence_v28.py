from emulate import Emulator,ROOT
from playtest import start_game,fight_keys
import json
em=Emulator(ROOT/'build/custom/golden-axe.bin')
try:
    start_game(em)
    for frame in range(5530):
        before=em.word(0xC17A);em.run(1,fight_keys(em,True))
        delta=(em.word(0xC17A)-before)&65535
        if 5509<=frame<=5513:
            print(json.dumps(dict(frame=frame,delta=delta,mode=hex(em.word(0xC172)),words={hex(a):em.word(a) for a in (0xC17A,0xC176,0xF150,0xF1FC,0xF294,0xF36C,0xD960,0xD964,0xD966,0xF2E4)},sat_flag=em.byte(0xC183))))
finally:em.close()
