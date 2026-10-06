"""Audit the visible plane tiles after real damage, pause and jutsu selection."""
import hashlib,json
from emulate import Emulator,ROOT
from playtest import start_game,select_jutsu,JUTSUS
from review_sprite_budget import SpriteAudit


TRAIL=((0x82E9,0x82F4,0x82F5,0x82F6,0x82F7),
       (0x82EA,0x82EA,0x8498,0x8499,0x849A),
       (0x82EB,0x82EB,0x82EB,0x849B,0x849C),
       (0x82EC,0x82EC,0x82EC,0x82EC,0x849D),
       (0x82ED,)*5)


def words(vram,address,count):
    return [int.from_bytes(vram[address+i*2:address+i*2+2],'big') for i in range(count)]


def main():
    em=Emulator(ROOT/'build/custom/golden-axe.bin');report=dict(ram_modified=False)
    version=json.loads((ROOT/'assets/custom/asset-report.json').read_text())['version']
    short='v'+version.removeprefix('0.')
    try:
        start_game(em);audit=SpriteAudit(em);seen=set();contacts=[]
        for index,name in enumerate(JUTSUS):
            before=(em.word(0xF180),em.word(0xF184))
            select_jutsu(em,index);em.run(2)
            vram=audit.read_vram();icon=words(vram,0xCD2A,2)+words(vram,0xCDAA,2)
            assert len(set(icon))==4 and all(0x8494<=n<=0x84BF for n in icon)
            pixels=b''.join(vram[(n&2047)*32:(n&2047)*32+32] for n in icon)
            signature=hashlib.sha256(pixels).hexdigest();assert signature not in seen;seen.add(signature)
            assert not em.word(0xF160) and not em.word(0xF162),'Selection cast a technique'
            assert em.word(0xF180)==before[0] and em.word(0xF184)==before[1]
            hint='ELEGIR' if index else '      '
            assert words(vram,0xCDC4,6)==[0x84C0+ord(c)-32 for c in hint]
            em.save(ROOT/f'build/checks/hud-{short}-icon-{index}.png')
            contacts.append(dict(jutsu=name,tiles=icon,pixel_sha256=signature))
        em.core.retro_reset();start_game(em);audit=SpriteAudit(em)
        damage=False;drained=False;partial=False;pause=False;damage_hp=None
        for frame in range(500):
            em.run(1,[7] if frame<75 else [])
            hp=em.byte(0xFE7E);trail=em.word(0xF36E)
            assert hp<=trail<=48,(frame,hp,trail)
            vram=audit.read_vram();actual=words(vram,0xCD08,12)
            expected=[TRAIL[min(4,max(0,hp-i*4))][min(4,max(0,trail-i*4))] for i in range(12)]
            assert actual==expected,('Visible life meter disagrees with health/trail',frame,hp,trail,actual,expected)
            if trail>hp:
                damage=True;damage_hp=hp;em.save(ROOT/f'build/checks/hud-{short}-damage.png')
                if not pause:
                    em.run(1,[3]);em.run(2);assert em.byte(0xC175)
                    frozen=(em.word(0xF36E),em.word(0xF370),em.byte(0xFE7E))
                    em.run(90)
                    assert frozen==(em.word(0xF36E),em.word(0xF370),em.byte(0xFE7E))
                    em.run(1,[3]);em.run(2);assert not em.byte(0xC175);pause=True
            if damage and trail<48:drained=True
            if hp%4:partial=True
        assert damage and drained and partial and pause,(damage,drained,partial,pause)
        report.update(result='pass',version=version,technique_icons=contacts,damage_hp=damage_hp,
            visible_damage_trail=True,trail_drained=True,partial_health_cells=True,pause_freezes_trail=True,
            rom_sha256=hashlib.sha256((ROOT/'build/custom/golden-axe.bin').read_bytes()).hexdigest())
        (ROOT/'build/checks/hud-feedback-check.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report))
    finally:em.close()


if __name__=='__main__':main()
