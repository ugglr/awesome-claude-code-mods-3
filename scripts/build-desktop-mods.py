#!/usr/bin/env python3
"""Generate 20 self-contained Desktop Code plugins and their native tests.

Run after build-mods.py/build-tests.py; does not edit the original 50 plugins.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODS = []

UI = r'''// Pure presentation helpers, copied into each standalone plugin.
export function clean(v, n=9000) { return String(v ?? '').replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f-\u009f]/g,'').slice(0,n) }
export function text(E,v,props={}) { return E.Text({...props,children:[clean(v)]}) }
export function code(E,v) { return E.Code({source:clean(v),language:'text'}) }
export function row(E,children) { return E.Box({flexDirection:'row',columnGap:2,flexWrap:'wrap',children}) }
export function frame(E,title,children) { return E.Box({flexDirection:'column',gap:1,children:[text(E,title,{bold:true,color:'cyan'}),...children]}) }
export function bounded(v,n=9000) { if(v.length>n)throw Error('Input exceeds '+n+' characters.');return v }
export function path(v) { v=v.trim();if(!v||v.startsWith('-')||/[\x00-\x1f]/.test(v))throw Error('Enter a path without control characters or leading flags.');return v }
export function xml(v) { return clean(v,200).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c])) }
export function num(v) { return Number.isFinite(v)?v:0 }
export function pct(v) { return Math.max(0,Math.min(100,num(v))) }
export function count(v) { return Number.isFinite(v)?v.toLocaleString('en-US'):'not reported' }
export function waitUntil(v,now) { const n=Date.parse(v);if(!Number.isFinite(n))return 'reset not reported';const m=Math.max(0,Math.ceil((n-now)/60000));return m?Math.floor(m/60)+'h '+m%60+'m':'reset due; awaiting report' }
export function chart(E,values,labels,alt,scale) {
 const data=values.slice(-12), names=labels.slice(-12),max=scale||Math.max(1,...data.map(num)),h=40+data.length*30
 const rows=data.map((v,i)=>'<text x="12" y="'+(28+i*30)+'" fill="#d8dfeb" font-size="12">'+xml(names[i])+'</text><rect x="180" y="'+(12+i*30)+'" width="'+(Math.max(0,num(v))/max*310)+'" height="20" rx="5" fill="#8b9cf7"/><text x="505" y="'+(28+i*30)+'" fill="#d8dfeb" font-size="12">'+xml(Math.round(num(v)*10)/10)+'</text>').join('')
 return E.Svg({source:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 580 '+h+'" width="580" height="'+h+'"><rect width="580" height="'+h+'" rx="12" fill="#182234"/>'+rows+'</svg>',alt:clean(alt),height:h})
}
export function gauge(E,value,label) { return chart(E,[pct(value)],[label],label+': '+count(value)+'%',100) }
export function usageChips(u,records,now) {
 const totals=records.reduce((a,r)=>({input:a.input+num(r.input_tokens),output:a.output+num(r.output_tokens),cache:a.cache+num(r.cache_read_input_tokens)}),{input:0,output:0,cache:0})
 return [...u.rateLimits.slice(0,4).map(r=>r.kind+' '+count(r.percentUsed)+'% · '+waitUntil(r.resetsAt,now)),
  'Context '+count(u.context?.percent)+'%', 'Input '+count(totals.input),'Output '+count(totals.output),'Cache read '+count(totals.cache),'USD '+(Number.isFinite(u.cost?.usd)?u.cost.usd.toFixed(2):'not reported')]
}
export function strip(E,chips,columns) {
 const w=Math.min(1000,Math.max(240,(columns||80)*8)),colors=['#bbdbc6','#d4c8ed','#cbd5ed','#edcfbd','#bddec9','#ccd6f1','#e7d6a7']
 let x=4,y=4
 const pills=chips.map((s,i)=>{const cw=Math.min(w-8,s.length*6.5+24);if(x+cw>w){x=4;y+=40}const p='<rect x="'+x+'" y="'+y+'" width="'+cw+'" height="32" rx="16" fill="'+colors[i%colors.length]+'"/><text x="'+(x+12)+'" y="'+(y+21)+'" font-family="system-ui" font-size="12" fill="#202523">'+xml(s)+'</text>';x+=cw+8;return p}).join('')
 const h=y+36
 return E.Svg({source:'<svg xmlns="http://www.w3.org/2000/svg" width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'">'+pills+'</svg>',alt:chips.join('; '),height:h})
}
export function columns(E,e,children) { return E.Box({flexDirection:e.props.bodyColumns>=70?'row':'column',gap:2,children:children.map(c=>E.Box({flexDirection:'column',flexGrow:1,children:c}))}) }
'''

def add(slug, title, description, use, *, state='', start='', hooks='', command='', body='', access='', test='', preview='', band=''):
    MODS.append(dict(id='desktop-'+slug, title=title, category='Desktop', description=description, use=use, access=access, sample='', surface='desktop', state=state, start=start, hooks=hooks, command=command, body=body, test=test, preview=preview, band=band))

STEP = r'''
on('turn.step',async function*($,e,next){
 const r=yield* next(e)
 if(r.usage){records=[...records,{model:clean(e.model,80),...r.usage}].slice(-30);$.ui.invalidate('ui.render')}
 return r
})
'''
COMPLETE = "await $.turn.complete({turnId:'turn',answer:'',durationMs:4200,isAborted:false,usage:null})"
REQUEST = "const stream=$.turn.step({turnId:'turn',index:0,model:'claude-test',messageCount:1});let step=await stream.next();while(!step.done)step=await stream.next()"
USAGE_ACCESS = 'Reads reported session usage; missing figures remain labeled not reported. No pricing guesses or subscription billing calculation.'

add('usage-strip','Desktop Usage Strip','Show quota, reset countdowns, tokens, and cost in a composer strip.','Keep the reference image’s usage information beside your prompt.',
 state='let records=[],enabled=true', hooks=STEP,
 start="$.clock.every(60000,()=>$.ui.invalidate('ui.render'))",
 body=r'''
const u=await $.session.usage(),now=await $.clock.now()
const chips=usageChips(u,records,now)
return [strip(E,chips,e.props.bodyColumns),text(E,'Token totals: latest '+records.length+' observed requests. USD is the engine session ledger, not a subscription charge.'),button('toggle',enabled?'Hide composer strip':'Show composer strip',()=>{enabled=!enabled;redraw()})]
''',band=r'''
on('ui.render',{component:'AbovePrompt'},async($,e,next)=>{
 const downstream=await next(e)
 if(e.surface!=='desktop'||!enabled||e.props.hasSurvey)return downstream
 const E=$.ui.resolve(e),u=await $.session.usage(),now=await $.clock.now()
 const parts=usageChips(u,records,now)
 return E.Box({flexDirection:'column',gap:1,children:[strip(E,parts,e.props.bodyColumns),...(downstream?[downstream]:[])]})
})
''',access=USAGE_ACCESS+' Observes the latest 30 API requests in memory. Draws a composable AbovePrompt band on Desktop where the host exposes it; the command pane always offers the full display. Refreshes countdowns every minute.',
 test=r'''
expect(await ui.find({type:'Svg'})).toBeDefined()
const band=await $.ui.mount(bandSite(ID))
expect((await band.find({type:'Svg'})).props.alt).toContain('five_hour 37%')
expect(await band.find({type:'Text',text:'Other pane untouched'})).toBeDefined()
await ui.press({key:'toggle'})
expect(await band.find({type:'Svg'})).toBeUndefined()
await band.unmount()
state.emptyLimits=true;state.contextMissing=true;state.costMissing=true
await ui.press({key:'refresh'})
expect((await ui.find({type:'Svg'})).props.alt).toContain('USD not reported')
''',preview=REQUEST)

add('context-map','Desktop Context Map','Chart context headroom and sampled window growth.','Spot a filling context window visually.',state='let samples=[]',
 hooks=r'''on('turn.complete',async($,e,next)=>{const r=await next(e),u=await $.session.usage();if(Number.isFinite(u.context?.percent))samples=[...samples,u.context.percent].slice(-12);$.ui.invalidate('ui.render');return r})''',
 body=r'''const c=(await $.session.usage()).context||{}
return [text(E,count(c.tokens)+' / '+count(c.window)+' tokens'),...(Number.isFinite(c.percent)?[gauge(E,c.percent,'Context fill')]:[text(E,'Context usage not reported.')]),text(E,'Headroom: '+(Number.isFinite(c.tokens)&&Number.isFinite(c.window)?count(Math.max(0,c.window-c.tokens)):'not reported')),
 ...(samples.length?[chart(E,samples,samples.map((_,i)=>'Turn '+(i+1)),'Sampled context percentages')]:[text(E,'Complete a turn to start sampling.')]),button('clear','Clear chart',()=>{samples=[];redraw()})]''',access=USAGE_ACCESS+' Samples after observed completed turns; latest 12 samples, reset on reload.',
 test=COMPLETE+r''';expect(await ui.find({type:'Text',text:'Complete a turn to start sampling.'})).toBeUndefined();await ui.press({key:'clear'});expect(await ui.find({type:'Text',text:'Complete a turn to start sampling.'})).toBeDefined();state.contextMissing=true;await ui.press({key:'refresh'});expect(await ui.find({type:'Text',text:'Context usage not reported.'})).toBeDefined()''',preview=COMPLETE)

add('quota-clock','Desktop Quota Clock','Chart reported plan windows with live reset countdowns.','See when each quota window is due to reset.',start="$.clock.every(60000,()=>$.ui.invalidate('ui.render'))",
 body=r'''const u=await $.session.usage(),now=await $.clock.now()
return [...u.rateLimits.slice(0,8).flatMap(r=>[text(E,r.kind+' · '+count(r.percentUsed)+'% · '+waitUntil(r.resetsAt,now)),...(Number.isFinite(r.percentUsed)?[gauge(E,r.percentUsed,r.kind)]:[])]),...(u.rateLimits.length?[]:[text(E,'No plan windows reported.')])]''',access=USAGE_ACCESS+' Clock redraws once per minute; reaching zero does not invent a new quota reading.',
 test=r'''expect(await ui.find({type:'Text',text:/five_hour · 37% · 3h 0m/})).toBeDefined();await clock.advance(60000);expect(await ui.find({type:'Text',text:/2h 59m/})).toBeDefined();state.emptyLimits=true;await ui.press({key:'refresh'});expect(await ui.find({type:'Text',text:'No plan windows reported.'})).toBeDefined()''')

add('cost-watch','Desktop Cost Watch','Set a local budget reminder against reported session USD.','Keep a session cost target visible without changing tool permissions.',state="let budget=5,message=''",
 start="const saved=await $.store.get(prefix+'budget');if(Number.isFinite(saved)&&saved>0)budget=saved",
 body=r'''const usd=(await $.session.usage()).cost?.usd
return [input('budget','Session USD target',String(budget),async(v)=>{const n=Number(v);if(!Number.isFinite(n)||n<=0||n>100000){message='Use a target above 0 and at most 100000.';redraw();return}await $.store.set(prefix+'budget',n);budget=n;message='Target saved.';redraw()}),text(E,'Reported USD: '+(Number.isFinite(usd)?usd.toFixed(2):'not reported')),
 ...(Number.isFinite(usd)?[gauge(E,usd/budget*100,'Budget used'),text(E,usd>=budget?'Target reached. Reminder only.':'Remaining target: USD '+Math.max(0,budget-usd).toFixed(2))]:[]),text(E,message||'Session ledger; not an invoice or subscription charge. No calls are blocked.') ]''',access=USAGE_ACCESS+' Saves a user-entered budget per workspace in the local plugin store. Does not enforce a spending limit.',
 test=r'''await ui.input({key:'budget',text:'-1'});expect(saved.size).toBe(0);await ui.input({key:'budget',text:'1'});expect([...saved.values()][0]).toBe(1);expect(await ui.find({type:'Text',text:'Target reached. Reminder only.'})).toBeDefined();state.costMissing=true;await ui.press({key:'refresh'});expect(await ui.find({type:'Text',text:'Reported USD: not reported'})).toBeDefined()''',preview="await ui.input({key:'budget',text:'3'})")

add('token-flow','Desktop Token Flow','Chart uncached input, output, cache reads, and cache writes.','Compare token sources across observed requests.',state='let records=[]',hooks=STEP,
 body=r'''const total=records.reduce((a,r)=>a.map((n,i)=>n+num(r[['input_tokens','output_tokens','cache_read_input_tokens','cache_creation_input_tokens'][i]])),[0,0,0,0])
return [text(E,'Latest '+records.length+' observed requests; API-reported token categories.'),...(records.length?[chart(E,total,['Uncached input','Output','Cache read','Cache write'],'Token totals: '+total.join(', '))]:[text(E,'No requests observed yet.')]),button('clear','Clear observations',()=>{records=[];redraw()})]''',access='Observes API usage from the latest 30 completed requests in memory; includes any agent requests routed through the session. No model calls.',test=REQUEST+r''';expect((await ui.find({type:'Svg'})).props.alt).toContain('20, 10, 1000, 80');await ui.press({key:'clear'});expect(await ui.find({type:'Text',text:'No requests observed yet.'})).toBeDefined()''',preview=REQUEST)

add('tool-pulse','Desktop Tool Pulse','Chart completed tool latency and failures by tool.','See which observed tools take time or fail.',state='let records=[]',
 hooks=r'''on('tool.call',async($,e,next)=>{const t=await $.clock.now();try{const r=await next(e);records=[...records,{tool:clean(e.tool,80),ms:Math.max(0,(await $.clock.now())-t),failed:!!(r.deny||r.isError)}].slice(-100);$.ui.invalidate('ui.render');return r}catch(error){records=[...records,{tool:clean(e.tool,80),ms:Math.max(0,(await $.clock.now())-t),failed:true}].slice(-100);$.ui.invalidate('ui.render');throw error}})''',
 body=r'''const names=[...new Set(records.map(r=>r.tool))].slice(0,12),means=names.map(n=>{const a=records.filter(r=>r.tool===n);return a.reduce((s,r)=>s+r.ms,0)/a.length})
return [text(E,records.length+' observed calls · '+records.filter(r=>r.failed).length+' failures'),...(names.length?[chart(E,means,names,'Average completed tool milliseconds')]:[text(E,'No tools observed yet.')]),...names.map(n=>text(E,n+': '+records.filter(r=>r.tool===n).length+' calls')),button('clear','Clear tool chart',()=>{records=[];redraw()})]''',access='Observes tool names, completion/refusal/error state and local clock durations for the latest 100 calls. Does not save command arguments or tool results.',test=r'''await $.tool.call({tool:'Read',file_path:'README.md'});state.failTool=true;await $.tool.call({tool:'Read',file_path:'missing.md'});expect(await ui.find({type:'Text',text:'2 observed calls · 1 failures'})).toBeDefined();expect(state.downstream).toBe(2);await ui.press({key:'clear'});expect(await ui.find({type:'Text',text:'No tools observed yet.'})).toBeDefined()''',preview="await $.tool.call({tool:'Read',file_path:'README.md'});await $.tool.call({tool:'Bash',command:'npm test'})")

add('turn-chart','Desktop Turn Chart','Chart turn durations with interruption labels.','Compare the duration of your latest turns.',state='let turns=[]',
 hooks=r'''on('turn.complete',async($,e,next)=>{turns=[...turns,{ms:num(e.durationMs),aborted:e.isAborted,agent:clean(e.agentId||'main',60)}].slice(-12);$.ui.invalidate('ui.render');return next(e)})''',
 body=r'''return [text(E,turns.length+' completed turns observed'),...(turns.length?[chart(E,turns.map(t=>t.ms/1000),turns.map((t,i)=>'#'+(i+1)+(t.aborted?' interrupted':'')),'Turn duration in seconds'),...turns.map((t,i)=>text(E,'#'+(i+1)+' '+t.agent+' · '+(t.ms/1000).toFixed(1)+'s'+(t.aborted?' · interrupted':'')))]:[text(E,'No completed turns observed.')]),button('clear','Clear turn chart',()=>{turns=[];redraw()})]''',access='Observes durations, agent IDs and interruption flags for the latest 12 completed turns; memory only.',test=COMPLETE+r''';expect(await ui.find({type:'Text',text:'#1 main · 4.2s'})).toBeDefined();await ui.press({key:'clear'});expect(await ui.find({type:'Text',text:'No completed turns observed.'})).toBeDefined()''',preview=COMPLETE)

add('edit-map','Desktop Edit Map','Chart successful built-in edits grouped by file path.','See which files Claude has touched this session.',state='let edits=[]',
 hooks=r'''on('tool.call',{tool:['Edit','Write']},async($,e,next)=>{const r=await next(e);if(!r.deny&&!r.isError){edits=[...edits,clean(e.file_path,500)].slice(-100);$.ui.invalidate('ui.render')}return r})''',
 body=r'''const names=[...new Set(edits)].slice(0,12)
return [text(E,edits.length+' successful Edit/Write calls observed'),...(names.length?[chart(E,names.map(n=>edits.filter(p=>p===n).length),names.map(n=>n.split('/').pop()),'Edits per file'),...names.map(n=>text(E,n))]:[text(E,'No edits observed.')]),text(E,'Bash, MCP, and other mods’ writes are not detected.'),button('clear','Clear edit map',()=>{edits=[];redraw()})]''',access='Observes successful Edit/Write file paths only, latest 100 calls in memory. Does not read file contents; not a full filesystem audit.',test=r'''await $.tool.call({tool:'Write',file_path:'src/app.ts',content:'x'});state.failTool=true;await $.tool.call({tool:'Write',file_path:'src/no.ts',content:'x'});expect(await ui.find({type:'Text',text:'1 successful Edit/Write calls observed'})).toBeDefined();expect(await ui.find({type:'Text',text:'src/no.ts'})).toBeUndefined();await ui.press({key:'clear'});expect(await ui.find({type:'Text',text:'No edits observed.'})).toBeDefined()''',preview="await $.tool.call({tool:'Write',file_path:'src/app.ts',content:'fixture'});await $.tool.call({tool:'Edit',file_path:'src/ui.ts',old_string:'a',new_string:'b'})")

add('agent-desk','Desktop Agent Desk','Filter reported agents and copy a status snapshot.','Keep a readable agent roster next to the conversation.',state="let filter=''",
 body=r'''const all=await $.agent.list(),agents=all.filter(a=>(a.description+' '+a.status+' '+a.id).toLowerCase().includes(filter.toLowerCase())).slice(0,30)
const snapshot=agents.map(a=>a.id+' · '+a.status+' · '+a.description).join('\n')
return [input('filter','Filter agents',filter,v=>{filter=bounded(v,200);redraw()}),text(E,agents.length+' matching agents'),...agents.map(a=>frame(E,clean(a.description,200),[text(E,a.id+' · '+a.status+' · '+(a.type||'unspecified'))])),...(agents.length?[]:[text(E,'No matching agents reported.')]),button('copy','Copy roster',()=>copy(snapshot))]''',access='Reads engine-reported agent metadata on refresh. No spawning, messages, transcript reads, or agent control. Clipboard on button press.',test=r'''expect(await ui.find({type:'Text',text:'1 matching agents'})).toBeDefined();await ui.press({key:'copy'});expect(state.copies[0]).toContain('a-1');await ui.input({key:'filter',text:'nonexistent'});expect(await ui.find({type:'Text',text:'No matching agents reported.'})).toBeDefined()''')

GIT_LOAD = r'''
async function load($){try{const args=tab==='status'?['status','--short','--branch']:tab==='staged'?['diff','--cached','--no-ext-diff','--no-textconv','--no-color','--']:['diff','--no-ext-diff','--no-textconv','--no-color','--']
 const r=await $.process.run(['git','--no-pager',...args],{cwd:await $.session.cwd(),timeoutMs:10000});report=clean(r.exitCode===0?r.stdout||'No changes.':'Git inspection failed: '+r.stderr)}catch(error){report='Git inspection failed: '+error.message}$.ui.invalidate('ui.render')}
'''
add('review-desk','Desktop Review Desk','Switch between Git status, staged diff, and unstaged diff.','Inspect a change from one desktop review pane.',state="let tab='status',report='Open to inspect Git.'\n"+GIT_LOAD,command='await load($)',
 body=r'''return [row(E,['status','staged','unstaged'].map(t=>button('tab-'+t,t+(tab===t?' ✓':''),async()=>{tab=t;await load($)}))),code(E,report),button('reload','Reload Git',()=>load($)),button('copy','Copy visible report',()=>copy(report)),text(E,'Read-only Git inspection. No staging, commits, or command execution from the diff.') ]''',access='Runs read-only Git argv commands in session cwd only when opened or refreshed. External diff and textconv disabled. Output truncated to 9,000 characters. Clipboard only on press.',test=r'''await ui.press({key:'tab-staged'});expect(state.argv.some(a=>a.includes('--cached')&&a.includes('--no-ext-diff')&&a.includes('--no-textconv'))).toBe(true);await ui.press({key:'copy'});expect(state.copies[0]).toContain('new label');state.processError=true;await ui.press({key:'reload'});expect((await ui.find({type:'Code'})).props.source).toContain('Git inspection failed')''',preview="await ui.press({key:'tab-staged'})")

FILE_LOAD = r'''
async function readText($,target){const chosen=path(target),p=/^(\/|[A-Za-z]:[\\/])/.test(chosen)?chosen:(await $.session.cwd()).replace(/[\\/]$/,'')+'/'+chosen,s=await $.fs.stat(p);if(s.kind!=='file'||s.isLink||s.size>131072)throw Error('Choose a regular non-symlink text file up to 128 KiB.');const content=await $.fs.read(p);if(content.includes('\0'))throw Error('Binary files are not supported.');return clean(content)}
'''
add('file-desk','Desktop File Desk','Read a bounded text file with line filtering and path drafting.','Inspect a file while preparing a precise question about it.',state="let target='README.md',source='',filter='',message='Choose a file to read.'\n"+FILE_LOAD,
 body=r'''const lines=source.split('\n').map((s,i)=>(i+1)+': '+s).filter(s=>!filter||s.toLowerCase().includes(filter.toLowerCase())).slice(0,100)
return [input('path','Text file',target,async(v)=>{try{target=path(v);source=await readText($,target);message='Read '+target}catch(error){source='';message=error.message}redraw()}),input('filter','Filter lines',filter,v=>{filter=bounded(v,200);redraw()}),text(E,message),code(E,source?lines.join('\n'):'No file loaded.'),button('draft','Draft a question',async()=>{const r=await $.prompt.fill({text:'Review '+target+' and explain the relevant lines.'});if(!r.isFilled)$.ui.toast('Composer unavailable.')})]''',access='Reads a user-chosen regular text file up to 128 KiB on input submission; no automatic reads. Symlinks/binary files refused, preview truncated to 9,000 characters and 100 matching lines. Paths may point to private files. Fills a composer draft on press; never submits it.',test=r'''await ui.input({key:'path',text:'README.md'});expect(state.reads).toEqual(['/work/README.md']);await ui.input({key:'filter',text:'Setup'});expect((await ui.find({type:'Code'})).props.source).toContain('Setup');await ui.press({key:'draft'});expect(state.drafts[0]).toContain('README.md');state.isLink=true;await ui.input({key:'path',text:'linked.txt'});expect(state.reads.length).toBe(1);expect(await ui.find({type:'Text',text:/non-symlink/})).toBeDefined()''',preview="await ui.input({key:'path',text:'README.md'})")

add('markdown-reader','Desktop Markdown Reader','Render a local Markdown document with a source tab.','Read project documentation in a desktop pane.',state="let target='README.md',source='',tab='preview',message='Choose a Markdown file.'\n"+FILE_LOAD,
 body=r'''return [input('path','Markdown file',target,async(v)=>{try{const p=path(v);if(!/\.md$/i.test(p))throw Error('Choose a .md file.');target=p;source=await readText($,target);message='Loaded '+target}catch(error){source='';message=error.message}redraw()}),row(E,['preview','source'].map(t=>button('tab-'+t,t,()=>{tab=t;redraw()}))),text(E,message),...(source?[tab==='preview'?E.Markdown({text:source}):code(E,source)]:[text(E,'No document loaded.')]),button('copy','Copy Markdown source',()=>copy(source))]''',access='Reads a chosen .md file up to 128 KiB, refuses symlinks, renders at most 9,000 characters. Markdown links behave like normal links when clicked; mod makes no network requests. Clipboard on press.',test=r'''await ui.input({key:'path',text:'README.md'});expect(await ui.find({type:'Markdown'})).toBeDefined();await ui.press({key:'tab-source'});expect((await ui.find({type:'Code'})).props.source).toContain('# Demo');await ui.press({key:'copy'});expect(state.copies[0]).toContain('## Setup');await ui.input({key:'path',text:'.env'});expect(state.reads.length).toBe(1);expect(await ui.find({type:'Text',text:'Choose a .md file.'})).toBeDefined()''',preview="await ui.input({key:'path',text:'README.md'})")

add('compare-desk','Desktop Compare Desk','Compare two local text files in responsive side-by-side columns.','Check two versions without switching windows.',state="let left='before.txt',right='after.txt',a='',b='',message='Load two files to compare.'\n"+FILE_LOAD,
 body=r'''const aa=a.split('\n'),bb=b.split('\n'),n=Math.max(aa.length,bb.length),changed=Array.from({length:n},(_,i)=>i).filter(i=>aa[i]!==bb[i])
return [input('left','Left file',left,v=>{left=path(v);redraw()}),input('right','Right file',right,v=>{right=path(v);redraw()}),button('load','Compare files',async()=>{try{const x=await readText($,left),y=await readText($,right);a=x;b=y;message='Compared preview: '+changedLines(x,y)+' differing line positions.'}catch(error){a='';b='';message=error.message}redraw()}),text(E,message),columns(E,e,[[text(E,left,{bold:true}),code(E,a||'No left preview.')],[text(E,right,{bold:true}),code(E,b||'No right preview.')]]),text(E,changed.length?'Changed line positions: '+changed.slice(0,40).map(i=>i+1).join(', '):'No differing preview lines.'),text(E,'Position comparison, not an insertion-aware diff. Each preview is bounded to 9,000 characters.') ]''',access='Reads two user-chosen regular non-symlink text files up to 128 KiB each on Compare. No writes. Line positions compare truncated previews; insertions shift subsequent positions.',test=r'''await ui.press({key:'load'});expect(await ui.find({type:'Text',text:'Compared preview: 1 differing line positions.'})).toBeDefined();expect(state.reads).toEqual(['/work/before.txt','/work/after.txt']);state.size=131073;await ui.press({key:'load'});expect(state.reads.length).toBe(2);expect(await ui.find({type:'Text',text:/up to 128 KiB/})).toBeDefined()''',preview="await ui.press({key:'load'})")
MODS[-1]['state']+=r'''
function changedLines(a,b){const x=a.split('\n'),y=b.split('\n');return Array.from({length:Math.max(x.length,y.length)},(_,i)=>i).filter(i=>x[i]!==y[i]).length}
'''

add('prompt-builder','Desktop Prompt Builder','Build a saved prompt from goal, constraints, and acceptance criteria.','Prepare a clear request before filling the composer.',state="let fields={goal:'',constraints:'',acceptance:''},message=''",
 start="const s=await $.store.get(prefix+'fields');if(s&&['goal','constraints','acceptance'].every(k=>typeof s[k]==='string'&&s[k].length<=2000))fields=s",
 body=r'''const draft=['Goal: '+fields.goal,'Constraints: '+fields.constraints,'Acceptance criteria: '+fields.acceptance].join('\n\n')
return [...Object.entries(fields).map(([key,v])=>input(key,key,v,async(value)=>{try{const next={...fields,[key]:bounded(value.trim(),2000)};await $.store.set(prefix+'fields',next);fields=next;message='Saved locally.'}catch(error){message=error.message}redraw()})),code(E,draft),button('draft','Fill composer draft',async()=>{if(!fields.goal){message='Enter a goal first.';redraw();return}const r=await $.prompt.fill({text:draft});if(!r.isFilled)$.ui.toast('Composer unavailable.')}),button('copy','Copy prompt',()=>copy(draft)),text(E,message||'Fill replaces the current composer draft; review and send it yourself.') ]''',access='Saves up to 2,000 characters per field in a workspace-partitioned local store. Copy/fill only on press. Fill replaces the composer draft without submitting a prompt.',test=r'''await ui.press({key:'draft'});expect(state.drafts.length).toBe(0);await ui.input({key:'goal',text:'Improve keyboard navigation'});await ui.input({key:'acceptance',text:'Tab reaches every control'});await ui.press({key:'draft'});expect(state.drafts[0]).toContain('Acceptance criteria: Tab reaches every control');expect(saved.size).toBe(1);await ui.input({key:'goal',text:'x'.repeat(2001)});expect([...saved.values()][0].goal).toBe('Improve keyboard navigation')''',preview="await ui.input({key:'goal',text:'Improve keyboard navigation'});await ui.input({key:'constraints',text:'Preserve existing shortcuts'});await ui.input({key:'acceptance',text:'Tab reaches every control'})")

add('session-brief','Desktop Session Brief','Combine observed tool and turn counts with a manual handoff note.','Copy a factual session summary with your next step.',state="let calls=0,failures=0,turns=0,note=''",
 hooks=r'''on('tool.call',async($,e,next)=>{const r=await next(e);calls++;if(r.deny||r.isError)failures++;$.ui.invalidate('ui.render');return r})
on('turn.complete',async($,e,next)=>{turns++;$.ui.invalidate('ui.render');return next(e)})''',
 body=r'''const summary='Workspace: '+await $.session.cwd()+'\nObserved turns: '+turns+'\nObserved tools: '+calls+'\nTool errors/refusals: '+failures+'\nUser note: '+note
return [text(E,'Counts begin at plugin load; tool completion does not prove a task passed.'),input('note','Next step / handoff',note,v=>{note=bounded(v,2000);redraw()}),code(E,summary),button('copy','Copy brief',()=>copy(summary)),button('clear','Clear counters and note',()=>{calls=0;failures=0;turns=0;note='';redraw()})]''',access='Observes tool status and turn completion counts in memory; reads cwd. Does not read messages or tool outputs. User note and counters reset on reload; clipboard on press.',test=COMPLETE+r''';await $.tool.call({tool:'Read',file_path:'README.md'});await ui.input({key:'note',text:'Review accessibility next'});await ui.press({key:'copy'});expect(state.copies[0]).toContain('Observed turns: 1');expect(state.copies[0]).toContain('Review accessibility next');await ui.press({key:'clear'});expect((await ui.find({type:'Code'})).props.source).toContain('Observed tools: 0')''',preview=COMPLETE+";await ui.input({key:'note',text:'Review the staged patch and run focused checks'})")

add('bookmark-dock','Desktop Bookmark Dock','Keep labeled web references with copy and delete controls.','Put project references one click away.',state="let items=[],label='',url='',message=''",
 start="await load($)",command='await load($)',
 body=r'''return [input('label','Label',label,v=>{label=bounded(v.trim(),120);redraw()}),input('url','HTTP / HTTPS URL',url,v=>{url=bounded(v.trim(),2000);redraw()}),button('save','Save bookmark',async()=>{try{const u=new URL(url);if(!['http:','https:'].includes(u.protocol)||u.username||u.password)throw Error('Use an HTTP/HTTPS URL without embedded credentials.');const keys=(await $.store.keys()).filter(k=>k.startsWith(prefix+'item:'));if(keys.length>=100)throw Error('Limit is 100 bookmarks; delete one first.');await $.store.set(prefix+'item:'+crypto.randomUUID(),{label:label||u.hostname,url:u.href});url='';label='';message='Saved locally.';await load($)}catch(error){message=error.message}redraw()}),...items.map((x,i)=>row(E,[E.Link({href:x.url,label:x.label}),button('copy-'+i,'Copy URL',()=>copy(x.url)),button('delete-'+i,'Delete',async()=>{await $.store.delete(x.key);await load($)})])),text(E,message||'Links open only when clicked. Latest 100 workspace bookmarks.'),button('reload','Reload bookmarks',()=>load($))]''',access='Stores up to 100 user-entered HTTP/HTTPS bookmarks per workspace; credential URLs refused. Clipboard on press. Clicking a link uses the host browser. Mod makes no network requests.',test=r'''await ui.input({key:'url',text:'javascript:alert(1)'});await ui.press({key:'save'});expect(saved.size).toBe(0);await ui.input({key:'label',text:'Docs'});await ui.input({key:'url',text:'https://example.com/docs'});await ui.press({key:'save'});expect(saved.size).toBe(1);await ui.press({key:'copy-0'});expect(state.copies[0]).toBe('https://example.com/docs');await ui.press({key:'delete-0'});expect(saved.size).toBe(0)''',preview="await ui.input({key:'label',text:'Project docs'});await ui.input({key:'url',text:'https://example.com/docs'});await ui.press({key:'save'})")
MODS[-1]['state']+=r'''
async function load($){items=[];for(const key of (await $.store.keys()).filter(k=>k.startsWith(prefix+'item:')).sort().slice(-100)){const x=await $.store.get(key);if(x&&typeof x.label==='string'&&typeof x.url==='string'){try{const u=new URL(x.url);if(['http:','https:'].includes(u.protocol)&&!u.username&&!u.password)items.push({...x,key})}catch{}}}$.ui.invalidate('ui.render')}
'''

add('checklist-desk','Desktop Checklist Desk','Move saved work items through To do, Doing, and Done columns.','Track a small workflow on the desktop.',state="let items=[],message=''",
 start='await load($)',command='await load($)',
 body=r'''return [input('entry','Work item','',async(v)=>{try{const s=bounded(v.trim(),1000);if(!s)return;const keys=(await $.store.keys()).filter(k=>k.startsWith(prefix+'item:'));if(keys.length>=100)throw Error('Limit is 100 items; delete one first.');await $.store.set(prefix+'item:'+new Date(await $.clock.now()).toISOString()+':'+crypto.randomUUID(),{text:s,phase:0});await load($)}catch(error){message=error.message;redraw()}}),columns(E,e,['To do','Doing','Done'].map((name,phase)=>[text(E,name,{bold:true}),...items.filter(x=>x.phase===phase).map(x=>frame(E,x.text,[button('move-'+x.key,'Move to '+['To do','Doing','Done'][(phase+1)%3],async()=>{const latest=await $.store.get(x.key);if(latest)await $.store.set(x.key,{...latest,phase:(latest.phase+1)%3});await load($)}),button('delete-'+x.key,'Delete',async()=>{await $.store.delete(x.key);await load($)})])),...(items.some(x=>x.phase===phase)?[]:[text(E,'Empty')])])),text(E,message||items.length+' saved items'),button('reload','Reload board',()=>load($))]''',access='Stores up to 100 user-entered work items per workspace. Move/delete only on press; reload sees other sessions. Same-item concurrent changes are last-write-wins. Responsive columns stack in narrow panes.',test=r'''await ui.input({key:'entry',text:'Review keyboard controls'});expect(saved.size).toBe(1);const key=[...saved.keys()][0];await ui.press({key:'move-'+key});expect(saved.get(key).phase).toBe(1);await ui.press({key:'move-'+key});expect(saved.get(key).phase).toBe(2);await ui.press({key:'delete-'+key});expect(saved.size).toBe(0)''',preview="await ui.input({key:'entry',text:'Review keyboard controls'});await ui.input({key:'entry',text:'Capture desktop screenshots'});await ui.press({key:'move-'+[...saved.keys()][0]})")
MODS[-1]['state']+=r'''
async function load($){items=[];for(const key of (await $.store.keys()).filter(k=>k.startsWith(prefix+'item:')).sort().slice(-100)){const x=await $.store.get(key);if(x&&typeof x.text==='string'&&[0,1,2].includes(x.phase))items.push({...x,key})}$.ui.invalidate('ui.render')}
'''

add('workspace-home','Desktop Workspace Home','Show the current workspace, Git state, and session usage together.','Orient yourself when switching between desktop sessions.',state="let report='Reload to inspect Git.'",command='await load($)',
 body=r'''const cwd=await $.session.cwd(),u=await $.session.usage()
return [text(E,cwd,{bold:true}),columns(E,e,[[text(E,'Workspace Git state'),code(E,report)],[text(E,'Session context: '+count(u.context?.percent)+'%'),text(E,'Reported USD: '+(Number.isFinite(u.cost?.usd)?u.cost.usd.toFixed(2):'not reported')),text(E,'Plan windows: '+u.rateLimits.length)]]),button('copy','Copy workspace path',()=>copy(cwd)),button('reload','Reload Git state',()=>load($))]''',access='Reads cwd and reported usage; runs read-only git status argv on open/reload, bounded to 9,000 characters. Clipboard on press. No filesystem writes.',test=r'''expect(await ui.find({type:'Text',text:'/work'})).toBeDefined();await ui.press({key:'copy'});expect(state.copies[0]).toBe('/work');expect(state.argv[0]).toEqual(['git','--no-pager','status','--short','--branch']);state.processError=true;await ui.press({key:'reload'});expect((await ui.find({type:'Code'})).props.source).toContain('Git inspection failed')''')
MODS[-1]['state']+=r'''
async function load($){try{const r=await $.process.run(['git','--no-pager','status','--short','--branch'],{cwd:await $.session.cwd(),timeoutMs:10000});report=clean(r.exitCode===0?r.stdout||'Clean workspace.':'Git inspection failed: '+r.stderr)}catch(error){report='Git inspection failed: '+error.message}$.ui.invalidate('ui.render')}
'''

add('break-bell','Desktop Break Bell','Set an adjustable countdown with a visual progress chart and toast.','Remember a break during a long desktop session.',state="let minutes=25,remaining=1500,running=false,last=0,message=''",
 start=r'''$.clock.every(1000,async()=>{if(!running)return;const now=await $.clock.now();remaining=Math.max(0,remaining-(now-last)/1000);last=now;if(remaining===0){running=false;$.ui.toast('Break Bell: time for a break.')}$.ui.invalidate('ui.render')})''',
 body=r'''const seconds=Math.ceil(remaining)
return [input('minutes','Minutes (1–180)',String(minutes),v=>{const n=Number(v);if(!Number.isInteger(n)||n<1||n>180){message='Use whole minutes from 1 to 180.';redraw();return}minutes=n;remaining=n*60;running=false;message='Timer reset.';redraw()}),text(E,Math.floor(seconds/60).toString().padStart(2,'0')+':'+(seconds%60).toString().padStart(2,'0'),{bold:true}),gauge(E,(1-remaining/(minutes*60))*100,'Interval elapsed'),row(E,[button('start',running?'Pause':'Start',async()=>{const now=await $.clock.now();if(running)remaining=Math.max(0,remaining-(now-last)/1000);last=now;running=!running;redraw()}),button('reset','Reset',()=>{running=false;remaining=minutes*60;redraw()})]),text(E,message||'Local session timer. No OS alarm or background reminder after closing Claude.') ]''',access='Uses a local one-second clock and one completion toast; memory only, reset on reload. Does not play audio or send an OS notification.',test=r'''await ui.input({key:'minutes',text:'0'});expect(await ui.find({type:'Text',text:'25:00'})).toBeDefined();await ui.input({key:'minutes',text:'1'});await ui.press({key:'start'});await clock.advance(10000);expect(await ui.find({type:'Text',text:'00:50'})).toBeDefined();await ui.press({key:'start'});await clock.advance(10000);expect(await ui.find({type:'Text',text:'00:50'})).toBeDefined();await ui.press({key:'start'});await clock.advance(50000);expect(state.toasts).toEqual(['Break Bell: time for a break.']);await ui.press({key:'reset'});expect(await ui.find({type:'Text',text:'01:00'})).toBeDefined()''',preview="await ui.input({key:'minutes',text:'15'});await ui.press({key:'start'});await clock.advance(120000)")

add('json-desk','Desktop JSON Desk','Validate pasted JSON with a searchable key summary and formatted preview.','Inspect an API response visually without a file or network request.',state="let source='',parsed=null,filter='',message='Paste JSON to begin.'",
 body=r'''const list=parsed&&typeof parsed==='object'?Object.entries(parsed).filter(([k])=>k.toLowerCase().includes(filter.toLowerCase())).slice(0,50):[]
const formatted=JSON.stringify(parsed,null,2)
return [input('source','JSON',source,v=>{try{source=bounded(v,9000);parsed=JSON.parse(source);message='Valid JSON.'}catch(error){parsed=null;message='Invalid JSON: '+error.message}redraw()}),input('filter','Filter top-level keys',filter,v=>{filter=bounded(v,200);redraw()}),text(E,message),columns(E,e,[[text(E,'Keys (up to 50)',{bold:true}),...list.map(([k,v])=>text(E,k+' · '+(v===null?'null':Array.isArray(v)?'array':typeof v)))],[text(E,'Formatted preview',{bold:true}),code(E,message==='Valid JSON.'?formatted:'No valid JSON.')]]),button('copy','Copy formatted JSON',async()=>{if(message==='Valid JSON.')await copy(bounded(formatted,30000))})]''',access='Parses pasted JSON locally, input up to 9,000 characters, first 50 matching top-level keys, display capped at 9,000 characters. Clipboard on press (up to 30,000 characters). No files or persistence.',test=r'''await ui.input({key:'source',text:'{"ready":true,"items":[1,2]}'});expect(await ui.find({type:'Text',text:'ready · boolean'})).toBeDefined();await ui.input({key:'filter',text:'items'});expect(await ui.find({type:'Text',text:'ready · boolean'})).toBeUndefined();await ui.press({key:'copy'});expect(JSON.parse(state.copies[0]).items).toEqual([1,2]);await ui.input({key:'source',text:'{bad'});await ui.press({key:'copy'});expect(state.copies.length).toBe(1);await ui.input({key:'source',text:'null'});expect(await ui.find({type:'Text',text:'Valid JSON.'})).toBeDefined()''',preview="await ui.input({key:'source',text:'{\"name\":\"desktop-mods\",\"ready\":true,\"tools\":[\"usage-strip\",\"review-desk\"]}'})")

assert len(MODS) == 20

MODULE = r'''import {clean,text,code,row,frame,bounded,path,xml,num,pct,count,waitUntil,chart,gauge,columns,usageChips,strip} from './ui.js'
const ID=__ID__, TITLE=__TITLE__
let surface=null,prefix=''
__STATE__
export function register(on){
 on('session.start',async($,e,next)=>{
  surface=e.surface;prefix='workspace:'+encodeURIComponent(e.cwd)+':'
  await $.command.register({name:ID,description:__DESC__,immediate:true})
  if(surface==='desktop'){__START__}
  return next(e)
 })
 on('command.run',{command:__ID__},async($,e)=>{
  if(surface!=='desktop')return {text:TITLE+' requires the Claude Desktop Code tab.'}
  __COMMAND__
  await $.ui.open({id:ID,title:TITLE,focus:true,closeOnEscape:true})
  return {}
 })
 __HOOKS__
 __BAND__
 on('ui.render',{component:'Pane'},async($,e,next)=>{
  if(e.requestId!==ID)return next(e)
  const E=$.ui.resolve(e)
  if(e.surface!=='desktop')return text(E,TITLE+' requires the Claude Desktop Code tab.')
  try{return frame(E,TITLE,[...await draw($,E,e),E.Button({key:'refresh',label:'Refresh',onPress:()=>$.ui.invalidate('ui.render')})])}
  catch(error){return frame(E,TITLE,[text(E,'Unable to display: '+clean(error.message,500),{color:'yellow'}),E.Button({key:'refresh',label:'Retry',onPress:()=>$.ui.invalidate('ui.render')})])}
 })
}
async function draw($,E,e){
 const redraw=()=>$.ui.invalidate('ui.render')
 const button=(key,label,onPress)=>E.Button({key,label,onPress})
 const input=(key,label,value,onSubmit)=>E.Input({key,label,value,submitLabel:'apply',onSubmit})
 const copy=async(value)=>{const r=await $.ui.copy({text:clean(value,30000)});if(!r.isCopied)$.ui.toast('Clipboard unavailable.')}
 __BODY__
}
'''

# Use the existing engine fixture schema, adding flags that test missing data.
FIXTURE = (ROOT/'mods/task-board/tests/fixtures.ts').read_text()
FIXTURE = FIXTURE.replace('contextMissing:false,', 'costMissing:false,contextMissing:false,')
FIXTURE = FIXTURE.replace('cost:{usd:1.2}', 'cost:state.costMissing?undefined:{usd:1.2}')
FIXTURE += r'''
export function bandSite(plugin, surface:'terminal'|'desktop'='desktop') {
 return {plugin,component:'AbovePrompt' as const,requestId:'band',surface,viewport:{columns:90,rows:40},props:{hasSurvey:false,isWorking:false,maxRows:6,bodyColumns:90,scroll:{offset:0,bodyRows:6},view:{}}}
}
'''

TEST = r'''import {expect,test} from 'claude-code/testing'
import {world,site,bandSite} from './fixtures'
const ID=__ID__

test('desktop command opens only on request',async($,on)=>{
 const {state}=world(on)
 await $.session.start({surface:'desktop',isInteractive:true,cwd:'/work'})
 expect(state.registered[0]).toMatchObject({name:ID,immediate:true})
 expect(state.opened).toEqual([])
 await $.command.run({command:ID,args:''})
 expect(state.opened[0]).toMatchObject({id:ID,focus:true,closeOnEscape:true})
})
test('other pane remains untouched',async($,on)=>{
 world(on)
 const ui=await $.ui.mount({...site(ID,'desktop'),requestId:'other'})
 expect(await ui.find({type:'Text',text:'Other pane untouched'})).toBeDefined()
 await ui.unmount()
})
for(const width of [36,84])test('desktop controls at width '+width,async($,on)=>{
 const {state,saved,clock}=world(on)
 await $.session.start({surface:'desktop',isInteractive:true,cwd:'/work'})
 await $.command.run({command:ID,args:''})
 const ui=await $.ui.mount(site(ID,'desktop',width))
 expect(await ui.find({type:'Text',text:__TITLE__})).toBeDefined()
 __TEST__
 expect(await ui.find({type:'Text',text:/Unable to display:/})).toBeUndefined()
 await ui.unmount()
})
for(const surface of ['terminal',null] as const)test('explains unsupported surface '+surface,async($,on)=>{
 const {state}=world(on)
 await $.session.start({surface,isInteractive:surface!==null,cwd:'/work'})
 const r=await $.command.run({command:ID,args:''})
 expect(r.text).toContain('requires the Claude Desktop Code tab')
 expect(state.opened.length).toBe(0)
 expect(state.argv.length).toBe(0)
 expect(state.reads.length).toBe(0)
})
test('capture native render tree for fixture preview',async($,on)=>{
 const {state,saved,clock}=world(on)
 await $.session.start({surface:'desktop',isInteractive:true,cwd:'/work'})
 await $.command.run({command:ID,args:''})
 const ui=await $.ui.mount(site(ID,'desktop',84))
 __PREVIEW__
 const tree=await ui.find({type:'Box'})
 expect(tree).toBeDefined()
 expect(await ui.find({type:'Text',text:/Unable to display:/})).toBeUndefined()
 console.log('MOD_PREVIEW:'+JSON.stringify({id:ID,surface:'desktop',tree}))
 await ui.unmount()
})
'''

def build():
    for m in MODS:
        d=ROOT/'mods'/m['id']
        for sub in ['.claude-plugin','hooks','tests']:
            (d/sub).mkdir(parents=True,exist_ok=True)
        (d/'.claude-plugin/plugin.json').write_text(json.dumps(dict(name=m['id'],version='1.0.0',description=m['description'],author={'name':'Yash Thakker'},license='MIT',homepage='https://github.com/whyashthakker/awesome-claude-code-mods'),indent=2)+'\n')
        (d/'hooks/hooks.json').write_text('{"modules":["./register.js"]}\n')
        source=MODULE
        for key in ['id','title','description','state','start','hooks','command','body','band']:
            value=json.dumps(m[key]) if key in ['id','title','description'] else m[key]
            source=source.replace('__'+('DESC' if key=='description' else key.upper())+'__',value)
        (d/'hooks/register.js').write_text('\n'.join(line.rstrip() for line in source.splitlines())+'\n')
        (d/'hooks/ui.js').write_text(UI)
        (d/'LICENSE').write_bytes((ROOT/'LICENSE').read_bytes())
        test=TEST
        for key in ['id','title','test','preview']:
            test=test.replace('__'+key.upper()+'__',json.dumps(m[key]) if key in ['id','title'] else m[key])
        (d/'tests/register.test.ts').write_text('\n'.join(line.rstrip() for line in test.splitlines())+'\n')
        (d/'tests/fixtures.ts').write_text(FIXTURE)
        (d/'README.md').write_text(f'''# {m['title']}

{m['description']}

**Use it when:** {m['use']}

![{m['title']} fixture preview](../../assets/screenshots/{m['id']}.png)

*Desktop-surface native test-kit tree, painted in a browser fixture preview with sample data. This is not a Claude Desktop app capture. [Provenance](../../docs/SCREENSHOTS.md).*

## Install and open

Requires Claude Code 2.1.287+ in the **Claude Desktop Code tab**; tested with 2.1.288's native test kit. Chat/Cowork tabs do not host this API. WSL Desktop sessions do not support plugins. No runtime packages or build step.

Install the current checkout immediately from a terminal in this repository:

```sh
claude plugin marketplace add .
claude plugin install {m['id']}@awesome-claude-code-mods
```

Or install the published collection:

```sh
claude plugin marketplace add whyashthakker/awesome-claude-code-mods
claude plugin install {m['id']}@awesome-claude-code-mods
```

Start a new **local Code session** in Claude Desktop, or run `/reload-plugins` in an open Code session, then `/{m['id']}`. Click controls or use Tab and Enter; Esc closes the pane. Non-Desktop commands return a compatibility explanation. [Desktop setup and all 20 mods](../../docs/DESKTOP.md).

## Access and behavior

{m['access']}

Histories begin at load and reset on reload; no earlier activity is reconstructed. Store keys use the workspace directory; saved items are local to this plugin. Files/processes use session cwd. Stored content and clipboard exports can contain private information. No model calls, automatic prompt submissions, or permission approvals.

## Verify

```sh
claude plugin validate mods/{m['id']} --strict
claude plugin test mods/{m['id']}
```

Native tests cover command opening, pane isolation, Desktop controls at two widths, unsupported surfaces, error/empty states, and preview capture. These checks validate element trees and callbacks; native Desktop painting and keyboard acceptance remain a manual check. [Validation](../../docs/VALIDATION.md).

MIT licensed, with source and tests included.
''')
    catalog=json.loads((ROOT/'catalog.json').read_text())
    catalog=[m for m in catalog if m.get('surface')!='desktop' and not m['id'].startswith('desktop-')]
    catalog.extend({k:m[k] for k in ['id','title','category','description','use','access','sample','surface']} for m in MODS)
    (ROOT/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
    p=ROOT/'.claude-plugin/marketplace.json'
    marketplace=json.loads(p.read_text())
    marketplace['metadata'].update(description='70 MIT-licensed Claude Code mods, including 20 for the Desktop Code tab',version='1.1.0')
    marketplace['plugins']=[x for x in marketplace['plugins'] if not x['name'].startswith('desktop-')]
    marketplace['plugins'].extend(dict(name=m['id'],source='./mods/'+m['id'],description=m['description'],version='1.0.0',category='productivity') for m in MODS)
    p.write_text(json.dumps(marketplace,indent=2)+'\n')
    print('Built 20 standalone Desktop plugins; catalogue contains',len(catalog))

if __name__=='__main__':
    build()
