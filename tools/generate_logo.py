from PIL import Image, ImageDraw, ImageFont
import os

BASE = os.path.dirname(os.path.dirname(__file__))
OUT_DIR = os.path.join(BASE, 'static', 'img')
os.makedirs(OUT_DIR, exist_ok=True)

# sizes
LOGO_PNG = os.path.join(OUT_DIR, 'logo.png')
FAV_PNG = os.path.join(OUT_DIR, 'Fevicon.png')
FAV_ICO = os.path.join(OUT_DIR, 'favicon.ico')

# colors
grad1 = (102,126,234)
grad2 = (118,75,162)
text_color = (31,41,55)
sub_color = (71,85,105)

# fonts
FONT_PATH = 'C:/Windows/Fonts/Arial.ttf'
if not os.path.exists(FONT_PATH):
    FONT_PATH = None

font_large = ImageFont.truetype(FONT_PATH, 28) if FONT_PATH else ImageFont.load_default()
font_small = ImageFont.truetype(FONT_PATH, 12) if FONT_PATH else ImageFont.load_default()

# create logo image (400x120)
img = Image.new('RGBA', (400,120), (255,255,255,0))
d = ImageDraw.Draw(img)

# draw circle with gradient approximation (radial by rings)
cx, cy, r = 52, 52, 36
for i in range(r,0,-1):
    t = i / r
    # interpolate
    col = tuple(int(grad1[j]*t + grad2[j]*(1-t)) for j in range(3))
    d.ellipse((cx-i, cy-i, cx+i, cy+i), fill=col)

# Draw B letter
font_b_large = ImageFont.truetype(FONT_PATH, 34) if FONT_PATH else ImageFont.load_default()
try:
    bbox = font_b_large.getbbox('B')
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
except Exception:
    try:
        ascent, descent = font_b_large.getmetrics()
        h = ascent + descent
        w = h
    except Exception:
        w, h = (24, 28)

d.text((cx - w/2, cy - h/2), 'B', fill=(255,255,255), font=font_b_large)

# Draw text
d.text((100,34), 'Bhrikutimandap', fill=text_color, font=font_large)
d.text((100,64), 'Market & Culture', fill=sub_color, font=font_small)

img.save(LOGO_PNG)
print('Wrote', LOGO_PNG)

# favicon (transparent 64x64)
fav = Image.new('RGBA', (64,64), (0,0,0,0))
df = ImageDraw.Draw(fav)
# draw circle
cx, cy, r = 32, 32, 28
for i in range(r,0,-1):
    t = i / r
    col = tuple(int(grad1[j]*t + grad2[j]*(1-t)) for j in range(3))
    df.ellipse((cx-i, cy-i, cx+i, cy+i), fill=col)

# draw simple B
font_b = ImageFont.truetype(FONT_PATH, 28) if FONT_PATH else ImageFont.load_default()
try:
    bbox = font_b.getbbox('B')
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
except Exception:
    try:
        ascent, descent = font_b.getmetrics()
        h = ascent + descent
        w = h
    except Exception:
        w, h = (18, 20)

df.text((cx - w/2, cy - h/2), 'B', fill=(255,255,255), font=font_b)

fav.save(FAV_PNG)
# save ICO (requires multiple sizes)
ico_sizes = [(16,16),(32,32),(48,48),(64,64)]
icons = []
for s in ico_sizes:
    icons.append(fav.resize(s, Image.LANCZOS))
icons[0].save(FAV_ICO, format='ICO', sizes=ico_sizes)
print('Wrote', FAV_PNG)
print('Wrote', FAV_ICO)
