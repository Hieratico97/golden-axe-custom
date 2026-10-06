"""20-second editorial cut: verified gameplay, architecture and agent loop."""
import hashlib,json,math,subprocess,sys,wave
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/video-python'))
import imageio_ffmpeg

W,H,FPS=1920,1080,30
OUT=ROOT/'build/videos/desarrollo-20s'
SOURCE=ROOT/'build/v0.29-backup/videos/kakashi-konoha-v0.29-partida.mp4'
PCM=ROOT/'build/videos/kakashi-konoha-v0.29-audio.wav'
BG='#091320';PANEL='#14243A';INK='#F3F6FA';MUTED='#A7BACF'
CYAN='#55DDD2';GOLD='#F6C778';PINK='#EA86B5';LINE='#35506C'
FONTS={}


def font(size,bold=False):
    key=size,bold
    if key not in FONTS:FONTS[key]=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf',size)
    return FONTS[key]


def label(draw,xy,text,size=34,color=INK,bold=False):
    draw.text(xy,text,font=font(size,bold),fill=color)


def wrap(draw,xy,text,width,size=34,color=MUTED,line_height=49,bold=False):
    x,y=xy;line=''
    for word in text.split():
        candidate=(line+' '+word).strip()
        if draw.textlength(candidate,font=font(size,bold))>width and line:
            label(draw,(x,y),line,size,color,bold);y+=line_height;line=word
        else:line=candidate
    if line:label(draw,(x,y),line,size,color,bold);y+=line_height
    return y


def arrow(draw,points,color=CYAN,width=6):
    draw.line(points,fill=color,width=width,joint='curve')
    x,y=points[-1];px,py=points[-2];a=math.atan2(y-py,x-px)
    draw.polygon([(x,y),(x-21*math.cos(a-.45),y-21*math.sin(a-.45)),
        (x-21*math.cos(a+.45),y-21*math.sin(a+.45))],fill=color)


def box(draw,rect,title,subtitle='',accent=CYAN,active=False):
    x,y,r,b=rect
    draw.rounded_rectangle(rect,24,fill=PANEL,outline=accent if active else LINE,width=5 if active else 2)
    draw.rounded_rectangle((x+24,y+26,x+32,b-26),4,fill=accent)
    label(draw,(x+58,y+35),title,38,INK,True)
    if subtitle:wrap(draw,(x+58,y+102),subtitle,r-x-90,29,MUTED,43)


def canvas(title,kicker,chapter,t):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    for x in range(0,W,80):d.line((x,150,x,H),fill='#102034')
    for y in range(150,H,80):d.line((0,y,W,y),fill='#102034')
    label(d,(64,29),kicker.upper(),24,CYAN,True)
    label(d,(64,66),title,56,INK,True)
    label(d,(1680,42),f'{chapter:02} / 06',28,MUTED,True)
    d.rectangle((0,H-8,W,H),fill=LINE)
    d.rectangle((0,H-8,round(W*t/20),H),fill=CYAN)
    return im,d


def gameplay_frame(raw,title,kicker,chapter,t,heading,body,tag):
    im,d=canvas(title,kicker,chapter,t)
    # The complete native 320x224 picture stays visible, including its HUD.
    shot=Image.frombytes('RGB',(320,224),raw).resize((1280,896),Image.Resampling.NEAREST)
    im.paste(shot,(64,144))
    d.rounded_rectangle((1390,174,1856,950),26,fill=PANEL,outline=LINE,width=2)
    d.rounded_rectangle((1424,214,1504,224),5,fill=CYAN)
    y=wrap(d,(1424,265),heading,392,43,INK,56,True)
    y=wrap(d,(1424,y+34),body,390,33,MUTED,48)
    label(d,(1424,842),tag,25,GOLD,True)
    label(d,(1424,887),'GAMEPLAY REAL · v0.29',21,MUTED)
    return im


def architecture(local,t):
    im,d=canvas('Del ensamblador a una ROM jugable','Arquitectura',2,t)
    cards=[(64,320,624,555),(680,320,1240,555),(1296,320,1856,555)]
    titles=['ASM 68000 + recursos','ROM de Mega Drive','Emulador']
    subs=['Motor desensamblado + arte nuevo','Ensamblador + empaquetado','Mando, imagen y sonido']
    for i,rect in enumerate(cards):box(d,rect,titles[i],subs[i],(CYAN,GOLD,PINK)[i],int(local/.95)%3==i)
    arrow(d,[(628,435),(674,435)]);arrow(d,[(1244,435),(1290,435)])
    label(d,(68,225),'GOLDEN AXE → KAKASHI: KONOHA',31,CYAN,True)
    box(d,(64,655,945,872),'Código visible; lógica difícil','Memoria, rutinas heredadas y límites gráficos.',CYAN)
    box(d,(975,655,1856,872),'Contenido prácticamente nuevo','Personajes, nivel, historia, jutsus y jefe.',GOLD)
    label(d,(68,972),'Basado en un desensamblado existente de Golden Axe.',30,MUTED)
    return im


def loop(local,t):
    im,d=canvas('Cambiar → jugar → observar → repetir','Bucle agéntico',4,t)
    coords=[(64,285,624,485),(680,285,1240,485),(1296,285,1856,485),
            (1296,625,1856,825),(680,625,1240,825),(64,625,624,825)]
    titles=['1. Código + arte','2. Compilar ROM','3. Jugar con mando',
            '4. Grabar vídeo','5. Revisar + pruebas','6. Elegir mejora']
    subs=['Codex implementa','Construcción reproducible','Entradas reales de control',
          'Partida con audio','Fotogramas + datos del motor','La evidencia vuelve al agente']
    active=min(5,int(local/4*6))
    for i,rect in enumerate(coords):box(d,rect,titles[i],subs[i],CYAN,active==i)
    arrow(d,[(628,385),(674,385)]);arrow(d,[(1244,385),(1290,385)])
    arrow(d,[(1576,493),(1576,617)])
    arrow(d,[(1290,725),(1246,725)]);arrow(d,[(674,725),(630,725)])
    arrow(d,[(40,725),(24,725),(24,385),(56,385)],GOLD,4)
    label(d,(65,960),'El vídeo revela problemas que compilar no detecta.',37,GOLD,True)
    return im


def remote(local,t):
    im,d=canvas('Revisión humana, también en remoto','Arquitectura de revisión',6,t)
    coords=[(64,285,624,525),(680,285,1240,525),(1296,285,1856,525)]
    for i,(rect,title,sub) in enumerate(zip(coords,
            ['Codex en local','Vídeo en Drive','Revisión remota'],
            ['Modifica, prueba y graba','Gameplay para comprobar','La persona da nuevas indicaciones'])):
        box(d,rect,title,sub,(CYAN,GOLD,PINK)[i],min(2,int(local))==i)
    arrow(d,[(628,405),(674,405)]);arrow(d,[(1244,405),(1290,405)])
    arrow(d,[(1576,535),(1576,645),(344,645),(344,535)],GOLD)
    label(d,(660,595),'NUEVAS INSTRUCCIONES',27,GOLD,True)
    label(d,(66,775),'Mucha autonomía. Bugs visibles.',56,INK,True)
    label(d,(68,863),'La revisión humana sigue siendo necesaria.',39,MUTED)
    label(d,(68,987),'Golden Axe × Naruto · Desarrollo asistido por IA',27,CYAN)
    return im


CHAPTERS=[
    dict(kind='game',duration=3,start=13,title='Golden Axe, convertido en Konoha',kicker='Un experimento con Codex',
        heading='Una hack ROM de Naruto',body='Kakashi, nuevas técnicas y una fase sobre el motor original.',tag='ENSAMBLADOR 68000'),
    dict(kind='architecture',duration=4,start=10),
    dict(kind='game',duration=3,start=22.9,title='El agente implementa y prueba',kicker='Del cambio al juego',
        heading='Arte + código + sonido',body='Los cambios se comprueban en una partida real del emulador.',tag='KATON · COMBATE'),
    dict(kind='loop',duration=4,start=10),
    dict(kind='game',duration=3,start=112.95,title='El resultado también se observa',kicker='Revisión visual',
        heading='Mirar el vídeo para mejorar',body='Escala, impactos y efectos: los fotogramas orientan la siguiente iteración.',tag='KAMUI · ITACHI'),
    dict(kind='remote',duration=3,start=10),
]


def run(cmd,**kwargs):
    return subprocess.run(cmd,creationflags=subprocess.CREATE_NO_WINDOW,**kwargs)


def main():
    OUT.mkdir(parents=True,exist_ok=True);ff=imageio_ffmpeg.get_ffmpeg_exe()
    source_report=json.loads((ROOT/'build/v0.29-backup/videos/recording-v0.29.json').read_text())
    assert source_report['victory'] and source_report['decoder_check']=='pass'
    assert SOURCE.stat().st_size==source_report['bytes']
    silent=OUT/'desarrollo-sin-audio.mp4';final=OUT/'golden-axe-bucle-agentico-20s.mp4'
    encoder=subprocess.Popen([ff,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
        '-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18',
        '-pix_fmt','yuv420p','-movflags','+faststart',str(silent)],stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
    frame_count=0;saved=[];timeline=[]
    try:
        for chapter,row in enumerate(CHAPTERS,1):
            length=row['duration']*FPS;decoder=None;begin=frame_count/FPS
            if row['kind']=='game':
                decoder=subprocess.Popen([ff,'-hide_banner','-loglevel','error','-ss',str(row['start']),'-i',str(SOURCE),
                    '-t',str(row['duration']),'-vf','fps=30,scale=320:224:flags=neighbor','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],
                    stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
            for i in range(length):
                t=frame_count/FPS
                if decoder:
                    raw=decoder.stdout.read(320*224*3);assert len(raw)==320*224*3,('Short gameplay decode',chapter,i)
                    im=gameplay_frame(raw,row['title'],row['kicker'],chapter,t,row['heading'],row['body'],row['tag'])
                else:im=globals()[row['kind']](i/FPS,t)
                if i in (length//2,length-1):
                    path=OUT/f'review-{chapter:02}-{i:03}.png';im.save(path);saved.append(path.name)
                encoder.stdin.write(im.tobytes());frame_count+=1
            if decoder:
                decoder.stdout.close();err=decoder.stderr.read();assert decoder.wait()==0,err.decode(errors='replace')
            timeline.append(dict(chapter=chapter,kind=row['kind'],start_seconds=begin,duration_seconds=row['duration'],
                gameplay_source_seconds=row['start'] if row['kind']=='game' else None))
            print(json.dumps(dict(chapter=chapter,frames=frame_count)),flush=True)
        encoder.stdin.close();err=encoder.stderr.read();assert encoder.wait()==0,err.decode(errors='replace')
    finally:
        if encoder.poll() is None:encoder.kill();encoder.wait()
    assert frame_count==600
    with wave.open(str(PCM),'rb') as wav:
        channels=wav.getnchannels();rate=wav.getframerate();width=wav.getsampwidth()
        assert (channels,rate,width)==(2,44100,2)
        raw=wav.readframes(wav.getnframes())
    import numpy as np
    sound=[]
    for row in CHAPTERS:
        start=round(row['start']*rate);n=row['duration']*rate
        samples=np.frombuffer(raw,dtype='<i2').reshape(-1,2)[start:start+n].astype(float)
        assert len(samples)==n
        gain=1.4 if row['kind']=='game' else .7;samples*=gain
        fade=round(rate*.1);ramp=np.linspace(0,1,fade)[:,None]
        samples[:fade]*=ramp;samples[-fade:]*=ramp[::-1]
        sound.append(np.clip(samples,-32768,32767).astype('<i2').tobytes())
    audio=OUT/'desarrollo-audio.wav'
    with wave.open(str(audio),'wb') as wav:
        wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(rate);wav.writeframes(b''.join(sound))
    mux=run([ff,'-y','-hide_banner','-loglevel','error','-i',str(silent),'-i',str(audio),'-c:v','copy',
        '-c:a','aac','-b:a','192k','-t','20','-movflags','+faststart',str(final)],capture_output=True)
    assert mux.returncode==0,mux.stderr.decode(errors='replace')
    decode=run([ff,'-hide_banner','-loglevel','error','-i',str(final),'-f','null','-'],capture_output=True)
    assert decode.returncode==0,decode.stderr.decode(errors='replace')
    sheet=Image.new('RGB',(1280,3*380),BG);draw=ImageDraw.Draw(sheet)
    for i,path in enumerate(saved[::2]):
        x=i%2*640;y=i//2*380
        shot=Image.open(OUT/path);sheet.paste(shot.resize((640,360),Image.Resampling.LANCZOS),(x,y+20))
        label(draw,(x+8,y),f'{timeline[i]["start_seconds"]:.0f}–{timeline[i]["start_seconds"]+timeline[i]["duration_seconds"]:.0f}s',16,CYAN)
    sheet.save(OUT/'storyboard.png')
    report=dict(result='pass',duration_seconds=20,frames=600,fps=30,width=W,height=H,
        audio='Stereo AAC 192k; game music/SFX from the verified take; no narration',
        timeline=timeline,source_video=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        source_rom_sha256=source_report['rom_sha256'],decoder_check='pass',output=str(final),
        bytes=final.stat().st_size,sha256=hashlib.sha256(final.read_bytes()).hexdigest(),review_frames=saved)
    (OUT/'video-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))


def verify_encoded():
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    final=OUT/'golden-axe-bucle-agentico-20s.mp4'
    check=run([ff,'-hide_banner','-loglevel','error','-i',str(final),
        '-map','0:v:0','-progress','pipe:1','-nostats','-f','null','-'],capture_output=True)
    assert check.returncode==0,check.stderr.decode(errors='replace')
    progress=check.stdout.decode().splitlines()
    frames=[int(line.split('=',1)[1]) for line in progress if line.startswith('frame=')][-1]
    assert frames==600,frames
    sheet=Image.new('RGB',(1280,1080),BG)
    saved=[]
    for i,t in enumerate([1.5,5,8.5,12,15.5,18.5]):
        path=OUT/f'encoded-{i+1:02}.png'
        result=run([ff,'-y','-hide_banner','-loglevel','error','-ss',str(t),
            '-i',str(final),'-frames:v','1',str(path)],capture_output=True)
        assert result.returncode==0,result.stderr.decode(errors='replace')
        with Image.open(path) as shot:
            assert shot.size==(1920,1080)
            sheet.paste(shot.resize((640,360),Image.Resampling.LANCZOS),(i%2*640,i//2*360))
        saved.append(path.name)
    sheet.save(OUT/'encoded-storyboard.png')
    report_path=OUT/'video-report.json'
    report=json.loads(report_path.read_text(encoding='utf-8'))
    report.update(encoded_frames=frames,encoded_review_frames=saved,encoded_decoder_check='pass')
    report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(encoded_frames=frames,output=str(final),review=str(OUT/'encoded-storyboard.png'))))


if __name__=='__main__':
    if '--verify-only' in sys.argv:verify_encoded()
    else:main()
