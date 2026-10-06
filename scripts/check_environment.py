"""Exercise training wood, real rendered lighting, pause and restoration."""
import hashlib,json,struct
import numpy as np
from PIL import Image
from emulate import Emulator,ROOT
from playtest import start_game,fight_keys,dismiss_story

rom=ROOT/'build/custom/golden-axe.bin'
normal=np.array(struct.unpack('>64H',(ROOT/'assets/custom/city-atmosphere-palettes.bin').read_bytes())).reshape(4,16)
bright=np.array(struct.unpack('>64H',(ROOT/'assets/custom/city-atmosphere-hit-palettes.bin').read_bytes())).reshape(4,16)

def palette(em):return np.array([em.word(0xC060+i*2) for i in range(16)])

def sky(em):
    scene=np.array(Image.open(ROOT/'assets/custom/konoha.png'))
    camera=em.word(0xC210)
    crop=scene[16:40,camera+24:camera+288]
    yy,xx=np.where(crop==2);assert len(xx),'No unoccluded sky sample'
    # Whole flat sky patches tolerate the native horizontal camera shake.
    for y,x in zip(yy,xx):
        if x<4 or x>=crop.shape[1]-4:continue
        if np.all(crop[y,max(0,x-4):x+5]==2):
            return em.frame.getpixel((int(x+24),int(y+16)))
    raise AssertionError('No stable sky patch')

em=Emulator(rom)
try:
    start_game(em)
    for frame in range(12000):
        em.run(1,fight_keys(em,True))
        if em.word(0xD01C)+em.word(0xC210)-128>=430:break
    assert em.word(0xF1A4)==0,'Target broken before melee test'
    for frame in range(320):
        world=em.word(0xD01C)+em.word(0xC210)-128
        y=em.word(0xD020)
        if abs(y-128)>3:keys=[4 if y>128 else 5]
        elif world<466:keys=[7]
        elif em.byte(0xD044)&1:keys=[7]
        else:keys=[0]
        em.run(1,keys)
        if em.word(0xF1A4):break
    assert em.word(0xF1A4)==1,('Training target did not break from melee',world,y)
    assert em.word(0xF1E0)>0,'No debris on target break'
    em.save(ROOT/'build/checks/training-target-broken-v19.png')
    target=dict(broken=True,scroll_available=True,debris=True,frame=frame)
    em.core.retro_reset();start_game(em)
    for frame in range(12000):
        em.run(1,fight_keys(em,True))
        if em.word(0xF220):break
    assert em.word(0xF220)
    dismiss_story(em);em.run(2)
    daylight=sky(em);assert daylight[2]>daylight[0],daylight
    em.save(ROOT/'build/checks/mangekyo-day-v19.png')
    stages=set();entry=False;night=None;render_colours=set()
    for frame in range(6000):
        em.run(1,fight_keys(em,True))
        if em.word(0xF284):
            matches=[i for i in range(4) if np.array_equal(palette(em),normal[i]) or np.array_equal(palette(em),bright[i])]
            assert matches,('Unknown phase palette',palette(em).tolist())
            stages.update(matches)
            if not em.word(0xF3E4):render_colours.add(sky(em))
            if not entry:
                entry=True;em.save(ROOT/'build/checks/mangekyo-transition-v19.png')
            if np.array_equal(palette(em),normal[3]) and not em.word(0xF3E4):
                candidate=sky(em)
                # Palette RAM is committed to CRAM on the next native VBlank.
                if candidate[0]>candidate[2] and candidate[1]<daylight[1]:
                    night=candidate;em.save(ROOT/'build/checks/mangekyo-night-v19.png');break
    assert entry and night and night[0]>night[2] and night[1]<daylight[1],(daylight,night,stages)
    assert stages==set(range(4)),('Missing a visible fade step',stages)
    em.run(1,[3]);em.run(3);assert em.byte(0xC175)
    paused=palette(em).copy();cue=em.word(0xF2EC);colour=sky(em)
    em.run(90)
    assert np.array_equal(paused,palette(em)) and cue==em.word(0xF2EC) and colour==sky(em)
    em.run(1,[3]);em.run(3);assert not em.byte(0xC175)
    for frame in range(12000):
        em.run(1,fight_keys(em,True))
        if em.word(0xF10A):break
    assert em.word(0xF10A) and np.array_equal(palette(em),normal[0]),'Daylight not restored on victory'
    em.run(1,[3]);start_game(em)
    assert not em.word(0xF284) and np.array_equal(palette(em),normal[0]),'Restart retained the red world'
    report=dict(result='pass',ram_modified=False,training_target=target,fade_stages=sorted(stages),
        daylight_sky_rgb=daylight,mangekyo_sky_rgb=night,rendered_fade_colours=sorted(render_colours),pause_holds_lighting=True,
        victory_restores_daylight=True,restart_restores_daylight=True,
        rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest())
    (ROOT/'build/checks/environment-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
finally:em.close()
