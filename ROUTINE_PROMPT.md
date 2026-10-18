# Instructions for the daily Reels routine

(The scheduled task only says: "Open ROUTINE_PROMPT.md in the megoo-reels repo on main and follow it exactly." Edit THIS file on GitHub to change how the Reels are made.)

You make TOMORROW's two Instagram Reels for MeGo's account @_megoo.me (8 AM and 8 PM Cairo) and hand them to the auto-publisher.

MISSION: help everyday Arabic-speaking people (Egypt/Arab world, NOT developers) see how things that used to be hard are now easy with AI. Every Reel must leave a normal person thinking "I can do that today from my phone." Simple Egyptian colloquial, no jargon. Core format: "❌ زمان: … / ✅ دلوقتي: …". Read CLAUDE.md first and follow every rule in it.

SCHEDULE NOTE: run this task every evening (about 9 PM Cairo). D = tomorrow's Cairo date: D=$(TZ=Africa/Cairo date -d tomorrow +%F). Weekday theme = weekday of D.

HOW PUBLISHING WORKS: push to main only (never a claude/ branch). GitHub Actions posts reels/$D/am/reel.mp4 at 05:00 UTC (8 AM Cairo) and reels/$D/reel.mp4 at 17:00 UTC (8 PM Cairo). Never post to Instagram yourself, never edit workflows or secrets.

0. NO REPEATS (hard rule). First run `python3 tools/check_unique.py --list` and read it: every app/feature/action ever used. Never reuse an idea, feature or trick from it (even reworded), and the two Reels of the day must differ from each other. If a build says REPEATED CONTENT, replace those slides with genuinely new, verified ideas.

1. TOPICS (two DIFFERENT ones). 8 PM Reel: practical theme by weekday of D (Sat work & career; Sun study & learning; Mon photos & design; Tue daily life; Wed small business; Thu hidden AI features on phones/WhatsApp/Google; Fri one new AI feature or free tool from the last 1–2 weeks). 8 AM Reel: a different quick-win topic (morning routine, commute, breakfast/meals, messages, planning the day…), never the same apps/angle as the 8 PM Reel. Use web search to confirm every app/feature exists, is available now (ideally in Egypt) and works as described; verify specific facts in 2 sources; never invent features, numbers or prices. Avoid anything already in reels/ (read each post.json, including reels/*/am/post.json).

2. FILES. Evening: reels/$D/post.json. Morning: reels/$D/am/post.json. Format:
{"slides":[{"type":"cover","kicker":"AI Tips","title":"…","subtitle":"…"},{"type":"point","title":"…","body":"❌ زمان: …\n✅ دلوقتي: …","tag":"AppName"},…,{"type":"cta","title":"…","body":"…"}]}
7 slides: cover, 5 points, cta. Cover title ≤ 3 short lines; point title exactly 2 lines (~14 chars each); body ≤ 30 words; tag ≤ 18 Latin chars; cta body ≤ 12 words. *word* = highlight pill, exactly 1 single word per title. Say exactly which app and what to type/tap. Bidi: space between Arabic "و" and an English word; never chain English names with "و"; non-breaking space inside two-word English names; don't end a body with an emoji. Hook/emotion rules are in CLAUDE.md. The voice reads ALL slide text aloud, so write it to be heard (natural spoken Egyptian); keep the TOTAL text of all 7 slides to about 140 words so the Reel stays ≤ ~60 s at a natural speaking pace (shorter bodies are better than a sped-up voice).

3. BUILD (each Reel separately).
  pip install numpy scipy playwright (python3 -m pip …), python3 -m playwright install --with-deps chromium, ffmpeg if missing; tools/setup_fonts.sh
  python3 tools/build.py reels/$D/post.json /tmp/out_pm      and      python3 tools/build.py reels/$D/am/post.json /tmp/out_am
  The environment provides GEMINI_API_KEYS (comma-separated Gemini API keys for the voice-over; the build falls through to the next model/key when a free daily quota is spent). If the build prints "WARNING: GEMINI_API_KEY not set" or "VOICE-OVER FAILED", say so clearly in your final message (the Reel is then music-only) and also send a notification. If it prints "STILL TOO LONG" or the duration is over ~62 s, shorten the slide text and rebuild. OVERFLOW = shorten that slide and rebuild.
  Check with Read: slide_01.png, a point slide, the cta slide of each, and frames at ~12 s and ~45 s (ffmpeg -ss): no clipped text, broken Arabic, misplaced English, missing ❌/✅; the AM Reel must look futuristic/neon and the PM Reel must look clearly different. Then cp /tmp/out_pm/reel.mp4 reels/$D/ and cp /tmp/out_am/reel.mp4 reels/$D/am/.

4. CAPTIONS. Write the website as https://megoo.me.
  reels/$D/caption.txt (evening): line 1 keyword-rich hook naming the task + emoji; 3–5 ✅ bullets; a question for comments + "احفظ البوست 🔖 وابعته لحد محتاج يعرف ده 📩"; @mention official app accounts only if sure (max 3); "تابع @_megoo.me كل يوم هتعرف حاجة جديدة تسهّل حياتك بالذكاء الاصطناعي 🚀 | التفاصيل على https://megoo.me (اللينك في البايو)"; EXACTLY 5 hashtags at the end.
  reels/$D/am/caption.txt (morning, SHORT): 2 lines (hook + one benefit) + 1 question + "احفظ البوست 🔖 وابعته لحد محتاج يعرف ده 📩" + the follow line with https://megoo.me + EXACTLY 5 hashtags.

5. PUBLISH. git add reels/$D && git commit -m "Reels $D: <pm topic> + <am topic>" && git push origin HEAD:main (pull --rebase first if rejected). If a build or push fails, say so clearly.

6. Finish with a short summary: both topics, apps covered, durations, whether the voice-over worked, and "Auto-posts at 8 AM and 8 PM Cairo. To stop one, add an empty file named HOLD next to its reel.mp4 (reels/$D/am/HOLD or reels/$D/HOLD) on GitHub before then." If anything failed or the voice-over is missing, send a PushNotification.
