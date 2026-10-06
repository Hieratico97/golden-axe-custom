"""Estimate transparent-column savings from the actual native VDP pixels."""
import hashlib,json
from emulate import Emulator,ROOT
from playtest import fight_keys
from review_sprite_budget import SpriteAudit

em=Emulator(ROOT/'build/custom/golden-axe.bin')
try:
    em.run(330);audit=SpriteAudit(em);max_width=0;over=0;samples=0;actor_width=0;actor_over=0
    for frame in range(15000):
        em.run(1,fight_keys(em,True))
        if frame%3==0:
            row=audit.sample(trim_transparent='all');samples+=1
            max_width=max(max_width,row['max_pixels_per_line']);over+=bool(row['overflow_lines'])
            actor_row=audit.sample(trim_transparent='actors')
            actor_width=max(actor_width,actor_row['max_pixels_per_line']);actor_over+=bool(actor_row['overflow_lines'])
        if em.word(0xF10A):break
    assert em.word(0xF10A)
    report=dict(ram_modified=False,mode='offline simulation from actual VDP tiles; game unchanged',
        victory=True,samples=samples,simulated_max_pixels_per_line=max_width,simulated_overflow_frames=over,
        actor_trim_offscreen_max_pixels=actor_width,actor_trim_offscreen_overflow_frames=actor_over,
        rom_sha256=hashlib.sha256((ROOT/'build/custom/golden-axe.bin').read_bytes()).hexdigest())
    (ROOT/'build/checks/transparent-columns-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
finally:em.close()
