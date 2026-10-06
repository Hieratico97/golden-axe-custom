"""Actor sprite columns keep their native four-tile vertical stride."""
import json
import numpy as np


def sprite_trim_art(out,frames,directives):
    parts=[];counts={}
    for name,poses in frames.items():
        data=[];metas=[];saved=0;empty=0;pose_columns=[]
        for im in poses:
            a=np.array(im)
            assert a.shape==(64,64)
            regions=[];all_columns=[]
            for piece,(x,y) in enumerate(((0,0),(32,0),(0,32),(32,32))):
                columns=[col for col in range(4) if np.any(a[y:y+32,x+col*8:x+(col+1)*8])]
                all_columns.append(set(columns))
                left=min(columns) if columns else 0
                width=max(columns)-left+1 if columns else 0
                data.extend((left,width));saved+=(4-width)*8;empty+=not columns
                if width:regions.append((x-32+left*8,y-64,(width-1)*4+3,piece*16+left*4,width*8))
            assert regions,('Completely empty actor pose',name)
            for flip in (False,True):
                block=[len(regions)-1]
                for x,y,size,tile,width in regions:
                    if flip:x=-x-width;tile|=0x800
                    block.extend((y&255,size,tile>>8,tile&255,x&255))
                metas.extend(block+[0]*(24-len(block)))
            pose_columns.append(all_columns)
        assert len(data)==len(poses)*8
        (out/f'actor-trim-{name}.bin').write_bytes(bytes(data))
        assert len(metas)==len(poses)*48
        (out/f'actor-trim-meta-{name}.bin').write_bytes(bytes(metas))
        parts += [f'ActorTrim{name.title()}:',f'\tbinclude "custom/actor-trim-{name}.bin"','\teven']
        parts += [f'ActorTrimMeta{name.title()}:',f'\tbinclude "custom/actor-trim-meta-{name}.bin"','\teven']
        # A core/frame boundary can occur between SAT and actor transfers.
        # Union geometry protects both old and new complete poses, including
        # a partially transferred pose. Invalid cache uses the full canvas.
        union=[]
        for old in range(len(poses)+1):
            for new in range(len(poses)):
                regions=[]
                for n in range(4):
                    columns=set(range(4)) if old==len(poses) else pose_columns[old][n]|pose_columns[new][n]
                    if not columns:continue
                    left=min(columns);width=max(columns)-left+1
                    regions.append((n%2*32-32+left*8,n//2*32-64,(width-1)*4+3,n*16+left*4,width*8))
                for flip in (False,True):
                    block=[len(regions)-1]
                    for x,y,size,tile,width in regions:
                        if flip:x=-x-width;tile|=0x800
                        block.extend((y&255,size,tile>>8,tile&255,x&255))
                    union.extend(block+[0]*(24-len(block)))
        (out/f'actor-trim-union-{name}.bin').write_bytes(bytes(union))
        parts += [f'ActorTrimUnion{name.title()}:',f'\tbinclude "custom/actor-trim-union-{name}.bin"','\teven']
        counts[name]=dict(poses=len(poses),bytes=len(data),empty_pieces=empty,
            mean_transparent_fetch_pixels_removed_per_pose=round(saved/len(poses),2))
    (out/'actor-trim-report.json').write_text(json.dumps(dict(result='pass',actors=counts,
        stride_tiles=4,only_transparent_columns_removed=True),indent=2)+'\n')
    return parts
