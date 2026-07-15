# -*- coding: utf-8 -*-
import os, sys, threading, time, webbrowser
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)

from app_3200 import app

def open_browser():
    time.sleep(1.5)
    try: webbrowser.open('http://127.0.0.1:5592')
    except: pass

if __name__ == '__main__':
    print('http://127.0.0.1:5592')
    print('古风取名 v3.2 - 3200字库 + 新评分体系')
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host='127.0.0.1', port=5592, debug=False)
