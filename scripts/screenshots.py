#!/usr/bin/env python3
"""Capture actual local preview pages with Playwright Chromium."""
import argparse,json,os
from pathlib import Path
from provenance import file_digest
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser()
parser.add_argument('--browser',default=os.environ.get('MODS_BROWSER','/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'))
args=parser.parse_args()
catalog=json.loads((ROOT/'catalog.json').read_text())
manifest={'kind':'browser-preview-of-native-kit-tree','claudeCode':'2.1.288','images':[]}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=args.browser if Path(args.browser).is_file() else None,headless=True)
 page=browser.new_page(viewport={'width':1000,'height':1200},device_scale_factor=1)
 for m in catalog:
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto((ROOT/'assets/previews'/f"{m['id']}.html").as_uri())
  page.locator('.pane > .box').wait_for()
  if errors:raise RuntimeError(errors)
  page.locator('#capture').screenshot(path=str(ROOT/'assets/screenshots'/f"{m['id']}.png"))
  snapshot=json.loads((ROOT/'assets/previews'/f"{m['id']}.json").read_text())
  manifest['images'].append({'id':m['id'],'sourceSha256':snapshot['sourceSha256'],'snapshotSha256':file_digest(ROOT/'assets/previews'/f"{m['id']}.json"),'pngSha256':file_digest(ROOT/'assets/screenshots'/f"{m['id']}.png")})
  print('Captured '+m['id'],flush=True)
 # Verify the gallery really searches and filters, with every image loaded.
 page.goto((ROOT/'gallery.html').as_uri())
 assert page.locator('.card').count()==len(catalog)
 page.locator('#search').fill('checksum')
 assert page.locator('.card:visible').count()==1
 page.locator('#search').fill('')
 page.locator('#category').select_option('Git')
 assert page.locator('.card:visible').count()==8
 page.locator('#category').select_option('Desktop')
 assert page.locator('.card:visible').count()==20
 page.locator('#category').select_option('')
 page.set_viewport_size({'width':390,'height':844})
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 assert page.locator('.card:visible').count()==len(catalog)
 page.screenshot(path=str(ROOT/'assets/screenshots/gallery-mobile.png'))
 browser.close()
(ROOT/'assets/screenshots/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(str(len(catalog))+' screenshots and gallery browser checks passed')
