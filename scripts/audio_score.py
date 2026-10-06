"""Original pentatonic FM score and FM/PSG Foley for the native cartridge."""
import math


def frequency(midi):
    if not midi:return 0
    block=int(max(0,min(7,midi//12-1)))
    hz=440*2**((midi-69)/12)
    fnum=round(144*hz*2**20/(7670454*2**(block-1)))
    return (block<<11)|min(2047,fnum)


def patch_data(patch,channel):
    # Four operators in YM register order 1,3,2,4; algorithm 4's carriers are 2/4.
    offset=channel%3;data=[]
    for base,values in zip((0x30,0x40,0x50,0x60,0x70,0x80),patch[:6]):
        for slot,value in enumerate(values):data.extend((base+slot*4+offset,value))
    data.extend((0xB0+offset,patch[6],0xB4+offset,patch[7]))
    return data


SOFT_FLUTE=((1,1,1,1),(79,82,57,57),(13,13,12,12),(4,4,3,3),(1,1,1,1),(0x47,0x47,0x37,0x37),0x04,0xC0)
MUTED_PLUCK=((1,1,1,1),(72,77,60,60),(21,21,20,20),(11,12,9,9),(3,3,3,3),(0x67,0x67,0x57,0x57),0x04,0x80)
WARM_BASS=((1,1,1,1),(47,55,37,37),(24,24,23,23),(6,7,5,5),(3,3,3,3),(0x47,0x47,0x37,0x37),0x0C,0xC0)
TAIKO=((1,2,1,1),(38,54,30,30),(31,31,31,31),(19,22,18,20),(10,12,10,12),(0x2F,0x2F,0x2F,0x2F),0x24,0xC0)
BATTLE_STRINGS=((1,1,1,1),(56,61,38,38),(17,18,16,17),(3,4,3,3),(1,2,1,2),(0x37,0x37,0x37,0x37),0x14,0xC2)
BATTLE_OSTINATO=((1,2,1,1),(57,64,44,44),(25,25,24,24),(8,9,6,7),(3,3,2,3),(0x57,0x57,0x47,0x47),0x0C,0x40)
SFX_IMPACT=((1,3,1,1),(24,34,20,20),(31,31,31,31),(24,25,22,23),(12,12,10,10),(0x2F,0x2F,0x2F,0x2F),0x24,0xC0)
AMBIENT=((1,1,1,1),(78,84,73,73),(21,21,20,20),(14,14,12,12),(4,4,4,4),(0x5F,0x5F,0x5F,0x5F),0x04,0xC0)


def music_tables(directives):
    palettes=((SOFT_FLUTE,MUTED_PLUCK,WARM_BASS,TAIKO),
              (SOFT_FLUTE,MUTED_PLUCK,WARM_BASS,TAIKO),
              (BATTLE_STRINGS,BATTLE_OSTINATO,WARM_BASS,TAIKO),
              (SOFT_FLUTE,MUTED_PLUCK,WARM_BASS,TAIKO),
              (BATTLE_STRINGS,BATTLE_OSTINATO,WARM_BASS,TAIKO))
    parts=['MusicPatchTable:','\tdc.l '+','.join(f'MusicPatch{i}' for i in range(6))]
    for channel,patch in enumerate((*palettes[0],SFX_IMPACT,AMBIENT)):
        data=patch_data(patch,channel)
        parts += [f'MusicPatch{channel}:',f'\tdc.w {len(data)//2}',directives(data),'\teven']
    parts += ['MusicScenePatchTable:','\tdc.l '+','.join(f'MusicScenePatches{i}' for i in range(5))]
    for scene,patches in enumerate(palettes):
        parts += [f'MusicScenePatches{scene}:','\tdc.l '+','.join(f'MusicScenePatch{scene}_{c}' for c in range(4))]
        for channel,patch in enumerate(patches):
            data=patch_data(patch,channel)
            parts += [f'MusicScenePatch{scene}_{channel}:',f'\tdc.w {len(data)//2}',directives(data),'\teven']
    # Eight-note motifs with real held notes; -1 means tie, not another attack.
    motifs=((69,72,76,72,67,69,64,0),
            (57,62,64,62,55,57,60,0),
            (64,67,71,74,72,71,67,62),
            (74,76,79,81,79,76,74,0),
            (64,67,71,74,76,74,71,67))
    names=('Tsukuyomi','Konoha - brisa entre los tejados','Itachi - destino escarlata','Genjutsu roto','Mangekyo - romper el destino')
    tempi=(13,10,7,11,6)
    roots=((45,48,43,40),(50,43,47,45),(40,48,43,47,40,45,48,47),(50,55,47,50),(40,48,43,47,45,48,50,47))
    parts += ['MusicSceneTable:','\tdc.l '+','.join(f'MusicScene{i}' for i in range(5))]
    report=[]
    for scene in range(5):
        steps=[];tempo=tempi[scene]
        length=512 if scene in (2,4) else 256 if scene==1 else 128
        melody_notes=[]
        for step in range(length):
            root=roots[scene][(step//32)%len(roots[scene])];beat=step%16
            spacing=4 if scene in (0,1,3) else 2
            motif=motifs[scene];note=motif[(step//spacing)%8]
            # Sparse breathy village phrases, lower register and longer attacks.
            lead=note if step%spacing==0 else -1 if note else 0
            if scene in (2,4) and (step//32)%4==3 and note:lead=note-12 if lead>0 else lead
            pluck=root+12+(0,7,12,7,3,7,12,7)[step%8]
            if scene in (0,1,3) and step%2:pluck=0
            bass=root if step%4==0 else -1
            drum=36 if beat in (0,8) else 43 if beat in (4,12) else 0
            if scene in (0,3) and beat:drum=0
            if scene==1 and beat not in (0,8):drum=0
            if scene==4 and beat in (3,7,11,14,15):drum=45
            elif scene==2 and beat in (7,15):drum=43
            volumes=(51,59,50,62) if scene==1 else (39,48,42,52) if scene in (0,3) else (30,39,35,33)
            if scene==4:volumes=(28,36,33,30)
            gates=(tempo*spacing-1,tempo-2,tempo*4-1,tempo-1)
            if scene==1:
                # Lower register, soft FM modulation and breathing space.
                section=(step//64)%4
                if section==1 and lead>0:lead+=2
                if section==3 and step%32>=16:lead=0
                if step%4:pluck=0
                if beat not in (0,):drum=0
                volumes=(61,69,59,75)
                gates=(tempo*4-3,tempo*2-2,tempo*4-1,tempo-1)
            elif scene in (2,4):
                # Eight harmonic bars with an opening, answer and final rise.
                # Intensity comes from orchestration and rhythm, not shrillness.
                section=step//128
                phrase=(0,3,7,10,12,10,7,3) if section in (0,2) else (12,10,7,5,3,5,7,10)
                lead=root+24+phrase[(step//4)%8] if step%4==0 else -1
                if section==0 and step%32>=24:lead=0
                if scene==4 and section==3 and lead>0:lead+=3
                pluck=root+12+(0,7,12,7,3,7,10,7)[(step//2)%8] if step%2==0 else -1
                if section==0 and beat%4:pluck=0
                bass=root if beat in (0,8) else root+7 if beat==12 and section>=2 else -1
                drum=36 if beat in (0,8) else 43 if beat in (6,12) else 0
                if section>=1 and beat==15:drum=45
                if scene==4 and beat in (3,7,11,14):drum=45
                crescendo=(3-section)*2
                volumes=tuple(v+crescendo for v in ((37,47,39,42) if scene==2 else (34,44,37,38)))
                gates=(tempo*4-1,tempo*2-2,tempo*8-1,tempo-1)
            if lead>0:melody_notes.append(lead)
            events=[]
            for n,v,g in zip((lead,pluck,bass,drum),volumes,gates):
                f=65535 if n==-1 else frequency(n)
                events.append((f,v,0 if n==-1 else min(255,g)))
            steps.append(events)
        parts += [f'MusicScene{scene}:',f'\tdc.w {tempo},{len(steps)}',f'\tdc.l MusicNotes{scene}',f'MusicNotes{scene}:']
        for events in steps:
            data=[]
            for note,vol,gate in events:data.extend((note>>8,note&255,vol,gate))
            parts.append(directives(data))
        parts.append('\teven')
        report.append(dict(scene=scene,title=names[scene],step_frames=tempo,steps=len(steps),seconds=round(len(steps)*tempo/59.9227,2),
                           instruments='warm flute, muted pluck, bass, soft taiko' if scene==1 else 'strings, ostinato, bass, taiko' if scene in (2,4) else 'warm flute, pluck, bass, taiko',
                           held_notes=True,lead_max_midi=max(melody_notes),harmonic_bars=len(roots[scene]),
                           arrangement_sections=4 if scene in (1,2,4) else 1))
    return parts,dict(original_composition=True,sampled_audio=False,chip='YM2612 + SN76489',music_channels=4,sfx_fm_channel=4,ambient_fm_channel=5,packet_bytes=16,jutsu_music_ducking_db=9,scenes=report)


def sound_tables(directives):
    # tone-period/sweep plus FM pitch envelope. The ninth byte is key-on/off.
    profiles=((10,95,35,2,3,76,-2),(18,320,-12,1,1,50,-1),
              (35,35,9,1,4,94,-.5),(34,700,-17,3,5,69,.4),
              (33,390,-8,1,2,48,-.25),(34,280,5,2,6,57,.6),
              (24,650,-14,1,2,43,-.3),(28,110,15,2,5,59,-.5),
              (28,70,0,4,5,96,-.25),(20,800,-30,2,2,50,-1),
              (18,210,7,2,4,88,-1),(4,180,-20,9,15,84,0),
              (12,700,15,7,5,38,-.5),(14,280,8,4,3,52,-.6),
              (7,65,75,7,8,91,-3),(5,760,12,13,11,40,-.4),
              (20,25,36,1,1,102,-2.6),(30,900,-22,2,3,80,-1.3),
              (18,30,50,1,1,96,-2.4),(28,270,18,1,0,48,-.6),
              (30,500,14,2,2,65,-.9),(26,800,8,1,0,38,-.45),(22,120,16,2,3,57,-.7),
              (42,42,6,2,3,93,-.2),(9,82,30,1,2,74,-2.6),
              (13,500,22,1,1,43,-1.2),(12,140,23,2,3,88,-2),(18,820,-12,1,1,39,-.5))
    names=('punch','heavy-kick','lightning','kamui','fire','water','earth','ninken','crows','clone-smoke','kunai','selector','landing','hurt','swing','footstep',
           'raikiri-contact','kamui-contact','chidori-contact','katon-contact','suiton-contact','doton-contact','ninken-contact',
           'chidori-cast','head-hit','body-hit','kunai-slash-hit','sweep-thud')
    priorities=(2,3,3,3,3,3,3,3,3,2,2,0,1,2,1,0,4,4,4,4,4,4,4,3,2,2,3,3)
    patches=(SFX_IMPACT,
        ((7,11,1,1),(26,34,20,20),(31,31,31,31),(19,21,16,18),(7,9,6,8),(0x3F,0x3F,0x2F,0x2F),0x2C,0xC0),
        ((2,3,1,1),(40,48,25,25),(22,24,21,23),(7,9,5,7),(3,4,3,4),(0x4B,0x4B,0x3B,0x3B),0x14,0xC3),
        ((1,3,1,1),(35,43,22,22),(31,31,31,31),(13,15,11,13),(6,7,5,6),(0x4F,0x4F,0x3F,0x3F),0x24,0xC0),
        ((1,2,1,1),(49,53,30,30),(23,25,22,24),(10,12,8,10),(3,4,3,4),(0x4F,0x4F,0x3F,0x3F),0x14,0xC0),
        ((1,1,1,1),(30,42,19,19),(31,31,31,31),(22,24,20,22),(10,12,10,12),(0x2F,0x2F,0x2F,0x2F),0x24,0xC0),
        ((2,3,1,1),(36,44,25,25),(31,31,31,31),(12,14,10,12),(5,6,5,6),(0x4F,0x4F,0x3F,0x3F),0x24,0xC0),
        ((1,1,1,1),(65,68,48,48),(29,29,28,28),(20,20,18,18),(7,7,6,6),(0x2F,0x2F,0x2F,0x2F),0x0C,0xC0))
    families=(0,0,1,2,3,4,5,6,2,2,1,7,5,0,7,7,1,2,1,3,4,5,6,1,0,0,7,5)
    parts=['SfxPriorities:',directives(priorities),'\teven','SfxTable:']
    parts += ['\tdc.l '+','.join(f'Sfx{i}' for i in range(start,min(start+16,len(profiles)))) for start in range(0,len(profiles),16)]
    parts += ['SfxPatchTable:']
    parts += ['\tdc.l '+','.join(f'SfxPatch{families[i]}' for i in range(start,min(start+16,len(profiles)))) for start in range(0,len(profiles),16)]
    for i,patch in enumerate(patches):
        data=patch_data(patch,4)
        parts += [f'SfxPatch{i}:',f'\tdc.w {len(data)//2}',directives(data),'\teven']
    rows=[]
    for i,(duration,period,slope,volume,noise,pitch,bend) in enumerate(profiles):
        data=[]
        for frame in range(duration):
            divisor=max(12,min(1023,period+slope*frame+int(math.sin(frame*2.1)*period*.13)))
            attenuation=min(15,volume+int(frame/duration*12))
            noise_volume=min(15,noise+int(frame/duration*11))
            if i==8:attenuation=min(15,4+frame%6*2);noise_volume=min(15,5+frame%5*2)
            note=frequency(pitch+bend*frame)
            fmvol=min(127,(55 if i==11 else 58 if i==15 else 20)+int(frame/duration*65))
            key=0xF5 if frame==0 else 0xFF
            if i in (2,16,18,23):
                # Stuttering birds/electric crackles, not a plain descending beep.
                note=frequency(pitch+bend*frame+(0,5,-7,12)[frame%4])
                noise_volume=min(15,noise_volume+(3 if frame%3 else 0))
                if frame%4==0:key=0xF5
                elif frame%4==3:key=5
            elif i in (3,17):
                note=frequency(pitch+bend*frame+math.sin(frame*.45)*5)
                attenuation=min(15,4+round((1-math.sin(frame*.4))*3)+int(frame/duration*5))
            elif i in (4,19):
                fmvol=min(127,18+int(frame/duration*46))
                attenuation=12  # Fire is a rolling noise burst with a low FM body.
            elif i in (5,20):
                attenuation=min(15,5+int(frame/duration*8))
                noise_volume=min(15,2+int(frame/duration*11))
                note=frequency(pitch+bend*frame+math.sin(frame*.5)*3)
            elif i in (6,21,27):
                note=frequency(pitch-max(0,frame-2)*.65)
                fmvol=min(127,13+int(frame/duration*80))
            elif i in (7,22):
                note=frequency(pitch+bend*frame+(4 if frame%8<3 else -5))
                if frame%8==0:key=0xF5
            # Give every material a distinct noise texture and attack/tail.
            noise_clock=0xE7
            if i in (2,16,18,23):
                noise_clock=0xE4
                if frame<5:fmvol+=9;attenuation=min(15,attenuation+3)
            elif i in (3,17):
                noise_clock=0xE6
                divisor=max(160,divisor);note=frequency(pitch-12+bend*frame+math.sin(frame*.35)*4)
                noise_volume=min(15,noise_volume+4)
            elif i in (4,19):
                noise_clock=0xE6
                noise_volume=min(15,1+int(frame/duration*13))
                if frame%6==0:key=0xF5
            elif i in (5,20):noise_clock=0xE5
            elif i in (6,21,27):
                noise_volume=min(15,5+int(frame/duration*10));attenuation=14
                if frame in (0,5,11):key=0xF5
            elif i in (7,22):
                noise_clock=0xE6
                if frame%8==4:key=5
            elif i==15:fmvol=max(72,fmvol);attenuation=15;noise_volume=max(13,noise_volume)
            data += [0xC0|(divisor&15),divisor>>4,0xD0|attenuation,noise_clock,0xF0|noise_volume,note>>8,note&255,min(127,fmvol),key]
        data += [0xC0,1,0xDF,0xE7,0xFF,0,0,127,5]
        parts += [f'Sfx{i}:',f'\tdc.w {duration+1}',directives(data),'\teven']
        rows.append(dict(id=i,name=names[i],priority=priorities[i],frames=duration+1,packet_bytes=9,fm_timbre=families[i],registers=data))
    return parts,rows
