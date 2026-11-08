"""Comic-book UI for the Reels: every slide is a comic page.
  cover : "AI Tips" sticker, the title in a big tilted panel, the hero with a starburst + the subtitle as a narrator box
  point : chapter sticker + app tag, the 2-line title as a shout banner,
          panel 1 = yellow narrator box (🎬 line) + red action bar (👉 line) + tap-path stickers + 💡/⚠️ sticky note,
          panel 2 = the hero (big emoji + name) with a speech bubble that types the prompt (or "says", or the 💡/⚠️ line)
  cta   : "النهاية" panel with the ending, the body, like/save/share stickers and the site link
Used by tools/make_reel.py (still PNGs + overflow check) and tools/reel_anim.py (animated frames).
wrap(key, k, cls, inner) adds animation timing to each piece; the default just renders it.
"""
import os
import make_reel as M

AR_DIGITS = "٠١٢٣٤٥٦٧٨٩"
def ar(n): return "".join(AR_DIGITS[int(d)] for d in str(n))
def plain(key, k, cls, inner): return f'<div class="{cls}">{inner}</div>'
def strip_mark(line):
    for e in ("🎬", "👉", "❌", "✅"):
        if line.strip().startswith(e): return line.strip()[len(e):].strip()
    return line.strip()

def font_css():
    def f(p): return M.font_b64(p)
    return ("@font-face{font-family:Comic;src:url(data:font/woff2;base64,%s) format('woff2');unicode-range:U+0600-06FF,U+0750-077F,U+FB50-FDFF,U+FE70-FEFF;}"
            "@font-face{font-family:Comic;src:url(data:font/woff2;base64,%s) format('woff2');}") % (f("lalezar-arabic-400-normal.woff2"), f("lalezar-latin-400-normal.woff2"))

# Day-rotating comic accents: (narrator box, action bar, highlight/burst)
ACCENTS = [("#FFE14D", "#FF4B4B", "#4DA3FF"), ("#C6F432", "#FF3E9A", "#2EE6D6"), ("#FFB347", "#1FB59E", "#9B7BFF"), ("#FFE14D", "#2F6BFF", "#FF7A45")]

def vars_css(seed, night):
    narr, act, hl = ACCENTS[seed % len(ACCENTS)]
    if night:   # 8 AM: night comic (dark panels, light ink lines, neon offset shadows)
        return (f"body{{--fg:#F4F1E8;--page:#0D0F1E;--paper:#1C1F35;--text:#F4F1E8;--line:#F4F1E8;--shadow:{hl};--narr:{narr};--act:{act};--hl:{hl};--dots:{hl}40}}"
                f".bubble,.chip,.cxcta{{box-shadow:0 0 26px {hl}66,10px 10px 0 {hl}!important}} .heroE{{filter:drop-shadow(0 0 30px {hl}aa)}}")
    return f"body{{--page:var(--bg);--paper:#FFFDF5;--text:#141414;--line:#141414;--shadow:#141414;--narr:{narr};--act:{act};--hl:{hl};--dots:#14141424}}"

CSS = """
body{background:radial-gradient(var(--dots) 3.2px,transparent 3.6px) 0 0/26px 26px,var(--page)!important;color:var(--text)}
.blob,.ghost,body::before,body::after{display:none!important}
.top,.top .cnt,.handle{color:var(--text)!important}
.top .site,.handle{background:var(--paper);border:4px solid var(--line);padding:4px 16px;border-radius:10px}
.main{min-height:0;justify-content:center}
.cx{display:flex;flex-direction:column;gap:30px}
.cxhead{display:flex;align-items:center;gap:18px}
.chap,.ctag,.cxkick{font-family:Comic;font-size:40px;line-height:1.3;padding:6px 26px 2px;border:5px solid var(--line);background:var(--hl);color:#141414;border-radius:12px;box-shadow:6px 6px 0 var(--shadow);transform:rotate(-3deg)}
.ctag{font-family:Mono;font-size:28px;background:var(--paper);color:var(--text);transform:rotate(2deg);direction:ltr;padding:8px 20px}
.boom{font-family:Comic;font-weight:400;font-size:104px;line-height:1.12;color:var(--text);text-shadow:5px 5px 0 var(--paper),-2px -2px 0 var(--paper)}
.boom em{font-style:normal;display:inline-block;background:var(--hl);color:#141414;border:6px solid var(--line);padding:4px 22px 0;border-radius:14px;transform:rotate(-2.5deg);box-shadow:8px 8px 0 var(--shadow);text-shadow:none}
.panel{background:var(--paper);border:7px solid var(--line);border-radius:10px;box-shadow:14px 14px 0 var(--shadow);padding:30px 32px;display:flex;flex-direction:column;gap:20px;position:relative}
.p1{transform:rotate(-.8deg)} .p2{transform:rotate(.8deg);flex-direction:row;align-items:center;gap:26px}
.narr{align-self:flex-start;background:var(--narr);color:#141414;border:5px solid var(--line);padding:10px 24px;font-size:38px;font-weight:800;line-height:1.5;margin:-58px -14px 0 0;box-shadow:6px 6px 0 var(--shadow)}
.narr small{display:block;font-family:Comic;font-size:28px;opacity:.7;line-height:1.2}
.act{background:var(--act);color:#fff;border:5px solid var(--line);border-radius:12px;padding:16px 26px;font-size:44px;font-weight:900;line-height:1.5;box-shadow:6px 6px 0 var(--shadow)}
.stickers{display:flex;flex-wrap:wrap;gap:14px;align-items:center}
.chip{direction:ltr;unicode-bidi:isolate;font-size:32px;font-weight:900;padding:6px 22px;background:#fff;color:#141414;border:4px solid var(--line);border-radius:10px;box-shadow:5px 5px 0 var(--shadow)}
.stickers .arr b{font-family:Comic;font-size:44px;color:var(--text)}
.note{background:#FFF6A8;color:#141414;border:4px dashed #141414;padding:12px 22px;font-size:36px;font-weight:800;line-height:1.5;transform:rotate(1.2deg)}
.heroW{display:flex;flex-direction:column;align-items:center;gap:6px;flex:none}
.heroE{font-size:170px;line-height:1}
.hname{font-family:Comic;font-size:34px;background:var(--line);color:var(--paper);padding:2px 18px 0;border-radius:8px}
.bubble{flex:1;background:#fff;color:#141414;border:6px solid var(--line);border-radius:44px;padding:20px 28px 24px;position:relative;box-shadow:8px 8px 0 var(--shadow)}
.bubble::after{content:"";position:absolute;left:-40px;bottom:40px;border:22px solid transparent;border-right:34px solid var(--line)}
.bubble::before{content:"";position:absolute;left:-26px;bottom:46px;border:16px solid transparent;border-right:26px solid #fff;z-index:1}
.bubble .bl{font-family:Comic;font-size:30px;opacity:.6;line-height:1.3}
.bubble .pb{font-size:40px;line-height:1.55;font-weight:800}
.cxcover{display:flex;flex-direction:column;gap:40px}
.cxkick{align-self:flex-start;font-family:Mono;font-size:32px}
.cxtitle{background:var(--paper);border:8px solid var(--line);box-shadow:16px 16px 0 var(--shadow);padding:34px 36px 26px;transform:rotate(-1.5deg)}
.cxtitle .boom{font-size:118px}
.cxrow{display:flex;align-items:center;gap:30px}
.burst{width:300px;height:300px;flex:none;display:flex;align-items:center;justify-content:center;font-size:170px;background:var(--hl);border:0;clip-path:polygon(50% 0,61% 22%,85% 10%,78% 36%,100% 45%,79% 58%,92% 84%,64% 76%,50% 100%,37% 76%,9% 86%,22% 59%,0 46%,22% 36%,14% 10%,39% 22%)}
.cxrow .narr{margin:0;font-size:44px}
.cxcta{background:var(--paper);border:8px solid var(--line);box-shadow:16px 16px 0 var(--shadow);padding:40px 40px 44px;display:flex;flex-direction:column;gap:22px;transform:rotate(-1deg)}
.theend{align-self:flex-start;font-family:Comic;font-size:40px;background:var(--narr);color:#141414;border:5px solid var(--line);padding:4px 24px 0;transform:rotate(-3deg)}
.cxcta .boom{font-size:96px}
.cxcta .cbody{font-size:42px;font-weight:800;line-height:1.6}
.cxcta .icons{display:flex;gap:16px;flex-wrap:wrap} .cxcta .icons span{font-size:32px;font-weight:900;background:#fff;color:#141414;border:4px solid var(--line);border-radius:12px;padding:8px 20px;box-shadow:5px 5px 0 var(--shadow)}
.cxcta .url{display:inline-block;font-family:Mono;direction:ltr;font-size:44px;font-weight:700;padding:10px 26px;background:var(--hl);color:#141414;border:5px solid var(--line);border-radius:12px;box-shadow:6px 6px 0 var(--shadow)}
.cxcta .site2{font-size:32px;font-weight:800;color:var(--text)!important;line-height:2}
"""

def lines_html(text, wrap, key, start=0):
    return "".join(wrap(key, start + k, "", l) for k, l in enumerate(M.esc(text).split("<br>")))

def point(slide, i, wrap=plain, hero=None):
    hero = hero or {}
    bl = M.body_lines(slide); kinds = [M.line_kind(l) for l in bl]
    head = wrap("chap", 0, "chap", f"الفصل {ar(i)}") + (wrap("tag", 0, "ctag", M.esc(slide["tag"], False)) if slide.get("tag") else "")
    h = f'<div class="cxhead">{head}</div>'
    h += '<div class="boom">' + lines_html(slide["title"], wrap, "title") + "</div>"
    p1, notes = "", []
    for k, (l, kind) in enumerate(zip(bl, kinds)):
        txt = M.esc(strip_mark(l))
        if kind == "before": p1 += wrap("line", k, "narr", f"<small>الراوي</small>{txt}")
        elif kind == "after": p1 += wrap("line", k, "act", "👉 " + txt)
        else: notes.append((k, l))
    if slide.get("path"):
        st = []
        for k, step in enumerate(slide["path"]):
            if k: st.append(wrap("arrow", k, "arr", "<b>←</b>"))
            st.append(wrap("chip", k, "chip", M.esc(step, False)))
        p1 += '<div class="stickers">' + "".join(st) + "</div>"
    say, say_key = None, "bubble"
    if slide.get("prompt"):
        words = M.esc(slide["prompt"], False).split()
        say = ('<div class="bl">✨ اكتب كده بالظبط</div><div class="pb" dir="auto">'
               + " ".join(wrap("word", k, "", w).replace("<div", "<span").replace("</div>", "</span>") for k, w in enumerate(words))
               + '<i class="caret"></i></div>')
    elif slide.get("says"): say = f'<div class="pb">{M.esc(slide["says"])}</div>'
    elif notes:
        k, l = notes.pop(0); say, say_key = f'<div class="pb">{M.esc(l)}</div>', ("noteb", k)
    for k, l in notes: p1 += wrap("line", k, "note", M.esc(l))
    h += wrap("panelA", 0, "panel p1", p1)
    if say or hero:
        heroW = f'<div class="heroE">{hero.get("emoji", "🙂")}</div>' + (f'<div class="hname">{M.esc(hero.get("name", ""), False)}</div>' if hero.get("name") else "")
        bub = wrap(say_key if isinstance(say_key, str) else "line", 0 if isinstance(say_key, str) else say_key[1], "bubble", say) if say else ""
        h += wrap("panelB", 0, "panel p2", bub + wrap("hero", 0, "heroW", heroW))
    return f'<div class="cx">{h}</div>'

def cover(slide, wrap=plain, hero=None):
    emoji = slide.get("emoji") or (hero or {}).get("emoji", "✨")
    h = wrap("kick", 0, "cxkick", M.esc(slide.get("kicker", "AI Tips"), False))
    h += wrap("ctitle", 0, "cxtitle", '<div class="boom">' + lines_html(slide["title"], wrap, "title") + "</div>")
    sub = wrap("sub", 0, "narr", M.esc(slide.get("subtitle", ""))) if slide.get("subtitle") else ""
    h += f'<div class="cxrow">{wrap("burst", 0, "burst", emoji)}{sub}</div>'
    return f'<div class="cxcover">{h}</div>'

def cta(slide, wrap=plain):
    icons = "".join(wrap("icon", k, "", x).replace("<div", "<span").replace("</div>", "</span>") for k, x in enumerate(["❤️ لايك", "🔖 احفظ", "↗️ شارك"]))
    h = wrap("end", 0, "theend", "النهاية ✨")
    h += '<div class="boom">' + lines_html(slide["title"], wrap, "title") + "</div>"
    h += wrap("cbody", 0, "cbody", M.esc(slide.get("body")))
    h += f'<div class="icons">{icons}</div>'
    h += wrap("site", 0, "site2", 'الموقع واللينك في البايو 🔗<br><span class="url">🌐 https://megoo.me</span>')
    return wrap("ctabox", 0, "cxcta", h)

def main_html(slide, i, wrap=plain, hero=None):
    t = slide.get("type", "point")
    if t == "cover": return cover(slide, wrap, hero)
    if t == "cta": return cta(slide, wrap)
    return point(slide, i, wrap, hero)

def enabled(): return os.environ.get("REEL_UI", "comic") == "comic"   # REEL_UI=classic brings back the card layout
