import board
import time
import array
import keypad
import busio
import digitalio
import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import random
import neopixel

DARK_RED = (25,0,0)
RED = (50, 0, 0)
ORANGE = (40, 15, 0)
YELLOW = (25, 20, 00)
GREEN = (0, 50, 0)
CYAN = (0, 25, 25)
BLUE = (0, 0, 50)
PURPLE = (25,0, 10)
VIOLET = (30, 5, 40)
WHITE = (255, 255, 255)
BLACK = (0,0,0)
RAINBOW = (BLACK, RED, ORANGE, YELLOW, GREEN, BLUE, VIOLET)

CAPS_LED = False
SCROLL_LED = True
caps_on = False
scroll_on = False

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=.5, auto_write=True)
pixel[0] = CYAN
glow_pixel = neopixel.NeoPixel(board.D2, 7, brightness=.7, auto_write=True)
glow_pixel.fill(BLACK)
glow_pixel[0] = YELLOW
glow_mode = 0
glow_delta = -1
glow_interval = .2
cc = None
usb = None
kb_layer = 0
delayed_k = None
SCROLL_LED_OFF = 237
SCROLL_LED_ON = 238
CAPS_LED_OFF = 239
CAPS_LED_ON = 240
KEY_PRESSED = 241
KEY_RELEASED = 242
GLOW_OFF = 243
GLOW_ON = 244
key_pressed = True

uart = busio.UART(board.TX, board.RX, baudrate=115200, timeout=0)

random.seed(int(time.monotonic()*100000))

# check for USB
try:
    cc = ConsumerControl(usb_hid.devices)
    usb = Keyboard(usb_hid.devices)
    pixel[0] = YELLOW
except:
    pixel[0] = BLUE

key_matrix = keypad.KeyMatrix(
    row_pins=(board.A3, board.D6, board.D7, board.D8),
    column_pins=(board.A2, board.A1, board.A0, board.SCK, board.MISO, board.MOSI, board.D10),
    columns_to_anodes=True,
)

left_keys = 6
right_keys = 7

kc = Keycode
key_code = [[
    kc.ESCAPE,    kc.Q,   kc.W,      kc.E,   kc.R,    kc.T,       kc.Y,     kc.U,   kc.I,   kc.O,        kc.P,          kc.MINUS,   kc.BACKSPACE,
    kc.TAB,       kc.A,   kc.S,      kc.D,   kc.F,    kc.G,       kc.H,     kc.J,   kc.K,   kc.L,        kc.SEMICOLON,  None,       kc.QUOTE,
    kc.CAPS_LOCK, kc.Z,   kc.X,      kc.C,   kc.V,    kc.B,       kc.N,     None,   kc.M,   kc.COMMA,    kc.PERIOD, kc.FORWARD_SLASH, kc.RIGHT_SHIFT,
    kc.CONTROL,  kc.ALT, kc.WINDOWS, None,  kc.SPACE, None,       kc.SPACE, None,   None,kc.LEFT_BRACKET, kc.EQUALS, kc.RIGHT_BRACKET, kc.ENTER
    ], [
    kc.GRAVE_ACCENT,kc.ONE,kc.TWO, kc.THREE, kc.FOUR, kc.FIVE,    kc.SIX, kc.SEVEN, kc.EIGHT, kc.NINE,   kc.ZERO,       kc.MINUS,   kc.DELETE,
    kc.TAB,       None,   None,      None,   None,    None,       kc.H,     kc.J,   kc.K,   kc.L,        kc.SEMICOLON,  None,       kc.QUOTE,
    kc.CAPS_LOCK, None,   None,      None,   None,    None,       kc.N,     None,   kc.M,   kc.COMMA,    kc.PERIOD,  kc.BACKSLASH,   kc.RIGHT_SHIFT,
    kc.CONTROL,   kc.ALT, kc.WINDOWS,None,  kc.SPACE, None,       kc.SPACE, None,   None,kc.APPLICATION, kc.EQUALS,   kc.RIGHT_BRACKET, kc.ENTER
    ], [
    kc.ESCAPE,    kc.F1,  kc.F2,     kc.F3,  kc.F4,   kc.F5,      kc.F6,    kc.F7,  kc.F8,  kc.F9,       kc.F10,        kc.F11,     kc.F12,
    kc.TAB,       None,   None,      None,   None,    kc.G,       kc.H,     kc.J,   kc.K,   kc.L,        kc.SEMICOLON,  None,       kc.PRINT_SCREEN,
    kc.CAPS_LOCK, None,   None,      None,   None,    kc.B,    kc.PAGE_UP,  None,   kc.M,   kc.HOME,     kc.UP_ARROW,   kc.END,     kc.RIGHT_SHIFT,
    kc.CONTROL, GLOW_OFF, GLOW_ON,   None,  kc.SPACE, None,    kc.PAGE_DOWN,None,   None, kc.LEFT_ARROW, kc.DOWN_ARROW, kc.RIGHT_ARROW, kc.ENTER ]]

class KeyEvent:
    def __init__(self, scancode, key_pressed):
        self.pressed = key_pressed
        self.key_code = scancode
        self.key_number = None

def random_pixels(prob=1):
    for i in range(6):
        if random.random() < prob:
            glow_pixel[i+1] = RAINBOW[int(random.random()*7)]
        else:
            glow_pixel[i+1] = BLACK

def shifted(k):
    if kb_layer==0 or not k:
        return k
    return key_code[kb_layer][key_code[0].index(k)]

def tap(k):
    usb.press(k)
    time.sleep(.0001)
    usb.release(k)

def set_glow_mode(mode):
    glow_mode = mode
    if glow_mode > 5:
        glow_mode = 1
    glow_interval = .2
    if glow_mode==0:
        # Turn off LEDs for OFF or for COMPUTER modes
        for i in range(6):
            glow_pixel[i+1] = BLACK
    elif glow_mode==1:
        # Breathing mode
        for i in range(6):
            glow_pixel[i+1] = DARK_RED
    elif glow_mode==2:
        # Night Light mode
        for i in range(6):
            glow_pixel[i+1] = BLUE
    elif glow_mode==3:
        # Rainbow mode
        for i in range(6):
            glow_pixel[i+1] = RAINBOW[i]
    elif glow_mode==4:
        # Computer mode
        random_pixels(.1)
    elif glow_mode==5:
        # Chaos mode
        glow_interval = .4
        random_pixels()

glow_pixel[0] = BLACK

prev_tm = time.monotonic()
while True:
    if usb:
        try:
            prev_caps = caps_on
            caps_on = usb.led_on(Keyboard.LED_CAPS_LOCK)
            if caps_on:
                if CAPS_LED:
                    glow_pixel[0] = YELLOW
                elif not prev_caps:
                    uart.write(bytearray([CAPS_LED_ON]))
            else:
                if CAPS_LED:
                    glow_pixel[0] = BLACK
                elif prev_caps:
                    uart.write(bytearray([CAPS_LED_OFF]))

            prev_scroll = scroll_on
            scroll_on = usb.led_on(Keyboard.LED_SCROLL_LOCK)
            if scroll_on:
                if SCROLL_LED:
                    glow_pixel[0] = CYAN
                elif not prev_scroll:
                    uart.write(bytearray([SCROLL_LED_ON]))
            else:
                if SCROLL_LED:
                    glow_pixel[0] = BLACK
                elif prev_scroll:
                    uart.write(bytearray([SCROLL_LED_OFF]))
        except Exception as x:
            print('Caught this exception: ' + repr(x))
            glow_pixel[0] = RED

    tm = time.monotonic()
    if glow_mode>0 and tm > prev_tm + glow_interval:
        prev_tm = tm
        if glow_mode==1:
            # red breathing
            v = glow_pixel[1][0] + glow_delta
            if v<0:
                v = 0
                glow_delta = 1
            elif v > 25:
                v = 25
                glow_delta = -1
                if usb:
                    uart.write(bytearray([GLOW_OFF+glow_mode]))
            for i in range(6):
                glow_pixel[i+1] = (v,0,0)
        elif glow_mode==3:
            # scrolling rainbow
            v = glow_pixel[1]
            for i in range(5):
                glow_pixel[i+1] = glow_pixel[i+2]
            glow_pixel[6] = v
        elif glow_mode==4:
            # computer
            random_pixels(.1)
        elif glow_mode==5:
            # random colors
            random_pixels()

    k_event = key_matrix.events.get()
    if k_event:
        k = k_event.key_number
        y = int(k / right_keys)
        x = k - y*right_keys
        k = key_code[0][y*(left_keys+right_keys) + left_keys + x]
        if usb:
            pixel[0] = ORANGE
        else:
            try:
                b = [ KEY_PRESSED, k ]
                if not k_event.pressed:
                    b[0] = KEY_RELEASED
                uart.write(bytearray(b))
                pixel[0] = BLUE
            except Exception as x:
                print('Caught this exception: ' + repr(x))
                pixel[0] = RED
            continue

    if not k_event:
        try:
            key_pressed = True
            while True:
                data = uart.read(1)
                if not data:
                    break
                pixel[0] = BLUE
                b = data[0]
                if b>=GLOW_OFF and b<=GLOW_OFF+5:
                    set_glow_mode(b - GLOW_OFF)
                    break
                if b>=SCROLL_LED_OFF and b<=CAPS_LED_ON:
                    if b==SCROLL_LED_ON:
                        glow_pixel[0] = CYAN
                    elif b==CAPS_LED_ON:
                        glow_pixel[0] = YELLOW
                    else:
                        glow_pixel[0] = BLACK
                    glow_pixel.show()
                    break
                if b==KEY_PRESSED:
                    key_pressed = True
                    continue
                if b==KEY_RELEASED:
                    key_pressed = False
                    continue
                k_event = KeyEvent(b, key_pressed)
                k = k_event.key_code
                break
        except Exception as x:
            print('Caught this exception: ' + repr(x))
            pixel[0] = RED
            continue

    if not k_event:
        continue

    if (delayed_k==kc.CONTROL or kb_layer==2) and k in (kc.ALT, kc.WINDOWS):
        if k_event.pressed:
            if k==kc.ALT:
                set_glow_mode(0)
            else:
                set_glow_mode(glow_mode + 1)
            if usb:
                uart.write(bytearray([GLOW_OFF+glow_mode]))
            continue

    if k_event.pressed:
        if delayed_k:
            if delayed_k==kc.TAB:
                usb.press(kc.CONTROL)
            elif delayed_k==kc.CAPS_LOCK:
                usb.press(kc.SHIFT)
            elif delayed_k==kc.RIGHT_SHIFT:
                usb.press(delayed_k)
            elif delayed_k==kc.SPACE:
                if kb_layer==0:
                    kb_layer = 1
            elif delayed_k==kc.ENTER:
                kb_layer = 2
            delayed_k = None
        if k==kc.CONTROL:
            kb_layer = 2
        elif k in (kc.TAB, kc.CAPS_LOCK, kc.SPACE, kc.PAGE_DOWN, kc.ENTER, kc.RIGHT_SHIFT):
            delayed_k = k
        else:
            k = shifted(k)
            if k:
                usb.press(k)
    else:
        if delayed_k:
            if delayed_k==k:
                delayed_k = None
                if k==kc.CONTROL:
                    pass
                elif k in (kc.TAB, kc.CAPS_LOCK, kc.ENTER):
                    tap(k)
                elif k==kc.SPACE:
                    if kb_layer==1:
                        kb_layer = 0
                    else:
                        tap(k)
                elif k==kc.RIGHT_SHIFT:
                    tap(kc.ENTER)
                elif k==kc.PAGE_DOWN:
                    if kb_layer==2:
                        tap(k)
                    else:
                        tap(kc.SPACE)
                else:
                    tap(k)
                continue
            elif delayed_k==kc.TAB:
                usb.press(kc.CONTROL)
            elif delayed_k==kc.CAPS_LOCK:
                usb.press(kc.SHIFT)
            elif delayed_k==kc.PAGE_DOWN:
                if kb_layer==0:
                    kb_layer = 1
            elif delayed_k==kc.ENTER:
                kb_layer = 2
            else:
                usb.press(delayed_k)
            delayed_k = None

        if k in (kc.CONTROL, kc.ENTER):
            if kb_layer==2:
                kb_layer = 0
        elif k==kc.SPACE:
            if kb_layer==1:
                kb_layer = 0
            else:
                usb.release(k)
        elif k==kc.PAGE_DOWN:
            if kb_layer<2:
                usb.release(kc.SPACE)
            else:
                usb.release(k)
        elif k==kc.TAB:
            usb.release(kc.CONTROL)
        elif k==kc.CAPS_LOCK:
            usb.release(kc.SHIFT)
        else:
            k = shifted(k)
            if k:
                usb.release(k)
