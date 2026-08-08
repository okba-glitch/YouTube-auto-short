"""
config.py - إعدادات مركزية لمشروع فيديوهات تعليم البرمجة (طويلة، ~30 دقيقة،
كل 12 ساعة). مبني بنفس فلسفة مشروع Terminal Shorts، بصح موجّه لمحتوى
تعليمي أطول بكثير، بموسيقى خلفية، وعرض تنفيذ الكود فعليًا.
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Config:
    # ==================== المسارات ====================
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = os.path.join(BASE_DIR, "data")
    OUTPUT_DIR = os.path.join(BASE_DIR, "output")
    SANDBOX_DIR = os.path.join(BASE_DIR, "sandbox")
    MUSIC_DIR = os.path.join(BASE_DIR, "music")

    # ==================== المفاتيح ====================
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    YOUTUBE_CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID", "")
    YOUTUBE_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
    YOUTUBE_REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")
    DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

    # ==================== محرك الـ AI (مفتوح المصدر فقط) ====================
    # "groq"   -> Groq Cloud، استضافة سريعة ومجانية لنماذج مفتوحة الوزن
    #             (Llama 3.3 70B من Meta) — يحتاج GROQ_API_KEY (مجاني).
    # "ollama" -> تشغيل محلي 100%، بلا إنترنت ولا مفاتيح، لأي نموذج مفتوح
    #             (llama3.1, qwen2.5, mistral...) عبر https://ollama.com
    LLM_BACKEND = os.environ.get("LLM_BACKEND", "groq").lower()
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:70b")

    # فيديو واحد كيدير 20-30+ نداء API متتالي (outline + segment لكل
    # واحد) — الخطة المجانية ديال Groq عندها حد صارم ديال الطلبات/دقيقة،
    # فكنستناو شوية بين كل نداء وآخر باش نتجنبو 429 Too Many Requests من
    # البداية (بالإضافة لـ retry/backoff فـ llm_backend.py كخط دفاع ثاني).
    LLM_REQUEST_DELAY_SECONDS = float(os.environ.get("LLM_REQUEST_DELAY_SECONDS", "2.0"))

    # ==================== إعدادات المحتوى ====================
    SUPPORTED_LANGUAGES = ["python", "javascript"]
    CONTENT_TYPES = ["code", "slide", "mixed"]
    NARRATION_LANGUAGE = "en"  # الشرح دائمًا بالإنجليزية

    # طول الفيديو المستهدف: ~30 دقيقة، عبر توليد على مرحلتين (outline ثم
    # تفصيل كل segment على حدة) باش يبقى الـ JSON صغير وموثوق ولا يتقطعش
    TARGET_VIDEO_MINUTES = (28, 32)
    WORDS_PER_MINUTE = 150  # تقدير سرعة الراوي (لتخطيط عدد الكلمات فقط)
    SEGMENTS_RANGE = (22, 30)
    TOTAL_NARRATION_WORDS_RANGE = (4300, 5100)

    # ==================== إعدادات الفيديو ====================
    VIDEO_WIDTH = 1920
    VIDEO_HEIGHT = 1080
    VIDEO_FPS = 30

    # ==================== إعدادات التحقق من الكود ====================
    CODE_EXECUTION_TIMEOUT_SECONDS = 15
    MAX_CODE_FIX_ATTEMPTS = 2
    SHOW_EXECUTION_DEFAULT = True  # يبان "ترمينال" بعد كتابة الكود بالنتيجة

    # ==================== الموسيقى الخلفية ====================
    # ملفات mp3/wav حرة الاستعمال يزيدها المستخدم بنفسو، شوف music/README.md.
    # الهيكل: music/coding/*.mp3 (فرشة وقت الكتابة) ، music/slide/*.mp3
    # (فرشة الشرائح) ، music/execution/*.mp3 (صوت قصير لحظة تشغيل الكود).
    # إذا مجلد معين خاوي، الرندر كيكمّل عادي بلا موسيقى (skip تلقائي).
    MUSIC_ENABLED = os.environ.get("MUSIC_ENABLED", "true").lower() == "true"
    MUSIC_VOLUME = float(os.environ.get("MUSIC_VOLUME", "0.14"))       # فرشة الموسيقى
    STINGER_VOLUME = float(os.environ.get("STINGER_VOLUME", "0.22"))  # صوت لحظة التنفيذ

    # ==================== إعدادات الرفع ====================
    AUTO_UPLOAD = os.environ.get("AUTO_UPLOAD", "true").lower() == "true"
    UPLOAD_PRIVACY = os.environ.get("UPLOAD_PRIVACY", "public")

    @classmethod
    def ensure_dirs(cls):
        for d in (cls.DATA_DIR, cls.OUTPUT_DIR, cls.SANDBOX_DIR, cls.MUSIC_DIR):
            os.makedirs(d, exist_ok=True)

    @classmethod
    def display(cls):
        print("\n" + "=" * 60)
        print("⚙️  CONFIGURATION - Coding Tutorials (30-min / every 12h)")
        print("=" * 60)
        print(f"LLM_BACKEND:           {cls.LLM_BACKEND}")
        print(f"GROQ_API_KEY:          {'✅ set' if cls.GROQ_API_KEY else '❌ missing'}")
        print(f"TARGET_VIDEO_MINUTES:  {cls.TARGET_VIDEO_MINUTES}")
        print(f"SEGMENTS_RANGE:        {cls.SEGMENTS_RANGE}")
        print(f"SUPPORTED_LANGUAGES:   {cls.SUPPORTED_LANGUAGES}")
        print(f"MUSIC_ENABLED:         {cls.MUSIC_ENABLED}")
        print(f"AUTO_UPLOAD:           {cls.AUTO_UPLOAD}")
        print("=" * 60 + "\n")
