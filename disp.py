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

