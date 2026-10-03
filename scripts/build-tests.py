#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
catalog=json.loads((ROOT/'catalog.json').read_text())
FIXTURE=r'''import { mock } from 'claude-code/testing'
export function world(on) {
  const clock=mock.clock(on,{now:Date.parse('2026-10-03T09:00:00Z')})
  const saved=new Map<string,any>()
  const state={registered:[] as any[],opened:[] as any[],argv:[] as any[],copies:[] as string[],drafts:[] as string[],toasts:[] as string[],reads:[] as string[],size:100,isLink:false,sizeError:false,processError:false,failTool:false,downstream:0,contextMissing:false,emptyAgents:false,emptyLimits:false,sourceOverride:null as string|null}
  const sources:Record<string,string>={
    'package.json':'{"name":"demo-app","version":"1.2.0","scripts":{"test":"vitest run","build":"vite build"},"dependencies":{"react":"^19.0.0"},"devDependencies":{"vitest":"^3.0.0"}}',
    'README.md':'# Demo application\n\n## Setup\n```md\n# not a heading\n```\n### Tests\n',
    'data.csv':'name,city\n"Ada, A.",London\nGrace,"New\nYork"\n',
    'app.log':'INFO server ready\nWARN retrying\nERROR connection refused\nINFO recovered\n',
    '.env.example':'API_URL=https://example.com\nAPI_KEY=\n# docs\n',
    'before.txt':'hello\nold\n', 'after.txt':'hello\nnew\n',
    'animation.txt':'[o] frame one\f[-] frame two'
  }
  on('store.keys',()=>({value:[...saved.keys()]}))
  on('store.get',($,e)=>({value:saved.get(e.key)}))
  on('store.set',($,e)=>{saved.set(e.key,e.value);return {value:undefined}})
  on('store.delete',($,e)=>{saved.delete(e.key);return {value:undefined}})
  on('session.start',($,e)=>({cwd:e.cwd}))
  on('session.cwd',()=>({value:'/work'}))
  on('session.usage',()=>({value:{context:state.contextMissing?{window:200000}:{tokens:84000,window:200000,percent:42},rateLimits:state.emptyLimits?[]:[{kind:'five_hour',percentUsed:37,resetsAt:'2026-10-03T12:00:00Z'},{kind:'seven_day',percentUsed:61,resetsAt:'2026-10-09T09:00:00Z'}],cost:{usd:1.2}}}))
  on('agent.list',()=>({value:state.emptyAgents?[]:[{id:'a-1',description:'Review accessibility',type:'Explore',status:'running'}]}))
  on('command.register',($,e)=>{state.registered.push(e);return {value:undefined}})
  on('ui.open',($,e)=>{state.opened.push(e);return {value:{isPlaced:true}}})
  on('ui.copy',($,e)=>{state.copies.push(e.text);return {value:{isCopied:true}}})
  on('prompt.fill',($,e)=>{state.drafts.push(e.text);return {isFilled:true}})
  on('ui.toast',($,e)=>{state.toasts.push(e.text);return {value:undefined}})
  on('ui.render',()=>({type:'Text',props:{},children:['Other pane untouched']}))
  on('fs.stat',()=>state.sizeError?{deny:'File does not exist'}:{value:{kind:'file',size:state.size,mtimeMs:0,isLink:state.isLink}})
  on('fs.read',($,e)=>{state.reads.push(e.path);return {value:state.sourceOverride ?? sources[e.path.split('/').pop()] ?? 'sample text'}})
  on('fs.list',()=>({value:[{name:'src',kind:'dir',size:0,isLink:false},{name:'package.json',kind:'file',size:220,isLink:false},{name:'linked',kind:'dir',size:0,isLink:true}]}))
  on('process.run',($,e)=>{
    state.argv.push(e.argv)
    if(state.processError)return {deny:'Git not available'}
    let stdout='sample Git inspection\n'
    if(e.argv.includes('status'))stdout='## feature/mod-gallery\n M src/index.ts\n?? docs/notes.md\n'
    if(e.argv.includes('branch'))stdout='* feature/mod-gallery  123abcd [origin/feature/mod-gallery] Add gallery\n  main                 456def0 [origin/main] Release\n'
    if(e.argv.includes('--cached'))stdout=e.argv.includes('--stat')?' src/index.ts | 2 +-\n 1 file changed\n':'@@ -1 +1 @@\n-old label\n+new label\n'
    if(e.argv.includes('log'))stdout='123abcd  2026-10-03  Ada\n    Add keyboard controls\n456def0  2026-10-02  Grace\n    Fix empty states\n'
    if(e.argv.includes('stash'))stdout=e.argv.includes('list')?'stash@{0}  WIP on feature/search\nstash@{1}  WIP on main\n':' src/search.ts | 8 ++++----\n'
    if(e.argv.includes('worktree'))stdout='worktree /work\nHEAD 123abcd\nbranch refs/heads/main\n\nworktree /work-review\nHEAD 456def0\nbranch refs/heads/review\n'
    if(e.argv.includes('--diff-filter=U'))stdout='src/config.ts\n'
    if(e.argv.includes('grep'))stdout=e.argv.includes('TODO|FIXME|HACK')?'src/index.ts:12:// TODO improve empty state\nsrc/api.ts:44:// FIXME retry timeout\n':'src/config.ts:4:<<<<<<< HEAD\nsrc/config.ts:8:>>>>>>> review\n'
    if(e.argv.includes('blame'))stdout='123abcd (Ada 2026-10-03 1) # Demo application\n456def0 (Grace 2026-10-02 2) ## Setup\n'
    if(e.argv.includes('check-ignore'))stdout='.gitignore:3:dist/\tdist/bundle.js\n'
    return {value:{exitCode:0,stdout,stderr:''}}
  })
  on('tool.call',()=>{state.downstream++;return state.failTool?{result:'Fixture failure',isError:true}:{result:'ok'}})
  on('turn.complete',()=>({text:''}))
  on('turn.step',async function*($,e){
    yield {kind:'text',index:0,text:'ok'}
    return {turnId:e.turnId,index:e.index,answer:'ok',toolUses:[],stopReason:'end_turn',usage:{input_tokens:20,output_tokens:10,cache_read_input_tokens:1000,cache_creation_input_tokens:80}}
  })
  return {clock,saved,state}
}
export function site(plugin, surface:'terminal'|'desktop'='terminal', width=60) {
  return {plugin,component:'Pane' as const,requestId:plugin,surface,viewport:{columns:width+40,rows:30},props:{title:plugin,isFocused:true,bodyColumns:width,placement:'inline' as const,scroll:{offset:0,bodyRows:20},view:{}}}
}
'''

def custom(id,code):customs[id]=code
customs={}
custom('context-meter',"""
expect(await ui.find({type:'Text',text:'84,000 / 200,000 tokens'})).toBeDefined()
state.contextMissing=true
await ui.press({key:'refresh'})
expect(await ui.find({type:'Text',text:/not reported/i})).toBeDefined()
""")
custom('quota-watch',"""
expect(await ui.find({type:'Text',text:/five_hour/})).toBeDefined()
state.emptyLimits=true
await ui.press({key:'refresh'})
expect(await ui.find({type:'Text',text:'No plan limits reported for this account.'})).toBeDefined()
""")
custom('cache-inspector',"""
const stream=$.turn.step({turnId:'turn',index:0,model:'claude-test',messageCount:1})
let step=await stream.next();while(!step.done)step=await stream.next()
expect(await ui.find({type:'Text',text:/Read 1000 · wrote 80 · uncached 20/})).toBeDefined()
""")
custom('tool-timing',"""
await $.tool.call({tool:'Read',file_path:'README.md'})
state.failTool=true
await $.tool.call({tool:'Read',file_path:'missing.md'})
expect(await ui.find({type:'Text',text:/Read\\s+2\\s+0\\s+1/})).toBeDefined()
""")
custom('error-inbox',"""
state.failTool=true
await $.tool.call({tool:'Read',file_path:'missing.md'})
expect(await ui.find({type:'Text',text:'1. Read · Fixture failure'})).toBeDefined()
await ui.press({key:'clear'})
expect(await ui.find({type:'Text',text:'0 recent failures'})).toBeDefined()
""")
custom('edit-heatmap',"""
await $.tool.call({tool:'Write',file_path:'/work/src/index.ts',content:'hello'})
state.failTool=true
await $.tool.call({tool:'Write',file_path:'/work/src/failed.ts',content:'hello'})
expect(await ui.find({type:'Text',text:/1  \\/work\\/src\\/index.ts/})).toBeDefined()
expect(await ui.find({type:'Text',text:/failed.ts/})).toBeUndefined()
""")
custom('turn-timeline',"""
await $.turn.complete({turnId:'t',answer:'done',durationMs:2300,isAborted:true,usage:null})
expect(await ui.find({type:'Text',text:/2.3s · 0 output tokens · interrupted/})).toBeDefined()
""")
custom('agent-board',"""
expect(await ui.find({type:'Code'})).toBeDefined()
state.emptyAgents=true
await ui.press({key:'refresh'})
expect(await ui.find({type:'Text',text:'No subagents currently reported.'})).toBeDefined()
""")
for id in ['branch-board','staged-review','commit-browser','stash-browser','worktree-map','conflict-radar','blame-view','ignore-check','todo-finder']:
    custom(id,"""
expect(state.argv.length > 0).toBe(true)
for(const argv of state.argv) {
  expect(argv.slice(0,2)).toEqual(['git','--no-pager'])
  expect(['status','branch','diff','log','stash','worktree','grep','blame','check-ignore'].includes(argv[2])).toBe(true)
}
state.processError=true
await ui.press({key:'refresh'})
expect((await ui.find({type:'Code'}))?.props.source).toContain('Git not available')
""")
customs['blame-view']+="""
state.processError=false
await ui.input({key:'target',text:'file; touch /tmp/unsafe'})
expect(state.argv[state.argv.length-1].slice(-2)).toEqual(['--','file; touch /tmp/unsafe'])
await ui.input({key:'target',text:'--help'})
expect((await ui.find({type:'Code'}))?.props.source).toContain('leading flags')
"""
customs['stash-browser']+="""
state.processError=false
const before=state.argv.length
await ui.input({key:'target',text:'--help'})
expect(state.argv.length).toBe(before)
expect((await ui.find({type:'Code'}))?.props.source).toContain('Use a stash reference')
"""
custom('file-tree',"""
expect(await ui.find({key:'dir-0'})).toBeDefined()
expect(await ui.find({key:'dir-2'})).toBeUndefined()
await ui.press({key:'dir-0'})
expect((await ui.find({key:'target'}))?.props.value).toBe('./src')
""")
file_checks={'package-scripts':'vitest run','dependency-table':'react','markdown-map':'Setup','json-browser':'demo-app','csv-table':'2 data rows','log-viewer':'connection refused','env-example':'API_KEY · value needed'}
for id,expected in file_checks.items():
    custom(id,f"""
expect((await ui.find({{type:'Code'}}))?.props.source).toContain({json.dumps(expected)})
state.size=999999
const before=state.reads.length
await ui.press({{key:'refresh'}})
expect(state.reads.length).toBe(before)
expect((await ui.find({{type:'Code'}}))?.props.source).toContain('256 KiB')
state.size=100;state.sizeError=true
await ui.press({{key:'refresh'}})
expect((await ui.find({{type:'Code'}}))?.props.source).toContain('File does not exist')
""")
customs['markdown-map']+="""
state.sizeError=false
await ui.press({key:'refresh'})
expect((await ui.find({type:'Code'}))?.props.source).not.toContain('not a heading')
"""
customs['log-viewer']+="""
state.sizeError=false
await ui.input({key:'filter',text:'ERROR'})
expect((await ui.find({type:'Code'}))?.props.source).not.toContain('INFO recovered')
"""
customs['env-example']+="""
state.sizeError=false
const readCount=state.reads.length
await ui.input({key:'target',text:'.env'})
expect(state.reads.length).toBe(readCount)
expect((await ui.find({type:'Code'}))?.props.source).toContain('real env files are refused')
state.isLink=true
await ui.input({key:'target',text:'.env.example'})
expect(state.reads.length).toBe(readCount)
expect((await ui.find({type:'Code'}))?.props.source).toContain('Symlink')
"""
custom('file-compare',"""
expect((await ui.find({type:'Code'}))?.props.source).toContain('1 differing line positions')
await ui.input({key:'right',text:'before.txt'})
expect((await ui.find({type:'Code'}))?.props.source).toBe('Files are identical.')
state.size=999999
await ui.press({key:'refresh'})
expect((await ui.find({type:'Code'}))?.props.source).toContain('64 KiB')
""")
for m in catalog:
 if m['category']=='Workspace':
    value=m['sample']
    code=f"""
await ui.input({{key:'entry',text:{json.dumps(value)}}})
expect(saved.size).toBe(1)
expect([...saved.keys()][0]).toContain('workspace:%2Fwork:item:')
await $.command.run({{command:{json.dumps(m['id'])},args:''}})
expect(saved.size).toBe(1)
"""
    if m['id'] in ['task-board','release-checklist']:
        code+="await ui.press({key:'toggle-0'});expect([...saved.values()][0].done).toBe(true)\n"
    if m['id']=='snippet-shelf':code+=f"await ui.press({{key:'copy-0'}});expect(state.copies).toEqual([{json.dumps(value)}])\n"
    if m['id']=='prompt-shelf':code+=f"await ui.press({{key:'draft-0'}});expect(state.drafts).toEqual([{json.dumps(value)}])\n"
    if m['id']=='handoff-notes':code+="await ui.press({key:'copy-all'});expect(state.copies[0]).toContain('Done: API parser')\n"
    if m['id']=='link-shelf':code+="""
expect((await ui.find({type:'Link'}))?.props.href).toBe('https://code.claude.com/docs/en/plugins/mods/overview')
await ui.input({key:'entry',text:'Bad | javascript:alert(1)'})
expect(saved.size).toBe(1)
"""
    code+="await ui.press({key:'delete-0'});expect(saved.size).toBe(0)\n"
    custom(m['id'],code)
utils={
 'regex-lab':("2 matches",'pattern','(', 'Invalid input:'),
 'json-format':('"count": 50','source','{bad','Invalid input:'),
 'url-lab':('hello world','source','not a URL','Invalid input:'),
 'base64-lab':('SGVsbG8sIG1vZHMh','mode','unknown','Mode must'),
 'time-lab':('1791018000','source','bad date','Invalid input:'),
 'hash-lab':('2cf24dba5fb0a30e26e83b2ac5b9e29e','algorithm','MD5','Use SHA-256'),
 'color-lab':('Contrast:','foreground','red','six-digit'),
 'uuid-lab':('-', 'count','0','integer from 1 to 20'),
 'text-counter':('"words": 6','source','x'*12001,'Input exceeds'),
}
for id,(expected,key,bad,message) in utils.items():
 custom(id,f"""
expect((await ui.find({{type:'Code'}}))?.props.source).toContain({json.dumps(expected)})
await ui.press({{key:'copy'}})
expect(state.copies.length).toBe(1)
await ui.input({{key:{json.dumps(key)},text:{json.dumps(bad)}}})
expect((await ui.find({{type:'Code'}}))?.props.source).toContain({json.dumps(message)})
""")
customs['base64-lab']+="""
await ui.input({key:'mode',text:'decode'})
await ui.input({key:'source',text:'SGVsbG8sIG1vZHMh'})
expect((await ui.find({type:'Code'}))?.props.source).toBe('Hello, mods!')
await ui.input({key:'source',text:'%%%bad'})
expect((await ui.find({type:'Code'}))?.props.source).toContain('Invalid input:')
"""
customs['regex-lab']+="""
await ui.input({key:'pattern',text:'(a+)+$'})
expect((await ui.find({type:'Code'}))?.props.source).toContain('Invalid input:')
"""
custom('ascii-flipbook',"""
expect(await ui.find({type:'Text',text:'Frame 1 / 2'})).toBeDefined()
await ui.press({key:'next'})
expect(await ui.find({type:'Text',text:'Frame 2 / 2'})).toBeDefined()
await ui.press({key:'play'});await clock.advance(500)
expect(await ui.find({type:'Text',text:'Frame 1 / 2'})).toBeDefined()
await ui.input({key:'target',text:'animation.txt'})
expect((await ui.find({type:'Code'}))?.props.source).toBe('[o] frame one')
""")
custom('focus-clock',"""
await ui.press({key:'start'});await clock.advance(1000)
expect(await ui.find({type:'Text',text:'24:59'})).toBeDefined()
await ui.press({key:'start'});await clock.advance(1000)
expect(await ui.find({type:'Text',text:'24:59'})).toBeDefined()
await ui.press({key:'reset'})
expect(await ui.find({type:'Text',text:'25:00'})).toBeDefined()
""")
custom('stopwatch',"""
await ui.press({key:'start'});await clock.advance(2000)
await ui.press({key:'lap'})
expect(await ui.find({type:'Text',text:'Lap 1 · 2.0s'})).toBeDefined()
await ui.press({key:'start'});await clock.advance(1000)
expect(await ui.find({type:'Text',text:'2.0 seconds'})).toBeDefined()
await ui.press({key:'reset'})
expect(await ui.find({type:'Text',text:'0.0 seconds'})).toBeDefined()
""")
custom('test-ledger',"""
await $.tool.call({tool:'Bash',command:'npm test'})
expect(await ui.find({type:'Text',text:'1. tool completed\\nnpm test'})).toBeDefined()
state.failTool=true
await $.tool.call({tool:'Bash',command:'npm run build'})
expect(await ui.find({type:'Text',text:'2. tool error\\nnpm run build'})).toBeDefined()
""")
custom('command-history',"""
await $.tool.call({tool:'Bash',command:'git status --short'})
await ui.press({key:'copy-0'})
expect(state.copies).toEqual(['git status --short'])
""")
custom('scope-watch',"""
await $.tool.call({tool:'Write',file_path:'/work/src/index.ts',content:'hello'})
expect(state.toasts).toEqual([])
await $.tool.call({tool:'Write',file_path:'/work/docs/readme.md',content:'hello'})
expect(state.toasts.length).toBe(1)
expect(await ui.find({type:'Text',text:'docs/readme.md'})).toBeDefined()
""")
custom('read-only-mode',"""
await $.tool.call({tool:'Bash',command:'pwd'})
const before=state.downstream
await ui.press({key:'toggle'})
const denied=await $.tool.call({tool:'Write',file_path:'example.txt',content:'data'})
expect(denied.deny).toContain('Read-only Mode is enabled')
expect(state.downstream).toBe(before)
const allowed=await $.tool.call({tool:'Read',file_path:'README.md'})
expect(allowed.result).toBe('ok')
await ui.press({key:'toggle'})
expect((await $.tool.call({tool:'Bash',command:'pwd'})).result).toBe('ok')
""")
for m in catalog:
 d=ROOT/'mods'/m['id']/'tests'
 (d/'fixtures.ts').write_text(FIXTURE)
 id=json.dumps(m['id']);title=json.dumps(m['title'])
 content=f'''import {{ expect, test }} from 'claude-code/testing'
import {{ world, site }} from './fixtures'
const ID={id}

test('registers an immediate command and opens only its pane', async ($, on) => {{
 const {{state}}=world(on)
 await $.session.start({{surface:'terminal',isInteractive:true,cwd:'/work'}})
 expect(state.registered.length).toBe(1)
 expect(state.registered[0].name).toBe(ID)
 expect(state.registered[0].immediate).toBe(true)
 expect(state.opened).toEqual([])
 await $.command.run({{command:ID,args:''}})
 expect(state.opened[0]).toMatchObject({{id:ID,title:{title},focus:true,closeOnEscape:true}})
}})

test('leaves another plugin pane untouched', async ($, on) => {{
 world(on)
 const ui=await $.ui.mount({{...site(ID),requestId:'someone-else'}})
 expect(await ui.find({{type:'Text',text:'Other pane untouched'}})).toBeDefined()
 await ui.unmount()
}})

for(const surface of ['terminal','desktop'] as const) {{
 test('valid controls and behavior on '+surface, async ($,on)=>{{
  const {{state,saved,clock}}=world(on)
  await $.session.start({{surface,isInteractive:true,cwd:'/work'}})
  await $.command.run({{command:ID,args:''}})
  const ui=await $.ui.mount(site(ID,surface,surface==='terminal'?34:70))
  expect(await ui.find({{type:'Text',text:{title}}})).toBeDefined()
  expect(await ui.find({{type:'Text',text:'Unable to inspect this data.'}})).toBeUndefined()
  {customs[m['id']]}
  await ui.unmount()
 }})
}}
'''
 # Non-board utility output exact flags held test enough.
 (d/'register.test.ts').write_text(content)
print('Built native tests for',len(catalog),'mods')
# Capture native-kit render trees. The browser preview paints these snapshots,
# never handwritten screenshots or a reimplementation of the mod's calculations.
preview_actions={
 'cache-inspector':"const stream=$.turn.step({turnId:'preview',index:0,model:'claude-test',messageCount:1});let p=await stream.next();while(!p.done)p=await stream.next()",
 'tool-timing':"for(let i=0;i<4;i++)await $.tool.call({tool:'Read',file_path:'README.md'});await $.tool.call({tool:'Bash',command:'git status'})",
 'error-inbox':"state.failTool=true;await $.tool.call({tool:'Read',file_path:'missing.md'});await $.tool.call({tool:'Bash',command:'npm test'})",
 'edit-heatmap':"for(let i=0;i<5;i++)await $.tool.call({tool:'Write',file_path:'src/index.ts',content:'fixture'});await $.tool.call({tool:'Write',file_path:'src/index.test.ts',content:'fixture'})",
 'turn-timeline':"await $.turn.complete({turnId:'one',answer:'',durationMs:12400,isAborted:false,usage:null});await $.turn.complete({turnId:'two',answer:'',durationMs:7200,isAborted:true,usage:null})",
 'focus-clock':"await ui.press({key:'start'});await clock.advance(125000)",
 'stopwatch':"await ui.press({key:'start'});await clock.advance(12400);await ui.press({key:'lap'});await clock.advance(4700);await ui.press({key:'start'})",
 'test-ledger':"await $.tool.call({tool:'Bash',command:'npm test'});state.failTool=true;await $.tool.call({tool:'Bash',command:'npm run build'})",
 'command-history':"await $.tool.call({tool:'Bash',command:'git status --short'});await $.tool.call({tool:'Bash',command:'npm test'});await $.tool.call({tool:'Bash',command:'rg -n TODO src/'})",
 'scope-watch':"await $.tool.call({tool:'Write',file_path:'/work/docs/README.md',content:'fixture'});await $.tool.call({tool:'Write',file_path:'/work/package.json',content:'fixture'})",
 'read-only-mode':"await ui.press({key:'toggle'});await $.tool.call({tool:'Bash',command:'npm run build'})",
}
for m in catalog:
 id=json.dumps(m['id']);title=json.dumps(m['title']);action=preview_actions.get(m['id'],'')
 if m['category']=='Workspace':
  action='await ui.input({key:"entry",text:'+json.dumps(m['sample'])+'})'
  if m['id'] in ['task-board','release-checklist']:action+=';await ui.input({key:"entry",text:"Review the keyboard controls"});await ui.press({key:"toggle-0"})'
 p=ROOT/'mods'/m['id']/'tests/register.test.ts'
 with p.open('a') as f:f.write(f'''

test('capture native render tree for fixture preview', async($,on)=>{{
 const {{state,saved,clock}}=world(on)
 await $.session.start({{surface:'terminal',isInteractive:true,cwd:'/work'}})
 await $.command.run({{command:ID,args:''}})
 const ui=await $.ui.mount(site(ID,'terminal',78))
 {action}
 const tree=await ui.find({{type:'Box'}})
 expect(tree).toBeDefined()
 console.log('MOD_PREVIEW:'+JSON.stringify({{id:ID,tree}}))
 await ui.unmount()
}})
''')

# Keep generated source clean for git diff --check.
for m in catalog:
 p=ROOT/'mods'/m['id']/'tests/register.test.ts'
 p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')
