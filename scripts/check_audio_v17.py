"""Compare real cartridge audio and observe each cast/contact sound route."""
import hashlib,json
import numpy as np
from emulate import Emulator,ROOT
from playtest import start_game,begin_jutsu,fight_keys,dismiss_story,JUTSUS


def metrics(em):
    stereo=np.frombuffer(b''.join(em.audio),dtype='<i2').astype(float).reshape(-1,2)
    mono=stereo.mean(1)
    power=abs(np.fft.rfft(mono*np.hanning(len(mono))))**2
    hz=np.fft.rfftfreq(len(mono),1/44100)
    return dict(rms=round(float(np.sqrt(np.mean(stereo**2))),2),peak=int(abs(stereo).max()),
        above_2500_hz_ratio=round(float(power[hz>=2500].sum()/power.sum()),5),
        centroid_hz=round(float((power*hz).sum()/power.sum()),1))


def village_audio(path,tag):
    em=Emulator(path,capture_audio=True)
    try:
        start_game(em)
        # Defeat the first wave and stand still before the next scroll trigger.
        # Enemy hits/footsteps otherwise dominate a comparison of the music.
        for frame in range(1200):
            em.run(1,fight_keys(em))
            alive=[s for s in (0xD100,0xD180,0xD200) if em.byte(s)&128 and em.byte(s+0x64)>0]
            if not alive:break
        em.run(120);assert em.word(0xC26C)==0,'No quiet gap after first wave'
        reactions=em.word(0xF3D4);em.audio.clear();em.run(720)
        assert em.word(0xF3D4)==reactions,'Enemy effects contaminated music comparison'
        assert em.word(0xF300)==1
        em.save_audio(ROOT/f'build/checks/konoha-{tag}.wav')
        return metrics(em)
    finally:em.close()


old=village_audio(ROOT/'build/v0.16-preview-backup/golden-axe.bin','before-v17')
new=village_audio(ROOT/'build/custom/golden-axe.bin','v17')
assert new['rms']<old['rms']*.9,('Village did not become quieter',old,new)
assert new['above_2500_hz_ratio']<old['above_2500_hz_ratio'],('Harsh upper spectrum not reduced',old,new)
assert new['peak']<32767
effects=[]
for index,name in enumerate(JUTSUS):
    em=Emulator(ROOT/'build/custom/golden-axe.bin',capture_audio=True)
    try:
        start_game(em);em.audio.clear();begin_jutsu(em,index)
        first=em.word(0xF246);sounds={first};expected=(2,3,23,4,5,6,7)[index]
        assert first==expected,(name,'Wrong launch sound',first)
        for frame in range(150):
            em.run(1)
            if em.word(0xF244):sounds.add(em.word(0xF246))
        assert 16+index in sounds,(name,'Contact sound not heard',sounds)
        em.save_audio(ROOT/f'build/checks/{name}-v17.wav')
        audio=metrics(em);assert audio['rms']>100 and audio['peak']<32767,(name,audio)
        effects.append(dict(jutsu=name,cast_sound=first,contact_sound=16+index,sounds=sorted(sounds),audio=audio))
    finally:em.close()
em=Emulator(ROOT/'build/custom/golden-axe.bin',capture_audio=True)
try:
    start_game(em)
    for frame in range(12000):
        em.run(1,fight_keys(em,True))
        if em.word(0xF220):break
    assert em.word(0xF220);dismiss_story(em);em.run(30)
    assert em.word(0xF300)==2
    boss_tempo=em.word(0xF306);em.audio.clear();em.run(720,[4])
    em.save_audio(ROOT/'build/checks/itachi-battle-v17.wav');boss=metrics(em)
    for frame in range(12000):
        em.run(1,fight_keys(em,True))
        if em.word(0xF300)==4:break
    assert em.word(0xF300)==4,'No Mangekyo musical transition'
    phase_tempo=em.word(0xF306);em.audio.clear();em.run(600,[4])
    em.save_audio(ROOT/'build/checks/mangekyo-battle-v17.wav');phase=metrics(em)
    assert phase_tempo<boss_tempo and boss_tempo<10,(boss_tempo,phase_tempo)
    assert boss['rms']>new['rms'] and phase['rms']>new['rms'],(new,boss,phase)
    assert max(boss['peak'],phase['peak'])<32767
finally:em.close()
report=dict(result='pass',version='0.17',ram_modified=False,village_before=old,village_after=new,
    village_rms_reduction_percent=round(100*(1-new['rms']/old['rms']),1),jutsu_sounds=effects,
    itachi=boss,mangekyo=phase,battle_step_frames=[boss_tempo,phase_tempo],
    rom_sha256=hashlib.sha256((ROOT/'build/custom/golden-axe.bin').read_bytes()).hexdigest())
(ROOT/'build/checks/audio-v17-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
