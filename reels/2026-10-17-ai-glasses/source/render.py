import sys, os
from playwright.sync_api import sync_playwright
here=os.path.dirname(os.path.abspath(__file__))
mode=sys.argv[1]; out=sys.argv[2]; os.makedirs(out,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    pg=b.new_page(viewport={'width':1080,'height':1920})
    pg.on('console',lambda m:print('console:',m.text)); pg.on('pageerror',lambda e:print('ERR',e))
    pg.goto('file://'+here+'/scene.html'); pg.evaluate('document.fonts.ready')
    total=pg.evaluate('TOTAL')
    if mode=='stills':
        ts=[float(x) for x in sys.argv[3].split(',')]
    else:
        fps=30; ts=[i/fps for i in range(int(total*fps))]
    for i,t in enumerate(ts):
        pg.evaluate(f'render({t})')
        pg.screenshot(path=f'{out}/{i:04d}.jpg',type='jpeg',quality=92)
    print('total',total,'frames',len(ts))
    b.close()
