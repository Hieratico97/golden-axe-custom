"""Capture all displayed walk poses from actual controller movement."""
import json
from PIL import Image,ImageDraw
from emulate import Emulator,ROOT
from playtest import start_game
em=Emulator(ROOT/'build/custom/golden-axe.bin')
version=json.loads((ROOT/'assets/custom/asset-report.json').read_text())['version']
short='v'+version.removeprefix('0.')
try:
    start_game(em);em.run(24,[4]);shots={};frames=[]
    for i in range(58):
        em.run(1,[7]);pose=em.word(0xD072)
        frames.append(em.frame.copy())
        if 29<=pose<=36 and pose not in shots:
            x=em.word(0xD01C)-128;y=em.word(0xD020)
            shots[pose]=em.frame.crop((x-48,y-88,x+48,y+8))
    assert set(shots)==set(range(29,37)),shots.keys()
    sheet=Image.new('RGB',(1152,624),'#152233');d=ImageDraw.Draw(sheet)
    for i,(pose,im) in enumerate(sorted(shots.items())):
        x=i%4*288;y=i//4*312;d.text((x+10,y+5),f'Walk {pose-29+1}',fill='white')
        sheet.paste(im.resize((288,288),Image.Resampling.NEAREST),(x,y+24))
    sheet.save(ROOT/f'build/checks/walk-{short}-real-contact.png')
    frames[0].resize((960,672),0).save(ROOT/f'build/checks/walk-{short}-real.gif',save_all=True,
        append_images=[im.resize((960,672),0) for im in frames[1:]],duration=17,loop=0)
finally:em.close()
