from playtest import start_game
"""Check all Kakashi techniques: real contacts, poses, FX phases and cost."""
import json,sys
from emulate import Emulator,ROOT
from playtest import JUTSUS,begin_jutsu
kind=sys.argv[1];index=JUTSUS.index(kind)
em=Emulator(ROOT/'build/custom/golden-axe.bin',capture_audio=True)
try:
 start_game(em);em.audio.clear();begin_jutsu(em,index)
 assert em.word(0xF180)<120,'Chakra not consumed'
 poses=set();fx=set();shots=[];cast_x=em.word(0xD01C)
 for frame in range(76):
  em.run(1);poses.add(em.word(0xD070))
  if em.byte(0xD700):fx.add(em.word(0xD770))
  shots.append(em.frame.resize((640,448),0))
  if frame in (6,16,28,42,60):em.save(ROOT/f'build/checks/{kind}-{frame}.png')
 assert em.word(0xF190+index*2)>0,(kind,'no confirmed contact')
 assert {16,17}<=poses and len(poses)>=(3 if index==1 else 4),(kind,poses)
 if index==0:assert len(poses&{37,39,41,43})>=3,'Raikiri lacks running animation'
 assert len(fx)>=3,(kind,fx)
 assert em.word(0xF100)==0 and em.word(0xF106)==0,'Assist spawned'
 shots[0].save(ROOT/f'build/checks/{kind}.gif',save_all=True,append_images=shots[1:],duration=17,loop=0)
 em.save_audio(ROOT/f'build/checks/{kind}.wav')
 report=dict(result='pass',jutsu=kind,ram_modified=False,contacts=em.word(0xF190+index*2),body_poses=sorted(poses),effect_poses=sorted(fx),remaining_chakra=em.word(0xF180),supports=False)
 (ROOT/f'build/checks/{kind}-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
finally:em.close()
