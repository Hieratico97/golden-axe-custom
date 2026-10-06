"""Observe original gait and magic after dismissing its actual opening story."""
import json
from PIL import Image,ImageDraw
from emulate import Emulator,ROOT
em=Emulator(ROOT/'build/baseline/golden-axe.bin')
try:
    em.run(350)
    for i in range(4):
        em.save(ROOT/f'build/checks/original-reference-{i}.png')
        print(i,hex(em.word(0xC172)),hex(em.byte(0xD000)),flush=True)
        em.run(1,[3]);em.run(180)
    if em.byte(0xC175):em.run(1,[3]);em.run(3)
    em.run(1800)
    em.run(1,[0]);em.run(120)
    assert (em.byte(0xD042)&127)==0,'Original story has not finished'
    em.save(ROOT/'build/checks/original-controller-ready.png')
    seen=set();shots=[];unique={};trace=[]
    for i in range(72):
        em.run(1,[7])
        shots.append(em.frame.copy())
        # The custom D070 pose cache does not exist in the original game.
        # Track its displayed metadata and native animation subframe instead.
        meta=(em.word(0xD00A)<<16)|em.word(0xD00C)
        trace.append(dict(frame=i,x=em.word(0xD01C),lane=em.word(0xD020),
            state=em.word(0xD042),animation_subframe=em.byte(0xD014),metadata=meta))
        if meta not in unique and len(unique)<8 and not(em.byte(0xD042)&127):
            x=em.word(0xD01C)-128;y=em.word(0xD020)
            unique[meta]=em.frame.crop((x-48,y-88,x+48,y+8))
    sheet=Image.new('RGB',(1152,624),'#152233');draw=ImageDraw.Draw(sheet)
    for i,(meta,im) in enumerate(unique.items()):
        x=i%4*288;y=i//4*312;draw.text((x+10,y+5),f'Original pose {i+1}',fill='white')
        sheet.paste(im.resize((288,288),0),(x,y+24))
    sheet.save(ROOT/'build/checks/original-walk-contact.png')
    shots[0].resize((960,672),0).save(ROOT/'build/checks/original-walk.gif',save_all=True,
        append_images=[im.resize((960,672),0) for im in shots[1:]],duration=17,loop=0)
    em.run(12)
    em.run(1,[1])
    for i in range(120):
        em.run(1)
        if i in (12,30,60,90):em.save(ROOT/f'build/checks/original-magic-{i}.png')
    (ROOT/'build/checks/original-reference.json').write_text(json.dumps(dict(ram_modified=False,
        story_dismissed=True,walk_trace=trace,unique_walk_metadata=len(unique)),indent=2)+'\n')
    print(json.dumps(dict(story_dismissed=True,walk_frames=len(shots),unique_walk_metadata=len(unique))))
finally:em.close()
