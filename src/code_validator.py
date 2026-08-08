"""
code_validator.py - القطعة الأهم فهاد المشروع: تنفذ كل "code" segment
فعليًا فـ sandbox معزول قبل ما نبنيو الفيديو، باش نتأكدو الكود صحيح
وخدام. إذا فشل، نعاود نطلبو من الـ AI يصلحو (عدد محاولات محدود)، وإلا
نرفضو السكريبت كامل بدل ما ننشرو فيديو فيه كود غالط.

كنسجلو ستيدأوت النجاح فـ seg["_execution_output"] باش render_engine.py
يقدر يبان "ترمينال" حقيقي بالنتيجة الفعلية بعد ما يتكتب الكود — هادشي
كيعطي مصداقية للفيديو (الكود لي كيتكتب هو نفسو لي تنفذ وعطا هاد النتيجة).

⚠️ ملاحظة أمان: التنفيذ كيتم بـ subprocess معزول بحدود وقت + بلا شبكة
   قدر الإمكان. لاستعمال إنتاجي جدي، يُفضّل تشغيل هذا داخل حاوية Docker
   منعزولة تمامًا (network=none, read-only fs) بدل subprocess مباشر.
"""
import os
import subprocess
import tempfile

from src.config import Config
from src.logger import Logger

_RUNNERS = {
    "python": {
        "ext": ".py",
        "cmd": lambda path: ["python3", path],
    },
    "javascript": {
        "ext": ".js",
        "cmd": lambda path: ["node", path],
    },
}


def is_language_supported(language):
    return language.lower() in _RUNNERS


def run_code(code: str, language: str):
    """
    ينفذ الكود فـ sandbox معزول ويرجّع (success: bool, output_or_error: str).
    """
    language = language.lower()
    if language not in _RUNNERS:
        return False, f"unsupported language for validation: {language}"

    runner = _RUNNERS[language]
    os.makedirs(Config.SANDBOX_DIR, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=runner["ext"], dir=Config.SANDBOX_DIR,
        delete=False, encoding="utf-8",
    ) as f:
        f.write(code)
        script_path = f.name

    try:
        result = subprocess.run(
            runner["cmd"](script_path),
            capture_output=True,
            text=True,
            timeout=Config.CODE_EXECUTION_TIMEOUT_SECONDS,
            cwd=Config.SANDBOX_DIR,
            env={"PATH": os.environ.get("PATH", "")},  # بيئة مبسطة، بلا أسرار
        )
        if result.returncode != 0:
            return False, (result.stderr or result.stdout or "non-zero exit code").strip()[:2000]
        return True, result.stdout.strip()[:2000]

    except subprocess.TimeoutExpired:
        return False, f"execution timed out after {Config.CODE_EXECUTION_TIMEOUT_SECONDS}s"
    except FileNotFoundError as e:
        return False, f"runtime not available on this machine: {e}"
    except Exception as e:
        return False, f"unexpected sandbox error: {e}"
    finally:
        try:
            os.unlink(script_path)
        except OSError:
            pass


def validate_and_fix_segments(script_data, fix_callback):
    """
    يمر على كل "code" segment، ينفذه، وإذا فشل يطلب تصحيح عبر fix_callback
    (دالة كتاخد topic/language/code/error وترجع كود مصحح أو None).
    يرجّع (all_valid: bool, script_data معدّل بالكود المصحح + مخرجات
    التنفيذ الحقيقية محفوظة فـ seg["_execution_output"] لاستعمالها من
    render_engine.py باش يبان "ترمينال" حقيقي فـ الفيديو).
    """
    language = script_data.get("language", "").lower()
    if language in ("", "none"):
        return True, script_data  # فيديو كامل بلا كود (slide-only)، ماكاين شي لتنفيذ

    if not is_language_supported(language):
        Logger.warning(f"Language '{language}' not sandboxed — skipping code validation")
        return True, script_data

    for i, seg in enumerate(script_data["segments"]):
        if seg["type"] != "code":
            continue

        code = seg["code"]
        attempts = 0
        success, output = run_code(code, language)

        while not success and attempts < Config.MAX_CODE_FIX_ATTEMPTS:
            attempts += 1
            Logger.warning(f"Segment {i} code failed (attempt {attempts}): {output[:200]}")
            fixed_code = fix_callback(language, code, output)
            if not fixed_code:
                break
            code = fixed_code
            success, output = run_code(code, language)

        if not success:
            Logger.error(f"Segment {i} code could not be fixed after {attempts} attempts — rejecting script")
            return False, script_data

        seg["code"] = code  # يحفظ النسخة المصححة (أو الأصلية إذا نجحت من أول مرة)
        seg["_execution_output"] = output  # يتعرض فـ "ترمينال" الفيديو
        seg["_execution_success"] = True
        Logger.success(f"Segment {i} code validated ✅")

    return True, script_data
