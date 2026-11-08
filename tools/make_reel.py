#!/usr/bin/env python3
"""megoo carousel generator — Arabic RTL, 1080x1920 PNG slides.
Usage: python3 make_carousel.py post.json OUT_DIR
Fonts: run once in the same folder:
  npm pack @fontsource-variable/cairo @fontsource/jetbrains-mono --silent
  for f in *.tgz; do tar xzf $f && mv package ${f%.tgz}; done
post.json = {"slides":[
  {"type":"cover","kicker":"...","title":"...","subtitle":"..."},
  {"type":"point","title":"...","body":"...","tag":"optional short english term"},
  {"type":"cta","title":"...","body":"..."}]}
"""
import base64, glob, html, json, os, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
HANDLE = "@_megoo.me"
SITE = "megoo.me"
LOGO = os.path.join(HERE, "logo-disabled.png")  # logo turned off; rename to logo.png to re-enable

def font_b64(pattern):
    hits = glob.glob(os.path.join(HERE, "**", pattern), recursive=True)
    if not hits:
        sys.exit(f"font not found: {pattern} (run the npm pack step)")
    return base64.b64encode(open(hits[0], "rb").read()).decode()

CSS = """
@font-face{font-family:Cairo;src:url(data:font/woff2;base64,%(ar)s) format('woff2');font-weight:200 1000;unicode-range:U+0600-06FF,U+0750-077F,U+FB50-FDFF,U+FE70-FEFF,U+200C-200E;}
@font-face{font-family:Cairo;src:url(data:font/woff2;base64,%(la)s) format('woff2');font-weight:200 1000;}
@font-face{font-family:Mono;src:url(data:font/woff2;base64,%(mono)s) format('woff2');font-weight:700;}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden}
body{font-family:Cairo,sans-serif;background:#9C8BFF;color:#15131A;direction:rtl;position:relative;overflow:hidden}
.bg{display:none}
.wrap{position:absolute;inset:0;padding:150px 90px 300px;display:flex;flex-direction:column}
.top{display:flex;justify-content:space-between;align-items:center;font-size:32px;font-weight:800;color:#15131A}
.top .site{font-family:Mono;direction:ltr;font-size:30px}
.top .cnt{color:rgba(21,19,26,.6);direction:ltr}
.main{flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:30px}
.kicker{display:inline-block;align-self:flex-start;font-size:32px;font-weight:800;color:#C8F25A;background:#15131A;padding:6px 28px;border-radius:999px;margin-bottom:44px;direction:ltr}
h1{font-size:112px;line-height:1.45;font-weight:900;letter-spacing:-.5px}
h1 em,h2 em{font-style:normal;display:inline-block;background:#C8F25A;color:#15131A;padding:0 20px;line-height:1.25;border-radius:22px;vertical-align:baseline}
.sub{font-size:42px;line-height:1.7;margin-top:40px;font-weight:700;color:rgba(21,19,26,.78)}
.num{align-self:flex-start;font-size:36px;font-weight:900;background:#FFD23F;color:#15131A;width:84px;height:84px;border-radius:24px;display:flex;align-items:center;justify-content:center;margin-bottom:34px;font-family:Mono}
h2{font-size:78px;line-height:1.5;font-weight:900;margin-bottom:36px}
.body{font-size:42px;line-height:1.75;font-weight:700;color:#15131A}
.tag{display:inline-block;align-self:flex-start;margin-top:44px;font-family:Mono;font-size:28px;color:#15131A;background:#FFB39F;padding:8px 24px;border-radius:14px;direction:ltr}
.foot{height:170px;display:flex;justify-content:space-between;align-items:center;font-size:30px}
.handle{font-family:Mono;direction:ltr;font-weight:700;display:flex;gap:16px;align-items:center;font-size:30px}
.handle s{text-decoration:none;opacity:.4}
.mark{display:flex;align-items:flex-end;gap:12px;direction:ltr}
.mark i{display:block;border-radius:10px}
.mark .a{width:44px;height:52px;background:#C8F25A}.mark .b{width:44px;height:72px;background:#FFD23F}
.mark .c{width:44px;height:52px;background:#FFB39F}.mark .d{width:40px;height:40px;border-radius:50%%;background:#FF5A36;align-self:flex-start}
.swipe{font-weight:900;font-size:30px;background:#15131A;color:#C8F25A;padding:8px 24px;border-radius:999px}
.cta-box{background:#15131A;color:#F4F1FF;border-radius:40px;padding:60px 60px}
.cta-box h2 em{color:#15131A}
.cta-box .body{color:#E4DEFF}
.icons{display:flex;gap:22px;margin-top:46px;font-size:32px;font-weight:800}
.icons span{background:rgba(255,255,255,.1);padding:14px 28px;border-radius:999px}
.site2{margin-top:44px;font-size:32px;font-weight:700;color:#E4DEFF}
.site2 b{font-family:Mono;color:#C8F25A;direction:ltr;unicode-bidi:isolate}
"""

def esc(s, allow_em=True):
    s = html.escape(s or "")
    if allow_em:  # *word* -> gradient highlight
        parts = s.split("*")
        s = "".join(f"<em>{p}</em>" if i % 2 else p for i, p in enumerate(parts))
    return s.replace("\n", "<br>")

# New layout pieces (plain string, NOT %-formatted, so "%" is safe here). Colours come from CSS variables that
# tools/reel_anim.py sets per theme: --bg (slide background), --fg (ink), --hl (highlight), --hlfg (text on highlight).
EXTRA_CSS = """
body{--bg:#9C8BFF;--fg:#15131A;--hl:#C8F25A;--hlfg:#15131A}
.main{min-height:0}  /* keep .main inside the safe area so the OVERFLOW check can see text that does not fit */
.wrap{padding:170px 130px 320px 90px}  /* right side kept clear of Instagram's like/comment/share column */
.ptop{display:flex;align-items:center;gap:22px;margin-bottom:24px}
.ptop .num{margin-bottom:0}
.ptop .tag{margin-top:0;align-self:center;font-size:30px}
h2{margin-bottom:26px}
.cards{display:flex;flex-direction:column;gap:18px}
.card{font-size:44px;line-height:1.6;font-weight:700;padding:20px 30px;border-radius:28px}
.card.before{font-size:38px;opacity:.8;background:color-mix(in srgb,var(--fg) 9%,transparent)}
.card.after{background:var(--fg);color:var(--bg);font-weight:800;box-shadow:0 18px 40px color-mix(in srgb,var(--fg) 22%,transparent)}
.card.tip,.card.warn{font-size:37px;border:4px dashed color-mix(in srgb,var(--fg) 45%,transparent)}
.card.plain{padding:0}
.path{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin-top:24px}
.path .chip{direction:ltr;unicode-bidi:isolate;font-size:32px;font-weight:800;padding:6px 24px;border-radius:999px;background:var(--bg);color:var(--fg);border:4px solid var(--fg);position:relative}
.path b{font-size:34px;opacity:.55;font-weight:900}
.prompt{margin-top:24px;border-radius:30px;background:#FFFFFFF0;color:#15131A;padding:20px 30px 24px;box-shadow:0 20px 50px #0002}
.prompt .ph{font-size:28px;font-weight:800;opacity:.55;margin-bottom:6px}
.prompt .pb{font-size:39px;line-height:1.6;font-weight:700}
.caret{display:inline-block;width:5px;height:40px;background:currentColor;vertical-align:middle;margin-inline-start:8px;animation:blink 1s steps(2) infinite}
@keyframes blink{50%{opacity:0}}
.herow{margin-inline-start:auto}
.hero{display:inline-block;font-size:32px;font-weight:800;padding:6px 22px;border-radius:999px;border:3px solid var(--fg);color:var(--fg)}
.cemoji{font-size:150px;line-height:1;margin-bottom:22px;align-self:flex-start}
"""

# story format: 🎬 = what happened to the hero (faded card), 👉 = what they did with AI (solid card).
# ❌/✅ are the old "زمان / دلوقتي" format, still rendered so older posts rebuild.
KINDS = (("🎬", "before"), ("👉", "after"), ("❌", "before"), ("✅", "after"), ("💡", "tip"), ("⚠", "warn"))
def line_kind(line):
    """🎬 / 👉 / 💡 / ⚠️ (or old ❌ / ✅) at the start of a body line picks its card style."""
    line = line.strip()
    return next((k for e, k in KINDS if line.startswith(e)), "plain")

def body_lines(slide):
    return [l for l in (slide.get("body") or "").split("\n") if l.strip()]

def hero_chip(hero):
    return f'<span class="hero">{hero.get("emoji", "")} {esc(hero.get("name", ""), False)}</span>' if hero else ""

def point_main(slide, i, wrap=lambda key, k, cls, inner: f'<div class="{cls}">{inner}</div>', hero=None):
    """Point slide: number + app tag, 2-line title, ❌/✅ (+💡/⚠️) cards, optional tap path chips and a ready-to-copy prompt.
    wrap(key, k, cls, inner) lets tools/reel_anim.py add animation timing to each piece."""
    top = wrap("num", 0, "num", str(i)) + (wrap("tag", 0, "tag", esc(slide["tag"], False)) if slide.get("tag") else "") + (wrap("hero", 0, "herow", hero_chip(hero)) if hero else "")
    h = f'<div class="ptop">{top}</div>'
    h += "<h2>" + "".join(wrap("title", k, "", l) for k, l in enumerate(esc(slide["title"]).split("<br>"))) + "</h2>"
    h += '<div class="cards">' + "".join(wrap("line", k, f"card {line_kind(l)}", esc(l)) for k, l in enumerate(body_lines(slide))) + "</div>"
    if slide.get("path"):
        chips = []
        for k, step in enumerate(slide["path"]):
            if k: chips.append(wrap("arrow", k, "arr", "<b>←</b>").replace("<div", "<span").replace("</div>", "</span>"))
            chips.append(wrap("chip", k, "chip", esc(step, False)).replace("<div", "<span").replace("</div>", "</span>"))
        h += '<div class="path">' + "".join(chips) + "</div>"
    if slide.get("prompt"):
        words = esc(slide["prompt"], False).split()
        h += wrap("prompt", 0, "prompt", '<div class="ph">✨ اكتب كده بالظبط</div><div class="pb" dir="auto">'
                  + " ".join(wrap("word", k, "", w).replace("<div", "<span").replace("</div>", "</span>") for k, w in enumerate(words))
                  + '<i class="caret"></i></div>')
    return h

def slide_html(slide, i, n, css, logo="", hero=None):
    bar = "".join(f'<i class="{"on" if k == i else ""}"></i>' for k in range(n))
    t = slide.get("type", "point")
    import comic
    if comic.enabled():
        main = comic.main_html(slide, i, hero=hero)
    elif t == "cover":
        emoji = slide.get("emoji") or (hero or {}).get("emoji")
        main = ((f'<div class="cemoji">{emoji}</div>' if emoji else "")
                + f'<div class="kicker">{esc(slide.get("kicker"), False)}</div>'
                f'<h1>{esc(slide["title"])}</h1>'
                + (f'<div class="sub">{esc(slide.get("subtitle"))}</div>' if slide.get("subtitle") else ""))
    elif t == "cta":
        main = (f'<div class="cta-box"><h2>{esc(slide["title"])}</h2>'
                f'<div class="body">{esc(slide.get("body"))}</div>'
                '<div class="icons"><span>❤️ لايك</span><span>🔖 احفظ</span><span>↗️ شارك</span></div>'
                '<div class="site2">التفاصيل كاملة على <b>megoo.me</b> · اللينك في البايو 🔗</div></div>')
    else:
        main = point_main(slide, i, hero=hero)
    mark = '<div class="mark"><i class="a"></i><i class="b"></i><i class="c"></i><i class="d"></i></div>'
    swipe = ''
    return f"""<!doctype html><html lang="ar"><head><meta charset="utf-8"><style>{css}</style></head>
<body><div class="wrap"><div class="top"><span class="site">megoo.me</span><span class="cnt">{i+1}/{n}</span></div>
<div class="main">{main}</div>
<div class="foot"><span class="handle">{SITE}<s>|</s>{HANDLE}</span>{swipe}{mark}</div></div></body></html>"""

def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    css = CSS % {"ar": font_b64("cairo-arabic-wght-normal.woff2"),
                 "la": font_b64("cairo-latin-wght-normal.woff2"),
                 "mono": font_b64("jetbrains-mono-latin-700-normal.woff2")} + EXTRA_CSS
    import comic
    if comic.enabled(): css += comic.font_css() + comic.CSS + comic.vars_css(0, False)
    slides = spec["slides"]
    logo = ""
    for ext, mime in ((".png", "image/png"), (".svg", "image/svg+xml")):
        f = os.path.splitext(LOGO)[0] + ext
        if os.path.exists(f):
            logo = f"data:{mime};base64," + base64.b64encode(open(f, "rb").read()).decode()
            break
    exe = "/opt/pw-browsers/chromium" if os.path.exists("/opt/pw-browsers/chromium") else None
    with sync_playwright() as p:
        b = p.chromium.launch(**({"executable_path": exe} if exe and os.path.isfile(exe) else {}))
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        for i, s in enumerate(slides):
            pg.set_content(slide_html(s, i, len(slides), css, logo, spec.get("hero")))
            pg.evaluate("document.fonts.ready")
            path = os.path.join(out, f"slide_{i+1:02d}.png")
            pg.screenshot(path=path)
            pg.add_style_tag(content=".body,.cards,.path,.prompt,.tag,.sub,.icons,.site2{visibility:hidden}")
            pg.screenshot(path=os.path.join(out, f"slide_{i+1:02d}a.png"))
            pg.set_content(slide_html(s, i, len(slides), css, logo, spec.get("hero")))
            pg.evaluate("document.fonts.ready")
            # overflow check
            over = pg.evaluate("(()=>{const m=document.querySelector('.main');return m.scrollHeight>m.clientHeight+2})()")
            print(path, "OVERFLOW!" if over else "ok")
        b.close()

if __name__ == "__main__":
    main()
