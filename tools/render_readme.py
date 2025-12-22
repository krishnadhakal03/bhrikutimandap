from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

BASE = os.path.dirname(os.path.dirname(__file__))
INPUT = os.path.join(BASE, 'docs', 'README.md')
OUT_PNG = os.path.join(BASE, 'docs', 'README.png')
OUT_PDF = os.path.join(BASE, 'docs', 'README.pdf')

FONT_PATH = None
try:
    # common Windows font
    FONT_PATH = 'C:/Windows/Fonts/Arial.ttf'
except Exception:
    FONT_PATH = None

font = ImageFont.truetype(FONT_PATH, 16) if FONT_PATH and os.path.exists(FONT_PATH) else ImageFont.load_default()

with open(INPUT, 'r', encoding='utf-8') as f:
    text = f.read()

lines = []
for paragraph in text.split('\n'):
    if paragraph.strip() == '':
        lines.append('')
        continue
    wrapped = textwrap.wrap(paragraph, width=80)
    lines.extend(wrapped)

# compute image size
padding = 32
# compute line height using a temporary draw instance for compatibility
try:
    # Pillow >= 8: getbbox
    bbox = font.getbbox('A')
    line_height = bbox[3] - bbox[1] + 6
except Exception:
    try:
        ascent, descent = font.getmetrics()
        line_height = ascent + descent + 6
    except Exception:
        line_height = 20 + 6
img_height = padding * 2 + line_height * len(lines)
img_width = 1000

img = Image.new('RGB', (img_width, img_height), color=(255,255,255))
d = ImageDraw.Draw(img)

# title style for first line
y = padding
for i, line in enumerate(lines):
    if i == 0:
        d.text((padding, y), line, fill=(34,37,44), font=font)
    else:
        d.text((padding, y), line, fill=(55,65,81), font=font)
    y += line_height

# save PNG
img.save(OUT_PNG)
# save PDF
img.convert('RGB').save(OUT_PDF)

print('Wrote', OUT_PNG)
print('Wrote', OUT_PDF)
