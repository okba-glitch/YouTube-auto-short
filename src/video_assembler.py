"""
video_assembler.py - يجمع كل clips ديال الـ segments (كل وحد فيه صورة+صوت+
موسيقى) فـ فيديو نهائي واحد بـ ffmpeg concat.
"""
import os
import subprocess

from src.logger import Logger


def assemble_final_video(segment_clip_paths, out_path):
    """
    segment_clip_paths: لائحة مرتبة ديال مسارات clips (.mp4) لكل segment.
    يرجّع out_path عند النجاح، أو None عند الفشل.
    """
    if not segment_clip_paths:
        Logger.error("No segment clips to assemble")
        return None

    list_path = out_path + "_concat.txt"
    with open(list_path, "w", encoding="utf-8") as f:
        for p in segment_clip_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
        "-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart",
        out_path,
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=900)
    os.remove(list_path)

    if result.returncode != 0:
        Logger.error(f"Final assembly failed: {result.stderr.decode(errors='ignore')[:400]}")
        return None

    if not os.path.exists(out_path):
        return None

    Logger.success(f"Final video assembled: {out_path}")
    return out_path
