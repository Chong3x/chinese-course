"""生成课程网站（GitHub Pages，docs/）：首页 → HSK 1–6 等级页 → 课文页 → 课后练习"""
import os, re, shutil, sys, json, html
sys.path.insert(0, os.path.dirname(__file__))
from content import LESSONS
from content_l1 import L1
from i18n import SITE as TX, LANGS, TITLES, TOPICS
from site_map import LEVELS, lesson_nav

OUT, PRACTICE, PDFS = sys.argv[1], sys.argv[2], sys.argv[3]
ALL = {L['id']: L for L in [L1] + LESSONS}
PDF_NAMES = {"L1": "第01课_介绍我的国家.pdf", "L2": "第02课_我怎么去学校.pdf", "L3": "第03课_我的爱好.pdf",
             "L4": "第04课_我的好朋友.pdf", "L5": "第05课_在饭馆.pdf"}

OFFICIAL = {}
for line in open('/home/claude/hsk30repo/corpus/syllabus2025/syllabus2025_words.tsv', encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    if len(p) > 1 and p[0] != 'word': OFFICIAL.setdefault(p[0], p[1])
def coverage(lv):
    return len({w for lid in lv['lessons'] for w, *_ in ALL[lid]['words'] if OFFICIAL.get(w) == str(lv['n'])})

def e(s): return html.escape(str(s), quote=True)
def tx(key, tag='span', cls='', **v):
    zh = TX[key]['zh']
    for k, val in v.items(): zh = zh.replace('{' + k + '}', str(val))
    dv = f" data-v='{e(json.dumps(v, ensure_ascii=False))}'" if v else ''
    c = f' class="{cls}"' if cls else ''
    return f'<{tag}{c} data-i="{key}"{dv}>{e(zh)}</{tag}>'

CSS = open(os.path.join(os.path.dirname(__file__), 'site.css'), encoding='utf-8').read()
JS = open(os.path.join(os.path.dirname(__file__), 'site.js'), encoding='utf-8').read()
SPK = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#14304A" stroke-width="2" aria-hidden="true"><path d="M11 5 6 9H2v6h4l5 4V5z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M19 5a10 10 0 0 1 0 14"/></svg>'

def page(title, depth, body, active='', lesson_json=''):
    up = '../' * depth
    langs = ''.join(f'<option value="{k}">{n}</option>' for k, n in LANGS)
    data_lesson = f" data-lesson='{e(lesson_json)}'" if lesson_json else ''
    ic = lambda d: f'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">{d}</svg>'
    def bn(key, href, icon, extra=''):
        on = ' class="on"' if active == key else ''
        return f'<a href="{href}"{on}{extra}>{icon}{tx(key)}</a>'
    bnav = ('<nav class="bnav" aria-label="Menu">'
            + bn('navHome', f'{up}index.html', ic('<path d="M3 11 12 4l9 7v9H3z"/>'))
            + bn('navLevels', f'{up}index.html#levels', ic('<path d="M4 20V10M10 20V6M16 20v-8M22 20H2"/>'))
            + bn('navPractice', f'{up}index.html#levels', ic('<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/>'), ' id="bnav-practice"')
            + bn('navMock', f'{up}hsk2/index.html#mock', ic('<path d="M4 4h16v16H4z"/><path d="M8 9h8M8 13h8M8 17h5"/>'))
            + '</nav>')
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&family=ZCOOL+KuaiLe&display=swap">
<link rel="stylesheet" href="{up}assets/style.css"></head>
<body data-root="{up}"{data_lesson}>
<header class="topbar"><div class="wrap"><a class="brand" href="{up}index.html">轻松学中文</a>
<nav class="topnav" aria-label="Main"><a href="{up}index.html#levels" data-i="navLevels">HSK 等级</a><a href="{up}hsk2/index.html#mock" data-i="navMock">模拟考</a><a href="{up}index.html#more" data-i="navMore">更多资料</a>
<label class="langbox"><span class="lbl" data-i="langLabel">界面语言</span><select class="lang" onchange="setLang(this.value)" aria-label="Language">{langs}</select></label></nav></div></header>
{body}
<footer><div class="wrap">{tx('foot1','p')}{tx('foot2','p')}</div></footer>
{bnav}
<script src="{up}assets/site.js"></script></body></html>"""

def nwrender(s, words):
    def rep(m):
        w = m.group(1)
        py = words.get(w, {'得': 'de', '着': 'zhe', '过': 'guo'}.get(w, ''))
        return f'<span class="nw">{e(w)}<span class="p">{e(py)}</span></span>'
    out, pos = [], 0
    for m in re.finditer(r'\{([^}]+)\}', s):
        out.append(e(s[pos:m.start()])); out.append(rep(m)); pos = m.end()
    out.append(e(s[pos:]))
    return ''.join(out)
def plain(s): return s.replace('{', '').replace('}', '')

def home():
    cards = ''
    for lv in LEVELS:
        n_open = len(lv['lessons']); cov = coverage(lv); pct = round(cov / lv['new'] * 100)
        status = (f'<p class="st-open">{tx("openN", n=n_open)} · {tx("coverN", a=cov, b=lv["new"])}</p>' if n_open
                  else f'<p class="st-soon">{tx("soon")}</p>')
        cards += f"""<a class="lvcard" href="{lv['id']}/index.html"><div class="top"><span class="badge" style="background:{lv['color']}">HSK {lv['n']}</span>{tx('stage_' + lv['stage'], cls='small')}</div>
<p style="margin:0;font-weight:700">{tx('lv_' + lv['id'])}</p>
<div class="nums"><div><b>{lv['new']}</b> {tx('newWordsLbl', cls='small')}</div>{tx('totalN', cls='small', n=lv['total'])}</div>
<p class="small" style="margin:0">{tx('examLabel')}{tx('exam_' + lv['exam'])}</p>
<div class="bar"><i style="width:{pct}%;background:{lv['color']}"></i></div>{status}</a>"""
    sizes = ' '.join(f'data-{lid.lower()}="{len(L["words"])}"' for lid, L in ALL.items())
    res = [("https://hskstory.com/", "r1"), ("https://hskstory.com/guides/hsk-30-syllabus", "r2"),
           ("https://hskstory.com/guides/hsk-3-syllabus", "r3"), ("https://www.chinesetest.cn", "r4")]
    resh = ''.join(f'<a href="{u}" target="_blank" rel="noopener"><b>{tx(k + "t")} ↗</b>{tx(k + "d", cls="d")}</a>' for u, k in res)
    body = f"""<section class="hero"><div class="wrap">
<div class="l">{tx('heroKicker','p','kicker')}<h1>{tx('heroTitle')}</h1>{tx('heroP2','p','d')}
<div class="acts"><a class="btn b-gold" href="#levels" data-i="chooseLevel">选择我的等级 →</a><a class="btn b-ink2" href="start/index.html" data-i="placementBtn">不知道自己几级？先上水平测试课</a></div></div>
<div class="cont" id="cont" {sizes}>{tx('continue','p','k')}
<div data-c="on" style="display:none;flex-direction:column;gap:10px">
<span class="badge" style="background:#17698F;align-self:flex-start" data-c="tag"></span><p class="t" data-c="title"></p>
<div><div class="row">{tx('wMast')}<b data-c="m" style="color:#14304A"></b></div><div class="bar" style="margin-top:6px"><i data-c="fill" style="width:0;background:#17698F"></i></div></div>
<div class="row" style="justify-content:flex-start;gap:16px"><span>🔥 <b data-c="days"></b></span><span>⭐ <b data-c="stars"></b></span></div>
<a class="btn b-ink" data-c="go" href="#" data-i="continueBtn">继续今天的练习 →</a></div>
<div data-c="off" style="display:flex;flex-direction:column;gap:12px">{tx('notStarted','p')}<a class="btn b-ink" href="#levels" data-i="chooseLevel">选择我的等级 →</a></div>
</div></div></section>
<main class="wrap">
<section class="block" id="levels">{tx('levelsTitle','h2','sec')}{tx('levelsLead','p','lead')}<div class="lvgrid">{cards}</div></section>
<div class="split"><div class="place">{tx('placeKicker','p','k')}<h3>介绍我的国家</h3><div class="sub-tr" data-tr="title_L1" style="color:#14304A;margin:0"></div>{tx('placeP','p')}
<a class="btn b-ink" style="align-self:flex-start" href="start/index.html" data-i="placeBtn">开始水平测试课 →</a></div>
<div class="how">{tx('howTitle','p','small')}<ol><li>{tx('how1')}</li><li>{tx('how2')}</li><li>{tx('how3')}</li><li>{tx('how4')}</li></ol></div></div>
<section class="block" id="more">{tx('moreTitle','h2','sec')}{tx('moreLead','p','lead')}<div class="res">{resh}</div></section>
</main>"""
    return page('轻松学中文 · 新版 HSK 1–6 课程', 0, body, 'navHome')

def level_page(lv):
    rows = ''
    for k, lid in enumerate(lv['lessons'], 1):
        L = ALL[lid]
        rows += f"""<div class="lrow"><div class="no">{k:02d}</div><div class="tt"><p class="n">{e(L['title'])}</p><div class="sub-tr" data-tr="title_{lid}" style="color:var(--soft);margin:0;font-size:14px"></div>
<p class="small"><span data-i="topic_{lid}">{e(L['topic'])}</span> · {tx('nWords', n=len(L['words']))}</p></div>
<span class="chip" data-prog="{lid}" data-n="{len(L['words'])}">{e(TX['stTodo']['zh'])}</span>
<div class="acts"><a class="btn b-blue" href="{k:02d}.html" data-i="btnText">📖 学课文</a><a class="btn b-gold" href="{k:02d}-practice.html" data-i="btnPractice">🎯 练习</a></div></div>"""
    n_open = len(lv['lessons'])
    if lv['id'] == 'hsk2':
        L1x = ALL['L1']
        rows = f"""<div class="lrow" style="background:#FDF1D2"><div class="no" style="background:#F2C14E;color:#14304A">00</div><div class="tt">{tx('placeKicker','p','small')}<p class="n">{e(L1x['title'])}</p><div class="sub-tr" data-tr="title_L1" style="color:var(--soft);margin:0;font-size:14px"></div>
<p class="small"><span data-i="topic_L1">{e(L1x['topic'])}</span> · {tx('nWords', n=len(L1x['words']))}</p></div>
<span class="chip" data-prog="L1" data-n="{len(L1x['words'])}">{e(TX['stTodo']['zh'])}</span>
<div class="acts"><a class="btn b-blue" href="../start/index.html" data-i="btnText">📖 学课文</a><a class="btn b-gold" href="../start/practice.html" data-i="btnPractice">🎯 练习</a></div></div>""" + rows
    if n_open:
        for k in range(n_open + 1, n_open + 3):
            rows += f'<div class="lrow soon"><div class="no">{k:02d}</div><div class="tt">{tx("soon","p","n")}</div><span class="chip soon" data-i="soon">即将推出</span></div>'
    else:
        rows = f'<div class="empty">{tx("noLessons","p")}</div>'
    cov = coverage(lv); ids = ','.join(lv['lessons'])
    nwords = sum(len(ALL[l]['words']) for l in lv['lessons']); nwrite = sum(len(ALL[l]['write']) for l in lv['lessons'])
    side = ''
    if n_open:
        topics = ''.join(f'<span data-i="topic_{l}">{e(ALL[l]["topic"])}</span>' for l in lv['lessons'])
        side += f"""<div class="box">{tx('myProg','p','k')}
<div><div data-sum="{ids}" data-n="{nwords}" data-kind="m" data-key="m" style="display:flex;justify-content:space-between;font-size:14px">{tx('wMast')}<b>0 / {nwords}</b></div><div class="bar" style="margin-top:6px"><i data-fill="m" style="width:0;background:var(--green)"></i></div></div>
<div><div data-sum="{ids}" data-n="{nwrite}" data-kind="w" data-key="w" style="display:flex;justify-content:space-between;font-size:14px">{tx('wWrite')}<b>0 / {nwrite}</b></div><div class="bar" style="margin-top:6px"><i data-fill="w" style="width:0;background:var(--green)"></i></div></div></div>
<div class="box">{tx('coverH','p','k')}{tx('coverP','p','small', a=cov, b=lv['new'], lv=lv['n'])}<div class="bar"><i style="width:{round(cov/lv['new']*100)}%;background:{lv['color']}"></i></div></div>"""
    if n_open: side += f"""<div class="box dark" id="mock">{tx('mockH','p','k')}<p class="fun" style="margin:0;font-size:24px">{tx('mock1')}</p>{tx('mockSoon','p')}</div>"""
    if n_open:
        side += f'<div class="box">{tx("topicsH","p","k")}<div class="tags">{topics}</div></div>'
    wkey = 'statWrite12' if lv['write_note'] else 'statWrite'
    body = f"""<section class="lvhead" style="background:{lv['color']}"><div class="wrap">
<p class="crumb"><a href="../index.html" data-i="navHome">首页</a>　/　HSK {lv['n']}</p>
<div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap"><span class="badge" style="background:#fff;color:{lv['color']};font-size:18px">HSK {lv['n']}</span><h1>{tx('lv_' + lv['id'])}</h1></div>
<div class="stats4"><div><b>{lv['new']}</b>{tx('statNew','p', n=lv['total'])}</div><div><b>{lv['write']}</b>{tx(wkey,'p')}</div>
<div><b style="font-size:20px">{tx('exam_' + lv['exam'])}</b>{tx('statExam','p')}</div><div><b>{n_open}</b>{tx('statLessons','p', n=lv['plan'])}</div></div>
</div></section>
<main class="wrap lvmain"><div class="lessons">{tx('lessonsH','h2','sec')}{rows}</div><aside>{side}</aside></main>"""
    return page(f'HSK {lv["n"]} · 轻松学中文', 1, body, 'navLevels')

def lesson_page(L, prev, nxt, depth, crumb, practice_href, pdf_href):
    words = {w: py for w, py, en, ru in L['words']}
    vcards = ''.join(f'<button type="button" class="vc" data-w="{e(w)}"><span class="zh">{e(w)}</span><span class="py">{e(py)}</span><span class="mn">{e(en)}<br>{e(ru)}</span></button>'
                     for w, py, en, ru in L['words'])
    grams = ''
    for g in L['gram']:
        ex = ''.join(f'<p class="ex"><span>{nwrender(x, words)}</span><button type="button" class="play" data-say="{e(plain(x))}" aria-label="🔊">{SPK}</button></p>' for x in g['ex'])
        pr = ''.join(f'<details><summary>{e(q)}</summary>{e(a)}</details>' for q, a in g.get('prac', []))
        grams += f'<div class="gram"><h3>{e(g["title"])}</h3><span class="rule">{e(g["rule"])}</span>{ex}{pr}</div>'
    narrative = len(set(s for s, _ in L['text'])) == 1
    lines = ''.join(f'<div class="line">{"" if narrative else f"<span class=who>{e(s)}</span>"}<div class="say">{nwrender(t, words)}</div><button type="button" class="play" data-say="{e(plain(t))}" aria-label="🔊">{SPK}</button></div>'
                    for s, t in L['text'])
    qs = ''.join(f'<details><summary>{e(q)}</summary>{e(a)}</details>' for q, a in L['q'])
    chars = ''.join(f'<span>{e(c)}</span>' for c, py, w in L['write'])
    nav = lesson_nav(L['id'], L['title'])
    tag = tx('placeKicker') if nav['level'] == 'start' else tx('lessonInLevel', lv=nav['lv'], n=nav['no'])
    pager = '<div class="pager">' + (f'<a class="btn b-sky" href="{prev}" data-i="prev">← 上一课</a>' if prev else '<span></span>') + \
            (f'<a class="btn b-sky" href="{nxt}" data-i="next">下一课 →</a>' if nxt else '') + '</div>'
    body = f"""<section class="lhead"><div class="wrap"><p class="crumb">{crumb}</p>
<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap"><span class="badge" style="background:#17698F">{tag}</span>
<span class="small" style="color:#C9DCE8"><span data-i="topic_{L['id']}">{e(L['topic'])}</span> · {tx('nWords', n=len(L['words']))} · {tx('grammarN', n=len(L['gram']))}</span></div>
<h1>{e(L['title'])}</h1><div class="sub-tr" data-tr="title_{L['id']}"></div>
<div class="acts"><a class="btn b-gold" href="{practice_href}" data-i="startPractice">🎯 开始课后练习</a><a class="btn b-ink2" href="{pdf_href}" data-i="pdf">📄 上课幻灯片（PDF）</a></div></div></section>
<nav class="tabs" aria-label="Sections"><div class="wrap"><a href="#words" data-i="secWords">生词</a><a href="#grammar" data-i="secGram">语法和句型</a><a href="#text" data-i="secText">课文</a><a href="#chars" data-i="secChars">本课要会写的字</a><a href="{practice_href}" data-i="tabPractice">课后练习</a></div></nav>
<main class="wrap lmain">
<section id="words"><div class="sechead"><div>{tx('secWords','h2','sec')}{tx('leadWords','p')}</div>
<div class="toolbar"><button type="button" data-toggle="hide-py" data-box="vg" class="on" data-i="hidePy">隐藏拼音</button><button type="button" data-toggle="hide-mn" data-box="vg" class="on" data-i="hideMn">隐藏意思</button></div></div>
<div class="vgrid hide-py hide-mn" id="vg">{vcards}</div></section>
<section id="grammar">{tx('secGram','h2','sec')}<div class="ggrid" style="margin-top:12px">{grams}</div></section>
<section id="text"><div class="sechead"><div><h2 class="sec">{tx('secText')}：{e(L['text_title'])}</h2>{tx('leadText','p')}</div>
<div class="toolbar"><button type="button" data-toggle="allpy" data-box="tx" data-i="allPy">显示全部拼音</button></div></div>
<div class="text" id="tx">{lines}</div><div class="qs">{qs}</div></section>
<section id="chars">{tx('secChars','h2','sec')}{tx('leadChars','p','lead')}<div class="chars">{chars}</div></section>
<div class="cta"><div>{tx('ctaDone','p','t')}{tx('ctaList','p','d')}</div><a class="btn b-gold" href="{practice_href}" data-i="startPractice">🎯 开始课后练习</a></div>
{pager}</main>"""
    return page(f'{L["title"]} · 轻松学中文', depth, body, 'navLevels', json.dumps(nav, ensure_ascii=False))

def practice_page(lid, depth, lesson_href):
    h = open(os.path.join(PRACTICE, f'{lid}_practice.html'), encoding='utf-8').read()
    up = '../' * depth
    bar = ('<div style="max-width:760px;margin:0 auto;padding:12px 16px 0;display:flex;gap:14px;font-size:15px;font-weight:700">'
           f'<a href="{lesson_href}" style="color:#17698F;text-decoration:none" data-i="backLesson">← 回到课文</a>'
           f'<a href="{up}index.html" style="color:#17698F;text-decoration:none" data-i="courseHome">课程首页</a></div>')
    return h.replace('<div class="wrap" id="app"></div>', bar + '<div class="wrap" id="app"></div>', 1)

def redirect(target):
    return f'<!DOCTYPE html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={target}"><title>…</title></head><body><a href="{target}">{target}</a></body></html>'

def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    for d in ('assets', 'pdf', 'start', 'lessons', 'practice'): os.makedirs(os.path.join(OUT, d))
    open(os.path.join(OUT, 'assets/style.css'), 'w', encoding='utf-8').write(CSS)
    full = dict(TX); full.update({f'title_{k}': v for k, v in TITLES.items()}); full.update({f'topic_{k}': v for k, v in TOPICS.items()})
    open(os.path.join(OUT, 'assets/site.js'), 'w', encoding='utf-8').write(JS.replace('__TX__', json.dumps(full, ensure_ascii=False)).replace('__LANGS__', json.dumps(LANGS, ensure_ascii=False)))
    open(os.path.join(OUT, '.nojekyll'), 'w').write('')
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(home())
    for f in PDF_NAMES.values(): shutil.copy(os.path.join(PDFS, f), os.path.join(OUT, 'pdf', f))
    L = ALL['L1']
    crumb = f'<a href="../index.html" data-i="navHome">首页</a>　/　{tx("placementName")}'
    open(os.path.join(OUT, 'start/index.html'), 'w', encoding='utf-8').write(
        lesson_page(L, None, '../hsk2/01.html', 1, crumb, 'practice.html', f'../pdf/{PDF_NAMES["L1"]}'))
    open(os.path.join(OUT, 'start/practice.html'), 'w', encoding='utf-8').write(practice_page('L1', 1, 'index.html'))
    for lv in LEVELS:
        d = os.path.join(OUT, lv['id']); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(level_page(lv))
        for k, lid in enumerate(lv['lessons'], 1):
            L = ALL[lid]
            prev = f'{k-1:02d}.html' if k > 1 else None
            nxt = f'{k+1:02d}.html' if k < len(lv['lessons']) else None
            crumb = f'<a href="../index.html" data-i="navHome">首页</a>　/　<a href="index.html">HSK {lv["n"]}</a>　/　{tx("lessonN", n=k)}'
            open(os.path.join(d, f'{k:02d}.html'), 'w', encoding='utf-8').write(
                lesson_page(L, prev, nxt, 1, crumb, f'{k:02d}-practice.html', f'../pdf/{PDF_NAMES[lid]}'))
            open(os.path.join(d, f'{k:02d}-practice.html'), 'w', encoding='utf-8').write(practice_page(lid, 1, f'{k:02d}.html'))
    for lid in ALL:
        nav = lesson_nav(lid, '')
        open(os.path.join(OUT, 'lessons', f'{lid}.html'), 'w').write(redirect('../' + nav['lesson']))
        open(os.path.join(OUT, 'practice', f'{lid}.html'), 'w').write(redirect('../' + nav['practice']))
    print('site ok')

main()
