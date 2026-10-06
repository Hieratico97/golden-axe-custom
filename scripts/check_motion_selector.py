"""Real controller regressions for held chords, stride cycles and run casting."""
import hashlib,json
from emulate import Emulator,ROOT
from playtest import start_game

em=Emulator(ROOT/'build/custom/golden-axe.bin')
report={'ram_modified':False,'version':json.loads((ROOT/'assets/custom/asset-report.json').read_text())['version']}
try:
    start_game(em)
    x,y=em.word(0xD01C),em.word(0xD020)
    em.run(1,[4,1]);assert em.word(0xF182)==1
    em.run(60,[4,1]);assert em.word(0xF182)==1,'Held chord cycled repeatedly'
    assert em.word(0xD01C)==x and em.word(0xD020)==y,'Selector moved player'
    assert em.word(0xF184)==0,'Selecting cast a jutsu'
    em.run(1,[1]);em.run(1,[5,1]);assert em.word(0xF182)==0
    em.run(30,[5,1]);assert em.word(0xF182)==0
    # Direction taps while A remains physically held, including wraparound.
    chosen=[]
    for _ in range(9):
        em.run(1,[1]);em.run(1,[4,1]);chosen.append(em.word(0xF182))
    assert chosen==[1,2,3,4,5,6,0,1,2],chosen
    assert not em.word(0xF184)
    # A-first and direction-first chords must never spend chakra or cast,
    # regardless of which button is released first.
    permutations=[]
    for delay in (1,2,6,15):
        for release_a_first in (False,True):
            em.run(1)
            selected=em.word(0xF182);casts=em.word(0xF184)
            em.run(delay,[1]);assert em.word(0xF184)==casts
            em.run(1,[4,1]);em.run(8,[4,1])
            assert em.word(0xF182)==(selected+1)%7
            em.run(3,[4] if release_a_first else [1]);em.run(1)
            assert em.word(0xF184)==casts and not em.word(0xF160)
            assert em.word(0xF180)==120
            permutations.append([delay,release_a_first])
    em.run(3,[5]);em.run(1,[5,1]);em.run(1);assert not em.word(0xF184)
    em.save(ROOT/'build/checks/ui-v11-selector.png')
    report.update(held_chord_frames=60,selection_taps=chosen,selector_stationary=True,selector_never_cast=True,a_first_release_permutations=permutations,direction_first_safe=True)
    # Start outside object lanes. Take enough steps to cover both full cycles.
    em.core.retro_reset();start_game(em);em.run(45,[4]);em.run(1)
    walk=set();walk_frames=[];origin=em.word(0xD01C)+em.word(0xC210)
    for f in range(54):
        em.run(1,[7]);walk.add(em.word(0xD072));walk_frames.append(em.frame.resize((640,448),0))
    walked=em.word(0xD01C)+em.word(0xC210)-origin
    assert set(range(29,37))<=walk,('walk',walk)
    em.save(ROOT/'build/checks/walk-v11.png')
    walk_frames[0].save(ROOT/'build/checks/walk-v11.gif',save_all=True,append_images=walk_frames[1:],duration=17,loop=0)
    em.core.retro_reset();start_game(em);em.run(45,[4]);em.run(1)
    em.run(2,[7]);em.run(3)
    origin=em.word(0xD01C)+em.word(0xC210)
    run=set();states=set();run_frames=[]
    for f in range(30):
        em.run(1,[7]);run.add(em.word(0xD072));states.add(em.byte(0xD042)&127);run_frames.append(em.frame.resize((640,448),0))
    ran=em.word(0xD01C)+em.word(0xC210)-origin
    print(json.dumps(dict(walk=sorted(walk),run=sorted(run),states=sorted(states),walked=walked,ran=ran)))
    assert set(range(37,45))<=run,('run',run)
    assert 8 in states,('not native running',states)
    assert ran/30>walked/54*1.5,(walked,ran)
    em.save(ROOT/'build/checks/run-v11.png')
    run_frames[0].save(ROOT/'build/checks/run-v11.gif',save_all=True,append_images=run_frames[1:],duration=17,loop=0)
    em.run(1,[7,1]);assert not em.word(0xF160),'A cast before release'
    em.run(1,[7]);assert em.word(0xF160),'Cannot cast directly from running'
    count=em.word(0xF184);em.run(160,[1]);assert em.word(0xF184)==count,'Held A recast automatically'
    report.update(walk_poses=sorted(walk),run_poses=sorted(run),walk_pixels=walked,walk_frames=54,run_pixels=ran,run_frames=30,run_cast=True,held_a_casts=1)
    # A pressed during a confirmed punch survives native recovery.
    em.core.retro_reset();start_game(em)
    for f in range(600):
        em.run(1,[7,0])
        if em.word(0xF156):break
    assert em.word(0xF156),'No melee contact before buffer check'
    em.run(1,[1]);em.run(1);pending=em.word(0xF2B4)
    assert pending>0,('A was not buffered',hex(em.word(0xD042)))
    for waited in range(36):
        em.run(1)
        if em.word(0xF184):break
    assert em.word(0xF184)==1,'Buffered jutsu was lost during recovery'
    report.update(melee_jutsu_buffer=pending,buffer_cast_after_frames=waited+1)
    em.core.retro_reset();start_game(em)
    for f in range(600):
        em.run(1,[7,0])
        if em.word(0xF156):break
    em.run(1,[1]);em.run(1);assert em.word(0xF2B4)
    em.run(1,[4,1]);assert not em.word(0xF2B4),'Selecting kept a queued cast'
    em.run(1,[1]);em.run(40)
    assert not em.word(0xF184),'Selection released a buffered jutsu'
    report.update(selection_cancels_queued_cast=True)
    # Release finishes native deceleration and switches immediately to guard.
    em.core.retro_reset();start_game(em);em.run(24,[4]);em.run(18,[7]);em.run(20)
    assert em.word(0xD070)==0,('stopping pose',em.word(0xD070))
    report.update(result='pass',stop_pose=0,rom_sha256=hashlib.sha256((ROOT/'build/custom/golden-axe.bin').read_bytes()).hexdigest())
    (ROOT/'build/checks/motion-selector-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
finally:em.close()
