"""
tts_engine.py - يحوّل narration كل segment لصوت. Piper (محلي، مجاني، بلا
إنترنت، مفتوح المصدر) كأولوية، وgTTS كـ fallback إذا Piper مش متوفر.
يرجّع (path, duration). النطق الافتراضي إنجليزي (en) — الشرح فهاد المشروع
دايمًا بالإنجليزية.
"""
import os
import subprocess
import wave

from src.config import Config
from src.logger import Logger

_PIPER_MODELS = {
    "en": "en_US-lessac-medium.onnx",
}


def _wav_duration(path):
    try:
        with wave.open(path, "rb") as w:
            return w.getnframes() / float(w.getframerate())
    except Exception:
        return None


def _try_piper(text, out_path, language="en"):
    model_name = _PIPER_MODELS.get(language, _PIPER_MODELS["en"])
    model_path = os.path.join(Config.BASE_DIR, "models", "piper", model_name)
    if not os.path.exists(model_path):
        return None

    try:
        proc = subprocess.run(
            ["piper", "--model", model_path, "--output_file", out_path],
            input=text.encode("utf-8"),
            capture_output=True,
            timeout=60,
        )
        if proc.returncode == 0 and os.path.exists(out_path):
            return out_path
        Logger.warning(f"Piper failed: {proc.stderr.decode(errors='ignore')[:200]}")
        return None
    except FileNotFoundError:
        return None
    except Exception as e:
        Logger.warning(f"Piper error: {e}")
        return None


def _try_gtts(text, out_path, language="en"):
    try:
        from gtts import gTTS
        mp3_path = out_path.replace(".wav", ".mp3")
        gTTS(text=text, lang=language).save(mp3_path)

        # يحوّل لـ WAV باش يبقى format موحّد مع باقي الـ pipeline
        subprocess.run(
            ["ffmpeg", "-y", "-i", mp3_path, "-ar", "22050", "-ac", "1", out_path],
            capture_output=True, timeout=60,
        )
        os.remove(mp3_path)
        return out_path if os.path.exists(out_path) else None
    except Exception as e:
        Logger.warning(f"gTTS fallback failed: {e}")
        return None


def generate_audio(text, out_path, language="en"):
    """
    يرجّع (path, duration_seconds) أو (None, None) عند الفشل الكامل.
    """
    result = _try_piper(text, out_path, language)
    if not result:
        Logger.info("Piper unavailable — falling back to gTTS")
        result = _try_gtts(text, out_path, language)

    if not result:
        return None, None

    duration = _wav_duration(result)
    if duration is None:
        Logger.warning("Could not read WAV duration — estimating from word count")
        duration = max(2.0, len(text.split()) / 2.5)  # ~150 كلمة/دقيقة تقريبًا

    return result, duration
