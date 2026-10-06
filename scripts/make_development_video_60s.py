"""One-minute split-screen explainer, with real gameplay throughout."""
import hashlib,json,math,subprocess,sys,wave
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import make_development_video as style

ROOT=style.ROOT
OUT=ROOT/'build/videos/desarrollo-60s'
SOURCE=style.SOURCE
PCM=style.PCM
W,H,FPS=1920,1080,30
BG,PANEL,INK,MUTED=style.BG,style.PANEL,style.INK,style.MUTED
CYAN,GOLD,PINK,LINE=style.CYAN,style.GOLD,style.PINK,style.LINE
label,wrap,font,arrow=style.label,style.wrap,style.font,style.arrow
RUN_FLAGS=dict(creationflags=subprocess.CREATE_NO_WINDOW)

# Each segment uses the matching audio from the same verified controller take.
SCENES=[
    dict(title='Golden Axe × Naruto',eyebrow='UNA HACK ROM',accent=CYAN,cuts=[(22.4,3),(64.1,3)],
        mode='hook',footer='Kakashi en Konoha. El motor sigue siendo Golden Axe.',
        steps=[('Personajes','Kakashi y ninjas enemigos'),('Mundo','Una fase nueva en Konoha'),('Combate','Jutsus, combos y un jefe')]),
    dict(title='Leer el motor original',eyebrow='01 / INGENIERÍA INVERSA',accent=GOLD,cuts=[(12,6)],
        mode='pipeline',footer='Código visible; comportamiento difícil de deducir.',
        steps=[('Desensamblado','Código Motorola 68000'),('Investigar rutinas','Memoria, animación y colisiones'),('Cambiar y observar','Ejecutar para comprobar el efecto')]),
    dict(title='Construir una ROM',eyebrow='02 / ARQUITECTURA',accent=CYAN,cuts=[(37.7,3),(45.1,3)],
        mode='pipeline',footer='El ensamblador une lógica, gráficos y sonido.',
        steps=[('ASM + recursos','Motor, sprites, escenarios y audio'),('Ensamblar y empaquetar','Construcción reproducible'),('Emulador de Mega Drive','Imagen, sonido y entradas de mando')]),
    dict(title='El agente implementa',eyebrow='03 / DESARROLLO CON CODEX',accent=PINK,cuts=[(54.8,3),(71.3,3)],
        mode='pipeline',footer='Cada cambio termina en una partida que se puede revisar.',
        steps=[('Elegir una mejora','Combate, animaciones o escenario'),('Editar código y arte','Respetar los límites de Mega Drive'),('Compilar y jugar','Comprobar el resultado real')]),
    dict(title='El vídeo es evidencia',eyebrow='04 / REVISIÓN VISUAL',accent=CYAN,cuts=[(80,6)],
        mode='review',footer='Compilar sin errores no garantiza que el juego se vea bien.',
        steps=[('Escala','Comparar personajes y escenario'),('Impactos','Observar reacciones y efectos'),('Fluidez','Detectar pausas y cambios de pose')]),
    dict(title='El bucle agéntico',eyebrow='05 / ITERACIÓN',accent=GOLD,cuts=[(92.2,3),(107,3)],
        mode='loop',footer='La siguiente mejora parte de lo que acaba de ocurrir.',
        steps=[('Implementar','Código + arte'),('Compilar','ROM nueva'),('Jugar','Control real'),('Grabar','Vídeo + sonido'),('Revisar','Pruebas + fotogramas'),('Iterar','Nueva mejora')]),
    dict(title='La pelea con Itachi',eyebrow='06 / JEFE FINAL',accent=PINK,cuts=[(112,6)],
        mode='boss',footer='Kakashi combate a Itachi dentro de un genjutsu.',
        steps=[('Más resistencia','60 puntos de vida'),('Enemigos adicionales','Clones con menos vida'),('Ataques propios','Cuervos y jutsu de fuego')]),
    dict(title='Técnicas y respuesta',eyebrow='07 / COMBATE CONTRA ITACHI',accent=CYAN,cuts=[(119,6)],
        mode='review',footer='Animación, sonido y reacción deben transmitir el impacto.',
        steps=[('Kakashi','Kamui, Raikiri y otros jutsus'),('Itachi','Clones, cuervos y fuego'),('Revisar el resultado','Legibilidad y sensación de combate')]),
    dict(title='Revisión en remoto',eyebrow='08 / ARQUITECTURA DE REVISIÓN',accent=GOLD,cuts=[(128,6)],
        mode='pipeline',footer='Las indicaciones humanas vuelven a Codex.',
        steps=[('Codex en local','Modifica, ejecuta y graba'),('Vídeo en Drive','Permite revisar la partida a distancia'),('Feedback humano','Orienta la siguiente iteración')]),
    dict(title='Autonomía ≠ acabado',eyebrow='09 / ESTADO DEL EXPERIMENTO',accent=PINK,cuts=[(145.8,6)],
        mode='ending',footer='Un prototipo jugable. Todavía necesita criterio y trabajo.',
        steps=[('Mucho contenido nuevo','Sobre un motor clásico'),('Bugs y arte irregular','La IA aún deja errores evidentes'),('Revisión humana','Sigue siendo necesaria')]),
]


def ease(x):
    x=max(0,min(1,x));return 1-(1-x)**3


def combat_detail(raw):
    image=Image.frombytes('RGB',(320,224),raw)
    pixels=np.asarray(image).astype(np.int16)
    # Track a small pale head/hair cluster, excluding sky and large wall patches.
    roi=pixels[45:140,170:319]
    mask=(roi.min(axis=2)>155)&(roi.max(axis=2)-roi.min(axis=2)<45)&(roi[:,:,2]>=roi[:,:,0]-10)
    points=set(map(tuple,np.argwhere(mask)));candidates=[]
    while points:
        seed=points.pop();todo=[seed];component=[seed]
        while todo:
            y,x=todo.pop()
            for nxt in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
                if nxt in points:points.remove(nxt);todo.append(nxt);component.append(nxt)
        if not 5<=len(component)<=110:continue
        ys,xs=zip(*component)
        if max(xs)-min(xs)>18 or max(ys)-min(ys)>18:continue
        cx=sum(xs)/len(xs)+170;cy=sum(ys)/len(ys)+45
        candidates.append((len(component)*2-abs(cx-280)*.25,cx,cy))
    _,cx,cy=max(candidates) if candidates else (0,277,80)
    x=max(0,min(280,round(cx-20)));y=max(0,min(200,round(cy-8)))
    return image.crop((x,y,x+40,y+24)).resize((232,139),Image.Resampling.NEAREST)


def card(d,rect,title,sub,accent,active,number):
    x,y,r,b=rect
    d.rounded_rectangle(rect,18,fill=PANEL,outline=accent if active else LINE,width=3 if active else 1)
    d.rounded_rectangle((x+18,y+20,x+63,y+65),10,fill=accent if active else LINE)
    label(d,(x+30,y+22),str(number),27,BG if active else INK,True)
    label(d,(x+83,y+18),title,31,INK,True)
    wrap(d,(x+83,y+65),sub,r-x-107,26,MUTED,35)


def frame(raw,row,index,local,absolute,cut_local):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im);accent=row['accent']
    for x in range(0,W,72):d.line((x,100,x,H),fill='#102034')
    for y in range(110,H,72):d.line((0,y,W,y),fill='#102034')
    label(d,(36,24),'GOLDEN AXE → KAKASHI: KONOHA',32,INK,True)
    label(d,(1390,30),'DESARROLLO CON IA',23,CYAN,True)
    label(d,(1778,26),f'{int(absolute):02}s / 60',26,MUTED,True)
    d.line((36,92,1884,92),fill=LINE,width=2)
    # Entire picture and HUD always remain visible on the left.
    shot=Image.frombytes('RGB',(320,224),raw).resize((1152,806),Image.Resampling.NEAREST)
    im.paste(shot,(36,160))
    d.rectangle((34,158,1189,967),outline=accent,width=2)
    label(d,(36,112),'GAMEPLAY REAL  /  v0.29',24,MUTED,True)
    if index>=6:
        d.rounded_rectangle((821,111,1188,151),10,fill='#3B223A')
        label(d,(845,114),'KAKASHI vs ITACHI',25,PINK,True)
    else:
        label(d,(900,113),'MEGA DRIVE',25,GOLD,True)
    d.rounded_rectangle((36,983,1188,1040),14,fill=PANEL)
    label(d,(56,990),row['footer'],26,INK)
    # Right panel: the explanation stays beside the game for all 60 seconds.
    d.rounded_rectangle((1220,112,1884,1040),24,fill=BG,outline=LINE,width=2)
    slide=round(30*(1-ease(local/.45)))
    label(d,(1252+slide,145),row['eyebrow'],23,accent,True)
    wrap(d,(1252+slide,191),row['title'],588,47,INK,58,True)
    d.rounded_rectangle((1252,325,1330+round(470*ease(local/.9)),330),2,fill=accent)
    active=min(len(row['steps'])-1,int(local/6*len(row['steps'])))
    if row['mode']=='loop':
        # Snake diagram: 1 → 2 ↓ 3 ← 4 ↓ 5 → 6, built one step at a time.
        coords=[(1252,370),(1560,370),(1560,540),(1252,540),(1252,710),(1560,710)]
        for j,(title,sub) in enumerate(row['steps']):
            reveal=ease((local-j*.48)/.32)
            if reveal<=0:continue
            x,y=coords[j];y+=round(14*(1-reveal));color=accent if active==j else LINE
            d.rounded_rectangle((x,y,x+292,y+135),16,fill=PANEL,outline=color,width=3 if active==j else 1)
            label(d,(x+18,y+14),f'{j+1:02}',23,accent,True)
            label(d,(x+18,y+43),title,30,INK,True)
            label(d,(x+18,y+91),sub,24,MUTED)
        routes=[[(1548,433),(1556,433)],[(1706,508),(1706,535)],[(1556,602),(1548,602)],
                [(1398,679),(1398,705)],[(1548,773),(1556,773)]]
        for j,p in enumerate(routes):
            if local>(j+1)*.48:
                arrow(d,p,accent,4)
                if active==j:
                    f=(local%1)/1
                    x=p[0][0]+(p[-1][0]-p[0][0])*f
                    y=p[0][1]+(p[-1][1]-p[0][1])*f
                    d.ellipse((x-5,y-5,x+5,y+5),fill=INK)
        if local>3:arrow(d,[(1848,853),(1866,853),(1866,351),(1398,351),(1398,365)],GOLD,3)
        wrap(d,(1254,908),'Cambiar → jugar → observar → repetir',570,28,accent,37,True)
    else:
        for j,(title,sub) in enumerate(row['steps']):
            reveal=ease((local-j*.6)/.4)
            if reveal<=0:continue
            y=374+j*173+round(18*(1-reveal))
            card(d,(1252,y,1852,y+147),title,sub,accent,active==j,j+1)
            if active==j:
                f=(local%2)/2
                d.rounded_rectangle((1270,y+137,1270+max(3,564*f),y+141),2,fill=accent)
                pulse=4+round(2*math.sin(local*5))
                d.ellipse((1822-pulse,y+33-pulse,1822+pulse,y+33+pulse),fill=accent)
            if j<2 and row['mode']=='pipeline' and local>(j+1)*.6:
                arrow(d,[(1552,y+150),(1552,y+168)],accent,4)
        note={'hook':'UN MOTOR CLÁSICO. UN JUEGO CASI NUEVO.',
              'pipeline':'CÓDIGO → EJECUCIÓN → EVIDENCIA',
              'review':'VER → COMPARAR → CORREGIR',
              'boss':'LA BATALLA CONTINÚA A LA IZQUIERDA',
              'ending':'MÁS AGENCIA. AÚN MUCHO AI SLOP.'}[row['mode']]
        wrap(d,(1254,932),note,570,25,accent,35,True)
        if index in (6,7,9) and local>=3.8:
            # Brief close-ups accompany the boss fight; the full game stays visible.
            y=720+round(18*(1-ease((local-3.8)/.3)))
            d.rounded_rectangle((1252,y,1852,y+147),18,fill=PANEL,outline=accent,width=3)
            detail=combat_detail(raw)
            im.paste(detail,(1256,y+4))
            label(d,(1510,y+21),'Detalle del combate',28,INK,True)
            wrap(d,(1510,y+67),'Efectos y reacciones, vistos de cerca.',315,26,MUTED,34)
    # Timeline with ten chapter marks and an animated cue inside the current card.
    for j in range(10):
        x=36+j*185;d.rounded_rectangle((x,1057,x+174,1064),3,fill=accent if j==index else LINE)
        if j<index:d.rounded_rectangle((x,1057,x+174,1064),3,fill=CYAN)
    d.rectangle((0,1074,W,1080),fill=LINE)
    d.rectangle((0,1074,round(W*absolute/60),1080),fill=accent)
    # A short border pulse signals each new gameplay cut, without covering it.
    if cut_local<.23:
        d.rectangle((34,158,1189,967),outline=INK,width=max(2,round(8*(1-cut_local/.23))))
    return im


def run(cmd,**kw):return subprocess.run(cmd,**RUN_FLAGS,**kw)


def extract(ff,seconds):
    p=run([ff,'-hide_banner','-loglevel','error','-ss',str(seconds),'-i',str(SOURCE),
           '-frames:v','1','-vf','scale=320:224:flags=neighbor','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],capture_output=True)
    assert p.returncode==0,p.stderr.decode(errors='replace')
    assert len(p.stdout)==320*224*3
    return p.stdout


def preview():
    OUT.mkdir(parents=True,exist_ok=True);ff=style.imageio_ffmpeg.get_ffmpeg_exe()
    sheet=Image.new('RGB',(1280,1800),BG)
    for i,row in enumerate(SCENES):
        local=3.6;start=row['cuts'][0][0];offset=local
        if len(row['cuts'])>1:start=row['cuts'][1][0];offset=local-3
        im=frame(extract(ff,start+offset),row,i,local,i*6+local,offset)
        im.save(OUT/f'layout-{i+1:02}.png')
        sheet.paste(im.resize((640,360),Image.Resampling.LANCZOS),(i%2*640,i//2*360))
    sheet.save(OUT/'layout-storyboard.png');print(str(OUT/'layout-storyboard.png'))


def main():
    OUT.mkdir(parents=True,exist_ok=True);ff=style.imageio_ffmpeg.get_ffmpeg_exe()
    source_report=json.loads((ROOT/'build/v0.29-backup/videos/recording-v0.29.json').read_text())
    assert source_report['victory'] and source_report['decoder_check']=='pass'
    assert SOURCE.stat().st_size==source_report['bytes']
    assert sum(duration for row in SCENES for _,duration in row['cuts'])==60
    silent=OUT/'desarrollo-sin-audio.mp4';final=OUT/'golden-axe-bucle-agentico-60s.mp4'
    encoder=subprocess.Popen([ff,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
        '-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','fast',
        '-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(silent)],
        stdin=subprocess.PIPE,stderr=subprocess.PIPE,**RUN_FLAGS)
    frames=0;timeline=[]
    try:
        for index,row in enumerate(SCENES):
            scene_frame=0
            for start,duration in row['cuts']:
                decoder=subprocess.Popen([ff,'-hide_banner','-loglevel','error','-ss',str(start),'-i',str(SOURCE),
                    '-t',str(duration),'-vf','fps=30,scale=320:224:flags=neighbor','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],
                    stdout=subprocess.PIPE,stderr=subprocess.PIPE,**RUN_FLAGS)
                timeline.append(dict(output_start=frames/FPS,source_start=start,duration=duration,
                                     chapter=index+1,itachi=index>=6))
                for i in range(duration*FPS):
                    raw=decoder.stdout.read(320*224*3)
                    assert len(raw)==320*224*3,('Short decode',index,i)
                    im=frame(raw,row,index,scene_frame/FPS,frames/FPS,i/FPS)
                    encoder.stdin.write(im.tobytes());frames+=1;scene_frame+=1
                decoder.stdout.close();err=decoder.stderr.read();assert decoder.wait()==0,err.decode(errors='replace')
            print(json.dumps(dict(chapter=index+1,frames=frames)),flush=True)
        encoder.stdin.close();err=encoder.stderr.read();assert encoder.wait()==0,err.decode(errors='replace')
    finally:
        if encoder.poll() is None:encoder.kill();encoder.wait()
    assert frames==1800
    with wave.open(str(PCM),'rb') as wav:
        assert (wav.getnchannels(),wav.getframerate(),wav.getsampwidth())==(2,44100,2)
        original=np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2').reshape(-1,2)
    rate=44100;parts=[]
    for row in timeline:
        start=round(row['source_start']*rate);n=round(row['duration']*rate)
        samples=original[start:start+n].astype(float)*3.2;assert len(samples)==n
        # Smooth the abrupt music transitions; preserve all actual gameplay SFX.
        fade=round(rate*.055);ramp=np.linspace(0,1,fade)[:,None]
        samples[:fade]*=ramp;samples[-fade:]*=ramp[::-1]
        parts.append(samples)
    samples=np.concatenate(parts)
    # Quiet, original synthesized whoosh marks chapter changes.
    rng=np.random.default_rng(68000)
    for sec in (range(6,60,6) if globals().get('TRANSITION_CUES',True) else []):
        n=int(.16*rate);t=np.arange(n)/rate
        noise=rng.standard_normal(n)
        noise=np.convolve(noise,np.ones(9)/9,mode='same')
        cue=noise*np.sin(np.pi*np.arange(n)/n)**2*1800
        pos=sec*rate;samples[pos:pos+n]+=cue[:,None]
    samples=26000*np.tanh(samples/26000)
    pcm=samples.astype('<i2');audio=OUT/'desarrollo-audio.wav'
    with wave.open(str(audio),'wb') as wav:
        wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(rate);wav.writeframes(pcm.tobytes())
    mux=run([ff,'-y','-hide_banner','-loglevel','error','-i',str(silent),'-i',str(audio),'-c:v','copy',
        '-c:a','aac','-b:a','192k','-t','60','-movflags','+faststart',str(final)],capture_output=True)
    assert mux.returncode==0,mux.stderr.decode(errors='replace')
    report=dict(result='pass',duration_seconds=60,frames=frames,fps=FPS,width=W,height=H,
        layout='Persistent left gameplay / animated right explanations',itachi_gameplay_seconds=24,
        source_video=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        source_rom_sha256=source_report['rom_sha256'],timeline=timeline,
        audio=('Stereo AAC; corresponding original gameplay music/SFX; no narration; '+
               ('synthesized transition cues' if globals().get('TRANSITION_CUES',True) else 'no added transition cues')),
        audio_rms=round(float(np.sqrt(np.mean(pcm.astype(float)**2))),1),output=str(final),
        bytes=final.stat().st_size,sha256=hashlib.sha256(final.read_bytes()).hexdigest())
    (OUT/'video-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    verify()


def verify():
    ff=style.imageio_ffmpeg.get_ffmpeg_exe();final=OUT/'golden-axe-bucle-agentico-60s.mp4'
    check=run([ff,'-hide_banner','-loglevel','error','-i',str(final),'-map','0:v:0',
        '-progress','pipe:1','-nostats','-f','null','-'],capture_output=True)
    assert check.returncode==0,check.stderr.decode(errors='replace')
    frames=[int(s.split('=',1)[1]) for s in check.stdout.decode().splitlines() if s.startswith('frame=')][-1]
    assert frames==1800,frames
    # Decode both streams to catch audio/container errors too.
    check=run([ff,'-hide_banner','-loglevel','error','-i',str(final),'-f','null','-'],capture_output=True)
    assert check.returncode==0,check.stderr.decode(errors='replace')
    sheet=Image.new('RGB',(1280,1800),BG);saved=[]
    for i in range(10):
        path=OUT/f'encoded-{i+1:02}.png';t=i*6+(4.8 if i in (6,7,9) else 3.6)
        result=run([ff,'-y','-hide_banner','-loglevel','error','-ss',str(t),'-i',str(final),
            '-frames:v','1',str(path)],capture_output=True)
        assert result.returncode==0,result.stderr.decode(errors='replace')
        with Image.open(path) as shot:
            assert shot.size==(W,H)
            sheet.paste(shot.resize((640,360),Image.Resampling.LANCZOS),(i%2*640,i//2*360))
        saved.append(path.name)
    sheet.save(OUT/'encoded-storyboard.png')
    report_path=OUT/'video-report.json';report=json.loads(report_path.read_text(encoding='utf-8'))
    report.update(encoded_frames=frames,decoder_check='pass',encoded_review_frames=saved)
    report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report),flush=True)


if __name__=='__main__':
    if '--preview' in sys.argv:preview()
    elif '--verify-only' in sys.argv:verify()
    else:main()
