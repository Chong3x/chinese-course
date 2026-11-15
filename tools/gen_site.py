"""生成课程网站（GitHub Pages，放在 docs/ 目录）"""
import os, re, shutil, sys, json, html
sys.path.insert(0, os.path.dirname(__file__))
from content import LESSONS
from content_l1 import L1
from i18n import SITE as TX, LANGS, TITLES, TOPICS, DATES

OUT = sys.argv[1]          # e.g. /home/claude/repo/docs
PRACTICE = sys.argv[2]     # folder with Ln_practice.html
PDFS = sys.argv[3]         # folder with student PDFs
ALL = [L1] + LESSONS
SITE = "轻松学中文"
PDF_NAMES = {"L1": "第01课_介绍我的国家.pdf", "L2": "第02课_我怎么去学校.pdf", "L3": "第03课_我的爱好.pdf",
             "L4": "第04课_我的好朋友.pdf", "L5": "第05课_在饭馆.pdf"}

def e(s): return html.escape(str(s), quote=True)

def tx(key, tag='span', cls='', **v):
    zh = TX[key]['zh']
    for k, val in v.items(): zh = zh.replace('{'+k+'}', str(val))
    dv = f" data-v='{e(json.dumps(v, ensure_ascii=False))}'" if v else ''
    c = f' class="{cls}"' if cls else ''
    return f'<{tag}{c} data-i="{key}"{dv}>{e(zh)}</{tag}>'

CSS = """
:root{--ink:#14304A;--soft:#3D4F63;--bg:#F7F5EE;--card:#FDFCF8;--sky:#E3F0F6;--blue:#17698F;--blue2:#2FA4D8;--gold:#F2C14E;--line:#D9E2E8}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--ink);font-family:'Noto Sans SC','PingFang SC','Microsoft YaHei',Arial,sans-serif;line-height:1.6}
a{color:var(--blue)}
.fun{font-family:'ZCOOL KuaiLe','Noto Sans SC',sans-serif;font-weight:400}
.wrap{max-width:960px;margin:0 auto;padding:0 18px}
nav.top{background:var(--ink);color:#F7F5EE}
nav.top .wrap{display:flex;align-items:center;justify-content:space-between;height:60px;gap:12px}
nav.top a{color:#F7F5EE;text-decoration:none;font-weight:700}
nav.top .brand{font-size:22px}
nav.top .links a{margin-left:16px;font-size:15px;opacity:.9}
.hero{background:var(--ink);color:#F7F5EE;padding:40px 0 56px}
.hero h1{font-size:44px;margin:0 0 10px;line-height:1.2}
.hero p{color:#C9DCE8;font-size:18px;margin:0 0 22px;max-width:640px}
.btn{display:inline-block;border:none;border-radius:14px;padding:12px 20px;font-size:17px;font-weight:700;text-decoration:none;cursor:pointer;font-family:inherit}
.b-gold{background:var(--gold);color:var(--ink)}.b-blue{background:var(--blue);color:#fff}.b-sky{background:var(--sky);color:var(--ink)}
section.block{padding:34px 0 8px}
h2.sec{font-size:30px;margin:0 0 6px}
p.lead{color:var(--soft);margin:0 0 18px}
.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.step{background:var(--card);border-radius:18px;padding:16px}
.step b{display:block;font-size:30px;color:var(--blue)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}
.lcard{background:var(--card);border-radius:20px;padding:20px;display:flex;flex-direction:column;gap:8px;border:2px solid transparent}
.lcard:hover{border-color:var(--blue2)}
.lcard .k{font-size:13px;font-weight:700;color:var(--blue);letter-spacing:1px}
.lcard h3{margin:0;font-size:24px}
.lcard .t{color:var(--soft);font-size:14px}
.lcard .w{font-size:20px;letter-spacing:2px}
.lcard .acts{display:flex;gap:8px;margin-top:auto;padding-top:8px;flex-wrap:wrap}
.lcard .acts a{font-size:15px;padding:9px 14px}
.tag{display:inline-block;background:var(--gold);color:var(--ink);border-radius:8px;padding:1px 8px;font-size:12px;font-weight:700;margin-left:6px;vertical-align:middle}
.res{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.res a{background:var(--card);border-radius:16px;padding:16px;text-decoration:none;color:var(--ink);display:block}
.res a b{display:block;font-size:17px}.res a span{color:var(--soft);font-size:14px}
footer{margin-top:40px;padding:24px 0 40px;color:var(--soft);font-size:13px;border-top:1px solid var(--line)}
.lhead{background:var(--ink);color:#F7F5EE;padding:26px 0 30px}
.lhead .k{color:var(--gold);font-weight:700;font-size:14px;letter-spacing:1px}
.lhead h1{font-size:40px;margin:4px 0 6px;line-height:1.2}
.lhead p{color:#C9DCE8;margin:0 0 16px}
.lhead .acts{display:flex;gap:10px;flex-wrap:wrap}
.toolbar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
.toolbar button{border:2px solid var(--line);background:#fff;border-radius:12px;padding:8px 12px;font-size:15px;font-weight:700;color:var(--ink);cursor:pointer;font-family:inherit}
.toolbar button.on{border-color:var(--blue);background:var(--sky)}
.vgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.vc{background:var(--card);border-radius:16px;padding:14px 10px;text-align:center;cursor:pointer;border:2px solid transparent;user-select:none}
.vc:active{border-color:var(--blue2)}
.vc .zh{font-size:34px;font-weight:700;line-height:1.3}
.vc .py{color:var(--blue);font-weight:700;font-size:16px}
.vc .mn{color:var(--soft);font-size:13px;line-height:1.4}
.hide-py .vc:not(.open) .py,.hide-mn .vc:not(.open) .mn{visibility:hidden}
.gram{background:var(--card);border-radius:18px;padding:16px 18px;margin-bottom:12px}
.gram h3{margin:0 0 6px;font-size:22px}
.gram .rule{display:inline-block;background:var(--gold);border-radius:10px;padding:4px 12px;font-weight:700;font-size:15px;margin-bottom:8px}
.gram .ex{font-size:20px;margin:6px 0;padding-left:14px;border-left:5px solid var(--blue2)}
.gram details{margin-top:8px;color:var(--soft)}
.text{background:var(--card);border-radius:18px;padding:12px 16px}
.line{display:flex;gap:10px;align-items:flex-start;padding:10px 0;border-bottom:1px solid var(--line)}
.line:last-child{border-bottom:none}
.who{flex:none;background:var(--blue);color:#fff;border-radius:8px;padding:2px 8px;font-size:13px;font-weight:700;margin-top:6px}
.say{flex:1;font-size:21px;line-height:1.8}
.play{flex:none;border:none;background:var(--sky);border-radius:10px;padding:6px 10px;font-size:17px;cursor:pointer}
.nw{font-weight:700;border-bottom:2px dotted var(--blue2);cursor:pointer}
.nw .p{display:none;font-size:13px;color:var(--blue);font-weight:400;margin-left:2px}
.nw.show .p,.allpy .nw .p{display:inline}
.qs{margin-top:12px}
.qs details{background:var(--card);border-radius:12px;padding:10px 14px;margin-bottom:8px}
.chars{display:flex;gap:10px;flex-wrap:wrap}
.chars span{background:#fff;border:2px solid var(--line);border-radius:12px;width:58px;height:58px;display:flex;align-items:center;justify-content:center;font-size:30px;font-weight:700}
.lang{border:none;border-radius:10px;padding:6px 8px;font-size:14px;background:#24496B;color:#F7F5EE;font-family:inherit;margin-left:14px}
.sub-tr{font-size:15px;color:#C9DCE8;margin:-4px 0 8px}
.lcard .sub-tr{color:var(--soft);font-size:14px;margin:0}
.pager{display:flex;justify-content:space-between;gap:10px;margin-top:30px}
@media (max-width:640px){nav.top .brand{font-size:18px;white-space:nowrap}nav.top .links a{display:none}.lang{margin-left:6px}.hero h1{font-size:34px}.steps{grid-template-columns:1fr 1fr}.lhead h1{font-size:30px}nav.top .links a{margin-left:10px;font-size:14px}.say{font-size:19px}}
"""

JS = """
const TX=__TX__, LANGS=__LANGS__, LOC={zh:"zh-CN",kk:"kk-KZ",en:"en-GB",ru:"ru-RU"};
let LANG="zh";try{LANG=localStorage.getItem("ui-lang")||"zh";}catch(e){}
function tr(k,v){let s=(TX[k]||{})[LANG];if(s===undefined)s=(TX[k]||{}).zh||"";if(v)for(const x in v)s=String(s).split("{"+x+"}").join(v[x]);return s;}
function apply(){document.documentElement.lang=LANG==="zh"?"zh-CN":LANG;document.querySelectorAll("[data-i]").forEach(el=>{const v=el.dataset.v?JSON.parse(el.dataset.v):null;el.textContent=tr(el.dataset.i,v);});
 document.querySelectorAll("[data-date]").forEach(el=>{try{const d=new Date(el.dataset.date+"T12:00:00");
  if(LANG==="kk"){const M=["қаңтар","ақпан","наурыз","сәуір","мамыр","маусым","шілде","тамыз","қыркүйек","қазан","қараша","желтоқсан"],W=["жексенбі","дүйсенбі","сейсенбі","сәрсенбі","бейсенбі","жұма","сенбі"];el.textContent=d.getDate()+" "+M[d.getMonth()]+", "+W[d.getDay()];}
  else el.textContent=d.toLocaleDateString(LOC[LANG],{month:"long",day:"numeric",weekday:"short"});}catch(e){}});
 document.querySelectorAll("[data-tr]").forEach(el=>{const s=tr(el.dataset.tr);el.textContent=LANG==="zh"?"":s;el.style.display=(LANG==="zh"||!s)?"none":"";});
 const sel=document.getElementById("lang");if(sel)sel.value=LANG;}
function setLang(l){LANG=l;try{localStorage.setItem("ui-lang",l);}catch(e){}apply();}
document.addEventListener("DOMContentLoaded",apply);

let zh=null;function pv(){try{const v=speechSynthesis.getVoices();zh=v.find(x=>/^zh(-|_)?CN/i.test(x.lang))||v.find(x=>/^zh/i.test(x.lang))||null;}catch(e){}}
try{pv();speechSynthesis.onvoiceschanged=pv;}catch(e){}
function say(t){if(!zh){alertBox(tr('noVoice'));return;}try{speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(t);u.voice=zh;u.lang=zh.lang;u.rate=0.8;speechSynthesis.speak(u);}catch(e){}}
function alertBox(m){let d=document.getElementById('msg');if(!d){d=document.createElement('div');d.id='msg';d.style.cssText='position:fixed;left:50%;bottom:20px;transform:translateX(-50%);background:#14304A;color:#fff;padding:10px 16px;border-radius:12px;z-index:9';document.body.appendChild(d);}d.textContent=m;d.style.display='block';setTimeout(()=>d.style.display='none',2500);}
document.addEventListener('click',ev=>{
  const c=ev.target.closest('.vc');if(c){c.classList.toggle('open');say(c.dataset.w);return;}
  const n=ev.target.closest('.nw');if(n){n.classList.toggle('show');return;}
  const p=ev.target.closest('[data-say]');if(p){say(p.dataset.say);return;}
  const t=ev.target.closest('[data-toggle]');if(t){const cls=t.dataset.toggle;const box=document.getElementById(t.dataset.box);box.classList.toggle(cls);t.classList.toggle('on');}
});
"""

def head(title, depth):
    up = '../' * depth
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&family=ZCOOL+KuaiLe&display=swap">
<link rel="stylesheet" href="{up}assets/style.css"></head><body>
<nav class="top"><div class="wrap"><a class="brand fun" href="{up}index.html">{SITE}</a>
<div class="links"><a href="{up}index.html#lessons" data-i="navLessons">课程</a><a href="{up}index.html#more" data-i="navMore">更多资料</a>
<select id="lang" class="lang" onchange="setLang(this.value)" aria-label="Language">{''.join(f'<option value="{k}">{n}</option>' for k, n in LANGS)}</select></div></div></nav>"""

def foot(depth):
    up = '../' * depth
    return f"""<footer><div class="wrap">
{tx('foot1','p')}{tx('foot2','p')}
</div></footer><script src="{up}assets/site.js"></script></body></html>"""

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

def level_tag(L): return '入门复习' if L['id'] == 'L1' else 'HSK 2'

def lesson_page(L, prev, nxt):
    words = {w: py for w, py, en, ru in L['words']}
    n = L['num']
    vcards = ''.join(f'<div class="vc" data-w="{e(w)}"><div class="zh">{e(w)}</div><div class="py">{e(py)}</div><div class="mn">{e(en)}<br>{e(ru)}</div></div>'
                     for w, py, en, ru in L['words'])
    grams = ''
    for g in L['gram']:
        ex = ''.join(f'<p class="ex">{nwrender(x, words)} <button class="play" data-say="{e(plain(x))}">🔊</button></p>' for x in g['ex'])
        pr = ''.join(f'<details><summary>{e(q)}</summary>{e(a)}</details>' for q, a in g.get('prac', []))
        grams += f'<div class="gram"><h3>{e(g["title"])}</h3><div class="rule">{e(g["rule"])}</div>{ex}{pr}</div>'
    narrative = len(set(s for s, _ in L['text'])) == 1
    lines = ''.join(f'<div class="line">{"" if narrative else f"<span class=who>{e(s)}</span>"}<div class="say">{nwrender(t, words)}</div><button class="play" data-say="{e(plain(t))}">🔊</button></div>'
                    for s, t in L['text'])
    qs = ''.join(f'<details><summary>{e(q)}</summary>{e(a)}</details>' for q, a in L['q'])
    chars = ''.join(f'<span>{e(c)}</span>' for c, py, w in L['write'])
    pager = f'<div class="pager">{f"<a class=\"btn b-sky\" href=\"{prev}.html\" data-i=\"prev\">← 上一课</a>" if prev else "<span></span>"}{f"<a class=\"btn b-sky\" href=\"{nxt}.html\" data-i=\"next\">下一课 →</a>" if nxt else ""}</div>'
    body = f"""{head(f'第 {n} 课 · {L["title"]} · {SITE}', 1)}
<header class="lhead"><div class="wrap"><div class="k">{tx('lessonN', n=n)} · {e(level_tag(L)) if L['id']!='L1' else tx('tagReview')} · <span data-date="{DATES[L['id']]}">{e(L.get('date',''))}</span></div>
<h1 class="fun">{e(L['title'])}</h1><div class="sub-tr" data-tr="title_{L['id']}"></div><p>{tx('topicLabel')}<span data-i="topic_{L['id']}">{e(L.get('topic',''))}</span>　·　{tx('nWords', n=len(L['words']))}</p>
<div class="acts"><a class="btn b-gold" href="../practice/{L['id']}.html" data-i="startPractice">🎯 开始课后练习</a><a class="btn b-sky" href="../pdf/{e(PDF_NAMES[L['id']])}" data-i="pdf">📄 上课幻灯片（PDF）</a></div></div></header>
<main class="wrap">
<section class="block">{tx('secWords','h2','sec fun')}{tx('leadWords','p','lead')}
<div class="toolbar"><button data-toggle="hide-py" data-box="vg" class="on" data-i="hidePy">隐藏拼音</button><button data-toggle="hide-mn" data-box="vg" class="on" data-i="hideMn">隐藏意思</button></div>
<div class="vgrid hide-py hide-mn" id="vg">{vcards}</div></section>
<section class="block">{tx('secGram','h2','sec fun')}{grams}</section>
<section class="block"><h2 class="sec fun">{tx('secText')}：{e(L['text_title'])}</h2>{tx('leadText','p','lead')}
<div class="toolbar"><button data-toggle="allpy" data-box="tx" data-i="allPy">显示全部拼音</button></div>
<div class="text" id="tx">{lines}</div><div class="qs">{qs}</div></section>
<section class="block">{tx('secChars','h2','sec fun')}{tx('leadChars','p','lead')}<div class="chars">{chars}</div></section>
{pager}
</main>{foot(1)}"""
    return body

def index_page():
    cards = ''
    for L in ALL:
        ws = '　'.join(w for w, *_ in L['words'][:4])
        tag = tx('tagReview', cls='tag') if L['id'] == 'L1' else f'<span class="tag">{e(level_tag(L))}</span>'
        cards += f"""<div class="lcard"><div class="k">{tx('lessonN', n=L['num'])}{tag}</div><h3 class="fun">{e(L['title'])}</h3><div class="sub-tr" data-tr="title_{L['id']}"></div>
<div class="t"><span data-i="topic_{L['id']}">{e(L.get('topic',''))}</span> · {tx('nWords', n=len(L['words']))}</div><div class="w">{e(ws)}……</div>
<div class="acts"><a class="btn b-blue" href="lessons/{L['id']}.html" data-i="btnText">📖 学课文</a><a class="btn b-gold" href="practice/{L['id']}.html" data-i="btnPractice">🎯 练习</a></div></div>"""
    res = [("https://hskstory.com/", "r1"), ("https://hskstory.com/guides/hsk-30-syllabus", "r2"),
           ("https://hskstory.com/guides/hsk-3-syllabus", "r3"), ("https://www.chinesetest.cn", "r4")]
    resh = ''.join(f'<a href="{u}" target="_blank" rel="noopener"><b>{tx(k+"t")} ↗</b>{tx(k+"d")}</a>' for u, k in res)
    return f"""{head(SITE + ' · 新版 HSK 课程', 0)}
<header class="hero"><div class="wrap"><h1 class="fun">轻松学中文</h1>
{tx('heroP','p')}
<a class="btn b-gold" href="lessons/L2.html" data-i="start">开始学习 →</a></div></header>
<main class="wrap">
<section class="block">{tx('howTitle','h2','sec fun')}{tx('howLead','p','lead')}
<div class="steps"><div class="step"><b>1</b>{tx('step1')}</div><div class="step"><b>2</b>{tx('step2')}</div>
<div class="step"><b>3</b>{tx('step3')}</div><div class="step"><b>4</b>{tx('step4')}</div></div></section>
<section class="block" id="lessons">{tx('lessonsTitle','h2','sec fun')}{tx('lessonsLead','p','lead')}
<div class="cards">{cards}</div></section>
<section class="block" id="more">{tx('moreTitle','h2','sec fun')}{tx('moreLead','p','lead')}<div class="res">{resh}</div></section>
</main>{foot(0)}"""

def practice_page(lid):
    h = open(os.path.join(PRACTICE, f'{lid}_practice.html'), encoding='utf-8').read()
    bar = ('<div style="max-width:760px;margin:0 auto;padding:12px 16px 0;display:flex;gap:14px;font-size:15px;font-weight:700">'
           f'<a href="../lessons/{lid}.html" style="color:#17698F;text-decoration:none" data-i="backLesson">← 回到课文</a>'
           '<a href="../index.html" style="color:#17698F;text-decoration:none" data-i="courseHome">课程首页</a></div>')
    return h.replace('<div class="wrap" id="app"></div>', bar + '<div class="wrap" id="app"></div>', 1)

def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    for d in ('assets', 'lessons', 'practice', 'pdf'): os.makedirs(os.path.join(OUT, d))
    open(os.path.join(OUT, 'assets/style.css'), 'w', encoding='utf-8').write(CSS)
    full = dict(TX); full.update({f'title_{k}': v for k, v in TITLES.items()}); full.update({f'topic_{k}': v for k, v in TOPICS.items()})
    open(os.path.join(OUT, 'assets/site.js'), 'w', encoding='utf-8').write(JS.replace('__TX__', json.dumps(full, ensure_ascii=False)).replace('__LANGS__', json.dumps(LANGS, ensure_ascii=False)))
    open(os.path.join(OUT, '.nojekyll'), 'w').write('')
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(index_page())
    ids = [L['id'] for L in ALL]
    for i, L in enumerate(ALL):
        prev = ids[i-1] if i > 0 else None
        nxt = ids[i+1] if i + 1 < len(ids) else None
        open(os.path.join(OUT, 'lessons', L['id'] + '.html'), 'w', encoding='utf-8').write(lesson_page(L, prev, nxt))
        open(os.path.join(OUT, 'practice', L['id'] + '.html'), 'w', encoding='utf-8').write(practice_page(L['id']))
        shutil.copy(os.path.join(PDFS, PDF_NAMES[L['id']]), os.path.join(OUT, 'pdf', PDF_NAMES[L['id']]))
    print('site ok', ids)

main()
