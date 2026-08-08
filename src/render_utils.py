"""
render_utils.py - أدوات مشتركة للرندر (خطوط، word-wrap، ألوان الموضوع).
"""
from PIL import ImageFont

_FONT_MONO_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
_FONT_MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
_FONT_SANS_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# ألوان موحّدة بين شرائح "slide" وشاشات "code" باش يبقى فيه هوية بصرية موحدة
COLORS = {
    "bg": (13, 17, 23),          # خلفية شبه سوداء (بحال VSCode dark)
    "bg_panel": (22, 27, 34),
    "text": (230, 237, 243),
    "accent": (88, 166, 255),    # أزرق
    "accent2": (63, 185, 80),    # أخضر
    "muted": (139, 148, 158),
    "keyword": (255, 123, 114),
    "string": (165, 214, 255),
    "comment": (110, 118, 129),
    "number": (121, 192, 255),
}


def get_font(size, mono=True, bold=False):
    if mono:
        path = _FONT_MONO_BOLD if bold else _FONT_MONO_REGULAR
    else:
        path = _FONT_SANS_BOLD if bold else _FONT_SANS_REGULAR
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def wrap_text(draw, text, font, max_width):
    words = text.split()
    if not words:
        return [""]
    lines, current = [], []
    for w in words:
        trial = " ".join(current + [w])
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(" ".join(current))
            current = [w]
        else:
            current.append(w)
    if current:
        lines.append(" ".join(current))
    return lines
