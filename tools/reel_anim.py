import json, os, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv=[sys.argv[0]]+sys.argv[1:]
import make_reel as M
from playwright.sync_api import sync_playwright
spec=json.load(open(os.environ.get('POST','post.json'),encoding='utf-8')); slides=spec['slides']; n=len(slides)
css = M.CSS % {"ar": M.font_b64("cairo-arabic-wght-normal.woff2"),"la": M.font_b64("cairo-latin-wght-normal.woff2"),"mono": M.font_b64("jetbrains-mono-latin-700-normal.woff2")} + M.EXTRA_CSS
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
.url{display:inline-block;margin-top:22px;font-family:Mono;direction:ltr;font-size:46px;font-weight:700;padding:12px 30px;border-radius:16px;background:#C8F25A;color:#15131A;text-decoration:underline;text-underline-offset:8px}
.mark i.a{opacity:1}
h1{font-size:100px}
.wrap{z-index:1;transform-origin:50% 45%}
@keyframes kb{from{transform:scale(1)}to{transform:scale(1.035)}}
@keyframes tap{0%{box-shadow:0 0 0 0 color-mix(in srgb,var(--hl) 80%,transparent)}100%{box-shadow:0 0 0 26px transparent}}
@keyframes win{from{opacity:0}to{opacity:1}}
@keyframes punch{0%{opacity:0;transform:scale(1.5)}60%{opacity:1;transform:scale(.96)}100%{opacity:1;transform:none}}
.segs{position:absolute;top:44px;left:44px;right:44px;display:flex;gap:10px;z-index:6}
.segs i{flex:1;height:9px;border-radius:9px;background:color-mix(in srgb,var(--fg) 22%,transparent);overflow:hidden}
.segs i.done{background:var(--fg)}
.segs b{display:block;height:100%;background:var(--fg);transform-origin:right;animation:bar linear both}
.prog{display:none}
.cemoji{animation:pop .6s .05s both,bob 2.6s .8s ease-in-out infinite}
"""
def lines(s,cls,d0,step,anim=None):
    anim=anim or ENTER+' .7s'
    out=[]
    for k,l in enumerate(M.esc(s).split('<br>')):
        out.append(f'<div class="a" style="animation:{anim} {d0+k*step:.2f}s both cubic-bezier(.2,.8,.2,1)">{l}</div>')
    return ''.join(out)
PLAN=json.load(open(os.environ['VO_PLAN'])) if os.environ.get('VO_PLAN') else None
DUR=PLAN['dur'] if PLAN else [3.4]+[5.2]*(n-2)+[4.6]
def rv(i,j,default): return PLAN['reveal'][i][j] if PLAN and j<len(PLAN['reveal'][i]) else default   # when the voice reaches line j
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
    chl=t['bg'] if t['hl']==t['fg'] else t['hl']   # CTA box is filled with fg, so a fg-coloured highlight would vanish
    return f'''body{{background:{t['bg']};color:{t['fg']};--bg:{t['bg']};--fg:{t['fg']};--hl:{chl};--hlfg:{t['fg']}}}
.top,.top .cnt,.handle,.sub,.body{{color:{t['fg']}}} .top .cnt{{opacity:.6}}
.main h1 em,.main h2 em{{background:{t['hl']};color:{t['hlfg']}}}
.num{{background:{t['badge']};color:{t['badgefg']}}}
.kicker{{background:{t['fg']};color:{t['bg']}}}
.ghost{{color:{t['fg']}}} .prog{{background:{t['fg']}}}
.b1{{background:{b1}}} .b2{{background:{b2}}} .b3{{background:{b3}}}
.mark i{{box-shadow:0 0 0 3px rgba(21,19,26,.18)}}
.tag{{background:{t['fg']};color:{t['bg']}}}
.cta-box{{background:{t['fg']}}} .cta-box h2,.cta-box .body,.cta-box .site2{{color:{t['bg']}}} .cta-box h2 em{{background:{chl};color:{t['fg']}}} .site2 b{{color:{chl}}} .url{{background:{chl};color:{t['fg']}}}'''
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
    return f"""body{{--bg:#070B1A;--fg:#E8F6FF;--hl:{c};--hlfg:#070B1A}}
.card.before{{background:#FFFFFF10!important}} .card.after{{background:#0E1530!important;color:#E8F6FF!important;border:3px solid {c1};box-shadow:0 0 34px {c1}66,inset 0 0 26px {c1}22!important}}
.card.tip,.card.warn{{border-color:{c2}99!important}} .hero{{border-color:{c2}!important;color:{c2}!important;box-shadow:0 0 18px {c2}66}}
.path .chip{{background:transparent!important;color:{c}!important;border:3px solid {c};box-shadow:0 0 20px {c}77}}
.prompt{{background:#0E1530F2!important;color:#E8F6FF!important;border:2px solid {c2};box-shadow:0 0 40px {c2}55!important;font-family:Cairo}}
.segs i{{background:#E8F6FF22!important}} .segs b,.segs i.done{{background:linear-gradient(90deg,{c1},{c2})!important;box-shadow:0 0 14px {c1}}}
body{{background:radial-gradient(900px 700px at 85% 8%,{c1}33,transparent 60%),radial-gradient(900px 800px at 5% 95%,{c2}30,transparent 60%),#070B1A!important;color:#E8F6FF!important}}
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
.cta-box h2,.cta-box .body,.cta-box .site2{{color:#E8F6FF!important}} .site2 b{{color:{c1}!important}} .url{{background:{c1}!important;color:#070B1A!important;box-shadow:0 0 34px {c1}99}}
.icons span{{background:transparent!important;border:2px solid {c2};box-shadow:0 0 18px {c2}66}}
.mark i{{box-shadow:0 0 18px currentColor}} .mark .a{{background:{c1}}} .mark .b{{background:{c2}}} .mark .c{{background:#E8F6FF}} .mark .d{{background:{c1}}}
body::before{{content:"";position:absolute;left:-50%;right:-50%;bottom:0;height:62%;background:linear-gradient({c1}40 2px,transparent 2px) 0 0/90px 90px,linear-gradient(90deg,{c1}40 2px,transparent 2px) 0 0/90px 90px;transform:perspective(520px) rotateX(62deg);transform-origin:bottom;-webkit-mask-image:linear-gradient(transparent,#000);animation:gridmove 3s linear infinite}}
body::after{{content:"";position:absolute;inset:0;background:repeating-linear-gradient(transparent 0 5px,#00000026 5px 6px);pointer-events:none;z-index:5}}
@keyframes gridmove{{to{{background-position:0 90px,0 90px}}}}"""
import comic as C
COMIC_ANIM = """
@keyframes slam{0%{opacity:0;transform:scale(1.25) rotate(var(--r,0deg))}60%{opacity:1;transform:scale(.97) rotate(var(--r,0deg))}100%{opacity:1;transform:scale(1) rotate(var(--r,0deg))}}
@keyframes stamp{0%{opacity:0;transform:scale(2.2) rotate(-12deg)}70%{opacity:1;transform:scale(.92) rotate(-3deg)}100%{opacity:1;transform:rotate(-3deg)}}
@keyframes shake{0%,100%{transform:translate(0,0)}25%{transform:translate(-8px,4px)}50%{transform:translate(7px,-5px)}75%{transform:translate(-4px,-3px)}}
@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}
.p1{--r:-.8deg} .p2{--r:.8deg} .cxtitle{--r:-1.5deg} .cxcta{--r:-1deg}
.burst{animation:pop .6s .5s both,spin 18s 1.1s linear infinite!important}
"""
def comic_page(i,s):
    D=DUR[i]; t=s.get('type','point'); hero=spec.get('hero') or {}
    bl=M.body_lines(s); nb=len(bl)
    after=next((k for k,l in enumerate(bl) if M.line_kind(l)=='after'),max(nb-1,0))
    t_after=rv(i,after+1,1.0+after*1.1); t_pr=rv(i,nb+1,1.0+nb*1.1); t_end=max(t_pr+1.0,D-0.9)
    words=len((s.get('prompt') or '').split()) or 1
    t_b=(t_pr-.5) if s.get('prompt') else (t_after+.9)
    def wrap(key,k,cls,inner):
        st={'chap':'stamp .55s .1s','tag':'pop .5s .35s','title':f'punch .55s {(.05 if t=="cover" else .25)+k*.18:.2f}s',
            'line':f'up .55s {rv(i,k+1,1.0+k*1.1)-.1:.2f}s','panelA':f'slam .5s {max(.3,rv(i,1,1.0)-.35):.2f}s',
            'chip':f'stamp .45s {t_after+.5+k*.3:.2f}s','arrow':f'pop .35s {t_after+.4+k*.3:.2f}s',
            'panelB':f'slam .5s {t_b:.2f}s','hero':f'pop .6s {t_b+.15:.2f}s,shake .5s {t_b+.8:.2f}s','bubble':f'pop .5s {t_b+.3:.2f}s',
            'noteb':f'pop .5s {t_b+.3:.2f}s','word':f'win .08s {t_pr+(t_end-t_pr)*k/words:.2f}s',
            'kick':'stamp .5s .1s','ctitle':'slam .5s .02s','burst':'pop .6s .5s','sub':f'up .6s {rv(i,1,1.2):.2f}s',
            'end':'stamp .55s .1s','ctabox':'slam .55s .02s','cbody':f'up .6s {rv(i,1,1.0):.2f}s','icon':f'stamp .45s {1.3+k*.2:.2f}s','site':'up .6s 2s'}.get(key,'up .6s .3s')
        st=','.join(x.strip()+' both cubic-bezier(.2,.8,.2,1)' for x in st.split(','))   # every animation keeps its end state
        return f'<div class="a {cls}" style="animation:{st}">{inner}</div>'
    main=C.main_html(s,i,wrap,hero)
    css_c=C.font_css()+C.CSS+C.vars_css(SEED,AM)+COMIC_ANIM
    return f"""<!doctype html><html lang="ar"><head><meta charset="utf-8"><style>{css}{ANIM}{theme_css(i)}{css_c}</style></head><body>
<div class="segs">{''.join(f'<i class="done"></i>' if k<i else (f'<i><b style="animation-duration:{D}s"></b></i>' if k==i else '<i></i>') for k in range(n))}</div>
<div class="wrap" style="animation:kb {D}s linear both">
<div class="top"><span class="site">🌐 https://megoo.me</span><span class="cnt">{i+1}/{n}</span></div>
<div class="main">{main}</div>
<div class="foot"><span class="handle">https://megoo.me<s>|</s>@_megoo.me</span></div></div></body></html>"""
def page(i,s):
    if C.enabled(): return comic_page(i,s)
    t=s.get('type','point'); D=DUR[i]
    if t=='cover':
        emo=s.get('emoji') or (spec.get('hero') or {}).get('emoji')
        main=((f'<div class="cemoji">{emo}</div>' if emo else '')+
              f'<div class="kicker a" style="animation:pop .6s .1s both">{M.esc(s["kicker"],False)}</div>'
              f'<h1>{lines(s["title"],"",.05,.18,"punch .55s")}</h1>'
              f'<div class="sub a" style="animation:up .7s {rv(i,1,1.3):.2f}s both">{M.esc(s.get("subtitle",""))}</div>')
        ghost=''
    elif t=='cta':
        icons=''.join(f'<span class="a" style="animation:pop .5s {1.3+k*.18:.2f}s both,pulse 1.6s {2.2+k*.3:.2f}s ease-in-out infinite">{x}</span>' for k,x in enumerate(['❤️ لايك','🔖 احفظ','↗️ شارك']))
        main=(f'<div class="cta-box a" style="animation:up .8s .1s both"><h2>{lines(s["title"],"",.4,.2)}</h2>'
              f'<div class="body a" style="animation:up .6s {rv(i,1,1.0):.2f}s both">{M.esc(s.get("body"))}</div>'
              f'<div class="icons">{icons}</div>'
              f'<div class="site2 a" style="animation:up .6s 2s both">الموقع واللينك في البايو 🔗<div class="url">🌐 https://megoo.me</div></div></div>')
        ghost=''
    else:
        bl=M.body_lines(s); nb=len(bl)
        after=next((k for k,l in enumerate(bl) if M.line_kind(l)=='after'),nb-1)
        t_after=rv(i,after+1,1.0+after*1.1)
        t_pr=rv(i,nb+1,1.0+nb*1.1); t_end=max(t_pr+1.0,D-0.9)                 # the prompt is spoken last: type it out while it is read
        words=len((s.get('prompt') or '').split()) or 1
        def wrap(key,k,cls,inner):
            st={'num':'pop .6s .15s','tag':'pop .5s .3s','title':f'{ENTER} .7s {.35+k*.2:.2f}s',
                'line':f'{BODYIN} .7s {rv(i,k+1,1.0+k*1.1):.2f}s',
                'chip':f'pop .45s {t_after+.5+k*.3:.2f}s both,tap .9s {t_after+.75+k*.3:.2f}s','arrow':f'up .4s {t_after+.4+k*.3:.2f}s',
                'prompt':f'up .6s {t_pr-.35:.2f}s','hero':'pop .5s .45s','word':f'win .08s {t_pr+(t_end-t_pr)*k/words:.2f}s'}[key]
            return f'<div class="a {cls}" style="animation:{st} both cubic-bezier(.2,.8,.2,1)">{inner}</div>'
        main=M.point_main(s,i,wrap,spec.get('hero'))
        ghost=f'<div class="ghost">{i}</div>'
    mark='<div class="mark"><i class="a"></i><i class="b"></i><i class="c"></i><i class="d"></i></div>'
    return f"""<!doctype html><html lang="ar"><head><meta charset="utf-8"><style>{css}{ANIM}{theme_css(i)}{style_css(i)}{future_css(i) if AM else ''}</style></head><body>
<div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div>{ghost}
<div class="segs">{''.join(f'<i class="done"></i>' if k<i else (f'<i><b style="animation-duration:{D}s"></b></i>' if k==i else '<i></i>') for k in range(n))}</div>
<div class="wrap" style="animation:kb {D}s linear both"><div class="top"><span class="site">🌐 https://megoo.me</span><span class="cnt">{i+1}/{n}</span></div>
<div class="main">{main}</div>
<div class="foot"><span class="handle">https://megoo.me<s>|</s>@_megoo.me</span>{mark}</div></div></body></html>"""
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
