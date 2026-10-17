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
starts = np.cumsum([0, 3.6, 3.8, 4.0, 9.0, 3.4, 8.0, 4.8])
put(boom(), 0.0, 1.0); put(rumble(3.4), 0.0, 1.0); put(hiss(3.4), 0.05, 0.8)
put(whoosh(), starts[1] - 0.25)
put(riser(1.0), starts[1] + 1.2); put(tick(2600, .12), starts[1] + 2.2, 1.4)   # freeze snap
put(boom(1.2, 48), starts[1] + 2.2, .6)
put(whoosh(.5, 200, 1500), starts[2] - 0.2)
put(tick(900), starts[2] + 0.9); put(tick(1400), starts[2] + 1.6)
put(whoosh(.7, 400, 5000), starts[3] - 0.3)
put(whir(8.6), starts[3] + 0.4); put(tick(), starts[3] + 3.0); put(tick(), starts[3] + 5.8); put(tick(2200), starts[3] + 7.2, 1.2)
put(whoosh(), starts[4] - 0.2); put(boom(1.0, 70), starts[4] + 2.2, .5)
put(hiss(7.4), starts[5] + 0.5); put(tick(), starts[5] + 2.2); put(tick(), starts[5] + 4.6)
put(whoosh(.5), starts[6] - 0.2); put(tick(1500), starts[6] + .3); put(tick(1700), starts[6] + .55)
put(whoosh(.6, 300, 2500), starts[7] - 0.2); put(tick(2000), starts[7] + 2.75)
mix /= np.abs(mix).max() + 1e-9
wf.write(sys.argv[2], sr, (mix * 0.85 * 32767).astype(np.int16))
