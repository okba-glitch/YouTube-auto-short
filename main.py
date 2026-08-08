#!/usr/bin/env python3
"""
main.py - المشروع الكامل: توليد سكريبت (outline ثم تفصيل كل segment) →
تحقق/تصحيح الكود فـ sandbox → توليد صوت لكل segment (Piper/gTTS، إنجليزي) →
رندر كل segment (كود يتكتب + "ترمينال" وقت التنفيذ، أو slide) بموسيقى
خلفية خافتة → تجميع الفيديو النهائي (~28-32 دقيقة) → رفع ليوتيوب
(long-form). يشتغل مرة كل 12 ساعة عبر .github/workflows/tutorial.yml.
"""
import os
import random
import sys
import time

from src.config import Config
from src.logger import Logger
from src.groq_integration import generate_tutorial_script, fix_code_with_groq
from src.code_validator import validate_and_fix_segments
from src.tts_engine import generate_audio
from src.render_engine import render_segment
from src.video_assembler import assemble_final_video
from src.notifications import send_discord_notification

Config.ensure_dirs()
TOPICS_FILE = os.path.join(Config.BASE_DIR, "topics.txt")


def load_topics():
    try:
        with open(TOPICS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        Logger.error(f"Error loading topics: {e}")
        return ["Understanding Python decorators"]


def pick_topic():
    return random.choice(load_topics())


def build_script(topic, language):
    Logger.info(f"🎓 Generating tutorial script: {topic}")
    script = generate_tutorial_script(topic, language)
    if not script:
        Logger.error("Script generation failed")
        return None

    Logger.info(f"🧩 {len(script['segments'])} segments planned — validating code in sandbox...")

    def fix_callback(lang, broken_code, error):
        return fix_code_with_groq(lang, broken_code, error, topic=topic)

    all_valid, script = validate_and_fix_segments(script, fix_callback)
    if not all_valid:
        Logger.error("Code validation failed after retries — rejecting tutorial")
        return None

    Logger.success("Script generated and all code validated ✅")
    return script


def render_full_video(script, work_dir):
    """يولد صوت + فيديو لكل segment، ويرجع لائحة clips مرتبة."""
    language = script.get("language", "python")
    clip_paths = []

    for i, seg in enumerate(script["segments"]):
        Logger.info(f"[Segment {i+1}/{len(script['segments'])}] type={seg['type']}: {seg['title']}")

        audio_path = os.path.join(work_dir, f"audio_{i}.wav")
        result_path, duration = generate_audio(
            seg["narration"], audio_path, language=Config.NARRATION_LANGUAGE
        )
        if not result_path:
            Logger.error(f"Segment {i} audio generation failed")
            return None

        seg["_language"] = language  # يستعمل من render_engine للـ syntax highlighting
        clip_path = render_segment(seg, result_path, duration, work_dir, i)
        if not clip_path:
            Logger.error(f"Segment {i} rendering failed")
            return None

        clip_paths.append(clip_path)
        Logger.success(f"[Segment {i+1}/{len(script['segments'])}] rendered ✅")

    return clip_paths


def generate_and_upload_tutorial(topic=None, language="multi"):
    try:
        topic = topic or pick_topic()
        Logger.info("=" * 60)
        Logger.info(f"🎬 Starting tutorial generation: {topic}")
        Logger.info("=" * 60)

        script = build_script(topic, language)
        if not script:
            send_discord_notification(f"Tutorial generation failed (script/code) for: {topic}", is_error=True)
            return False

        ts = int(time.time())
        work_dir = os.path.join(Config.OUTPUT_DIR, f"work_{ts}")
        os.makedirs(work_dir, exist_ok=True)

        clip_paths = render_full_video(script, work_dir)
        if not clip_paths:
            send_discord_notification(f"Tutorial rendering failed for: {topic}", is_error=True)
            return False

        final_path = os.path.join(Config.OUTPUT_DIR, f"tutorial_{ts}.mp4")
        result = assemble_final_video(clip_paths, final_path)
        if not result:
            send_discord_notification(f"Final video assembly failed for: {topic}", is_error=True)
            return False

        Logger.success(f"Tutorial video ready: {result}")

        if Config.AUTO_UPLOAD:
            from src.uploader import YouTubeUploader
            uploader = YouTubeUploader()
            video_id = uploader.upload_video(
                video_path=result,
                title=script.get("title", topic),
                description=script.get("description", ""),
                tags=script.get("tags"),
            )
            if video_id:
                url = f"https://youtube.com/watch?v={video_id}"
                Logger.success(f"Uploaded: {url}")
                send_discord_notification(f"New tutorial uploaded: {url}")
                return True
            else:
                send_discord_notification(f"Upload failed for: {topic}", is_error=True)
                return False
        else:
            Logger.info("Auto-upload disabled — video ready in output/")
            return True

    except Exception as e:
        Logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        send_discord_notification(f"Unexpected error: {e}", is_error=True)
        return False


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "--once":
        success = generate_and_upload_tutorial()
        sys.exit(0 if success else 1)
    elif args[0] == "--topic" and len(args) > 1:
        success = generate_and_upload_tutorial(" ".join(args[1:]))
        sys.exit(0 if success else 1)
    elif args[0] == "--config":
        Config.display()
    else:
        print("Usage: python main.py [--once] [--topic 'topic name'] [--config]")
