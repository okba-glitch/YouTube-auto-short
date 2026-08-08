"""
audio_mixer.py - يخلط صوت الراوي مع موسيقى خلفية خافتة من مصادر مفتوحة/
حرة الرخصة يوفرها المستخدم فـ music/<mood>/*.mp3|wav (شوف
music/README.md لمصادر مقترحة). يدعم:
  - "bed": فرشة موسيقى هادئة طول الـ segment (mood="coding" أو "slide")
  - "stinger": صوت قصير عند لحظة تنفيذ الكود (mood="execution")، كيتزاد
    فوق الفرشة فاللحظة المضبوطة (stinger_offset بالثواني)

إذا الموسيقى معطلة (MUSIC_ENABLED=false) أو ماكاينش ملفات فـ المجلد
المطلوب، كترجع صوت الراوي الأصلي بلا تغيير — الرندر كيكمل عادي بلا خطأ.
"""
import os
import glob
import random
import subprocess

from src.config import Config
from src.logger import Logger


def _pick_track(mood):
    folder = os.path.join(Config.MUSIC_DIR, mood)
    tracks = glob.glob(os.path.join(folder, "*.mp3")) + glob.glob(os.path.join(folder, "*.wav"))
    return random.choice(tracks) if tracks else None


def mix_segment_audio(narration_path, out_path, duration, mood="coding", stinger_offset=None):
    """
    يبني صوت segment نهائي = راوي + فرشة موسيقى خافتة (mood) + (اختياري)
    stinger قصير فلحظة stinger_offset (تنفيذ الكود). يرجّع مسار الصوت
    النهائي، أو narration_path الأصلي إذا الموسيقى معطلة/غير متوفرة.
    """
    if not Config.MUSIC_ENABLED:
        return narration_path

    bed_track = _pick_track(mood)
    stinger_track = _pick_track("execution") if stinger_offset is not None else None

    if not bed_track and not stinger_track:
        return narration_path  # ماكاين حتى تراك — الصوت الأصلي كافي

    inputs = ["-i", narration_path]
    filters = []
    mix_labels = ["0:a"]
    next_input_idx = 1

    if bed_track:
        inputs += ["-stream_loop", "-1", "-i", bed_track]
        filters.append(
            f"[{next_input_idx}:a]volume={Config.MUSIC_VOLUME},afade=t=in:d=1,"
            f"atrim=0:{duration}[bed]"
        )
        mix_labels.append("bed")
        next_input_idx += 1

    if stinger_track:
        inputs += ["-i", stinger_track]
        delay_ms = int(max(stinger_offset, 0) * 1000)
        filters.append(
            f"[{next_input_idx}:a]volume={Config.STINGER_VOLUME},atrim=0:2.5,"
            f"adelay={delay_ms}|{delay_ms}[stinger]"
        )
        mix_labels.append("stinger")
        next_input_idx += 1

    mix_inputs = "".join(f"[{label}]" for label in mix_labels)
    filters.append(
        f"{mix_inputs}amix=inputs={len(mix_labels)}:duration=first:"
        f"dropout_transition=2[aout]"
    )

    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", ";".join(filters),
        "-map", "[aout]", "-t", str(duration),
        out_path,
    ]

    result = subprocess.run(cmd, capture_output=True, timeout=60)
    if result.returncode != 0:
        Logger.warning(f"Music mix failed, using narration only: {result.stderr.decode(errors='ignore')[:200]}")
        return narration_path
    return out_path if os.path.exists(out_path) else narration_path
