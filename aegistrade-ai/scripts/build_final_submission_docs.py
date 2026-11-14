"""Build final-report and presentation Word documents; no network or inference."""
from pathlib import Path
from docx import Document
from scripts import build_design_and_viva_docs as b

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'


def architecture():
    b.ASSETS=DOCS/'assets';b.ASSETS.mkdir(parents=True,exist_ok=True)
    fig,ax=b.canvas(10.4)
    b.box(ax,.25,9.25,9.5,.75,'Streamlit UI → FastAPI','Auth • consent • plans • status / resume • exact human review')
    b.box(ax,.25,7.95,9.5,.75,'Locked point-in-time case','Frozen universe • completed OHLCV • dated filing/news cutoff • no future data')
    b.arrow(ax,(5,9.25),(5,8.7))
    b.box(ax,.25,6.25,2.8,1.05,'C0 ROUTER','EMA trend / pullback\nRSI reversion / breakout','#e9f2e8')
    b.box(ax,3.6,6.25,2.8,1.05,'C1 E1 baseline','One ReAct agent\nsame tools + budget','#fff1df')
    b.box(ax,6.95,6.25,2.8,1.05,'C2 specialist team','Market → strategy → critic\nfour routes + SMC','#fff1df')
    for x in (1.65,5,8.35):b.arrow(ax,(5,7.95),(x,7.3))
    b.box(ax,.25,4.45,4.55,1.05,'Hybrid RAG + dated evidence','BM25 + vectors + RRF + reranker\nsource / date / passage IDs')
    b.box(ax,5.2,4.45,4.55,1.05,'Scoped FastMCP tools + hooks','Permission / budget before tool\ntrace / scrub after tool')
    b.arrow(ax,(5,6.25),(2.5,5.5));b.arrow(ax,(8.35,6.25),(7.5,5.5))
    b.box(ax,.25,2.65,9.5,1.05,'Typed hand-offs + deterministic financial controls','Citations / adverse evidence / route • quantity / fees / slippage / stops / targets')
    b.arrow(ax,(2.5,4.45),(4.1,3.7));b.arrow(ax,(7.5,4.45),(5.9,3.7))
    b.box(ax,.25,.85,4.55,1.0,'Historical replay','Upfront-approved rules\nlater-open simulated fills','#e9f2e8')
    b.box(ax,5.2,.85,4.55,1.0,'Supervised simulated action','Approve / edit / reject exact hash\nfinal freshness + risk checks','#e9f2e8')
    b.arrow(ax,(3.2,2.65),(2.5,1.85));b.arrow(ax,(6.8,2.65),(7.5,1.85))
    ax.text(5,.25,'Audit/checkpoints → reviewed lessons → E1–E4 harness → Prometheus/Grafana → CI',ha='center',fontsize=9.5,color=b.NAVY)
    return b.save(fig,'final_architecture_v027')


def main():
    image=architecture();figures={'final_architecture':image}
    report=b.build('FINAL_PROJECT_REPORT',figures,'FINAL CAPSTONE PROJECT REPORT',version='0.27.0',document_date='14 November 2026')
    old=b.DOCS;b.DOCS=ROOT
    try:presentation=b.build('FINAL_PRESENTATION_README',{},'FINAL PRESENTATION & DEMO GUIDE',version='0.27.0',document_date='14 November 2026')
    finally:b.DOCS=old
    print(report);print(presentation)
    assert len(Document(report).paragraphs)>40
    assert len(Document(report).inline_shapes)>=1


if __name__=='__main__':main()
