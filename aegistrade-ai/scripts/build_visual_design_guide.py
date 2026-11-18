"""Render the current AegisTrade design guide as a visual, vector PDF."""
from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "AEGISTRADE_DESIGN_GUIDE_VISUAL_v035.pdf"

NAVY = "#102A43"
BLUE = "#245BC1"
CYAN = "#DFF3FA"
PALE = "#EEF4FC"
INK = "#17233B"
MUTED = "#607089"
GREEN = "#137A4D"
GREEN_BG = "#E4F6ED"
AMBER = "#9B6300"
AMBER_BG = "#FFF4D6"
RED = "#B4232C"
RED_BG = "#FDE9EA"
LINE = "#C8D5E8"
WHITE = "#FFFFFF"


def new_page(title: str, subtitle: str = ""):
    fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, .925), 1, .075, boxstyle="square,pad=0", facecolor=NAVY, edgecolor=NAVY))
    ax.text(.055, .965, title, color=WHITE, fontsize=19, fontweight="bold", va="center")
    if subtitle: ax.text(.055, .935, subtitle, color="#D7E5F7", fontsize=8.8, va="center")
    return fig, ax


def footer(ax, page):
    ax.plot([.055, .945], [.045, .045], color=LINE, lw=.8)
    ax.text(.055, .025, "AEGISTRADE AI  /  DESIGN GUIDE  /  VERSION 0.35  /  SIMULATION ONLY", color=MUTED, fontsize=7)
    ax.text(.945, .025, str(page), color=MUTED, fontsize=8, ha="right")


def wrap(text, width):
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False))


def box(ax, x, y, w, h, title, body="", fill=PALE, edge=LINE, title_color=NAVY, body_size=8.2, title_size=10, radius=.012):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=.012,rounding_size={radius}", facecolor=fill, edgecolor=edge, lw=1.1))
    ax.text(x+.018, y+h-.025, title, color=title_color, fontsize=title_size, fontweight="bold", va="top")
    if body:
        ax.text(x+.018, y+h-.052, body, color=INK, fontsize=body_size, va="top", linespacing=1.35)


def arrow(ax, x1, y1, x2, y2, color=BLUE, lw=1.8):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=12, color=color, lw=lw))


def pill(ax, x, y, text, color=BLUE, width=None):
    width = width or max(.1, .012*len(text)+.035)
    ax.add_patch(FancyBboxPatch((x, y), width, .027, boxstyle="round,pad=.005,rounding_size=.014", facecolor=color, edgecolor=color))
    ax.text(x+width/2, y+.0135, text, color=WHITE, fontsize=7.3, fontweight="bold", ha="center", va="center")


def bullet_list(ax, x, y, items, width=75, gap=.052, size=9, color=INK):
    for i, item in enumerate(items):
        yy=y-i*gap
        ax.add_patch(Circle((x, yy+.003), .0045, facecolor=BLUE, edgecolor="none"))
        ax.text(x+.015, yy+.012, wrap(item,width), fontsize=size, color=color, va="top", linespacing=1.3)


def page1(pdf):
    fig=plt.figure(figsize=(8.27,11.69),facecolor="white");ax=fig.add_axes([0,0,1,1]);ax.axis("off");ax.set_xlim(0,1);ax.set_ylim(0,1)
    ax.add_patch(FancyBboxPatch((0,.72),1,.28,boxstyle="square,pad=0",facecolor=NAVY,edgecolor=NAVY))
    ax.text(.06,.945,"LEARNING GUIDE · VERSION 0.35 · SIMULATION ONLY",fontsize=9,color="#BDD4F1",fontweight="bold")
    ax.text(.06,.875,"AegisTrade AI",fontsize=32,color=WHITE,fontweight="bold")
    ax.text(.06,.825,"How the current project is designed and why",fontsize=18,color=WHITE)
    ax.text(.06,.765,wrap("A research platform that compares one tool-using agent with a supervisor-led specialist team on the same historical evidence, while Python retains authority over routes, risk and simulated execution.",82),fontsize=10.5,color="#E4EDF8",linespacing=1.4)
    ax.text(.06,.665,"THE IDEA IN FOUR SENTENCES",fontsize=10,color=BLUE,fontweight="bold")
    items=[
        ("1","Code finds and constrains the signal","EMA, RSI, ADX, ATR, breakout and SMC conditions are calculated on completed daily bars."),
        ("2","Agents interpret dated evidence","C1 and C2 read company disclosures and policy through typed read tools and cite what they observed."),
        ("3","Code controls the money","Whole-share sizing, fees, exposure, stops, targets and later-open fills are deterministic."),
        ("4","Everything is recorded","Plans, tool calls, hand-offs, failures, human overrides and simulated fills remain auditable."),
    ]
    y=.585
    for num,title,body in items:
        ax.add_patch(Circle((.09,y+.025),.027,facecolor=BLUE,edgecolor="none"));ax.text(.09,y+.025,num,color=WHITE,fontsize=13,fontweight="bold",ha="center",va="center")
        ax.text(.14,y+.046,title,fontsize=12,color=NAVY,fontweight="bold",va="top")
        ax.text(.14,y+.018,wrap(body,82),fontsize=9,color=INK,va="top",linespacing=1.35)
        y-=.105
    box(ax,.06,.075,.88,.105,"The boundary that makes the project safe",wrap("The language model may interpret evidence and explain a recommendation. It cannot size a position, change risk policy, bypass validation or place a live order. AegisTrade has no live broker connection.",105),fill=AMBER_BG,edge="#E7C66D",title_color=AMBER,body_size=9.2,title_size=11)
    footer(ax,1);pdf.savefig(fig);plt.close(fig)


def page2(pdf):
    fig,ax=new_page("Detailed design diagram","Read from top to bottom. Numbers match the walkthrough and implementation layers.")
    layers=[
        ("1","People and screen","Streamlit · port 8501","Official original UI; workspace selector and notification bell","Market Data · Overview · Strategy Backtests · AI Agent Experiments · Evaluation · RAG · Lessons"),
        ("2","Service layer","FastAPI · port 8000 · v0.35","Typed schemas, reviewer authorization, paid-call consent","Background jobs · progress · call budgets · pause/resume · retained results"),
        ("3","Point-in-time data","Completed daily bars only","OHLCV, universes, indicators, automatic screening","Dated issuer filings and announcements · bounded web fallback · evidence cutoff"),
        ("4","Architecture experiment","Same case, model, tools and ceiling","C0 deterministic reference · C1 single agent","C2 supervisor + market + strategy + independent critic"),
        ("5","Tools and inference","Typed read-only boundary","MCP: snapshot · company evidence · policy search · strategy check","Claude CLI · ChatGPT/Codex CLI · OpenRouter · JSON transport"),
        ("6","Control and simulation","Python remains final authority","Citation/date/quote/route gates · sizing · fees · stops · targets","Optional HUMAN_EVIDENCE_OVERRIDE only for eligible evidence-blocked cases"),
        ("7","Records and proof","Auditable evaluation","Decision/trade/tool ledgers · checkpoints · attributed human P&L","Reviewed lessons · E1/E2/E3/E4 · Recall@5 · security · 377 tests"),
    ]
    top=.89;h=.102;gap=.012
    for i,(n,label,head,left,right) in enumerate(layers):
        y=top-(i+1)*h-i*gap
        ax.add_patch(FancyBboxPatch((.055,y),.12,h,boxstyle="round,pad=.008,rounding_size=.012",facecolor=NAVY,edgecolor=NAVY))
        ax.text(.075,y+h-.025,n,fontsize=18,color="#86B7FF",fontweight="bold",va="top")
        ax.text(.075,y+h-.055,wrap(label,16),fontsize=9,color=WHITE,fontweight="bold",va="top")
        ax.add_patch(FancyBboxPatch((.185,y),.76,h,boxstyle="round,pad=.008,rounding_size=.012",facecolor=PALE if i%2==0 else WHITE,edgecolor=LINE))
        ax.text(.205,y+h-.023,head,fontsize=10.2,color=NAVY,fontweight="bold",va="top")
        ax.text(.205,y+h-.051,wrap(left,47),fontsize=8.2,color=INK,va="top",linespacing=1.25)
        ax.text(.58,y+h-.051,wrap(right,49),fontsize=8.2,color=INK,va="top",linespacing=1.25)
        if i<6:arrow(ax,.565,y-.002,.565,y-.012,color="#7395C5",lw=1.2)
    footer(ax,2);pdf.savefig(fig);plt.close(fig)


def page3(pdf):
    fig,ax=new_page("The corrected C0, C1 and C2 comparison","The capstone comparison is C1 single agent versus C2 multi-agent. C0 is a secondary reference.")
    cards=[
        (.06,"C0","DETERMINISTIC REFERENCE","Python router chooses EMA trend, EMA pullback, RSI reversion or breakout.","0 model calls","Shows the no-generation route. Its code agreement is not directly comparable model quality.","#E9EEF5"),
        (.355,"C1","SINGLE-AGENT BASELINE","One agent performs the complete evidence-review task using the full shared read-tool set.","Ceiling: 8 calls","Guideline-matched baseline: same cases, model, evidence, tools and call ceiling as C2.",CYAN),
        (.65,"C2","MULTI-AGENT TEAM","Supervisor coordinates market, strategy and independent critic specialists through typed hand-offs.","Ceiling: 8 calls","Tests whether decomposition and a critic improve grounding, safety and reliability enough to justify cost.",GREEN_BG),
    ]
    for x,code,label,body,calls,meaning,fill in cards:
        box(ax,x,.56,.255,.285,code,"",fill=fill,edge=LINE,title_size=28,title_color=NAVY)
        ax.text(x+.018,.778,label,fontsize=8,color=BLUE,fontweight="bold")
        ax.text(x+.018,.735,wrap(body,31),fontsize=9,color=INK,va="top",linespacing=1.35)
        pill(ax,x+.018,.635,calls,color=BLUE,width=.145)
        ax.text(x+.018,.6,wrap(meaning,31),fontsize=8,color=MUTED,va="top",linespacing=1.3)
    box(ax,.06,.35,.845,.125,"Fairness contract",wrap("C1 and C2 receive the same historical case, cutoff-safe evidence, model, available read tools, output-token guidance and eight-call ceiling. The architectural decomposition is the intended independent variable.",103),fill=PALE,title_size=12,body_size=9.3)
    box(ax,.06,.15,.405,.125,"Where each flow appears",wrap("AI Agent Experiments shows C0/C1/C2. Strategy Backtests focuses on the end-to-end C2 portfolio. C1 is not presented as a separate portfolio product.",47),fill=WHITE,title_size=11)
    box(ax,.5,.15,.405,.125,"What success means",wrap("Task success, citation support, abstention quality, errors, calls, cost and latency are primary. P&L is a secondary standardized outcome, not proof of investment skill.",47),fill=WHITE,title_size=11)
    footer(ax,3);pdf.savefig(fig);plt.close(fig)


def page4(pdf):
    fig,ax=new_page("How one C2 decision is made","A fixed graph plus typed hand-offs prevents a model from changing the workflow order.")
    nodes=[
        (.055,"1","Technical case","Code-qualified\ncompleted bar",PALE),
        (.225,"2","Supervisor","Typed plan and\nshared state",CYAN),
        (.395,"3","Market specialist","Snapshot + dated\ncompany evidence",CYAN),
        (.565,"4","Strategy specialist","Policy search +\npermitted route",CYAN),
        (.735,"5","Independent critic","Re-observes sources\nand checks claims",GREEN_BG),
    ]
    for x,n,t,b,fill in nodes:
        box(ax,x,.66,.14,.16,t,b,fill=fill,title_size=9.3,body_size=7.8)
        ax.add_patch(Circle((x+.015,.802),.015,facecolor=BLUE,edgecolor="none"));ax.text(x+.015,.802,n,color=WHITE,fontsize=7,fontweight="bold",ha="center",va="center")
    for x in [.195,.365,.535,.705]:arrow(ax,x,.74,x+.025,.74)
    arrow(ax,.805,.65,.805,.58)
    box(ax,.61,.43,.39,.13,"6 · Deterministic validation",wrap("Schema · code route · passage IDs · cutoff dates · exact quotes · critic verdict",49),fill=PALE,title_size=11,body_size=8.6)
    arrow(ax,.805,.42,.805,.35)
    box(ax,.53,.2,.27,.105,"PASS","Eligible portfolio action\nthen deterministic sizing",fill=GREEN_BG,edge="#89C9AA",title_color=GREEN,title_size=13)
    box(ax,.82,.2,.13,.105,"FAIL","BLOCKED\nreason saved",fill=RED_BG,edge="#E8A6AA",title_color=RED,title_size=13,body_size=8)
    arrow(ax,.78,.42,.66,.31,color=GREEN);arrow(ax,.84,.42,.885,.31,color=RED)
    box(ax,.06,.42,.4,.19,"Evidence rules",wrap("Missing coverage is disclosed, not treated as good news. Strong trend, confirmed pullback and RSI reversion are not rejected solely because coverage is incomplete when no concrete adverse event is found. Breakout remains stricter: recent readable corroboration, exact quote and independent critic support are mandatory.",49),fill=AMBER_BG,edge="#E7C66D",title_color=AMBER,title_size=11,body_size=8.3)
    box(ax,.06,.17,.4,.16,"Holding reviews",wrap("Open positions are reviewed every five sessions and when fresh disclosures appear. A supported adverse event can lead to EXIT. Missing evidence alone is not an adverse event. Protective code exits never wait for an agent or person.",49),fill=WHITE,title_size=11,body_size=8.3)
    footer(ax,4);pdf.savefig(fig);plt.close(fig)


def page5(pdf):
    fig,ax=new_page("How one historical trade is simulated","Research and fills obey time order; later information never enters an earlier decision.")
    stages=[
        ("DAY T · CLOSE","Signal + evidence","Indicators use the completed bar. C2 researches the shortlisted candidate using only evidence available by the cutoff."),
        ("DAY T · CLOSE","Validation + sizing","Python validates the research, sizes whole shares and applies exposure, cash and risk limits."),
        ("DAY T+1 · OPEN","Synthetic fill","Eligible orders fill no earlier than a later session open with slippage and fixed delivery charges."),
        ("LATER SESSIONS","Protection + review","Stops, trailing stops, 8% target, strategy exits, holding reviews and supported adverse news can close the position."),
        ("END OF WINDOW","Mark to market","Open holdings are valued at the final close. They are not force-sold merely to finish the test."),
    ]
    y=.82
    ax.plot([.13,.13],[.19,.84],color=BLUE,lw=3)
    for i,(when,title,body) in enumerate(stages):
        ax.add_patch(Circle((.13,y),.022,facecolor=BLUE,edgecolor=WHITE,lw=2))
        pill(ax,.18,y+.033,when,color=NAVY,width=.17)
        ax.text(.18,y+.01,title,fontsize=11,color=NAVY,fontweight="bold",va="top")
        ax.text(.18,y-.02,wrap(body,76),fontsize=8.8,color=INK,va="top",linespacing=1.35)
        y-=.145
    box(ax,.58,.135,.35,.165,"Fixed demonstration policy",wrap("Normal risk 1% · breakout risk 0.5% · 2× ATR stop · 2.5× ATR breakout stop · trailing protection · 8% net target · 10 bps slippage · up to 3 researched candidates · review holdings every 5 sessions",42),fill=PALE,title_size=11,body_size=8.1)
    footer(ax,5);pdf.savefig(fig);plt.close(fig)


def page6(pdf):
    fig,ax=new_page("Human-in-the-loop evidence override","An optional study for eligible evidence-blocked actions—not an approval pause on every C2 decision.")
    box(ax,.06,.73,.25,.13,"Technically positive case",wrap("Code finds an eligible BUY or SELL situation.",30),fill=PALE,title_size=10)
    arrow(ax,.31,.795,.39,.795)
    box(ax,.39,.73,.25,.13,"C2 evidence block",wrap("Research remains BLOCKED because evidence is insufficient or unresolved.",30),fill=AMBER_BG,edge="#E7C66D",title_color=AMBER,title_size=10)
    arrow(ax,.64,.795,.72,.795)
    box(ax,.72,.73,.22,.13,"Eligibility gate",wrap("Hard risk, safety, freshness, provider and schema failures are never overridable.",26),fill=RED_BG,edge="#E8A6AA",title_color=RED,title_size=10,body_size=7.8)
    arrow(ax,.83,.72,.83,.64)
    box(ax,.62,.48,.32,.14,"Notification + human review",wrap("Bell icon shows a pending HUMAN_EVIDENCE_OVERRIDE. UI displays action, current price and entry price for SELL. Reviewer records APPROVE/REJECT and rationale.",39),fill=CYAN,title_size=11,body_size=8.1)
    arrow(ax,.7,.47,.55,.38,color=GREEN);arrow(ax,.86,.47,.9,.38,color=RED)
    box(ax,.38,.25,.32,.12,"APPROVE",wrap("Queue a linked synthetic action. A BUY creates a position carrying the override ID.",38),fill=GREEN_BG,edge="#89C9AA",title_color=GREEN,title_size=12,body_size=8)
    box(ax,.75,.25,.19,.12,"REJECT",wrap("Keep the original C2 BLOCKED result.",23),fill=RED_BG,edge="#E8A6AA",title_color=RED,title_size=12,body_size=8)
    arrow(ax,.54,.24,.54,.17,color=GREEN)
    box(ax,.19,.08,.7,.085,"Linked outcome ledger",wrap("Request → human decision → position opened → automatic protection or later linked SELL → realised/unrealised P&L → completed outcome → optional reviewed lesson. C2 P&L already contains this contribution.",91),fill=PALE,title_size=10.5,body_size=8.4)
    box(ax,.06,.45,.25,.18,"Never waits for approval",wrap("Protective stop, take-profit target, hard portfolio limit, stale-data block and provider/schema failure remain deterministic and fail closed.",29),fill=WHITE,title_size=10.5,body_size=8.2)
    footer(ax,6);pdf.savefig(fig);plt.close(fig)


def page7(pdf):
    fig,ax=new_page("RAG, historical evidence and Recall@5","Policy retrieval and company research are separate evidence systems with different roles.")
    box(ax,.06,.68,.39,.18,"Policy corpus · 87 passages",wrap("Project rules and bounded external references carry IDs, authority, source and date metadata. Hybrid lexical/neural retrieval, fusion and reranking return cited passages. Python still enforces policy.",48),fill=CYAN,title_size=12,body_size=8.5)
    box(ax,.55,.68,.39,.18,"Point-in-time company evidence",wrap("Cached NSE filings and announcements retain publication and availability timestamps. A bounded dated-web fallback may supplement missing coverage and is persisted with its cutoff.",48),fill=GREEN_BG,title_size=12,body_size=8.5)
    arrow(ax,.45,.77,.55,.77)
    ax.text(.5,.79,"agents read both",fontsize=7.5,color=MUTED,ha="center")
    ax.text(.06,.61,"INITIAL DEVELOPMENT RETRIEVAL RESULT",fontsize=9,color=BLUE,fontweight="bold")
    headers=["Metric","Before rewrite","After rewrite","Change"]
    rows=[("Recall@5","0.9406","0.9604","+0.0198"),("MRR@5","0.8667","0.8815","+0.0148"),("nDCG@5","0.8852","0.9013","+0.0161")]
    x0=.06;y0=.54;widths=[.28,.2,.2,.2];rh=.055
    x=x0
    for h,w in zip(headers,widths):
        ax.add_patch(FancyBboxPatch((x,y0),w,rh,boxstyle="square,pad=0",facecolor=NAVY,edgecolor=WHITE));ax.text(x+.012,y0+rh/2,h,color=WHITE,fontsize=8.5,fontweight="bold",va="center");x+=w
    for i,row in enumerate(rows):
        x=x0;y=y0-(i+1)*rh
        for value,w in zip(row,widths):
            ax.add_patch(FancyBboxPatch((x,y),w,rh,boxstyle="square,pad=0",facecolor=PALE if i%2==0 else WHITE,edgecolor=LINE,lw=.7));ax.text(x+.012,y+rh/2,value,color=INK,fontsize=8.5,va="center");x+=w
    box(ax,.06,.23,.88,.115,"What remains for final Recall@5",wrap("Karthika, Mathangi and Vineet independently label 36 blinded queries (12 each) against the frozen 87-passage catalogue. At least 30 accepted queries must remain. The reviewed packet is validated, frozen and rerun before/after rewriting on the exact same corpus.",105),fill=AMBER_BG,edge="#E7C66D",title_color=AMBER,title_size=11,body_size=8.8)
    box(ax,.06,.08,.88,.095,"Why this is separate from the 102 agent cases",wrap("Recall@5 tests whether retrieval returns all independently relevant passages. The agent cases test architecture decisions, grounding and security. Completing one review does not substitute for the other.",105),fill=WHITE,title_size=10.5,body_size=8.7)
    footer(ax,7);pdf.savefig(fig);plt.close(fig)


def page8(pdf):
    fig,ax=new_page("Fresh evaluation protocol and status","Review first, freeze second, run models third. Held-out labels never enter prompts or tools.")
    experiments=[
        ("E1","Architecture","C1 single agent vs C2 multi-agent; C0 secondary reference","20 development, then 40 held-out × 3"),
        ("E2","Security","C2 text defences off versus on","32 distinct attacks + 10 clean controls"),
        ("E3","Memory","C2 reviewed memory off versus on","Frozen playbook × 3 held-out repetitions"),
        ("E4","Ablation","Deterministic routing/retrieval/critic reference","No-paid-call reproducible engineering evidence"),
    ]
    y=.78
    for code,name,comparison,evidence in experiments:
        ax.add_patch(FancyBboxPatch((.06,y),.1,.095,boxstyle="round,pad=.008,rounding_size=.012",facecolor=BLUE,edgecolor=BLUE));ax.text(.11,y+.047,code,color=WHITE,fontsize=17,fontweight="bold",ha="center",va="center")
        ax.add_patch(FancyBboxPatch((.175,y),.765,.095,boxstyle="round,pad=.008,rounding_size=.012",facecolor=PALE,edgecolor=LINE));ax.text(.195,y+.067,name,fontsize=10.5,color=NAVY,fontweight="bold");ax.text(.195,y+.039,wrap(comparison,73),fontsize=8.3,color=INK);ax.text(.68,y+.039,wrap(evidence,31),fontsize=8,color=MUTED)
        y-=.12
    box(ax,.06,.23,.42,.14,"New review packet",wrap("20 fresh development · 40 fresh held-out · 32 attacks · 10 clean controls. Symbols are disjoint from the 17 November templates.",47),fill=GREEN_BG,title_size=11,body_size=8.7)
    box(ax,.52,.23,.42,.14,"Old 102 records",wrap("Retained unchanged as a historical audit trail. They do not need review and do not enter the new final metrics.",47),fill=WHITE,title_size=11,body_size=8.7)
    box(ax,.06,.08,.88,.095,"Verified engineering evidence",wrap("Fresh E4 ledger: 20261118T055107-c7102b3d · regression suite: 377 tests passed · failures and negative results remain reportable rather than being removed.",105),fill=PALE,title_size=10.5,body_size=8.8)
    footer(ax,8);pdf.savefig(fig);plt.close(fig)


def page9(pdf):
    fig,ax=new_page("Component map","What each part does and why it exists.")
    rows=[
        ("Official UI","app/ui.py","8501 dashboard, notification bell, progress, ledgers and review controls"),
        ("REST API","app/api.py","v0.35 typed boundary, authorization, consent and background jobs"),
        ("Market data","market.py · nse_data.py · universes.py","Cached OHLCV, named universes and provenance"),
        ("Signals","strategies.py · smc.py · selection.py","Indicators, approved routes, SMC and automatic ranking"),
        ("Company evidence","company_research.py · evidence_library.py · dated_web.py","Cutoff-safe filings, announcements and bounded fallback"),
        ("RAG","corpus.jsonl · corpus.py · knowledge.py","87 passages, hybrid retrieval, reranking and fingerprints"),
        ("Agents","agentic.py · agent_tools.py · config/agents.json","C1, C2 graph, typed hand-offs and prompt v20"),
        ("MCP","mcp_servers/ · mcp_runtime.py","Narrow read-tool interface; broker action withheld from agents"),
        ("Providers","llm_backend.py · llm_research.py","Claude CLI, Codex CLI and OpenRouter adapters"),
        ("Evidence gates","research_gate.py · breakout_evidence.py","Schemas, routes, citations, cutoff dates, quotes and critic verdict"),
        ("Portfolio","c2_portfolio.py · engine.py","Checkpointed C2 loop, sizing, fills, holdings and metrics"),
        ("Protection","fees.py · trailing_stop.py · reentry modules","Costs, stops, targets and controlled recovery entries"),
    ]
    x=[.06,.25,.52];w=[.19,.27,.42];y=.865;rh=.063
    for i,(component,files,why) in enumerate(rows):
        yy=y-(i+1)*rh
        fill=PALE if i%2==0 else WHITE
        for xx,ww in zip(x,w):ax.add_patch(FancyBboxPatch((xx,yy),ww,rh,boxstyle="square,pad=0",facecolor=fill,edgecolor=LINE,lw=.6))
        ax.text(x[0]+.01,yy+rh/2,component,fontsize=8.2,color=NAVY,fontweight="bold",va="center")
        ax.text(x[1]+.01,yy+rh/2,wrap(files,32),fontsize=7.1,color=MUTED,va="center")
        ax.text(x[2]+.01,yy+rh/2,wrap(why,53),fontsize=7.4,color=INK,va="center")
    footer(ax,9);pdf.savefig(fig);plt.close(fig)


def page10(pdf):
    fig,ax=new_page("Authority, demo path and honest limits","The design is strongest when each claim is tied to the component that actually owns it.")
    box(ax,.06,.69,.42,.18,"Who decides what",wrap("Python: indicators, route, ranking, quantity, exposure, fees, stops, targets and fills. Agents: interpret unstructured evidence and explain. C2 critic: independent interpretation check. Human: eligible evidence override and reviewed lessons. Nobody: live exchange order.",48),fill=PALE,title_size=12,body_size=8.5)
    box(ax,.52,.69,.42,.18,"Recommended demo path",wrap("Market Data → Overview → Policy Knowledge → AI Agent Experiments (C1 vs C2) → one C2 trace → Strategy Backtests → C2 portfolio ledger/equity → optional evidence override → Capstone Evaluation → tests.",48),fill=CYAN,title_size=12,body_size=8.5)
    ax.text(.06,.62,"LIMITATIONS TO SAY OUT LOUD",fontsize=9,color=BLUE,fontweight="bold")
    bullet_list(ax,.075,.57,[
        "Simulation only; no broker connection, investment advice or guarantee of executable prices.",
        "Daily bars do not reproduce intraday order paths, and raw prices are not fully corporate-action adjusted.",
        "Current-member and curated universes retain survivorship and selection bias.",
        "Historical evidence coverage is uneven; missing coverage is disclosed rather than guessed.",
        "Model outputs vary, and provider/schema/timeout failures remain in the metrics.",
        "C2 has not established a durable trading edge. Its present value is auditable evidence review.",
        "Initial Recall@5 and small AI repeats remain development evidence until fresh reviews are frozen and rerun.",
    ],width=96,gap=.062,size=8.7)
    box(ax,.06,.07,.88,.105,"Viva answer to remember",wrap("C1 and C2 solve the same evidence-review task with the same case, model, read tools and call ceiling. C1 uses one agent; C2 uses a supervisor, market specialist, strategy specialist and independent critic. Python remains the authority for routes, validation, risk and simulated execution.",105),fill=NAVY,edge=NAVY,title_color="#8FC1FF",body_size=9,title_size=11)
    # white body text overlay for dark box
    ax.add_patch(FancyBboxPatch((.06,.07),.88,.105,boxstyle="round,pad=.012,rounding_size=.012",facecolor=NAVY,edgecolor=NAVY))
    ax.text(.078,.15,"Viva answer to remember",color="#8FC1FF",fontsize=11,fontweight="bold",va="top")
    ax.text(.078,.122,wrap("C1 and C2 solve the same evidence-review task with the same case, model, read tools and call ceiling. C1 uses one agent; C2 uses a supervisor, market specialist, strategy specialist and independent critic. Python remains the authority for routes, validation, risk and simulated execution.",105),color=WHITE,fontsize=8.8,va="top",linespacing=1.3)
    footer(ax,10);pdf.savefig(fig);plt.close(fig)


def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with PdfPages(OUT,metadata={"Title":"AegisTrade AI Current Design Guide v0.35","Author":"AegisTrade AI Capstone Team","Subject":"Simulation-only multi-agent research architecture"}) as pdf:
        for fn in (page1,page2,page3,page4,page5,page6,page7,page8,page9,page10): fn(pdf)
    print(OUT)


if __name__=="__main__":main()
