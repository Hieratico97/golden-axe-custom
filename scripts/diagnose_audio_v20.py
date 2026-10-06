import sys,ctypes as C
from emulate import Emulator,ROOT
from playtest import start_game,fight_keys
for tag,path in [('v19',ROOT/'build/v0.19-backup/golden-axe.bin'),('v20',ROOT/'build/custom/golden-axe.bin')]:
 em=Emulator(path,capture_audio=True)
 try:
  start_game(em)
  for frame in range(1200):
   em.run(1,fight_keys(em))
   if not any(em.byte(s)&128 and em.byte(s+0x64)>0 for s in (0xD100,0xD180,0xD200)):break
  em.run(150)
  em.core.retro_serialize_size.restype=C.c_size_t
  em.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t]
  size=em.core.retro_serialize_size();buf=C.create_string_buffer(size);assert em.core.retro_serialize(buf,size)
  rom=path.read_bytes();sig=rom[0x1D2F0+8:0x1D2F0+64];pos=buf.raw.find(sig)
  print(tag,'z80',pos,'head',buf.raw[pos-8:pos+56].hex(),'rom',rom[0x1D2F0:0x1D2F0+64].hex())
  for _ in range(5):
   print(tag, 'frame',frame,'scene',em.word(0xF300),'music',em.word(0xF310),'volumes',[em.byte(0xF31C+i) for i in range(4)],'duck',em.word(0xF320),'sfx',em.word(0xF246),em.word(0xF244),'landings',em.word(0xF3D2),'scorepointer',hex((em.word(0xF308)<<16)|em.word(0xF30A)))
   em.run(240)
 finally:em.close()
