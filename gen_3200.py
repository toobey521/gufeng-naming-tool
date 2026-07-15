# -*- coding: utf-8 -*-
"""古风取名 v3.2 — 3200字库 + 新评分体系（五行为王）
   评分维度：五行命理35 + 诗文出处20 + 音律读音20 + 字义内涵20 + 字形书写15 = 110
"""
import os, sys, json, random
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from char_db_3200 import CHAR_SET, get_char_info, get_wuxing_gender, STATS

def find_data(name):
    paths = []
    try: paths.append(os.path.join(sys._MEIPASS, name))
    except: pass
    try: paths.append(os.path.join(os.path.dirname(sys.executable), name))
    except: pass
    paths.append(os.path.join(BASE, name))
    paths.append(name)
    for p in paths:
        if os.path.exists(p): return p
    return None

NAME_POOL = {}
pool_path = find_data('name_pool.json')
if pool_path:
    with open(pool_path, 'r', encoding='utf-8') as f:
        NAME_POOL = json.load(f)
    NAME_POOL = {k:v for k,v in NAME_POOL.items()
                 if k[0] in CHAR_SET and k[1] in CHAR_SET}

GEN_VERSION = '3.2'
CLASSICS_HIGH = {'诗经','楚辞','周易','论语','尚书','礼记','道德经','庄子'}
BAD_HOMOPHONES = {'王八','死','傻','笨','猪','狗','屎','尿','屁','瘟','丧','哭'}

def score(pair, bazi, gender='male'):
    c1, c2 = pair[0], pair[1]
    i1, i2 = get_char_info(c1), get_char_info(c2)
    if not i1: i1 = {'char':c1,'pinyin':'','tone':2,'strokes':8,'wuxing':'土','gender':'n','tags':'','meaning':''}
    if not i2: i2 = {'char':c2,'pinyin':'','tone':2,'strokes':8,'wuxing':'土','gender':'n','tags':'','meaning':''}
    src = NAME_POOL.get(pair, []) if isinstance(NAME_POOL, dict) else []

    # 五行命理 0-35
    bazi_score = 15
    if bazi:
        rec = bazi.get('recommend_element', '')
        if rec:
            mc = sum(1 for c in pair if get_char_info(c) and get_char_info(c)['wuxing'] == rec)
            if mc == 2:
                bazi_score = 35 if i1.get('wuxing','') != i2.get('wuxing','') else 33
            elif mc == 1:
                bazi_score = 25
            else:
                bazi_score = 12
        else:
            bazi_score = 18
    bazi_score = max(0, min(bazi_score, 35))

    # 诗文出处 0-20
    lit_score = 3
    if src:
        hc = sum(1 for s in src if s.get('s','') in CLASSICS_HIGH or any(c in s.get('t','') for c in ['诗经','楚辞','周易','论语']))
        if hc >= 1 and len(src) >= 2:
            lit_score = 18
        elif hc >= 1:
            lit_score = 14
        else:
            lit_score = 7
    lit_score = max(0, min(lit_score, 20))

    # 音律读音 0-20
    tone_score = 10
    t1, t2 = i1['tone'], i2['tone']
    if (t1 <= 2 and t2 >= 3) or (t1 >= 3 and t2 <= 2):
        tone_score = 16
    elif t1 != t2:
        tone_score = 13
    else:
        tone_score = 8
    if t1 == 3 and t2 == 3: tone_score = 5
    if t1 == 4 and t2 == 4: tone_score = 7
    for bad in BAD_HOMOPHONES:
        if bad in pair[0] or bad in pair[1]:
            tone_score = 2; break
    tone_score = max(0, min(tone_score, 20))

    # 字义内涵 0-20
    meaning_score = 10
    for c in pair:
        if c in '德仁义礼智信忠孝悌恕恭宽惠敏和': meaning_score += 3
        elif c in '光明希望美好坚韧智慧正直高洁清雅温和积极远大': meaning_score += 2
        elif c in '善良包容从容文雅坚定诚信才华吉祥尊贵祥瑞富贵': meaning_score += 2
        if c in '霸皇天帝龙王': meaning_score -= 2
        if c in '奴婢妾妓娼淫': meaning_score -= 5
        if c in '愁苦悲凄凉寒孤': meaning_score -= 3
    meaning_score = max(0, min(meaning_score, 20))

    # 字形书写 0-15
    stroke_score = 10
    ts = i1['strokes'] + i2['strokes']
    if ts <= 16: stroke_score = 13
    elif ts <= 22: stroke_score = 12
    elif ts <= 28: stroke_score = 8
    elif ts <= 34: stroke_score = 5
    else: stroke_score = 3
    if abs(i1['strokes'] - i2['strokes']) > 8: stroke_score -= 2
    stroke_score = max(0, min(stroke_score, 15))

    total_raw = bazi_score + lit_score + tone_score + meaning_score + stroke_score
    total = int(total_raw * 100 / 110)
    total = min(total, 100)

    return {
        'pair': pair, 'sources': src,
        'total': total,
        'bazi_score': bazi_score,
        'lit_score': lit_score,
        'tone_score': tone_score,
        'meaning_score': meaning_score,
        'stroke_score': stroke_score,
        'strokes_total': ts,
    }

def generate(surname, year, month, day, gender, hour=12, count=20, fixed_char='', fixed_pos=''):
    import bazi as _bazi
    bazi = _bazi.calculate_bazi(year, month, day, gender, hour)
    
    if not NAME_POOL:
        return {'bazi': bazi, 'names': []}
    
    all_chars = list(CHAR_SET)
    random.shuffle(all_chars)
    selected = set(all_chars[:random.randint(600, min(1000, len(all_chars)))])
    
    # 如有固定字，确保它被选中
    if fixed_char and fixed_char in CHAR_SET:
        selected.add(fixed_char)
    
    results = []
    for pair in NAME_POOL:
        if not (pair[0] in selected and pair[1] in selected):
            continue
        # 固定字过滤
        if fixed_char:
            if fixed_pos == 'middle' and pair[0] != fixed_char:
                continue
            if fixed_pos == 'last' and pair[1] != fixed_char:
                continue
            if fixed_pos == '' and fixed_char not in pair:
                continue
        r = score(pair, bazi, gender)
        if r and r['total'] >= 45:
            r['name'] = surname + pair
            results.append(r)
    results.sort(key=lambda x: -x['total'])
    
    final = []
    seen = set()
    for r in results:
        if len(final) >= count: break
        c1, c2 = r['pair'][0], r['pair'][1]
        if sum(1 for ch in r['pair'] if ch in seen) > 1: continue
        seen.add(c1); seen.add(c2)
        final.append(r)
    return {'bazi': bazi, 'names': final}
