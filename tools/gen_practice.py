import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from content import LESSONS
from content_l1 import L1
from i18n import PRACTICE, LANGS, TITLES
from site_map import lesson_nav
LESSONS = [L1] + LESSONS

OUT = sys.argv[1]
ONLY = sys.argv[2:]  # lesson ids
TPL = open(os.path.join(os.path.dirname(__file__), 'practice_template.html'), encoding='utf-8').read()
HW = open('/home/claude/vendor/hw/package/dist/hanzi-writer.min.js', encoding='utf-8').read()
DATA_DIR = '/home/claude/vendor/hwd/package'

def build(L):
    strokes = {}
    for c, py, w in L['write']:
        strokes[c] = json.load(open(os.path.join(DATA_DIR, c + '.json'), encoding='utf-8'))
    data = {
        'id': L['id'], 'title': L['title'], 'sub': (lambda n: '课后练习 · 水平测试课' if n['level']=='start' else f"课后练习 · HSK {n['lv']} · 第 {n['no']} 课")(lesson_nav(L['id'], L['title'])),
        'words': [list(x) for x in L['words']], 'text_title': L['text_title'],
        'text': [list(x) for x in L['text']], 'narrative': len(set(s for s, _ in L['text'])) == 1,
        'q': [list(x) for x in L['q']], 'fill': [list(x) for x in L['fill']], 'fill_bank': L['fill_bank'],
        'order': [[list(c), a] for c, a in L['order']], 'fix': [list(x) for x in L['fix']],
        'write': [{'c': c, 'py': py, 'word': w} for c, py, w in L['write']],
        'tr': TITLES.get(L['id'], {}),
        'nav': lesson_nav(L['id'], L['title']),
    }
    def js(o):  # safe for inline <script>
        return json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
    audio_path = os.path.join(OUT, L['id'] + '_audio.json')
    audio = json.load(open(audio_path, encoding='utf-8')) if os.path.exists(audio_path) else {}
    html = (TPL.replace('__TITLE__', f"第 {L['num']} 课 · {L['title']} · 课后练习")
               .replace('__HANZI_WRITER__', HW.replace('</script', '<\\/script'))
               .replace('__DATA__', js(data)).replace('__I18N__', js(PRACTICE)).replace('__LANGS__', js(LANGS)).replace('__STROKES__', js(strokes)).replace('__AUDIO__', js(audio)))
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"{L['id']}_practice.html")
    open(p, 'w', encoding='utf-8').write(html)
    return p, len(html)

for L in LESSONS:
    if not ONLY or L['id'] in ONLY:
        print(build(L))
