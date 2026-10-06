"""Record a continuous real-emulator playthrough with controller input and audio.

No game RAM is modified. The installed FFmpeg wheel is local to tools/.
"""
import ctypes as C
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from emulate import Emulator, ROOT
from playtest import fight_keys, JUTSUS

sys.path.insert(0,str(ROOT/'tools/video-python'))
import imageio_ffmpeg


class Geometry(C.Structure):
    _fields_=[('width',C.c_uint),('height',C.c_uint),('max_width',C.c_uint),
              ('max_height',C.c_uint),('aspect',C.c_float)]
class Timing(C.Structure):
    _fields_=[('fps',C.c_double),('sample_rate',C.c_double)]
class AV(C.Structure):
    _fields_=[('geometry',Geometry),('timing',Timing)]


# One selected jutsu per encounter, after demonstrating the native melee combo.
WAVE_JUTSUS=(None,3,4,5,6,1,2,0,None,1)
COSTS=(30,40,25,30,35,25,30)


def record_fight_keys(em):
    keys=fight_keys(em)
    wave=min(9,em.word(0xC210)//224)
    if not em.word(0xF220) and 0 in keys and em.word(0xF152)>=2:
        forward=6 if em.byte(0xD044)&1 else 7
        if wave==0:return (0,forward)
        if wave==8:return (0,13-forward)
    if em.word(0xF220) and 0 in keys:
        hp=em.word(0xF282)
        if not em.word(0xF2DE):return (0,4)
        if em.word(0xF152)>=2:
            forward=6 if em.byte(0xD044)&1 else 7
            if not em.word(0xF2DA):return (0,forward)
            if not em.word(0xF2DC):return (0,13-forward)
            return (0,13-forward if hp>24 else forward)
        if all(em.word(a) for a in (0xF2DA,0xF2DC)) and hp>40 and em.word(0xF2DE)<3:return (0,4)
    # At the viewport edge, an enemy can be 34px away while the route asks
    # for 30px. Use the actual 36px melee reach instead of pushing the clamp.
    edge=(keys==[7] and em.word(0xD01C)>=400) or (keys==[6] and em.word(0xD01C)<=176)
    if edge:
        for slot in (0xD100,0xD180,0xD200):
            if not(em.byte(slot)&128) or not em.byte(slot+0x64):continue
            dx=em.word(slot+0x1C)-em.word(0xD01C)
            dy=em.word(slot+0x20)-em.word(0xD020)
            if abs(dx)<=36 and abs(dy)<=5 and (em.byte(0xD044)&1)==(dx<0):
                return (0,)
    return keys


def choose_keys(em,frame,cast_waves,framed_waves,story_frames,boss_frames):
    if em.word(0xF204):
        page=em.word(0xF202);story_frames.setdefault(page,frame)
        if frame-story_frames[page]<150:return ()
        return (0,) if frame%2==0 else ()
    if em.word(0xF220) and em.word(0xF200)==2:
        boss_frames.setdefault('start',frame)
        if frame-boss_frames['start']<720:
            dy=em.word(0xF22E)-em.word(0xD020) if em.word(0xF22A) else 172-em.word(0xD020)
            if abs(dy)>4:return (5 if dy>0 else 4,)
            return (6,) if frame%240<60 else (7,) if frame%240<120 else ()
    wave=min(9,em.word(0xC210)//224)
    desired=WAVE_JUTSUS[wave]
    if em.word(0xF160):return ()
    world=em.word(0xD01C)+em.word(0xC210)-128
    if 350<=world<=650 and not em.word(0xF1A4):
        # Show the new wooden training target breaking through a real attack.
        dy=128-em.word(0xD020)
        dx=496-world
        if abs(dy)>3:return (5 if dy>0 else 4,)
        direction=7 if dx>=0 else 6
        if abs(dx)>26 or (em.byte(0xD044)&1)!=(dx<0):return (direction,)
        return (0,)
    # Demonstrate any route missed against the small early enemies before
    # magic finishes the boss. Inputs still use native range and recovery.
    if em.word(0xF220) and not all(em.word(a) for a in (0xF2DA,0xF2DC,0xF2DE)):
        return record_fight_keys(em)
    targets=[s for s in (0xD100,0xD180,0xD200)
             if em.byte(s)&128 and em.byte(s+0x64)>0]
    if not targets or desired is None or wave in cast_waves:
        if targets and wave==9 and wave in cast_waves and frame-boss_frames.get('start',frame)>1620:
            # After the melee/jutsu showcase, finish the real fight with Raikiri.
            if em.word(0xF182)!=0:
                return (4,1) if frame%2==0 else ()
            return fight_keys(em,True)
        return record_fight_keys(em)
    # Step back into the middle of the viewport before a large effect.
    if wave not in framed_waves:
        if em.word(0xD01C)>128+180:return (6,)
        framed_waves.add(wave)
    if em.word(0xF182)!=desired:
        return (4,1) if frame%2==0 else ()
    target=min(targets,key=lambda s:abs(em.word(s+0x1C)-em.word(0xD01C)))
    dx=em.word(target+0x1C)-em.word(0xD01C)
    dy=em.word(target+0x20)-em.word(0xD020)
    direction=7 if dx>=0 else 6
    if abs(dy)>5:return (5 if dy>0 else 4,)
    if abs(dx)>88:return (direction,)
    if (em.byte(0xD044)&1)!=(dx<0):return (direction,)
    if em.word(0xF180)<COSTS[desired]:return record_fight_keys(em)
    if em.word(0xF162) or (em.byte(0xD042)&127):return ()
    # A edge on alternate frames: wait until native recovery permits a cast.
    return (1,) if frame%2==0 else ()


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--preview-seconds',type=int,default=0)
    parser.add_argument('--version',default='0.17')
    parser.add_argument('--show-movement',action='store_true')
    options=parser.parse_args()
    preview=options.preview_seconds>0
    version=options.version
    tag='estado-actual' if preview else 'partida'
    output=ROOT/'build/videos'
    output.mkdir(parents=True,exist_ok=True)
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    em=Emulator(ROOT/'build/custom/golden-axe.bin',capture_audio=True)
    encoder=None
    try:
        em.run(350);em.audio.clear()
        av=AV();em.core.retro_get_system_av_info(C.byref(av))
        fps=av.timing.fps
        silent=output/f'kakashi-konoha-v{version}-video.mp4'
        logfile=output/'record-encode.log'
        with logfile.open('wb') as log:
            encoder=subprocess.Popen([ffmpeg,'-y','-hide_banner','-loglevel','warning',
                '-f','rawvideo','-pix_fmt','rgb24','-s','320x224','-r',str(fps),
                '-i','pipe:0','-vf','scale=960:672:flags=neighbor',
                '-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p',
                '-movflags','+faststart','-an',str(silent)],stdin=subprocess.PIPE,
                stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
            events=[];cast_waves=set();framed_waves=set();last_cast=0;last_wave=-1;victory_frame=None
            story_frames={};boss_frames={};story_faces=set()
            recorded=0;movement_start=None;movement_poses=set()
            em.save(output/f'kakashi-konoha-v{version}-poster.png')
            for frame in range(round(fps*options.preview_seconds) if preview else 18000):
                wave=min(9,em.word(0xC210)//224)
                keys=choose_keys(em,frame,cast_waves,framed_waves,story_frames,boss_frames) if victory_frame is None else ()
                if options.show_movement and movement_start is None and em.word(0xF200)==1 and not em.word(0xF204):
                    movement_start=frame
                if movement_start is not None:
                    age=frame-movement_start
                    if age<45:keys=(4,)
                    elif age==45 or 48<=age<51:keys=()
                    elif 46<=age<48 or 51<=age<93:keys=(7,)
                em.run(1,keys)
                if (em.byte(0xD042)&127)==8 and not em.word(0xF160):
                    movement_poses.add(em.word(0xD072))
                if em.word(0xF204) and em.word(0xF20C)!=65535:story_faces.add(em.word(0xF20C))
                if wave!=last_wave:
                    print(json.dumps({'recording_seconds':round(frame/fps,1),'encounter':wave+1}),flush=True)
                    last_wave=wave
                if em.word(0xF184)!=last_cast:
                    kind=em.word(0xF164);cast_waves.add(wave)
                    events.append({'frame':frame,'seconds':round(frame/fps,2),
                                   'jutsu':JUTSUS[kind],'encounter':wave+1})
                    last_cast=em.word(0xF184)
                if em.word(0xF160)==50:
                    em.save(output/f'capture-{JUTSUS[em.word(0xF164)]}.png')
                encoder.stdin.write(em.frame.tobytes());recorded+=1
                assert em.word(0xF100)==0 and em.word(0xF106)==0
                if em.word(0xF10A) and victory_frame is None:
                    victory_frame=frame
                if victory_frame is not None and frame-victory_frame>=round(fps*4):break
            encoder.stdin.close()
            result=encoder.wait(timeout=60)
        assert result==0,logfile.read_text(errors='replace')
        if not preview:assert victory_frame is not None,'Recording did not reach victory'
        assert set(e['jutsu'] for e in events)==set(JUTSUS),events
        assert em.word(0xF156)>=3,'No melee combo demonstrated'
        routes=[em.word(a) for a in (0xF2D8,0xF2DA,0xF2DC,0xF2DE)]
        assert all(routes),('Missing a directional combo route',routes)
        if not preview:
            assert set(story_frames)==set(range(8)),story_frames
            assert story_faces==set(range(4)),story_faces
            assert em.word(0xF1A4)>0,'Training-target break missing from video'
        assert all(em.word(a) for a in (0xF236,0xF238,0xF23A)),'Missing boss technique in video'
        if options.show_movement:assert set(range(37,45))<=movement_poses,('Running not demonstrated',movement_poses)
        audio=output/f'kakashi-konoha-v{version}-audio.wav'
        em.save_audio(audio)
        pcm=np.frombuffer(b''.join(em.audio),dtype='<i2')
        assert np.sqrt(np.mean(pcm.astype(float)**2))>50,'Audio recording is silent'
        final=output/f'kakashi-konoha-v{version}-{tag}.mp4'
        mux=subprocess.run([ffmpeg,'-y','-hide_banner','-loglevel','warning',
            '-i',str(silent),'-i',str(audio),'-c:v','copy','-c:a','aac','-b:a','160k',
            '-movflags','+faststart','-shortest',str(final)],capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW,timeout=60)
        assert mux.returncode==0,mux.stderr.decode(errors='replace')
        decode=subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-i',str(final),
            '-f','null','-'],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=60)
        assert decode.returncode==0,decode.stderr.decode(errors='replace')
        report=dict(result='pass',source='Genesis Plus GX libretro, real controller input',
                    ram_modified=False,continuous_take=True,version=version,
                    rom_sha256=hashlib.sha256((ROOT/'build/custom/golden-axe.bin').read_bytes()).hexdigest(),
                    width=960,height=672,fps=fps,frames=recorded,duration_seconds=round(recorded/fps,2),
                    audio_rate=round(av.timing.sample_rate),audio_rms=round(float(np.sqrt(np.mean(pcm.astype(float)**2))),1),
                    victory=victory_frame is not None,preview=preview,melee_contacts=em.word(0xF156),max_combo=em.word(0xF15A),
                    jutsu_events=events,jutsu_contacts={name:em.word(0xF190+i*2) for i,name in enumerate(JUTSUS)},
                    objects_broken=em.word(0xF1E6),scrolls_collected=em.word(0xF1E8),
                    training_target_broken=bool(em.word(0xF1A4)),
                    story_pages=[dict(page=k,seconds=round(v/fps,2)) for k,v in sorted(story_frames.items())],
                    story_faces=sorted(story_faces),boss_hp=em.word(0xF280),
                    boss_techniques=dict(clones=em.word(0xF236),crows=em.word(0xF238),fire=em.word(0xF23A)),
                    damage_reactions=em.word(0xF3D0),player_reactions=em.word(0xF3D4),landings=em.word(0xF3D2),music_steps=em.word(0xF310),music_scene=em.word(0xF300),village_chirps=em.word(0xF316),output=str(final),bytes=final.stat().st_size,decoder_check='pass')
        report['combo_routes']={name:em.word(0xF2D8+i*2) for i,name in enumerate(('neutral','lunge','sweep','uppercut'))}
        report['current_boss_hp']=em.byte(0xD164)
        report['mangekyo']=bool(em.word(0xF284))
        report['flank_changes']=em.word(0xF3EC)
        report['kamui_absorbed_shots']=em.word(0xF3EA)
        report['phase_second_flames']=em.word(0xF2FE)
        report['elemental_fire_counters']=em.word(0xF368)
        report['native_running_poses']=sorted(movement_poses)
        report['movement_showcase_seconds']=round(movement_start/fps,2) if movement_start is not None else None
        (output/f"recording-v{version}{'-preview' if preview else ''}.json").write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(report),flush=True)
    finally:
        if encoder and encoder.poll() is None:encoder.kill();encoder.wait()
        em.close()


if __name__=='__main__':main()
