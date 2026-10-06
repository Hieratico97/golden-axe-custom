from playtest import start_game
"""Verify pause freezes play, keeps graphics intact and resumes from controls."""
import json
from emulate import Emulator,ROOT
from playtest import begin_jutsu
em=Emulator(ROOT/'build/custom/golden-axe.bin')
try:
 start_game(em);em.run(30,[7]);em.run(1,[3]);em.run(3)
 assert em.byte(0xC175),'Start did not pause'
 fields=(0xD01C,0xD014,0xD042,0xD11C,0xD114,0xD142,0xF100,0xF160)
 before=[em.word(a) for a in fields];em.run(90,[7,0,1])
 assert before==[em.word(a) for a in fields],'Gameplay moved during pause'
 em.save(ROOT/'build/checks/pause.png')
 em.run(1,[3]);em.run(3);assert not em.byte(0xC175),'Start did not resume'
 em.save(ROOT/'build/checks/pause-resumed.png')
 # Move away from the first intact crate; rightward movement is correctly blocked.
 x=em.word(0xD01C);em.run(24,[6]);assert em.word(0xD01C)<x,'Movement did not resume'
 em.core.retro_reset();start_game(em);begin_jutsu(em,4);em.run(20)
 assert em.word(0xF160)>0
 em.run(1,[3]);em.run(3);assert em.byte(0xC175)
 fields=(0xF160,0xF162,0xF168,0xF180,0xD070,0xD770)
 before=[em.word(a) for a in fields];em.run(90,[7,0,1])
 assert before==[em.word(a) for a in fields],'Jutsu advanced during pause'
 em.save(ROOT/'build/checks/pause-jutsu.png')
 em.run(1,[3]);em.run(3);assert not em.byte(0xC175)
 assert em.word(0xF160)<before[0],'Jutsu did not resume'
 report=dict(paused=True,actors_frozen=True,jutsu_frozen=True,resumed=True,ram_modified=False,result='pass')
 (ROOT/'build/checks/pause-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
finally:em.close()
