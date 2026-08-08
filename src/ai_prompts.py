"""
ai_prompts.py - البرومبتات لتوليد سكريبت تعليم برمجة طويل (~28-32 دقيقة)
على مرحلتين:
  1) OUTLINE_SYSTEM_PROMPT: يخطط الفيديو كامل (title/description/tags +
     لائحة "stubs" لكل segment: نوعه، عنوانه، هدفه، عدد كلمات مستهدف،
     وهل نبانو تنفيذ الكود فـ "ترمينال" أم لا).
  2) SEGMENT_SYSTEM_PROMPT: يفصّل segment واحد فقط (narration + code أو
     bullets) بناءً على الـ stub ديالو + الكود السابق (للاستمرارية).

هاد الفصل بين التخطيط والتفصيل كيخلي كل نداء API صغير وموثوق (JSON ماشي
كبير باش يتقطع فـ النص الناقص)، وكيسمح بفيديو طويل بعدد segments كبير
(22-30) بدل ما كنا محدودين بـ 5-12 فـ نداء واحد ضخم.
"""

# ============================================================
# المرحلة 1: OUTLINE (تخطيط الفيديو)
# ============================================================

OUTLINE_SYSTEM_PROMPT = """You are a senior software engineer and a \
YouTube educator known for HIGH-RETENTION long-form programming \
tutorials (target runtime: 28-32 minutes, narrated in English at \
~150 words/minute).

You are planning the STRUCTURE of the video only — not the full content \
yet. The video is a sequence of SEGMENTS. Each segment is either:
- "slide": a concept/comparison/recap explained with NO code on screen.
- "code": real, runnable code typed on screen and explained step by step.

HOOK RULE (segment 0, always type "slide"):
The first segment is the most important one — its narration will cover \
the first ~15-20 seconds viewers see, where most viewers decide whether \
to keep watching. Its "goal" must describe a hook using ONE of these \
techniques:
- open on a concrete, relatable problem or mistake the viewer has made
- a surprising or counter-intuitive claim about the topic
- a sharp question that creates a curiosity gap
...followed immediately by a specific, concrete promise of what the \
viewer will be able to build/understand by the end. NEVER start with \
"In this video" or "Hi guys, welcome back" — ban those phrases entirely.

CLOSING RULE (last segment, always type "slide"):
Concise recap of the 2-4 key takeaways + one specific suggested next \
topic to explore. No generic "thanks for watching, don't forget to \
subscribe" filler as the main content — one short natural line is fine \
at the very end of the narration only.

STRUCTURE:
- Segment 0: hook + promise (slide).
- Then a logical, incremental build-up: a mix of "slide" (concept/why) \
  and "code" (implementation) segments, each with a single clear goal, \
  building toward one complete, coherent project or concept mastery. \
  Prefer many small focused code segments over a few huge ones — this \
  keeps typing animations short on screen and pacing energetic.
- Last segment: recap (slide).

For EVERY segment, also decide "target_words": the approximate narration \
length (150-230 words for most segments, higher for the hook and dense \
concept explanations, lower for short transitional slides). The SUM of \
all target_words across all segments MUST be between {words_min} and \
{words_max} words — this is what makes the final video ~30 minutes long, \
so plan the number of segments and their sizes accordingly.

For "code" segments, also decide "show_execution": true if actually \
running this exact code produces output worth showing on screen (a \
printed result, a computed value, an assertion passing, a visible \
effect) — false if this segment only defines something (e.g. a class or \
function signature) with nothing meaningful to run yet.

Output ONLY valid JSON (no markdown fences, no preamble), with these \
exact keys:
- "language": programming language for "code" segments (e.g. "python", \
  "javascript"). Use "none" only if the ENTIRE video is conceptual.
- "title": specific, compelling YouTube title, max 100 characters, no \
  clickbait exaggeration.
- "description": 2-4 professional sentences on what the viewer will \
  learn, then 3-5 relevant hashtags. IMPORTANT: this is a single JSON \
  string value — do NOT put a literal newline inside it; if you want the \
  hashtags on a separate visual line, encode that as the two-character \
  escape sequence \\n inside the JSON string, never a raw line break.
- "tags": array of 8-15 relevant lowercase tags (no # symbol).
- "segments": array of {segments_min} to {segments_max} objects, each \
  with EXACTLY: "type" ("slide" or "code"), "title" (max 60 chars), \
  "goal" (1-2 sentences describing exactly what this segment must \
  accomplish and, for the hook/closing segments, which technique to \
  use), "target_words" (integer), and — for "code" segments only — also \
  "show_execution" (boolean).

Be technically accurate above all else. Plan for ONE clear learning \
outcome — depth over a shallow tour of many unrelated things.

REMINDER: your entire output must be ONE valid JSON object, parseable by \
a strict JSON parser. Escape every newline inside string values as \\n, \
every tab as \\t, and every double quote inside a string as \\".
"""


def build_outline_system_prompt(words_min, words_max, segments_min, segments_max):
    return OUTLINE_SYSTEM_PROMPT.format(
        words_min=words_min, words_max=words_max,
        segments_min=segments_min, segments_max=segments_max,
    )


def build_outline_user_prompt(topic, preferred_language):
    lang_hint = (
        "Pick whichever language best fits the topic (Python, JavaScript, "
        "or another mainstream language)."
        if preferred_language == "multi"
        else f"Use {preferred_language} for all code segments."
    )
    return (
        f"Topic: {topic}\n"
        f"{lang_hint}\n\n"
        f"Plan the outline now as JSON."
    )


# ============================================================
# المرحلة 2: SEGMENT DETAIL (تفصيل كل segment على حدة)
# ============================================================

SEGMENT_SYSTEM_PROMPT = """You are writing ONE segment of a long-form \
English-narrated programming tutorial. You will be given the segment's \
type, title and goal (from the outline), plus context. Write ONLY this \
segment, in full detail.

RULES FOR "code" SEGMENTS (CRITICAL):
- Code MUST be complete, correct, and runnable EXACTLY as written — it \
  will be executed automatically in a sandbox. If it doesn't run, the \
  whole video is discarded.
- If earlier code was given to you as context, this segment's code must \
  be the FULL updated program (previous code + this segment's changes), \
  never a diff or partial snippet, UNLESS the goal clearly calls for an \
  unrelated new example.
- Include all necessary imports. No placeholder comments like "# rest of \
  code here" — write everything out.
- If show_execution is true, make sure running the code actually prints \
  or otherwise demonstrates something worth seeing, and mention in the \
  narration that you'll run it, briefly describing what the output shows.

RULES FOR NARRATION (applies to both types):
- English only. Natural, confident, professional teacher tone. No filler \
  ("um", "so basically", excessive "alright guys").
- Length must be close to the requested target_words (±15%).
- Explain the WHY, not just the WHAT — reasoning, trade-offs, common \
  mistakes to avoid. Follow the segment's "goal" precisely.
- If this is the hook segment (index 0), follow the hook technique named \
  in the goal exactly, and never open with "In this video" or "Hi guys".
- If this is the closing segment (last), recap key takeaways and suggest \
  one next topic, ending with one short natural sign-off line.

Output ONLY valid JSON (no markdown fences, no preamble) with EXACTLY \
these keys:
- "type": must match the requested type exactly ("slide" or "code")
- "title": short segment heading (max 60 chars)
- "narration": the full spoken narration for this segment only. This is \
  a single JSON string value — encode any line breaks as \\n, never a \
  raw newline character.
- "code": the FULL, complete, runnable code (only if type is "code"; \
  omit entirely for "slide"). Encode line breaks inside this string as \
  \\n, never a raw newline character.
- "bullets": array of 2-4 short bullet points, max 12 words each (only \
  if type is "slide"; omit entirely for "code")

REMINDER: your entire output must be ONE valid JSON object, parseable by \
a strict JSON parser. Escape every newline inside string values as \\n, \
every tab as \\t, and every double quote inside a string as \\".
"""


def build_segment_user_prompt(topic, language, stub, prev_code, index, total):
    position = "FIRST segment (the hook)" if index == 0 else (
        "LAST segment (the closing recap)" if index == total - 1 else
        f"segment {index + 1} of {total}"
    )
    context = (
        f"Tutorial topic: {topic}\n"
        f"Programming language: {language}\n"
        f"Position: {position}\n\n"
        f"This segment's type: {stub['type']}\n"
        f"This segment's title: {stub['title']}\n"
        f"This segment's goal: {stub['goal']}\n"
        f"Target narration length: ~{stub.get('target_words', 180)} words\n"
    )
    if stub["type"] == "code":
        context += f"show_execution: {stub.get('show_execution', True)}\n"
    if prev_code:
        context += (
            f"\nFull code so far from the previous code segment (build on "
            f"this if continuing the same program):\n---\n{prev_code}\n---\n"
        )
    context += "\nWrite this segment now as JSON."
    return context


def build_fix_prompt(topic, language, broken_code, error_message):
    """يستعمل لما الكود يفشل فالتنفيذ، باش نطلبو من الـ AI يصلحو."""
    return (
        f"The following {language} code from a tutorial about '{topic}' "
        f"failed when executed in a sandbox.\n\n"
        f"--- CODE ---\n{broken_code}\n\n"
        f"--- ERROR ---\n{error_message}\n\n"
        f"Fix the code so it runs correctly and produces sensible output. "
        f"Output ONLY the corrected, complete code — no explanation, no "
        f"markdown fences, no comments about what you changed."
    )


# ============================================================
# التحقق (Validation)
# ============================================================

_REQUIRED_STUB_KEYS = ("type", "title", "goal", "target_words")
_REQUIRED_SEGMENT_KEYS = ("type", "title", "narration")


def validate_outline(data):
    if "segments" not in data or not isinstance(data["segments"], list):
        return False, "missing 'segments' array"

    n = len(data["segments"])
    if not (10 <= n <= 40):  # نطاق واسع كحماية إضافية فوق SEGMENTS_RANGE
        return False, f"segments count out of sane range: {n}"

    for i, stub in enumerate(data["segments"]):
        for key in _REQUIRED_STUB_KEYS:
            if key not in stub:
                return False, f"stub {i} missing key '{key}'"
        if stub["type"] not in ("slide", "code"):
            return False, f"stub {i} has invalid type '{stub['type']}'"

    if data["segments"][0]["type"] != "slide":
        return False, "first segment (hook) must be type 'slide'"
    if data["segments"][-1]["type"] != "slide":
        return False, "last segment (recap) must be type 'slide'"

    for key in ("title", "description", "tags", "language"):
        if key not in data:
            return False, f"missing top-level key '{key}'"

    return True, "ok"


def validate_segment(data, expected_type):
    for key in _REQUIRED_SEGMENT_KEYS:
        if key not in data:
            return False, f"segment missing key '{key}'"
    if data["type"] != expected_type:
        return False, f"expected type '{expected_type}', got '{data['type']}'"
    if expected_type == "code" and not data.get("code", "").strip():
        return False, "type 'code' but no code provided"
    if expected_type == "slide" and not data.get("bullets"):
        return False, "type 'slide' but no bullets provided"
    return True, "ok"


def validate_full_script(data):
    """تحقق نهائي بعد تجميع كل segments المفصّلة."""
    if "segments" not in data or not data["segments"]:
        return False, "no segments in assembled script"

    has_code_segment = False
    for i, seg in enumerate(data["segments"]):
        for key in _REQUIRED_SEGMENT_KEYS:
            if key not in seg:
                return False, f"segment {i} missing key '{key}'"
        if seg["type"] == "code":
            has_code_segment = True
            if not seg.get("code", "").strip():
                return False, f"segment {i} is type 'code' but has no code"
        if seg["type"] == "slide" and not seg.get("bullets"):
            return False, f"segment {i} is type 'slide' but has no bullets"

    if has_code_segment and not data.get("language"):
        return False, "has code segments but no 'language' specified"

    for key in ("title", "description", "tags"):
        if key not in data:
            return False, f"missing top-level key '{key}'"

    return True, "ok"
