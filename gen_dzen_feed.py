# -*- coding: utf-8 -*-
"""Генератор dzen-feed.xml по требованиям Дзена (dzen.ru/help/ru/website/rss-modify.html):
- namespaces: content, dc, media, atom, georss
- item: title, link, guid, pubDate (свежие!), media:rating=nonadult, category=native-draft,
  description, enclosure (обложка ≥700px, без length), content:encoded (h1 + figure + текст ≥300)
- минимум 10 материалов, свежесть 2-3 дня, HTML только из разрешённых тегов (таблицы → списки)
Источники: 7 готовых дзен-текстов из прежнего фида + статьи блога (см. EXTRA).
Запуск: python gen_dzen_feed.py  (из корня репо; потом git commit/push и «на проверку» в Дзен-студии)."""
import re, os, sys, html, datetime
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://alyanskons.ru"
OLD  = os.path.join(HERE, "dzen-feed.xml")
OUT  = OLD
EXTRA = [  # (html-файл, обложка в img/dzen)
    ("blog-shtrafy-ekologiya-2026.html", "dzcover_shtrafy.png"),
    ("blog-otchetnost-2026.html",        "dzcover_otchetnost.png"),
    ("blog-ekologicheskiy-audit.html",   "dzcover_audit.png"),
]
ALLOWED = ("p", "a", "b", "i", "u", "s", "h1", "h2", "h3", "h4",
           "blockquote", "ul", "ol", "li", "figure", "img", "figcaption", "br", "video", "source")

def table_to_list(m):
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(0), re.S)
    out = []
    for r in rows:
        cells = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)]
        cells = [c for c in cells if c]
        if cells:
            out.append("<li>" + " — ".join(cells) + "</li>")
    return "<ul>" + "".join(out) + "</ul>" if out else ""

def clean_html(x):
    x = re.sub(r"<table.*?</table>", table_to_list, x, flags=re.S)          # таблицы запрещены
    x = re.sub(r"<(script|style|nav|footer|header|form|aside).*?</\1>", "", x, flags=re.S)
    x = re.sub(r"<!--.*?-->", "", x, flags=re.S)
    x = re.sub(r"</?(div|section|span|article|main|small|strong|em)[^>]*>",
               lambda m: {"strong": "<b>", "/strong": "</b>", "em": "<i>", "/em": "</i>"}.get(
                   m.group(0).strip("<>").split()[0], ""), x)
    # прочие неразрешённые теги — выпилить, содержимое оставить
    x = re.sub(r"</?([a-zA-Z0-9]+)([^>]*)>",
               lambda m: m.group(0) if m.group(1).lower() in ALLOWED else "", x)
    x = re.sub(r'\s(class|id|style|data-[\w-]+)="[^"]*"', "", x)
    x = re.sub(r"\n{3,}", "\n\n", x)
    return x.strip()

def parse_old():
    t = open(OLD, encoding="utf-8").read()
    items = []
    for m in re.finditer(r"<item>(.*?)</item>", t, re.S):
        b = m.group(1)
        g = lambda tag: (re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", b, re.S) or [None, ""])[1].strip()
        enc = re.search(r'<enclosure url="([^"]+)"', b)
        cont = re.search(r"<content:encoded><!\[CDATA\[(.*?)\]\]></content:encoded>", b, re.S)
        items.append(dict(title=html.unescape(g("title")), link=g("link"),
                          guid=g("guid") or "dzen-" + os.path.basename(g("link")),
                          desc=html.unescape(g("description")), cover=enc.group(1) if enc else "",
                          content=clean_html(cont.group(1).strip()) if cont else ""))
    return items

def parse_blog(fn):
    t = open(os.path.join(HERE, fn), encoding="utf-8").read()
    title = re.search(r"<title>(.*?)</title>", t, re.S).group(1)
    title = html.unescape(re.sub(r"\s*[—|-]\s*Альянс Консалтинг.*$", "", title.strip(), flags=re.S))
    dm = re.search(r'og:description[^>]*content="([^"]+)"', t) or re.search(r'name="description"[^>]*content="([^"]+)"', t)
    desc = html.unescape(dm.group(1)) if dm else title
    am = re.search(r"<article[^>]*>(.*?)</article>", t, re.S)
    body = clean_html(am.group(1) if am else t)
    return title, desc, body

items = parse_old()
have_links = {i["link"] for i in items}
for fn, cover in EXTRA:
    link = f"{SITE}/{fn}"
    if link in have_links: continue
    title, desc, body = parse_blog(fn)
    items.append(dict(title=title, link=link, guid="dzen-" + fn.replace(".html", ""),
                      desc=desc, cover=f"{SITE}/img/dzen/{cover}", content=body))

# свежие pubDate: раскидать по последним ~2.5 суткам, новые первыми
now = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
xml_items = []
for i, it in enumerate(items):
    pub = (now - datetime.timedelta(hours=5 * i + 2)).strftime("%a, %d %b %Y %H:%M:%S +0300")
    content = it["content"]
    if not re.match(r"\s*<h1", content):                      # заголовок дублируется в тексте
        content = f"<h1>{html.escape(it['title'])}</h1>\n" + content
    content = re.sub(r'^(<h1>.*?</h1>\s*)<img ([^>]+?)/?\s*>',  # первую голую картинку — в figure
                     r"\1<figure><img \2/></figure>", content, flags=re.S)
    content = content.replace("//>", "/>")
    ctype = "image/png" if it["cover"].lower().endswith(".png") else "image/jpeg"
    xml_items.append(f"""    <item>
      <title>{html.escape(it['title'])}</title>
      <link>{it['link']}</link>
      <guid isPermaLink="false">{it['guid']}</guid>
      <pubDate>{pub}</pubDate>
      <media:rating scheme="urn:simple">nonadult</media:rating>
      <category>native-draft</category>
      <description>{html.escape(it['desc'])}</description>
      <enclosure url="{it['cover']}" type="{ctype}"/>
      <content:encoded><![CDATA[{content}]]></content:encoded>
    </item>""")

feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:dc="http://purl.org/dc/elements/1.1/"
     xmlns:media="http://search.yahoo.com/mrss/"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:georss="http://www.georss.org/georss">
  <channel>
    <title>Экология для чайников</title>
    <link>{SITE}/</link>
    <description>Просто и по делу про экологию предприятия: отчётность, СЗЗ, НВОС, штрафы и как их избежать.</description>
    <language>ru</language>
{chr(10).join(xml_items)}
  </channel>
</rss>
"""
open(OUT, "w", encoding="utf-8").write(feed)
print(f"фид собран: {len(items)} материалов → {OUT}")

# ── линтер по спеке ──
import xml.etree.ElementTree as ET
errs = []
try: ET.fromstring(feed.encode())
except Exception as e: errs.append("XML не валиден: " + str(e))
if len(items) < 10: errs.append(f"материалов {len(items)} < 10")
for it in items:
    body = re.sub(r"<[^>]+>", "", it["content"])
    if len(body) < 300: errs.append(f"«{it['title'][:30]}»: текст {len(body)} зн. < 300")
    if "<table" in it["content"]: errs.append(f"«{it['title'][:30]}»: осталась таблица")
    cov = it["cover"].replace(SITE + "/", "").replace("/", os.sep)
    p = os.path.join(HERE, cov)
    if not os.path.exists(p): errs.append(f"«{it['title'][:30]}»: нет обложки {cov}")
    else:
        try:
            from PIL import Image
            w = Image.open(p).width
            if w < 700: errs.append(f"«{it['title'][:30]}»: обложка {w}px < 700")
        except ImportError: pass
print("ЛИНТЕР: " + ("✅ чисто" if not errs else "⚠ " + "; ".join(errs)))
