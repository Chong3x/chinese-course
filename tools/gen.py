import json, os, random, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from content import LESSONS

OUT = sys.argv[1]  # e.g. /home/claude/lessons

# official pinyin lookup for review words
E = {}
for l in open('/home/claude/hsk30repo/corpus/syllabus2025/syllabus2025_entries.tsv', encoding='utf-8'):
    p = l.rstrip('\n').split('\t')
    if p[0] != 'index':
        E.setdefault(p[4], []).append((int(p[1]) if p[1].isdigit() else 9, p[5]))
def py_of(w):
    return sorted(E[w])[0][1]

BASE_CSS = open('/home/claude/deck/project/deck.css', encoding='utf-8').read()
EXTRA_CSS = """
/* 游戏与新课 */
.goal { font-size: 30px; font-weight: 700; color: #14304A; background: #F2C14E; border-radius: 16px; padding: 12px 28px; margin: 0; align-self: flex-start; }
.wcard .mean { font-size: 26px; font-weight: 700; color: #17698F; margin: 0; text-align: center; }
.row .tag2 { font-size: 26px; font-weight: 700; color: #F7F5EE; background: #9A3412; border-radius: 10px; padding: 4px 14px; margin: 0; }
.headrow { display: flex; align-items: center; gap: 48px; }
.rows.tight { gap: 12px; }
.rows.tight .row { padding: 12px 28px; }
.vcard { background: #FDFCF8; border-radius: 20px; padding: 22px 14px; display: flex; flex-direction: column; align-items: center; gap: 6px; }
.vcard .zh { font-size: 52px; font-weight: 700; margin: 0; }
.vcard .py { font-size: 28px; color: #17698F; font-weight: 700; margin: 0; }
.vcard .en { font-size: 24px; color: #3D4F63; margin: 0; text-align: center; }
.vcard .ru { font-size: 24px; color: #3D4F63; margin: 0; text-align: center; }
.rule { font-size: 30px; font-weight: 700; color: #14304A; background: #F2C14E; border-radius: 16px; padding: 12px 28px; margin: 0; align-self: flex-start; }
.exs { display: flex; flex-direction: column; gap: 12px; }
.exs .ex { font-size: 40px; line-height: 1.5; margin: 0; padding-left: 28px; border-left: 8px solid #2FA4D8; }
.dialog { display: flex; flex-direction: column; gap: 10px; background: #FDFCF8; border-radius: 24px; padding: 32px 40px; }
.dialog .line { display: flex; gap: 20px; align-items: baseline; }
.dialog .spk { font-size: 26px; font-weight: 700; color: #F7F5EE; background: #17698F; border-radius: 10px; padding: 2px 0; width: 120px; text-align: center; flex: none; margin: 0; }
.dialog .say { font-size: 32px; line-height: 1.5; margin: 0; flex: 1; }
.dialog.big { padding: 22px 40px; gap: 6px; }
.dialog.big .say { font-size: 33px; }
.dialog .para { font-size: 34px; line-height: 1.6; margin: 0; }
.dialog.big .para { font-size: 36px; }
"""

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def render(s, pinyin, words):
    def rep(m):
        w = m.group(1)
        if pinyin:
            py = words.get(w) or {'得': 'de', '着': 'zhe', '过': 'guo'}.get(w) or py_of(w)
            return f'<span class="nw">{esc(w)}</span><span class="nwpy">{esc(py)}</span>'
        return esc(w)
    out = []
    pos = 0
    for m in re.finditer(r'\{([^}]+)\}', s):
        out.append(esc(s[pos:m.start()]))
        out.append(rep(m))
        pos = m.end()
    out.append(esc(s[pos:]))
    return ''.join(out)

def section(sid, cls, body, notes):
    c = f' class="{cls}"' if cls else ''
    return f'<section id="{sid}"{c}>\n{body}\n<aside>{esc(notes)}</aside>\n</section>\n'

def build(L):
    words = {w: py for w, py, en, ru in L['words']}
    n = L['num']
    S = []  # (id, html)
    # 1 cover
    S.append(('cover', section('cover', 'dark',
        f'<p class="eyebrow">第 {n} 课 · {esc(L["date"])}</p>\n<h1>{esc(L["title"])}</h1>\n'
        f'<p class="lead">话题：{esc(L["topic"])}</p>\n<p class="hello">今天学 20 个新词，认识它们的汉字！</p>',
        f'开场 1 分钟。本课 20 个生词全部来自 2025 年官方 HSK 考试大纲二级词表，话题“{L["topic"]}”。'
        '她的弱项是认汉字：今天每个环节都先看汉字、后看拼音，拼音一律点击才出现。')))
    # 2 warm
    qs = '\n'.join(f'<p class="q fragment">{esc(q)}</p>' for q in L['warm'])
    S.append(('warm', section('warm', 'alt',
        f'<p class="eyebrow">热身 · 聊一聊</p>\n<h2>热身：聊一聊</h2>\n<div class="qs">\n{qs}\n</div>\n'
        '<p class="tip">先听，再看。听不懂可以说：“请再说一遍。”</p>',
        '5 分钟。先口头问，她答不出来再点击显示文字。问题里已经用了今天的一些生词，她能听懂就说明这些词她会说，今天重点练认字。')))
    # 3 review
    cards = '\n'.join(f'<div class="wcard"><p class="zh">{esc(w)}</p><p class="mean fragment">{esc(py_of(w))}</p></div>' for w in L['review'])
    S.append(('review', section('review', '',
        f'<p class="eyebrow">复习 · {esc(L["review_title"])}</p>\n<h2>还认识这些字吗？</h2>\n<div class="grid5">\n{cards}\n</div>\n'
        '<p class="goal">看汉字，说拼音和意思</p>',
        '4 分钟。随便指一个词，她看汉字读出来、说出意思，再点击显示拼音。读不出来的词记下来，这节课结束前再问一次。')))
    # 4-5 new words
    for i in range(2):
        chunk = L['words'][i*10:(i+1)*10]
        cards = '\n'.join(
            f'<div class="vcard"><p class="zh">{esc(w)}</p><p class="py">{esc(py)}</p><p class="en">{esc(en)}</p><p class="ru">{esc(ru)}</p></div>'
            for w, py, en, ru in chunk)
        sid = f'new{i+1}'
        S.append((sid, section(sid, '',
            f'<p class="eyebrow">生词 {i*10+1}–{i*10+10}</p>\n<h2>生词（{"一二"[i]}）</h2>\n<div class="grid5">\n{cards}\n</div>',
            '5 分钟。每个词：你读两遍，她跟读两遍，再用这个词说一句话。'
            '读完这一页，用手遮住拼音（或者让她闭眼睛再睁开），指着汉字让她再读一遍。俄文释义请你课前核对。')))
    # 6-7 grammar
    for i, g in enumerate(L['gram']):
        exs = '\n'.join(f'<p class="ex">{render(e, True, words)}</p>' for e in g['ex'])
        rows = '\n'.join(f'<div class="row"><p class="n">{k+1}</p><p class="prompt">{esc(p)}</p><p class="ans fragment">{esc(a)}</p></div>'
                         for k, (p, a) in enumerate(g['prac']))
        sid = f'gram{i+1}'
        S.append((sid, section(sid, 'alt',
            f'<p class="eyebrow">语法 {i+1}</p>\n<h2>{esc(g["title"])}</h2>\n<p class="rule">{esc(g["rule"])}</p>\n'
            f'<div class="exs">\n{exs}\n</div>\n<div class="rows">\n{rows}\n</div>',
            '6 分钟。先读例句，她跟读；再让她回答下面两个问题，答完点击显示参考答案。'
            '最后让她自己用这个句型说两句关于自己的话。')))
    # 8 text with pinyin, 9 text hanzi only + questions
    narrative = len(set(s for s, _ in L['text'])) == 1
    def dialog(pinyin, big):
        if narrative:
            inner = '\n'.join(f'<p class="para">{render(t, pinyin, words)}</p>' for _, t in L['text'])
        else:
            inner = '\n'.join(f'<div class="line"><p class="spk">{esc(s)}</p><p class="say">{render(t, pinyin, words)}</p></div>' for s, t in L['text'])
        return f'<div class="dialog{" big" if big else ""}">\n{inner}\n</div>'
    S.append(('text1', section('text1', '',
        f'<p class="eyebrow">课文 · 拼音版</p>\n<h2>{esc(L["text_title"])}</h2>\n{dialog(True, False)}',
        '5 分钟。你先读一遍，她跟读一遍。生词后面有拼音。读完以后翻到下一页，不看拼音再读一遍。')))
    qrow = '\n'.join(f'<p class="qchip fragment">{esc(q)}</p>' for q, a in L['q'])
    ans = '；'.join(f'{q} {a}' for q, a in L['q'])
    S.append(('text2', section('text2', 'alt',
        f'<p class="eyebrow">课文 · 汉字版（挑战）</p>\n<h2>不看拼音，再读一遍！</h2>\n{dialog(False, True)}\n<div class="qrow">\n{qrow}\n</div>',
        f'5 分钟。这一页没有拼音，这是她最需要练的。读不出来的字先等 3 秒，再提示拼音的第一个声母。读完点击显示问题。答案：{ans}')))
    # 10-11 recognition game
    rnd = random.Random(L['id'])
    mixed = L['words'][:]
    rnd.shuffle(mixed)
    for i in range(2):
        chunk = mixed[i*10:(i+1)*10]
        cards = '\n'.join(f'<div class="wcard"><p class="zh">{esc(w)}</p><p class="mean fragment">{esc(py)} · {esc(en)}</p></div>' for w, py, en, ru in chunk)
        sid = f'rec{i+1}'
        S.append((sid, section(sid, '',
            f'<p class="eyebrow">游戏 1 · 闪电认字（{"上下"[i]}）</p>\n<h2>看汉字，3 秒说出拼音和意思</h2>\n<div class="grid5">\n{cards}\n</div>\n'
            '<p class="goal">过关：10 个词都在 3 秒内说对</p>',
            '4 分钟。词的顺序已经打乱。玩法一：你指一个，她 3 秒内读出来，再点击显示答案。'
            '玩法二（听音找字）：你说一个词，她说出它在第几个。答错的词这一关最后再来一次。')))
    # 12 fill
    bank = ''.join(f'<p class="chip">{esc(w)}</p>' for w in L['fill_bank'])
    rows = '\n'.join(f'<div class="row"><p class="n">{k+1}</p><p class="prompt">{esc(p.replace("___", "______"))}</p><p class="ans fragment">{esc(a)}</p></div>'
                     for k, (p, a) in enumerate(L['fill']))
    S.append(('fill', section('fill', '',
        f'<p class="eyebrow">游戏 2 · 选词填空</p>\n<div class="headrow"><h2>选词填空</h2><div class="chips">{bank}</div></div>\n<div class="rows tight">\n{rows}\n</div>',
        '4 分钟。她说出答案后，把整句读一遍，再点击显示答案。整句读出来比只说一个词记得牢。')))
    # 13 order
    rows = '\n'.join(f'<div class="row"><p class="n">{k+1}</p><div class="chips">{"".join(f"<p class=\"chip\">{esc(c)}</p>" for c in chips)}</div><p class="ans fragment">{esc(a)}</p></div>'
                     for k, (chips, a) in enumerate(L['order']))
    S.append(('order', section('order', 'alt',
        f'<p class="eyebrow">游戏 3 · 排一排</p>\n<h2>排一排，变成一句话</h2>\n<div class="rows">\n{rows}\n</div>\n<p class="goal">过关：在 Meet 聊天框里打出正确的句子</p>',
        '3 分钟。让她把句子打在 Meet 聊天框里，练汉字输入。打对了再点击显示答案。')))
    # 14 fix
    rows = '\n'.join(f'<div class="row"><p class="tag2">错句</p><p class="prompt">{esc(w)}</p><p class="ans fragment">{esc(r)}</p></div>'
                     for w, r in L['fix'])
    S.append(('fix', section('fix', '',
        f'<p class="eyebrow">游戏 4 · 找错误</p>\n<h2>找错误：哪里不对？</h2>\n<div class="rows">\n{rows}\n</div>',
        f'3 分钟。让她先说错在哪儿、说出正确的句子，再点击显示答案。错在哪里：{L["fix_note"]}')))
    # 15 speak
    frames = '\n'.join(f'<p class="frame">{esc(f)}</p>' for f in L['speak'])
    S.append(('speak', section('speak', 'alt',
        f'<p class="eyebrow">说一说</p>\n<h2>{esc(L["speak_title"])}</h2>\n<div class="frames">\n{frames}\n</div>',
        '4 分钟。让她用这些句子说自己的情况。第一遍不打断，说完只纠正 1–2 个最重要的错误，再让她重说一遍。')))
    # 16 homework
    tags = ['写一写', '读一读', '认一认']
    cards = '\n'.join(f'<div class="hwcard"><p class="tag">{t}</p><p class="body">{esc(b)}</p></div>' for t, b in zip(tags, L['hw']))
    S.append(('homework', section('homework', 'gold',
        f'<p class="eyebrow">作业 · 三选一</p>\n<h2>今天的作业</h2>\n<div class="hw">\n{cards}\n</div>\n<p class="lead">{esc(L["next"])}</p>',
        '1 分钟。作业量要小。“认一认”最适合她：每天花 5 分钟看汉字说拼音，两周后认字会明显进步。'
        '下课前回到“复习”和“闪电认字”里答错的词，再问一遍。')))
    return S

def write_deck(L):
    root = os.path.join(OUT, L['id'], 'project')
    os.makedirs(os.path.join(root, 'slides'), exist_ok=True)
    S = build(L)
    for sid, html in S:
        open(os.path.join(root, 'slides', sid + '.html'), 'w', encoding='utf-8').write(html)
    open(os.path.join(root, 'deck.css'), 'w', encoding='utf-8').write(BASE_CSS + EXTRA_CSS)
    idx = {"v": 5, "createdOnFiles": {"v": 1, "at": "2026-11-15T15:00:00Z"}, "lists": "css",
           "format": {"v": 1, "shared": ["project/deck.css"]},
           "title": f"第 {L['num']} 课 · {L['title']}", "cover": "cover", "order": [s for s, _ in S],
           "sections": {"s1": {"description": "开场：热身和复习上节课", "start": "cover"},
                        "s2": {"description": "生词：20 个 HSK2 官方词", "start": "new1"},
                        "s3": {"description": "语法：两个句型", "start": "gram1"},
                        "s4": {"description": "课文：拼音版和汉字版", "start": "text1"},
                        "s5": {"description": "练习游戏：认字、填空、排词、改错", "start": "rec1"},
                        "s6": {"description": "说一说和作业", "start": "speak"}},
           "faces": {"noto-sans-sc": {"family": "Noto Sans SC", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap"},
                     "zcool-kuaile": {"family": "ZCOOL KuaiLe", "href": "https://fonts.googleapis.com/css2?family=ZCOOL+KuaiLe&display=swap"}},
           "designSystems": []}
    open(os.path.join(root, 'deck.json'), 'w', encoding='utf-8').write(json.dumps(idx, ensure_ascii=False))
    return [s for s, _ in S]

for L in LESSONS:
    print(L['id'], write_deck(L))
