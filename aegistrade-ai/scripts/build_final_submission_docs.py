"""Build final-report and presentation Word documents; no network or inference."""
from pathlib import Path
from docx import Document
from scripts import build_design_and_viva_docs as b

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'


def architecture():
    from matplotlib.patches import Circle
    b.ASSETS=DOCS/'assets';b.ASSETS.mkdir(parents=True,exist_ok=True)
    fig,ax=b.canvas(12.8)
    def number(x,y,n,color='#d85f52'):
        ax.add_patch(Circle((x,y),.18,facecolor=color,edgecolor='white',linewidth=1.2,zorder=8))
        ax.text(x,y,str(n),ha='center',va='center',fontsize=9,weight='bold',color='white',zorder=9)
    def line(a,c,label='',rad=0): b.arrow(ax,a,c,label,rad)

    # User, API and model-facing guardrail boundary.
    b.box(ax,.25,11.75,2.0,.72,'Reviewer','C0/C2 • dates • capital\nconsent • approve','#e9f2e8')
    b.box(ax,2.55,11.75,4.9,.72,'Simplified Streamlit UI + FastAPI','fixed risk policy • auth • allowance • progress • resume')
    b.box(ax,7.75,11.75,2.0,.72,'Input / output guards','typed requests • cutoff\ninjection scan • scrub','#fde8e5')
    line((2.25,12.1),(2.55,12.1));line((7.45,12.1),(7.75,12.1));number(.42,12.42,1)

    b.box(ax,.25,10.55,2.9,.72,'C0 baseline','four-route ROUTER • zero LLM','#e9f2e8')
    b.box(ax,3.55,10.55,2.9,.72,'C2 supervisor plan','market → strategy → critic','#fff1df')
    b.box(ax,6.85,10.55,2.9,.72,'C1 single-agent baseline','same case / tools / budget','#fff1df')
    for x in (1.7,5,8.3):line((5,11.75),(x,11.27))
    number(.42,11.18,2)

    # Specialist layer, visually matching the faculty diagram's central agent row.
    b.box(ax,.25,9.15,2.9,.92,'Market specialist','historical snapshot • company pack\noptional bounded dated-web fallback','#fff1df')
    b.box(ax,3.55,9.15,2.9,.92,'Strategy specialist','policy RAG • code route\ntyped action + citations','#fff1df')
    b.box(ax,6.85,9.15,2.9,.92,'Independent critic','own observations • accept/reject\nno execution permission','#fff1df')
    line((5,10.55),(1.7,10.07),rad=.08)
    line((3.15,9.61),(3.55,9.61));line((6.45,9.61),(6.85,9.61))
    number(.42,9.93,3);number(3.72,9.93,4);number(7.02,9.93,5)

    b.box(ax,.25,7.85,9.5,.72,'Pre/post-tool hooks','per-agent allow-list + call/context budget  •  trace + provenance + secret scrub  •  untrusted evidence stays data','#fde8e5')
    for x in (1.7,5,8.3):line((x,9.15),(x,8.57))
    number(.42,8.47,6)

    # Tool plane.
    tools=[(.25,'Market MCP','snapshot + evidence'),(2.2,'Knowledge MCP','RAG + passage IDs'),
           (4.15,'Strategy MCP','approved route'),(6.1,'Records MCP','frozen lessons'),
           (8.05,'Dated web','historical fallback')]
    for x,title,detail in tools:b.box(ax,x,6.65,1.7,.72,title,detail,'#eaf1f8')
    for x in (1.1,3.05,5,6.95,8.9):line((5,7.85),(x,7.37))

    # Evidence and state plane.
    stores=[(.25,'OHLCV cache','frozen universes\ncompleted daily bars'),(2.2,'Evidence library','filings / releases\ndates + hashes'),
            (4.15,'Hybrid index','BM25 + vectors\nRRF + reranker'),(6.1,'Lesson store','review / reject\nfreeze / retrieve'),
            (8.05,'Run state','JSON / SQLite\ncheckpoint + trace')]
    for x,title,detail in stores:b.box(ax,x,5.25,1.7,.85,title,detail,'#edf4fa')
    for x in (1.1,3.05,5,6.95,8.9):line((x,6.65),(x,6.1))

    b.box(ax,.25,3.85,9.5,.82,'Typed hand-offs + deterministic validation and financial controls','schema • cutoff • citation • route • adverse evidence  |  whole shares • fixed fees • slippage • stops • targets • capacity','#fde8e5')
    line((5,5.25),(5,4.67));number(.42,4.57,7)

    b.box(ax,.25,2.45,4.45,.85,'Historical portfolio replay','upfront-approved rules • candidate pool\nlater-open simulated fills • no forced final sale','#e9f2e8')
    b.box(ax,5.3,2.45,4.45,.85,'WAITING_HUMAN decision','C2 BUY / SELL • approve / reject + rationale\nno repeated C2 call • separate decision ledger','#e9f2e8')
    line((3.3,3.85),(2.48,3.3));line((6.7,3.85),(7.52,3.3));number(.42,3.17,8)

    b.box(ax,.25,1.15,9.5,.72,'Simulated broker / historical fill engine → immutable audit ledger','cash • holdings • decisions • 10-session outcome • citations • model/tool usage • failures • checkpoints • P&L','#edf4fa')
    line((2.48,2.45),(3.4,1.87));line((7.52,2.45),(6.6,1.87))
    b.box(ax,.25,.12,2.9,.55,'E1–E4 evaluation','C0/C1/C2 • security • memory')
    b.box(ax,3.55,.12,2.9,.55,'Prometheus + Grafana','latency • calls • errors • outcomes')
    b.box(ax,6.85,.12,2.9,.55,'CI + Docker','evaluation gate • reproducible demo')
    for x in (1.7,5,8.3):line((5,1.15),(x,.67))
    number(.42,.78,9)
    return b.save(fig,'final_architecture_v027')


def main():
    image=architecture();figures={'final_architecture':image}
    report=b.build('FINAL_PROJECT_REPORT',figures,'FINAL CAPSTONE PROJECT REPORT',version='0.31.0',document_date='14 November 2026')
    old=b.DOCS;b.DOCS=ROOT
    try:presentation=b.build('FINAL_PRESENTATION_README',{},'FINAL PRESENTATION & DEMO GUIDE',version='0.31.0',document_date='14 November 2026')
    finally:b.DOCS=old
    print(report);print(presentation)
    assert len(Document(report).paragraphs)>40
    assert len(Document(report).inline_shapes)>=1


if __name__=='__main__':main()
