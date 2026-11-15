# 中文课程资料库（HSK 3.0）

一对一中文课的全部资料：课程数据、上课幻灯片、课后练习网页和生成工具。
以后做中文教学网站时，可以直接用 `data/lessons/` 里的课程数据。

## 目录

| 路径 | 内容 |
| --- | --- |
| `data/lessons/L2.json` … | 每节课的结构化数据：生词（汉字、拼音、英文、俄文）、语法、课文、练习、答案、手写字 |
| `slides/` | 上课幻灯片（Claude Slides 格式：`project/deck.json` + `project/slides/*.html` + `project/deck.css`） |
| `practice/` | 课后练习网页（单个 HTML 文件，直接用浏览器打开） |
| `docs/` | 课程网站（GitHub Pages）：https://chong3x.github.io/chinese-course/ |
| `tools/` | 生成工具：`gen.py` 生成幻灯片，`gen_practice.py` 生成练习网页，`gen_site.py` 生成网站 |

## 课程进度

| 课 | 日期 | 话题 | 等级 |
| --- | --- | --- | --- |
| 第 1 课 | 2026-11-14 | 介绍我的国家（测水平） | A 版 HSK2–3 / B 版 HSK4 |
| 第 2 课 | 2026-11-16 | 我怎么去学校 | HSK 2 |
| 第 3 课 | 2026-11-18 | 我的爱好 | HSK 2 |
| 第 4 课 | 2026-11-23 | 我的好朋友 | HSK 2 |
| 第 5 课 | 2026-11-25 | 在饭馆 | HSK 2 |

## 标准和来源

- 第 2 课起的生词、拼音、手写字都按 2025 年 11 月发布的官方 HSK 考试大纲（新版 HSK，2026 年 12 月 13 日起正式考试）核对。
- 词表数据来自 [hsk30](https://pypi.org/project/hsk30/)（从官方大纲 PDF 提取，只含“词—等级”这类事实数据）。本仓库不重新分发官方词表；运行工具前请先下载这份数据。
- 课文、例句、练习题都是为这门课原创的。
- 笔顺数据：[Hanzi Writer](https://github.com/chanind/hanzi-writer)（MIT）＋ hanzi-writer-data（Arphic Public License）。商用网站上线前请再核对这两个许可。
- 课件里的人物（阿依达、小明、丽娜）都是虚构的。不要把学生的真名、录音或成绩放进这个仓库。

## 怎么生成

```bash
# 准备数据（官方大纲词表 + 笔顺数据）
git clone --depth 1 https://github.com/harukicoder/hsk30 /home/claude/hsk30repo
npm pack hanzi-writer hanzi-writer-data   # 解压到 /home/claude/vendor/hw 和 /home/claude/vendor/hwd

python3 tools/gen.py out/slides              # 生成幻灯片
python3 tools/gen_practice.py out/practice   # 生成练习网页
```

新课程：在 `tools/content.py` 里加一节课的数据，再运行上面两个命令。
