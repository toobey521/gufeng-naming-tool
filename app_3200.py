# -*- coding: utf-8 -*-
"""古风取名 v3.2 — 3200字库服务器"""
import os, sys, threading, time
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from flask import Flask, render_template, jsonify, request

__VERSION__ = 'v3.2-3200'

from gen_3200 import generate, NAME_POOL, GEN_VERSION
from char_db_3200 import CHAR_SET, get_char_info, STATS as CDB_STATS

app = Flask(__name__)

@app.after_request
def no_cache(resp):
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

_LIT_CACHE = None
def get_lit():
    global _LIT_CACHE
    if _LIT_CACHE is None:
        try:
            p = os.path.join(BASE, 'literature_db.py')
            import importlib.util
            s = importlib.util.spec_from_file_location('ldbmod3', p)
            m = importlib.util.module_from_spec(s)
            s.loader.exec_module(m)
            _LIT_CACHE = m.LITERATURE_DB
        except:
            _LIT_CACHE = []
    return _LIT_CACHE

def find_poem(title):
    for e in get_lit():
        if e['title'] == title: return e
    for e in get_lit():
        if title in e['title']: return e
    return None

@app.route('/')
def index():
    try:
        path = os.path.join(BASE, 'templates', 'index.html')
        if not os.path.exists(path):
            return f'DEBUG: base={BASE}, meipass={getattr(sys,"_MEIPASS","none")}, tpl_exists=False'
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        import traceback
        return f'Error: {str(e)}\n{traceback.format_exc()}'

@app.route('/debug')
def debug_info():
    return jsonify({
        'version': __VERSION__,
        'gen_version': GEN_VERSION,
        'dims': '五行命理0-35 + 诗文出处0-20 + 音律读音0-20 + 字义内涵0-20 + 字形书写0-15',
        'char_db_size': CDB_STATS['total_entries'],
        'char_set_size': CDB_STATS['unique'],
        'char_stats': CDB_STATS,
        'name_pool_size': len(NAME_POOL),
    })

@app.route('/poem')
def poem_api():
    t = request.args.get('title','').strip()
    if not t: return jsonify({'found':False})
    e = find_poem(t)
    if e: return jsonify({'found':True,'title':e['title'],'source':e['source'],'dynasty':e['dynasty'],'content':e['content']})
    return jsonify({'found':False})

@app.route('/generate', methods=['POST'])
def api_generate():
    try:
        d = request.get_json(force=True)
        surname = d.get('surname','').strip()
        year = int(d.get('year',2024)); month = int(d.get('month',1)); day = int(d.get('day',1))
        gender = d.get('gender','male'); hour = int(d.get('hour',12)) if d.get('hour') else 12
        count = int(d.get('count',20))
        if not surname: return jsonify({'success':False,'error':'请填写姓氏'})
        
        result = generate(surname, year, month, day, gender, hour, count*2)
        b = result['bazi']
        names = []
        seen = set()
        
        wx_symbols = {'金':'⚔️','木':'🌲','水':'💧','火':'🔥','土':'🏔️'}
        tone_names = {1:'阴平',2:'阳平',3:'上声',4:'去声'}
        
        for n in result['names']:
            nm = n['name']
            if nm in seen: continue
            seen.add(nm)
            
            src = n.get('sources',[])
            pair = list(n['pair'])
            
            lit = []
            for s in src[:3]:
                e = find_poem(s.get('t',''))
                lit.append({
                    'title': s.get('t',''),
                    'source': s.get('s',''),
                    'snippet': s.get('l',''),
                    'full_text': e['content'] if e else s.get('l',''),
                    'explain': '名字取自「'+s.get('t','')+'」('+s.get('s','')+')'
                })
            
            analysis = []
            
            ml = []
            for ch in pair:
                info = get_char_info(ch)
                if info:
                    tag = info.get('tags','')
                    meaning = info.get('meaning','')
                    display = f'「{ch}」五行属{info["wuxing"]}'
                    if tag and tag != '通用':
                        display += f'，{tag}'
                    if meaning:
                        display += f'，{meaning}'
                    ml.append(display)
                    ml.append(f'   笔画{info["strokes"]}画')
            if ml: analysis.append({'title':'📖 字义与寓意分析','content':'\\n'.join(ml)})
            
            ti = []
            all_t = []
            for ch in pair:
                info = get_char_info(ch)
                if info:
                    py = info.get('pinyin','')
                    if py: py = py.rstrip('1234567890')
                    tn = tone_names.get(info['tone'],'')
                    ti.append(f'{ch}({py} {tn})')
                    all_t.append(info['tone'])
            tc = '声调有起伏' if len(set(all_t))>=2 else '声调较平'
            analysis.append({'title':'🔊 音律分析','content':f'   声调：{" ".join(ti)}，{tc}'})
            
            si = []
            ts = 0
            for ch in pair:
                info = get_char_info(ch)
                if info: si.append(f'{ch}({info["strokes"]}画)'); ts += info['strokes']
            sc = '笔画适中' if ts<=22 else '笔画稍多'
            analysis.append({'title':'✍️ 字形分析','content':f'   笔画：{" ".join(si)} 共{ts}画，{sc}'})
            
            if b:
                wx_str = ' '.join(f'{wx_symbols.get(k,"")}{k}{v}' for k,v in sorted(b['wuxing']['counts'].items(), key=lambda x:-x[1]))
                rec = b['recommend_element']
                pw = []
                for ch in pair:
                    info = get_char_info(ch)
                    if info: pw.append(f'{ch}({info["wuxing"]})')
                wl = [
                    f'   八字：{b["bazi_str"]}  日主：{b["ri_zhu"]}({b["ri_zhu_wx"]})',
                    f'   五行分布：{wx_str}',
                    f'   推荐用神：{wx_symbols.get(rec,"")}{rec}',
                    f'   名字用字五行：{" ".join(pw)}'
                ]
                if n.get('bazi_score',0) >= 25:
                    wl.append(f'   ✅ 名字含{rec}五行元素，与八字喜用神相合')
                analysis.append({'title':'☯️ 五行八字分析','content':'\\n'.join(wl)})
            
            dims = [
                ('☯️五行命理', n['bazi_score'], 35),
                ('📜诗文出处', n['lit_score'], 20),
                ('🔊音律读音', n['tone_score'], 20),
                ('📖字义内涵', n['meaning_score'], 20),
                ('✍️字形书写', n['stroke_score'], 15),
            ]
            bars = []
            for dn, ds, dm in dims:
                bl = int(ds/dm*10) if dm>0 else 0
                bars.append(f'{dn}：{"█"*bl}{"░"*(10-bl)} {ds}/{dm}')
            lvl = '🌟 绝佳好名' if n['total']>=85 else '👍 上乘之名' if n['total']>=75 else '✅ 不错'
            analysis.append({'title':f'📊 综合评分 {n["total"]} {lvl}','content':'\\n'.join(bars)})
            
            names.append({
                'name': nm, 'total_score': n['total'],
                'bazi_score': n['bazi_score'],
                'lit_score': n['lit_score'],
                'tone_score': n['tone_score'],
                'meaning_score': n['meaning_score'],
                'stroke_score': n['stroke_score'],
                'given_chars': pair,
                'lit_analysis': lit, 'phrase_analysis': lit,
                'analysis': analysis,
                'char_info': [get_char_info(ch) for ch in pair if get_char_info(ch)]})
            if len(names) >= count: break
        
        return jsonify({
            'success': True, 'lit_db_size': 316933, 'names': names,
            'debug_dims': {'bazi_max':35,'lit_max':20,'tone_max':20,'meaning_max':20,'stroke_max':15},
            'version': __VERSION__,
            'bazi': {
                'birth_date': b['birth_date'], 'gender': b['gender'],
                'bazi_str': b['bazi_str'], 'zodiac': b['zodiac'],
                'ri_zhu': b['ri_zhu'], 'ri_zhu_wx': b['ri_zhu_wx'],
                'wuxing_counts': b['wuxing']['counts'],
                'recommend_element': b['recommend_element'],
                'recommend_text': b['wuxing']['summary']['recommend_text'],
                'pillars': [{'name':p[0],'text':p[1]+p[2]} for p in b['pillars']],
            }
        })
    except Exception as e:
        import traceback
        print(f'GEN ERR: {e}\n{traceback.format_exc()}')
        return jsonify({'success':False,'error':str(e)+'\n'+traceback.format_exc()})

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5592,debug=False)
