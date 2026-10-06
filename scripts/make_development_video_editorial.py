"""Editorial redesign: large gameplay, warm paper, restrained typography."""
import math,sys
from PIL import Image,ImageDraw,ImageFont
import make_development_video_60s as base

PAPER='#F2EFE7';BLACK='#20211F';GRAY='#6F716B';RULE='#CAC9C1';RED='#AC3E29'
FONTS={}
CONTENT=[
    ('EL PROYECTO','Golden Axe\n× Naruto.',
     'Una hack ROM para Mega Drive. Kakashi en Konoha, con Itachi como jefe final.'),
    ('INGENIERÍA INVERSA','Entender\nel motor.',
     'Partimos de un desensamblado existente. Hay que entender rutinas, memoria y límites de la consola.'),
    ('ARQUITECTURA','Del código\na la ROM.',
     'El ensamblador reúne la lógica y los recursos. El resultado se ejecuta en un emulador.'),
    ('IMPLEMENTACIÓN','Una mejora\npor vuelta.',
     'Codex modifica código y recursos. Después compila y comprueba el cambio jugando.'),
    ('REVISIÓN VISUAL','Ver lo que\nfalla.',
     'El vídeo revela pausas, escalas e impactos que compilar sin errores no garantiza.'),
    ('ITERACIÓN','Volver\nal código.',
     'Lo que ocurre en la partida orienta la siguiente mejora.'),
    ('JEFE FINAL','Itachi.',
     'Kakashi ha caído en un genjutsu. Itachi invoca clones y ataca con cuervos y fuego.'),
    ('COMBATE','Animación\ny respuesta.',
     'El efecto, el sonido y la reacción del enemigo tienen que acompañar al golpe.'),
    ('REVISIÓN REMOTA','Revisar\na distancia.',
     'El vídeo se sube a Drive. La persona revisa la partida y devuelve indicaciones a Codex.'),
    ('ESTADO ACTUAL','Jugable.\nInacabado.',
     'Quedan errores de animación, combate y coherencia visual. La revisión humana sigue siendo necesaria.'),
]


def font(size,kind='sans',bold=False):
    key=(size,kind,bold)
    if key not in FONTS:
        filename=({'sans':('arial.ttf','arialbd.ttf'),'serif':('georgia.ttf','georgiab.ttf'),
                   'mono':('consola.ttf','consolab.ttf')}[kind][int(bold)])
        FONTS[key]=ImageFont.truetype('C:/Windows/Fonts/'+filename,size)
    return FONTS[key]


def text(d,xy,s,size=30,color=BLACK,kind='sans',bold=False):
    d.text(xy,s,font=font(size,kind,bold),fill=color,spacing=7)


def wrap(d,xy,s,width=510,size=31,color=BLACK,kind='sans',leading=43,bold=False):
    x,y=xy;line=''
    for word in s.split():
        trial=(line+' '+word).strip()
        if d.textlength(trial,font=font(size,kind,bold))>width and line:
            text(d,(x,y),line,size,color,kind,bold);y+=leading;line=word
        else:line=trial
    if line:text(d,(x,y),line,size,color,kind,bold);y+=leading
    return y


def reveal(local,delay=0):return base.ease((local-delay)/.28)


def line_item(d,y,title,sub,local,n):
    f=reveal(local,.3+n*.48)
    if f==0:return
    y+=round(8*(1-f))
    d.line((1330,y-14,1866,y-14),fill=RULE,width=1)
    text(d,(1330,y),f'{n+1:02}',25,RED,'mono')
    text(d,(1390,y-3),title,32,BLACK,'sans',True)
    if sub:wrap(d,(1390,y+43),sub,465,26,GRAY,leading=34)


def node(d,rect,title,sub='',active=False):
    x,y,r,b=rect
    d.rectangle(rect,outline=RED if active else BLACK,width=2)
    text(d,(x+18,y+15),title,28,RED if active else BLACK,'sans',True)
    if sub:text(d,(x+18,y+56),sub,23,GRAY,'mono')


def down(d,x,y,end,color=BLACK):
    d.line((x,y,x,end-8),fill=color,width=2)
    d.polygon([(x-5,end-10),(x+5,end-10),(x,end)],fill=color)


def frame(raw,row,index,local,absolute,cut_local):
    im=Image.new('RGB',(1920,1080),'#141512');d=ImageDraw.Draw(im)
    # Native aspect ratio, exact 4x pixel scale, no crop or artificial camera.
    im.paste(Image.frombytes('RGB',(320,224),raw).resize((1280,896),Image.Resampling.NEAREST),(0,92))
    text(d,(32,25),'GOLDEN AXE / KAKASHI: KONOHA',26,'#E8E8E0','mono')
    text(d,(32,1017),'KAKASHI vs ITACHI' if index>=6 else 'MEGA DRIVE / PARTIDA EN EMULADOR',24,'#D3D4CC','mono')
    text(d,(1068,1017),'v0.29',24,'#A3A69D','mono')
    d.rectangle((1280,0,1919,1079),fill=PAPER)
    d.line((1330,91,1866,91),fill=BLACK,width=2)
    text(d,(1330,45),'NOTAS DE DESARROLLO',21,GRAY,'mono')
    text(d,(1800,45),f'{index+1:02}',21,GRAY,'mono')
    eyebrow,title,body=CONTENT[index]
    offset=round(10*(1-reveal(local)))
    text(d,(1330,127+offset),eyebrow,21,RED,'mono')
    # Intro / final use a serif display face; technical pages use plain Arial.
    display='serif' if index in (0,9) else 'sans'
    text(d,(1326,185+offset),title,65 if index in (0,9) else 66,BLACK,display,True)
    body_y=377 if '\n' in title else 304
    body_end=wrap(d,(1330,body_y),body,536,31,BLACK,leading=43)
    y=max(body_end+57,590)
    if index==0:
        d.line((1330,639,1866,639),fill=BLACK,width=2)
        text(d,(1330,669),'Motor original.',40,BLACK,'serif')
        text(d,(1330,727),'Contenido nuevo.',40,BLACK,'serif')
        text(d,(1330,846),'Código 68000 / arte / sonido',23,GRAY,'mono')
    elif index==1:
        line_item(d,y,'Rutinas','Animación y colisiones',local,0)
        line_item(d,y+117,'Memoria','Estado del juego y recursos',local,1)
        line_item(d,y+234,'Consola','Tiles, sprites y audio',local,2)
    elif index==2:
        if reveal(local,.2):node(d,(1330,y,1866,y+96),'ASM 68000 + recursos','Sprites / escenario / sonido',local<2)
        if local>.6:
            down(d,1598,y+98,y+128)
            node(d,(1330,y+130,1866,y+226),'Ensamblador → ROM','Archivo ejecutable de Mega Drive',2<=local<4)
        if local>1.0:
            down(d,1598,y+228,y+258)
            node(d,(1330,y+260,1866,y+356),'Emulador','Mando / imagen / sonido',local>=4)
    elif index==3:
        line_item(d,y,'Elegir una mejora','Combate, animación o escenario',local,0)
        line_item(d,y+117,'Editar y compilar','Cambiar código y recursos',local,1)
        line_item(d,y+234,'Probar jugando','Comprobar el resultado real',local,2)
    elif index==4:
        for j,(a,b) in enumerate([('Escala','Personajes y escenario'),('Movimiento','Pausas y cambios de pose'),('Impacto','Efectos y reacción al daño')]):
            line_item(d,y+j*117,a,b,local,j)
    elif index==5:
        labels=['Código','ROM','Partida','Vídeo','Revisión']
        for j,s in enumerate(labels):
            if local<j*.34:continue
            yy=y+j*59
            text(d,(1330,yy),f'{j+1:02}',23,RED,'mono')
            text(d,(1390,yy-4),s,32,BLACK,'sans',True)
            if j<4:down(d,1750,yy+29,yy+55,GRAY)
        if local>1.7:
            d.line((1810,y+269,1847,y+269,1847,y+14,1742,y+14),fill=RED,width=2)
            d.polygon([(1742,y+14),(1751,y+9),(1751,y+19)],fill=RED)
            text(d,(1330,y+328),'Otra vuelta.',30,RED,'serif')
    elif index==6:
        text(d,(1327,552),'60',127,BLACK,'sans',True)
        text(d,(1502,650),'puntos de vida',27,GRAY)
        d.line((1330,729,1866,729),fill=BLACK,width=2)
        for j,s in enumerate(['Clones con menos vida','Cuervos','Jutsu de fuego']):
            if local>j*.5:text(d,(1330,759+j*58),s,33,BLACK)
    elif index==7:
        text(d,(1330,y),'KAKASHI',22,RED,'mono')
        text(d,(1330,y+40),'Kamui / Raikiri',38,BLACK,'sans',True)
        d.line((1330,y+112,1866,y+112),fill=RULE,width=1)
        text(d,(1330,y+149),'ITACHI',22,RED,'mono')
        wrap(d,(1330,y+189),'Clones / cuervos / fuego',530,35,BLACK,leading=43,bold=True)
        d.line((1330,y+279,1866,y+279),fill=RULE,width=1)
        text(d,(1330,y+308),'Ver, escuchar, corregir.',29,GRAY,'serif')
    elif index==8:
        for j,(a,b) in enumerate([('Codex','Modifica, juega y graba'),('Drive','Vídeo para la revisión remota'),('La persona','Devuelve nuevas instrucciones')]):
            if local<j*.4:continue
            yy=y+j*121
            node(d,(1330,yy,1866,yy+94),a,b,min(2,int(local/2))==j)
            if j<2:down(d,1598,yy+96,yy+119,GRAY)
    elif index==9:
        d.line((1330,662,1866,662),fill=BLACK,width=2)
        text(d,(1330,693),'Más autonomía.',39,BLACK,'serif')
        text(d,(1330,750),'Todavía hace falta',36,BLACK,'serif')
        text(d,(1330,798),'criterio.',54,RED,'serif')
    # Small editorial folio; no countdown, neon bars or decorative UI.
    d.line((1330,984,1866,984),fill=RULE,width=1)
    d.line((1330,984,1330+round(536*min(local/6,1)),984),fill=RED,width=2)
    text(d,(1330,1014),'Un experimento con Codex',20,GRAY,'mono')
    return im


if __name__=='__main__':
    base.OUT=base.ROOT/'build/videos/desarrollo-60s-editorial'
    base.frame=frame
    base.TRANSITION_CUES=False
    if '--preview' in sys.argv:base.preview()
    elif '--verify-only' in sys.argv:base.verify()
    else:base.main()
