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

class Game:
    def __init__(self, audio_out):
        self.audio = audio_out
        self.audio.stop()
        
    def tick(self, tm, prev_tm, r_pos, prev_r_pos, k_event):
        pass
