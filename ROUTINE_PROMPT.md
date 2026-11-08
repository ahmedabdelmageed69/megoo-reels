# Instructions for the daily Reels routine

(The scheduled task only says: "Open ROUTINE_PROMPT.md in the megoo-reels repo on main and follow it exactly." Edit THIS file on GitHub to change how the Reels are made.)

You make TOMORROW's two Instagram Reels for MeGo's account @_megoo.me (8 AM and 8 PM Cairo) and hand them to the auto-publisher.

MISSION: help everyday Arabic-speaking people (Egypt/Arab world, NOT developers) see how things that used to be hard are now easy with AI. Every Reel must leave a normal person thinking "I didn't know AI could do THAT, and I can do it today from my phone." Simple Egyptian colloquial, no jargon. Core format: a SHORT STORY. One everyday character (the "hero") has a real problem, and each slide is a chapter where they use AI to get one step closer to solving it. (The old "❌ زمان / ✅ دلوقتي" format is retired; the build rejects it.) Read CLAUDE.md first and follow every rule in it.

SCHEDULE NOTE: run this task every evening (about 9 PM Cairo). D = tomorrow's Cairo date: D=$(TZ=Africa/Cairo date -d tomorrow +%F). Weekday theme = weekday of D.

HOW PUBLISHING WORKS: push to main only (never a claude/ branch). GitHub Actions posts reels/$D/am/reel.mp4 at 05:00 UTC (8 AM Cairo) and reels/$D/reel.mp4 at 17:00 UTC (8 PM Cairo). Never post to Instagram yourself, never edit workflows or secrets.

0. NO REPEATS (hard rule). First run `python3 tools/check_unique.py --list` and read it: every app/feature/action/prompt ever used. Never reuse an idea, feature, prompt or trick from it (even reworded), and the two Reels of the day must differ from each other. If a build says REPEATED CONTENT, replace those slides with genuinely new, verified ideas.

1. DEPTH OVER BREADTH: "ONE JOB, FIVE LEVELS DEEP" (the most important rule).
  Each Reel solves ONE specific real-life job a normal Egyptian has (examples of the kind of job: understand a lab-results sheet, answer a landlord's WhatsApp politely, plan a week of cheap meals from what's in the fridge, turn a voice note into a written complaint, prepare a child for tomorrow's exam). NOT "5 random tips about an app".
  Tell it as the hero's story. The HERO: a named, believable Egyptian everyday person (e.g. سارة موظفة، عم حسن صاحب محل، مازن طالب ثانوي، أم يوسف، الحاج محمود على المعاش), with a different name/age/role in every Reel (never the same hero twice in a row, and the AM and PM heroes must differ). The cover introduces the hero BY NAME and their problem in one line, the 5 chapters follow them step by step, and the CTA is the happy ending + "وإنت كمان تقدر".
  The 5 chapters (point slides) go deeper step by step on that ONE job:
    1) the first win: the simplest way AI does the job (exact app + exact prompt);
    2) make the result better (a smarter prompt: table, shorter, in Egyptian, as a voice note…);
    3) the level most people never reach (compare, combine two files, use the camera/voice/Live, follow up);
    4) turn it into action (a message, a list, a reminder, questions for the doctor/teacher/boss…);
    5) a pro move or an honest limit: 💡 something even heavy users miss, or ⚠️ what AI gets wrong / what to never send it (privacy, medical, money). This honesty is what makes people trust and save the Reel.
  It must be REAL AI (generative AI, AI camera/voice/translation/editing, assistants). Plain phone settings (crop, recycle bin, snooze, focus modes, reminders) are NOT AI: never make a Reel or a slide out of them.
  Never use anything a normal person already knows. Self-test each slide: "would my uncle who uses WhatsApp and Facebook learn something new from this slide?" If not, replace it.

2. TOPICS + RESEARCH (two DIFFERENT jobs).
  8 PM Reel: theme by weekday of D (Sat work & career; Sun study & learning; Mon photos & design; Tue daily life & home; Wed small business; Thu hidden AI features on phones/WhatsApp/Google; Fri one new AI feature or free tool from the last 1–2 weeks).
  8 AM Reel: a different quick-win job for the morning (messages, planning the day, commute, breakfast/meals, kids, health…), never the same apps/angle as the 8 PM Reel.
  FRESHNESS: each Reel must include at least one feature/update released or expanded in the last ~30 days (search the official blogs/news: Google/Gemini, OpenAI/ChatGPT, Meta AI/WhatsApp, Samsung Galaxy AI, Apple, Microsoft Copilot, CapCut/Canva…). Say it naturally ("جديد", "نزلت الشهر ده").
  Process: search, list ~8 candidate jobs/features, score each on (new? / useful for a normal Egyptian? / free and available in Egypt and in Arabic? / can be shown in taps + a prompt?), pick the best two. Verify every app/feature exists, is available now and works as described in 2 sources; never invent features, numbers or prices. Put the URLs you used in "sources" in post.json (not shown in the video; the build refuses a post without ≥ 3).

3. FILES. Evening: reels/$D/post.json. Morning: reels/$D/am/post.json. Format:
{"hero":{"name":"سارة","emoji":"👩"},
 "sources":["https://…","https://…","https://…"],
 "slides":[{"type":"cover","kicker":"AI Tips","emoji":"🧪","title":"…","subtitle":"…"},
  {"type":"point","title":"…","body":"🎬 …\n👉 …","path":["Gemini","+","Camera"],"prompt":"…","tag":"AppName"},
  …,{"type":"cta","title":"…","body":"…"}]}
  7 slides: cover, 5 points, cta. "hero" = the character's name + ONE emoji; it is shown as a chip on every chapter so the story feels continuous, and the hero emoji is the big cover emoji unless the cover sets its own "emoji". Cover title ≤ 3 short lines: the hero by name + the problem (e.g. "سارة مش *فاهمة*\nورقة التحاليل"). Point titles are what the hero DID, in past tense (صوّرت الورقة، طلبت جدول…). CTA title = the ending (e.g. "سارة خرجت\n*مطمّنة*"), body = "وإنت كمان تقدر…" + send it to someone. Point title exactly 2 lines (~14 chars each); body ≤ 30 words; tag ≤ 18 Latin chars; cta body ≤ 12 words. *word* = highlight pill, exactly 1 single word per title.
  "prompt" = the EXACT words to type or say to the AI, in natural Egyptian Arabic (≤ 22 words). It is shown as a chat box that types itself and is read aloud as "اكتب: …". At least 2 points need one; 3–4 is better. Prompts are the most saved part of the Reel: make them specific and genuinely useful (role, format, length, dialect), not "اسأله عن…".
  "path" = the exact taps, max 4 chips (each ≤ 18 chars, app/button names as they appear on screen), e.g. ["WhatsApp","Meta AI","Camera"]. Shown as chips, NOT read aloud, so don't repeat the taps word for word in the 👉 line; use it on most points.
  Body lines: "🎬 …" = the story moment (what happened to the hero, how they felt; a tiny scene, past tense) and "👉 …" = what they did with AI (the action). Optional third line "💡 …" (pro tip) or "⚠️ …" (limit/privacy) gets its own card; use one somewhere in the Reel. Keep the story flowing: each 🎬 line follows from the previous chapter (e.g. "بس الأرقام لسه ملخبطاها", "افتكرت تحليل السنة اللي فاتت").
  Bidi: space between Arabic "و" and an English word; never chain English names with "و"; non-breaking space inside two-word English names; don't end a body with an emoji.
  The voice reads ALL text aloud (titles, body lines, prompts; not the path), slowly and softly: keep the TOTAL spoken text to about 105 words (the build's lint counts it; above ~110 the voice gets sped up, above 125 the build refuses). Shorter bodies are better than a fast voice: let the prompt carry the detail.
  A complete example in this format: samples/lab-results.post.json (study its depth and prompts; don't copy its topic).
  Check before building: python3 tools/lint_post.py reels/$D/post.json (also runs inside the build).

4. BUILD (each Reel separately).
  pip install numpy scipy playwright (python3 -m pip …), python3 -m playwright install --with-deps chromium, ffmpeg if missing; tools/setup_fonts.sh
  python3 tools/build.py reels/$D/post.json /tmp/out_pm      and      python3 tools/build.py reels/$D/am/post.json /tmp/out_am
  The environment provides GEMINI_API_KEYS (comma-separated Gemini API keys for the voice-over; the build falls through to the next model/key when a free daily quota is spent). If the build prints "WARNING: GEMINI_API_KEY not set" or "VOICE-OVER FAILED", rebuild once (the voice split is random); if it fails again say so clearly in your final message (the Reel is then music-only) and also send a notification. If it prints "STILL TOO LONG" or the duration is over ~62 s, shorten the slide text and rebuild. OVERFLOW = shorten that slide and rebuild. LINT FAILED = fix what it lists.
  Check with Read: slide_01.png, a point slide with a prompt, the cta slide of each, and frames at ~12 s and ~45 s (ffmpeg -ss): no clipped text, broken Arabic, misplaced English; the comic panels show the narrator box, action bar, stickers, the hero and the speech bubble; the AM Reel must be the dark night-comic look and the PM Reel the light paper comic. Then cp /tmp/out_pm/reel.mp4 reels/$D/ and cp /tmp/out_am/reel.mp4 reels/$D/am/.

5. CAPTIONS. Write the website as https://megoo.me.
  reels/$D/caption.txt (evening): line 1 keyword-rich hook naming the job + emoji; 2 lines telling the hero's story in short; 3–5 ✅ bullets (one per step she/he took); the best prompt from the Reel written out in full under "📋 انسخ البرومبت:" so people can copy it; a question for comments + "احفظ البوست 🔖 وابعته لحد محتاج يعرف ده 📩"; @mention official app accounts only if sure (max 3); "تابع @_megoo.me كل يوم هتعرف حاجة جديدة تسهّل حياتك بالذكاء الاصطناعي 🚀 | التفاصيل على https://megoo.me (اللينك في البايو)"; EXACTLY 5 hashtags at the end.
  reels/$D/am/caption.txt (morning, SHORT): 2 lines (hook + one benefit) + "📋 انسخ البرومبت:" with one prompt + 1 question + "احفظ البوست 🔖 وابعته لحد محتاج يعرف ده 📩" + the follow line with https://megoo.me + EXACTLY 5 hashtags.

6. PUBLISH. git add reels/$D && git commit -m "Reels $D: <pm topic> + <am topic>" && git push origin HEAD:main (pull --rebase first if rejected). If a build or push fails, say so clearly.

7. Finish with a short summary: both jobs, apps/features covered (and which one is new this month), durations, whether the voice-over worked, and "Auto-posts at 8 AM and 8 PM Cairo. To stop one, add an empty file named HOLD next to its reel.mp4 (reels/$D/am/HOLD or reels/$D/HOLD) on GitHub before then." If anything failed or the voice-over is missing, send a PushNotification.
