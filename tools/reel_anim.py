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
def lines(s,cls,d0,step,anim='up .7s'):
    out=[]
    for k,l in enumerate(M.esc(s).split('<br>')):
        out.append(f'<div class="a" style="animation:{anim} {d0+k*step:.2f}s both cubic-bezier(.2,.8,.2,1)">{l}</div>')
    return ''.join(out)
DUR=[4.2]+[5.8]*(n-2)+[5.2]
import datetime
def _day():
    try: return datetime.date.fromisoformat(os.path.basename(os.path.dirname(os.environ['POST']))).toordinal()
    except Exception: return datetime.date.today().toordinal()
# soft palettes, one per day (rotates), so every reel looks different
PALETTES=[
 dict(ink='#2A1A2E',bgs=['#FFC8A2','#F4A7B9','#FFD6A5','#E7A9C4','#FFB59E'],acc=['#FFF3B0','#C9F0E3','#FFFFFF']),
 dict(ink='#0B2545',bgs=['#A9D6E5','#BFE3D0','#8ECAE6','#CDE7F0','#9AD1D4'],acc=['#FFE8A3','#FFFFFF','#FFC8B8']),
 dict(ink='#1E1B3A',bgs=['#CDB4FF','#BDE0FE','#FFC8DD','#E0C3FC','#D7C8FF'],acc=['#FDFFB6','#FFFFFF','#CAFFBF']),
 dict(ink='#12372A',bgs=['#B7E4C7','#D8F3DC','#95D5B2','#CDEAC0','#A8DADC'],acc=['#FFF1A8','#FFFFFF','#FFD6C0']),
 dict(ink='#3A2318',bgs=['#F6D8AE','#F9C6A5','#FBE3C0','#F2B5A0','#EBCFA0'],acc=['#FFFFFF','#CDE8E5','#FFF3B0']),
]
PAL=PALETTES[_day()%len(PALETTES)]
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
        body=''.join(f'<div class="a" style="animation:inR .7s {1.0+k*1.1:.2f}s both cubic-bezier(.2,.8,.2,1)">{l}</div>' for k,l in enumerate(bl))
        main=(f'<div class="num a" style="animation:pop .6s .15s both">{i}</div>'
              f'<h2>{lines(s["title"],"",.35,.2)}</h2><div class="body">{body}</div>'
              + (f'<div class="tag a" style="animation:pop .5s {1.1+len(bl)*1.1:.2f}s both">{M.esc(s["tag"],False)}</div>' if s.get('tag') else ''))
        ghost=f'<div class="ghost">{i}</div>'
    mark='<div class="mark"><i class="a"></i><i class="b"></i><i class="c"></i><i class="d"></i></div>'
    return f"""<!doctype html><html lang="ar"><head><meta charset="utf-8"><style>{css}{ANIM}{theme_css(i)}</style></head><body>
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
