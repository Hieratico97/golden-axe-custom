"""Confirm visible reactions and audible FM scenes from real controller play."""
import hashlib,json
import numpy as np
from emulate import Emulator,ROOT
from playtest import dismiss_story,start_game,fight_keys


def pcm(em):return np.frombuffer(b''.join(em.audio),dtype='<i2').astype(float)
def rms(samples):return float(np.sqrt(np.mean(samples**2)))


em=Emulator(ROOT/'build/custom/golden-axe.bin',capture_audio=True)
report=dict(ram_modified=False,version='0.17')
try:
    em.run(330)
    for _ in range(240):
        if em.word(0xF204) and not em.word(0xF200):break
        em.run(1)
    assert em.word(0xF204) and em.word(0xF300)==0,'Intro music did not initialize'
    em.audio.clear();em.run(300)
    intro=pcm(em);assert rms(intro)>150
    em.save_audio(ROOT/'build/checks/music-tsukuyomi-v12.wav')
    dismiss_story(em);em.run(24);assert em.word(0xF300)==1
    em.audio.clear();start=em.word(0xF310);em.run(600,[4]);stage=pcm(em)
    assert em.word(0xF310)-start>=59,'Music score did not advance at the 10-frame tempo'
    assert em.word(0xF316)>=1,'Village ambient voice never played'
    assert rms(stage)>150 and rms(stage)<6000
    assert np.max(abs(stage))<32767,'Sound clipped'
    em.save_audio(ROOT/'build/checks/music-konoha-v12.wav')
    birds=em.word(0xF316)
    em.run(1,[3]);em.run(3);assert em.byte(0xC175)
    counter=em.word(0xF30E);em.audio.clear();em.run(150)
    assert em.word(0xF30E)==counter,'Music advanced during pause'
    paused=pcm(em);pause_rms=rms(paused[-44100:])
    assert pause_rms<rms(stage)*.25,('Music did not silence in pause',pause_rms,rms(stage))
    em.run(1,[3]);em.run(60);assert em.word(0xF30E)>counter
    report.update(intro_rms=round(rms(intro),1),konoha_rms=round(rms(stage),1),peak=int(np.max(abs(stage))),village_chirps=birds,pause_tail_rms=round(pause_rms,1),pause_resumed=True)
    # Natural enemy strikes and a native melee chain, without touching RAM.
    em.core.retro_reset();start_game(em);em.audio.clear()
    player_hurt=set();enemy_hurt=set();air=set();floor=set();dust=set();frames=[];flashes=[];scatter=set()
    for frame in range(650):
        em.run(1,[7,0])
        player_state=em.byte(0xD042)&127
        if player_state==0x48:player_hurt.add(em.word(0xD070))
        if em.byte(0xD043)==0x1A:air.add(em.word(0xD070))
        if player_state==0x58:floor.add(em.word(0xD070))
        if 0<em.byte(0xD164)<6:enemy_hurt.add(em.word(0xD170))
        if em.byte(0xD780):dust.add(em.word(0xD788))
        if em.byte(0xD800):scatter.add(em.word(0xD808))
        if em.word(0xF382)>=13 or em.word(0xF392)>=13:
            flashes.append(frame)
            # Native palette staging buffers must agree, including bank offsets.
            for address in range(0xC000,0xC060,2):assert em.word(address)==em.word(address+0x80),('Flash target diverged',hex(address))
        if 68<=frame<=185 or 195<=frame<=335:frames.append(em.frame.resize((960,672),0))
        if frame in (76,92,115,153,203,211,221,260):em.save(ROOT/f'build/checks/damage-v12-{frame}.png')
    assert {9,10,15}<=enemy_hurt,enemy_hurt
    assert {23,24,25}<=air,air
    assert {26,27}<=floor and floor&{28,63},floor
    assert dust=={0x2C1,0x2C3,0x2C5},dust
    assert scatter=={0x2C7},scatter
    assert em.word(0xF3D0)>=4 and em.word(0xF3D4)>0
    assert em.word(0xF3D2)>=2 and len(flashes)>=8
    assert em.word(0xF15A)>=3 and em.word(0xF158)>=1
    frames[0].save(ROOT/'build/checks/damage-v12.gif',save_all=True,append_images=frames[1:],duration=17,loop=0)
    em.save_audio(ROOT/'build/checks/damage-v12.wav')
    reactions=em.word(0xF3D0);player_reactions=em.word(0xF3D4);landings=em.word(0xF3D2);combo=em.word(0xF15A)
    # Walk into actual melee range, then let a ninja hit the standing hero.
    # This catches a locomotion renderer accidentally erasing his hurtbox.
    em.core.retro_reset();start_game(em)
    em.run(45,[4]);em.run(12,[7]);right_hurt=em.byte(0xD004)
    em.run(12,[6]);left_hurt=em.byte(0xD004)
    em.run(20);idle_hurt=em.byte(0xD004)
    assert [right_hurt,left_hurt,idle_hurt]==[53,11,15],('Native locomotion hurtboxes lost',right_hurt,left_hurt,idle_hurt)
    em.core.retro_reset();start_game(em);standing_damage=False;previous=48
    for frame in range(700):
        keys=[k for k in fight_keys(em) if k!=0]
        em.run(1,keys)
        if em.byte(0xFE7E)<previous and not keys:standing_damage=True
        previous=em.byte(0xFE7E)
        if (em.byte(0xD042)&127)==0x48:player_hurt.add(em.word(0xD070))
    assert standing_damage,'Standing hero could not receive enemy damage'
    assert 23 in player_hurt and player_hurt&{61,62},('Head/body player reaction missing',player_hurt)
    report.update(enemy_recoil=sorted(enemy_hurt),player_air=sorted(air),player_floor_recovery=sorted(floor),player_stagger=sorted(player_hurt),standing_and_walking_hurtboxes=True,native_hurtboxes=[right_hurt,left_hurt,idle_hurt],dust_tiles=[hex(n) for n in sorted(dust)],impact_scatter_tiles=[hex(n) for n in sorted(scatter)],confirmed_reactions=reactions,player_reactions=player_reactions,landings=landings,flash_frames=len(flashes),max_combo=combo,result='pass',rom_sha256=hashlib.sha256((ROOT/'build/custom/golden-axe.bin').read_bytes()).hexdigest())
    (ROOT/'build/checks/damage-audio-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
finally:em.close()
