#!/usr/bin/env python3
"""Run the real Claude validator and test kit, fail if any check fails."""
import concurrent.futures,json,subprocess,sys,re,argparse
from provenance import source_digest
from pathlib import Path
root=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser();parser.add_argument('--capture-previews',action='store_true');args=parser.parse_args()
catalog=json.loads((root/'catalog.json').read_text())
version=subprocess.check_output(['claude','--version'],text=True).strip()
def check(m):
 reports=[];ok=True
 for command in [['claude','plugin','validate','mods/'+m['id'],'--strict'],['claude','plugin','test','mods/'+m['id']]]:
  p=subprocess.run(command,cwd=root,capture_output=True,text=True,timeout=90)
  output=p.stdout+p.stderr
  captures=[]
  def capture(match):
   data=json.loads(match.group(1))
   def normalize(value):
    if isinstance(value,dict):return {k:normalize(v) for k,v in value.items() if k not in ['press','input','select','text'] or k=='text' and value.get('type')!='Box'}
    if isinstance(value,list):return [normalize(v) for v in value]
    return value
   if args.capture_previews:
    data['sourceSha256']=source_digest(root,m['id'])
    path=root/'assets/previews';path.mkdir(parents=True,exist_ok=True)
    (path/(m['id']+'.json')).write_text(json.dumps(normalize(data),indent=2)+'\n')
   captures.append(data)
   return '[Captured native render tree for '+m['id']+']'
  output=re.sub(r'MOD_PREVIEW:(.*)',capture,output)
  if command[2]=='test' and not captures:ok=False
  reports.append({'command':' '.join(command),'exitCode':p.returncode,'output':output.replace(str(root),'.')})
  ok &= p.returncode==0
 return {'id':m['id'],'passed':ok,'checks':reports}
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for r in pool.map(check,catalog):
  results.append(r);print(('PASS' if r['passed'] else 'FAIL')+' '+r['id'],flush=True)
  if not r['passed']:
   for c in r['checks']:
    if c['exitCode']:print(c['output'],flush=True)
(root/'docs/check-results.json').write_text(json.dumps({'version':version,'mods':results},indent=2)+'\n')
print(str(sum(r['passed'] for r in results))+'/'+str(len(results))+' mods pass native validation and tests')
sys.exit(0 if all(r['passed'] for r in results) else 1)
