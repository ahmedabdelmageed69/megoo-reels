#!/usr/bin/env python3
"""Voice-over for a Reel with Gemini TTS: one continuous, low, secretive, unhurried take that reads ALL the text on the slides.
The voice is made FIRST and decides how long each slide lasts (the video grows to fit the speech) and when each line appears.
  python3 tools/voiceover.py plan post.json WORKDIR              -> WORKDIR/plan.json (+ per-slide wavs)
  python3 tools/voiceover.py mix  post.json WORKDIR reel_in.mp4 reel_out.mp4
Env: GEMINI_API_KEY (required; GEMINI_API_KEYS = comma-separated list to fall through when one key's daily quota is spent), GEMINI_VOICE (default Puck), GEMINI_TTS_MODEL (default gemini-3.8-flash-tts)
A slide may carry "vo" to override what is spoken for it.
"""
import base64, json, os, re, subprocess, sys, time, urllib.error, urllib.request
X, LEAD, TAIL, MIN = 0.45, 0.5, 0.7, [3.4, 5.2, 4.6]   # xfade overlap, silence before/after the line, minimum slide time (cover, point, cta)
def run(*a): subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def clean(t): return re.sub(r'\s+', ' ', re.sub(r'[^\w\s:،؟?!.,/+\-]', ' ', t.replace(' ', ' '))).strip()
def parts(s):
    """The pieces of a slide in the order they appear (and are spoken)."""
    if s.get('vo'): return [clean(s['vo'])]
    t = s.get('type', 'point')
    if t == 'cover': return [clean(s['title']), clean(s.get('subtitle', ''))]
    if t == 'cta': return [clean(s['title']), clean(s.get('body', ''))]
    return [clean(s['title'])] + [clean(l) for l in s.get('body', '').split('\n') if l.strip()]
def dur_of(f): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))
def gemini(texts):
    arc = ('Narrate this as ONE continuous take by the same single speaker, in a natural Egyptian Arabic accent. Keep the SAME very low, quiet, secretive, intimate voice from the first word to the last, '
           'like whispering a secret to a close friend; calm and steady, never louder or more excited at the end. Speak SLOWLY, at a relaxed, unhurried pace, and read every word. '
           'Pause about one second between lines of the same section and about two seconds between sections. Sections:\n')
    body = {'contents': [{'parts': [{'text': arc + '\n\n'.join(f'Section {k+1}:\n' + '\n'.join(p) for k, p in enumerate(texts))}]}],
            'generationConfig': {'responseModalities': ['AUDIO'], 'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': os.environ.get('GEMINI_VOICE', 'Puck')}}}}}
    models = [os.environ['GEMINI_TTS_MODEL']] if os.environ.get('GEMINI_TTS_MODEL') else ['gemini-3.8-flash-tts', 'gemini-3.8-flash-lite-tts', 'gemini-3.1-flash-tts-preview']
    keys = [k.strip() for k in os.environ.get('GEMINI_API_KEYS', os.environ.get('GEMINI_API_KEY', '')).split(',') if k.strip()]
    for model, key in [(m, k) for m in models for k in keys]:   # free tier = ~10 requests a day per model and key, so fall through to the next one
        req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent', json.dumps(body).encode(),
                                     {'Content-Type': 'application/json', 'x-goog-api-key': key})
        for attempt in range(4):
            try:
                d = base64.b64decode(json.load(urllib.request.urlopen(req, timeout=240))['candidates'][0]['content']['parts'][0]['inlineData']['data']); print('voice model:', model, file=sys.stderr); break
            except urllib.error.HTTPError as e:
                msg = e.read().decode()[:3000]
                if e.code == 429 and 'PerDay' in msg: d = None; break          # daily quota gone: next model
                if attempt == 3: raise
                time.sleep(25 if e.code == 429 else 3)
            except Exception:
                if attempt == 3: raise
                time.sleep(3)
        if d: break
    else: sys.exit('every TTS model/key hit its daily free quota')
    return d if d[:4] == b'RIFF' else b'RIFF' + d
def plan(post, work):
    slides = json.load(open(post, encoding='utf-8'))['slides']; n = len(slides); os.makedirs(work, exist_ok=True)
    P = [parts(s) for s in slides]
    full = f'{work}/full.wav'; open(full, 'wb').write(gemini(P))
    log = subprocess.run(['ffmpeg', '-i', full, '-af', 'silencedetect=n=-38dB:d=0.3', '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]; en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
    total = dur_of(full); gaps = [(e - a, (a + e) / 2) for a, e in zip(st, en) if 0.3 < (a + e) / 2 < total - 0.3]
    chars = [sum(len(x) for x in p) for p in P]; cum = [0]
    for c in chars: cum.append(cum[-1] + c)
    cuts, last = [], 0.0
    for k in range(1, n):                                    # each slide boundary = the longest pause near where it should fall by text length
        exp = total * cum[k] / cum[-1]
        win = [g for g in gaps if abs(g[1] - exp) < 0.14 * total and g[1] > last + 0.3]
        if not win: sys.exit(f'could not find the pause before slide {k+1}; try again')
        m = max(win, key=lambda g: g[0] - 3 * abs(g[1] - exp) / total)[1]; cuts.append(m); last = m
    b = [0.0] + cuts + [total]; segs, durs, reveal = [], [], []
    for i in range(n):
        o = f'{work}/seg{i}.wav'
        run('ffmpeg', '-y', '-ss', f'{b[i]:.3f}', '-to', f'{b[i+1]:.3f}', '-i', full, '-af', 'silenceremove=start_periods=1:start_threshold=-42dB,areverse,silenceremove=start_periods=1:start_threshold=-42dB,areverse', '-ar', '48000', '-ac', '2', o)
        v = dur_of(o); t = 'cover' if i == 0 else 'cta' if i == n - 1 else 'point'
        segs.append(o); durs.append(round(max(MIN[['cover', 'point', 'cta'].index(t)], LEAD + v + TAIL + X), 2))
        c = [0]
        for x in P[i]: c.append(c[-1] + len(x))
        reveal.append([round(max(0.3, LEAD + v * c[j] / max(c[-1], 1) - 0.15), 2) for j in range(len(P[i]))])   # when each line starts being spoken
    json.dump({'dur': durs, 'reveal': reveal, 'segs': segs}, open(f'{work}/plan.json', 'w'))
    print('voice plan:', [f'{d:.1f}s' for d in durs], f'total ~{sum(durs) - (n - 1) * X:.0f}s', file=sys.stderr)
def mix(post, work, vin, vout):
    pl = json.load(open(f'{work}/plan.json')); n = len(pl['dur']); inputs, fl, off = [], [], 0.0
    for i in range(n):
        inputs += ['-i', pl['segs'][i]]; ms = int((off + LEAD) * 1000); fl.append(f'[{i+1}:a]adelay={ms}|{ms}[d{i}]'); off += pl['dur'][i] - X
    fl.append(''.join(f'[d{i}]' for i in range(n)) + f'amix=inputs={n}:normalize=0[vo]')
    fl.append('[0:a]volume=0.5[mu]'); fl.append('[mu][vo]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[aout]')
    run('ffmpeg', '-y', '-i', vin, *inputs, '-filter_complex', ';'.join(fl), '-map', '0:v', '-map', '[aout]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', vout)
if __name__ == '__main__':
    if sys.argv[1] == 'plan': plan(sys.argv[2], sys.argv[3])
    else: mix(*sys.argv[2:6])
