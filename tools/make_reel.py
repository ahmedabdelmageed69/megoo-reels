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

def slide_html(slide, i, n, css, logo=""):
    bar = "".join(f'<i class="{"on" if k == i else ""}"></i>' for k in range(n))
    t = slide.get("type", "point")
    if t == "cover":
        main = (f'<div class="kicker">{esc(slide.get("kicker"), False)}</div>'
                f'<h1>{esc(slide["title"])}</h1>'
                + (f'<div class="sub">{esc(slide.get("subtitle"))}</div>' if slide.get("subtitle") else ""))
    elif t == "cta":
        main = (f'<div class="cta-box"><h2>{esc(slide["title"])}</h2>'
                f'<div class="body">{esc(slide.get("body"))}</div>'
                '<div class="icons"><span>❤️ لايك</span><span>🔖 احفظ</span><span>↗️ شارك</span></div>'
                '<div class="site2">التفاصيل كاملة على <b>megoo.me</b> · اللينك في البايو 🔗</div></div>')
    else:
        main = (f'<div class="num">{i}</div><h2>{esc(slide["title"])}</h2>'
                f'<div class="body">{esc(slide.get("body"))}</div>'
                + (f'<div class="tag">{esc(slide["tag"], False)}</div>' if slide.get("tag") else ""))
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
                 "mono": font_b64("jetbrains-mono-latin-700-normal.woff2")}
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
            pg.set_content(slide_html(s, i, len(slides), css, logo))
            pg.evaluate("document.fonts.ready")
            path = os.path.join(out, f"slide_{i+1:02d}.png")
            pg.screenshot(path=path)
            pg.add_style_tag(content=".body,.tag,.sub,.icons,.site2{visibility:hidden}")
            pg.screenshot(path=os.path.join(out, f"slide_{i+1:02d}a.png"))
            pg.set_content(slide_html(s, i, len(slides), css, logo))
            pg.evaluate("document.fonts.ready")
            # overflow check
            over = pg.evaluate("(()=>{const m=document.querySelector('.main');return m.scrollHeight>m.clientHeight+2})()")
            print(path, "OVERFLOW!" if over else "ok")
        b.close()

if __name__ == "__main__":
    main()
