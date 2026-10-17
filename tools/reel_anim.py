import json, os, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv=[sys.argv[0]]+sys.argv[1:]
import make_reel as M
from playwright.sync_api import sync_playwright
spec=json.load(open(os.environ.get('POST','post.json'),encoding='utf-8')); slides=spec['slides']; n=len(slides)
css = M.CSS % {"ar": M.font_b64("cairo-arabic-wght-normal.woff2"),"la": M.font_b64("cairo-latin-wght-normal.woff2"),"mono": M.font_b64("jetbrains-mono-latin-700-normal.woff2")}
ANIM = """
@keyframes up{from{opacity:0;transform:translateY(70px)}to{opacity:1;transform:none}}
@keyframes inR{from{opacity:0;transform:translateX(-120px)}to{opacity:1;transform:none}}
@keyframes pop{0%{opacity:0;transform:scale(.3) rotate(-12deg)}70%{opacity:1;transform:scale(1.12) rotate(4deg)}100%{opacity:1;transform:scale(1) rotate(0)}}
@keyframes wipe{from{clip-path:inset(0 0 0 100%)}to{clip-path:inset(0 0 0 0)}}
@keyframes grow{0%{transform:scaleY(0)}70%{transform:scaleY(1.2)}100%{transform:scaleY(1)}}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-14px)}}
@keyframes drift{0%{transform:translate(0,0) rotate(0)}50%{transform:translate(60px,-80px) rotate(25deg)}100%{transform:translate(0,0) rotate(0)}}
@keyframes zoom{from{opacity:0;transform:scale(1.6)}to{opacity:1;transform:none}}
@keyframes flip{from{opacity:0;transform:perspective(800px) rotateX(80deg) translateY(40px)}to{opacity:1;transform:none}}
@keyframes bar{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.08)}}
@keyframes ghost{from{opacity:0;transform:translateY(120px) rotate(-8deg)}to{opacity:.13;transform:none rotate(-8deg)}}
.a{opacity:0;animation-fill-mode:both;animation-timing-function:cubic-bezier(.2,.8,.2,1)}
.blob{position:absolute;border-radius:40px}
.b1{width:220px;height:220px;background:#C8F25A;top:330px;left:-110px;animation:drift 9s ease-in-out infinite}
.b2{width:160px;height:160px;border-radius:50%;background:#FF5A36;bottom:470px;right:-80px;animation:drift 7s ease-in-out infinite reverse}
.b3{width:120px;height:260px;background:#FFD23F;top:1250px;left:-60px;animation:drift 11s ease-in-out infinite}
.ghost{position:absolute;font-family:Mono;font-size:900px;font-weight:700;color:#15131A;left:-40px;top:420px;line-height:1;opacity:0;animation:ghost .9s .1s both cubic-bezier(.2,.8,.2,1)}
.prog{position:absolute;top:0;left:0;right:0;height:14px;background:#15131A;transform-origin:right;animation:bar linear both}
.mark i{transform-origin:bottom;animation:grow .7s both cubic-bezier(.2,.8,.2,1),bob 2.4s 1s ease-in-out infinite}
.mark .b{animation-delay:.1s,1.2s}.mark .c{animation-delay:.2s,1.4s}.mark .d{animation-delay:.3s,1.6s}
h1 em,h2 em{animation:wipe .6s both cubic-bezier(.2,.8,.2,1)}
.icons span{display:inline-block}
.cta-box{position:relative;z-index:2}
.mark i.a{opacity:1}
h1{font-size:100px}
.wrap{z-index:1}
"""
def lines(s,cls,d0,step,anim=None):
    anim=anim or ENTER+' .7s'
    out=[]
    for k,l in enumerate(M.esc(s).split('<br>')):
        out.append(f'<div class="a" style="animation:{anim} {d0+k*step:.2f}s both cubic-bezier(.2,.8,.2,1)">{l}</div>')
    return ''.join(out)
DUR=[3.4]+[5.2]*(n-2)+[4.6]
import datetime
def _day():
    # reels/<date>/reel.mp4 = evening, reels/<date>/am/reel.mp4 = morning; the two always get different looks
    try:
        d=os.path.dirname(os.environ['POST']); am=os.path.basename(d)=='am'
        if am: d=os.path.dirname(d)
        return datetime.date.fromisoformat(os.path.basename(d)).toordinal()*2+(1 if am else 0)
    except Exception: return datetime.date.today().toordinal()*2
# soft palettes, one per day (rotates), so every reel looks different
PALETTES=[
 dict(ink='#2A1A2E',bgs=['#FFC8A2','#F4A7B9','#FFD6A5','#E7A9C4','#FFB59E'],acc=['#FFF3B0','#C9F0E3','#FFFFFF']),
 dict(ink='#0B2545',bgs=['#A9D6E5','#BFE3D0','#8ECAE6','#CDE7F0','#9AD1D4'],acc=['#FFE8A3','#FFFFFF','#FFC8B8']),
 dict(ink='#1E1B3A',bgs=['#CDB4FF','#BDE0FE','#FFC8DD','#E0C3FC','#D7C8FF'],acc=['#FDFFB6','#FFFFFF','#CAFFBF']),
 dict(ink='#12372A',bgs=['#B7E4C7','#D8F3DC','#95D5B2','#CDEAC0','#A8DADC'],acc=['#FFF1A8','#FFFFFF','#FFD6C0']),
 dict(ink='#3A2318',bgs=['#F6D8AE','#F9C6A5','#FBE3C0','#F2B5A0','#EBCFA0'],acc=['#FFFFFF','#CDE8E5','#FFF3B0']),
]
SEED=_day()
PAL=PALETTES[SEED%len(PALETTES)]
AM=os.environ.get('REEL_MODE')=='am' or os.path.basename(os.path.dirname(os.environ.get('POST','')))=='am'   # 8 AM Reel = futuristic look
STYLE=SEED%4   # 0 soft, 1 round, 2 sharp, 3 outline; also picks the entry animation
ENTER=['up','zoom','flip','inR'][STYLE]
BODYIN=['inR','up','zoom','flip'][STYLE]
THEMES=[]
for k in range(7):
    bg=PAL['bgs'][k%5]; ink=PAL['ink']; acc=PAL['acc']
    THEMES.append(dict(bg=bg,fg=ink,hl=(ink if k%2 else acc[k%3]),hlfg=(bg if k%2 else ink),badge=ink,badgefg=bg,blobs=(acc[(k+1)%3],PAL['bgs'][(k+2)%5],acc[(k+2)%3])))
def theme_css(i):
    t=THEMES[i%len(THEMES)]; b1,b2,b3=t['blobs']
    return f'''body{{background:{t['bg']};color:{t['fg']}}}
.top,.top .cnt,.handle,.sub,.body{{color:{t['fg']}}} .top .cnt{{opacity:.6}}
.main h1 em,.main h2 em{{background:{t['hl']};color:{t['hlfg']}}}
.num{{background:{t['badge']};color:{t['badgefg']}}}
.kicker{{background:{t['fg']};color:{t['bg']}}}
.ghost{{color:{t['fg']}}} .prog{{background:{t['fg']}}}
.b1{{background:{b1}}} .b2{{background:{b2}}} .b3{{background:{b3}}}
.mark i{{box-shadow:0 0 0 3px rgba(21,19,26,.18)}}
.tag{{background:{t['fg']};color:{t['bg']}}}
.cta-box{{background:{t['fg']}}} .cta-box h2,.cta-box .body,.cta-box .site2{{color:{t['bg']}}} .cta-box h2 em{{background:{t['hl']};color:{t['fg']}}} .site2 b{{color:{t['hl']}}}'''
def style_css(i):
    t=THEMES[i%len(THEMES)]; hl=t['hl']; fg=t['fg']
    return [
     '',
     f""".num{{border-radius:50%}} .tag{{border-radius:999px}} .blob{{border-radius:50%}} .cta-box{{border-radius:70px}}
.main h1 em,.main h2 em{{background:linear-gradient(transparent 52%,{hl} 52%);color:{fg};border-radius:0;padding:0 8px}}
body::before{{content:"";position:absolute;inset:0;background:radial-gradient({fg}22 3px,transparent 3px) 0 0/54px 54px}}""",
     f""".num{{border-radius:6px}} .tag{{border-radius:4px}} .blob{{border-radius:8px;transform:rotate(18deg)}} .cta-box{{border-radius:14px}} .kicker{{border-radius:8px}}
.main h1 em,.main h2 em{{border-radius:6px;transform:skewX(-8deg)}} .prog{{top:auto;bottom:0}}
body::before{{content:"";position:absolute;inset:0;background:repeating-linear-gradient(135deg,{fg}12 0 3px,transparent 3px 38px)}}""",
     f""".blob{{background:transparent!important;border:26px solid {fg}33;border-radius:50%}} .ghost{{color:transparent!important;-webkit-text-stroke:5px {fg}}}
.num{{background:transparent!important;color:{fg}!important;border:5px solid {fg}}} .tag{{background:transparent!important;color:{fg}!important;border:3px solid {fg}}}
.main h1 em,.main h2 em{{border-radius:999px}}
body::before{{content:"";position:absolute;inset:0;background:linear-gradient({fg}14 2px,transparent 2px) 0 0/72px 72px,linear-gradient(90deg,{fg}14 2px,transparent 2px) 0 0/72px 72px}}""",
    ][STYLE]
NEON=[('#00F0FF','#FF2BD6'),('#7CFF6B','#00B7FF'),('#FFB000','#FF3D81')]
def future_css(i):
    c1,c2=NEON[SEED%3]; c=(c1,c2)[i%2]
    return f"""body{{background:radial-gradient(900px 700px at 85% 8%,{c1}33,transparent 60%),radial-gradient(900px 800px at 5% 95%,{c2}30,transparent 60%),#070B1A!important;color:#E8F6FF!important}}
.top,.top .cnt,.handle,.sub,.body,.main h1,.main h2{{color:#E8F6FF!important}} .top .cnt{{opacity:.7}}
.top .site,.handle,.tag,.num,.kicker{{font-family:Mono!important}}
.main h1 em,.main h2 em{{background:{c}!important;color:#070B1A!important;border-radius:10px!important;transform:none!important;box-shadow:0 0 38px {c}aa,0 0 90px {c}55}}
.main h1,.main h2{{text-shadow:0 0 26px {c1}66}}
.kicker{{background:transparent!important;color:{c1}!important;border:3px solid {c1};border-radius:6px!important;box-shadow:0 0 24px {c1}88}}
.num{{background:transparent!important;color:{c1}!important;border:3px solid {c1}!important;border-radius:6px!important;box-shadow:0 0 24px {c1}88,inset 0 0 18px {c1}44}}
.tag{{background:transparent!important;color:{c2}!important;border:3px solid {c2}!important;border-radius:6px!important;box-shadow:0 0 22px {c2}88}}
.ghost{{color:transparent!important;-webkit-text-stroke:4px {c1}55;filter:drop-shadow(0 0 22px {c1}66)}}
.blob{{background:radial-gradient(circle,{c1}88,transparent 70%)!important;border:0!important;border-radius:50%!important;filter:blur(18px)}} .b2{{background:radial-gradient(circle,{c2}88,transparent 70%)!important}}
.prog{{background:linear-gradient(90deg,{c1},{c2})!important;height:10px;box-shadow:0 0 22px {c1}}}
.cta-box{{background:#0E1530!important;border:3px solid {c1};box-shadow:0 0 50px {c1}66,inset 0 0 40px {c1}22;border-radius:18px!important}}
.cta-box h2,.cta-box .body,.cta-box .site2{{color:#E8F6FF!important}} .site2 b{{color:{c1}!important}}
.icons span{{background:transparent!important;border:2px solid {c2};box-shadow:0 0 18px {c2}66}}
.mark i{{box-shadow:0 0 18px currentColor}} .mark .a{{background:{c1}}} .mark .b{{background:{c2}}} .mark .c{{background:#E8F6FF}} .mark .d{{background:{c1}}}
body::before{{content:"";position:absolute;left:-50%;right:-50%;bottom:0;height:62%;background:linear-gradient({c1}40 2px,transparent 2px) 0 0/90px 90px,linear-gradient(90deg,{c1}40 2px,transparent 2px) 0 0/90px 90px;transform:perspective(520px) rotateX(62deg);transform-origin:bottom;-webkit-mask-image:linear-gradient(transparent,#000);animation:gridmove 3s linear infinite}}
body::after{{content:"";position:absolute;inset:0;background:repeating-linear-gradient(transparent 0 5px,#00000026 5px 6px);pointer-events:none;z-index:5}}
@keyframes gridmove{{to{{background-position:0 90px,0 90px}}}}"""
def page(i,s):
    t=s.get('type','point'); D=DUR[i]
    if t=='cover':
        main=(f'<div class="kicker a" style="animation:pop .6s .1s both">{M.esc(s["kicker"],False)}</div>'
              f'<h1>{lines(s["title"],"",.35,.22)}</h1>'
              f'<div class="sub a" style="animation:up .7s 1.3s both">{M.esc(s.get("subtitle",""))}</div>')
        ghost=''
    elif t=='cta':
        icons=''.join(f'<span class="a" style="animation:pop .5s {1.3+k*.18:.2f}s both,pulse 1.6s {2.2+k*.3:.2f}s ease-in-out infinite">{x}</span>' for k,x in enumerate(['❤️ لايك','🔖 احفظ','↗️ شارك']))
        main=(f'<div class="cta-box a" style="animation:up .8s .1s both"><h2>{lines(s["title"],"",.4,.2)}</h2>'
              f'<div class="body a" style="animation:up .6s 1s both">{M.esc(s.get("body"))}</div>'
              f'<div class="icons">{icons}</div>'
              f'<div class="site2 a" style="animation:up .6s 2s both">التفاصيل كاملة على <b>megoo.me</b> · اللينك في البايو 🔗</div></div>')
        ghost=''
    else:
        bl=M.esc(s.get('body','')).split('<br>')
        body=''.join(f'<div class="a" style="animation:{BODYIN} .7s {1.0+k*1.1:.2f}s both cubic-bezier(.2,.8,.2,1)">{l}</div>' for k,l in enumerate(bl))
        main=(f'<div class="num a" style="animation:pop .6s .15s both">{i}</div>'
              f'<h2>{lines(s["title"],"",.35,.2)}</h2><div class="body">{body}</div>'
              + (f'<div class="tag a" style="animation:pop .5s {1.1+len(bl)*1.1:.2f}s both">{M.esc(s["tag"],False)}</div>' if s.get('tag') else ''))
        ghost=f'<div class="ghost">{i}</div>'
    mark='<div class="mark"><i class="a"></i><i class="b"></i><i class="c"></i><i class="d"></i></div>'
    return f"""<!doctype html><html lang="ar"><head><meta charset="utf-8"><style>{css}{ANIM}{theme_css(i)}{style_css(i)}{future_css(i) if AM else ''}</style></head><body>
<div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div>{ghost}
<div class="prog" style="animation-duration:{D}s"></div>
<div class="wrap"><div class="top"><span class="site">megoo.me</span><span class="cnt">{i+1}/{n}</span></div>
<div class="main">{main}</div>
<div class="foot"><span class="handle">megoo.me<s>|</s>@_megoo.me</span>{mark}</div></div></body></html>"""
out=sys.argv[1] if len(sys.argv)>1 else 'anim'; os.makedirs(out,exist_ok=True)
only=[int(x) for x in sys.argv[2:]] or range(n)
FPS=30
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium') if os.path.isfile('/opt/pw-browsers/chromium') else p.chromium.launch()
    pg=b.new_page(viewport={'width':1080,'height':1920})
    for i in only:
        pg.set_content(page(i,slides[i])); pg.evaluate("document.fonts.ready")
        d=f'{out}/s{i+1:02d}'; os.makedirs(d,exist_ok=True)
        for f in range(int(DUR[i]*FPS)):
            pg.evaluate(f"document.getAnimations().forEach(a=>{{a.pause();a.currentTime={f*1000/FPS}}})")
            pg.screenshot(path=f'{d}/{f:04d}.jpg',type='jpeg',quality=93)
        print('slide',i+1,'done',flush=True)
    b.close()
