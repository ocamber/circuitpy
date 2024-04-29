import audiocore
import board
import displayio
import vectorio
import usb_hid
from adafruit_hid.keycode import Keycode
from adafruit_display_text import label
from audiopwmio import PWMAudioOut as AudioOut
from terminalio import FONT

black = 0x000000
white = 0xFFFFFF
display = board.DISPLAY
key_map = [
    7,8,9,
    4,5,6,
    1,2,3,
    0]
shifted_map = [
    '/', '^', 'C',
    'X', '',  'S',
    '-', '',  'E',
    '+', '',  '']
error_sound = audiocore.WaveFile(open('boop.wav','rb'))

def display_group():
    group = displayio.Group()
    palette = displayio.Palette(1)
    palette[0] = black
    rect = vectorio.Rectangle(pixel_shader=palette, \
        width=display.width + 1, height=display.height, x=0, y=0)
    group.append(rect)
    
    bitmap = displayio.OnDiskBitmap('img/calc.bmp')
    img = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
    group.append(img)
    return group

class Calc:
    def __init__(self, audio):
        self.audio = audio
        self.val = ['','','','']
        self.op = ['','']
        self.result = ''
        self.is_shifted = False
        self.last_k = -1
        
    def last_key(self):
        return self.last_k
        
    def result_keys(self):
        r = []
        for c in self.result:
            if c=='-':
                r.append(Keycode.MINUS)
            elif c=='.':
                r.append(Keycode.PERIOD)
            elif c=='0':
                r.append(Keycode.ZERO)
            elif c=='1':
                r.append(Keycode.ONE)
            elif c=='2':
                r.append(Keycode.TWO)
            elif c=='3':
                r.append(Keycode.THREE)
            elif c=='4':
                r.append(Keycode.FOUR)
            elif c=='5':
                r.append(Keycode.FIVE)
            elif c=='6':
                r.append(Keycode.SIX)
            elif c=='7':
                r.append(Keycode.SEVEN)
            elif c=='8':
                r.append(Keycode.EIGHT)
            elif c=='9':
                r.append(Keycode.NINE)
        return r
        
    def display_legend(self):
        group = display_group()
        y = 8
        for ln in ['/      ^      C', 'X           +/-', '-            CE', '+']:
            img = label.Label(FONT, text=ln, color=white)
            img.x = 34
            img.y = y
            group.append(img)
            y += 16
        display.show(group)
    
    def display_values(self):
        group = display_group()
        txt = ' '
        self.result = '0'
        r = 0
        for i in range(4):
            if self.result=='ERR':
                pass
            elif i==0:
                try:
                    r = float(self.val[0])
                except:
                    self.result = 'ERROR'
            elif i<3:
                v = self.val[i]
                o = self.op[i-1]
                if v:
                    try:
                        if o=='+':
                            r += float(v)
                        elif o=='-':
                            r -= float(v)
                        elif o=='X':
                            r *= float(v)
                        elif o=='/':
                            r /= float(v)
                        elif o=='^':
                            r = r ** float(v)
                    except:
                        self.result = 'ERROR'
            if i==0 or i == 3:
                o = ' '
            else:
                o = self.op[i-1]
            v = '                    '
            if i==3:
                if self.result != 'ERROR':
                    try:
                        self.result = str(float(r))
                    except:
                        self.result = 'ERROR'
                v += self.result
                v = v[-19:]
                o = '='
            else:
                v += self.val[i]
                v = v[-15:]
            img = label.Label(FONT, text= o+v, color=white)
            if i==3:
                img.x=2
            else:
                img.x=26
            img.y=8 + i*16
            group.append(img)
        display.show(group)
        
    def add_char(self, k):
        v = self.val[0]
        if self.op[1]:
            v = self.val[2]
        elif self.op[0]:
            v = self.val[1]
        if k==10:
            v = v.replace('.','') + '.'
        else:
            v += str(key_map[k])
        try:
            test_v = float(v)
        except:
            self.audio.play(error_sound)
            return
        if self.op[1]:
            self.val[2] = v
        elif self.op[0]:
            self.val[1] = v
        else:
            self.val[0] = v
    
    def tick(self, r_pos, prev_r_pos, k_event):
        if r_pos != prev_r_pos:
            if r_pos<prev_r_pos:
                pass
            else:
                pass

        if k_event:
            k = k_event.key_number
            if k_event.pressed:
                self.last_k = k
                if k==11:
                    self.is_shifted = True
                    self.display_legend()
            else:
                if k==11:
                    self.is_shifted = False
                    self.last_k = -1
                    self.display_values()
                    return
                
                if not self.is_shifted:
                    self.add_char(k)
                    self.display_values()
                    return
                
                o = shifted_map[k]
                if not o:
                    self.audio.play(error_sound)
                    return
                i = 0
                if self.op[1]:
                    i = 2
                elif self.op[0]:
                    i = 1
                if o == 'S':
                    if self.val[i].startswith('-'):
                        self.val[i] = self.val[i][1:]
                    else:
                        self.val[i] = '-' + self.val[i]
                elif o=='E':
                    self.val[i] = ''
                elif o=='C':
                    for i in (0,1):
                        self.op[i] = ''
                        self.val[i] = ''
                    self.val[2] = ''
                elif i>1:
                    try:
                        op = self.op[0]
                        r = float(self.val[0])
                        v = float(self.val[1])
                        if op=='+':
                            r += float(v)
                        elif op=='-':
                            r -= float(v)
                        elif op=='X':
                            r *= float(v)
                        elif op=='/':
                            r /= float(v)
                        elif op=='^':
                            r = r ** float(v)
                        self.val[0] = str(r)
                        self.op[0] = self.op[1]
                        self.val[1] = self.val[2]
                        self.op[1] = o
                        self.val[2] = ''
                    except:
                        self.audio.play(error_sound)
                elif self.val[i]:
                    self.op[i] = o
                else:
                    self.audio.play(error_sound)
                self.display_values()
