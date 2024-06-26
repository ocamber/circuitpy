import board
import time
import digitalio
import keypad
import terminalio
import displayio
import vectorio
import adafruit_miniqr
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from digitalio import DigitalInOut, Direction, Pull

"""
A general purpose data driven multi-id system for the
Badger RP2040 with logos, photos, and scan codes
"""

# Turn on LED
led = digitalio.DigitalInOut(board.USER_LED)
led.direction = digitalio.Direction.OUTPUT
led.value = True

# Set up button IO
button_a = DigitalInOut(board.SW_A)
button_a.direction = Direction.INPUT
button_a.pull = Pull.DOWN
button_b = DigitalInOut(board.SW_B)
button_b.direction = Direction.INPUT
button_b.pull = Pull.DOWN
button_c = DigitalInOut(board.SW_C)
button_c.direction = Direction.INPUT
button_c.pull = Pull.DOWN
button_up = DigitalInOut(board.SW_UP)
button_up.direction = Direction.INPUT
button_up.pull = Pull.DOWN
button_down = DigitalInOut(board.SW_DOWN)
button_down.direction = Direction.INPUT
button_down.pull = Pull.DOWN

# Set text, font, and color
black = 0x000000
white = 0xFFFFFF
id_font = bio_font = terminalio.FONT
desc_font = org_font = bitmap_font.load_font('fonts/desc-font.bdf')
name_font = bitmap_font.load_font('fonts/name-font.bdf')
xname_font = bitmap_font.load_font('fonts/xname-font.bdf')
bar_font = bitmap_font.load_font('fonts/bar-font.bdf')

# Display states/controls
display = board.DISPLAY
data = []
badge_index = 0
display_mode = 0
bio_line_index = 0
bio_lines = 0

def show_display(group):
    time.sleep(display.time_to_refresh+.1)
    display.show(group)
    display.refresh()

def add_background(group, color):
    # Set the palette for the background color
    back_palette = displayio.Palette(1)
    back_palette[0] = color
    background_rect = vectorio.Rectangle(pixel_shader=back_palette, \
        width=display.width + 1, height=display.height, x=0, y=0)
    group.append(background_rect)

def fetchImage(imgStr):
    if not imgStr:
        return None
    if len(imgStr)<1:
        return None
    attr = None
    if imgStr[:1]=='[':
        p = imgStr.find(']',1,10)
        if p>0:
            attr = imgStr[1:p].split(',')
            imgStr = imgStr[p+1:]
    bitmap = displayio.OnDiskBitmap(imgStr)
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

def makeLabel(font, text, label_direction='LTR', scale=None):
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
        img = label.Label(font, text=text, color=black, scale=scale)
    else:
        img = label.Label(font, text=text, color=black, label_direction=label_direction)
    if attr:
        img.x = int(attr[0])
        img.y = int(attr[1])
    return img

def display_bio():
    item = data[badge_index]
    group = displayio.Group()
    add_background(group, white)
    img = label.Label(bio_font, text='Bio for '+item['xname'] + ' ('+item['name']+'):', color=black)
    img.y = 5
    group.append(img)
    fp = open(item['bio'], mode='r')
    i = 0
    ln = fp.readline()
    while ln and i<bio_line_index:
        ln = fp.readline()
        i += 1
    bio_lines = i+1
    i = 0
    while ln and i<8:
        img = label.Label(bio_font, text=ln, color=black)
        img.x = 10
        img.y = 6 + 14*(i+1)
        group.append(img)
        ln = fp.readline()
        i += 1
    bio_lines += i
    fp.close()
    show_display(group)

def display_badge():
    index = badge_index
    item = data[index]

    # Create the display group and set background
    group = displayio.Group()
    base_img = fetchImage(item['img'])

    # Base image or background and org label
    if base_img:
        group.append(base_img)
    else:
        add_background(group, black)
        text = item['org']
        if len(text)>0:
            img = label.Label(org_font, text=item['org'], color=white)
            img.x = 4
            img.y = 6
            group.append(img)

    # set foreground palette
    palette = displayio.Palette(1)
    palette[0] = white

    # logo / id area
    img = fetchImage(item['logo'])
    if img:
        if not base_img:
            group.append(vectorio.Rectangle(pixel_shader=palette, width=172, height=40, x=3, y=13))
            img.x = 3
            img.y = 15
        group.append(img)

    # id number
    img = makeLabel(id_font, text=item['id'], scale=2)
    if img:
        if not base_img:
            img.x = 50
            img.y = 27
        group.append(img)

    # name label
    img = makeLabel(name_font, text=item['name'])
    if img:
        if not base_img:
            group.append(vectorio.Rectangle(pixel_shader=palette, width=172, height=36, x=3, y=54))
            img.x = 5
            img.y = 68
        group.append(img)

    # xname label
    img = makeLabel(xname_font, text=item['xname'])
    if img:
        if not base_img:
            group.append(vectorio.Rectangle(pixel_shader=palette, width=172, height=21, x=3, y=91))
            img.x = 5
            img.y = 100
        group.append(img)

    # desc label
    img = makeLabel(desc_font, item['desc'])
    if img:
        if not base_img:
            group.append(vectorio.Rectangle(pixel_shader=palette, width=172, height=14, x=3, y=113))
            img.x = 5
            img.y = 120
        group.append(img)

    # photo / QR area
    if not base_img:
        group.append(vectorio.Rectangle(pixel_shader=palette, width=120, height=128, x=176, y=0))

    if display_mode==2:
        qr_text = item['qr']
        if len(qr_text)>0:
            qr = adafruit_miniqr.QRCode(qr_type=3, error_correct=adafruit_miniqr.L)
            qr.add_data(qr_text.encode('utf-8'))
            qr.make()
            bitmap = displayio.Bitmap(qr.matrix.width*4, qr.matrix.height*4, 2)
            for row in range(qr.matrix.height*4):
                for col in range(qr.matrix.width*4):
                    y = int(row/4)
                    x = int(col/4)
                    if qr.matrix[x,y]:
                        bitmap[col,row] = 1
                    else:
                        bitmap[col, row] = 0
            qr_palette = displayio.Palette(2)
            qr_palette[0] = white
            qr_palette[1] = black
            img = displayio.TileGrid(bitmap, pixel_shader=qr_palette)
            img.x = 180
            img.y = 4
            group.append(img)
    else:
        img = fetchImage(item['photo'])
        if img:
            if not base_img:
                img.x = 175
                img.y = 0
            group.append(img)

    # bar code of id number
    text = strip_coord(item['id'])
    if len(text)>0 and len(text)<7:
        group.append(vectorio.Rectangle(pixel_shader=palette, width=24, height=128, x=272, y=0))
        img = makeLabel(bar_font, text='*'+text+'*', label_direction='DWR')
        img.x = 281
        img.y = 6
        group.append(img)

    # Show the group and refresh the screen to see the result
    show_display(group)

# read data file
fp=open('data.txt', mode='r')
try:
    ln = fp.readline()
    while (ln):
        fields = ln.split('|')
        item = { 'img':fields[0], 'org':fields[1], 'id':fields[2], 'name':fields[3], \
                'xname':fields[4], 'desc':fields[5], \
                'logo':None, 'photo':None, 'qr':None, 'bio':None }
        try:
            item['logo'] = fields[6]
            item['photo'] = fields[7]
            item['qr'] = fields[8]
            item['bio'] = fields[9]
        except:
            pass
        data.append(item)
        ln = fp.readline()
except:
    pass
fp.close()

badge_index = 0
display_badge()

ticks = 0
button_pressed = False
while True:
    ticks += 1
    if ticks > 9:
        ticks = 0
        led.value = not led.value

    k_num = -1
    if button_a.value==True:
        k_num = 0
    elif button_b.value==True:
        k_num = 1
    elif button_c.value==True:
        k_num = 2
    elif button_up.value==True:
        k_num = 3
    elif button_down.value==True:
        k_num = 4
    else:
        button_pressed = False

    if button_pressed or k_num < 0 or k_num == display_mode:
        pass
    elif k_num < 3:
        display_mode = k_num
        button_pressed = True
        if display_mode == 1:
            bio_line_index = 0
            display_bio()
        else:
            display_badge()
    else:
        button_pressed = True
        if display_mode == 1:
            i = bio_line_index + (-1 if k_num==3 else 1)
            if i >= bio_lines:
                i = bio_lines-1
            if i<0:
                i = 0
            if i != bio_line_index:
                bio_line_index = i
                display_bio()
        else:
            n = len(data)
            i = badge_index + (-1 if k_num==3 else 1)
            if i>=n:
                i = 0
            if i<0:
                i = n-1
            badge_index = i
            display_badge()

    time.sleep(.1)
