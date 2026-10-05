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
# 2) reel frames
tmp = tempfile.mkdtemp()
subprocess.run([sys.executable, f'{HERE}/reel_anim.py', f'{tmp}/frames'], env={**os.environ, 'POST': post}, check=True)
DUR = [4.2] + [5.8] * (n - 2) + [5.2]; X = 0.45
total = sum(DUR) - (n - 1) * X
subprocess.run([sys.executable, f'{HERE}/hum.py', str(total + 2), f'{tmp}/hum.wav'], check=True)
trans = ['smoothleft', 'circleopen', 'smoothleft', 'slideleft']
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
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{out}/reel.mp4', '-an', '-c:v', 'copy', f'{out}/reel_no_audio.mp4'], check=True)
shutil.rmtree(tmp)
print('built', out, f'{total:.1f}s')
