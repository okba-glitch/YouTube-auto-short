"""
description_generator.py - توليد الوصف والهاشتاجات التلقائية لكل فيديو

يستخدم نفس AI backend (Groq/Ollama) لتوليد وصف احترافي و5 هاشتاجات
ذات صلة مباشرة بالموضوع.
"""

import json
import time
from src.config import Config
from src.logger import Logger
from src.llm_backend import query_llm


DESCRIPTION_AND_HASHTAGS_SYSTEM_PROMPT = """You are a YouTube content strategist specializing in programming tutorials.
Your task is to generate a compelling YouTube video description and 5 relevant hashtags.

DESCRIPTION REQUIREMENTS:
- 2-3 sentences, 80-120 words maximum
- Clearly state what viewers will learn
- Mention prerequisites (if any)
- Suggest next related topics
- Professional, engaging tone (no hype or clickbait)

HASHTAGS REQUIREMENTS:
- Exactly 5 hashtags
- All lowercase, no spaces
- Searchable and relevant to the tutorial topic
- Mix of popular and niche hashtags
- Start each with # symbol

Output ONLY valid JSON (no markdown, no preamble) with these exact keys:
- "description": single string (encode newlines as \\n)
- "hashtags": array of 5 strings, each starting with #

REMINDER: Your entire output must be ONE valid JSON object, parseable by a strict JSON parser.
Escape every newline inside string values as \\n, never a raw newline character.
"""


def build_description_user_prompt(title, topic, overview, language):
    """بناء prompt للمستخدم لتوليد الوصف والهاشتاجات"""
    return (
        f"Tutorial Title: {title}\n"
        f"Topic: {topic}\n"
        f"Programming Language: {language}\n"
        f"Content Overview: {overview}\n\n"
        f"Generate the description and 5 hashtags now as JSON."
    )


def generate_description_and_hashtags(title, topic, overview, language="python"):
    """
    توليد الوصف والهاشتاجات الخاصة بالفيديو
    
    Args:
        title: عنوان الفيديو
        topic: الموضوع الرئيسي
        overview: ملخص المحتوى
        language: لغة البرمجة
        
    Returns:
        dict: {"description": "...", "hashtags": ["#tag1", ...]} أو None إذا فشل
    """
    Logger.info("🏷️  Generating video description and hashtags...")
    
    user_prompt = build_description_user_prompt(title, topic, overview, language)
    
    time.sleep(Config.LLM_REQUEST_DELAY_SECONDS)
    
    response = query_llm(
        system_prompt=DESCRIPTION_AND_HASHTAGS_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_tokens=300,
        temperature=0.7
    )
    
    if not response:
        Logger.error("Failed to generate description and hashtags")
        return None
    
    try:
        data = json.loads(response, strict=False)
        
        # التحقق من المفاتيح المطلوبة
        if "description" not in data or "hashtags" not in data:
            Logger.error("Response missing 'description' or 'hashtags' keys")
            return None
        
        # التحقق من أن الهاشتاجات 5 بالضبط
        if not isinstance(data["hashtags"], list) or len(data["hashtags"]) != 5:
            Logger.warning(f"Expected 5 hashtags, got {len(data.get('hashtags', []))}")
            # نأخذ أول 5 أو نملأ بـ placeholders
            hashtags = data.get("hashtags", [])[:5]
            while len(hashtags) < 5:
                hashtags.append(f"#programming{len(hashtags)}")
            data["hashtags"] = hashtags
        
        Logger.success("Description and hashtags generated ✅")
        return data
        
    except json.JSONDecodeError as e:
        Logger.error(f"Failed to parse description/hashtags JSON: {e}")
        return None
    except Exception as e:
        Logger.error(f"Error generating description/hashtags: {e}")
        return None


def enhance_script_with_metadata(script, title=None, topic=None):
    """
    إضافة الوصف والهاشتاجات إلى السكريبت إذا لم تكن موجودة
    
    Args:
        script: dict السكريبت الكامل
        title: عنوان الفيديو (اختياري - سيتم استخراجه من script إذا لم يتم توفيره)
        topic: الموضوع (اختياري)
        
    Returns:
        dict: السكريبت المحسّن
    """
    title = title or script.get("title", "Programming Tutorial")
    topic = topic or script.get("title", "Programming")
    overview = script.get("description", "Learn important programming concepts")
    language = script.get("language", "python")
    
    # إذا كانت الهاشتاجات موجودة بالفعل، لا نعيد توليدها
    if script.get("hashtags"):
        return script
    
    meta = generate_description_and_hashtags(title, topic, overview, language)
    
    if meta:
        script["description"] = meta.get("description", script.get("description", ""))
        script["hashtags"] = meta.get("hashtags", script.get("hashtags", []))
    
    return script
