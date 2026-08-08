"""
llm_backend.py - طبقة تجريد فوق مزوّدي الـ AI، بشرط واحد: نماذج مفتوحة
الوزن (open-weight) فقط — Llama، Qwen، Mistral... حسب اختيار LLM_BACKEND
فـ config.py:

  - "groq"   : Groq Cloud (سريع، مجاني بحدود معقولة) يشغّل Llama 3.3 70B
               من Meta (open-weight license) — هو لي كيغلّب السكريبت.
  - "ollama" : تشغيل محلي كامل بلا إنترنت ولا API key، لأي موديل مفتوح
               مثبت محليًا (مثلاً: ollama pull llama3.1:70b)

كل الملفات الأخرى (groq_integration.py) كتنادي chat_completion() هنا
بلا ما تعرف شكون المزوّد الفعلي — هادشي كيسمح تبدّل المزوّد بغير تغيير
env variable وحدة (LLM_BACKEND)، بلا تعديل أي كود.
"""
import random
import time

import requests

from src.config import Config
from src.logger import Logger

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# ⚠️ ملاحظة إصلاح: خطة Groq المجانية عندها rate limit صارم (طلبات/دقيقة +
# توكنز/دقيقة). فيديو واحد كيدير 20-30+ نداء API متتالي بسرعة (outline +
# segment لكل واحد)، وهادشي كيولّي بسهولة لـ "429 Too Many Requests" —
# خصوصًا إذا شغّلتي main.py مرتين قريب من بعضهم، أو الخطة عندك ضيقة.
# الحل: retry بـ exponential backoff + jitter، وكنحترمو Retry-After header
# إذا Groq رجعاتو (هي لي كتعرف بالضبط شحال خاصنا نتسناو)، بدل ما نستسلمو
# من أول محاولة فاشلة.
GROQ_MAX_RETRIES = 5
GROQ_BASE_BACKOFF_SECONDS = 2.0


def _groq_chat(system_prompt, user_prompt, temperature, max_tokens):
    if not Config.GROQ_API_KEY:
        Logger.warning("GROQ_API_KEY not set")
        return None
    payload = {
        "model": Config.GROQ_MODEL,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    headers = {
        "Authorization": f"Bearer {Config.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    for attempt in range(1, GROQ_MAX_RETRIES + 1):
        try:
            resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=90)

            if resp.status_code == 429:
                wait = _retry_after_seconds(resp, attempt)
                Logger.warning(
                    f"Groq rate limited (429), attempt {attempt}/{GROQ_MAX_RETRIES} "
                    f"— waiting {wait:.1f}s before retry"
                )
                if attempt < GROQ_MAX_RETRIES:
                    time.sleep(wait)
                    continue
                Logger.error("Groq still rate limited after all retries — giving up")
                return None

            # 5xx = مشكل مؤقت عند Groq نفسها، يستاهل retry بحال 429
            if resp.status_code >= 500:
                wait = _backoff_seconds(attempt)
                Logger.warning(
                    f"Groq server error ({resp.status_code}), attempt "
                    f"{attempt}/{GROQ_MAX_RETRIES} — retrying in {wait:.1f}s"
                )
                if attempt < GROQ_MAX_RETRIES:
                    time.sleep(wait)
                    continue
                resp.raise_for_status()

            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            # مشاكل شبكة/timeout عابرة — retry بنفس المنطق بدل ما نطيحو دغيا
            wait = _backoff_seconds(attempt)
            Logger.warning(
                f"Groq request failed ({e}), attempt {attempt}/{GROQ_MAX_RETRIES}"
                + (f" — retrying in {wait:.1f}s" if attempt < GROQ_MAX_RETRIES else "")
            )
            if attempt < GROQ_MAX_RETRIES:
                time.sleep(wait)
                continue
            return None

    return None


def _backoff_seconds(attempt):
    """Exponential backoff + jitter: 2, 4, 8, 16... ثانية تقريبًا."""
    base = GROQ_BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
    return base + random.uniform(0, base * 0.3)


def _retry_after_seconds(resp, attempt):
    """
    كيقرا Retry-After header (بالثواني) إذا Groq رجعاتو مع الـ 429 — هادي
    أدق من backoff عشوائي لأنها كتجي من نفس السيرفر لي عندو الحد. إذا
    ماكانش header، كنرجعو لـ exponential backoff عادي.
    """
    retry_after = resp.headers.get("Retry-After")
    if retry_after:
        try:
            return float(retry_after) + random.uniform(0, 1.0)
        except ValueError:
            pass
    return _backoff_seconds(attempt)


def _ollama_chat(system_prompt, user_prompt, temperature, max_tokens):
    url = f"{Config.OLLAMA_URL}/api/chat"
    payload = {
        "model": Config.OLLAMA_MODEL,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    try:
        resp = requests.post(url, json=payload, timeout=300)
        resp.raise_for_status()
        return resp.json()["message"]["content"]
    except Exception as e:
        Logger.warning(f"Ollama request failed (is `ollama serve` running?): {e}")
        return None


def chat_completion(system_prompt, user_prompt, temperature=0.5, max_tokens=2000):
    """يرجّع نص الرد (str) أو None عند الفشل، بغض النظر على المزوّد."""
    if Config.LLM_BACKEND == "ollama":
        return _ollama_chat(system_prompt, user_prompt, temperature, max_tokens)
    return _groq_chat(system_prompt, user_prompt, temperature, max_tokens)
