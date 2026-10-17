"""Synthesize the sound-design layer for the Tesla reel (no external samples)."""
import sys, numpy as np, scipy.signal as sg, scipy.io.wavfile as wf
sr = 44100; T = float(sys.argv[1]); N = int(sr * T)
rng = np.random.default_rng(15)
mix = np.zeros(N)
def put(sig, at, g=1.0):
    s = int(at * sr); e = min(N, s + len(sig))
    if s < N: mix[s:e] += sig[:e - s] * g
def env(n, a, r):
    t = np.arange(n) / sr; return np.minimum(np.clip(t / a, 0, 1), np.clip((n / sr - t) / r, 0, 1))
def whoosh(d=0.55, lo=300, hi=3000):
    n = int(d * sr); x = rng.standard_normal(n); t = np.arange(n) / sr
    fc = lo + (hi - lo) * np.sin(np.pi * t / d) ** 2
    y = np.zeros(n); b, a = sg.butter(2, [lo, hi], 'band', fs=sr); y = sg.lfilter(b, a, x)
    return y * np.sin(np.pi * t / d) ** 2 * 0.5
def boom(d=1.6, f0=55):
    n = int(d * sr); t = np.arange(n) / sr
    f = f0 * (1 + 1.5 * np.exp(-t * 18)); y = np.sin(2 * np.pi * np.cumsum(f) / sr)
    return y * np.exp(-t * 2.6) * 0.9
def tick(f=1800, d=0.06):
    n = int(d * sr); t = np.arange(n) / sr; return np.sin(2 * np.pi * f * t) * np.exp(-t * 70) * 0.35
def riser(d=1.2):
    n = int(d * sr); t = np.arange(n) / sr; x = rng.standard_normal(n)
    b, a = sg.butter(2, 2500, 'high', fs=sr); return sg.lfilter(b, a, x) * (t / d) ** 2 * 0.25
def whir(d, f=95):
    n = int(d * sr); t = np.arange(n) / sr; x = rng.standard_normal(n)
    b, a = sg.butter(2, [400, 1600], 'band', fs=sr); nz = sg.lfilter(b, a, x)
    am = 0.6 + 0.4 * np.sin(2 * np.pi * f * t)
    return nz * am * env(n, .4, .5) * 0.18
def hiss(d):
    n = int(d * sr); t = np.arange(n) / sr; x = rng.standard_normal(n)
    b, a = sg.butter(2, [900, 6000], 'band', fs=sr); y = sg.lfilter(b, a, x)
    flick = 0.75 + 0.25 * np.sin(2 * np.pi * 13 * t) * np.sin(2 * np.pi * 3.1 * t)
    return y * flick * env(n, .15, .5) * 0.22
def rumble(d):
    n = int(d * sr); t = np.arange(n) / sr; x = rng.standard_normal(n)
    b, a = sg.butter(2, 140, 'low', fs=sr); return sg.lfilter(b, a, x) * env(n, .3, .8) * 1.6
# scene starts (must match scene.html)
starts = np.cumsum([0, 3.6, 4.4, 3.4, 10.0, 4.6, 6.0, 4.8])
def blip(f=1200,d=.09):
    n=int(d*sr);t=np.arange(n)/sr;return np.sin(2*np.pi*f*t)*np.exp(-t*30)*.3
def ding():
    n=int(1.2*sr);t=np.arange(n)/sr;return (np.sin(2*np.pi*1320*t)+.5*np.sin(2*np.pi*1980*t))*np.exp(-t*4)*.3
put(boom(), 0.0, .9); put(riser(.6), .4); put(ding(), 1.0)
put(whoosh(), starts[1]-.25); put(riser(1.0), starts[1]+1.3); put(tick(2600,.12), starts[1]+2.3, 1.4); put(boom(1.2,48), starts[1]+2.3, .5)
put(tick(1500), starts[1]+2.6); put(tick(1700), starts[1]+2.9)
put(whoosh(.5,200,1500), starts[2]-.2); [put(tick(900+k*250), starts[2]+.8+k*.2) for k in range(3)]
s4=starts[3]; put(whoosh(.7,400,5000), s4-.3); put(riser(2.2), s4+.4, .8)
for k in range(8): put(blip(900+120*(k%3)), s4+3.5+k*.35, .8)
put(ding(), s4+7.4); put(tick(2200), s4+7.6)
s5=starts[4]; put(whoosh(), s5-.2)
for k in range(16): put(tick(1000+k*60,.04), s5+.3+k*.1, .7)
put(ding(), s5+1.9, .7)
s6=starts[5]; put(whoosh(), s6-.2); put(tick(1800), s6+.6)
for k in range(5): put(blip(700,.12), s6+1.4+k*.9, .6)
put(boom(1.0,70), s6+3.2, .4)
put(whoosh(.5), starts[6]-.2); put(tick(1500), starts[6]+.3); put(tick(1700), starts[6]+.55)
put(whoosh(.6,300,2500), starts[7]-.2); put(tick(2000), starts[7]+2.75)
mix /= np.abs(mix).max() + 1e-9
wf.write(sys.argv[2], sr, (mix * 0.85 * 32767).astype(np.int16))
