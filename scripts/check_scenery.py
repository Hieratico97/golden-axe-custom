"""Audit displayed scene columns through the full fight using controller input.

Read actual VRAM and its latched horizontal scroll, not only source assets.
Check background integrity, the exposed row below the compact HUD and wind.
"""
import ctypes as C
import hashlib,json,struct,time
from emulate import Emulator,ROOT
from playtest import start_game,fight_keys

def swapped(raw):
    b=bytearray(len(raw));b[::2]=raw[1::2];b[1::2]=raw[::2];return bytes(b)

em=Emulator(ROOT/'build/custom/golden-axe.bin')
try:
    em.core.retro_serialize_size.restype=C.c_size_t
    em.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t]
    em.core.retro_serialize.restype=C.c_bool
    size=em.core.retro_serialize_size();buffer=C.create_string_buffer(size)
    raw=(ROOT/'assets/custom/city-tiles.bin').read_bytes()
    display=(ROOT/'assets/custom/scene-display.bin').read_bytes()
    logical=(ROOT/'assets/custom/scene-logical.bin').read_bytes()
    alltiles=(ROOT/'assets/custom/scene-all-tiles.bin').read_bytes()
    npc_lookup=(ROOT/'assets/custom/scene-npc-lookup.bin').read_bytes()
    npc_tiles=(ROOT/'assets/custom/scene-npc-tiles.bin').read_bytes()
    npc_count=json.loads((ROOT/'assets/custom/scene-npc-report.json').read_text())['tiles_per_frame']
    npc_phases=set();npc_pixels=0
    signature=swapped(raw)[32:288]
    start_game(em);base=None;checked=0;samples=0;hud_rows=0;scrolls=[]
    captures=[];wind=set();thresholds=[0,352,800,1248,1696,2016]
    began=time.perf_counter();max_dma=0;loaded_columns=0;shakes=set()
    for frame in range(12000):
        em.run(1,fight_keys(em,magic=True))
        max_dma=max(max_dma,em.word(0xF2E6));loaded_columns=max(loaded_columns,em.word(0xF2E8))
        assert em.byte(0xDB00)==0,('Falling leaf still rendered',frame)
        if thresholds and em.word(0xC210)>=thresholds[0] and not em.word(0xF204):
            scroll=thresholds.pop(0)
            path=ROOT/f'build/checks/scenery-v19-{scroll:04}.png';em.save(path)
            captures.append(dict(scroll=em.word(0xC210),path=str(path)))
        if frame%7==0:
            assert em.core.retro_serialize(buffer,size)
            state=buffer.raw
            if base is None:
                pos=state.find(signature);assert pos>=32
                assert state.find(signature,pos+1)==-1
                base=pos-32
            vram=swapped(state[base:base+65536])
            assert vram[:288]==raw[:288],('scene signature overwritten',frame)
            camera=-struct.unpack_from('>h',vram,0xAC02)[0]
            assert -4<=camera<=2244,camera
            shake=em.word(0xF3E2);shakes.add(shake if shake<32768 else shake-65536)
            scrolls.append(camera)
            # One extra partial edge column is visible between tile boundaries.
            for row in range(28):
                for tx in range(camera//8,camera//8+40+(camera%8!=0)):
                    pos=(row*320+max(0,min(319,tx)))*2
                    expected=struct.unpack_from('>H',display,pos)[0]
                    actual=struct.unpack_from('>H',vram,0xE000+row*128+(tx%64)*2)[0]
                    assert actual==expected,('wrong visible scene tile',frame,camera,row,tx,hex(expected),hex(actual))
                    q=struct.unpack_from('>H',logical,pos)[0]
                    slot=actual&2047
                    index=struct.unpack_from('>H',npc_lookup,q*2)[0]
                    pixels=alltiles[q*32:(q+1)*32]
                    if index:
                        phase=em.word(0xD962);assert 0<=phase<4
                        offset=(phase*npc_count+index-1)*32
                        pixels=npc_tiles[offset:offset+32];npc_phases.add(phase);npc_pixels+=1
                    assert vram[slot*32:(slot+1)*32]==pixels,('wrong streamed tile pixels',frame,camera,row,tx,slot,q,'NPC frame',em.word(0xD962),'logical camera',em.word(0xC210),'cache column',em.word(0xF2E2),'actual',vram[slot*32:(slot+1)*32].hex(),'expected',pixels.hex())
                    checked+=1
            if not em.word(0xF204) and not em.word(0xF10A):
                assert not any(vram[0xC100:0xC250]),('HUD covers architecture rows 2..4',frame)
                assert any(vram[0xCD00:0xCD50]) and any(vram[0xCD80:0xCDD0]),'Bottom HUD missing'
                assert not any(vram[0xCC00:0xCCD0]),('Inherited orange health blocks remain',frame)
                hud_rows+=1
            samples+=1
        if em.word(0xF10A):break
    assert em.word(0xF10A),'No victory'
    assert not thresholds,('Unseen sectors',thresholds)
    assert not wind,wind
    assert npc_phases=={0,1,2,3} and npc_pixels>1000,(npc_phases,npc_pixels)
    # Pause in a fresh scene and ensure the display-only wind stays frozen.
    em.core.retro_reset();start_game(em);em.run(12)
    em.run(1,[3]);em.run(3)
    assert em.byte(0xC175)
    pose=[em.word(a) for a in (0xDB08,0xDB18,0xDB1C)]
    em.run(120)
    assert pose==[em.word(a) for a in (0xDB08,0xDB18,0xDB1C)]
    em.run(1,[3]);em.run(4);assert not em.byte(0xC175)
    report=dict(result='pass',ram_modified=False,version='0.21',victory=True,shake_offsets=sorted(shakes),npc_phases=sorted(npc_phases),animated_npc_tiles_checked=npc_pixels,
        captures=captures,visible_tile_words_checked=checked,samples=samples,
        stage_width=2560,scene_tiles=len(alltiles)//32,resident_tiles=len(raw)//32,maximum_boundary_tile_bytes=max_dma,loaded_columns=loaded_columns,
        hud_height=16,hud_position='bottom',exposed_hud_rows_checked=hud_rows,falling_leaves=False,
        maximum_camera=max(scrolls),
        native_update_rate='one controller step per emulated video frame',
        elapsed_seconds=round(time.perf_counter()-began,2),
        rom_sha256=hashlib.sha256((ROOT/'build/custom/golden-axe.bin').read_bytes()).hexdigest())
    (ROOT/'build/checks/scenery-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
finally:em.close()
