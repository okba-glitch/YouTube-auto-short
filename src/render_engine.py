"""
render_engine.py - يبني clip فيديو (صورة+صوت) لكل segment:
  - "code": محاكاة كتابة الكود تدريجيًا مع syntax highlighting (Pygments)،
    ومنبعد (إذا show_execution) "ترمينال" كيبان كيشغل الكود ويطبع
    النتيجة الحقيقية اللي جات من sandbox (code_validator.py) — هادشي هو
    "وقت تجربة exécution" لي كيعطي مصداقية للفيديو.
  - "slide": عنوان + bullets كيبانو واحد بواحد.

فكل segment كنخلطو صوت الراوي مع موسيقى خلفية خافتة (mood حسب نوع
الـ segment، + stinger فلحظة التنفيذ) عبر src/audio_mixer.py — كيتخطى
الموسيقى تلقائيًا إذا مامكانش ملفات فـ music/.

يتطلب: ffmpeg مثبت على النظام، ومكتبة Pygments لـ syntax highlighting.
"""
import os
import subprocess

from PIL import Image, ImageDraw

from src.config import Config
from src.logger import Logger
from src.render_utils import get_font, wrap_text, COLORS
from src.audio_mixer import mix_segment_audio

try:
    from pygments import lex
    from pygments.lexers import get_lexer_by_name
    from pygments.token import Token
    _PYGMENTS_AVAILABLE = True
except ImportError:
    _PYGMENTS_AVAILABLE = False

W, H = Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT

_TOKEN_COLOR_MAP = {
    Token.Keyword: "keyword",
    Token.Name.Builtin: "keyword",
    Token.Name.Function: "accent",
    Token.Name.Class: "accent",
    Token.String: "string",
    Token.Comment: "comment",
    Token.Number: "number",
}


def _color_for_token(token_type):
    for tok, color_key in _TOKEN_COLOR_MAP.items():
        if token_type in tok:
            return COLORS[color_key]
    return COLORS["text"]


def _tokenize_code(code, language):
    if not _PYGMENTS_AVAILABLE:
        return [(code, COLORS["text"])]
    try:
        lexer = get_lexer_by_name(language, stripall=False)
    except Exception:
        return [(code, COLORS["text"])]
    return [(text, _color_for_token(ttype)) for ttype, text in lex(code, lexer)]


def _draw_window_chrome(draw, title):
    draw.rectangle([0, 0, W, 70], fill=COLORS["bg_panel"])
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        draw.ellipse([30 + i * 32, 25, 50 + i * 32, 45], fill=c)
    title_font = get_font(26, mono=True, bold=True)
    draw.text((150, 22), title[:70], font=title_font, fill=COLORS["muted"])


def _draw_code_frame(visible_code, language, title, out_path):
    """يرسم صورة وحدة: شاشة بحال محرر كود، بالجزء المكتوب لحد دابا."""
    img = Image.new("RGB", (W, H), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    _draw_window_chrome(draw, title)

    code_font = get_font(34, mono=True)
    x0, y0 = 60, 110
    line_height = 46
    top_margin, bottom_margin = y0, 40
    max_lines_visible = max((H - top_margin - bottom_margin) // line_height, 1)

    total_lines = visible_code.count("\n") + 1
    # نديرو "scroll": إذا الكود طويل، كنبانو غير آخر max_lines_visible سطر
    scroll_offset_lines = max(total_lines - max_lines_visible, 0)
    y_start = y0 - scroll_offset_lines * line_height

    x, y = x0, y_start
    tokens = _tokenize_code(visible_code, language)

    for text, color in tokens:
        parts = text.split("\n")
        for i, part in enumerate(parts):
            if part and y0 - line_height <= y <= H - bottom_margin:
                draw.text((x, y), part, font=code_font, fill=color)
                bbox = draw.textbbox((0, 0), part, font=code_font)
                x += bbox[2] - bbox[0]
            if i < len(parts) - 1:  # كاين \n بعد هاد الجزء
                y += line_height
                x = x0

    img.save(out_path)


def _draw_terminal_frame(text_lines, out_path, running=False):
    """
    يرسم صورة "ترمينال" ديال وقت تجربة التنفيذ: سطر أمر + النتيجة الحقيقية
    (أو حالة "running..." قبل ما تبان النتيجة).
    """
    img = Image.new("RGB", (W, H), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    _draw_window_chrome(draw, "Terminal — running the code")

    font = get_font(32, mono=True)
    prompt_font = get_font(32, mono=True, bold=True)
    x0, y = 60, 130

    draw.text((x0, y), "$ ", font=prompt_font, fill=COLORS["accent2"])
    prompt_w = draw.textbbox((0, 0), "$ ", font=prompt_font)[2]
    draw.text((x0 + prompt_w, y), "run", font=font, fill=COLORS["text"])
    y += 70

    if running:
        draw.text((x0, y), "⏳ running…", font=font, fill=COLORS["muted"])
        img.save(out_path)
        return

    max_lines = max((H - y - 60) // 44, 1)
    shown = text_lines[:max_lines]
    for line in shown:
        draw.text((x0, y), line[:110], font=font, fill=COLORS["accent2"])
        y += 44
    if len(text_lines) > max_lines:
        draw.text((x0, y), "…", font=font, fill=COLORS["muted"])

    img.save(out_path)


def _draw_slide_frame(title, bullets, num_visible, out_path):
    """يرسم صورة وحدة ديال slide: عنوان + عدد معين من bullets بانين."""
    img = Image.new("RGB", (W, H), COLORS["bg"])
    draw = ImageDraw.Draw(img)

    title_font = get_font(64, mono=False, bold=True)
    bullet_font = get_font(40, mono=False)

    # عنوان فالوسط العلوي
    lines = wrap_text(draw, title, title_font, W - 200)
    y = 140
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        x = (W - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=title_font, fill=COLORS["accent"])
        y += 80

    # خط فاصل
    y += 40
    draw.line([(150, y), (W - 150, y)], fill=COLORS["muted"], width=2)
    y += 60

    for i, bullet in enumerate(bullets):
        if i >= num_visible:
            break
        bullet_lines = wrap_text(draw, bullet, bullet_font, W - 300)
        draw.ellipse([150, y + 14, 168, y + 32], fill=COLORS["accent2"])
        for j, bl in enumerate(bullet_lines):
            draw.text((200, y + j * 50), bl, font=bullet_font, fill=COLORS["text"])
        y += len(bullet_lines) * 50 + 30

    img.save(out_path)


def _frames_to_clip(frame_specs, out_path, fps=Config.VIDEO_FPS):
    """
    frame_specs: list of (image_path, duration_seconds)
    يبني فيديو بلا صوت بـ ffmpeg concat demuxer.
    """
    list_path = out_path + ".txt"
    with open(list_path, "w", encoding="utf-8") as f:
        for path, duration in frame_specs:
            f.write(f"file '{os.path.abspath(path)}'\n")
            f.write(f"duration {duration}\n")
        # آخر صورة كتلزم تتكرر (quirk ديال concat demuxer)
        f.write(f"file '{os.path.abspath(frame_specs[-1][0])}'\n")

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
        "-vf", f"fps={fps},format=yuv420p",
        out_path,
    ]
    subprocess.run(cmd, capture_output=True, timeout=180)
    os.remove(list_path)
    return out_path if os.path.exists(out_path) else None


def render_code_segment(segment, audio_path, audio_duration, work_dir, index):
    """يبني clip كامل (كتابة + ترمينال تنفيذ + صوت + موسيقى) لـ segment code."""
    os.makedirs(work_dir, exist_ok=True)
    code = segment["code"]
    language = segment.get("_language", "python")
    title = segment.get("title", "")

    # نقسمو الكود لخطوات كتابة تدريجية (كل خطوة = تقريبًا سطر أو جزء سطر)
    lines = code.split("\n")
    steps = []
    acc = ""
    for line in lines:
        acc += (line + "\n")
        steps.append(acc)
    if not steps:
        steps = [code]

    typing_duration = min(audio_duration * 0.55, len(steps) * 0.35)
    per_step = max(typing_duration / max(len(steps), 1), 0.12)

    frame_specs = []
    for i, state in enumerate(steps):
        frame_path = os.path.join(work_dir, f"code_{index}_{i:04d}.png")
        _draw_code_frame(state, language, title, frame_path)
        frame_specs.append((frame_path, per_step))

    show_exec = bool(segment.get("show_execution", True)) and bool(segment.get("_execution_output"))
    execution_offset = None

    if show_exec:
        # "وقت تجربة exécution": فريم "running..." ومنبعد النتيجة الحقيقية
        running_path = os.path.join(work_dir, f"code_{index}_exec_running.png")
        _draw_terminal_frame([], running_path, running=True)

        output_text = segment.get("_execution_output", "") or "(no output)"
        output_lines = output_text.splitlines() or ["(no output)"]
        output_path = os.path.join(work_dir, f"code_{index}_exec_output.png")
        _draw_terminal_frame(output_lines, output_path, running=False)

        running_hold = 1.2
        output_hold = max(audio_duration - typing_duration - running_hold, 1.5)
        execution_offset = typing_duration  # لحظة الـ stinger الصوتي
        frame_specs.append((running_path, running_hold))
        frame_specs.append((output_path, output_hold))
    else:
        # ماكاين حتى تنفيذ يبان — الحالة النهائية ديال الكود تبقى بانة
        hold_duration = max(audio_duration - typing_duration, 1.0)
        frame_specs.append((frame_specs[-1][0], hold_duration))

    silent_video = os.path.join(work_dir, f"code_{index}_silent.mp4")
    _frames_to_clip(frame_specs, silent_video)

    mixed_audio_path = os.path.join(work_dir, f"audio_{index}_mixed.wav")
    final_audio = mix_segment_audio(
        audio_path, mixed_audio_path, audio_duration,
        mood="coding", stinger_offset=execution_offset,
    )

    return _mux_audio(silent_video, final_audio, os.path.join(work_dir, f"segment_{index}.mp4"))


def render_slide_segment(segment, audio_path, audio_duration, work_dir, index):
    """يبني clip كامل (صورة متحركة + صوت + موسيقى) لـ segment نوع slide."""
    os.makedirs(work_dir, exist_ok=True)
    title = segment.get("title", "")
    bullets = segment.get("bullets", [])

    n = max(len(bullets), 1)
    per_bullet = max(audio_duration * 0.6 / n, 1.0)
    hold_duration = max(audio_duration - per_bullet * n, 1.0)

    frame_specs = []
    for i in range(1, n + 1):
        frame_path = os.path.join(work_dir, f"slide_{index}_{i:02d}.png")
        _draw_slide_frame(title, bullets, i, frame_path)
        frame_specs.append((frame_path, per_bullet))
    frame_specs.append((frame_specs[-1][0], hold_duration))

    silent_video = os.path.join(work_dir, f"slide_{index}_silent.mp4")
    _frames_to_clip(frame_specs, silent_video)

    mixed_audio_path = os.path.join(work_dir, f"audio_{index}_mixed.wav")
    final_audio = mix_segment_audio(audio_path, mixed_audio_path, audio_duration, mood="slide")

    return _mux_audio(silent_video, final_audio, os.path.join(work_dir, f"segment_{index}.mp4"))


def _mux_audio(silent_video_path, audio_path, out_path):
    cmd = [
        "ffmpeg", "-y", "-i", silent_video_path, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-shortest", out_path,
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=180)
    if result.returncode != 0:
        Logger.error(f"Audio mux failed: {result.stderr.decode(errors='ignore')[:300]}")
        return None
    return out_path if os.path.exists(out_path) else None


def render_segment(segment, audio_path, audio_duration, work_dir, index):
    if segment["type"] == "code":
        return render_code_segment(segment, audio_path, audio_duration, work_dir, index)
    return render_slide_segment(segment, audio_path, audio_duration, work_dir, index)
