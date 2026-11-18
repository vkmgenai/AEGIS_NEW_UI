from pathlib import Path
import nbformat as nbf
ROOT=Path(__file__).resolve().parent
nb=nbf.v4.new_notebook()
M=lambda s:nb.cells.append(nbf.v4.new_markdown_cell(s.strip()))
C=lambda s:nb.cells.append(nbf.v4.new_code_cell(s.strip()))

def filecell(path):
    contents=(ROOT/path).read_text()
    C(f"%%writefile {path}\n"+contents)

M(r'''# 🛡️ AegisTrade AI — Google Colab Capstone Starter (Phase 1)
**A human-governed multi-agent algorithmic trading research platform**  
Team: **Veneet · Karthika · Mathangi**

**This notebook is runnable even without an OpenRouter API key.** It starts with deterministic synthetic prices. No brokerage account is connected. **All prices and performances generated from synthetic data are artificial and cannot predict investment results.**

### What you will actually run

1. Validate daily OHLCV data (synthetic by default, optional NSE research download).
2. Compute EMA, RSI, ATR, ADX and three preapproved strategies.
3. Compare fixed strategies versus a regime-aware router in a causal next-open backtest.
4. Use code-based risk checks, fees, slippage, and protective exits.
5. Retrieve dated policy passages with a hybrid BM25 / TF-IDF-vector starter.
6. Demonstrate **four typed FastMCP servers**, an optional **OpenRouter explanation**, and an actual **LangGraph human approval interrupt with SQLite checkpoint**.
7. Test exact-payload approval, stale quote rejection, idempotency and failure recovery.

> **Capstone scope:** This is an **end-to-end research MVP**, not the entire final capstone. The full 60 **human-labelled** golden cases, 30 independently prepared attacks, neural RAG/reranker, calibrated LLM judge, Reflexion experiments, FastAPI/Streamlit, Docker, CI and Grafana remain later work. The final checklist is in the companion README.

**Workflow**  
`Historical daily OHLCV → code indicators → regime / eligible strategy → code trade proposal → code risk & critic → human interrupt → mock order gateway → audit / reconciliation`

`BUY` and `SELL` in historical backtests are computational simulations; an external-style mock order is never submitted in the approval demonstration without a human decision.
''')
M('## Step 0 — Setup (CPU runtime is sufficient)\nRun the cells **top to bottom**. The first cell installs libraries in the Colab runtime. If Colab requests a restart, restart and run from the top.')
C('''%pip -q install "langgraph>=1,<2" "langgraph-checkpoint-sqlite>=3,<4" "fastmcp>=2,<4" "rank-bm25>=0.2.2,<1" "yfinance>=0.2.60,<2" "pydantic>=2,<3" "scikit-learn>=1.2,<2" "pytest>=8,<10"''')
C('''from pathlib import Path
Path("aegistrade").mkdir(exist_ok=True)
Path("mcp_servers").mkdir(exist_ok=True)
Path("tests").mkdir(exist_ok=True)
Path("output").mkdir(exist_ok=True)
for x in ("aegistrade/__init__.py","mcp_servers/__init__.py"):
    Path(x).touch()
print("Folders initialized")''')
M('## Step 1 — Write the reusable Python project modules\nEach section below writes an actual `.py` file. This makes the notebook a **self-contained Colab installer**: you do not need to upload the ZIP to run it.')
for path in ["aegistrade/market.py","aegistrade/strategies.py","aegistrade/engine.py","aegistrade/safety.py","aegistrade/knowledge.py","aegistrade/openrouter.py","aegistrade/memory.py","aegistrade/workflow.py","aegistrade/evaluation.py"]:
    filecell(path)
M('## Step 2 — Choose data source and examine daily prices\nStart with `USE_REAL_DATA=False` so the notebook is reproducible and never silently substitutes made-up prices for real ones. For a **research-only** test on publicly displayed NSE prices, change it to `True` after checking the data provider’s terms of use. Historical constituent membership, missing/delisted stocks, adjusted-price fills, taxes and market microstructure are not solved by this prototype.')
C('''import numpy as np, pandas as pd
from IPython.display import display
from aegistrade.market import synthetic_market,download_nse_history,validate_ohlcv,DEFAULT_SYMBOLS
USE_REAL_DATA = False   # SWITCH only when you want market-data-provider research access
SYMBOLS = DEFAULT_SYMBOLS  # 5 symbols for fast first test; extend to 8–12 after data review
if USE_REAL_DATA:
    data = download_nse_history(SYMBOLS, start="2022-01-01", end="2026-10-31")
    DATA_LABEL="RESEARCH DATA: provider-adjusted historical prices (NOT execution quotes)"
else:
    data = synthetic_market(n_days=620, symbols=SYMBOLS, seed=42)
    DATA_LABEL="SYNTHETIC DEMONSTRATION DATA — NOT REAL NSE PRICES"
print(DATA_LABEL)
print(f"Bars: {len(data)} | Instruments: {data.Symbol.nunique()} | Date range: {data.Date.min().date()} → {data.Date.max().date()}")
display(data.head(10))''')
M('## Step 3 — Indicators and market-regime-aware routing\nThe code calculates all indicators; the LLM is **not** responsible for price data or mathematical calculations. These routing rules are research assumptions that must be validated, not guaranteed profitable mappings.')
C('''from aegistrade.strategies import prepare_indicators, entry_signal, chosen_strategy
frame = prepare_indicators(data)
cols = ["Date","Symbol","Close","EMA20","EMA50","RSI14","ATR14","ADX14","Regime","RoutedStrategy"]
display(frame[cols].tail(12).round(3))
print("Market regime counts:")
print(frame.Regime.value_counts())''')
M('## Step 4 — Backtest using only previously completed daily bars\nSignal after close on day **T**; simulated entry at **T+1 open** or later. Same risk policy, fees and slippage for fixed strategies and the router. The fixed models and router are **not optimized against the held-out segment** in this starter.')
C('''from aegistrade.engine import backtest, TradePolicy
policy = TradePolicy(initial_cash=100_000,risk_per_trade=0.01,max_position_fraction=0.20,
                     max_positions=4,fee_bps=10,slippage_bps=10,atr_stop_multiple=2.0)
all_dates = sorted(frame.Date.unique())
split_date = pd.Timestamp(all_dates[int(0.70*len(all_dates))])
train_frame = frame[frame.Date < split_date].copy()
heldout_frame = frame[frame.Date >= split_date].copy()
print("DEVELOPMENT period:", train_frame.Date.min().date(), "to", train_frame.Date.max().date())
print("HELD-OUT historical period:", heldout_frame.Date.min().date(), "to", heldout_frame.Date.max().date())
print("This is a time split, distinct from the 60 manually labelled agent-evaluation cases.")
results = {}
for mode in ["EMA_TREND","RSI_REVERSION","BREAKOUT","ROUTER"]:
    curve, trades, metrics = backtest(heldout_frame, mode=mode, p=policy)
    results[mode] = {"curve":curve,"trades":trades,"metrics":metrics}
summary = pd.DataFrame({k:v["metrics"] for k,v in results.items()}).T
summary.index.name="Strategy mode"
display(summary)
summary.to_csv("output/heldout_backtest_comparison.csv")''')
C('''import matplotlib.pyplot as plt
plt.figure(figsize=(11,4.8))
for mode,run in results.items():
    plt.plot(run["curve"].Date,run["curve"].Equity,label=mode,lw=1.7)
plt.title("AegisTrade simulated held-out equity curves — "+("real price history research" if USE_REAL_DATA else "SYNTHETIC DATA"))
plt.xlabel("Trading date"); plt.ylabel("Portfolio value (₹, simulated)")
plt.grid(alpha=.25); plt.legend(); plt.tight_layout(); plt.show()
print("Reminder: synthetic results are NOT investment performance; past historical returns do not predict future returns.")''')
M('## Step 5 — RAG-grounded policy context\nThis starter performs hybrid **BM25 + TF-IDF-vector fusion** and simple token-overlap reranking. The final capstone requires upgrading to semantic embeddings and a cross-encoder reranker, plus Recall@5 on 30+ independently labelled queries.')
C('''from aegistrade.knowledge import PolicyRetriever
retriever=PolicyRetriever()
for d in retriever.search("What happens if the quote is too old after a human approved an order?",top_k=4):
    print(f"[{d['id']}] ({d['date']}) {d['title']}: {d['text']}")''')
M('## Step 6 — Four typed MCP tool servers\nThese functions are exposed as real FastMCP tools. Demonstrate **schema discovery** and a **read call** in-memory; the approved execution tool remains restricted. In the final deployed design only the action agent should be connected to the write server.')
for path in ["mcp_servers/market_server.py","mcp_servers/strategy_server.py","mcp_servers/risk_server.py","mcp_servers/action_server.py"]:
    filecell(path)
C('''from fastmcp import Client
from mcp_servers.market_server import mcp as market_mcp
from mcp_servers.strategy_server import mcp as strategy_mcp
from mcp_servers.risk_server import mcp as risk_mcp
from mcp_servers.action_server import mcp as action_mcp

async def inspect_typed_mcp():
    for label,server in [("Market",market_mcp),("Strategies",strategy_mcp),("Risk",risk_mcp),("Restricted simulated action",action_mcp)]:
        async with Client(server) as client:
            tools=await client.list_tools()
            print(label, "MCP tools:",[t.name for t in tools])
            if label == "Market":
                r=await client.call_tool("list_symbols",{})
                print("  typed result:",r.data)
await inspect_typed_mcp()''')
M('## Step 7 — Optional OpenRouter explanation (token budget controlled)\n**The AI only explains evidence and policy citations. It cannot change trade quantities or execute an order.** Before turning this on, receive your API key, know which model slug you may use, and agree on your token/credit budget. The notebook will not print or save your API key.')
C('''import os
from aegistrade.openrouter import BudgetedExplainer
USE_OPENROUTER = False        # Keep False until faculty supplies credentials and budget
OPENROUTER_MODEL = "openai/gpt-4.1-mini"  # Confirm your allowed provider/model ID first
MAX_LLM_CALLS = 2
MAX_LLM_OUTPUT_TOKENS = 240
if USE_OPENROUTER and not os.getenv("OPENROUTER_API_KEY"):
    try:
        from google.colab import userdata
        os.environ["OPENROUTER_API_KEY"] = userdata.get("OPENROUTER_API_KEY")
    except Exception:
        print("Add OPENROUTER_API_KEY via Colab → Secrets; no API calls will run without it.")
explainer=BudgetedExplainer(enabled=USE_OPENROUTER,model=OPENROUTER_MODEL,
                            max_calls=MAX_LLM_CALLS,max_output_tokens=MAX_LLM_OUTPUT_TOKENS,max_input_chars=3500)
print("OpenRouter enabled:",USE_OPENROUTER)
print("Maximum explanation calls in this notebook:",MAX_LLM_CALLS)''')
M('## Step 8 — LangGraph supervisor, specialists, critic, SQLite checkpoints and human review\n**Important:** The next cell will STOP at `interrupt()` and show the exact order payload. It will **not submit anything**. The replay quote is a *synthetic execution-fixture quote* with an explicit timestamp. It is **not** a live broker quote. If you wait too long before approving, the simulator will reject the stale fixture quote, as intended.')
C('''import sqlite3,uuid
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
from aegistrade.workflow import build_trade_graph
from aegistrade.safety import AuditBroker, RiskInputs, RiskParameters, utc_now

eligible = heldout_frame.apply(lambda r: r.RoutedStrategy!="NONE" and entry_signal(r,r.RoutedStrategy),axis=1)
candidates=heldout_frame.loc[eligible].sort_values("Date")
assert not candidates.empty, "No eligible historical BUY test cases; try the default synthetic dataset."
candidate=candidates.iloc[-1]
print("Selected historical REPLAY fixture:",candidate.Symbol,candidate.Date.date(),candidate.RoutedStrategy)

risk_inputs=RiskInputs(equity=100_000, available_cash=100_000,current_positions=0)
risk_params=RiskParameters()
broker=AuditBroker("aegistrade_demo.sqlite")
checkpoint_connection=sqlite3.connect("aegistrade_graph_checkpoints.sqlite",check_same_thread=False)
checkpointer=SqliteSaver(checkpoint_connection)
# We explicitly create a fresh DEMO quote fixture; this is not live market data.
fixture_quote_price=float(candidate.Close)
fixture_quote_observed=utc_now().isoformat()

graph=build_trade_graph(frame,broker,risk_inputs,risk_params,retriever,explainer,checkpointer,
    quote_price=fixture_quote_price,quote_observed_utc=fixture_quote_observed)
thread_cfg={"configurable":{"thread_id":"human-demo-"+uuid.uuid4().hex}}
review_state=graph.invoke({"symbol":str(candidate.Symbol),"signal_date":candidate.Date.strftime("%Y-%m-%d")},thread_cfg)
if "__interrupt__" in review_state:
    review_request=review_state["__interrupt__"][0].value
    print("PAUSED FOR HUMAN APPROVAL. NO ORDER HAS BEEN SUBMITTED.")
    print("Approved payload fingerprint candidate:",review_request["payload_hash"])
    print("Proposed exact order:",review_request["order"])
else:
    print("Blocked/abstained:",review_state.get("status"),review_state.get("trace"))''')
M('## Step 9 — HUMAN DECISION CELL: default is REJECT\nFor an accepted mock submission **you must deliberately change** `HUMAN_DECISION` to `"approve"` and rerun this cell shortly after Step 8. To demonstrate invalidation, change to `"edit"` first (e.g. quantity 1), then run this same cell a second time with `"approve"` on the newly displayed payload. No external broker is connected.')
C('''HUMAN_DECISION = "reject"   # options: "reject", "edit", "approve"
EDIT_CHANGES = {"quantity": 1}  # used only if HUMAN_DECISION=="edit"

if "__interrupt__" not in review_state:
    print("Nothing pending approval; re-run Step 8 with an eligible test case.")
else:
    review_request = review_state["__interrupt__"][0].value
    if HUMAN_DECISION == "edit":
        reviewer_reply={"decision":"edit","changes":EDIT_CHANGES}
    elif HUMAN_DECISION == "approve":
        reviewer_reply={"decision":"approve","payload_hash":review_request["payload_hash"]}
    else:
        reviewer_reply={"decision":"reject"}
    review_state = graph.invoke(Command(resume=reviewer_reply),thread_cfg)
    if "__interrupt__" in review_state:
        new_review=review_state["__interrupt__"][0].value
        print("Old approval invalidated. NEW human approval required.")
        print("New payload fingerprint:",new_review["payload_hash"])
        print("Revised order:",new_review["order"])
    else:
        print("Final graph status:",review_state.get("status"))
        print("Trace:",review_state.get("trace"))
        print("Simulated execution result:",review_state.get("execution","No write executed"))
print("Recent broker audit events:",broker.events()[-5:])''')
M('## Step 10 — Candidate Reflexion lessons: human-reviewed memory only\nThis stores *proposed* lessons. It does not train a model, and it is **not** a substitute for the final Reflexion experiment. Approved lessons are retrievable; rejected ones remain in the audit table but never influence decisions.')
C('''from aegistrade.memory import LessonStore
lessons=LessonStore("aegistrade_lessons.sqlite")
id1=lessons.propose("routing","When ADX is low, confirm that a trend strategy is eligible before recommending it.","Regime=RANGE and trend strength weak")
id2=lessons.propose("risk","After a losing trade, double position quantity to recover faster.","Any previous loss")
# Illustrative FACULTY-DEMO review decisions (not empirically validated lessons).
lessons.review(id1,"ACCEPT","Agrees with the frozen eligibility policy; evaluate on held-out cases before claiming improvement")
lessons.review(id2,"REJECT","Violates fixed risk limits and is unsupported")
print("Accepted routing lessons:",lessons.accepted("routing"))
print("All lesson decisions (including rejection):",lessons.all_lessons()[-2:])''')
M('## Step 11 — Evaluation scaffold and tests\nThe 60 records below are **algorithmic test fixtures**, not yet Sir’s independently human-labelled golden set. Independent gold labels must be written before seeing agent outputs and kept inaccessible to the agent. The final project must also complete the evaluation E1–E4 and red-team suites.')
C('''from aegistrade.evaluation import make_risk_fixtures
cases=make_risk_fixtures(seed=97)
print("Generated boundary fixtures:",len(cases))
print("Dev candidate cases:",sum("development" in c["purpose"] for c in cases))
print("Candidate held-out cases requiring independent human labels:",sum("human-label" in c["purpose"] for c in cases))
display(pd.DataFrame(cases).head(8))''')
for path in ["tests/test_foundation.py","tests/test_safety.py","tests/test_workflow.py"]:
    filecell(path)
C('''!python -m pytest -q tests''')
M('## Step 12 — Examine saved outputs and next stages\nYour Colab runtime may reset; back up CSVs, SQLite DBs and code to a private Google Drive folder only if permitted by your data policy. Do not publish keys or private institutional data.')
C('''from pathlib import Path
files=list(Path("output").glob("*"))+list(Path(".").glob("*.sqlite"))
print("Generated files:")
for f in files:print(f" - {f} ({f.stat().st_size:,} bytes)")
print("LLM calls attempted:",explainer.calls,"API usage (if enabled):",explainer.usage)
print("Next: replace synthetic with licensed historical data, extend universe carefully, independently label 60 cases, and build production-oriented services/monitoring.")''')
M('''### Project ownership and remaining steps
**Veneet:** historic data/provenance, trading signals, causal backtesting, performance benchmarks, independent golden/attack cases.  
**Karthika:** hybrid semantic RAG, typed tool registry, LangGraph agent decision flow, critic, memory, reviewed Reflexion.  
**Mathangi:** deterministic risk gate, exact-payload approvals, mock order gateway, audit and reconciliation, FastAPI/UI, authentication, deployment, CI and observability.

**Final capstone requirements not completed by this notebook:** persistent external services; real broker-grade approval authentication; FastAPI streaming UI; independent policy security review; prompt/tool injections and 30 independently defined attacks; 60 manually validated cases + 20 judge-calibration labels; semantic embedding cross-encoder retrieval and 30 Recall@5 labels; fair C0/C1/C2 comparisons; lesson ablations and cost/latency experiments repeated three times; Grafana/Prometheus dashboard, Docker Compose and CI.

**Reference interfaces:** [OpenRouter Chat API](https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request), [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts), [FastMCP clients](https://gofastmcp.com/clients/client), [yfinance documentation](https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html).''')
nb.metadata={"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
             "language_info":{"name":"python","version":"3.11"},
             "colab":{"provenance":[],"name":"AegisTrade_AI_Colab_Starter.ipynb"}}
nbf.validate(nb)
out=ROOT/"notebooks"/"AegisTrade_AI_Colab_Starter.ipynb"
nbf.write(nb,out)
print(out,len(nb.cells),out.stat().st_size)
