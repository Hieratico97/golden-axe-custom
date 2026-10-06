"""Allocate VRAM tile lifetimes offline, including reversible scroll events."""
import heapq,json,struct


def build_scene(result,out,tile_bytes,nemesis,slots=640,animation=None):
    # Nine fixed tiles allow emulator audits to locate VRAM at any scroll.
    prefix=(out.parents[1]/'assets/reference/scene-signature.bin').read_bytes()
    tiles=[prefix[i:i+32] for i in range(0,len(prefix),32)]
    td={raw:i for i,raw in enumerate(tiles)}
    logical=[];columns=[set() for _ in range(320)]
    animated=[]
    for y in range(0,224,8):
        row=[]
        for x in range(0,2560,8):
            raw=tile_bytes(result.crop((x,y,x+8,y+8)))
            variants=[tile_bytes(frame.crop((x,y,x+8,y+8))) for frame in animation] if animation else [raw]
            if any(v!=raw for v in variants):
                q=len(tiles);tiles.append(raw)
                animated.append(dict(column=x//8,row=y//8,logical=q,frames=variants))
            else:
                if raw not in td:td[raw]=len(tiles);tiles.append(raw)
                q=td[raw]
            row.append(q);columns[x//8].add(q)
        logical.append(row)
    uses={i:[] for i in range(9,len(tiles))}
    for x,col in enumerate(columns):
        for q in col:
            if q>=9:uses[q].append((max(0,x-41),min(280,x+1)))
    intervals=[]
    for q,parts in uses.items():
        a,b=parts[0]
        for c,d in parts[1:]:
            if c<=b+1:b=max(b,d)
            else:intervals.append((a,b,q));a,b=c,d
        intervals.append((a,b,q))
    intervals.sort()
    free=list(range(9,slots));heapq.heapify(free);active=[]
    assigned={};events=[[] for _ in range(281)];contents=[0]*slots;initial=[0]*slots
    for i in range(9):contents[i]=initial[i]=i
    peak=0
    for a,b,q in intervals:
        while active and active[0][0]<a:
            _,slot=heapq.heappop(active);heapq.heappush(free,slot)
        if not free:raise ValueError(f'Scene VRAM overflow at camera {a*8}: {len(active)+10} tiles, budget {slots}')
        slot=heapq.heappop(free);heapq.heappush(active,(b,slot));peak=max(peak,len(active)+9)
        assigned.setdefault(q,[]).append((a,b,slot))
        old=contents[slot]
        if a==0:initial[slot]=q
        elif old!=q:events[a].append((slot,q,old))
        contents[slot]=q
    display=[]
    for row in logical:
        new=[]
        for x,q in enumerate(row):
            if q<9:slot=q
            else:
                c=max(0,x-41)
                slot=next(s for a,b,s in assigned[q] if a<=c<=b)
            new.append(0x6000|slot)
        display.append(new)
    raw=b''.join(tiles)
    initial_raw=b''.join(tiles[q] for q in initial)
    (out/'city-tiles.bin').write_bytes(initial_raw)
    (out/'city.nem').write_bytes(nemesis(initial_raw))
    (out/'scene-all-tiles.bin').write_bytes(raw)
    (out/'scene-logical.bin').write_bytes(b''.join(struct.pack('>320H',*r) for r in logical))
    (out/'scene-display.bin').write_bytes(b''.join(struct.pack('>320H',*r) for r in display))
    (out/'scene-columns.bin').write_bytes(b''.join(struct.pack('>28H',*(display[y][x] for y in range(28))) for x in range(320)))
    initmap=[]
    for y in range(64):
        initmap.extend(display[y][:62]+[display[y][0]]*2 if y<28 else [0]*64)
    (out/'scene-initial-map.bin').write_bytes(struct.pack('>4096H',*initmap))
    data=bytearray();offsets=[]
    for ev in events:
        offsets.append(len(data));data+=struct.pack('>H',len(ev))
        for slot,new,old in ev:data+=struct.pack('>3H',slot,new,old)
    (out/'scene-events.bin').write_bytes(data)
    (out/'scene-event-offsets.bin').write_bytes(struct.pack('>281I',*offsets))
    # Adjacent resident slots in one world column form a single DMA run.
    # Keep source indices consecutive in that order as well.
    animated.sort(key=lambda item:(item['column'],display[item['row']][item['column']]&2047))
    assert len(animated)*4*32<=32768,'Animation source must fit its aligned ROM bank'
    lookup=[0]*len(tiles);index=bytearray(struct.pack('>H',len(animated)))
    report=json.loads((out/'scenery-report.json').read_text())
    inhabitants=report.get('animated_inhabitants',[])
    metadata=[]
    for i,item in enumerate(animated):
        x=item['column'];y=item['row'];q=item['logical'];slot=display[y][x]&2047
        lookup[q]=i+1;index+=struct.pack('>4H',x,slot,i,q)
        npc=next(n['id'] for n in inhabitants if n['x']//8<=x<=(n['x']+n['width']-1)//8
                 and n['y']//8<=y<=(n['y']+n['height']-1)//8)
        metadata.append(dict(column=x,row=y,logical=q,slot=slot,index=i,npc=npc))
    (out/'scene-npc-index.bin').write_bytes(index)
    (out/'scene-npc-lookup.bin').write_bytes(struct.pack('>'+str(len(lookup))+'H',*lookup))
    (out/'scene-npc-tiles.bin').write_bytes(b''.join(item['frames'][phase] for phase in range(4) for item in animated))
    (out/'scene-npc-report.json').write_text(json.dumps(dict(frames=4,tiles_per_frame=len(animated),
        bytes_per_frame=len(animated)*32,inhabitants=inhabitants,tiles=metadata),indent=2)+'\n')
    # The native boot loader still consumes an eight-bit block grid. Its flat
    # placeholder is replaced by the full ring map before the intro appears.
    (out/'city-blocks.bin').write_bytes(struct.pack('>4H',*[0x6000]*4))
    report.update(logical_tiles=len(tiles),resident_tiles=slots,peak_visible_tiles=peak,
                  forward_events=sum(map(len,events)),maximum_boundary_tile_bytes=max(map(len,events))*32,
                  streaming='offline lifetime allocation with reverse events',signature_tiles=9,
                  npc_animated_tiles=len(animated))
    (out/'scenery-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return slots,1
