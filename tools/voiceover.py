#!/usr/bin/env python3
"""Add a Google Cloud TTS voice-over to a built reel: starts low and intimate (like sharing a secret), ends with high energy.
Usage: python3 tools/voiceover.py post.json reel_in.mp4 reel_out.mp4
Env: GOOGLE_TTS_API_KEY (required), TTS_VOICE (default ar-XA-Wavenet-B)
Each slide may carry "vo": the short sentence(s) to speak; otherwise the title is read.
"""
import base64, json, os, subprocess, sys, tempfile, urllib.request
post, vin, vout = sys.argv[1:4]
KEY = os.environ['GOOGLE_TTS_API_KEY']; VOICE = os.environ.get('TTS_VOICE', 'ar-XA-Wavenet-B')
slides = json.load(open(post, encoding='utf-8'))['slides']; n = len(slides)
DUR = [3.4] + [5.2] * (n - 2) + [4.6]; X = 0.45
def tts(text, rate, pitch, gain):
    cfg = {'audioEncoding': 'MP3', 'speakingRate': round(rate, 3), 'volumeGainDb': round(gain, 1)}
    if 'Wavenet' in VOICE or 'Standard' in VOICE: cfg['pitch'] = round(pitch, 1)   # Chirp3-HD has no pitch control
    body = {'input': {'text': text}, 'voice': {'languageCode': 'ar-XA', 'name': VOICE}, 'audioConfig': cfg}
    req = urllib.request.Request(f'https://texttospeech.googleapis.com/v1/text:synthesize?key={KEY}', json.dumps(body).encode(), {'Content-Type': 'application/json'})
    return base64.b64decode(json.load(urllib.request.urlopen(req, timeout=60))['audioContent'])
def run(*a): subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
tmp = tempfile.mkdtemp(); inputs, filt, starts = [], [], []; off = 0.0
for i, s in enumerate(slides):
    t = i / (n - 1)                       # 0 = intimate whisper-ish, 1 = full energy
    text = s.get('vo') or s.get('title', '').replace('\n', ' ')
    rate, pitch, gain = 0.82 + 0.34 * t ** 1.5, -4 + 7 * t, -9 + 11 * t
    raw = f'{tmp}/v{i}.mp3'; open(raw, 'wb').write(tts(text, rate, pitch, gain))
    # soft + breathy + close early on (low-passed, small room), bright + compressed + punchy at the end
    eq = ('lowpass=f=3800,highpass=f=120,aecho=0.7:0.5:35:0.25,volume=0.9' if t < 0.4 else
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
