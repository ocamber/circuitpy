import board
import digitalio
import time

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
cnt = 1

while True:
    led.value = False
    time.sleep(1)
    for i = range(1, cnt):
        led.value = True
        time.sleep(0.3)
        led.value = False
        time.sleep(0.6)
    cnt = cnt + 1
    if cnt>9:
        cnt = 1

