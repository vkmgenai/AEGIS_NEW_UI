"""Build the current separate capstone Word documents without cloud calls.

Uses python-docx and matplotlib. Markdown files remain the editable source.
"""
from __future__ import annotations
import os
import re
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/tmp/aegis-mpl')
os.environ.setdefault('XDG_CACHE_HOME', '/tmp/aegis-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from scripts.build_viva_guide import append_markdown

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
ASSETS = DOCS / 'assets'
NAVY = '#173b5d'


def canvas(height=8):
    fig, ax = plt.subplots(figsize=(10, height))
    ax.set(xlim=(0, 10), ylim=(0, height)); ax.axis('off')
    fig.patch.set_facecolor('white')
    return fig, ax


def box(ax, x, y, w, h, title, detail='', color='#eaf1f8'):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle='round,pad=0.035,rounding_size=0.07',
        facecolor=color, edgecolor='#426682', linewidth=1.2))
    ax.text(x+w/2, y+h*(.68 if detail else .5), title, ha='center', va='center',
            fontsize=11, weight='bold', color=NAVY)
    if detail:
        ax.text(x+w/2, y+h*.28, detail, ha='center', va='center',
                fontsize=9.5, color='#263b4d', linespacing=1.4)


def arrow(ax, a, b, label='', rad=0):
    ax.annotate('', xy=b, xytext=a, arrowprops={
        'arrowstyle':'->', 'color':'#526d82', 'lw':1.5,
        'connectionstyle': f'arc3,rad={rad}'})
    if label:
        ax.text((a[0]+b[0])/2, (a[1]+b[1])/2+.08, label,
                fontsize=8.5, color=NAVY, ha='center',
                bbox={'facecolor':'white','edgecolor':'none','pad':1})


def save(fig, name):
    path=ASSETS/f'design_{name}.png'
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return path


def diagrams():
    ASSETS.mkdir(exist_ok=True)
    result={}
    fig,ax=canvas(8.5)
    box(ax,.3,7.3,9.4,.85,'Streamlit → FastAPI: consent and bounded work','Local evidence / state • Codex or OpenRouter • no live broker')
    box(ax,.3,5.85,9.4,.85,'Historical evidence: bars + policy + dated company filings','Locked symbol / cutoff • deterministic indicators and ranking')
    box(ax,.3,4.4,9.4,.85,'C2: market → strategy → critic → code validation','ENTRY or HOLDING_REVIEW • cited ENTER / HOLD / EXIT')
    arrow(ax,(5,7.3),(5,6.7));arrow(ax,(5,5.85),(5,5.25))
    box(ax,.3,2.75,4.3,1.0,'C2 historical portfolio','Upfront rule approval\nCash / positions / automatic fills','#fff1df')
    box(ax,5.35,2.75,4.35,1.0,'Supervised single action','Exact human interrupt\nPayload hash / SQLite','#fff1df')
    arrow(ax,(3,4.4),(2.45,3.75));arrow(ax,(7,4.4),(7.55,3.75))
    box(ax,.3,.8,4.3,1.0,'Mark unsold holdings at end','Realized + unrealized P&L\nTechnical reference alongside','#e9f2e8')
    box(ax,5.35,.8,4.35,1.0,'Final gates → simulator audit','Research / freshness / risk\nIdempotency and recovery','#e9f2e8')
    arrow(ax,(2.45,2.75),(2.45,1.8));arrow(ax,(7.55,2.75),(7.55,1.8))
    arrow(ax,(.3,3.2),(.3,4.75),rad=-.5)
    result['architecture']=save(fig,'architecture')

    fig,ax=canvas(6.8)
    for y,title,detail in [
        (5.65,'Current Nifty 50 snapshot → frozen top 20','Pre-period Close × Volume liquidity proxy; membership bias disclosed'),
        (4.1,'Completed-session evidence → eligibility filters','History • liquidity • volatility • entry • cash / capacity'),
        (2.55,'Rank eligible candidates → record audit','70% strength + 20% liquidity + 10% lower ATR fraction')]:
        box(ax,.35,y,9.3,.95,title,detail)
    arrow(ax,(5,5.65),(5,5.05));arrow(ax,(5,4.1),(5,3.5))
    box(ax,.35,.55,4.3,1.05,'Technical-only baseline','Next-open fills / fees / slippage\nZero generation calls','#e9f2e8')
    box(ax,5.3,.55,4.35,1.05,'Selected case → C2','Historical portfolio loop or\nseparate human-reviewed action','#fff1df')
    arrow(ax,(3,2.55),(2.5,1.6));arrow(ax,(7,2.55),(7.5,1.6))
    result['selection']=save(fig,'selection')

    fig,ax=canvas(8.3)
    box(ax,.4,7.1,9.2,.85,'Code supervisor: plan + locked historical case','No planner generation call; shared ceiling = 8 requests')
    stages=[(5.15,'Market specialist','Requests 1–2','market_snapshot + company_evidence\nTechnical regime + cited company assessment'),
            (3.3,'Strategy specialist','Requests 3–4','Policy + current route + position context\nCited ENTER / HOLD / EXIT'),
            (1.45,'Compliance critic','Requests 5–6','Policy + strategy + company observations\nEvidence critique → accept or reject')]
    for y,title,count,detail in stages:
        box(ax,.4,y,9.2,1.15,title+'  |  '+count,detail)
    arrow(ax,(5,7.1),(5,6.3));arrow(ax,(5,5.15),(5,4.45));arrow(ax,(5,3.3),(5,2.6))
    box(ax,.4,.05,9.2,.7,'Code guard → save citations, usage and both evidence hashes',color='#e9f2e8')
    arrow(ax,(5,1.45),(5,.75))
    ax.text(5,6.65,'Each pair: LLM chooses tool(s) → MCP executes → LLM interprets',ha='center',fontsize=9,color=NAVY,
            bbox={'facecolor':'white','edgecolor':'none','pad':2})
    result['llm']=save(fig,'llm')

    fig,ax=canvas(7.5)
    items=[(6.2,'81 source-labelled policy / reference passages','Stable IDs • authority • publication / retrieval / indexed dates'),
           (4.7,'Historical availability filter + query rewrite','Case date locked; external future references withheld'),
           (3.2,'BM25 + 384-dimensional MiniLM retrieval','Chroma persists vectors; model weights cached locally'),
           (1.7,'Reciprocal Rank Fusion → cross-encoder reranking','Shortlist scored jointly with query; return passage IDs'),
           (.2,'MCP search_policy → C2 grounding → code checks','Observed citations + project-policy authority + current corpus hash')]
    for y,title,detail in items:box(ax,.35,y,9.3,.95,title,detail)
    for y in [6.2,4.7,3.2,1.7]:arrow(ax,(5,y),(5,y-.55))
    result['rag']=save(fig,'rag')

    fig,ax=canvas(8.4)
    box(ax,.5,7.2,9,.9,'Completed C2 → current provenance / entry validated','Critic accepted • code guard passed • citations / corpus bound')
    box(ax,.5,5.65,9,.9,'Code-sized payload → risk + deterministic critic','Whole shares • 2ATR stop • capital / cash / exposure limits')
    arrow(ax,(5,7.2),(5,6.55))
    box(ax,.5,4.0,9,.95,'SQLite checkpoint → WAITING_HUMAN','Exact payload + hash + expiry • approve / edit / reject','#fff1df')
    arrow(ax,(5,5.65),(5,4.95))
    box(ax,.25,2.05,2.7,.95,'Reject','Terminal; no write')
    box(ax,3.65,2.05,2.7,.95,'Edit','Recheck; NEW hash')
    box(ax,7.05,2.05,2.7,.95,'Approve','Validate current hash')
    for x in [1.6,5,8.4]:arrow(ax,(5,4),(x,3))
    arrow(ax,(3.65,2.52),(3.0,4.0),rad=-.3)
    box(ax,4.8,.1,4.95,1.05,'Final gates → simulated write','Freshness • current research • risk / kill\nIdempotent record; reconcile timeout','#e9f2e8')
    arrow(ax,(8.4,2.05),(8.4,1.15))
    ax.text(2.2,.65,'Restart resumes the saved action state;\nit never grants approval automatically.',ha='center',fontsize=9.5,color=NAVY)
    result['approval']=save(fig,'approval')
    fig,ax=canvas(9.0)
    stages=[(7.75,'Initialize and lock the historical run','Capital • risk / fees • dates • data / prompt / corpus fingerprint'),
            (6.2,'OPEN: queued exits then eligible C2 entries','Revalidate research • next-open sizing • cash / capacity'),
            (4.65,'Code stop / profit exits: gap-aware execution','Opening events first; ambiguous intraday bars use stop first'),
            (3.1,'CLOSE: ratchet stops → code exits → C2 review','Raised stop active next session; checkpoint before research'),
            (1.55,'Rank candidates → completed C2 → queue entries','Friday/gap candidates wait for a fresh close; save checkpoints'),
            (0.0,'END: mark surviving holdings; no forced sale','Cash + marked holdings = initial + realized + unrealized P&L')]
    for y,title,detail in stages:box(ax,.3,y,9.1,.95,title,detail,color='#e9f2e8' if y==0 else '#eaf1f8')
    for y in [7.75,6.2,4.65,3.1,1.55]:arrow(ax,(4.85,y),(4.85,y-.6))
    arrow(ax,(9.4,2.03),(9.4,6.65),rad=.18)
    ax.text(9.77,4.2,'Next session',rotation=90,ha='center',fontsize=9,color=NAVY,bbox={'facecolor':'white','edgecolor':'none','pad':2})
    result['portfolio']=save(fig,'portfolio')
    fig,ax=canvas(8.5)
    stages=[
        (7.2,'Streamlit → FastAPI','Reviewer auth • enabled backend • explicit usage consent'),
        (5.7,'LangGraph: market → strategy → critic','Scoped prompts • typed hand-offs • shared 8-unit ceiling'),
        (4.2,'Selected inference transport','Codex CLI + ChatGPT login  OR  OpenRouter + API key'),
        (2.7,'Structured tool intent → application validation','No native CLI tools • AegisTrade executes real MCP'),
        (1.2,'Selected dated evidence → next specialist invocation','Market snapshot • company filings • policy RAG • route check')]
    for y,title,detail in stages:box(ax,.35,y,9.25,.85,title,detail)
    for y in [7.2,5.7,4.2,2.7]:arrow(ax,(4.9,y),(4.9,y-.65))
    arrow(ax,(.35,1.6),(.35,6.05),rad=-.04)
    ax.text(.05,3.65,'Evidence loop',rotation=90,ha='center',fontsize=9,color=NAVY)
    ax.text(4.9,.38,'Completed C2 → code validation/sizing → approval or replay rules → simulated fill',
            ha='center',fontsize=9,color=NAVY)
    result['backend']=save(fig,'backend')
    fig,ax=canvas(7.2)
    for y,title,detail in [
        (5.9,'Completed portfolio + immutable dated source evidence','Process failures and original assessments; no later P&L trade labels'),
        (4.45,'Deterministic pending drafts → human source review','Edit conditions; accept or reject with rationale; zero generation calls'),
        (3.0,'Freeze accepted lessons into an immutable version','ID / hash / reviewer / source dates; existing runs keep their version'),
        (1.55,'New C2 run selects version → bounded relevant retrieval','Up to 3 / 2400 characters; source evidence gets context priority')]:
        box(ax,.3,y,9.4,.95,title,detail)
    for y in [5.9,4.45,3.0]:arrow(ax,(5,y),(5,y-.5))
    ax.text(5,.55,'Later-period evaluation or explicit development replay → critic + code checks',ha='center',fontsize=10,color=NAVY)
    arrow(ax,(5,1.55),(5,.85))
    result['portfolio_memory']=save(fig,'portfolio_memory')
    return result


def build(stem, figures, short_title, version='0.19.1', document_date='11 November 2026'):
    doc=Document(); sec=doc.sections[0]
    sec.page_width=Inches(8.27);sec.page_height=Inches(11.69)
    sec.top_margin=Inches(.7);sec.bottom_margin=Inches(.65)
    sec.left_margin=Inches(.75);sec.right_margin=Inches(.75)
    normal=doc.styles['Normal'];normal.font.name='Calibri';normal.font.size=Pt(10.5)
    normal.paragraph_format.line_spacing=1.08;normal.paragraph_format.space_after=Pt(6)
    for name in ['Title','Heading 1','Heading 2','Heading 3']:
        doc.styles[name].font.name='Calibri';doc.styles[name].font.color.rgb=RGBColor.from_string('173B5D')
    doc.styles['Title'].font.size=Pt(33)
    doc.styles['Heading 1'].font.size=Pt(18)
    doc.styles['Heading 2'].font.size=Pt(13)
    doc.styles['Heading 3'].font.size=Pt(11)
    header=sec.header.paragraphs[0];header.text='AEGISTRADE AI  |  '+short_title
    header.runs[0].font.size=Pt(8);header.runs[0].font.color.rgb=RGBColor.from_string('61778C')
    footer=sec.footer.paragraphs[0];footer.alignment=2
    footer.add_run(f'{document_date}  •  Source v{version}  •  Page ').font.size=Pt(8)
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
    doc.core_properties.title=short_title
    doc.core_properties.subject='Source-reviewed capstone design and examination preparation'
    doc.core_properties.author='AegisTrade AI project team'
    text=(DOCS/(stem+'.md')).read_text()
    for part in re.split(r'(\[\[FIGURE:\w+\]\])',text):
        match=re.fullmatch(r'\[\[FIGURE:(\w+)\]\]',part)
        if match:
            p=doc.add_paragraph();p.paragraph_format.keep_with_next=True
            p.add_run().add_picture(str(figures[match[1]]),width=Inches(6.65))
        else:append_markdown(doc,part,page_breaks=True)
    target=DOCS/(stem+'.docx');doc.save(target)
    return target


def main():
    figures=diagrams()
    for stem,title in [
        ('AegisTrade_Detailed_Design_and_Demo_Guide','DETAILED DESIGN & DEMO GUIDE'),
        ('AegisTrade_Viva_Questions_and_Answers','VIVA QUESTIONS & ANSWERS'),
        ('AegisTrade_ChatGPT_Plus_Full_UI_Demo_Runbook','CHATGPT PLUS • FULL UI DEMO'),
        ('AegisTrade_Project_Summary_and_UI_Overview','PROJECT SUMMARY & UI OVERVIEW'),
        ('AegisTrade_Portfolio_Simulation_Demo_Step_by_Step','PORTFOLIO SIMULATION • STEP BY STEP'),
        ('AegisTrade_C2_Tuning_and_Reviewed_Memory_Plan','C2 TUNING & REVIEWED MEMORY')]:
        path=build(stem,figures,title)
        print(f'{path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)')

if __name__=='__main__':main()
