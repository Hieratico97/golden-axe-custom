"""Capture the running poses actually uploaded while using native double-tap."""
import json
from PIL import Image,ImageDraw
from emulate import Emulator,ROOT
from playtest import start_game

em=Emulator(ROOT/'build/custom/golden-axe.bin')
version=json.loads((ROOT/'assets/custom/asset-report.json').read_text())['version']
short='v'+version.removeprefix('0.')
try:
    start_game(em);em.run(45,[4]);em.run(1)
    em.run(2,[7]);em.run(3)
    shots={};frames=[]
    for _ in range(42):
        em.run(1,[7]);pose=em.word(0xD072);frames.append(em.frame.copy())
        if 37<=pose<=44 and pose not in shots:
            x=em.word(0xD01C)-128;y=em.word(0xD020)
            shots[pose]=em.frame.crop((x-48,y-88,x+48,y+8))
    assert set(shots)==set(range(37,45)),shots.keys()
    sheet=Image.new('RGB',(1152,624),'#152233');draw=ImageDraw.Draw(sheet)
    for i,(pose,im) in enumerate(sorted(shots.items())):
        x=i%4*288;y=i//4*312;draw.text((x+10,y+5),f'Run {pose-37+1}',fill='white')
        sheet.paste(im.resize((288,288),Image.Resampling.NEAREST),(x,y+24))
    sheet.save(ROOT/f'build/checks/run-{short}-real-contact.png')
    frames[0].resize((960,672),0).save(ROOT/f'build/checks/run-{short}-real.gif',save_all=True,
        append_images=[im.resize((960,672),0) for im in frames[1:]],duration=17,loop=0)
    print(json.dumps(dict(result='pass',ram_modified=False,displayed_poses=sorted(shots))))
finally:em.close()
