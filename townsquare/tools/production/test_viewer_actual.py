"""Actual headless-browser test of the local interactive model. Records console/errors and pixel proof."""
import asyncio,json,hashlib
from pathlib import Path
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[2]
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(env={**__import__('os').environ,'LD_LIBRARY_PATH':'/home/user/.cache/browser-deps/usr/lib/x86_64-linux-gnu'},args=['--use-gl=swiftshader','--enable-webgl','--no-sandbox'])
  page=await b.new_page(viewport={'width':1440,'height':900})
  logs=[];page.on('console',lambda m:logs.append([m.type,m.text]))
  await page.goto('http://127.0.0.1:8080/',wait_until='domcontentloaded')
  try:await page.wait_for_function('window.previewDiagnostics&&window.previewDiagnostics.modelLoaded',timeout=300000)
  except Exception as e:logs.append(['timeout',str(e)])
  await page.wait_for_timeout(4000)
  diag=await page.evaluate('window.previewDiagnostics')
  shot=R/'evidence/current-production/viewer-actual.png';await page.screenshot(path=str(shot))
  # Reversible cutaway + building selection must change the visible set.
  await page.select_option('#building','B01');await page.wait_for_timeout(1500);diag_b=await page.evaluate('window.previewDiagnostics');shotb=R/'evidence/current-production/viewer-B01.png';await page.screenshot(path=str(shotb))
  floors=await page.eval_on_selector_all('#floor option','els=>els.map(e=>e.value)')
  await page.select_option('#floor',floors[1]);await page.wait_for_timeout(1500);diag_f=await page.evaluate('window.previewDiagnostics');shotf=R/'evidence/current-production/viewer-B01-floor.png';await page.screenshot(path=str(shotf))
  await page.click('#reset');await page.wait_for_timeout(600);diag_r=await page.evaluate('window.previewDiagnostics')
  await b.close()
  r={'url':'http://127.0.0.1:8080/','model_loaded':diag.get('modelLoaded'),'frames':diag.get('frames'),'triangles_whole':diag.get('triangles'),'draw_calls':diag.get('calls'),'textures':diag.get('textures'),'building_selection':diag_b,'floor_cutaway':diag_f,'restored':diag_r,'console':logs[-25:],'screenshots':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [shot,shotb,shotf] if p.exists()},'scope':'Actual local headless Chromium/WebGL load and interaction. Not a visual acceptance of native render quality; software WebGL lighting differs from Blender.'}
  (R/'evidence/production/R14-viewer-actual-test.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
asyncio.run(main())
