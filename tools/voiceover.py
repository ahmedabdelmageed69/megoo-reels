#!/usr/bin/env python3
"""Add a Google Cloud TTS voice-over to a built reel: starts low and intimate (like sharing a secret), ends with high energy.
Usage: python3 tools/voiceover.py post.json reel_in.mp4 reel_out.mp4
Env: GEMINI_API_KEY (Gemini TTS: Egyptian accent + spoken style direction; voice via GEMINI_VOICE, default Puck, model via GEMINI_TTS_MODEL)
     or GOOGLE_TTS_API_KEY (Cloud TTS fallback; TTS_VOICE, default ar-XA-Wavenet-B)
Each slide may carry "vo": the short sentence(s) to speak; otherwise the title is read.
"""
import base64, json, os, subprocess, sys, tempfile, time, urllib.request
post, vin, vout = sys.argv[1:4]
GEM = os.environ.get('GEMINI_API_KEY'); KEY = os.environ.get('GOOGLE_TTS_API_KEY'); VOICE = os.environ.get('TTS_VOICE', 'ar-XA-Wavenet-B')
slides = json.load(open(post, encoding='utf-8'))['slides']; n = len(slides)
DUR = [3.4] + [5.2] * (n - 2) + [4.6]; X = 0.45
STYLES = [  # delivery direction, from a hushed secret to full energy
    'in a very low, quiet, secretive voice, almost whispering a secret to a close friend, slow and intimate',
    'in a soft, low, confiding voice, warm and unhurried',
    'in a calm, friendly, natural voice, getting a little brighter',
    'in a clear, upbeat voice with growing energy',
    'in an energetic, enthusiastic voice, faster and brighter',
    'in a high-energy, excited, punchy voice',
    'in a loud, joyful, high-energy voice, bursting with excitement, upbeat finish']
def gemini(text, t):
    style = STYLES[min(int(t * len(STYLES) + 1e-6), len(STYLES) - 1)]
    body = {'contents': [{'parts': [{'text': f'Speak in a natural Egyptian Arabic accent, {style}: {text}'}]}],
            'generationConfig': {'responseModalities': ['AUDIO'], 'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': os.environ.get('GEMINI_VOICE', 'Puck')}}}}}
    model = os.environ.get('GEMINI_TTS_MODEL', 'gemini-3.8-flash-tts')
    req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent', json.dumps(body).encode(),
                                 {'Content-Type': 'application/json', 'x-goog-api-key': GEM})
    for attempt in range(6):
        try:
            d = base64.b64decode(json.load(urllib.request.urlopen(req, timeout=90))['candidates'][0]['content']['parts'][0]['inlineData']['data'])
            return d if d[:4] == b'RIFF' else b'RIFF' + d    # API returns a WAV already
        except Exception as e:
            if attempt == 5: raise
            time.sleep(25 if '429' in str(e) else 3)   # free tier is rate limited per minute
def tts(text, rate, pitch, gain):
    cfg = {'audioEncoding': 'MP3', 'speakingRate': round(rate, 3), 'volumeGainDb': round(gain, 1)}
    if 'Wavenet' in VOICE or 'Standard' in VOICE: cfg['pitch'] = round(pitch, 1)   # Chirp3-HD has no pitch control
    body = {'input': {'text': text}, 'voice': {'languageCode': 'ar-XA', 'name': VOICE}, 'audioConfig': cfg}
    req = urllib.request.Request(f'https://texttospeech.googleapis.com/v1/text:synthesize?key={KEY}', json.dumps(body).encode(), {'Content-Type': 'application/json'})
    return base64.b64decode(json.load(urllib.request.urlopen(req, timeout=60))['audioContent'])
def run(*a): subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def one_take(texts):
    """One Gemini call for the whole script (same voice end to end), then cut it at the n-1 longest pauses."""
    arc = ('Narrate this as ONE continuous take by the same single speaker, in a natural Egyptian Arabic accent. Start very low, quiet and secretive, like whispering a secret to a close friend; '
           'gradually warm up and speed up; finish with loud, joyful, high energy. Pause clearly (about a second) between the lines. Lines:\n')
    body = {'contents': [{'parts': [{'text': arc + '\n'.join(f'{k+1}) {t}' for k, t in enumerate(texts))}]}],
            'generationConfig': {'responseModalities': ['AUDIO'], 'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': os.environ.get('GEMINI_VOICE', 'Puck')}}}}}
    model = os.environ.get('GEMINI_TTS_MODEL', 'gemini-3.8-flash-tts')
    req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent', json.dumps(body).encode(),
                                 {'Content-Type': 'application/json', 'x-goog-api-key': GEM})
    for attempt in range(6):
        try:
            d = base64.b64decode(json.load(urllib.request.urlopen(req, timeout=180))['candidates'][0]['content']['parts'][0]['inlineData']['data']); break
        except Exception as e:
            if attempt == 5: raise
            time.sleep(25 if '429' in str(e) else 3)
    full = f'{tmp}/full.wav'; open(full, 'wb').write(d if d[:4] == b'RIFF' else b'RIFF' + d)
    log = subprocess.run(['ffmpeg', '-i', full, '-af', 'silencedetect=n=-38dB:d=0.35', '-f', 'null', '-'], capture_output=True, text=True).stderr
    import re
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]; en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
    total = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', full]))
    gaps = [(e - a, (a + e) / 2) for a, e in zip(st, en) if 0.3 < (a + e) / 2 < total - 0.3]
    cuts = sorted(m for _, m in sorted(gaps, reverse=True)[:len(texts) - 1])
    if len(cuts) != len(texts) - 1: sys.exit(f'could not split the take into {len(texts)} lines (found {len(cuts)} pauses)')
    bounds = [0.0] + cuts + [total]; parts = []
    for k in range(len(texts)):
        o = f'{tmp}/seg{k}.wav'; run('ffmpeg', '-y', '-i', full, '-ss', f'{bounds[k]:.3f}', '-to', f'{bounds[k+1]:.3f}', '-ar', '48000', '-ac', '2', o); parts.append(o)
    return parts
tmp = tempfile.mkdtemp(); inputs, filt, starts = [], [], []; off = 0.0
takes = one_take([s.get('vo') or s.get('title', '').replace('\n', ' ') for s in slides]) if GEM else None
for i, s in enumerate(slides):
    t = i / (n - 1)                       # 0 = intimate whisper-ish, 1 = full energy
    text = s.get('vo') or s.get('title', '').replace('\n', ' ')
    rate, pitch, gain = 0.82 + 0.34 * t ** 1.5, -4 + 7 * t, -9 + 11 * t
    raw = takes[i] if GEM else f'{tmp}/v{i}.mp3'
    if not GEM: open(raw, 'wb').write(tts(text, rate, pitch, gain))
    # soft + breathy + close early on (low-passed, small room), bright + compressed + punchy at the end
    eq = 'highpass=f=80,volume=1.0' if GEM else ('lowpass=f=3800,highpass=f=120,aecho=0.7:0.5:35:0.25,volume=0.9' if t < 0.4 else
          'highpass=f=100,equalizer=f=3500:t=q:w=1:g=3,acompressor=threshold=-18dB:ratio=3,volume=1.15' if t > 0.7 else 'highpass=f=100')
    out = f'{tmp}/p{i}.wav'; run('ffmpeg', '-y', '-i', raw, '-af', eq, '-ar', '48000', '-ac', '2', out)
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out]))
    room = DUR[i] - X - 0.5
    if dur > room:                         # never let a line spill into the next slide
        sp = f'{tmp}/s{i}.wav'; run('ffmpeg', '-y', '-i', out, '-af', f'atempo={min(dur / room, 1.6):.3f}', sp); out = sp
    inputs += ['-i', out]; starts.append(int((off + 0.5) * 1000)); off += DUR[i] - X
fl = [f'[{k+1}:a]adelay={ms}|{ms}[d{k}]' for k, ms in enumerate(starts)]
vm = ''.join(f'[d{k}]' for k in range(n))
fl.append(f'{vm}amix=inputs={n}:normalize=0[vo]')
fl.append('[0:a]volume=0.55[mu]')                      # music sits under the voice
fl.append('[mu][vo]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[aout]')
run('ffmpeg', '-y', '-i', vin, *inputs, '-filter_complex', ';'.join(fl), '-map', '0:v', '-map', '[aout]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', vout)
print('voice-over added ->', vout)
