#!/usr/bin/env python3
"""Audit package boundaries, release artifacts, and screenshot source provenance."""
import json,re,struct,sys
from pathlib import Path
from provenance import source_digest,file_digest
ROOT=Path(__file__).resolve().parent.parent
mods=json.loads((ROOT/'catalog.json').read_text())
market=json.loads((ROOT/'.claude-plugin/marketplace.json').read_text())
manifest=json.loads((ROOT/'assets/screenshots/manifest.json').read_text())
images={m['id']:m for m in manifest['images']}
errors=[]
def require(condition,message):
 if not condition:errors.append(message)
require(len(mods)==70,'Expected 70 catalogue entries')
require(sum(m.get('surface')=='desktop' for m in mods)==20,'Expected 20 Desktop mods')
require(len({m['id'] for m in mods})==70,'Mod IDs are not unique')
require(len(list((ROOT/'mods').iterdir()))==70,'Expected exactly 70 plugin directories')
require(len(images)==70,'Expected 70 screenshot provenance entries')
require({m['name'] for m in market['plugins']}=={m['id'] for m in mods},'Marketplace/catalogue mismatch')
for m in mods:
 name=m['id'];d=ROOT/'mods'/name
 plugin=json.loads((d/'.claude-plugin/plugin.json').read_text())
 entry=next(p for p in market['plugins'] if p['name']==name)
 require(entry['version']==plugin['version'],name+': version mismatch')
 require(plugin['license']=='MIT',name+': manifest license')
 require((d/'LICENSE').read_bytes()==(ROOT/'LICENSE').read_bytes(),name+': license differs')
 require(json.loads((d/'hooks/hooks.json').read_text())['modules']==['./register.js'],name+': entry point')
 for src in (d/'hooks').glob('*.js'):
  content=src.read_text()
  require(not re.search(r'\$\.(http|model|mcp|agent\.spawn|session\.send)|\$\.fs\.write|\$\.prompt\.submit',content),name+': unexpected external capability')
  for path in re.findall(r"from ['\"]([^'\"]+)['\"]",content):
   require(path.startswith('./'),name+': non-local import '+path)
   require((src.parent/path).resolve().is_relative_to(d.resolve()),name+': import escapes plugin')
  require(not re.search(r'\b(require|setTimeout|setInterval)\s*\(',content),name+': forbidden runtime call')
 readme=(d/'README.md').read_text()
 require(f'../../assets/screenshots/{name}.png' in readme,name+': README has no screenshot')
 require('fixture preview' in readme,name+': screenshot provenance missing')
 image=ROOT/'assets/screenshots'/f'{name}.png'
 raw=image.read_bytes()
 require(raw[:8]==b'\x89PNG\r\n\x1a\n',name+': image is not PNG')
 width,height=struct.unpack('>II',raw[16:24])
 require(width>=800 and height>=300,name+': screenshot too small')
 data=json.loads((ROOT/'assets/previews'/f'{name}.json').read_text())
 require(data['sourceSha256']==source_digest(ROOT,name),name+': screenshot source is stale')
 record=images[name]
 require(record['sourceSha256']==data['sourceSha256'],name+': provenance source mismatch')
 require(record['snapshotSha256']==file_digest(ROOT/'assets/previews'/f'{name}.json'),name+': snapshot changed since screenshot')
 require(record['pngSha256']==file_digest(image),name+': screenshot changed without provenance')
 require((ROOT/'assets/previews'/f'{name}.html').is_file(),name+': HTML preview absent')
 require('Unable to inspect this data.' not in json.dumps(data),name+': error-state preview')
 require('Unable to display:' not in json.dumps(data),name+': Desktop error-state preview')
 if m.get('surface')=='desktop':
  require(data.get('surface')=='desktop',name+': must capture Desktop surface')
 require((d/'tests/register.test.ts').read_text().count('test(')>=4,name+': missing native behavioral tests')
# Check all local Markdown targets, including images and anchors.
for doc in [ROOT/'README.md',ROOT/'CONTRIBUTING.md',*ROOT.glob('docs/*.md'),*ROOT.glob('mods/*/README.md')]:
 for target in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)',doc.read_text()):
  if re.match(r'^[a-z]+:|^#',target):continue
  target=target.split('#')[0]
  require((doc.parent/target).exists(),str(doc.relative_to(ROOT))+': broken link '+target)
if errors:
 print('\n'.join(errors));sys.exit(1)
print('Audit passed: 70 standalone mods (20 Desktop), MIT licenses, local imports, live screenshot digests, and local links')
