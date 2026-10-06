import sys,subprocess,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
root=Path.cwd();sys.path.insert(0,str(root/'tools/video-python'));import imageio_ffmpeg
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--version',default='0.16');parser.add_argument('--preview',action='store_true')
options=parser.parse_args();version=options.version;short='v'+version.replace('0.','')
ff=imageio_ffmpeg.get_ffmpeg_exe()
video=root/'build/videos'/f"kakashi-konoha-v{version}-{'estado-actual' if options.preview else 'partida'}.mp4"
report_path=root/'build/videos'/f"recording-v{version}{'-preview' if options.preview else ''}.json"
report=json.loads(report_path.read_text())
duration=report['duration_seconds']
first={}
for event in report['jutsu_events']:first.setdefault(event['jutsu'],event['seconds'])
times=[11]+[t+.55 for t in first.values()]+[min(147,duration-6),duration-3]
assert len(times)==10,times
extra={'intro','walk','phase','resume','contact'}
if report.get('movement_showcase_seconds') is not None:extra.add('run')
expected={f'review-{short}-{t:.1f}.png' for t in times}|{f'review-{short}-{name}.png' for name in extra}
for path in (root/'build/videos').glob(f'review-{short}-*.png'):
 if path.name not in expected:path.unlink()
frames=[]
for t in times:
 path=root/f'build/videos/review-{short}-{t:.1f}.png'
 p=subprocess.run([ff,'-y','-hide_banner','-loglevel','error','-ss',str(t),'-i',str(video),'-frames:v','1',str(path)],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=20)
 assert p.returncode==0,p.stderr
 assert path.exists(),('Frame outside the recording',t,duration)
 frames.append((t,path))
sheet=Image.new('RGB',(1920,5*710),'#152233');draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
for i,(t,path) in enumerate(frames):
 x=i%2*960;y=i//2*710;draw.text((x+10,y+5),f'v{version} · {t:.1f}s',fill='#f4ddad',font=font);sheet.paste(Image.open(path),(x,y+38))
sheet.save(root/f'build/videos/review-{short}-contact.png')
print('10 frames extracted from actual encoded recording')
pages={row['page']:row['seconds'] for row in report.get('story_pages',[])}
if 0 in pages and 2 in pages and 7 in pages:
 for name,t in {'intro':pages[0]+1.4,'walk':pages[2]+3.25,
                'phase':pages[7]+1.4,'resume':pages[7]+2.9}.items():
  path=root/f'build/videos/review-{short}-{name}.png'
  p=subprocess.run([ff,'-y','-hide_banner','-loglevel','error','-ss',str(t),'-i',str(video),'-frames:v','1',str(path)],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=20)
  assert p.returncode==0 and path.exists(),(name,t,p.stderr)
 print('4 dialogue and movement frames extracted from the same encoded take')
if report.get('movement_showcase_seconds') is not None:
 t=report['movement_showcase_seconds']+1.3
 path=root/f'build/videos/review-{short}-run.png'
 p=subprocess.run([ff,'-y','-hide_banner','-loglevel','error','-ss',str(t),'-i',str(video),'-frames:v','1',str(path)],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=20)
 assert p.returncode==0 and path.exists(),('Native running frame',t,p.stderr)
 print('1 native double-tap running frame extracted from the same encoded take')
