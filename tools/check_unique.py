#!/usr/bin/env python3
"""Make sure a new Reel does not repeat anything already published (or queued) in reels/.
  python3 tools/check_unique.py reels/<date>[/am]/post.json   -> exit 1 + list of repeats if any slide is too close to an older one
  python3 tools/check_unique.py --list                         -> every app + action already used (read this BEFORE choosing topics)
  python3 tools/check_unique.py --all                          -> audit the whole archive
Compared per slide: title, the "دلوقتي" action line, and the cover title (normalised, fuzzy match), plus the same app doing the same job.
"""
import difflib, glob, json, os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
def norm(t): return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', ' ', re.sub(r'[ًٌٍَُِّْـ]', '', t.replace(' ', ' ')))).strip().lower()
def sim(a, b): return difflib.SequenceMatcher(None, a, b).ratio()
APPS = set('chatgpt gemini google maps translate docs photos canva whatsapp business lens chrome youtube drive keep live voice meta galaxy iphone android samsung capcut adobe express gboard remove'.split())
def feats(text):
    return {w for w in re.findall(r'[a-z]{4,}', text) if w not in APPS}   # feature names like "guided learning", "scan", "captions"
def items(path):
    """(kind, tag, text) for every comparable thing in a post."""
    out = []
    for i, s in enumerate(json.load(open(path, encoding='utf-8'))['slides']):
        t = s.get('type', 'point')
        if t == 'cover': out.append(('cover', '', norm(s.get('title', ''))))
        elif t == 'point':
            out.append(('title', s.get('tag', ''), norm(s.get('title', ''))))
            act = [l for l in s.get('body', '').split('\n') if '✅' in l or 'دلوقتي' in l]
            if act: out.append(('action', s.get('tag', ''), norm(re.sub(r'.*دلوقتي', '', act[0]))))
    return out
def posts(): return sorted(p for p in glob.glob(os.path.join(ROOT, 'reels', '**', 'post.json'), recursive=True))
def compare(path, others):
    mine = items(path); bad = []
    for o in others:
        for k, tag, txt in mine:
            for k2, tag2, txt2 in items(o):
                if k != k2 or not txt or not txt2: continue
                r = sim(txt, txt2)
                same_feature = k == 'action' and tag == tag2 and bool(feats(txt) & feats(txt2))   # same app + same named feature = same idea
                if (k == 'cover' and r > .72) or (k == 'title' and r > .78) or (k == 'action' and (r > .66 or (tag and tag == tag2 and r > .72))) or same_feature:
                    bad.append((os.path.relpath(o, ROOT), k, tag, txt, txt2, r))
    return bad
if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else '--list'
    if a == '--list':
        for p in posts():
            print('#', os.path.relpath(os.path.dirname(p), os.path.join(ROOT, 'reels')))
            for k, tag, txt in items(p):
                if k != 'title': print(f'   {k:6} {tag:16} {txt[:90]}')
    elif a == '--all':
        ps = posts(); n = 0
        for i, p in enumerate(ps):
            for b in compare(p, ps[:i]): n += 1; print(f'{os.path.relpath(p, ROOT)} ~ {b[0]} [{b[1]} {b[2]}] {b[5]:.2f}: {b[3][:50]} | {b[4][:50]}')
        print(n, 'repeats in archive')
    else:
        me = os.path.abspath(a); others = [p for p in posts() if os.path.abspath(p) != me]
        bad = compare(me, others)
        for b in bad: print(f'REPEAT ({b[5]:.2f}) {b[1]} [{b[2]}] "{b[3][:60]}" ~ {b[0]}: "{b[4][:60]}"')
        if bad: sys.exit(f'{len(bad)} repeated item(s): change those slides to a NEW idea, then rebuild')
        print('unique: nothing repeated from earlier Reels')
