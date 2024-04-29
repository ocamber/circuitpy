import array
import board
import math
import time
import keypad
import audiocore
import displayio
import digitalio
import vectorio
import rotaryio
import usb_hid
from adafruit_display_text import label
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from terminalio import FONT
from audiopwmio import PWMAudioOut as AudioOut
import neopixel
import calculator
import game_pong
import game_breakout
import game_spacewar
import game_life
import game_music
import game_spaceinvaders

cc = ConsumerControl(usb_hid.devices)
kbd = Keyboard(usb_hid.devices)
kbd_mode = 0
calc = None
game = None
black = 0x000000
white = 0xFFFFFF

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = True

button = digitalio.DigitalInOut(board.BUTTON)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

encoder = rotaryio.IncrementalEncoder(board.ROTA, board.ROTB)

display = board.DISPLAY

button_pressed = False
cursor_mode = False
cursor_mode_used = False
shift_mode = False
shift_mode_used = False

keys = keypad.Keys((
    board.KEY1, board.KEY2, board.KEY3,
    board.KEY4, board.KEY5, board.KEY6,
    board.KEY7, board.KEY8, board.KEY9,
    board.KEY10, board.KEY11, board.KEY12,
    ), value_when_pressed=False, pull=True)

RED = (200, 0, 0)
YELLOW = (130, 130, 00)
ORANGE = (190, 80, 0)
GREEN = (0, 200, 0)
CYAN = (0, 130, 130)
BLUE = (0, 0, 200)
PURPLE = (130, 0, 130)
GREY = (100, 100, 100)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

game_song = audiocore.WaveFile(open('StreetChicken.wav','rb'))
pin = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
pin.direction = digitalio.Direction.OUTPUT
pin.value = True
audio = AudioOut(board.SPEAKER)

key_code = [[
    Keycode.SEVEN, Keycode.EIGHT, Keycode.NINE,
    Keycode.FOUR, Keycode.FIVE, Keycode.SIX,
    Keycode.ONE, Keycode.TWO, Keycode.THREE,
    Keycode.ZERO
    ], [
    Keycode.HOME, Keycode.UP_ARROW, Keycode.PAGE_UP,
    Keycode.LEFT_ARROW, [Keycode.LEFT_BRACKET, Keycode.RIGHT_BRACKET], Keycode.RIGHT_ARROW,
    Keycode.END, Keycode.DOWN_ARROW, Keycode.PAGE_DOWN,
    [-Keycode.SHIFT, Keycode.NINE, Keycode.ZERO]
    ], [
    [-Keycode.SHIFT, Keycode.SEVEN], [-Keycode.SHIFT, Keycode.EIGHT], [-Keycode.SHIFT, Keycode.NINE, Keycode.ZERO],
    [-Keycode.SHIFT, Keycode.FOUR], [-Keycode.SHIFT, Keycode.FIVE], Keycode.BACKSLASH,
    [-Keycode.SHIFT, Keycode.ONE], [-Keycode.SHIFT, Keycode.TWO], [-Keycode.SHIFT, Keycode.THREE],
    [Keycode.LEFT_BRACKET, Keycode.RIGHT_BRACKET]]]

calc_mode = len(key_code)

key_legend = [[
    ' 7 &  8 *  9 (',
    ' 4 $  5 %  6 ^',
    ' 1 !  2 @  3 #',
    ' 0 )'
    ], [
    'Home  Up   PgUp',
    'Left  []   Rght',
    'End   Dwn  PgDn',
    '()'
    ], [
    '  &    *    ()',
    '  $    %    \\',
    '  !    @    #',
    '  []'
    ], [
    '7 /   8 ^  9 CE',
    '4 X   5    6',
    '1 -   2    3 C',
    '0 +'
    ], [
    ' Png  Brk  SpW',
    ' Lif  Mus  SpI',
    '',
    '']]

key_color = [[
    ORANGE, ORANGE, ORANGE,
    ORANGE, ORANGE, ORANGE,
    ORANGE, ORANGE, ORANGE,
    ORANGE
    ] , [
    BLUE, GREEN, CYAN,
    GREEN, ORANGE, GREEN,
    BLUE, GREEN, CYAN,
    ORANGE
    ] , [
    BLUE, BLUE, ORANGE,
    BLUE, BLUE, BLUE,
    BLUE, BLUE, BLUE,
    ORANGE
    ], [
    GREEN, GREEN, GREEN,
    GREEN, GREEN, GREEN,
    GREEN, GREEN, GREEN,
    GREEN
    ], [
    ORANGE, YELLOW, GREEN,
    CYAN, BLUE, PURPLE,
    RED, ORANGE, YELLOW,
    GREEN]]

pixels = neopixel.NeoPixel(board.NEOPIXEL, 12, brightness=.3, auto_write=True)

def add_background(group, color):
    # Set the palette for the background color
    back_palette = displayio.Palette(1)
    back_palette[0] = color
    background_rect = vectorio.Rectangle(pixel_shader=back_palette, \
        width=display.width + 1, height=display.height, x=0, y=0)
    group.append(background_rect)

def fetch_image(img_str):
    if not img_str:
        return None
    if len(img_str)<1:
        return None
    attr = None
    if img_str[:1]=='[':
        p = img_str.find(']',1,10)
        if p>0:
            attr = img_str[1:p].split(',')
            img_str = img_str[p+1:]
    bitmap = displayio.OnDiskBitmap(img_str)
    img = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
    if attr:
        img.x = int(attr[0])
        img.y = int(attr[1])
    return img

def strip_coord(text):
    if not text:
        return None
    if len(text)<2:
        return text
    if not text[:1]=='[':
        return text
    p = text.find(']',1,10)
    if p<2:
        return text
    return text[p+1:]

def make_label(text, scale=None):
    if not text:
        return None
    attr = None
    if text[:1]=='[':
        p = text.find(']',1,10)
        if p>0:
            attr = text[1:p].split(',')
            text = text[p+1:]
    if len(text)<1:
        return None
    if scale:
        img = label.Label(FONT, text=text, color=black, scale=scale)
    else:
        img = label.Label(FONT, text=text, color=black)
    if attr:
        img.x = int(attr[0])
        img.y = int(attr[1])
    return img

def set_key_color():
    pixels.auto_write = False
    i = 0
    for color in key_color[kbd_mode]:
        pixels[i] = color
        i += 1
    pixels.show()
    pixels.auto_write = True

def set_key_legend():
    group = displayio.Group()
    add_background(group, black)
    img = None
    if kbd_mode==calc_mode:
        img = fetch_image('img/calc.bmp')
    elif kbd_mode>calc_mode:
        img = fetch_image('img/game.bmp')
    else:
        img = fetch_image('img/atlad-logo.bmp')
    group.append(img)
    if cursor_mode:
        img = label.Label(FONT, text='CRSR', color=white)
        img.y = 40
        group.append(img)
    if shift_mode:
        img = label.Label(FONT, text='SHFT', color=white)
        img.y = 56
        group.append(img)
    i = 0
    for ln in key_legend[1 if cursor_mode else kbd_mode]:
        img = label.Label(FONT, text=ln, color=white)
        img.x = 38
        img.y = 8 + i*16
        group.append(img)
        i += 1
    display.show(group)

for klist in key_code:
    while len(klist)<12:
        klist.append(0)
    klist[10] = Keycode.KEYPAD_PERIOD
    klist[11] = Keycode.KEYPAD_ENTER
for klist in key_color:
    while len(klist)<12:
        klist.append(black)
    klist[10] = GREY
    klist[11] = RED
ki = 0
kn = len(key_legend)-1
for klist in key_legend:
    i = 0
    n = len(klist)
    while i<n:
        kleg = klist[i] + '                '
        if i<n-1:
            klist[i] = kleg[:16]
        else:
            klist[i] = kleg[:6] + ' .   ' + ('E-SH' if ki<kn else 'EXIT')
        i += 1
    ki += 1
set_key_color()
set_key_legend()

button_pressed = False
k_event = None
tm = time.monotonic()
led_tm = tm
prev_tm = tm
r_pos = encoder.position
prev_r_pos = r_pos

while True:
    prev_tm = tm
    prev_r_pos = r_pos
    
    if not button_pressed and not button.value:
        button_pressed = True
        continue
    
    if button.value and button_pressed:
        audio.stop()
        shift_mode = None
        cursor_mode = None
        game = None
        calc = None
        kbd_mode += 1
        kbd_mode %= len(key_legend)
        set_key_color()
        set_key_legend()
        button_pressed = False
        if kbd_mode>calc_mode:
            audio.play(game_song)
        elif kbd_mode==calc_mode:
            calc = calculator.Calc(audio)
        continue
    
    time.sleep(.001)
    if tm-led_tm > .5:
        led_tm = tm
        led.value = not led.value
        if kbd_mode>calc_mode:
            pixels.auto_write = False
            pColor = pixels[0]
            i = 0
            while i<9:
                pixels[i]=pixels[i+1]
                i += 1
            pixels[9] = pColor
            pixels.show()
            pixels.auto_write = True

    if not k_event:
        k_event = keys.events.get()

    if k_event:
        k_num = k_event.key_number
        if k_event.pressed:
            pixels[k_num] = WHITE
        elif kbd_mode<len(key_color):
            pixels[k_num] = key_color[kbd_mode][k_num]
        else:
            pixels[k_num] = BLACK
            
    tm = time.monotonic()
    r_pos = encoder.position

    if calc:
        if k_event:
            if k_event.key_number==11 and calc.last_key()==11 and not k_event.pressed:
                for k in calc.result_keys():
                    kbd.press(k)
                    kbd.release(k)
            calc.tick(r_pos, prev_r_pos, k_event)
        k_event = None
        prev_r_pos = r_pos
        continue

    if kbd_mode>calc_mode:
        if k_event:
            if not k_event.pressed:
                if k_event.key_number==11:
                    game = None
                    set_key_legend()
                elif game:
                    pass
                elif k_event.key_number==0:
                    game = game_pong.Game(audio)
                elif k_event.key_number==1:
                    game = game_breakout.Game(audio)
                elif k_event.key_number==2:
                    game = game_spacewar.Game(audio)
                elif k_event.key_number==3:
                    game = game_life.Game(audio)
                elif k_event.key_number==4:
                    game = game_music.Game(audio)
                elif k_event.key_number==5:
                    game = game_spaceinvaders.Game(audio)
        if game:
            game.tick(tm, prev_tm, r_pos, prev_r_pos, k_event)
        k_event = None
        prev_r_pos = r_pos
        continue
    
    if r_pos != prev_r_pos:
        if kbd_mode == 1:
            if r_pos<prev_r_pos:
                cc.send(ConsumerControlCode.VOLUME_INCREMENT)
            else:
                cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        else:
            if r_pos<prev_r_pos:
                cc.send(ConsumerControlCode.BRIGHTNESS_INCREMENT)
            else:
                cc.send(ConsumerControlCode.BRIGHTNESS_DECREMENT)
        prev_r_pos = r_pos
        
    if k_event:
        # normal keyboard
        if cursor_mode:
            k = key_code[1] [k_num]
        else:
            k = key_code[kbd_mode] [k_num]
        if k_event.pressed:
            active_mods = []
            if k_num==10:
                cursor_mode = time.monotonic()
                cursor_mode_used = False
            elif k_num==11:
                shift_mode = time.monotonic()
                shift_mode_used = False
                kbd.press(Keycode.SHIFT)
            elif cursor_mode:
                pass
            elif isinstance(k, list):
                pass
            else:
                kbd.press(k)
        else:
            if k_num==10:
                if cursor_mode:
                    if time.monotonic()-cursor_mode<.3 and not cursor_mode_used:
                        kbd.press(Keycode.KEYPAD_PERIOD)
                        kbd.release(Keycode.KEYPAD_PERIOD)
                cursor_mode = False
                cursor_mode_used = False
            elif k_num==11:
                kbd.release(Keycode.SHIFT)
                if shift_mode:
                    if time.monotonic()-shift_mode<.3 and not shift_mode_used:
                        kbd.press(Keycode.KEYPAD_ENTER)
                        kbd.release(Keycode.KEYPAD_ENTER)
                shift_mode = False
                shift_mode_used = False
            elif cursor_mode:
                kbd.press(k)
                kbd.release(k)
                cursor_mode_used = True
            elif isinstance(k, list):
                active_mods = []
                for kitem in k:
                    if shift_mode and abs(kitem) in [Keycode.SHIFT, Keycode.RIGHT_SHIFT]:
                        pass
                    elif kitem < 0:
                        if not -kitem in active_mods:
                            active_mods.insert(0, -kitem)
                            kbd.press(-kitem)
                    else:
                        if kitem in active_mods:
                            active_mods.remove(kitem)
                            kbd.release(kitem)
                        else:
                            kbd.press(kitem)
                            kbd.release(kitem)
                for kitem in active_mods:
                    kbd.release(kitem)
                if shift_mode:
                    shift_mode_used = True
            else:
                kbd.release(k)
                if shift_mode:
                    shift_mode_used = True
            active_mods = []
        set_key_legend()
        k_event = None
