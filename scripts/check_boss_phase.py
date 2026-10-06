"""Observe the two real boss phases and both clones using controller input."""
import hashlib,json,ctypes as C
from emulate import Emulator,ROOT
from playtest import start_game,fight_keys,dismiss_story

em=Emulator(ROOT/'build/custom/golden-axe.bin')
try:
    start_game(em)
    for frame in range(12000):
        em.run(1,fight_keys(em,True))
        if em.word(0xF220):break
    assert em.word(0xF220)
    dismiss_story(em)
    for frame in range(480):em.run(1)
    assert not em.word(0xF284)
    assert em.byte(0xD200)==0,'Second clone appears before Mangekyo'
    phase1_speed=set()
    for frame in range(12000):
        em.run(1,fight_keys(em,True))
        if em.byte(0xD100)&128 and em.byte(0xD143)<=2:
            v=em.word(0xD12C)
            if v:phase1_speed.add(v)
        if em.word(0xF284):break
    assert em.word(0xF284)==1 and em.word(0xF2EE)==1
    assert 0<em.byte(0xD164)<=30
    assert em.word(0xF204) and em.word(0xF202)==7,'Missing transformation dialogue'
    frozen=[em.word(a) for a in (0xD01C,0xD11C,0xD19C,0xD21C,0xF222)]
    em.run(12)
    assert frozen==[em.word(a) for a in (0xD01C,0xD11C,0xD19C,0xD21C,0xF222)]
    dismiss_story(em)
    assert em.word(0xF200)==2 and not em.word(0xF322),'Dialogue advanced the chapter'
    phase2_speed=set();patterns=set();actors=set();hp={};banks=set();two_clones=False;second_fire=False
    signatures=(ROOT/'assets/custom/city-tiles.bin').read_bytes()[32:288]
    signatures=bytes(v for pair in zip(signatures[1::2],signatures[::2]) for v in pair)
    em.core.retro_serialize_size.restype=C.c_size_t
    size=em.core.retro_serialize_size();buf=C.create_string_buffer(size)
    em.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t]
    rom=(ROOT/'build/custom/golden-axe.bin').read_bytes()
    base=None
    inherited_defeated=[hex(s) for s in (0xD180,0xD200) if em.byte(s)&128 and not em.byte(s+0x64)]
    passive_health_losses=[];healthy_clone_samples=0;pending_uploads=[];in_flight_uploads=[]
    for frame in range(2100):
        previous={s:em.byte(s+0x64) for s in (0xD180,0xD200) if em.byte(s)&128 and em.byte(s+0x64)>0}
        em.run(1)
        for pending in pending_uploads:
            slot=pending['slot'];source=pending['source'];pose=pending['pose'];address=pending['address']
            assert em.word(slot+0x72)==pose,('Clone upload did not commit next frame',pending)
            assert ((em.word(slot+0x74)<<16)|em.word(slot+0x76))==source
            assert em.core.retro_serialize(buf,size)
            raw=rom[source+pose*2048:source+(pose+1)*2048]
            expected=bytes(v for pair in zip(raw[1::2],raw[::2]) for v in pair)
            assert buf.raw[base+address:base+address+2048]==expected,('Completed clone upload differs',pending)
        pending_uploads=[]
        for s,old_hp in previous.items():
            if em.byte(s)&128 and em.byte(s+0x64)<old_hp:
                passive_health_losses.append(dict(frame=frame,slot=hex(s),before=old_hp,after=em.byte(s+0x64)))
        patterns.add(em.word(0xF226))
        if em.byte(0xD100)&128 and em.byte(0xD143)<=2:
            v=em.word(0xD12C)
            if v:phase2_speed.add(v)
        for slot,address in ((0xD180,0xA000),(0xD200,0x5000)):
            if not em.byte(slot)&128:continue
            actors.add(slot)
            # Corpses defeated by Kakashi before the transformation remain
            # active during their native death animation; they are not allies
            # newly losing health in this controller-free observation window.
            if em.byte(slot+0x64)>0:
                hp.setdefault(hex(slot),set()).add(em.byte(slot+0x64));healthy_clone_samples+=1
            assert em.byte(slot+0x64)<=8
            source=(em.word(slot+0x74)<<16)|em.word(slot+0x76)
            assert source==((em.word(0xD174)<<16)|em.word(0xD176)),'Clone costume differs'
            if frame%5==0:
                assert em.core.retro_serialize(buf,size)
                if base is None:base=buf.raw.find(signatures)-32;assert base>=0
                pose=em.word(slot+0x72)
                if pose==65535:continue
                raw=rom[source+pose*2048:source+(pose+1)*2048]
                expected=bytes(v for pair in zip(raw[1::2],raw[::2]) for v in pair)
                actual=buf.raw[base+address:base+address+2048]
                if actual!=expected:
                    # A video boundary can fall between the completed DMA and
                    # the cached-pose store. Require the exact planned drawing
                    # and its cache commit on the very next controller frame.
                    planned=em.word(0xF360 if slot==0xD180 else 0xF362)
                    assert planned==em.word(slot+0x70)==em.word(0xF294) and planned!=pose
                    assert em.byte(0xC183)&1 and not em.word(0xF1FC)
                    raw=rom[source+planned*2048:source+(planned+1)*2048]
                    planned_pixels=bytes(v for pair in zip(raw[1::2],raw[::2]) for v in pair)
                    assert actual==planned_pixels,('Clone bank corrupted',hex(slot),pose,planned)
                    pending=dict(slot=slot,address=address,source=source,pose=planned,frame=frame)
                    pending_uploads.append(pending);in_flight_uploads.append(pending)
                banks.add(address)
        if em.word(0xF2D0)==3 and all(em.byte(s)&128 for s in (0xD180,0xD200)):
            two_clones=True
            if not (ROOT/'build/checks/mangekyo-two-clones.png').exists():em.save(ROOT/'build/checks/mangekyo-two-clones.png')
        if em.word(0xF2F4) and em.byte(0xDD80):second_fire=True
    assert two_clones and actors=={0xD180,0xD200},(two_clones,actors,hp)
    assert not pending_uploads,'Last clone upload remains unverified'
    assert banks=={0xA000,0x5000},banks
    assert second_fire and em.word(0xF2FE)>0
    assert patterns=={0,1,2},patterns
    assert em.word(0xF3EC)>=3,'No actual flank changes'
    assert 1 in phase2_speed or 65534 in phase2_speed,phase2_speed
    assert em.word(0xF2EE)==1,'Phase retriggers every frame'
    assert not passive_health_losses,('Clone lost health without player attacks',passive_health_losses)
    assert healthy_clone_samples>200 and all(v=={8} for v in hp.values()),hp
    report=dict(result='pass',ram_modified=False,phase1_speed_words=sorted(phase1_speed),phase2_speed_words=sorted(phase2_speed),
                patterns=sorted(patterns),simultaneous_clones=2,clone_hp={s:sorted(v) for s,v in hp.items()},
                clone_vram_banks=[hex(a) for a in sorted(banks)],flank_changes=em.word(0xF3EC),
                second_flames=em.word(0xF2FE),transitions=em.word(0xF2EE),
                transformation_dialogue=True,dialogue_freezes_combat=True,
                no_friendly_fire_observed=not passive_health_losses,
                inherited_defeated_clones=inherited_defeated,healthy_clone_samples=healthy_clone_samples,
                in_flight_clone_uploads=in_flight_uploads,
                passive_clone_health_losses=passive_health_losses,
                friendly_contacts_rejected=em.word(0xF324),
                rom_sha256=hashlib.sha256(rom).hexdigest())
    (ROOT/'build/checks/boss-phase-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
finally:em.close()
