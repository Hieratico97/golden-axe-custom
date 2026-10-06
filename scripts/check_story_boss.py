"""Play the whole story, wait for Itachi's attacks, then win without RAM writes."""
import ctypes as C
import json
from pathlib import Path
import numpy as np
from emulate import Emulator,ROOT
from playtest import fight_keys,dismiss_story


def vram(em):
    em.core.retro_serialize_size.restype=C.c_size_t
    size=em.core.retro_serialize_size();buffer=C.create_string_buffer(size)
    em.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t]
    assert em.core.retro_serialize(buffer,size)
    raw=(ROOT/'assets/custom/city-tiles.bin').read_bytes()
    swapped=lambda b:bytes(v for pair in zip(b[1::2],b[::2]) for v in pair)
    offset=buffer.raw.find(swapped(raw[32:288]))-32
    assert offset>=0
    return swapped(buffer.raw[offset:offset+65536])


em=Emulator(ROOT/'build/custom/golden-axe.bin',capture_audio=True)
pages=[];faces=set();health=[];boss_poses=set();projectiles=set();hurt_poses=set();smoke=set();music_scenes=set()
try:
    em.run(330)
    for _ in range(240):
        if em.word(0xF204) and em.word(0xF20C)!=65535 and not em.word(0xF206):break
        em.run(1)
    assert em.word(0xF204) and not em.word(0xF200),'Intro did not initialize'
    music_scenes.add(em.word(0xF300))
    for page in range(3):
        assert em.word(0xF204) and em.word(0xF202)==page
        face=em.word(0xF20C);faces.add(face);pages.append(page)
        assert vram(em)[0x6000:0x6800]==(ROOT/'assets/custom/portrait-tiles.bin').read_bytes()[face*2048:(face+1)*2048]
        assert em.byte(0xD880)==0x7F,'Portrait not displayed'
        frozen=[em.word(a) for a in (0xD01C,0xD018,0xD020,0xD11C,0xC210)]
        em.run(30,[7,8]);assert frozen==[em.word(a) for a in (0xD01C,0xD018,0xD020,0xD11C,0xC210)]
        em.save(ROOT/f'build/checks/story-intro-{page}.png')
        em.run(1,[0]);em.run(2)
    assert em.word(0xF200)==1 and not em.word(0xF204)
    for frame in range(15000):
        em.run(1,fight_keys(em,True))
        music_scenes.add(em.word(0xF300))
        if em.word(0xF220):break
    assert em.word(0xF220),'Itachi did not spawn'
    assert em.byte(0xD164)==60 and em.word(0xF280)==60
    for page in (3,4):
        em.run(30)
        assert em.word(0xF202)==page
        face=em.word(0xF20C);faces.add(face);pages.append(page)
        em.save(ROOT/f'build/checks/story-boss-{page}.png')
        em.run(1,[0]);em.run(2)
    assert em.word(0xF200)==2
    initial=em.byte(0xD164);last_hp=initial;min_life=48;counter=0;clone_hp=set();clone_attacks=set()
    # Let the boss complete all techniques. Controller motion follows a projectile's lane.
    for frame in range(1500):
        keys=[]
        if em.word(0xF22A):
            dy=em.word(0xF22E)-em.word(0xD020)
            if abs(dy)>3:keys=[5 if dy>0 else 4]
        elif frame%240<60:keys=[6]
        elif frame%240<120:keys=[7]
        em.run(1,keys)
        music_scenes.add(em.word(0xF300))
        min_life=min(min_life,em.byte(0xFE7E));hurt_poses.add(em.word(0xD070));boss_poses.add(em.word(0xD170))
        if em.byte(0xD180)&128 and em.word(0xF2D0):
            hp=em.byte(0xD1E4);clone_hp.add(hp);clone_attacks.add(em.byte(0xD1C3))
            assert hp<=8,('Clone health not independent',hp)
            assert em.word(0xD1F4)==em.word(0xD174) and em.word(0xD1F6)==em.word(0xD176),'Clone is not Itachi'
        if em.byte(0xD980):smoke.add(em.word(0xD988))
        if em.word(0xF22A):
            typ=em.word(0xF232);projectiles.add(typ)
            if typ!=counter:
                em.save(ROOT/f'build/checks/itachi-technique-{typ}.png');counter=typ
        if min(em.word(a) for a in (0xF236,0xF238,0xF23A))>0 and em.word(0xF23C)>0:break
    techniques=[em.word(a) for a in (0xF236,0xF238,0xF23A)]
    # Stop moving after the projectile showcase: let the pursuing clone reach us.
    for frame in range(360):
        em.run(1)
        if em.byte(0xD180)&128 and em.word(0xF2D0):
            clone_hp.add(em.byte(0xD1E4));clone_attacks.add(em.byte(0xD1C3))
        if any(3<=pose<=8 for pose in clone_attacks):break
    assert all(techniques),('Missing boss technique',techniques)
    assert projectiles=={1,2},projectiles
    assert em.word(0xF23C)>0,'Projectiles never contacted Kakashi'
    assert min_life<48,('No actual damage from boss',min_life)
    assert {5,6,7,8,15}<=boss_poses,('Missing casting animation',boss_poses)
    assert smoke=={0x3E0,0x3F0},('Missing clone smoke phases',smoke)
    assert em.byte(0xD164)==initial,'Boss loses health without a player attack'
    assert 8 in clone_hp,('Clone does not spawn with eight HP',clone_hp)
    assert any(3<=pose<=8 for pose in clone_attacks),('Clone never attacked',clone_attacks)
    em.audio.clear();dead_frame=None;removed_frame=None;death_poses=set();observed_outro=set();clone_dies_first=False;clone_death=set()
    for frame in range(18000):
        if em.word(0xF204):
            page=em.word(0xF202)
            if page not in observed_outro and em.word(0xF20C)!=65535:
                observed_outro.add(page);pages.append(page);faces.add(em.word(0xF20C))
                face=em.word(0xF20C)
                assert vram(em)[0x6000:0x6800]==(ROOT/'assets/custom/portrait-tiles.bin').read_bytes()[face*2048:(face+1)*2048]
                em.save(ROOT/f'build/checks/story-outro-{page}.png')
        em.run(1,fight_keys(em,True))
        hp=em.byte(0xD164)
        music_scenes.add(em.word(0xF300))
        if em.byte(0xD180)&128 and not em.byte(0xD1E4) and hp>0:
            clone_dies_first=True;clone_death.add(em.word(0xD1F0))
        if not em.byte(0xD100) and em.byte(0xD180)&128 and em.byte(0xD1E4)>0:
            assert not em.word(0xF204),'Outro starts while a clone is alive'
        if em.byte(0xD100) and hp<last_hp:
            health.append(dict(frame=frame,before=last_hp,after=hp));last_hp=hp
        if em.byte(0xD100) and hp==0:
            if dead_frame is None:dead_frame=frame
            death_poses.add(em.word(0xD170))
        if dead_frame is not None and not em.byte(0xD100) and removed_frame is None:removed_frame=frame
        if em.word(0xF10A):break
    assert em.word(0xF10A),'Story cannot finish'
    assert clone_dies_first,'Clone did not die independently of Itachi'
    em.run(2);music_scenes.add(em.word(0xF300))
    assert music_scenes=={0,1,2,3,4},music_scenes
    assert len(health)>=8 and health[-1]['after']==0,health
    assert removed_frame-dead_frame>=40,(dead_frame,removed_frame)
    assert {13,14}<=death_poses and death_poses&{12,19},death_poses
    assert set(pages)==set(range(8)),pages
    assert faces==set(range(4)),faces
    # Outro first-frame face DMA may be deferred, but the complete story exercised all four portraits.
    em.save_audio(ROOT/'build/checks/itachi-fight.wav');em.save(ROOT/'build/checks/story-victory.png')
    audio=np.frombuffer(b''.join(em.audio),dtype='<i2')
    assert len(audio)>44100 and abs(audio.astype(np.int32)).max()>500
    report=dict(result='pass',ram_modified=False,pages=pages,faces=sorted(faces),boss_hp=initial,
                techniques=techniques,projectiles=sorted(projectiles),projectile_contacts=em.word(0xF23C),
                boss_casting_poses=sorted(boss_poses),player_damage_poses=sorted(hurt_poses),
                health_changes=health,death_poses=sorted(death_poses),death_duration=removed_frame-dead_frame,
                sounds_played=em.word(0xF248),music_scenes=sorted(music_scenes),music_steps=em.word(0xF310),victory=True)
    report['clone_smoke_tiles']=[hex(tile) for tile in sorted(smoke)]
    report.update(clone_initial_hp=8,clone_hp_observed=sorted(clone_hp),clone_is_itachi=True,clone_animation_states=sorted(clone_attacks),clone_dies_while_boss_alive=clone_dies_first,clone_death_poses=sorted(clone_death))
    (ROOT/'build/checks/story-boss-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
finally:em.close()
