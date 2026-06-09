import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone


FONT_DIR = os.path.join(settings.BASE_DIR, 'static', 'fonts')
WINDIR = os.environ.get('WINDIR', 'C:\\Windows')


def _get_font(name, size):
    aliases = {
        'arial.ttf': ['DejaVuSans.ttf', 'LiberationSans-Regular.ttf', 'FreeSans.ttf'],
        'arialbd.ttf': ['DejaVuSans-Bold.ttf', 'LiberationSans-Bold.ttf', 'FreeSansBold.ttf'],
        'ariali.ttf': ['DejaVuSans-Oblique.ttf', 'LiberationSans-Italic.ttf', 'FreeSansOblique.ttf'],
    }

    candidates = []
    for fname in (name, name.lower()):
        candidates.append(os.path.join(FONT_DIR, fname))
        candidates.append(os.path.join(WINDIR, 'Fonts', fname))

    base = os.path.splitext(name.lower())[0]
    for alt in aliases.get(name.lower(), []):
        candidates.append(f'/usr/share/fonts/truetype/dejavu/{alt}')
        candidates.append(f'/usr/share/fonts/TTF/{alt}')
        candidates.append(f'/usr/share/fonts/{alt}')

    linux_dirs = [
        '/usr/share/fonts/truetype/dejavu',
        '/usr/share/fonts/truetype/msttcorefonts',
        '/usr/share/fonts/TTF',
        '/usr/share/fonts',
    ]
    if os.name != 'nt':
        for d in linux_dirs:
            if os.path.isdir(d):
                for f in os.listdir(d):
                    if base in f.lower():
                        candidates.append(os.path.join(d, f))

    seen = set()
    for p in candidates:
        if p in seen:
            continue
        seen.add(p)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def generate_certificate_image(student_name, group_name, teacher_name, level, score, background_path):
    try:
        bg = Image.open(background_path).convert("RGBA")
    except Exception:
        return None

    img_w, img_h = bg.size
    draw = ImageDraw.Draw(bg)

    student_name = student_name.title()

    name_font = _get_font('Parisienne-Regular.ttf', int(img_w * 0.068))
    level_font = _get_font('arial.ttf', int(img_w * 0.0223))
    teacher_font = _get_font('arial.ttf', int(img_w * 0.0178))

    draw.text(
        (img_w / 2, img_h * 0.52),
        student_name,
        fill="#000000",
        font=name_font,
        anchor="mm",
        align="center"
    )

    level_text = level if level else "English Proficiency Level"
    draw.text(
        (img_w / 2, img_h * 0.71),
        level_text,
        fill="#000000",
        font=level_font,
        anchor="mm",
        align="center"
    )

    if teacher_name:
        teacher_x = img_w * 0.91
        teacher_y = img_h * 0.94
        draw.text(
            (teacher_x, teacher_y),
            teacher_name,
            fill="#ffffff",
            font=teacher_font,
            anchor="mm",
            align="center"
        )   

    output = BytesIO()
    bg = bg.convert("RGB")
    bg.save(output, format="PNG", quality=95)
    output.seek(0)

    return output


def save_certificate_pdf(student_name, group_name, teacher_name, level, score, background_path):
    img_data = generate_certificate_image(student_name, group_name, teacher_name, level, score, background_path)
    if img_data is None:
        return None

    safe_name = student_name.replace(' ', '_').replace('/', '_')
    filename = f"certificate_{safe_name}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.png"
    return ContentFile(img_data.read(), name=filename)
