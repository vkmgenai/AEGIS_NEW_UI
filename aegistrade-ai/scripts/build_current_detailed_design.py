"""Build the current plain-language detailed design Word document and diagrams."""
from scripts import build_design_and_viva_docs as b


def current_architecture():
    b.ASSETS.mkdir(parents=True,exist_ok=True)
    fig,ax=b.canvas(10.2)
    b.box(ax,.3,9.05,9.4,.82,'1  Question-led demo shell','Data & Stock • C2 Portfolio • Agent Comparison • Evaluation Evidence','#e9f2e8')
    b.box(ax,.3,7.75,9.4,.82,'2  FastAPI control boundary','Typed requests • reviewer authorization • explicit allowance • saved-run APIs','#fde8e5')
    b.arrow(ax,(5,9.05),(5,8.57))
    b.box(ax,.25,6.25,2.85,.9,'3  Market + selection','Frozen universe • OHLCV • indicators • ranked audit','#eaf1f8')
    b.box(ax,3.58,6.25,2.85,.9,'4  Research architectures','C0 reference • C1 single agent • C2 specialist team','#fff1df')
    b.box(ax,6.9,6.25,2.85,.9,'5  MCP evidence plane','Company pack • policy RAG • route • reviewed memory','#eaf1f8')
    for x in (1.68,5,8.33):b.arrow(ax,(5,7.75),(x,7.15))
    b.box(ax,.3,4.75,9.4,.82,'6  Deterministic research gate','Schema • cutoff • citations • route • adverse evidence • independent critic','#fde8e5')
    for x in (1.68,5,8.33):b.arrow(ax,(x,6.25),(5,5.57))
    b.box(ax,.25,3.18,4.45,.95,'7  Historical execution engine','Whole shares • costs • stops/targets • later-open simulated fills','#e9f2e8')
    b.box(ax,5.3,3.18,4.45,.95,'8  HUMAN_EVIDENCE_OVERRIDE','Eligible pause • separate decision • linked entry/exit • risk exits','#fff1df')
    b.arrow(ax,(4.1,4.75),(2.48,4.13));b.arrow(ax,(5.9,4.75),(7.52,4.13))
    b.box(ax,.3,1.62,9.4,.82,'9  Durable evidence and outcome layer','Research traces • checkpoints • ledgers • P&L • notifications • lessons','#eaf1f8')
    b.arrow(ax,(2.48,3.18),(4.2,2.44));b.arrow(ax,(7.52,3.18),(5.8,2.44))
    b.box(ax,.3,.25,4.45,.75,'Primary C1 versus C2 evaluation','Three repeats • grounding • risk • failures • latency/calls')
    b.box(ax,5.3,.25,4.45,.75,'Secondary financial outcomes','20-session case P&L • C2 portfolio • drawdown • limitations')
    b.arrow(ax,(4.2,1.62),(2.48,1.0));b.arrow(ax,(5.8,1.62),(7.52,1.0))
    return b.save(fig,'current_architecture_v032')


def research_flow():
    fig,ax=b.canvas(8.8)
    b.box(ax,.3,7.55,9.4,.8,'Locked historical case','Completed session • signal date • code route • evidence cutoff • same case family')
    b.box(ax,.25,5.85,2.85,1.05,'C0','Deterministic reference • zero LLM calls','#e9f2e8')
    b.box(ax,3.58,5.85,2.85,1.05,'C1','One tool-using agent • same research budget','#fff1df')
    b.box(ax,6.9,5.85,2.85,1.05,'C2','Market → strategy → critic • bounded correction','#fff1df')
    for x in (1.68,5,8.33):b.arrow(ax,(5,7.55),(x,6.9))
    b.box(ax,.3,4.25,9.4,.82,'Typed code validation','Route • dated citations • adverse-risk policy • abstention versus hard failure','#fde8e5')
    for x in (1.68,5,8.33):b.arrow(ax,(x,5.85),(5,5.07))
    b.box(ax,.25,2.55,4.45,1.0,'AI Agent Experiment','C1 vs C2 capability • calls • latency • failures','#eaf1f8')
    b.box(ax,5.3,2.55,4.45,1.0,'Outcome views','fixed 20-session case P&L • C2 portfolio ledger','#e9f2e8')
    b.arrow(ax,(4.2,4.25),(2.48,3.55));b.arrow(ax,(5.8,4.25),(7.52,3.55))
    b.box(ax,.3,.75,9.4,.82,'Interpret separately','Research quality is not profitability; historical profit is not proof of grounding or future edge.')
    b.arrow(ax,(2.48,2.55),(4.2,1.57));b.arrow(ax,(7.52,2.55),(5.8,1.57))
    return b.save(fig,'current_research_flow_v032')


def main():
    figures={'current_architecture':current_architecture(),'research_flow':research_flow()}
    path=b.build('AegisTrade_Current_Detailed_Design',figures,'CURRENT DETAILED DESIGN & CODE GUIDE',version='0.35.0',document_date='17 November 2026')
    print(path)


if __name__=='__main__':main()
