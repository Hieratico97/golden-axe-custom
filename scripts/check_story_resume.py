"""Compare controller cadence after dialogues using real input, without RAM writes."""
import argparse,hashlib,json
from emulate import Emulator,ROOT
from playtest import start_game,fight_keys


def audit(path):
    em=Emulator(path)
    try:
        start_game(em);exits=[];recent=-100;holds=[];samples=[];pages=set()
        for frame in range(12000):
            before=em.word(0xC17A);dialogue=em.word(0xF204)
            if dialogue:pages.add(em.word(0xF202))
            em.run(1,fight_keys(em,True))
            if dialogue and not em.word(0xF204):
                recent=frame;exits.append(dict(frame=frame,chapter=em.word(0xF200)))
            delta=(em.word(0xC17A)-before)&65535
            if frame-recent<=5:
                sample=dict(frame=frame,delta=delta,actor_bytes=em.word(0xF1FC),
                    budget_frames=em.word(0xF348),npc_bytes=em.word(0xD966),
                    cast=em.word(0xF160),dialogue=em.word(0xF204))
                samples.append(sample)
                if delta!=1:holds.append(sample)
            if em.word(0xF10A):break
        assert em.word(0xF10A),'Playthrough did not finish'
        assert 7 in pages and len(exits)==3,(pages,exits)
        return dict(rom_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            victory=True,ram_modified=False,frames=frame+1,dialogue_exits=exits,
            exit_controller_holds=holds,exit_samples=samples)
    finally:em.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--compare',action='store_true')
    options=parser.parse_args();report=dict(current=audit(ROOT/'build/custom/golden-axe.bin'))
    if options.compare:report['previous']=audit(ROOT/'build/v0.23-backup/golden-axe.bin')
    report.update(result='fail' if report['current']['exit_controller_holds'] else 'pass',ram_modified=False,
        rom_sha256=report['current']['rom_sha256'])
    (ROOT/'build/checks/story-resume-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
    assert not report['current']['exit_controller_holds'],report['current']['exit_controller_holds']
