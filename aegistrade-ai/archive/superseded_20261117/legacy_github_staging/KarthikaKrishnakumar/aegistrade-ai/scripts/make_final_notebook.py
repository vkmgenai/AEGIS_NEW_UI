import nbformat as nbf
from pathlib import Path
N=nbf.v4.new_notebook()
N.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
            'language_info':{'name':'python'}}
C=[]
def md(t):C.append(nbf.v4.new_markdown_cell(t))
def py(t):C.append(nbf.v4.new_code_cell(t))
md('''# AegisTrade AI — Final Capstone Research Companion (Google Colab)

This notebook is a **research/testing companion** to the complete multi-service project. The FastAPI dashboard, five MCP servers and Docker monitoring are best demonstrated locally with `docker compose up --build`.

**Safety:** Simulated trading only. Synthetic daily bars are the default. No real broker credentials or orders. Optional OpenRouter requests are disabled unless deliberately enabled.''')
md('## 1. Upload the final project ZIP\nDownload the complete ZIP from the ChatGPT response; upload that ZIP here when prompted.')
py('''from google.colab import files
from pathlib import Path
import zipfile, os
uploaded=files.upload()
archives=[p for p in uploaded if p.lower().endswith('.zip')]
assert archives, 'Upload the complete AegisTrade_AI_Final_Project.zip first.'
with zipfile.ZipFile(archives[0]) as z:z.extractall('/content')
root=Path('/content/AegisTrade_AI_Final_Project')
assert (root/'requirements-full.txt').exists(), 'Wrong ZIP structure: expected project folder.'
os.chdir(root)
print('Project folder:',root)
''')
md('## 2. Install dependencies\nColab needs internet to install full package dependencies. The first download of sentence-transformers models may be large; neural RAG is optional until ready.')
py('''import subprocess,sys
subprocess.check_call([sys.executable,'-m','pip','install','-q','-r','requirements-full.txt'])
print('Installed full project requirements')
''')
md('## 3. Generate reproducible synthetic daily data and indicators\nOHLCV below is **not live NSE data**. The backtester uses completed-day signals and next-session fill assumptions.')
py('''import pandas as pd
from aegistrade.market import synthetic_market
from aegistrade.strategies import prepare_indicators
frame=prepare_indicators(synthetic_market(n_days=620,seed=42))
print('Rows',len(frame),'Symbols:',sorted(frame.Symbol.unique().tolist()))
display(frame[['Date','Symbol','Close','EMA20','EMA50','RSI14','ATR14','ADX14','Regime','RoutedStrategy']].tail(10))
''')
md('## 4. Compare trading strategies\nA strategy backtest is NOT evidence that the LLM agent is profitable. It tests deterministic rules on a synthetic sample.')
py('''from aegistrade.experiments import strategy_comparison
comparison=pd.DataFrame(strategy_comparison(frame))
display(comparison[['config','mode','total_return_pct','sharpe','max_drawdown_pct','completed_trades','win_rate_pct']])
print('C1_SINGLE and C2_TEAM rows are identical *routing proxies*, NOT actual agent experiment scores.')
''')
md('## 5. Plot equity curves')
py('''from aegistrade.engine import backtest
import matplotlib.pyplot as plt
plt.figure(figsize=(11,4))
for mode in ['EMA_TREND','RSI_REVERSION','BREAKOUT','ROUTER']:
    equity, trades, metrics=backtest(frame,mode)
    plt.plot(equity.Date,equity.Equity,label=mode)
plt.title('Synthetic portfolio equity — illustration only')
plt.ylabel('Simulated INR');plt.xlabel('Date');plt.legend();plt.tight_layout();plt.show()
''')
md('## 6. Cited retrieval (offline)')
py('''from aegistrade.knowledge import PolicyRetriever
kb=PolicyRetriever(mode='offline')
for p in kb.search('What if approved order quantity changes and quote is stale?',5):
    print(p['id'],p['title'],p['text'])
print('Offline retrieval is TF-IDF fallback, not neural dense vectors.')
''')
md('## 7. Deterministic evaluation\nThe labels were generated as candidate reference cases and still require independent human review. Do not report this score as final capstone evidence.')
py('''import subprocess,sys
subprocess.run([sys.executable,'-m','evaluation.run_eval','--split','dev','--output','reports/eval_dev_colab.json'],check=True)
''')
md('## 8. Human approval using LangGraph interrupt()\nThe default decision is **reject**, and the broker is only a local mock. For a controlled simulated accept demo, edit the review decision to approve after inspecting the exact payload.')
py('''import sqlite3,uuid,json
from datetime import timezone
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
from aegistrade.workflow import build_trade_graph
from aegistrade.openrouter import BudgetedExplainer
from aegistrade.safety import AuditBroker,RiskInputs,RiskParameters,utc_now
from aegistrade.strategies import entry_signal,chosen_strategy
# Complete C2 research first in the app; supply its saved JSON, never fabricate a pass.
from aegistrade.research_gate import validate_completed_c2
RESEARCH_RESULT_PATH = ''  # e.g. data/research_runs/<run_id>.json
assert RESEARCH_RESULT_PATH, 'Complete C2 and set its saved result path before the approval demo'
saved=json.loads(Path(RESEARCH_RESULT_PATH).read_text())
completed=[x for x in saved['outputs'] if x.get('config')=='C2' and x.get('guard_pass')]
assert completed, 'A passing C2 case is required'
research=validate_completed_c2(completed[0])
rows=frame[(frame.Symbol==research['symbol'])&(frame.Date==pd.Timestamp(research['date']))]
assert len(rows)==1, 'Load the same historical dataset used for research'
r=rows.iloc[0]
broker=AuditBroker('data/colab_simulator.sqlite')
cp=SqliteSaver(sqlite3.connect('data/colab_checkpoints.sqlite',check_same_thread=False))
graph=build_trade_graph(frame,broker,RiskInputs(equity=100000,available_cash=100000,current_positions=0),
                       RiskParameters(max_quote_age_seconds=600),PolicyRetriever(),BudgetedExplainer(enabled=False),
                       cp,research_context=research,quote_price=float(r.Close),quote_observed_utc=utc_now().isoformat())
thread=uuid.uuid4().hex
cfg={'configurable':{'thread_id':thread}}
result=graph.invoke({'symbol':str(r.Symbol),'signal_date':str(r.Date.date()),'edit_count':0},cfg)
print('Interrupted?', '__interrupt__' in result)
if '__interrupt__' in result:
    pending=result['__interrupt__'][0].value
    print('Exact order:',pending['order'])
    print('Payload hash:',pending['payload_hash'])
    # Deliberately reject; do not switch unless actively testing acceptance.
    decision={'decision':'reject','payload_hash':pending['payload_hash']}
    final=graph.invoke(Command(resume=decision),cfg)
    print('Final status:',final.get('status'),'Trace:',final.get('trace',[]))
else:
    print('No signal / blocked:',result)
''')
md('## 9. Optional: real MCP tool discovery (no model spending)')
py('''import subprocess,sys
subprocess.run([sys.executable,'scripts/mcp_smoke.py'],check=True)
''')
md('## 10. Optional: OpenRouter experiment (explicit opt in)\n**Do not run until your institution confirms the account allowance.** This notebook keeps the budget small. Never paste a key into a shared notebook output.')
py('''ENABLE_OPENROUTER=False
if ENABLE_OPENROUTER:
    from google.colab import userdata
    key=userdata.get('OPENROUTER_API_KEY')
    assert key,'Add OPENROUTER_API_KEY to Colab Secrets first.'
    os.environ['OPENROUTER_API_KEY']=key
    subprocess.run([sys.executable,'-m','evaluation.run_llm_experiments','--cases','1',
                    '--config','all','--max-calls','3','--max-output-tokens','650'],check=True)
else:
    print('OpenRouter skipped. Set ENABLE_OPENROUTER=True only after API allowance confirmed.')
''')
md('''## Next steps before the final viva

1. Independently review the 60 golden labels and 36 retrieval labels; freeze held-out files.
2. Replace synthetic data with permitted historical daily prices, and document survivorship/corporate actions.
3. Evaluate neural embeddings + cross-encoder and actual tool-using multi-agent versus single-agent on unseen cases.
4. Collect human labels for judge calibration and report Cohen’s kappa.
5. Run real model-level red-team with defences off/on, not just regex checks.
6. Launch the **full project locally with Docker Compose** and record Grafana, approvals and error-recovery demos.

For detailed instructions, see the Word manual and `docs/COMPLIANCE_AND_REMAINING_WORK.md`.''')
N.cells=C
root=Path(__file__).resolve().parents[1]
out=root/'notebooks'/'AegisTrade_AI_Final_Colab.ipynb'
nbf.write(N,out)
print(out, 'cells',len(C))
