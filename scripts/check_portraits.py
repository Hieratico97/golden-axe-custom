"""Observe all four actual dialogue cards and compare their complete VDP tiles."""
import ctypes as C,hashlib,json
from PIL import Image,ImageDraw
from emulate import Emulator,ROOT
from playtest import fight_keys


def swapped(raw):
    result=bytearray(len(raw));result[::2]=raw[1::2];result[1::2]=raw[::2];return bytes(result)


em=Emulator(ROOT/'build/custom/golden-axe.bin')
try:
    raw=(ROOT/'assets/custom/portrait-tiles.bin').read_bytes();meta=json.loads((ROOT/'assets/custom/portraits-v25.json').read_text())
    assert meta['opaque_card_pixels']==[3844]*4
    em.core.retro_serialize_size.restype=C.c_size_t
    em.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t]
    size=em.core.retro_serialize_size();buf=C.create_string_buffer(size)
    signature=swapped((ROOT/'assets/custom/city-tiles.bin').read_bytes()[32:288])
    em.run(330);base=None;seen=set();pages={};captures={};samples=0
    for frame in range(15000):
        dialogue=em.word(0xF204);page=em.word(0xF202)
        if dialogue:pages.setdefault(page,frame)
        keys=[] if dialogue and frame-pages[page]<90 else fight_keys(em,True)
        em.run(1,keys)
        face=em.word(0xF20C)
        if em.word(0xF204) and face<4 and frame%9==0:
            assert em.core.retro_serialize(buf,size)
            if base is None:
                found=buf.raw.find(signature);assert found>=32 and buf.raw.find(signature,found+1)==-1
                base=found-32
            expected=swapped(raw[face*2048:(face+1)*2048])
            assert buf.raw[base+0x6000:base+0x6800]==expected,('Incomplete portrait card',page,face)
            samples+=1;seen.add(face)
            if face not in captures and frame-pages.get(page,frame)>=60:
                captures[face]=em.frame.copy();em.save(ROOT/f'build/checks/portrait-v25-real-{face}.png')
        if em.word(0xF10A):break
    assert em.word(0xF10A) and seen==set(range(4)) and set(pages)==set(range(8)),(seen,pages)
    sheet=Image.new('RGB',(960,696),'#152233');draw=ImageDraw.Draw(sheet)
    for face,im in sorted(captures.items()):
        x=face%2*480;y=face//2*348;draw.text((x+8,y+4),f'Dialogue face {face}',fill='white')
        sheet.paste(im.resize((480,336),0),(x,y+12))
    sheet.save(ROOT/'build/checks/portraits-v25-real-contact.png')
    report=dict(result='pass',ram_modified=False,faces=sorted(seen),pages=sorted(pages),
        complete_vdp_card_samples=samples,opaque_pixels=meta['opaque_card_pixels'],victory=True,
        rom_sha256=hashlib.sha256((ROOT/'build/custom/golden-axe.bin').read_bytes()).hexdigest())
    (ROOT/'build/checks/portraits-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
finally:em.close()
