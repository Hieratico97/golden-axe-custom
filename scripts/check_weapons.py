from playtest import start_game
import json
from emulate import Emulator,ROOT
em=Emulator(ROOT/'build/custom/golden-axe.bin',capture_audio=True)
try:
 start_game(em)
 em.audio.clear()
 for cycle in range(20):
  em.run(1,[5,0])
  for frame in range(25):
   em.run(1)
   if em.word(0xF134):
    em.save(ROOT/'build/checks/kunai-spark.png')
    break
  if em.word(0xF134):break
 assert em.word(0xF134)>0,'Kunai did not hit'
 em.save_audio(ROOT/'build/checks/kunai-impact.wav')
 em.save(ROOT/'build/checks/kunai-hit.png')
 report=dict(kunai_hits=em.word(0xF134),impact_sounds=em.word(0xF136),cycles=cycle+1,ram_modified=False)
 assert em.word(0xF136)>0
 before=em.word(0xC17A);em.run(600)
 assert (em.word(0xC17A)-before)&65535==600
 report['result']='pass'
 print(json.dumps(report))
 (ROOT/'build/checks/weapons-check.json').write_text(json.dumps(report,indent=2))
finally:em.close()
