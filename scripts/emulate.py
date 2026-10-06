"""Small libretro frontend for reproducible input, RAM inspection and screenshots."""
import ctypes as C
from pathlib import Path
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


class GameInfo(C.Structure):
    _fields_ = [('path', C.c_char_p), ('data', C.c_void_p), ('size', C.c_size_t), ('meta', C.c_char_p)]


class Variable(C.Structure):
    _fields_ = [('key', C.c_char_p), ('value', C.c_char_p)]


class Emulator:
    def __init__(self, path, capture_audio=False):
        self.core = C.CDLL(str(ROOT / 'tools/libretro/genesis_plus_gx_libretro.dll'))
        self.audio = []
        self.capture_audio = capture_audio
        self.keys = set()
        self.frame = None
        self.pixel_format = 0
        self.variables = {}
        self.directory = str(ROOT / 'build').encode()
        ENV = C.CFUNCTYPE(C.c_bool, C.c_uint, C.c_void_p)
        VIDEO = C.CFUNCTYPE(None, C.c_void_p, C.c_uint, C.c_uint, C.c_size_t)
        AUDIO = C.CFUNCTYPE(None, C.c_int16, C.c_int16)
        BATCH = C.CFUNCTYPE(C.c_size_t, C.c_void_p, C.c_size_t)
        POLL = C.CFUNCTYPE(None)
        INPUT = C.CFUNCTYPE(C.c_int16, C.c_uint, C.c_uint, C.c_uint, C.c_uint)

        def env(cmd, data):
            cmd &= ~0x10000
            if cmd == 10:
                self.pixel_format = C.cast(data, C.POINTER(C.c_int))[0]
                return True
            if cmd in (9, 30, 31):
                C.cast(data, C.POINTER(C.c_char_p))[0] = self.directory
                return True
            if cmd == 16:
                entries = C.cast(data, C.POINTER(Variable))
                i = 0
                while entries[i].key:
                    self.variables[entries[i].key] = entries[i].value.split(b'; ', 1)[-1].split(b'|')[0]
                    i += 1
                return True
            if cmd == 15:
                entry = C.cast(data, C.POINTER(Variable))[0]
                entry.value = self.variables.get(entry.key)
                return bool(entry.value)
            if cmd == 17:
                C.cast(data, C.POINTER(C.c_bool))[0] = False
                return True
            if cmd in (18, 35, 36):
                return False
            return False

        def video(data, w, h, pitch):
            if not data:
                return
            raw = C.string_at(data, pitch * h)
            if self.pixel_format == 1:
                self.frame = Image.frombytes('RGB', (w, h), raw, 'raw', 'BGRX', pitch)
            else:
                # RGB565 is the default format requested by Genesis Plus GX.
                a = np.frombuffer(raw, dtype='<u2').reshape(h, pitch//2)[:, :w]
                shift, mask = (11, 63) if self.pixel_format == 2 else (10, 31)
                rgb = np.stack((((a>>shift)&31)*255//31, ((a>>5)&mask)*255//mask, (a&31)*255//31), axis=-1).astype('uint8')
                self.frame = Image.fromarray(rgb)

        def audio_batch(data, size):
            if self.capture_audio:
                self.audio.append(C.string_at(data, size*4))
            return size
        self.callbacks = [ENV(env), VIDEO(video), AUDIO(lambda l, r: None),
                          BATCH(audio_batch), POLL(lambda: None),
                          INPUT(lambda port, device, index, button: int(port == 0 and button in self.keys))]
        setters = ['environment', 'video_refresh', 'audio_sample', 'audio_sample_batch', 'input_poll', 'input_state']
        for name, callback in zip(setters, self.callbacks):
            getattr(self.core, 'retro_set_' + name)(callback)
        self.core.retro_init()
        self.core.retro_set_controller_port_device(0, 1)
        self.core.retro_set_controller_port_device(1, 0)
        rom = Path(path).read_bytes()
        self.rom = C.create_string_buffer(rom)
        info = GameInfo(str(path).encode(), C.cast(self.rom, C.c_void_p), len(rom), None)
        self.core.retro_load_game.argtypes = [C.POINTER(GameInfo)]
        self.core.retro_load_game.restype = C.c_bool
        if not self.core.retro_load_game(C.byref(info)):
            raise RuntimeError('Could not load ROM')
        self.core.retro_get_memory_data.argtypes = [C.c_uint]
        self.core.retro_get_memory_data.restype = C.c_void_p
        self.core.retro_get_memory_size.argtypes = [C.c_uint]
        self.core.retro_get_memory_size.restype = C.c_size_t
        ptr = self.core.retro_get_memory_data(2)
        self.ram = (C.c_ubyte * self.core.retro_get_memory_size(2)).from_address(ptr)

    def run(self, frames, keys=()):
        self.keys = set(keys)
        for _ in range(frames):
            self.core.retro_run()

    def byte(self, address):
        return self.ram[(address & 65535) ^ 1]

    def word(self, address):
        return (self.byte(address) << 8) | self.byte(address + 1)

    def set_byte(self, address, value):
        self.ram[(address & 65535) ^ 1] = value

    def set_word(self, address, value):
        self.set_byte(address, value >> 8)
        self.set_byte(address + 1, value & 255)

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.frame.save(path)

    def save_audio(self, path):
        import wave
        class Geometry(C.Structure):
            _fields_=[('base_width',C.c_uint),('base_height',C.c_uint),('max_width',C.c_uint),('max_height',C.c_uint),('aspect',C.c_float)]
        class Timing(C.Structure):
            _fields_=[('fps',C.c_double),('sample_rate',C.c_double)]
        class AV(C.Structure):
            _fields_=[('geometry',Geometry),('timing',Timing)]
        av=AV();self.core.retro_get_system_av_info(C.byref(av))
        with wave.open(str(path),'wb') as wav:
            wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(round(av.timing.sample_rate))
            wav.writeframes(b''.join(self.audio))

    def close(self):
        self.core.retro_unload_game()
        self.core.retro_deinit()


if __name__ == '__main__':
    import sys
    em = Emulator(ROOT / 'build/baseline/golden-axe.bin')
    for i in range(8):
        em.run(120)
        em.run(1, [3])
        print(i, hex(em.word(0xC172)), hex(em.word(0xC104)), hex(em.word(0xD000)))
        em.save(ROOT / f'build/checks/baseline-{i}.png')
    em.close()
