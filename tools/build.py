#!/usr/bin/env python3
"""Build one day's megoo post from a post.json.
Usage: python3 tools/build.py post.json OUT_DIR
Outputs in OUT_DIR: slide_XX.png (4:5 carousel), reel.mp4 (9:16 animated, vocal-only hum), reel_no_audio.mp4
Needs: python3 + numpy/scipy + playwright (chromium) + ffmpeg, and fonts (run tools/setup_fonts.sh once).
"""
import json, os, subprocess, sys, shutil, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
post, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.makedirs(out, exist_ok=True)
n = len(json.load(open(post, encoding='utf-8'))['slides'])
# 1) carousel PNGs
r = subprocess.run([sys.executable, f'{HERE}/make_carousel_brand.py', post, out], capture_output=True, text=True, check=True)
print(r.stdout.strip())
if 'OVERFLOW' in r.stdout: sys.exit('OVERFLOW: shorten the slide text and rebuild')
# 2) voice first (if GEMINI_API_KEY is set): the speech decides how long each slide lasts and when each line appears
tmp = tempfile.mkdtemp(); plan_json = None
if (os.environ.get('GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEYS')) and not os.environ.get('NO_VOICE'):
    r = subprocess.run([sys.executable, f'{HERE}/voiceover.py', 'plan', post, f'{tmp}/vo'], capture_output=True, text=True)
    print(r.stderr.strip()[-400:])
    if r.returncode == 0: plan_json = f'{tmp}/vo/plan.json'
    else: print('WARNING: VOICE-OVER FAILED, building a silent-voice reel (music only)')
else: print('WARNING: GEMINI_API_KEY not set, building without voice-over')
subprocess.run([sys.executable, f'{HERE}/reel_anim.py', f'{tmp}/frames'], env={**os.environ, 'POST': post, **({'VO_PLAN': plan_json} if plan_json else {})}, check=True)
DUR = json.load(open(plan_json))['dur'] if plan_json else [3.4] + [5.2] * (n - 2) + [4.6]; X = 0.45
total = sum(DUR) - (n - 1) * X
import datetime
d = os.path.dirname(post); am = os.path.basename(d) == 'am'   # morning Reel lives in reels/<date>/am/
if am: d = os.path.dirname(d)
try: seed = datetime.date.fromisoformat(os.path.basename(d)).toordinal() * 2 + am
except Exception: seed = datetime.date.today().toordinal() * 2
subprocess.run([sys.executable, f'{HERE}/hum.py', str(total + 2), f'{tmp}/hum.wav'], env={**os.environ, 'MUSIC_SEED': str(seed), 'MUSIC_MODE': 'am' if am else ''}, check=True)
trans = [['smoothleft', 'circleopen', 'smoothleft', 'slideleft'], ['fade', 'wipeup', 'fadeblack', 'smoothup'],
         ['slideright', 'radial', 'wipeleft', 'smoothright'], ['circleclose', 'dissolve', 'slidedown', 'zoomin']][seed % 4]
args = ['ffmpeg', '-y', '-v', 'error']
for i in range(n): args += ['-framerate', '30', '-i', f'{tmp}/frames/s{i+1:02d}/%04d.jpg']
args += ['-i', f'{tmp}/hum.wav']
fl, prev, off = [], '0:v', 0.0
for k in range(1, n):
    off += DUR[k-1] - X
    fl.append(f'[{prev}][{k}:v]xfade=transition={trans[(k-1) % 4]}:duration={X}:offset={off:.3f}[v{k}]'); prev = f'v{k}'
fl.append(f'[{prev}]format=yuv420p[vout]')
fl.append(f'[{n}:a]atrim=0:{total:.2f},afade=t=out:st={total-2:.2f}:d=2,aresample=48000[aout]')
args += ['-filter_complex', ';'.join(fl), '-map', '[vout]', '-map', '[aout]', '-c:v', 'libx264', '-profile:v', 'high',
         '-crf', '20', '-r', '30', '-c:a', 'aac', '-b:a', '128k', '-ar', '48000', '-movflags', '+faststart', '-t', f'{total:.2f}', f'{out}/reel.mp4']
subprocess.run(args, check=True)
if plan_json:
    shutil.move(f'{out}/reel.mp4', f'{tmp}/music_only.mp4')
    subprocess.run([sys.executable, f'{HERE}/voiceover.py', 'mix', post, f'{tmp}/vo', f'{tmp}/music_only.mp4', f'{out}/reel.mp4'], check=True)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{out}/reel.mp4', '-an', '-c:v', 'copy', f'{out}/reel_no_audio.mp4'], check=True)
shutil.rmtree(tmp)
print('built', out, f'{total:.1f}s')
