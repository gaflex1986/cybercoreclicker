"""
Sound Manager with procedural audio generation.
Zero external audio files required - 100% self-contained!
"""
import math
import struct
import pygame

class SoundManager:
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._generate_sounds()
        except Exception as e:
            print(f"Audio init warning (running in silent mode): {e}")
            self.enabled = False

    def _generate_sine(self, freq=440.0, duration=0.1, volume=0.25, decay=True):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = bytearray()
        for i in range(n_samples):
            t = float(i) / sample_rate
            env = max(0.0, 1.0 - (i / n_samples)) if decay else 1.0
            val = int(32767.0 * volume * env * math.sin(2.0 * math.pi * freq * t))
            buf.extend(struct.pack('<hh', val, val))
        return pygame.mixer.Sound(buffer=bytes(buf))

    def _generate_sweep(self, start_f, end_f, duration=0.2, volume=0.25):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = bytearray()
        phase = 0.0
        for i in range(n_samples):
            t = float(i) / n_samples
            freq = start_f + (end_f - start_f) * t
            phase += 2.0 * math.pi * freq / sample_rate
            env = math.sin(math.pi * t)  # bell curve envelope
            val = int(32767.0 * volume * env * math.sin(phase))
            buf.extend(struct.pack('<hh', val, val))
        return pygame.mixer.Sound(buffer=bytes(buf))

    def _generate_chord(self, freqs, duration=0.25, volume=0.2):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = bytearray()
        for i in range(n_samples):
            t = float(i) / sample_rate
            env = max(0.0, 1.0 - (i / n_samples) ** 1.5)
            s = sum(math.sin(2.0 * math.pi * f * t) for f in freqs) / len(freqs)
            val = int(32767.0 * volume * env * s)
            buf.extend(struct.pack('<hh', val, val))
        return pygame.mixer.Sound(buffer=bytes(buf))

    def _generate_sounds(self):
        try:
            # 1. Click sound: crisp sci-fi tap
            self.sounds['click'] = self._generate_sine(freq=720, duration=0.04, volume=0.2)
            # 2. Crit sound: bright energetic zap
            self.sounds['crit'] = self._generate_chord([880, 1320, 1760], duration=0.12, volume=0.3)
            # 3. Buy sound: upbeat chime
            self.sounds['buy'] = self._generate_chord([523.25, 659.25, 783.99, 1046.50], duration=0.2, volume=0.25)
            # 4. Error sound: soft low buzz
            self.sounds['error'] = self._generate_sine(freq=160, duration=0.08, volume=0.2)
            # 5. Anomaly spawn / capture
            self.sounds['anomaly_spawn'] = self._generate_sweep(350, 900, duration=0.3, volume=0.25)
            self.sounds['anomaly_catch'] = self._generate_chord([600, 900, 1200, 1500], duration=0.35, volume=0.3)
            # 6. Hyperdrive start
            self.sounds['hyperdrive'] = self._generate_sweep(300, 1400, duration=0.5, volume=0.35)
            # 7. Achievement unlock
            self.sounds['achievement'] = self._generate_chord([440, 554, 659, 880, 1108], duration=0.45, volume=0.35)
            # 8. Donate / Cash payment sound
            self.sounds['cash'] = self._generate_chord([1046.50, 1318.51, 1567.98, 2093.0], duration=0.25, volume=0.35)
        except Exception as e:
            print(f"Error generating sounds: {e}")

    def play(self, sound_name):
        if not self.enabled:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled
