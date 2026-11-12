"""Build the fresh v0.19.1 design/viva/demo set; no inference or runtime mutations.

Run: .venv/bin/python -m scripts.build_current_version_documents
Markdown sources and PNG/Word outputs live under docs/current_v0_19_1.
"""
from pathlib import Path
from scripts import build_design_and_viva_docs as b
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'/'current_v0_19_1'


def figures():
    b.ASSETS=OUT/'assets';b.ASSETS.mkdir(parents=True,exist_ok=True)
    result={}
    fig,ax=b.canvas(9)
    b.box(ax,.25,7.7,9.5,.85,'Streamlit UI → FastAPI','Settings • reviewer token • explicit inference / replay authorization')
    b.box(ax,.25,6.25,9.5,.9,'Code screening + dated evidence','OHLCV / regime / ranking • official company packs • policy RAG')
    b.arrow(ax,(5,7.7),(5,7.15))
    b.box(ax,.25,4.8,9.5,.9,'C2: market → strategy → critic → code guard','Six normal inference calls • seven tool calls • read-only MCP')
    b.arrow(ax,(5,6.25),(5,5.7))
    b.box(ax,.25,2.95,4.45,1.15,'Historical portfolio','Upfront approved replay rules\nAutomatic historical fills / exits','#fff1df')
    b.box(ax,5.25,2.95,4.5,1.15,'Supervised order','Completed C2 → code proposal\nExact human approval → final gates','#fff1df')
    b.arrow(ax,(2.5,4.8),(2.5,4.1));b.arrow(ax,(7.5,4.8),(7.5,4.1))
    b.box(ax,.25,1.2,4.45,1.05,'Cash / holdings / ledger','Marked end holdings; no forced sale\nTechnical reference + passive context','#e9f2e8')
    b.box(ax,5.25,1.2,4.5,1.05,'Simulated broker + audit','Payload hash / request ID\nFreshness / risk / reconciliation','#e9f2e8')
    b.arrow(ax,(2.5,2.95),(2.5,2.25));b.arrow(ax,(7.5,2.95),(7.5,2.25))
    ax.text(5,.45,'Reviewed frozen lessons are optional context; code controls risk and permissions.',ha='center',fontsize=10,color=b.NAVY)
    result['current_architecture']=b.save(fig,'current_architecture')

    fig,ax=b.canvas(9.7)
    b.box(ax,.3,8.35,9.4,.9,'Code supervisor: lock case / purpose / budget','START → plan; no additional supervisor LLM call')
    rows=[(6.6,'Market specialist','Call 1: request snapshot + company evidence\nApplication runs 2 MCP reads → Call 2: typed assessment'),
          (4.6,'Strategy specialist','Call 3: request route + policy\nApplication runs 2 MCP reads → Call 4: typed route / action'),
          (2.6,'Independent critic','Call 5: request company + route + policy\nApplication runs 3 MCP reads → Call 6: accept / reject')]
    for y,title,detail in rows:b.box(ax,.3,y,9.4,1.15,title,detail)
    b.arrow(ax,(5,8.35),(5,7.75));b.arrow(ax,(5,6.6),(5,5.75));b.arrow(ax,(5,4.6),(5,3.75))
    b.box(ax,.3,.7,9.4,1.1,'Final deterministic guard → eligible result or BLOCK','Citations / dated pack / route / purpose / critic / frozen memory','#e9f2e8')
    b.arrow(ax,(5,2.6),(5,1.8))
    ax.text(5,.2,'Early market stop • bounded field correction • shared ceiling 8 calls / 16 tools',ha='center',fontsize=9,color=b.NAVY)
    result['current_orchestration']=b.save(fig,'current_orchestration')

    fig,ax=b.canvas(9.8)
    rows=[(8.4,'Create frozen run','Data / policy / prompt / model fingerprints; optional memory manifest'),
          (6.9,'Session OPEN','Queued sales before buys; research revalidation; code sizing and cash'),
          (5.4,'Protection during daily bar','Opening gaps first; stop / target; conservative ambiguous-bar ordering'),
          (3.9,'Completed CLOSE','Mark equity; strategy exits; due C2 holding review; next-session stop raises'),
          (2.4,'Code stock selection → dated ENTRY C2','Friday/pre-gap waits for fresh next-trading-close review'),
          (.9,'Checkpoint → next session or terminal result','End marks unsold holdings; no forced end-date liquidation')]
    for y,title,detail in rows:b.box(ax,.3,y,9.4,.95,title,detail)
    for y in [8.4,6.9,5.4,3.9,2.4]:b.arrow(ax,(5,y),(5,y-.55))
    ax.text(5,.2,'Budget / provider / user pause → saved phase → explicitly authorized resume',ha='center',fontsize=9.5,color=b.NAVY)
    result['current_portfolio']=b.save(fig,'current_portfolio')

    fig,ax=b.canvas(8.6)
    b.box(ax,.25,6.6,2.95,1.35,'Policy RAG','BM25 + embeddings\nRRF + cross-encoder\nExact IDs / dated references')
    b.box(ax,3.55,6.6,2.95,1.35,'Company archive','Symbol / cutoff pack\nDated official filings\nMateriality source windows')
    b.box(ax,6.85,6.6,2.9,1.35,'Reviewed memory','Completed source cases\nHuman accept / reject\nFreeze ID / hash / dates')
    b.box(ax,.25,4.5,9.5,1.05,'Bounded evidence + conditional reminders → specialists','Sources have different authority; none grants broker-write permission')
    for x in [1.72,5.02,8.3]:b.arrow(ax,(x,6.6),(x,5.55))
    b.box(ax,.25,2.65,9.5,1.05,'Memory guard: later evaluation or labelled development replay','Maximum 3 lessons / 2400 characters; evidence gets context priority','#fff1df')
    b.arrow(ax,(5,4.5),(5,3.7))
    b.box(ax,.25,.8,9.5,1.05,'Saved research: full audit + selected IDs + frozen manifest','No P&L-derived buy labels • no model-weight fine-tuning','#e9f2e8')
    b.arrow(ax,(5,2.65),(5,1.85))
    result['current_rag_memory']=b.save(fig,'current_rag_memory')

    fig,ax=b.canvas(8.8)
    rows=[(7.4,'Completed C2 experiment with accepted critic','Validate source / data / policy / route provenance before proposal'),
          (5.9,'Code proposal → risk / compliance validation','Whole-share sizing / stop / cash / exposure; typed exact payload'),
          (4.4,'Human interrupt: approve / edit / reject','Edit invalidates old hash and requires validation + new approval'),
          (2.9,'Final execution checks','Research / payload / quote freshness / deviation / expiry / risk'),
          (1.4,'Simulated broker → request-ID audit / reconciliation','Timeout after commit: reconcile before any retry; no live exchange')]
    for y,title,detail in rows:b.box(ax,.3,y,9.4,.95,title,detail)
    for y in [7.4,5.9,4.4,2.9]:b.arrow(ax,(5,y),(5,y-.55))
    ax.text(5,.55,'The order workflow reuses completed research; it is not another six-call C2 cycle.',ha='center',fontsize=9.5,color=b.NAVY)
    result['current_supervised']=b.save(fig,'current_supervised')
    return result


def main():
    b.DOCS=OUT
    art=figures()
    for stem,title in [
        ('AegisTrade_v0_19_1_Project_Design_and_Orchestration','v0.19.1 • DESIGN & ORCHESTRATION'),
        ('AegisTrade_v0_19_1_Viva_Questions_and_Answers','v0.19.1 • FRESH VIVA BANK'),
        ('AegisTrade_v0_19_1_UI_Demo_and_Test_Guide','v0.19.1 • UI DEMO & TEST GUIDE')]:
        path=b.build(stem,art,title);print(path.relative_to(ROOT),path.stat().st_size)

if __name__=='__main__':main()
