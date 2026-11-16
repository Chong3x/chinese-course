# 网站结构：等级、每课在网站上的位置
LEVELS = [
 {"id": "hsk1", "n": 1, "color": "#2E7D4F", "stage": "el", "new": 300, "total": 300, "write": "100", "write_note": "1–2", "exam": "LR", "plan": 15, "lessons": []},
 {"id": "hsk2", "n": 2, "color": "#17698F", "stage": "el", "new": 197, "total": 500, "write": "100", "write_note": "1–2", "exam": "LR", "plan": 10, "lessons": ["L2", "L3", "L4", "L5"]},
 {"id": "hsk3", "n": 3, "color": "#6B4FA0", "stage": "el", "new": 491, "total": 1000, "write": "250", "write_note": "", "exam": "F", "plan": 25, "lessons": []},
 {"id": "hsk4", "n": 4, "color": "#9A3412", "stage": "mid", "new": 990, "total": 2000, "write": "400", "write_note": "", "exam": "F", "plan": 50, "lessons": []},
 {"id": "hsk5", "n": 5, "color": "#7A5C00", "stage": "mid", "new": 1579, "total": 3600, "write": "550", "write_note": "", "exam": "F", "plan": 80, "lessons": []},
 {"id": "hsk6", "n": 6, "color": "#14304A", "stage": "mid", "new": 1777, "total": 5400, "write": "700", "write_note": "", "exam": "F", "plan": 90, "lessons": []},
]

def lesson_nav(lid, title):
    """网站上的位置。L1 是水平测试课，其他按等级编号。"""
    if lid == "L1":
        return {"id": lid, "level": "start", "no": 0, "title": title, "lesson": "start/index.html", "practice": "start/practice.html"}
    for lv in LEVELS:
        if lid in lv["lessons"]:
            no = lv["lessons"].index(lid) + 1
            return {"id": lid, "level": lv["id"], "lv": lv["n"], "no": no, "title": title,
                    "lesson": f"{lv['id']}/{no:02d}.html", "practice": f"{lv['id']}/{no:02d}-practice.html"}
    return None
