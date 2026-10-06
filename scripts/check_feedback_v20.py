"""Compare quiet music and observe complete technique sounds through real input."""
import hashlib,json,ctypes as C
import numpy as np
from emulate import Emulator,ROOT
from playtest import start_game,fight_keys,begin_jutsu,JUTSUS


def z80_program(em):
    em.core.retro_serialize_size.restype=C.c_size_t
    em.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t]
    size=em.core.retro_serialize_size();buffer=C.create_string_buffer(size)
    assert em.core.retro_serialize(buffer,size)
    original=(ROOT/'build/baseline/golden-axe.bin').read_bytes()[0x1D2F8:0x1D330]
    offset=buffer.raw.find(original)
    assert offset>=8 and buffer.raw.find(original,offset+1)==-1
    program=buffer.raw[offset-8:offset-5]
    assert program==bytes.fromhex('f318fd'),('Inherited Z80 driver still active',program.hex())
    return program.hex()


def metrics(em):
    pcm=np.frombuffer(b''.join(em.audio),dtype='<i2').astype(float).reshape(-1,2)
    mono=pcm.mean(1);power=abs(np.fft.rfft(mono*np.hanning(len(mono))))**2
    hz=np.fft.rfftfreq(len(mono),1/44100)
    return dict(rms=round(float(np.sqrt(np.mean(pcm**2))),2),peak=int(abs(pcm).max()),
        above_2500_hz_ratio=round(float(power[hz>=2500].sum()/power.sum()),6),
        centroid_hz=round(float((power*hz).sum()/power.sum()),1))


def quiet(path,label):
    em=Emulator(path,capture_audio=True)
    try:
        start_game(em)
        for frame in range(1200):
            em.run(1,fight_keys(em))
            if not any(em.byte(s)&128 and em.byte(s+0x64)>0 for s in (0xD100,0xD180,0xD200)):break
        em.run(150);assert em.word(0xC26C)==0
        assert em.word(0xF300)==1
        if label=='v20':z80_program(em)
        before=em.word(0xF3D4);em.audio.clear();em.run(1200)
        assert before==em.word(0xF3D4),'Combat contaminated quiet comparison'
        em.save_audio(ROOT/f'build/checks/konoha-{label}.wav')
        return metrics(em)
    finally:em.close()


old=quiet(ROOT/'build/v0.19-backup/golden-axe.bin','before-v20')
new=quiet(ROOT/'build/custom/golden-axe.bin','v20')
assert new['rms']<old['rms']*.85,(old,new)
assert new['above_2500_hz_ratio']<old['above_2500_hz_ratio'],(old,new)
assert new['centroid_hz']<old['centroid_hz'],(old,new)
assert new['peak']<32767
effects=[]
for index,name in enumerate(JUTSUS):
    em=Emulator(ROOT/'build/custom/golden-axe.bin',capture_audio=True)
    try:
        start_game(em);em.audio.clear();begin_jutsu(em,index)
        envelope=[];sound_runs=[];last=None;phases=[]
        for frame in range(200):
            em.run(1)
            envelope.append(em.word(0xF320))
            current=em.word(0xF246) if em.word(0xF244) else None
            if current!=last:sound_runs.append(dict(frame=frame,sound=current));last=current
            if em.byte(0xD700):phases.append(em.word(0xD770))
        assert max(envelope)==12 and envelope[-1]==0,(name,envelope)
        assert 16+index in [r['sound'] for r in sound_runs],(name,sound_runs)
        # A repeated multi-target contact must leave time for the sound tail.
        assert any(b==a-1 for a,b in zip(envelope,envelope[1:])),name
        em.save_audio(ROOT/f'build/checks/{name}-v20.wav')
        audio=metrics(em);assert audio['rms']>100 and audio['peak']<32767,(name,audio)
        assert len(set(phases))>=3,(name,phases)
        z80_program(em)
        effects.append(dict(jutsu=name,duck_peak=max(envelope),duck_released=True,sounds=sound_runs,
            animation_phases=sorted(set(phases)),audio=audio))
    finally:em.close()

em=Emulator(ROOT/'build/custom/golden-axe.bin')
try:
    start_game(em);phases={};hero=set();stopped=[]
    for frame in range(2000):
        hold=em.word(0xF150)
        before=[em.word(s+0x1C) for s in (0xD000,0xD100,0xD180,0xD200)]
        em.run(1,fight_keys(em))
        if hold:
            assert before==[em.word(s+0x1C) for s in (0xD000,0xD100,0xD180,0xD200)]
            stopped.append(hold)
        if em.word(0xF382):hero.add(em.word(0xD070))
        for slot,state in ((0xD100,0xF390),(0xD180,0xF3A0),(0xD200,0xF3B0)):
            timer=em.word(state+2);kind=em.word(state+6)
            if timer and em.byte(slot+0x43) in range(13,24):
                phases.setdefault(kind,set()).add(em.word(slot+0x70))
    assert {16,9,10,15}<=phases.get(1,set()),phases
    assert 17 in phases.get(2,set()) and 10 in phases.get(2,set()),phases
    assert stopped
    reactions={str(k):sorted(v) for k,v in phases.items()}
finally:em.close()

report=dict(result='pass',version='0.20',ram_modified=False,village_before=old,village_after=new,
    inherited_driver_disabled='DI / JR -3',z80_program_hex='f318fd',
    rms_reduction_percent=round(100*(1-new['rms']/old['rms']),1),jutsus=effects,
    grounded_reaction_sequences=reactions,hero_damage_poses=sorted(hero),hitstop_samples=len(stopped),
    rom_sha256=hashlib.sha256((ROOT/'build/custom/golden-axe.bin').read_bytes()).hexdigest())
(ROOT/'build/checks/feedback-v20-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
