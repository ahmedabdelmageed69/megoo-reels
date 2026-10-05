import sys
import numpy as np, scipy.signal as sg, scipy.io.wavfile as wf
sr=44100; T=float(sys.argv[1]) if len(sys.argv)>1 else 38.5; N=int(sr*T); t=np.arange(N)/sr
rng=np.random.default_rng(7)
def midi(m): return 440*2**((m-69)/12)
def voice(f0, start, dur, amp, vowel='u'):
    n=int(dur*sr); tt=np.arange(n)/sr
    vib=1+0.006*np.sin(2*np.pi*(5+rng.random())*tt+rng.random()*6)*np.clip(tt/0.8,0,1)
    drift=1+0.002*np.sin(2*np.pi*0.3*tt+rng.random()*6)
    f=f0*vib*drift; ph=2*np.pi*np.cumsum(f)/sr
    sig=np.zeros(n)
    for k in range(1,30):
        if f0*k>7000: break
        sig+=np.sin(k*ph)/k**1.6
    # formants
    F={'u':[(300,80),(870,90),(2240,120)],'m':[(250,60),(1100,120),(2300,150)],'a':[(700,110),(1220,120),(2600,160)]}[vowel]
    out=np.zeros(n)
    for i,(fc,bw) in enumerate(F):
        b,a=sg.iirpeak(fc,fc/bw,fs=sr); out+=sg.lfilter(b,a,sig)*[1,.5,.25][i]
    out+=0.0004*rng.standard_normal(n)  # breath
    env=np.minimum(np.clip(tt/0.6,0,1),np.clip((dur-tt)/0.9,0,1))**1.5
    y=np.zeros(N); s0=int(start*sr); e=min(N,s0+n); y[s0:e]=(out*env*amp)[:e-s0]; return y
mix=np.zeros(N)
# Am F C G  (bass, mid, top)
chords=[(45,[57,60,64]),(41,[57,60,65]),(48,[55,60,64]),(43,[55,59,62])]
L=4.5
for i in range(8):
    root,ch=chords[i%4]; st=i*L-0.3 if i else 0
    mix+=voice(midi(root),st,L+0.6,0.9,'m')
    for m in ch: mix+=voice(midi(m)*(1+rng.normal(0,.002)),st,L+0.6,0.5,'u')
# hummed melody (soft)
mel=[69,71,72,71, 69,67,69,0, 67,69,72,74, 72,71,69,0]
for j,m in enumerate(mel*2):
    if m and j*2.25<T-1: mix+=voice(midi(m),j*2.25,2.4,0.45,'m')
# reverb
ir_t=np.arange(int(2.2*sr))/sr; ir=rng.standard_normal(len(ir_t))*np.exp(-ir_t*2.8); ir[0]=1
wet=sg.fftconvolve(mix,ir)[:N]; wet/=np.abs(wet).max()+1e-9; dry=mix/np.abs(mix).max()
y=0.6*dry+0.5*wet
b,a=sg.butter(2,[80,4500],btype='band',fs=sr); y=sg.lfilter(b,a,y)
fade=np.ones(N); f=int(2*sr); fade[:int(.8*sr)]=np.linspace(0,1,int(.8*sr)); fade[-f:]=np.linspace(1,0,f); y*=fade
y=y/np.abs(y).max()*0.8
wf.write(sys.argv[2] if len(sys.argv)>2 else 'hum.wav',sr,(y*32767).astype(np.int16))
