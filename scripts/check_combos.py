from playtest import start_game
"""Check native melee chains and hit pause using controller input only."""
import json
from emulate import Emulator,ROOT
em=Emulator(ROOT/'build/custom/golden-axe.bin',capture_audio=True)
report={'ram_modified':False};shots=[];health=[];pauses=[];last_hp=6;player_poses=set();hurt_poses=set();fall_poses=set();finished=None
try:
 start_game(em);em.audio.clear()
 for frame in range(900):
  before=(em.byte(0xD014),em.word(0xD01C),em.byte(0xD114),em.word(0xD11C))
  stop=em.word(0xF150)
  em.run(1,[7,0])
  after=(em.byte(0xD014),em.word(0xD01C),em.byte(0xD114),em.word(0xD11C))
  if stop:
   assert before==after,('Actors moved during hit pause',frame,before,after)
   pauses.append(stop)
  hp=em.byte(0xD164)
  if hp<last_hp:
   health.append({'frame':frame,'before':last_hp,'after':hp,'attack':em.byte(0xD043)})
  last_hp=hp
  player_poses.add(em.word(0xD070))
  if 0<hp<6:hurt_poses.add(em.word(0xD170))
  if hp==0:fall_poses.add(em.word(0xD170))
  if frame%2==0:shots.append(em.frame.resize((640,448),0))
  if em.word(0xF158)>0 and finished is None:finished=frame
  if finished is not None and frame-finished>=100:break
 assert em.word(0xF156)>=3,('Chain too short',health)
 assert em.word(0xF15A)>=3
 assert 3 in pauses and 6 in pauses,pauses
 assert len(health)>=3 and health[2]['after']==0,health
 assert {8,9,11,12,15,53,54}<=player_poses,('Punch, slash and directional finisher missing',player_poses)
 assert {9,10,15}<=hurt_poses,hurt_poses
 assert {12,13,14}<=fall_poses,fall_poses
 em.save(ROOT/'build/checks/combo-finisher.png')
 em.save_audio(ROOT/'build/checks/combo-impact.wav')
 shots[0].save(ROOT/'build/checks/combo-preview.gif',save_all=True,append_images=shots[1:],duration=33,loop=0)
 report.update(health_changes=health,confirmed_hits=em.word(0xF156),max_chain=em.word(0xF15A),finishers=em.word(0xF158),hit_pause_frames=sorted(set(pauses)),player_poses=sorted(player_poses),hurt_poses=sorted(hurt_poses),fall_poses=sorted(fall_poses),result='pass')
 print(json.dumps(report))
finally:em.close()
(ROOT/'build/checks/combo-check.json').write_text(json.dumps(report,indent=2)+'\n')
