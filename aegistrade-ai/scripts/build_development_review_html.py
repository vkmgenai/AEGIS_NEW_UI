"""Build a standalone browser editor for the 20 development review cases."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "evaluation" / "agentic_candidates_20261118_v2"
SOURCE = PACKET / "agentic_development_20_REVIEW_TEMPLATE.jsonl"
OUTPUT = PACKET / "KARTHIKA_DEVELOPMENT_REVIEW_20.html"


def compact(text: str, limit: int = 1800) -> str:
    value = " ".join(str(text or "").split())
    return value[:limit] + ("…" if len(value) > limit else "")


def main() -> None:
    cases = [json.loads(line) for line in SOURCE.read_text().splitlines() if line.strip()]
    payload = []
    for case in cases:
        pack_path = ROOT / case["evidence_pack"]["relative_path"]
        pack = json.loads(pack_path.read_text())
        documents = []
        for doc in pack.get("documents", []):
            documents.append({
                "id": doc.get("id"),
                "kind": doc.get("kind"),
                "title": doc.get("title"),
                "published_at": doc.get("published_at"),
                "publisher": doc.get("publisher"),
                "source_url": doc.get("source_url"),
                "excerpt": compact(doc.get("text")),
            })
        payload.append({**case, "review_evidence_documents": documents})

    encoded = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.replace("__CASE_DATA__", encoded)
    OUTPUT.write_text(html, encoding="utf-8")
    print(OUTPUT)


TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AegisTrade — Karthika development review</title>
<style>
:root{--navy:#102a56;--blue:#245bc1;--pale:#eef5ff;--line:#cbd8ec;--ink:#17233b;--muted:#5f6f89;--good:#137a4d;--warn:#9b6300;--bad:#b4232c}
*{box-sizing:border-box} body{margin:0;background:#f4f7fc;color:var(--ink);font:15px/1.5 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
header{background:linear-gradient(120deg,var(--navy),var(--blue));color:white;padding:22px 28px;position:sticky;top:0;z-index:5;box-shadow:0 3px 12px #17376b44}
header h1{margin:0 0 4px;font-size:24px}.sub{opacity:.86}.wrap{max-width:1250px;margin:auto;padding:22px}
.progressbox,.card{background:white;border:1px solid var(--line);border-radius:14px;box-shadow:0 3px 12px #17376b12}.progressbox{padding:16px;margin-bottom:18px}
.bar{height:12px;background:#dce7f7;border-radius:9px;overflow:hidden;margin:8px 0}.bar>div{height:100%;background:linear-gradient(90deg,#2e6bd4,#22a274);width:0}
.layout{display:grid;grid-template-columns:240px 1fr;gap:18px}.sidebar{padding:12px;max-height:calc(100vh - 190px);overflow:auto}.casebtn{width:100%;text-align:left;border:0;border-radius:9px;padding:9px;margin:3px 0;background:#edf3fd;color:var(--ink);cursor:pointer}.casebtn.active{background:var(--blue);color:white}.casebtn.done:after{content:" ✓";color:var(--good);font-weight:700}.casebtn.active.done:after{color:white}
.main{padding:22px}.titleline{display:flex;justify-content:space-between;gap:12px;align-items:start}.tag{display:inline-block;padding:4px 9px;border-radius:12px;background:#e8effc;color:#244d96;font-size:12px;font-weight:650}
.metrics{display:grid;grid-template-columns:repeat(4,minmax(120px,1fr));gap:10px;margin:18px 0}.metric{background:var(--pale);border-radius:10px;padding:10px}.metric b{display:block;font-size:17px}.metric span{font-size:12px;color:var(--muted)}
label{font-weight:650;display:block;margin:13px 0 5px}select,input,textarea{width:100%;font:inherit;border:1px solid #aebed7;border-radius:8px;padding:9px;background:white}textarea{min-height:95px;resize:vertical}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}.check{display:flex;gap:9px;align-items:center;margin-top:16px}.check input{width:auto}.check label{margin:0}
details{border:1px solid var(--line);border-radius:9px;margin:8px 0;background:#fbfdff}summary{cursor:pointer;padding:11px;font-weight:650}.doc{padding:0 13px 13px}.docmeta{color:var(--muted);font-size:13px}.excerpt{white-space:pre-wrap;background:#f3f6fb;padding:10px;border-radius:8px;max-height:220px;overflow:auto}.actions{display:flex;flex-wrap:wrap;gap:9px;margin-top:18px}button.action{border:0;border-radius:8px;padding:10px 15px;background:var(--blue);color:white;font-weight:650;cursor:pointer}button.secondary{background:#e5edf9;color:#17376b}.status{padding:10px;border-radius:8px;margin-top:12px;display:none}.status.good{display:block;background:#e4f6ed;color:#0d6840}.status.bad{display:block;background:#fde9ea;color:#922029}
.help{background:#fff8df;border:1px solid #efd590;padding:12px;border-radius:9px;margin-bottom:15px}.small{font-size:13px;color:var(--muted)}a{color:#1f57b7}@media(max-width:850px){.layout{grid-template-columns:1fr}.sidebar{max-height:220px}.metrics{grid-template-columns:repeat(2,1fr)}.grid2{grid-template-columns:1fr}}
</style>
</head>
<body>
<header><h1>AegisTrade — development case review</h1><div class="sub">20 blinded cases · reviewer: Karthika · no model outputs · browser autosave</div></header>
<div class="wrap">
 <div class="progressbox"><b id="progressText">0 of 20 completed</b><div class="bar"><div id="progressBar"></div></div><div class="small">Your work is saved in this browser. Export JSONL before changing browser or clearing site data.</div></div>
 <div class="layout">
  <aside class="card sidebar" id="caseList"></aside>
  <main class="card main">
   <div class="help"><b>Decision rule:</b> inspect the technical snapshot and dated evidence. Choose the expected strategy, decide whether insufficient/adverse evidence should block it, and explain why. Do not use model outputs or future returns.</div>
   <div id="editor"></div>
  </main>
 </div>
</div>
<script>
const original=__CASE_DATA__;
const storageKey='aegistrade-dev-review-20261118-v2';
let saved={}; try{saved=JSON.parse(localStorage.getItem(storageKey)||'{}')}catch(e){}
let cases=original.map(x=>{const copy=JSON.parse(JSON.stringify(x)); delete copy.review_evidence_documents; return Object.assign(copy,saved[x.id]||{})});
let current=0;
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const docsFor=id=>original.find(x=>x.id===id).review_evidence_documents||[];
function complete(c){return ['EMA_TREND','EMA_PULLBACK','RSI_REVERSION','BREAKOUT','SMC','NONE'].includes(c.expected?.strategy)&&typeof c.expected?.blocked==='boolean'&&['ACCEPT','CORRECT','QUARANTINE'].includes(c.review_decision)&&String(c.review_rationale||'').trim().length>=20&&c.reviewer==='Karthika'&&c.reviewed_at_utc&&c.independently_reviewed===true}
function persist(){const out={};cases.forEach(c=>out[c.id]=c);localStorage.setItem(storageKey,JSON.stringify(out));renderList();updateProgress()}
function updateProgress(){const n=cases.filter(complete).length;document.getElementById('progressText').textContent=`${n} of ${cases.length} completed`;document.getElementById('progressBar').style.width=`${100*n/cases.length}%`}
function renderList(){const box=document.getElementById('caseList');box.innerHTML=cases.map((c,i)=>`<button class="casebtn ${i===current?'active':''} ${complete(c)?'done':''}" onclick="go(${i})">${i+1}. ${esc(c.input.symbol)} · ${esc(c.input.date)}<br><span class="small">${esc(c.input.regime)}</span></button>`).join('')}
function option(value,label,current){return `<option value="${value}" ${current===value?'selected':''}>${label}</option>`}
function render(){const c=cases[current],x=c.input,docs=docsFor(c.id);document.getElementById('editor').innerHTML=`
 <div class="titleline"><div><span class="tag">${esc(c.family)}</span><h2>${esc(x.symbol)} — ${esc(x.date)}</h2></div><div class="small">Case ${current+1} of ${cases.length}<br>${esc(c.id)}</div></div>
 <div class="metrics">
  <div class="metric"><b>${Number(x.Close).toFixed(2)}</b><span>Close</span></div><div class="metric"><b>${Number(x.RSI14).toFixed(2)}</b><span>RSI14</span></div>
  <div class="metric"><b>${Number(x.ADX14).toFixed(2)}</b><span>ADX14</span></div><div class="metric"><b>${Number(x.ATR14).toFixed(2)}</b><span>ATR14</span></div>
  <div class="metric"><b>${Number(x.EMA20).toFixed(2)}</b><span>EMA20</span></div><div class="metric"><b>${Number(x.EMA50).toFixed(2)}</b><span>EMA50</span></div>
  <div class="metric"><b>${x.PriorHigh==null?'—':Number(x.PriorHigh).toFixed(2)}</b><span>Prior high</span></div><div class="metric"><b>${x.PullbackRecent?'Yes':'No'}</b><span>Recent pullback</span></div>
 </div>
 <h3>Dated evidence (${docs.length} documents)</h3><div class="small">Evidence window: ${esc(c.evidence_pack.window_start)} to ${esc(c.evidence_pack.decision_at)} · Pack: ${esc(c.evidence_pack.relative_path)}</div>
 ${docs.map((d,i)=>`<details><summary>${i+1}. ${esc(d.title||d.kind||d.id)}</summary><div class="doc"><div class="docmeta">${esc(d.kind)} · ${esc(d.published_at)} · ${esc(d.publisher)} · ID ${esc(d.id)}</div>${d.source_url?`<p><a href="${esc(d.source_url)}" target="_blank" rel="noreferrer">Open original source</a></p>`:''}<div class="excerpt">${esc(d.excerpt)}</div></div></details>`).join('')}
 <h3>Human label</h3>
 <div class="grid2"><div><label>Expected strategy</label><select id="strategy">${option('','Choose…',c.expected?.strategy)}${option('EMA_TREND','EMA Trend',c.expected?.strategy)}${option('EMA_PULLBACK','EMA Pullback',c.expected?.strategy)}${option('RSI_REVERSION','RSI Reversion',c.expected?.strategy)}${option('BREAKOUT','Breakout',c.expected?.strategy)}${option('SMC','SMC',c.expected?.strategy)}${option('NONE','None / abstain',c.expected?.strategy)}</select></div>
 <div><label>Should this case be blocked?</label><select id="blocked">${option('','Choose…',typeof c.expected?.blocked==='boolean'?String(c.expected.blocked):'')}${option('false','No — allow recommendation',typeof c.expected?.blocked==='boolean'?String(c.expected.blocked):'')}${option('true','Yes — block/abstain',typeof c.expected?.blocked==='boolean'?String(c.expected.blocked):'')}</select></div></div>
 <div class="grid2"><div><label>Review decision</label><select id="decision">${option('','Choose…',c.review_decision)}${option('ACCEPT','Accept candidate label',c.review_decision)}${option('CORRECT','Correct candidate label',c.review_decision)}${option('QUARANTINE','Quarantine ambiguous case',c.review_decision)}</select></div><div><label>Reviewer</label><input id="reviewer" value="${esc(c.reviewer||'Karthika')}"></div></div>
 <label>Review rationale (minimum 20 characters)</label><textarea id="rationale" placeholder="Explain the technical route and how the dated evidence supports, blocks or does not adversely affect it.">${esc(c.review_rationale)}</textarea>
 <label>Conflict disclosure / uncertainty</label><textarea id="conflict" placeholder="Leave blank if none.">${esc(c.conflict_disclosure)}</textarea>
 <div class="check"><input type="checkbox" id="reviewed" ${c.independently_reviewed?'checked':''}><label for="reviewed">I personally reviewed this case without using model output or future returns.</label></div>
 <div class="actions"><button class="action" onclick="saveCase()">Save case</button><button class="action secondary" onclick="previous()">← Previous</button><button class="action secondary" onclick="next()">Next →</button><button class="action secondary" onclick="validateAll()">Validate all</button><button class="action" onclick="downloadJSONL()">Export completed JSONL</button></div><div id="status" class="status"></div>`}
function go(i){current=i;renderList();render();window.scrollTo({top:0,behavior:'smooth'})}function previous(){if(current>0)go(current-1)}function next(){if(current<cases.length-1)go(current+1)}
function saveCase(){const c=cases[current],blocked=document.getElementById('blocked').value;c.expected={strategy:document.getElementById('strategy').value,blocked:blocked===''?null:blocked==='true'};c.review_decision=document.getElementById('decision').value;c.review_rationale=document.getElementById('rationale').value.trim();c.conflict_disclosure=document.getElementById('conflict').value.trim();c.reviewer=document.getElementById('reviewer').value.trim();c.independently_reviewed=document.getElementById('reviewed').checked;if(c.independently_reviewed&&!c.reviewed_at_utc)c.reviewed_at_utc=new Date().toISOString();if(!c.independently_reviewed)c.reviewed_at_utc='';persist();show(complete(c)?'Case saved and complete.':'Case saved, but required fields remain. Complete cases show a check mark.',complete(c))}
function show(msg,good){const s=document.getElementById('status');s.className='status '+(good?'good':'bad');s.textContent=msg}
function errors(){const e=[];cases.forEach((c,i)=>{if(!complete(c))e.push(`Case ${i+1} (${c.id}) is incomplete or invalid.`)});return e}
function validateAll(){saveCase();const e=errors();show(e.length?`${e.length} cases need attention. First: ${e[0]}`:'All 20 cases are complete and ready to export.',!e.length)}
function downloadJSONL(){saveCase();const e=errors();if(e.length){show(`Export blocked: ${e.length} cases are incomplete.`,false);return}const clean=cases.map(c=>{const x=JSON.parse(JSON.stringify(c));delete x.review_evidence_documents;return x});const blob=new Blob([clean.map(x=>JSON.stringify(x)).join('\n')+'\n'],{type:'application/x-ndjson'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='agentic_development_20_REVIEWED_KARTHIKA.jsonl';a.click();URL.revokeObjectURL(a.href);show('Completed JSONL exported. Keep the original template unchanged.',true)}
renderList();render();updateProgress();
</script>
</body></html>'''


if __name__ == "__main__":
    main()
