import array
import board
import math
import displayio
import time
import vectorio
from audiocore import RawSample
from audiopwmio import PWMAudioOut as AudioOut
from adafruit_display_text import label
from terminalio import FONT

black = 0x000000
white = 0xFFFFFF
display = board.DISPLAY

class Game:
    def __init__(self, audio_out):
        self.audio = audio_out
        self.audio.stop()
        self.grid = []
        for y in range(64):
            self.grid.append([])
            for x in range(96):
                self.grid[y].append(' ')
        self.tick_time = .25
        self.xpos = 47
        self.ypos = 31
        self.prev_tm = time.monotonic()
    
    def update_display(self):
        group = displayio.Group()
        palette = displayio.Palette(1)
        palette[0] = black
        rect = vectorio.Rectangle(pixel_shader=palette, \
            width=display.width + 1, height=display.height, x=0, y=0)
        group.append(rect)
        
        bitmap = displayio.OnDiskBitmap('img/life.bmp')
        img = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
        group.append(img)
        
        display.show(group)
        
    def next_generation(self):
        pass
        
    def tick(self, tm, prev_tm, r_pos, prev_r_pos, k_event):
        if r_pos != prev_r_pos:
            if r_pos < prev_r_pos:
                self.tick_time += .05
                if self.tick_time > 1:
                    self.tick_time = 1
            else:
                self.tick_time -= .05
                if self.tick_time < 0:
                    self.tick_time = 0
        if k_event:
            pass
        tm = time.monotonic()
        if tm - self.prev_tm > self.tick_time:
            self.next_generation()
            self.prev_tm = tm
        self.update_display()