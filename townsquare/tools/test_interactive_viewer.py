"""Optional real headless-browser integration/screenshot test; never a final Blender image review."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];out=R/'evidence/viewer';out.mkdir(exist_ok=True);errors=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1440,'height':900},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:3000/',wait_until='domcontentloaded');page.wait_for_function("document.getElementById('loading').style.display==='none'",timeout=120000);page.screenshot(path=str(out/'whole-square.png'));page.locator('canvas').screenshot(path=str(out/'whole-square-canvas.png'))
 page.select_option('#building','B01');page.select_option('#floor','B01_L01');page.wait_for_function("document.getElementById('title').textContent.includes('B01_L01')");page.screenshot(path=str(out/'supermarket-floor.png'));page.locator('canvas').screenshot(path=str(out/'supermarket-floor-canvas.png'))
 assert page.locator('#programme').inner_text().startswith('Produce');page.click('#reset');page.wait_for_function("document.getElementById('building').value==='ALL'");browser.close()
r={'scope':'Actual headless Chromium/SwiftShader browser interaction and screenshots of approximate WebGL preview, NOT final Blender view inspection. Screenshots require separate actual visual opens.','status':'BROWSER_EXECUTED_SCREENSHOT_INSPECTION_PENDING','javascript_runtime_errors':errors,'actual_actions':['Loaded actual145MB clean-import-tested GLB through local HTTP','Whole square screenshot','Selected B01 and occupied B01_L01','Asserted supermarket programme/title','Restored whole square'],'screenshots':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.png')}};(out/'browser-check.json').write_text(json.dumps(r,indent=2)+'\n');print('ACTUAL_BROWSER_MODEL_LOADED_CONTROLS_EXECUTED',json.dumps(r),flush=True);assert not errors,errors
