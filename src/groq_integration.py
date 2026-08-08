"""
groq_integration.py - يبني السكريبت الكامل للتوتوريال عبر مرحلتين:
  1) outline: توليد خطة الفيديو (عناوين + أهداف كل segment) - نداء واحد
  2) detail: توليد كل segment بالتفصيل (narration + code/bullets) - نداء
     منفصل لكل segment، باش يبقى كل JSON صغير وموثوق وما يتقطعش
هاد الأسلوب كيعطي فيديوهات أطول (28-32 دقيقة) بشكل موثوق أكثر من طلب كل
شيء فـ نداء واحد ضخم قد ينقطع (JSON غير صالح لو تجاوز حد التوكنز). الاتصال
بالـ AI (مفتوح الوزن دائمًا: Groq/Llama أو Ollama محلي) عبر
src/llm_backend.py — الاسم "groq_integration" بقى كيما هو للتوافق مع
main.py، بصح دابا كيدعم أي backend مفتوح المصدر.

⚠️ ملاحظة إصلاح (مهمة): نماذج الـ LLM كتزيد أحيانًا سطر جديد حرفي (raw
   newline) داخل قيمة string فـ الـ JSON (مثلاً فـ "description" لما
   كنطلبو منها تحط الهاشتاغات "على سطر جديد") بدل ما تكتبو مهرّب (\\n).
   الـ JSON الصارم (json.loads بالافتراضي strict=True) كيرفض أي control
   character خام داخل string ويطيح بـ "Invalid control character at:
   line X column Y" — هادشي كان سبب فشل الـ pipeline كامل فالإنتاج رغم
   أن الـ JSON كان "شبه" صحيح. الحل: json.loads(..., strict=False) كيسمح
   بـ control characters خام داخل الـ strings، + دالة _sanitize_json_text
   كـ خط دفاع ثاني إذا الفشل كان لسبب آخر (مثلاً tab خام برا quotes).
"""
import json
import re
import time

from src.config import Config
from src.logger import Logger
from src.llm_backend import chat_completion
from src.ai_prompts import (
    build_outline_system_prompt, build_outline_user_prompt,
    SEGMENT_SYSTEM_PROMPT, build_segment_user_prompt, build_fix_prompt,
    validate_outline, validate_segment, validate_full_script,
)


def _strip_fences(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:]
    return raw.strip()


def _sanitize_json_text(raw: str) -> str:
    """
    خط دفاع ثاني: كيهرّب control characters خام (newline/tab/carriage
    return) لي موجودين داخل quoted strings فقط، باش حتى لو strict=False
    ماكفاش (حالات نادرة)، يبقى عندنا فرصة أخيرة قبل ما نعتبرو الرد فاشل.
    ماكيمسش شي حاجة برا الـ quotes باش ما نخربوش بنية الـ JSON نفسها.
    """
    def _escape_in_string(match):
        s = match.group(0)
        return (
            s.replace("\r\n", "\\n")
             .replace("\n", "\\n")
             .replace("\r", "\\n")
             .replace("\t", "\\t")
        )
    # يطابق أي "..." (يدعم \" مهربة بالداخل) ويطبق التهريب فوقها فقط
    return re.sub(r'"(?:\\.|[^"\\])*"', _escape_in_string, raw, flags=re.DOTALL)


def _safe_json_loads(raw: str, context: str):
    """
    يحاول json.loads بـ 3 مستويات تسامح متصاعدة، ويرجّع dict أو None:
      1) parsing عادي (strict=True) — أسرع حالة، الأغلبية كتعدي من هنا
      2) strict=False — كيسمح بـ control characters خام داخل strings
         (هادو غالبية الحالات لي كانت كتطيح، بحال الخطأ الأصلي)
      3) sanitize + strict=False — تهريب يدوي كخط دفاع أخير
    """
    cleaned = _strip_fences(raw)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    try:
        return json.loads(cleaned, strict=False)
    except json.JSONDecodeError as e:
        Logger.warning(f"{context}: strict=False parse still failed ({e}) — trying sanitizer")

    try:
        return json.loads(_sanitize_json_text(cleaned), strict=False)
    except json.JSONDecodeError as e:
        Logger.warning(f"{context}: JSON parse failed after sanitizing: {e}")
        return None


def _generate_outline(topic, preferred_language):
    words_min, words_max = Config.TOTAL_NARRATION_WORDS_RANGE
    seg_min, seg_max = Config.SEGMENTS_RANGE
    system = build_outline_system_prompt(words_min, words_max, seg_min, seg_max)
    user = build_outline_user_prompt(topic, preferred_language)

    raw = chat_completion(system, user, temperature=0.6, max_tokens=3000)
    if not raw:
        return None

    data = _safe_json_loads(raw, "Outline")
    if data is None:
        return None

    ok, reason = validate_outline(data)
    if not ok:
        Logger.warning(f"Outline failed validation: {reason}")
        return None
    return data


def _generate_segment(topic, language, stub, prev_code, index, total):
    user = build_segment_user_prompt(topic, language, stub, prev_code, index, total)
    raw = chat_completion(SEGMENT_SYSTEM_PROMPT, user, temperature=0.5, max_tokens=1800)
    if not raw:
        return None

    data = _safe_json_loads(raw, f"Segment {index}")
    if data is None:
        return None

    ok, reason = validate_segment(data, stub["type"])
    if not ok:
        Logger.warning(f"Segment {index} failed validation: {reason}")
        return None
    return data


def generate_tutorial_script(topic, preferred_language="multi"):
    """يرجّع dict (segments/title/description/tags/language) أو None."""
    if Config.LLM_BACKEND == "groq" and not Config.GROQ_API_KEY:
        Logger.warning("GROQ_API_KEY not set")
        return None

    outline = _generate_outline(topic, preferred_language)
    if not outline:
        Logger.error("Outline generation failed")
        return None

    language = outline.get("language", "python")
    n = len(outline["segments"])
    Logger.info(f"📝 Outline ready: {n} segments planned, language={language}")

    full_segments = []
    prev_code = ""
    for i, stub in enumerate(outline["segments"]):
        if i > 0 and Config.LLM_BACKEND == "groq" and Config.LLM_REQUEST_DELAY_SECONDS > 0:
            # وقفة استباقية بين كل نداء وآخر باش ما نضربوش rate limit ديال
            # Groq من البداية (بالإضافة لـ retry/backoff فـ llm_backend.py)
            time.sleep(Config.LLM_REQUEST_DELAY_SECONDS)

        Logger.info(f"  → writing segment {i + 1}/{n}: {stub['title']}")
        seg = _generate_segment(topic, language, stub, prev_code, i, n)
        if not seg:
            Logger.error(f"Segment {i} generation failed — aborting script")
            return None
        if seg["type"] == "code":
            prev_code = seg["code"]
        if stub["type"] == "code":
            seg["show_execution"] = stub.get("show_execution", True)
        full_segments.append(seg)

    outline["segments"] = full_segments

    ok, reason = validate_full_script(outline)
    if not ok:
        Logger.warning(f"Assembled script failed final validation: {reason}")
        return None

    total_words = sum(len(s["narration"].split()) for s in full_segments)
    est_minutes = total_words / Config.WORDS_PER_MINUTE
    Logger.info(f"📏 Estimated narration length: ~{total_words} words (~{est_minutes:.1f} min)")

    return outline


def fix_code_with_groq(language, broken_code, error_message, topic="this tutorial"):
    """دالة fix_callback المستعملة من code_validator.validate_and_fix_segments."""
    system = (
        "You are a precise code-fixing assistant. Output ONLY the "
        "corrected, complete, runnable code. No explanation, no markdown "
        "fences."
    )
    prompt = build_fix_prompt(topic, language, broken_code, error_message)
    raw = chat_completion(system, prompt, temperature=0.2, max_tokens=1500)
    return _strip_fences(raw) if raw else None
