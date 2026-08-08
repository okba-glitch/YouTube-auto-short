# 🎓 Coding Tutorials Auto-Generator (v2 — فيديوهات 30 دقيقة كل 12 ساعة)

مشروع موازي لـ Terminal Shorts، لفيديوهات تعليم برمجة **طويلة (~28-32
دقيقة)**، بلغات متعددة (Python, JavaScript, ...)، كيتنشر **تلقائيًا كل
12 ساعة** عبر GitHub Actions. الشرح دائمًا بالإنجليزية، بكود يتكتب على
الشاشة بـ syntax highlighting، بـ **تشغيل حقيقي للكود وعرض نتيجته فـ
ترمينال** بعد كل مقطع كود مهم، وبموسيقى خلفية خافتة (مود مختلف وقت
الكتابة مقابل وقت التنفيذ).

## ✨ جديد فـ v2 (مقارنة بالنسخة الأولى)

| قبل | دابا |
|---|---|
| فيديو 8-20 دقيقة، 5-12 segments، نداء API واحد ضخم لكامل السكريبت | فيديو **28-32 دقيقة**، **22-30 segment**، توليد على **مرحلتين** (outline خفيف ثم تفصيل كل segment على حدة) — أوثق بزاف، ماكايتقطعش JSON |
| Groq فقط، مربوط بالكود مباشرة | طبقة `src/llm_backend.py` مجردة: **Groq (Llama مفتوح الوزن) أو Ollama محلي 100%** — بدّل بغير `LLM_BACKEND` فـ env |
| الكود كيتكتب ومنبعد كيبقى واقف | بعد الكتابة، **"ترمينال" كيبان كيشغل الكود ويطبع النتيجة الحقيقية** لي جات من الـ sandbox (`show_execution`) |
| بلا موسيقى | **موسيقى خلفية خافتة** (`src/audio_mixer.py`) بمود مختلف: `coding` وقت الكتابة، `slide` وقت الشرح، `execution` (stinger قصير) لحظة تشغيل الكود |
| hook عادي | برومبت مخصص للـ hook (أول 15-20 ثانية): مشكلة/سؤال/معلومة مفاجئة + وعد واضح، ممنوع "In this video / Hi guys" |
| ماكاين شي جدولة | `.github/workflows/tutorial.yml` — cron **كل 12 ساعة**، رفع تلقائي ليوتيوب |

## 🧠 كيفاش كيخدم توليد السكريبت (مرحلتين)

1. **Outline** (`src/ai_prompts.py::OUTLINE_SYSTEM_PROMPT`): نداء واحد
   كيخطط الفيديو كامل — العنوان، الوصف، الـ tags، ولائحة "stubs" لكل
   segment (نوعه، عنوانه، هدفه، عدد كلمات مستهدف، وهل نبانو تنفيذه).
   مجموع الكلمات المستهدفة عبر كل الـ segments محسوب باش يعطي ~30 دقيقة
   (`Config.TOTAL_NARRATION_WORDS_RANGE`، افتراضيًا 4300-5100 كلمة عند
   150 كلمة/دقيقة).
2. **Detail** (`SEGMENT_SYSTEM_PROMPT`): نداء منفصل لكل segment، فيه
   السياق (الكود السابق إذا كاين، موقع الـ segment فالفيديو) — كيرجع
   narration + code/bullets كاملين. هادشي كيخلي كل نداء صغير وموثوق.
3. الكود كيتفحص فورًا فـ `code_validator.py` (sandbox حقيقي)، وإذا فشل
   كيتصحح تلقائيًا (حتى محاولتين) عبر نفس الـ backend.

## 📋 الـ pipeline كامل

| الملف | الدور |
|---|---|
| `src/config.py` | إعدادات مركزية (طول الفيديو، الموسيقى، الـ backend...) |
| `src/ai_prompts.py` | برومبتات outline + segment detail + hook rules |
| `src/llm_backend.py` | طبقة تجريد: Groq (Llama مفتوح الوزن) أو Ollama محلي |
| `src/groq_integration.py` | يبني السكريبت الكامل عبر outline→segments، + تصحيح الكود |
| `src/code_validator.py` | ⭐ ينفذ كل كود فعليًا فـ sandbox، يصلحه تلقائيًا، يحفظ مخرجات التنفيذ الحقيقية |
| `src/tts_engine.py` | Piper (محلي، مفتوح المصدر) + gTTS (fallback)، إنجليزي دائمًا |
| `src/render_utils.py` | خطوط، word-wrap، ألوان الموضوع الموحدة |
| `src/render_engine.py` | كود يتكتب تدريجيًا (Pygments) + "ترمينال" وقت التنفيذ، أو slide ببوليطات |
| `src/audio_mixer.py` | ⭐ يخلط الراوي مع موسيقى خلفية خافتة (mood حسب نوع الـ segment) |
| `src/video_assembler.py` | يجمع كل clips فـ فيديو نهائي واحد |
| `src/uploader.py` | رفع ليوتيوب كـ long-form video (category: Education) |
| `main.py` | يربط الـ pipeline كامل من الألف للياء |
| `topics.txt` | لائحة مواضيع برمجة (Python + JS) — واحد كيتختار عشوائيًا كل تشغيلة |
| `.github/workflows/tutorial.yml` | ⭐ تشغيل تلقائي **كل 12 ساعة** (cron) |
| `music/README.md` | مصادر مقترحة للموسيقى الحرة + الهيكل المطلوب |

## 🤖 الـ AI: مفتوح المصدر بالكامل

- **افتراضيًا**: Groq Cloud كيستضيف **Llama 3.3 70B** من Meta — نموذج
  **مفتوح الوزن** (مش نموذج مغلق كـ GPT/Gemini)، والاستضافة مجانية بحدود
  معقولة. `GROQ_API_KEY` مجاني من console.groq.com.
- **بديل محلي 100%**: بدّل `LLM_BACKEND=ollama` فـ `.env`، ثبت
  [Ollama](https://ollama.com) وشغّل `ollama pull llama3.1:70b` (أو أي
  نموذج مفتوح آخر: qwen2.5, mistral...) — بلا إنترنت ولا API key نهائيًا.
- **TTS**: Piper هو المحرك الأساسي — مفتوح المصدر بالكامل ويشتغل محليًا
  بلا إنترنت. gTTS كـ fallback فقط إذا نموذج Piper مامحملش.

## 🎬 الرندر: كود + ترمينال حقيقي + موسيقى

كل segment نوع "code":
1. الكود كيتكتب تدريجيًا سطر سطر (syntax highlighting بـ Pygments).
2. إذا `show_execution` = true، كيبان "ترمينال" كيقول running… ومنبعد
   **النتيجة الحقيقية** اللي طلعت من تنفيذ نفس الكود فـ sandbox قبل
   الرندر (`seg["_execution_output"]`) — ماشي نص مفبرك.
3. صوت الراوي كيتخلط مع فرشة موسيقى خافتة (`music/coding/`)، وفوقها
   stinger قصير (`music/execution/`) بالضبط فلحظة بداية التنفيذ.

كل segment نوع "slide" (شرح مفهوم/الـ hook/الخاتمة) كيتخلط مع فرشة
`music/slide/`. المجلدات فارغة عمدًا — زيد التراكات ديالك (شوف
`music/README.md`).

## ⏱️ الجدولة (كل 12 ساعة، تلقائي)

`.github/workflows/tutorial.yml` معدّ بـ:
```yaml
schedule:
  - cron: '0 */12 * * *'   # 00:00 و 12:00 UTC كل يوم
```
+ `workflow_dispatch` باش تقدر تشغلو يدويًا (بموضوع محدد أو عشوائي) من
تبويب Actions.

### الـ Secrets المطلوبة (Settings → Secrets and variables → Actions)
`GROQ_API_KEY`, `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`,
`YOUTUBE_REFRESH_TOKEN`, `DISCORD_WEBHOOK_URL` (اختياري).

⚠️ **ملاحظات مهمة على الجدولة:**
- ريبو **عمومي (public)** = دقائق Actions غير محدودة مجانًا. ريبو خاص
  عندو حصة شهرية محدودة (2000 دقيقة فالخطة المجانية) — فيديو 30 دقيقة
  كيدير رندر تقيل (ffmpeg بزاف من الصور)، خاصك تراقب الاستهلاك.
- `timeout-minutes: 120` فالـ workflow — راجعها إذا الرندر كيخد أكثر.
- الموسيقى ماغاديش تخدم على GitHub Actions إلا إذا `git add music/`
  وpush التراكات ديالك للريبو (ماشي محفوظة محليًا برا الريبو).

## 🚀 النشر والتجربة

```bash
cd coding-tutorials
git init && git add . && git commit -m "v2: 30-min pipeline + music + scheduling"
git branch -M main
git remote add origin https://github.com/<username>/<repo-name>.git
git push -u origin main
```

### تجربة محلية
```bash
pip install -r requirements.txt
cp .env.example .env   # عمر GROQ_API_KEY على الأقل
python main.py --config      # يتأكد الإعدادات مضبوطة
python main.py --topic "Understanding Python decorators"
# أو موضوع عشوائي من topics.txt:
python main.py --once
```
النتيجة: `output/tutorial_<timestamp>.mp4` (وإذا `AUTO_UPLOAD=true`
ومفاتيح يوتيوب مضبوطة، كينرفع تلقائيًا).

## ⚠️ نقطة أمان مهمة (باقية من v1)

`code_validator.py` كيستعمل حاليًا `subprocess` مباشر لتنفيذ الكود. هادشي
مقبول للتجربة المحلية، بصح لاستعمال إنتاجي (خصوصًا فـ GitHub Actions حيث
الكود جاي من AI بلا مراجعة بشرية)، **يُفضّل بزاف** نبدلوه بتنفيذ داخل
حاوية Docker معزولة تمامًا (`--network none`, filesystem مؤقت، بلا
صلاحيات) باش نتجنبو أي كود AI يدير حاجة ضارة بالخطأ.

## 🩹 إصلاح مهم (Aug 2026): تعطل توليد الـ outline بسبب JSON غير صالح

أول تشغيلة فـ GitHub Actions طاحت بـ:
```
Invalid control character at: line 4 column 282 (char 352)
```
السبب: الموديل (Llama عبر Groq) كان كيحط سطر جديد **حرفي** (raw newline)
داخل قيمة `"description"` (بدل `\n` مهرّب) — و`json.loads` الصارم
(`strict=True` هو الافتراضي) كيرفض أي control character خام داخل
string. تم الإصلاح فـ `src/groq_integration.py`:
- `json.loads(..., strict=False)` كخطوة أولى (كتسمح بـ control
  characters خام داخل strings — كافية لحل هاد الحالة بالضبط).
- دالة `_sanitize_json_text()` كخط دفاع ثاني (تهريب يدوي لـ
  newline/tab/carriage-return داخل quoted strings فقط) لو `strict=False`
  ماكفاش فحالات أندر.
- زيد تحذير صريح فـ `src/ai_prompts.py` للموديل باش يهرّب أي newline
  بـ `\n` من الأصل، كخط دفاع أول قبل الـ parsing.

## 🩹 إصلاح آخر (Aug 2026): تسريع الـ workflow + ملاحظة عن أخطاء GitHub نفسها

- **`.github/workflows/daily.yml`**: كان كيحمّل 9 نماذج Piper بلغات مختلفة
  (fr/es/de/pt/it/ja/zh/ar) رغم أن `Config.NARRATION_LANGUAGE` هو `"en"`
  دائمًا (الشرح إنجليزي فقط فهاد المشروع) — هادشي كان كيزيد فوقت الـ job
  بلا فايدة وكيزيد نقط فشل محتملة. دابا كيحمّل غير النموذج الإنجليزي.
- **إذا الـ workflow طاح بـ "Internal server error" أو "The job was not
  acquired by Runner... even after multiple attempts"**: هادشي **ماشي
  مشكل فـ الكود** — هو عطل مؤقت فبنية GitHub Actions نفسها (ماقدرش
  يخصص runner للـ job). الحل: `Re-run failed jobs` من صفحة الـ run، أو
  تأكد من [githubstatus.com](https://www.githubstatus.com) إذا كاين
  انقطاع عام. لا `main.py` ولا أي ملف فـ `src/` مسؤول عن هاد النوع
  ديال الخطأ.

## 📌 حدود معروفة

- ماكانقدروش نحملو ليك ملفات موسيقى حرة جاهزة فهاد المشروع (بيئة البناء
  بلا إنترنت) — خاصك تزيدهم بنفسك (`music/README.md`).
- Ollama (المسار المحلي 100%) كيحتاج جهاز عندو GPU/RAM كافية لموديل
  70B — الأخف (8B مثلاً) كيخدم بصح بجودة أقل شوية فالسكريبت.
- الـ 22-30 نداء API لكل فيديو (outline + segment لكل واحدة) كياخدو وقت
  — فيديو 30 دقيقة ممكن يخدم بين 15-40 دقيقة رندر حسب سرعة الـ runner.
