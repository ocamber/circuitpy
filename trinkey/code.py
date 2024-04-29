import board
import time
import busio
import digitalio
import neopixel
import adafruit_bme680
from digitalio import DigitalInOut, Direction, Pull
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keyboard import Keyboard

# change this to match the local pressure (hPa) at sea level and temp offset
sea_level_pressure = 1018
temperature_offset = -4

cc = None
usb = None
kbd = None

print('Initializing..')

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

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel.fill(ORANGE)

usb = None

print('Scanning for USB..')

try:
    cc = ConsumerControl(usb_hid.devices)
    usb = Keyboard(usb_hid.devices)
    kbd = KeyboardLayoutUS(usb)
    print('Keyboard USB found.')
except:
    print('Keyboard USB NOT FOUND.')

def output(txt):
    print(txt)
    if kbd:
        kbd.write(txt+'\n')

print('Scanning for STEMMA devices..')

bme680 = None
stemma = board.STEMMA_I2C
stemma_device = None
prevMS = time.monotonic()
try:
    while True:
        ms = time.monotonic()
        if ms<prevMS:
            prevMS = ms
        elif ms-prevMS>50:
            stemma = None
            break
        if stemma.try_lock():
            break
except:
    stemma = None

if stemma:
    for x in stemma.scan():
        stemma_device = x
        break
try:
    i2c = board.I2C()  # uses board.SCL and board.SDA
    bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)
    bme680.sea_level_pressure = sea_level_pressure
    print('BME680 found.')
    pixel.fill(BLUE)
except:
    print('NO BME680 FOUND.')
    pixel.fill(RED)

if stemma_device or bme680:
    print('STEMMA device found.')
else:
    print('No STEMMA devices.')

while True:
    time.sleep(10)
    if bme680:
        tempC = (bme680.temperature + temperature_offset)
        tempF = tempC*(9/5)+32
        txt = 'Temperat: %0.1f C / %0.1f F' % (tempC, tempF)
        print('--------------------------------')
        print(txt)
        print('Humidity: %0.1f%%' % bme680.relative_humidity)
        print('Pressure: %0.3f hPa' % bme680.pressure)
        print('Altitude: %0.2f m' % bme680.altitude)
        print('Gas/Vapor %d ohm' % bme680.gas)
        print()
