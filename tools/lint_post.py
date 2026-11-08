#!/usr/bin/env python3
"""Check a post.json against the format + depth rules before building.
  python3 tools/lint_post.py reels/<date>[/am]/post.json   -> exit 1 on any ERROR (WARN lines are advice)
tools/build.py runs this automatically for files under reels/ (set NO_LINT=1 to skip, e.g. for old posts).
"""
import json, re, sys

def words(t): return len(re.sub(r'[*❌✅💡⚠️🎬👉]', ' ', t or '').split())
def emojiless_end(t): return not re.search(r'[\U0001F300-\U0001FAFF☀-➿]\s*$', t or '')

def lint(path):
    post = json.load(open(path, encoding='utf-8')); S = post.get('slides', []); E, W = [], []
    types = [s.get('type', 'point') for s in S]
    if types != ['cover'] + ['point'] * 5 + ['cta']: E.append(f'slides must be cover, 5 points, cta (got {types})')
    src = [u for u in post.get('sources', []) if str(u).startswith('http')]
    if len(src) < 3: E.append('add "sources": at least 3 URLs you used to verify the apps/features (not shown in the video)')
    hero = post.get('hero') or {}
    if not hero.get('name') or not hero.get('emoji'): E.append('add "hero": {"name": "<everyday Egyptian name>", "emoji": "<one emoji>"} (the story\'s main character)')
    elif hero['name'] not in S[0].get('title', '') + S[0].get('subtitle', ''): W.append(f'cover should introduce the hero by name ({hero["name"]})')
    spoken = 0; prompts = paths = extras = 0
    for i, s in enumerate(S, 1):
        t = s.get('type', 'point'); title = s.get('title', ''); tl = title.split('\n')
        hl = re.findall(r'\*([^*]+)\*', title)
        if len(hl) != 1 or len(hl[0].split()) != 1: E.append(f'slide {i}: title needs exactly ONE *word* highlight (got {hl})')
        spoken += words(title)
        if t == 'cover':
            if len(tl) > 3: E.append(f'slide {i}: cover title max 3 lines')
            spoken += words(s.get('subtitle'))
        elif t == 'cta':
            if words(s.get('body')) > 12: E.append(f'slide {i}: cta body max 12 words')
            spoken += words(s.get('body'))
        else:
            body = s.get('body', ''); lines = [l for l in body.split('\n') if l.strip()]
            if len(tl) != 2: E.append(f'slide {i}: point title must be exactly 2 lines')
            if not any(l.strip().startswith('🎬') for l in lines) or not any(l.strip().startswith('👉') for l in lines):
                E.append(f'slide {i}: body needs a "🎬" story line (what happened to the hero) and a "👉" line (what they did with AI)')
            if re.search(r'❌|✅|زمان:|دلوقتي:', body): E.append(f'slide {i}: the old "❌ زمان / ✅ دلوقتي" format is retired; tell the story with 🎬 / 👉')
            if words(body) > 30: E.append(f'slide {i}: body {words(body)} words (max 30)')
            if not emojiless_end(body): W.append(f'slide {i}: body ends with an emoji (breaks RTL)')
            if re.search(r'(^|\s)و[A-Za-z]', body + ' ' + s.get('prompt', '')): W.append(f'slide {i}: put a space between "و" and an English word')
            tag = s.get('tag', '')
            if len(tag) > 18 or re.search(r'[؀-ۿ]', tag): E.append(f'slide {i}: tag must be Latin, max 18 chars ("{tag}")')
            if s.get('prompt'):
                prompts += 1
                if words(s['prompt']) > 22: E.append(f'slide {i}: prompt {words(s["prompt"])} words (max 22)')
                spoken += words(s['prompt']) + 1
            if s.get('path'):
                paths += 1
                if len(s['path']) > 4 or any(len(x) > 18 for x in s['path']): E.append(f'slide {i}: path = max 4 taps, each max 18 chars')
            extras += any(l.strip()[:1] in '💡⚠' for l in lines)
            spoken += words(body)
    if prompts < 2: E.append(f'DEPTH: only {prompts} point(s) have a "prompt"; give at least 2 ready-to-copy prompts')
    if paths < 2: W.append(f'DEPTH: only {paths} point(s) have a "path"; show the exact taps on most slides')
    if not extras: W.append('DEPTH: no 💡 (pro tip) or ⚠️ (limit/privacy) line anywhere; one honest caveat builds trust')
    # the storyteller voice reads ~1.7-2 words/s: ~105 words fits 60 s without speeding the voice up
    if spoken > 125: E.append(f'{spoken} spoken words (aim for ~105): the voice gets sped up / the Reel runs over 60 s; cut text')
    elif spoken > 110: W.append(f'{spoken} spoken words: the voice will be sped up a little; ~105 is ideal')
    return E, W, spoken

if __name__ == '__main__':
    E, W, n = lint(sys.argv[1])
    for w in W: print('WARN ', w)
    for e in E: print('ERROR', e)
    if E: sys.exit(f'{len(E)} lint error(s): fix post.json and rebuild')
    print(f'lint ok ({n} spoken words)')
