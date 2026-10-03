#!/usr/bin/env python3
"""Build independent plugins from reviewed templates. No runtime dependencies."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
MODS = []

def add(id, title, category, description, use, state='', start='', hooks='', command='', body='', access='', sample='', check='', test=''):
    MODS.append(dict(id=id,title=title,category=category,description=description,use=use,state=state,start=start,hooks=hooks,command=command,body=body,access=access,sample=sample,check=check,test=test))

UI = r'''// Pure UI helpers. No engine access; each plugin contains its own copy.
export function clean(value, limit = 9000) {
  return String(value ?? '').replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f-\u009f]/g, '').slice(0, limit)
}
export function text(E, value, props = {}) {
  return E.Text({ ...props, children: [clean(value)] })
}
export function code(E, value, language = 'text') {
  return E.Code({ source: clean(value), language })
}
export function row(E, children) {
  return E.Box({ flexDirection: 'row', columnGap: 2, flexWrap: 'wrap', children })
}
export function frame(E, title, subtitle, children) {
  return E.Box({ flexDirection: 'column', gap: 1, children: [
    text(E, title, { bold: true, color: 'cyan' }),
    text(E, subtitle, { dimColor: true }), ...children,
  ] })
}
export function bar(percent, width = 24) {
  const p = Math.max(0, Math.min(100, Number(percent) || 0))
  const n = Math.round(p / 100 * width)
  return '[' + '#'.repeat(n) + '-'.repeat(width - n) + '] ' + p.toFixed(1) + '%'
}
export function pretty(value) { return JSON.stringify(value, null, 2) }
export function bounded(value, max = 9000) {
  if (value.length > max) throw new Error('Input exceeds ' + max + ' characters. Use a smaller selection.')
  return value
}
export function entries(value) { return value && typeof value === 'object' ? Object.entries(value) : [] }
export function safePath(value) {
  const path = value.trim()
  if (!path || path.startsWith('-') || /[\x00-\x1f]/.test(path)) throw new Error('Enter a path without control characters or leading flags.')
  return path
}
'''

# Session diagnostics: observe real events, never manufacture activity.
add('context-meter','Context Meter','Session','See the current context window fill and remaining tokens.','Check headroom before a large refactor.',body="""
const u = await $.session.usage()
const c = u.context
if(c.tokens===undefined || c.percent===undefined) return [text(E,'Context usage not reported yet.'),text(E,'Window: '+c.window+' tokens'),refresh]
return [text(E, bar(c.percent), {color:c.percent >= 80 ? 'yellow' : 'green'}),
  text(E, Number(c.tokens).toLocaleString() + ' / ' + Number(c.window).toLocaleString() + ' tokens'),
  text(E, Math.max(0,c.window-c.tokens).toLocaleString() + ' tokens remaining'), refresh]
""",access='Reads session usage. No files, processes, network, or persistence.',check='84,000 / 200,000 tokens')
add('quota-watch','Quota Watch','Session','Inspect reported plan windows and their reset times.','Plan work around the limits your session reports.',body="""
const u = await $.session.usage()
return [text(E,'Reported plan windows',{bold:true}), ...u.rateLimits.map((r) => text(E,
  r.kind + '  ' + bar(r.percentUsed) + '\\nResets: ' + (r.resetsAt ? new Date(r.resetsAt).toISOString() : 'not reported'))),
  ...(u.rateLimits.length ? [] : [text(E,'No plan limits reported for this account.')]),refresh]
""",access='Reads session usage only.',check='Reported plan windows')
add('cache-inspector','Cache Inspector','Session','Track API cache reads, writes, and uncached input by request.','Check whether repeated turns are using the prompt cache.',state='let records = []',hooks="""
on('turn.step', async function* ($, e, next) {
  const result = yield* next(e)
  if(result.usage) {
    records = [...records, {model:e.model, agent:e.agentId || 'main', ...result.usage}].slice(-30)
    $.ui.invalidate('ui.render')
  }
  return result
})
""",body="""
return [text(E,'Latest 30 completed requests; counts from API reports.'),
  ...records.map((r,i)=>text(E,(i+1)+'. '+r.agent+' · '+r.model+'\\nRead '+(r.cache_read_input_tokens||0)+' · wrote '+(r.cache_creation_input_tokens||0)+' · uncached '+(r.input_tokens||0))),
  ...(records.length ? [] : [text(E,'No completed requests observed yet.')]), refresh]
""",access='Observes request token counts and model names in memory. No model calls.',check='No completed requests observed yet.')
add('tool-timing','Tool Timing','Session','Measure observed tool latency, call counts, and failures.','Find tools that slow down a session.',state='let stats = {}',hooks="""
on('tool.call', async ($, e, next) => {
  const t = await $.clock.now()
  try {
    const r = await next(e)
    const ms = Math.max(0, (await $.clock.now()) - t)
    const s = stats[e.tool] || {calls:0,ms:0,failed:0}
    stats[e.tool] = {calls:s.calls+1,ms:s.ms+ms,failed:s.failed+(r.deny||r.isError ? 1:0)}
    $.ui.invalidate('ui.render')
    return r
  } catch(error) { throw error }
})
""",body="""
return [text(E,'Tool                         calls   avg ms   failed',{bold:true}),
 ...Object.entries(stats).sort((a,b)=>b[1].ms-a[1].ms).map(([name,s])=>text(E,name.padEnd(28)+String(s.calls).padEnd(8)+Math.round(s.ms/s.calls).toString().padEnd(9)+s.failed)),
 ...(Object.keys(stats).length ? [] : [text(E,'No tool calls observed yet.')]),refresh]
""",access='Observes tool names, results, and clock; does not store arguments.',check='Tool                         calls   avg ms   failed')
add('error-inbox','Error Inbox','Session','Keep the last 30 failed or refused tool calls in one pane.','Revisit failures without searching the transcript.',state='let errors = []',hooks="""
on('tool.call', async ($, e, next) => {
 const r = await next(e)
 if(r.deny || r.isError) {
   errors = [...errors,{tool:e.tool,reason:clean(r.deny || (typeof r.result === 'string' ? r.result : 'Tool returned an error'),500)}].slice(-30)
   $.ui.invalidate('ui.render')
 }
 return r
})
""",body="""
return [text(E,errors.length+' recent failures',{bold:true}),
 ...errors.map((x,i)=>text(E,(i+1)+'. '+x.tool+' · '+x.reason,{color:'yellow'})),
 ...(errors.length ? []:[text(E,'No failed calls observed. Keep going.')]),
 E.Button({key:'clear',label:'Clear inbox',onPress:()=>{errors=[];$.ui.invalidate('ui.render')}})]
""",access='Keeps truncated tool error text in memory; may contain sensitive output.',check='0 recent failures')
add('edit-heatmap','Edit Heatmap','Session','Count successful Edit and Write calls by path.','See which files receive the most attention.',state='let files = {}',hooks="""
on('tool.call', {tool:['Edit','Write']}, async ($, e, next) => {
 const r = await next(e)
 if(!r.deny && !r.isError && typeof e.file_path === 'string') {
   if(Object.keys(files).length < 200 || files[e.file_path]) files[e.file_path]=(files[e.file_path]||0)+1
   $.ui.invalidate('ui.render')
 }
 return r
})
""",body="""
const sorted = Object.entries(files).sort((a,b)=>b[1]-a[1])
const max = sorted[0]?.[1] || 1
return [text(E,'Successful file tool calls; Bash edits are not counted.'),
 ...sorted.map(([path,n])=>text(E,'#'.repeat(Math.ceil(n/max*12)).padEnd(13)+n+'  '+path)),
 ...(sorted.length ? []:[text(E,'No successful file edits observed yet.')]),refresh]
""",access='Observes edited file paths; no content reads or persistence.',check='No successful file edits observed yet.')
add('turn-timeline','Turn Timeline','Session','Show duration, token totals, and interruption state per turn.','Compare long and short turns.',state='let turns = []',hooks="""
on('turn.complete', async ($, e, next) => {
 turns = [...turns,{duration:e.durationMs,aborted:e.isAborted,agent:e.agentId||'main',output:e.usage?.output_tokens||0}].slice(-30)
 $.ui.invalidate('ui.render')
 return next(e)
})
""",body="""
return [text(E,'Latest 30 observed turns',{bold:true}), ...turns.map((t,i)=>text(E,
 (i+1)+'. '+t.agent+' · '+(t.duration/1000).toFixed(1)+'s · '+t.output+' output tokens'+(t.aborted?' · interrupted':''))),
 ...(turns.length?[]:[text(E,'Complete a turn to begin the timeline.')]),refresh]
""",access='Observes turn durations and counts only; no answer storage.',check='Latest 30 observed turns')
add('agent-board','Agent Board','Session','Inspect the subagents reported by the session.','Keep track of delegated work without messaging anyone.',body="""
const agents = await $.agent.list()
return [text(E,'Subagents reported by this session',{bold:true}),
 ...agents.slice(0,40).map(a=>code(E,pretty(a),'json')),
 ...(agents.length?[]:[text(E,'No subagents currently reported.')]),refresh]
""",access='Reads agent metadata only. Does not spawn or message agents.',check='Subagents reported by this session')

# Git commands are argv-only, read-only, bounded, and requested by the user.
GIT = [
('branch-board','Branch Board','Inspect local branches, upstreams, and dirty files.','Choose a branch with current work in view.', ['status','--short','--branch'],['branch','-vv','--no-color'], '',''),
('staged-review','Staged Review','Review the staged diff before committing.','Check exactly what would go into your next commit.', ['diff','--cached','--stat'],['diff','--cached','--no-ext-diff','--no-textconv','--unified=2'], '', ''),
('commit-browser','Commit Browser','Browse the latest 20 commits with author and subject.','Find a recent change without leaving Claude Code.', ['log','-20','--date=short','--format=%h  %ad  %an%n    %s'],None,'',''),
('stash-browser','Stash Browser','List stashes and inspect a selected stash diff.','Recover the context of parked work without applying it.', ['stash','list','--format=%gd  %s'],['stash','show','--no-ext-diff','--no-textconv','--stat'], 'stash@{0}', 'stash reference'),
('worktree-map','Worktree Map','List worktree paths, branches, and locked states.','See where parallel work lives.', ['worktree','list','--porcelain'],None,'',''),
('conflict-radar','Conflict Radar','List unresolved paths and count conflict markers in tracked files.','Find remaining merge conflicts.', ['diff','--name-only','--diff-filter=U'],['grep','-n','-I','-E','^(<<<<<<< |=======|>>>>>>> )','--','.'], '', ''),
('blame-view','Blame View','Read authorship for the first 80 lines of a chosen tracked file.','Understand who last changed a line.', ['blame','--no-mailmap','-L','1,80','--'],None,'README.md','tracked file path'),
('ignore-check','Ignore Check','Explain which Git ignore rule matches a path.','Debug an unexpectedly ignored file.', ['check-ignore','-v','--no-index','--'],None,'dist/bundle.js','path to check'),
]
for id,title,desc,use,argv,argv2,default,label in GIT:
    state="let target = "+json.dumps(default)+"\nlet report = 'Open this pane to read Git state.'"
    load="""
async function load($) {
 try {
   const first = await $.process.run(ARGV, {timeoutMs:10000})
   report = (first.exitCode === 0 ? first.stdout || 'No matching entries.' : first.stderr || 'No matching entries (exit '+first.exitCode+').')
   SECOND
 } catch(error) { report = 'Git inspection failed: '+error.message }
 $.ui.invalidate('ui.render')
}
"""
    a=['git','--no-pager']+argv
    expr=json.dumps(a)
    if label and id != 'stash-browser': expr=expr+'.concat([safePath(target)])'
    if argv2:
        a2=['git','--no-pager']+argv2
        ex2=json.dumps(a2)+('.concat([target])' if id=='stash-browser' else '')
        second=f"const second = await $.process.run({ex2}, {{timeoutMs:10000}})\n report += '\\n\\n'+(second.stdout || second.stderr || 'No diff.')"
    else: second=''
    load=load.replace('ARGV',expr).replace('SECOND',second)
    if id=='stash-browser': load=load.replace('try {',"try {\n if(!/^stash@\\{\\d+\\}$/.test(target)) throw new Error('Use a stash reference such as stash@{0}.')")
    control="" if not label else f"""E.Input({{key:'target',label:{json.dumps(label)},value:target,submitLabel:'inspect',onSubmit:async(value)=>{{target=value;await load($)}}}}),"""
    add(id,title,'Git',desc,use,state=state+'\n'+load,command="if(e.args.trim()) target=e.args.trim()\nawait load($)",body=f"""
return [{control} code(E,report), E.Button({{key:'refresh',label:'Refresh Git state',hotkey:'r',plain:true,onPress:()=>load($)}})]
""",access='Runs read-only Git commands only when opened or refreshed. Git must be on PATH. No network, writes, or persistence.',sample=default,check='')

# Repository viewers.
READ = """
async function load($) {
 try {
  const path = safePath(target)
  const info = await $.fs.stat(path)
  if(info.size > 262144) throw new Error('File exceeds the 256 KiB viewer limit.')
  const source = await $.fs.read(path)
  report = transform(source)
 } catch(error) { report='Could not inspect file: '+error.message }
 $.ui.invalidate('ui.render')
}
"""
def viewer(id,title,desc,use,default,transform,lang='text',extra=''):
    add(id,title,'Repository',desc,use,state=f"let target={json.dumps(default)}\nlet report='Open a file to inspect it.'\n"+extra+'\n'+transform+'\n'+READ,command="if(e.args.trim()) target=e.args.trim()\nawait load($)",body=f"""
return [E.Input({{key:'target',label:'File',value:target,submitLabel:'open',onSubmit:async(value)=>{{target=value;await load($)}}}}),
 code(E,report,{json.dumps(lang)}),E.Button({{key:'refresh',label:'Read file again',onPress:()=>load($)}})]
""",access='Reads the chosen file (up to 256 KiB) on request. No writes, processes, network, or persistence.',sample=default)

add('file-tree','File Tree','Repository','Browse one directory at a time with clickable folders.','Explore a project without flooding the transcript.',state="let target='.'\nlet listing=[]\nlet report=''\n"+"""
async function load($) {
 try { listing=(await $.fs.list(safePath(target))).slice(0,100); report='' }
 catch(error) { listing=[];report=error.message }
 $.ui.invalidate('ui.render')
}
""",command="if(e.args.trim()) target=e.args.trim()\nawait load($)",body="""
return [E.Input({key:'target',label:'Directory',value:target,submitLabel:'browse',onSubmit:async(v)=>{target=v;await load($)}}),
 text(E,report || 'Up to 100 entries. Symlinks are shown but not followed by buttons.'),
 ...listing.map((f,i)=>f.kind==='dir'&&!f.isLink ? E.Button({key:'dir-'+i,label:'[dir] '+f.name,plain:true,onPress:async()=>{target=target.replace(/\\/$/,'')+'/'+f.name;await load($)}}):text(E,(f.isLink?'[link] ':'[file] ')+f.name+'  '+(f.size||0)+' B')),
 E.Button({key:'refresh',label:'Refresh directory',onPress:()=>load($)})]
""",access='Lists the directory the user chooses. Does not recursively walk or read file content.',sample='.')
viewer('package-scripts','Package Scripts','List npm scripts and package identity without running them.','Find available project commands.','package.json',"""
function transform(source) {
 const p=JSON.parse(source)
 return (p.name||'Unnamed package')+' @ '+(p.version||'?')+'\\n\\n'+entries(p.scripts).map(([k,v])=>k+'\\n  '+v).join('\\n')
}
""")
viewer('dependency-table','Dependency Table','Inspect dependency groups from a package manifest.','Check declared versions before upgrading.','package.json',"""
function transform(source) {
 const p=JSON.parse(source)
 return ['dependencies','devDependencies','peerDependencies','optionalDependencies'].map(k=>k+' ('+entries(p[k]).length+')\\n'+entries(p[k]).map(([n,v])=>n.padEnd(28)+v).join('\\n')).join('\\n\\n')
}
""")
add('todo-finder','TODO Finder','Repository','Find TODO, FIXME, and HACK notes in tracked files.','Build a quick backlog from the code already in your repo.',state="let report=''\n"+"""
async function load($) {
 try {
  const r=await $.process.run(['git','--no-pager','grep','-n','-I','-E','TODO|FIXME|HACK','--','.'],{timeoutMs:10000})
  report=r.exitCode===0?r.stdout:(r.exitCode===1?'No TODO, FIXME, or HACK markers in tracked files.':r.stderr)
 } catch(error) { report=error.message }
 $.ui.invalidate('ui.render')
}
""",command='await load($)',body="return [code(E,report),E.Button({key:'refresh',label:'Search tracked files',onPress:()=>load($)})]",access='Runs read-only git grep on request. Tracked files only; requires Git.')
viewer('markdown-map','Markdown Map','Build a heading outline with source line numbers.','Navigate a long README or design document.','README.md',"""
function transform(source) {
 let fence=null
 return source.split('\\n').flatMap((line,i)=>{
  const f=line.match(/^\\s{0,3}(`{3,}|~{3,})/)
  if(f) { if(!fence) fence=f[1][0];else if(fence===f[1][0])fence=null;return [] }
  if(fence)return []
  const m=line.match(/^(#{1,6})\\s+(.+)/)
  return m ? [(i+1).toString().padStart(4)+'  '+'  '.repeat(m[1].length-1)+m[2].replace(/\\s+#+\\s*$/,'')] : []
 }).join('\\n') || 'No ATX headings outside fenced code.'
}
""")
viewer('json-browser','JSON Browser','Summarize top-level JSON keys with types and a formatted preview.','Inspect a local API response or configuration.','package.json',"""
function transform(source) {
 const p=JSON.parse(source)
 return entries(p).map(([k,v])=>k+' · '+(Array.isArray(v)?'array['+v.length+']':v===null?'null':typeof v)).join('\\n')+'\\n\\n'+pretty(p)
}
""",'json')
viewer('csv-table','CSV Table','Preview quoted CSV fields, row counts, and column headers.','Read an exported dataset without launching a spreadsheet.','data.csv',"""
export function parseCSV(source) {
 const rows=[];let row=[],cell='',quoted=false
 for(let i=0;i<source.length;i++) {
  const c=source[i]
  if(c==='"') { if(quoted&&source[i+1]==='"'){cell+='"';i++}else if(quoted || cell==='')quoted=!quoted;else throw new Error('Quote inside unquoted CSV field.') }
  else if(c===','&&!quoted){row.push(cell);cell=''}
  else if(c==='\\n'&&!quoted){row.push(cell.replace(/\\r$/,''));rows.push(row);row=[];cell=''}
  else cell+=c
 }
 if(quoted)throw new Error('CSV has an unclosed quoted field.')
 if(cell || row.length){row.push(cell.replace(/\\r$/,''));rows.push(row)}
 return rows
}
function transform(source) {
 const rows=parseCSV(source)
 if(!rows.length)return 'Empty CSV.'
 return Math.max(0,rows.length-1)+' data rows · '+rows[0].length+' columns\\n\\n'+rows.slice(0,26).map(r=>r.map(c=>c.replace(/\\n/g,' ↵ ').slice(0,24).padEnd(25)).join(' | ')).join('\\n')
}
""")
viewer('log-viewer','Log Viewer','Show the last 60 lines of a small local log with an optional filter.','Inspect a development log on demand.','app.log',"""
function transform(source) {
 const lines=source.split('\\n').filter(l=>!filter || l.toLowerCase().includes(filter.toLowerCase()))
 return lines.length+' matching lines · showing last 60\\n\\n'+lines.slice(-60).join('\\n')
}
""",extra="let filter='' ")
# Add a filter control specifically to the log viewer.
MODS[-1]['body']=MODS[-1]['body'].replace('code(E,report,',"E.Input({key:'filter',label:'Contains',value:filter,submitLabel:'filter',onSubmit:async(v)=>{filter=v;await load($)}}), code(E,report,")
viewer('env-example','Env Example','List variable names and missing placeholders in an example env file.','Review setup requirements without reading your real .env.','.env.example',"""
function transform(source) {
 return source.split('\\n').flatMap((line,i)=>{
  const m=line.match(/^\\s*(?:export\\s+)?([A-Za-z_][A-Za-z0-9_]*)\\s*=\\s*(.*)$/)
  return m ? [(i+1)+': '+m[1]+' · '+(m[2].trim()?'example value provided':'value needed')] : []
 }).join('\\n') || 'No variable assignments found.'
}
""")
MODS[-1]['state']=MODS[-1]['state'].replace('const path = safePath(target)',"const path = safePath(target)\n  if(!/(?:^|\\/)\\.?env(?:\\.[\\w-]+)*\\.(example|sample|template)$/.test(path)) throw new Error('Choose an env example, sample, or template file; real env files are refused.')")
MODS[-1]['state']=MODS[-1]['state'].replace("const info = await $.fs.stat(path)","const info = await $.fs.stat(path)\n  if(info.isLink)throw new Error('Symlink env example files are refused.')")
MODS[-1]['access']='Reads only paths named env example, sample, or template (up to 256 KiB). Displays variable names and placeholder presence; no values.'
add('file-compare','File Compare','Repository','Compare two small text files by line without editing either.','Check config or fixture differences.',state="let left='before.txt',right='after.txt',report=''\n"+"""
async function load($) {
 try {
 const a=await $.fs.stat(safePath(left)),b=await $.fs.stat(safePath(right))
 if(a.size>65536||b.size>65536)throw new Error('Each file must be at most 64 KiB.')
 const x=(await $.fs.read(left)).split('\\n'),y=(await $.fs.read(right)).split('\\n')
 const diff=[]
 for(let i=0;i<Math.max(x.length,y.length);i++) if(x[i]!==y[i])diff.push((i+1)+': - '+(x[i]??'[missing]')+'\\n   + '+(y[i]??'[missing]'))
 report=diff.length?diff.length+' differing line positions (positional comparison)\\n\\n'+diff.slice(0,100).join('\\n'):'Files are identical.'
 } catch(error){report=error.message}
 $.ui.invalidate('ui.render')
}
""",command='await load($)',body="""
return [E.Input({key:'left',label:'Left file',value:left,submitLabel:'set',onSubmit:async(v)=>{left=v;await load($)}}),
 E.Input({key:'right',label:'Right file',value:right,submitLabel:'compare',onSubmit:async(v)=>{right=v;await load($)}}),
 code(E,report),E.Button({key:'refresh',label:'Compare again',onPress:()=>load($)})]
""",access='Reads two explicitly chosen text files up to 64 KiB each. Positional comparison, not an edit-distance diff.')

# Persistent, per-workspace collections. Each item has a separate store key.
BOARDS=[
('scratchpad','Scratchpad','Save short notes beside your conversation.','Keep temporary findings out of your prompt.','Note','Remember to verify keyboard navigation','Save notes','plain'),
('task-board','Task Board','Add tasks and toggle done status.','Track the small jobs that appear during a session.','Task','Verify empty states on mobile','Tasks','toggle'),
('decision-log','Decision Log','Record dated engineering decisions.','Remember why you chose an approach.','Decision','Keep all analytics collection opt-in','Decision history','dated'),
('snippet-shelf','Snippet Shelf','Save and copy short code or command snippets.','Keep useful one-liners at hand.','Snippet','git log --oneline -10','Saved snippets','copy'),
('link-shelf','Link Shelf','Save labeled HTTP and HTTPS reference links.','Keep docs for the current project visible.','Label | URL','Mods docs | https://code.claude.com/docs/en/plugins/mods/overview','Reference links','links'),
('prompt-shelf','Prompt Shelf','Save reusable prompts and put one into the composer as a draft.','Reuse a review or debugging prompt without auto-submitting it.','Prompt','Review this patch for accessibility and edge cases','Reusable prompts','draft'),
('release-checklist','Release Checklist','Keep a persistent checklist for a release.','Track review, checks, and release tasks in one place.','Check','Confirm build passes on a clean checkout','Release checks','toggle'),
('handoff-notes','Handoff Notes','Keep a dated list of progress and next steps, then copy it.','Leave a useful handoff for the next session.','Handoff note','Done: API parser. Next: verify empty responses.','Handoff notes','handoff'),
]
for id,title,desc,use,label,sample,heading,kind in BOARDS:
    state="""
let prefix=''
let items=[]
let message=''
async function load($) {
 const keys=(await $.store.keys()).filter(k=>k.startsWith(prefix)).sort().slice(-100)
 items=[]
 for(const key of keys) {
  const item=await $.store.get(key)
  if(item && typeof item.text==='string')items.push({...item,key})
 }
 $.ui.invalidate('ui.render')
}
async function save($, value) {
 try {
  const content=bounded(value.trim(),4000)
  if(!content)return
  VALIDATE
  const date=new Date(await $.clock.now()).toISOString()
  const key=prefix+date+'-'+crypto.randomUUID()
  await $.store.set(key,{text:content,done:false,date})
  message='Saved locally.'
  await load($)
 } catch(error){message=error.message;$.ui.invalidate('ui.render')}
}
"""
    valid="""const parts=content.split('|');const u=new URL(parts.slice(1).join('|').trim());if(!['http:','https:'].includes(u.protocol)||u.username||u.password)throw new Error('Use Label | https://example.com without credentials.')""" if kind=='links' else ''
    state=state.replace('VALIDATE',valid)
    button="text(E,item.text)"
    if kind=='toggle': button="E.Button({key:'toggle-'+i,label:(item.done?'[x] ':'[ ] ')+clean(item.text,300),plain:true,onPress:async()=>{const latest=await $.store.get(item.key);if(latest)await $.store.set(item.key,{...latest,done:!latest.done});await load($)}})"
    if kind=='copy': button="row(E,[code(E,item.text),E.Button({key:'copy-'+i,label:'Copy',onPress:async()=>{const r=await $.ui.copy({text:item.text});message=r.isCopied?'Copied.':'Clipboard unavailable.';$.ui.invalidate('ui.render')}})])"
    if kind=='draft': button="row(E,[text(E,item.text),E.Button({key:'draft-'+i,label:'Draft',onPress:async()=>{const r=await $.prompt.fill({text:item.text});message=r.isFilled?'Draft placed in composer; review and send it yourself.':'Composer is busy; draft was not placed.';$.ui.invalidate('ui.render')}})])"
    if kind=='links': button="E.Link({label:clean(item.text.split('|')[0].trim(),200),href:item.text.split('|').slice(1).join('|').trim()})"
    if kind in ['dated','handoff']: button="text(E,item.date.slice(0,16).replace('T',' ')+' UTC\\n'+item.text)"
    copyall="E.Button({key:'copy-all',label:'Copy handoff',onPress:async()=>{const r=await $.ui.copy({text:items.map(x=>x.date+' '+x.text).join('\\n')});message=r.isCopied?'Handoff copied.':'Clipboard unavailable.';$.ui.invalidate('ui.render')}})," if kind=='handoff' else ''
    add(id,title,'Workspace',desc,use,state=state,start="prefix='workspace:'+encodeURIComponent(e.cwd)+':item:'\nawait load($)",command='await load($)\nif(e.args.trim()) await save($,e.args)',body=f"""
return [text(E,{json.dumps(heading)}+' · '+items.length+' items',{{bold:true}}),
 E.Input({{key:'entry',label:{json.dumps(label)},value:'',placeholder:'Type and press Enter',submitLabel:'save',onSubmit:(v)=>save($,v)}}),
 ...items.map((item,i)=>E.Box({{flexDirection:'column',children:[{button},E.Button({{key:'delete-'+i,label:'Delete',plain:true,dimColor:true,onPress:async()=>{{await $.store.delete(item.key);await load($)}}}})]}})),
 {copyall} text(E,message || 'Saved per workspace. Refresh to see changes from other sessions.',{{dimColor:true}}),
 E.Button({{key:'refresh',label:'Reload saved items',onPress:()=>load($)}})]
""",access='Stores user-entered items in this plugin’s local store, partitioned by workspace path. Each item has a separate key. No file writes or network.'+(' Uses the clipboard.' if kind in ['copy','handoff'] else '')+(' Fills a draft in the composer on button press; does not submit a prompt.' if kind=='draft' else ''),sample=sample,check=heading+' · 0 items')

# Pure interactive utilities. No tools, subprocesses, remote calls, or persistent input.
def utility(id,title,desc,use,fields,transform,initial='',extra='',buttons=''):
    state='\n'.join('let '+name+'='+json.dumps(default) for name,label,default in fields)+'\nlet output='+json.dumps(initial)+'\n'+extra+'\n'+transform
    controls=[]
    for name,label,default in fields:
        controls.append(f"E.Input({{key:{json.dumps(name)},label:{json.dumps(label)},value:clean({name}),submitLabel:'apply',onSubmit:async(v)=>{{{name}=v;await calculate($)}}}})")
    state+="""
async function calculate($) {
 try { output=await transform() } catch(error){output='Invalid input: '+error.message}
 $.ui.invalidate('ui.render')
}
"""
    body='return ['+',\n'.join(controls)+',code(E,output),'+buttons+"E.Button({key:'copy',label:'Copy result',onPress:async()=>{const r=await $.ui.copy({text:output});if(!r.isCopied)$.ui.toast('Clipboard unavailable.')}})]"
    add(id,title,'Utilities',desc,use,state=state,command='await calculate($)',body=body,access='Works on the text you enter, in memory. Uses the clipboard on request. No files, processes, network, persistence, or model calls.',check=initial)

utility('regex-lab','Regex Lab','Test a regular expression against text and see matched ranges.','Debug a pattern before putting it in code.',[('pattern','Pattern','APP-\\d+'),('flags','Flags','g'),('source','Text','Fix APP-123 before APP-456')],"""
function transform() {
 bounded(source,2000);bounded(pattern,160)
 if(!/^[gimsuy]*$/.test(flags))throw new Error('Flags must be g, i, m, s, u, or y.')
 // Use a predictable subset rather than executing arbitrary backtracking patterns.
 let inClass=false,repeat=0
 for(let i=0;i<pattern.length;i++) {
  const c=pattern[i]
  if(c==='\\\\') {
   const escape=pattern[++i]
   if(/[1-9k]/.test(escape||''))throw new Error('Backreferences are refused.')
   continue
  }
  if(c==='[')inClass=true
  else if(c===']')inClass=false
  else if(!inClass) {
   if('()|'.includes(c))throw new Error('Groups and alternation are outside the supported subset.')
   if('*+?{'.includes(c) && ++repeat>1)throw new Error('Use at most one repetition operator in this lab.')
  }
 }
 const re=new RegExp(pattern,flags.includes('g')?flags:flags+'g')
 const found=Array.from(source.matchAll(re)).slice(0,40)
 return found.length+' matches\\n\\n'+found.map(m=>'['+m.index+', '+(m.index+m[0].length)+') '+m[0]).join('\\n')
}
""")
MODS[-1]['body']=MODS[-1]['body'].replace('return [',"return [text(E,'Supported subset: character classes, anchors, escapes, and one repetition; no groups or alternation.'),",1)
utility('json-format','JSON Format','Validate and pretty-print JSON without touching a file.','Clean up a copied API response.',[('source','JSON','{"name":"mods","count":50,"open":true}')],"function transform(){return pretty(JSON.parse(bounded(source)))}")
utility('url-lab','URL Lab','Inspect URL components and decoded query parameters locally.','Debug a callback URL without visiting it.',[('source','URL','https://example.com/callback?state=hello%20world&mode=preview#result')],"""
function transform(){
 const u=new URL(bounded(source))
 return pretty({protocol:u.protocol,hostname:u.hostname,port:u.port||'(default)',path:u.pathname,fragment:u.hash,query:Array.from(u.searchParams.entries()),hasCredentials:!!(u.username||u.password)})
}
""")
utility('base64-lab','Base64 Lab','Encode UTF-8 text or decode strict Base64.','Inspect a payload without sending it anywhere.',[('mode','Mode: encode or decode','encode'),('source','Text / Base64','Hello, mods!')],"""
function transform(){
 bounded(source)
 if(mode==='encode')return new TextEncoder().encode(source).toBase64()
 if(mode==='decode')return new TextDecoder('utf-8',{fatal:true}).decode(Uint8Array.fromBase64(source,{lastChunkHandling:'strict'}))
 throw new Error('Mode must be encode or decode.')
}
""")
utility('time-lab','Time Lab','Convert Unix seconds, milliseconds, or an ISO date to UTC.','Compare timestamps from logs and APIs.',[('source','Timestamp','2026-10-03T09:00:00Z')],"""
function transform(){
 const s=source.trim()
 const n=/^-?\\d+$/.test(s)?Number(s):null
 const d=new Date(n===null?s:(Math.abs(n)<1e11?n*1000:n))
 if(!Number.isFinite(d.getTime()))throw new Error('Use Unix seconds/milliseconds or an ISO date.')
 return 'UTC: '+d.toISOString()+'\\nUnix seconds: '+Math.floor(d.getTime()/1000)+'\\nUnix milliseconds: '+d.getTime()
}
""")
utility('hash-lab','Hash Lab','Calculate SHA-256, SHA-384, or SHA-512 for UTF-8 text.','Compare a checksum for a short string.',[('algorithm','Algorithm','SHA-256'),('source','Text','hello')],"""
async function transform(){
 if(!['SHA-256','SHA-384','SHA-512'].includes(algorithm))throw new Error('Use SHA-256, SHA-384, or SHA-512.')
 const digest=await crypto.subtle.digest(algorithm,new TextEncoder().encode(bounded(source)))
 return algorithm+'\\n'+Array.from(new Uint8Array(digest),x=>x.toString(16).padStart(2,'0')).join('')
}
""")
utility('color-lab','Color Lab','Convert hex colors and measure contrast against a background.','Check a foreground and background pair while designing.',[('foreground','Foreground hex','#86efac'),('background','Background hex','#0f172a')],"""
function rgb(s){if(!/^#[0-9a-f]{6}$/i.test(s))throw new Error('Use six-digit #RRGGBB colors.');return [1,3,5].map(i=>parseInt(s.slice(i,i+2),16))}
function luminance(c){return c.map(x=>{const v=x/255;return v<=0.04045?v/12.92:((v+0.055)/1.055)**2.4}).reduce((s,x,i)=>s+x*[0.2126,0.7152,0.0722][i],0)}
function transform(){
 const a=rgb(foreground),b=rgb(background),x=luminance(a),y=luminance(b)
 const ratio=(Math.max(x,y)+0.05)/(Math.min(x,y)+0.05)
 return 'Foreground RGB: '+a.join(', ')+'\\nBackground RGB: '+b.join(', ')+'\\nContrast: '+ratio.toFixed(2)+':1\\n'+(ratio>=4.5?'Meets 4.5:1 threshold for normal text.':'Below 4.5:1 threshold for normal text.')
}
""")
utility('uuid-lab','UUID Lab','Generate up to 20 random UUID v4 values locally.','Make IDs for fixtures and examples.',[('count','Count (1–20)','3')],"""
function transform(){const n=Number(count);if(!Number.isInteger(n)||n<1||n>20)throw new Error('Count must be an integer from 1 to 20.');return Array.from({length:n},()=>crypto.randomUUID()).join('\\n')}
""",buttons="E.Button({key:'generate',label:'Generate new IDs',onPress:()=>calculate($)}),")
utility('text-counter','Text Counter','Count words, lines, Unicode code points, and UTF-8 bytes.','Check text lengths before publishing or sending a payload.',[('source','Text','Build small tools. Make them useful.')],"""
function transform(){bounded(source);return pretty({words:source.trim()?source.trim().split(/\\s+/).length:0,lines:source?source.split('\\n').length:0,codePoints:Array.from(source).length,utf8Bytes:new TextEncoder().encode(source).length})}
""")
add('ascii-flipbook','ASCII Flipbook','Utilities','Play a local text animation whose frames are separated by a form feed.','Preview ASCII storyboards in a pane without a video decoder.',state="""
let target='animation.txt',frames=['( o.o )\\n > ^ <','( -.- )\\n > ^ <'],index=0,playing=false,report='Built-in two-frame demo. Open a text file to load your own.'
async function load($){
 try {
  const p=safePath(target),s=await $.fs.stat(p)
  if(s.size>131072)throw new Error('Animation must be at most 128 KiB.')
  const f=(await $.fs.read(p)).split('\\f')
  if(f.length>120||f.some(x=>x.length>4000))throw new Error('Use at most 120 frames of 4,000 characters each.')
  frames=f;index=0;report=f.length+' frames loaded.'
 } catch(error){report=error.message}
 $.ui.invalidate('ui.render')
}
""",start="$.clock.every(500,()=>{if(playing){index=(index+1)%frames.length;$.ui.invalidate('ui.render')}})",command='if(e.args.trim()){target=e.args.trim();await load($)}',body="""
return [E.Input({key:'target',label:'Text animation',value:target,submitLabel:'load',onSubmit:async(v)=>{target=v;await load($)}}),
 text(E,'Frame '+(index+1)+' / '+frames.length,{bold:true}),code(E,frames[index]),
 row(E,[E.Button({key:'play',label:playing?'Pause':'Play',hotkey:'p',plain:true,onPress:()=>{playing=!playing;$.ui.invalidate('ui.render')}}),
 E.Button({key:'next',label:'Next frame',hotkey:'n',plain:true,onPress:()=>{index=(index+1)%frames.length;$.ui.invalidate('ui.render')}})]),text(E,report)]
""",access='Reads a chosen text animation (up to 128 KiB), uses a 2 fps timer. No ffmpeg, audio, video decoding, or network.',sample='animation.txt',check='Frame 1 / 2')

# Workflow mods.
add('focus-clock','Focus Clock','Workflow','Run a 25-minute focus countdown with pause, reset, and a toast.','Keep a work interval visible during a long task.',state='let remaining=25*60, running=false, last=0',start="""
$.clock.every(1000,async()=>{
 if(!running)return
 const now=await $.clock.now()
 remaining=Math.max(0,remaining-(now-last)/1000);last=now
 if(remaining===0){running=false;$.ui.toast('Focus interval finished. Take a break.')}
 $.ui.invalidate('ui.render')
})
""",body="""
const seconds=Math.ceil(remaining)
return [text(E,Math.floor(seconds/60).toString().padStart(2,'0')+':'+(seconds%60).toString().padStart(2,'0'),{bold:true,color:'cyan'}),
 text(E,running?'Focus interval is running.':'Ready or paused.'),
 row(E,[E.Button({key:'start',label:running?'Pause':'Start',hotkey:'s',plain:true,onPress:async()=>{const now=await $.clock.now();if(running)remaining=Math.max(0,remaining-(now-last)/1000);last=now;running=!running;$.ui.invalidate('ui.render')}}),
 E.Button({key:'reset',label:'Reset 25 minutes',onPress:()=>{running=false;remaining=1500;$.ui.invalidate('ui.render')}})])]
""",access='Uses a local clock and a completion toast. No files, network, or persistence.',check='25:00')
add('stopwatch','Stopwatch','Workflow','Time a task with start, pause, and lap markers.','Measure a manual debugging or review session.',state='let elapsed=0,started=0,running=false,laps=[]',start="$.clock.every(1000,()=>{if(running)$.ui.invalidate('ui.render')})",body="""
const n=elapsed+(running?(await $.clock.now())-started:0)
return [text(E,(n/1000).toFixed(1)+' seconds',{bold:true,color:'cyan'}),
 row(E,[E.Button({key:'start',label:running?'Pause':'Start',onPress:async()=>{const now=await $.clock.now();if(running)elapsed+=now-started;else started=now;running=!running;$.ui.invalidate('ui.render')}}),
 E.Button({key:'lap',label:'Lap',onPress:async()=>{const n=elapsed+(running?(await $.clock.now())-started:0);laps=[...laps,n].slice(-20);$.ui.invalidate('ui.render')}}),
 E.Button({key:'reset',label:'Reset',onPress:()=>{elapsed=0;running=false;laps=[];$.ui.invalidate('ui.render')}})]),
 ...laps.map((x,i)=>text(E,'Lap '+(i+1)+' · '+(x/1000).toFixed(1)+'s'))]
""",access='Uses a local clock; laps live in memory.',check='0.0 seconds')
add('test-ledger','Test Ledger','Workflow','Record likely test, lint, and build commands and their tool status.','Keep validation attempts in view, with honest evidence boundaries.',state='let runs=[]',hooks="""
on('tool.call',{tool:'Bash'},async($,e,next)=>{
 const r=await next(e)
 if(/\\b(test|pytest|vitest|jest|tsc|lint|build)\\b/.test(e.command)){
  runs=[...runs,{command:clean(e.command,240),status:r.deny?'refused':r.isError?'tool error':'tool completed'}].slice(-30)
  $.ui.invalidate('ui.render')
 }
 return r
})
""",body="""
return [text(E,'Command detection is heuristic. Tool completion does not prove tests passed.'),
 ...runs.map((r,i)=>text(E,(i+1)+'. '+r.status+'\\n'+r.command)),
 ...(runs.length?[]:[text(E,'No likely validation commands observed yet.')]),refresh]
""",access='Observes Bash command strings and tool status in memory. Does not execute commands.',check='No likely validation commands observed yet.')
add('command-history','Command History','Workflow','Keep the last 40 Bash command strings and copy one for reuse.','Find a command Claude ran earlier in this session.',state='let commands=[]',hooks="""
on('tool.call',{tool:'Bash'},async($,e,next)=>{
 const r=await next(e)
 commands=[...commands,clean(e.command,2000)].slice(-40)
 $.ui.invalidate('ui.render')
 return r
})
""",body="""
return [text(E,'Observed Bash commands; may include private arguments.'),
 ...commands.map((c,i)=>row(E,[text(E,(i+1)+'. '+c),E.Button({key:'copy-'+i,label:'Copy',onPress:async()=>{const r=await $.ui.copy({text:c});if(!r.isCopied)$.ui.toast('Clipboard unavailable.')}})])),
 ...(commands.length?[]:[text(E,'No Bash commands observed yet.')]),refresh]
""",access='Observes Bash command arguments in memory; may include secrets. Clipboard only on request. No persistence.',check='No Bash commands observed yet.')
add('scope-watch','Scope Watch','Workflow','Warn when observed file edits leave a chosen path prefix.','Notice scope creep during a focused change.',state="let prefix='src/',warnings=[]",hooks="""
on('tool.call',{tool:['Edit','Write']},async($,e,next)=>{
 const r=await next(e)
 const cwd=(await $.session.cwd()).replace(/\\/$/,'')+'/'
 const path=e.file_path.startsWith(cwd)?e.file_path.slice(cwd.length):e.file_path
 if(!r.deny&&!r.isError&&!path.startsWith(prefix)){
  warnings=[...warnings,clean(path,500)].slice(-30)
  $.ui.toast('Edited outside watched prefix: '+clean(path,120))
  $.ui.invalidate('ui.render')
 }
 return r
})
""",body="""
return [E.Input({key:'prefix',label:'Expected path prefix',value:prefix,submitLabel:'watch',onSubmit:(v)=>{prefix=v.trim();warnings=[];$.ui.invalidate('ui.render')}}),
 text(E,'Advisory only. Bash and MCP edits are not detected.'),
 ...warnings.map(p=>text(E,p,{color:'yellow'})),
 ...(warnings.length?[]:[text(E,'No out-of-prefix edits observed.')]),refresh]
""",access='Observes Edit/Write paths, reads session cwd, and toasts on out-of-prefix edits. Does not block calls.',check='No out-of-prefix edits observed.')
add('read-only-mode','Read-only Mode','Workflow','Toggle a reminder guard that refuses built-in mutating tools and Bash.','Use a session for inspection with an extra visible guard.',state='let enabled=false,blocked=0',hooks="""
on('tool.call',{tool:['Edit','Write','NotebookEdit','Bash']},async($,e,next)=>{
 if(!enabled)return next(e)
 blocked+=1;$.ui.invalidate('ui.render')
 return {deny:'Read-only Mode is enabled. Use inspection tools or ask the user to disable it in /read-only-mode.'}
}).catch(async()=>({deny:'Read-only Mode guard failed; this call was refused.'}))
""",body="""
return [text(E,enabled?'Guard ON':'Guard OFF',{bold:true,color:enabled?'green':'yellow'}),
 text(E,'Blocks Edit, Write, NotebookEdit, and all Bash calls. MCP and other mods are outside this reminder guard.'),
 text(E,blocked+' calls refused'),
 E.Button({key:'toggle',label:enabled?'Disable guard':'Enable guard',onPress:()=>{enabled=!enabled;$.ui.invalidate('ui.render')}})]
""",access='Refuses selected tool.call events when manually enabled. No permission approvals. Not a security boundary; other tools/mods can write.',check='Guard OFF')

assert len(MODS)==50, len(MODS)

MODULE = '''import { clean, text, code, row, frame, bar, pretty, bounded, entries, safePath } from './ui.js'
const ID = __ID__
__STATE__
export function register(on) {
  on('session.start', async ($, e, next) => {
    __START__
    await $.command.register({name:ID, description:__DESC__, immediate:true, argumentHint:__HINT__})
    return next(e)
  })
  on('command.run', {command:__ID__}, async ($, e) => {
    __COMMAND__
    await $.ui.open({id:ID,title:__TITLE__,focus:true,closeOnEscape:true})
    return {}
  })
  __HOOKS__
  on('ui.render', {component:'Pane'}, async ($, e, next) => {
    if(e.requestId !== ID) return next(e)
    const E = $.ui.resolve(e)
    try {
      const body = await draw($, E)
      return frame(E,__TITLE__,__DESC__,body)
    } catch(error) {
      return frame(E,__TITLE__,'Unable to inspect this data.',[text(E,error.message,{color:'yellow'}),E.Button({key:'refresh',label:'Refresh',onPress:()=>$.ui.invalidate('ui.render')})])
    }
  })
}
async function draw($, E) {
  const refresh = E.Button({key:'refresh',label:'Refresh',hotkey:'r',plain:true,onPress:()=>$.ui.invalidate('ui.render')})
__BODY__
}
'''
# Direct engine calls only in the entry module, including top-level draw/load.
for m in MODS:
    d=ROOT/'mods'/m['id']
    for sub in ['.claude-plugin','hooks','tests']:(d/sub).mkdir(parents=True,exist_ok=True)
    manifest=dict(name=m['id'],version='1.0.0',description=m['description'],author={'name':'Yash Thakker'},license='MIT',homepage='https://github.com/whyashthakker/awesome-claude-code-mods')
    (d/'.claude-plugin/plugin.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (d/'hooks/hooks.json').write_text(json.dumps({'modules':['./register.js']},indent=2)+'\n')
    source=MODULE
    for key,value in dict(ID=json.dumps(m['id']),TITLE=json.dumps(m['title']),DESC=json.dumps(m['description']),HINT=json.dumps('[path]' if m['category'] in ['Git','Repository'] else '[entry]' if m['category']=='Workspace' else ''),STATE=m['state'],START=m['start'],COMMAND=m['command'],HOOKS=m['hooks'],BODY=m['body']).items():source=source.replace('__'+key+'__',value)
    (d/'hooks/register.js').write_text('\n'.join(line.rstrip() for line in source.splitlines())+'\n')
    (d/'hooks/ui.js').write_text(UI)
    (d/'LICENSE').write_text((ROOT/'LICENSE').read_text())
    readme=f'''# {m['title']}

{m['description']}

**Use it when:** {m['use']}

![{m['title']} render preview](../../assets/screenshots/{m['id']}.png)

*Screenshot of this mod's render tree in the fixture preview, with sample data. This is not a capture of the Claude Code application. [How previews are made](../../docs/SCREENSHOTS.md).*

## Install and open

```sh
claude plugin marketplace add whyashthakker/awesome-claude-code-mods
claude plugin install {m['id']}@awesome-claude-code-mods
```

Run `/reload-plugins` in an existing session, then `/{m['id']}`. Use Tab and Enter to operate controls; Esc closes the pane. Terminal and Desktop Code tab supported; pane UI is unavailable in `claude -p` and the VS Code chat panel.

Try the source without installing:

```sh
claude --plugin-dir ./mods/{m['id']}
```

'''
    if m['sample']:readme+=f"Example: open `/{m['id']}` and enter `{m['sample']}` in its input.\n\n"
    readme+=f'''## Access and behavior

{m['access']}

Module variables reset on hot reload. Diagnostic history begins when the mod loads and lasts until reload or process exit; it does not reconstruct earlier activity. Workspace collections persist in Claude Code's local plugin store and reload when reopened. Deleting an item removes only that item's store key. Collections show the latest 100 items; concurrent changes to the same item use last-write-wins behavior. All display output is bounded; viewers may truncate long content to 9,000 characters. Relative file paths and Git commands use the session working directory.

## Verify

Tested with Claude Code **2.1.288**. Minimum documented mods version: **2.1.287**. The API can change; validate against your installed version.

```sh
claude plugin validate mods/{m['id']} --strict
claude plugin test mods/{m['id']}
```

Tests cover plugin commands, pane isolation, both UI surfaces, and the behavior described in `tests/register.test.ts`. Drawing tests validate element trees; they do not verify pixels painted by the native apps. [Validation details](../../docs/VALIDATION.md).

MIT licensed. No runtime packages or build step required.
'''
    if m['category'] not in ['Session','Workflow']:
        readme=readme.replace('Diagnostic history begins when the mod loads and lasts until reload or process exit; it does not reconstruct earlier activity. ','')
    # Keep only relevant lifecycle notes in each README.
    if m['category']=='Workspace':
        readme=readme.replace('Module variables reset on hot reload. Diagnostic history begins when the mod loads and lasts until reload or process exit; it does not reconstruct earlier activity. ','')
    else:
        readme=readme.replace("Workspace collections persist in Claude Code's local plugin store and reload when reopened. Deleting an item removes only that item's store key. Collections show the latest 100 items; concurrent changes to the same item use last-write-wins behavior. ",'')
    (d/'README.md').write_text(readme)
public=[{k:m[k] for k in ['id','title','category','description','use','access','sample']} for m in MODS]
(ROOT/'catalog.json').write_text(json.dumps(public,indent=2)+'\n')
marketplace={'name':'awesome-claude-code-mods','owner':{'name':'Yash Thakker'},'metadata':{'description':'50 independent MIT-licensed Claude Code mods','version':'1.0.0'},'plugins':[{'name':m['id'],'source':'./mods/'+m['id'],'description':m['description'],'version':'1.0.0','category':m['category'].lower()} for m in MODS]}
(ROOT/'.claude-plugin/marketplace.json').write_text(json.dumps(marketplace,indent=2)+'\n')
print('Built',len(MODS),'standalone mods')
