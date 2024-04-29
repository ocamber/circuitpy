import board
import array
import math
import displayio
import vectorio
from audiocore import RawSample
from audiopwmio import PWMAudioOut as AudioOut
from adafruit_display_text import label
from terminalio import FONT

black = 0x000000
white = 0xFFFFFF
display = board.DISPLAY

def raw_sample(frequency, vol):
    length = 8000 // frequency
    sine_wave = array.array("H", [0] * length)
    for i in range(length):
        sine_wave[i] = int((1 + math.sin(math.pi * 2 * i / length)) * vol * (2 ** 15 - 1))
    return RawSample(sine_wave)

class Game:
    def __init__(self, audio_out):
        self.audio = audio_out
        self.audio.stop()
        self.volume = 0.85
        self.tone = [196, 220, 247, 262, 294, 330, 370, 392, 415]
    
    def legend(self):
        group = displayio.Group()
        palette = displayio.Palette(1)
        palette[0] = black
        rect = vectorio.Rectangle(pixel_shader=palette, \
            width=display.width + 1, height=display.height, x=0, y=0)
        group.append(rect)
        
        bitmap = displayio.OnDiskBitmap('img/gclef.bmp')
        img = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
        group.append(img)
        
        palette = displayio.Palette(1)
        palette[0] = white
        h = int(self.volume*20)
        rect = vectorio.Rectangle(pixel_shader=palette, \
            width=3, height=h, x=0, y=64-h)
        group.append(rect)
    
        y = 8
        for ln in ['G    A    B', 'C    D    E', 'F#   G    Ab', '         EXIT']:
            img = label.Label(FONT, text=ln, color=white)
            img.x = 38
            img.y = y
            group.append(img)
            y += 16
            
        display.show(group)

    def tick(self, tm, prev_tm, r_pos, prev_r_pos, k_event):
        if r_pos != prev_r_pos:
            if r_pos < prev_r_pos:
                self.volume += .1
                if self.volume > .95:
                    self.volume = .95
            else:
                self.volume -= .1
                if self.volume < .35:
                    self.volume = .35
            self.legend()
    
        if k_event:
            self.legend()
            if k_event.pressed:
                if k_event.key_number<9:
                    self.audio.play(raw_sample(self.tone[k_event.key_number], self.volume), loop=True)
            else:
                self.audio.stop()
