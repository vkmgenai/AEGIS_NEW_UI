"""AegisTrade AI local Streamlit console — simulation-only research and teaching UI.

Design goals: native accessible Streamlit theme, no global color CSS overrides,
readable on a 13-inch MacBook, clear pending approvals and safe demo controls.
"""
from __future__ import annotations

import json
import os
from urllib.parse import quote

import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="AegisTrade AI | Research Console",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "AegisTrade AI — simulation-only GenAI capstone prototype."},
)

# Deliberately avoid styling every sidebar descendant. Streamlit themes control
# foreground/background contrast; unscoped CSS made some widgets unreadable.
st.markdown(
    """<style>
    .block-container {max-width: 1280px; padding-top: 1.2rem; padding-bottom: 3rem;}
    h1 {letter-spacing: -.025em;}
    div[data-testid="stHorizontalBlock"] {gap: 0.85rem;}
    </style>""",
    unsafe_allow_html=True,
)

from app.client_errors import APIError
from app.live_progress import render_c2_progress
from app.backend_compat import compatible_backend,UI_API_CONTRACT

API = os.getenv("AEGIS_API_URL", "http://127.0.0.1:8000").rstrip("/")
PAGES = (
    "Market Data",
    "Overview",
    "Strategy Backtests",
    "AI Agent Experiments",
    "Supervised Trading",
    "Policy Knowledge",
    "Learning & Lessons",
    "Broker Audit",
)


def get(path: str, timeout: int = 60):
    response = requests.get(API + path, timeout=timeout)
    if not response.ok:
        raise APIError.from_response(response)
    return response.json()


def post(path: str, payload: dict, reviewer_token: str = "", timeout: int = 90):
    headers = {"X-Reviewer-Token": reviewer_token} if reviewer_token else {}
    response = requests.post(API + path, json=payload, headers=headers, timeout=timeout)
    if not response.ok:
        raise APIError.from_response(response)
    return response.json()


def fail(message: str, error: Exception | None = None):
    if isinstance(error,APIError):
        st.error(message+' '+error.detail)
        if error.action:st.info(error.action)
    else:st.error(message)
    if error is not None:
        with st.expander("Technical details"):
            st.code(str(error))


def render_table(records, caption: str = "", height: int = 320):
    frame = pd.DataFrame(records)
    if frame.empty:
        st.info("There are no records to display yet.")
    else:
        st.dataframe(frame, use_container_width=True, hide_index=True, height=height)
    if caption:
        st.caption(caption)


def selection_table(rows,caption='',height=320):
    labels={'ALREADY_HELD':'Already held','INSUFFICIENT_HISTORY':'Insufficient warm-up history',
            'LOW_LIQUIDITY':'Below turnover threshold','REGIME_ABSTAIN':'Regime requires abstention',
            'VOLATILITY_LIMIT':'Volatility limit','UNREVIEWED_PRICE_DISCONTINUITY':'Unreviewed price discontinuity',
            'NO_ENTRY_SIGNAL':'No entry signal','CAPITAL_OR_RISK_LIMIT':'Capital/risk cannot fund one share',
            'POSITION_LIMIT':'Portfolio position limit','DAILY_LOSS_LIMIT':'Daily-loss circuit breaker'}
    display=[]
    for row in rows:
        display.append({'Stock':row['symbol'],'Rank':row.get('rank'),'Selected':row.get('selected',False),
            'Strategy':row['strategy'],'Score':row['score'],'Estimated shares':row['estimated_quantity_at_signal_close'],
            'Reason':'; '.join(labels.get(r,r) for r in row.get('reasons',[])) or 'Eligible at signal close'})
    render_table(display,caption,height)


def heading(name: str, description: str):
    st.subheader(name)
    st.caption(description)


def metric_value(value, suffix: str = "") -> str:
    if value is None or pd.isna(value):
        return "—"
    try:
        return f"{float(value):,.2f}{suffix}"
    except (ValueError, TypeError):
        return str(value)


# Navigation is in the main content area so it remains accessible even when the
# sidebar collapses on a narrow or zoomed browser viewport.
with st.sidebar:
    st.title("🛡️ AegisTrade AI")
    st.caption("CAPSTONE • RESEARCH PROTOTYPE")
    st.info("SIMULATION ONLY — No live broker connection.")
    reviewer_token = st.text_input(
        "Reviewer token", key="aegis_reviewer_token", type="password",
        help="Find AEGIS_REVIEWER_TOKEN in your local .env file. Never publish it or show it during the viva.",
    )
    st.caption("A reviewer token is necessary for approving, editing or rejecting an order, and for reviewing lessons.")
    st.divider()
    st.caption("Local API")
    st.code(API, language="text")
    st.caption("If controls are hidden, widen the browser, use 100% zoom, or expand the sidebar with the arrow at the top left.")

st.title("AegisTrade AI")
st.caption("Automatic stock screening · C2 evidence research · Human-governed simulated actions")
if st.session_state.pop('open_research_workspace',False):
    st.session_state['aegis_workspace']='AI Agent Experiments'
    params=st.session_state.get('selection_research_settings',{})
    if params:
        from datetime import date as research_date
        st.session_state['ai_eval_start']=research_date.fromisoformat(params['start'])
        st.session_state['ai_eval_end']=research_date.fromisoformat(params['end'])
if st.session_state.pop('open_supervised_workspace',False):
    st.session_state['aegis_workspace']='Supervised Trading'
page = st.selectbox("Workspace", PAGES, key="aegis_workspace", help="Choose a workspace. This selector remains visible even when the sidebar is closed.")

try:
    health = get("/health", timeout=10)
    universe = get("/market/universe", timeout=15)
except Exception as exc:
    fail("The dashboard cannot reach the FastAPI backend on port 8000.", exc)
    st.markdown("**Run the backend in a separate Terminal:**")
    st.code("cd /path/to/aegistrade-ai\n.venv/bin/python -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --env-file .env", language="bash")
    st.caption("Then refresh this browser page. If port 8000 is occupied, check: lsof -nP -iTCP:8000 -sTCP:LISTEN")
    if st.button("Retry connection"):
        st.rerun()
    st.stop()

if not compatible_backend(health):
    st.warning('The dashboard and API use incompatible interfaces. Restart both services from the same project folder.')
    st.caption('Backend version: '+str(health.get('version','unknown'))+' | Backend interface: '+str(health.get('ui_api_contract','legacy'))+' | Required interface: '+str(UI_API_CONTRACT))
    st.code('bash scripts/start_unix.sh',language='bash')
    st.stop()

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    c1.metric("Execution", "Simulation only")
    c2.metric("Data source", str(health.get("data_source", "synthetic")).upper())
    c3.metric("Trading universe", f"{len(universe.get('symbols', []))} instruments")

if health.get('data_source')=='nsepython':
    provenance=universe.get('provenance',{})
    st.info('NSEPython cached OHLCV · '+str(len(universe['symbols']))+' stocks · source and coverage retained in the dataset manifest.')
    if provenance.get('survivorship_bias'):st.warning("Current-member or curated research selection is applied to history. Survivorship/selection bias remains; this is not a verified point-in-time constituent reconstruction.")
    if provenance.get('price_adjustment')=='unadjusted':st.warning('Raw NSE prices are not corporate-action adjusted. Splits, bonuses and demergers can distort simulated returns; results remain provisional.')
if health.get("data_source") == "synthetic":
    st.warning("Research dataset: SYNTHETIC. Charts, signals and P&L are illustrative and are not live NSE prices or verified investment results.")

if page == "Market Data":
    heading('Research universe and market data','Choose a retained universe, prepare its cached history and activate it for new work. No model calls on this screen.')
    profiles=[];chosen=None
    if health.get('universe_switching_supported'):
        try:
            profiles=get('/market/datasets')['datasets']
            by_id={item['id']:item for item in profiles}
            active=next((item['id'] for item in profiles if item['active']),'nifty20')
            chosen=st.selectbox('Universe dataset',list(by_id),index=list(by_id).index(active),format_func=lambda key:by_id[key]['name'],key='market_universe_choice')
            selected=by_id[chosen];st.write(selected['description'])
            dataset=get('/market/dataset?universe_id='+chosen)
        except Exception as exc:fail('Could not load research universes.',exc);st.stop()
    else:
        dataset=get('/market/dataset')
        st.info('The running API predates universe switching. Existing data is retained; restart the API and dashboard together when workers are idle to load the selector.')
    manifest=dataset.get('manifest') or {}
    a,b,c=st.columns(3)
    a.metric('Download',str(manifest.get('status','Not downloaded')).title())
    b.metric('Selected stocks',len(manifest.get('symbols',[])) if manifest else selected['count'] if chosen else 0)
    c.metric('Cached request chunks',dataset.get('cached_chunks',0))
    if st.button('Refresh download status'):st.rerun()
    preparation=dataset.get('preparation')
    if preparation:
        from app.dataset_progress import render_preparation_progress
        render_preparation_progress(chosen,preparation,get)
    if manifest:
        st.write(f"**Requested period:** {manifest.get('requested_start')} to {manifest.get('requested_end')}")
        st.caption('Earlier cached rows provide indicator warm-up and any pre-period selection. They are outside the evaluation window.')
        st.write('**Universe rule:** '+manifest.get('universe_selection',''))
        st.write('**Membership:** '+manifest.get('membership_mode','unknown')+' · as of '+str(manifest.get('membership_asof','unknown')))
        if manifest.get('survivorship_bias'):st.warning('Current-member or curated selection is applied backwards. Historical membership and selection bias remain; this is not a verified point-in-time index reconstruction.')
        if manifest.get('selection_bias'):st.warning(manifest['selection_bias'])
        if manifest.get('price_adjustment')=='unadjusted':st.warning('Raw NSE OHLCV: corporate actions and cash dividends are not reconstructed. Financial conclusions remain provisional.')
        if manifest.get('universe_ranking'):
            with st.expander('Why these stocks?',expanded=True):render_table(manifest['universe_ranking'],'Pre-period liquidity selection; no subsequent-return ranking.',height=320)
        if manifest.get('universe_exclusions'):
            with st.expander('Excluded from the universe screen'):render_table(manifest['universe_exclusions'])
        with st.expander('Per-stock history coverage',expanded=True):render_table(manifest.get('coverage',[]),height=300)
        if manifest.get('history_availability_note'):st.caption(manifest['history_availability_note'])
        if manifest.get('errors'):st.json(manifest['errors'])
    if chosen=='nifty100':
        with st.expander('Frozen official Nifty 100 members',expanded=False):render_table(selected['members'],height=350)
    if chosen=='research30':
        with st.expander('Frozen 30 members and research groups',expanded=True):
            st.caption('21 established + 6 cyclical + 3 event-research cases. These are experimental groups, not buy recommendations, current warning ratings or future-return labels. Groups are not included in C2 prompts.')
            render_table(selected['members'],height=350)
    ready=manifest.get('status')=='complete'
    is_active=dataset.get('active',dataset.get('active_source')=='nsepython')
    if ready and not is_active:
        acknowledged=st.checkbox('Use this provisional research dataset with the displayed limitations understood')
        if st.button('Use downloaded NSE data',disabled=not (acknowledged and reviewer_token)):
            try:
                payload={'acknowledge_provisional_data':True}
                if chosen:payload['universe_id']=chosen
                post('/market/dataset/activate',payload,reviewer_token)
                for key in ('active_ohlcv_csv','company_pack','selection_preview','selection_research_settings','linked_research','open_research_workspace','open_supervised_workspace'):
                    st.session_state.pop(key,None)
                st.rerun()
            except Exception as exc:fail('Dataset activation failed.',exc)
    elif ready and is_active:
        st.success('This dataset is active for new charts, screening, backtests and research. Existing portfolio runs retain their original data.')
        if st.button('Prepare OHLCV CSV download'):
            response=requests.get(API+'/market/ohlcv.csv',timeout=30)
            if response.ok:st.session_state['active_ohlcv_csv']=response.text
            else:st.error('Could not export active OHLCV data.')
        if st.session_state.get('active_ohlcv_csv'):
            st.download_button('Download active OHLCV CSV',st.session_state['active_ohlcv_csv'],file_name='aegistrade_'+str(chosen or 'active')+'_ohlcv.csv',mime='text/csv')
    if chosen and not ready:
        from datetime import date,timedelta
        defaults=manifest or universe.get('provenance',{})
        ending=date.fromisoformat(defaults.get('requested_end') or universe['last_date'])
        starting=date.fromisoformat(defaults.get('requested_start') or (pd.Timestamp(ending)-pd.DateOffset(years=5)).date().isoformat())
        with st.expander('Prepare or resume this universe',expanded=True):
            st.caption('Downloads public NSE data only, reusing validated history where possible. No LLM calls and no automatic activation. Newer listings can have shorter disclosed histories; code still requires indicator warm-up.')
            start=st.date_input('Dataset evaluation start',value=starting,key='dataset_start_'+chosen)
            end=st.date_input('Dataset evaluation end',value=ending,key='dataset_end_'+chosen)
            working=bool(preparation and preparation.get('worker_active'))
            if st.button('Prepare selected universe',disabled=not bool(reviewer_token) or working):
                try:
                    post('/market/dataset/prepare',{'universe_id':chosen,'start_date':start.isoformat(),'end_date':end.isoformat()},reviewer_token,timeout=30)
                    st.rerun()
                except Exception as exc:fail('Dataset preparation could not start.',exc)
    with st.expander('Download or resume on this computer'):
        st.code('.venv/bin/python -m scripts.download_universe --universe '+str(chosen or 'nifty20'),language='bash')
        st.caption('Keep the existing top-20 dataset. Each universe has its own directory and frozen constituent snapshot; switching does not delete another dataset. There is no synthetic or Yahoo fallback.')

elif page == "Overview":
    heading("Market overview", "Inspect daily OHLCV prices, technical indicators and the current simulated strategy candidate.")
    selectors = st.columns([2, 1])
    with selectors[0]:
        symbol = st.selectbox("Instrument", universe["symbols"], key="overview_symbol")
    with selectors[1]:
        lookback = st.selectbox("History window", [60, 120, 180, 360, 1260, 1600], index=2, key="overview_window")
    try:
        history = get(f"/market/history?symbol={quote(symbol)}&limit={lookback}")
        snapshot = get("/research/latest?symbol=" + quote(symbol))
    except Exception as exc:
        fail("Unable to load market research data.", exc)
        st.stop()
    bars = pd.DataFrame(history["bars"])
    if not bars.empty:
        bars["date"] = pd.to_datetime(bars["date"])
        tabs = st.tabs(["Price & averages", "Daily bar details", "Indicator explanation"])
        with tabs[0]:
            close_data = bars.set_index("date")[["close", "ema20", "ema50"]].rename(
                columns={"close": "Close", "ema20": "EMA 20", "ema50": "EMA 50"}
            )
            st.line_chart(close_data, height=350, use_container_width=True)
            st.caption("All three lines are derived from daily historical/synthetic bars. This chart is not a live price feed.")
        with tabs[1]:
            table = bars[["date", "open", "high", "low", "close", "volume", "rsi14", "regime"]].tail(30).iloc[::-1]
            render_table(table, "Latest 30 daily bars (newest first).", height=330)
        with tabs[2]:
            st.markdown("**EMA20 / EMA50:** moving averages used to identify directional trends. **RSI14:** momentum indicator that can support mean-reversion signals. **ATR14:** typical price range used in stop-loss calculations. **ADX14:** trend strength indicator. An indicator alone is not a trade instruction.")
    st.markdown("#### Latest research snapshot")
    m1, m2, m3 = st.columns(3)
    m1.metric("Reference close", "₹" + metric_value(snapshot.get("Close")))
    m2.metric("RSI (14)", metric_value(snapshot.get("RSI14")))
    m3.metric("ADX (14)", metric_value(snapshot.get("ADX14")))
    with st.container(border=True):
        st.write(f"**Detected regime:** {snapshot.get('regime', 'unknown')}")
        st.write(f"**Candidate strategy:** {snapshot.get('approved_candidate', 'NONE')}")
        st.write(f"**Signal date:** {snapshot.get('signal_date', 'unknown')}")
        st.caption("These are preapproved routing candidates, not automatic authorizations to trade.")
    with st.expander("How the AegisTrade workflow connects these parts", expanded=True):
        st.markdown("**Daily market data** → **Automatic stock ranking** → **Completed C2 research + critic/code checks** → **Code-sized order** → **Human approval** → **Final freshness/risk checks** → **Simulated broker + audit**")
        st.info("Next: run Strategy Backtests, inspect the stock-selection audit, then send selected candidates through C2. Only passing C2 cases can reach Supervised Trading.")

elif page == "Strategy Backtests":
    heading("Portfolio simulation", "Choose your capital, historical date range and risk. This is a reproducible DAILY-BAR backtest, not real-time paper trading.")
    simulation_engine=st.radio('Simulation engine',['C2 historical portfolio','Technical-only baseline'],horizontal=True,key='simulation_engine')
    is_c2=simulation_engine=='C2 historical portfolio'
    if is_c2 and health.get('signal_specific_evidence_supported'):
        st.info('Entry policy: strong trend and RSI-reversion signals can proceed with explicitly incomplete coverage after dated research, if no concrete adverse event remains unresolved. Breakouts require a recent verbatim source quote supporting actual improvement or a completed commercial event, independently corroborated by the critic. Known recent structural actions quarantine new entries on unadjusted prices. A cited adverse finding requires an EXIT after critic validation; it fills at a later eligible open.')
    st.info('C2 mode researches each prospective entry and periodically reviews holdings. Historical fills follow upfront approved rules; the separate supervised workflow retains per-order human review. Stops and strategy exits remain code-controlled. Open holdings are marked, never forcibly sold at the end.')
    if is_c2:
        inf=health.get('inference',{})
        st.caption('Backend: '+inf.get('backend','openrouter')+' | Model: '+health.get('agent_model','unknown')+' | Allowance unit: '+inf.get('budget_unit','model_requests'))
        if inf.get('backend')=='codex_cli':st.info('Codex consumes ChatGPT plan allowance. Caps count CLI invocations; internal provider requests and per-run USD cost are unknown. Response-token budgets are guidance, not hard provider token caps.')
    if is_c2 and health.get('dated_web_search_supported'):st.caption('Eligible cases with missing/UNKNOWN company evidence can use bounded dated web search before an evidence-based block. Sources must pass date/identity checks; strong technical signals do not override unresolved material risks.')
    if is_c2:st.caption('A long period can consume substantial API or ChatGPT plan allowance. The total allowance pauses the run before another case would exceed it. Normal research uses six inference units per case; eight are reserved conservatively. Begin with a short date window.')
    from datetime import date, timedelta
    first = date.fromisoformat(universe.get("provenance",{}).get("requested_start") or universe["first_date"])
    last = date.fromisoformat(universe["last_date"])
    selected_book=None
    if is_c2:
        try:
            books=get('/portfolio-lessons').get('versions',[]) if health.get('portfolio_memory_supported') else []
            choices={'No portfolio lessons':None,**{f"{b['created_at'][:19]} | {b['lesson_count']} lessons | trained through {b['trained_through']} | {b['id'][:8]}":b for b in books}}
            selected_book=choices[st.selectbox('Frozen portfolio lesson version',list(choices))]
        except Exception as exc:fail('Could not load portfolio lesson versions.',exc)
    if not health.get('configurable_stop_loss_supported',False):
        st.info('The initial stop-loss controls below need the updated API. Existing jobs can continue; finish or pause them, then restart the API and dashboard together before submitting a new simulation.')
    stop_method=st.selectbox('Initial stop-loss method',['ATR distance','Percentage below signal close'],key='initial_stop_method')
    with st.form("capital_simulation_form"):
        st.markdown("#### Simulation settings")
        c1,c2,c3=st.columns(3)
        with c1:
            capital=st.number_input("Initial capital (₹)",min_value=1000.0,max_value=100000000.0,value=200000.0,step=10000.0)
            risk_pct=st.number_input("Maximum risk per trade (%)",min_value=0.25,max_value=3.0,value=1.0,step=0.25)
        with c2:
            start_date=st.date_input("Simulation start",value=first,min_value=first,max_value=last)
            end_date=st.date_input("Simulation end",value=last,min_value=first,max_value=last)
        with c3:
            automatic_selection=st.checkbox("Automatically screen and rank stocks",value=True,disabled=is_c2)
            sim_mode=st.selectbox("Strategies to run",["ROUTER"] if is_c2 else ["ALL","ROUTER","EMA_TREND","RSI_REVERSION","BREAKOUT"],
                                  help="ALL compares four rule-based strategy configurations using identical starting capital and dates.")
            fee_bps=st.number_input("Fees (basis points per transaction)",min_value=0.0,max_value=100.0,value=10.0,step=5.0)
            slippage_bps=st.number_input("Slippage (basis points per transaction)",min_value=0.0,max_value=100.0,value=10.0,step=5.0)
        initial_atr=st.number_input('Initial stop distance (× ATR14 at signal)',min_value=0.5,max_value=10.0,value=2.0,step=0.5,disabled=stop_method!='ATR distance')
        initial_percent=st.number_input('Initial stop loss (% below signal close)',min_value=0.1,max_value=50.0,value=5.0,step=0.5,disabled=stop_method=='ATR distance')
        st.caption('The initial stop is fixed from the completed signal close before a later-open fill. A 5% stop means 5% below that close; fees, slippage and opening gaps can change the actual loss. This is separate from the portfolio risk-per-trade percentage.')
        take_profit=st.number_input('Take-profit target (% net return; 0 disables)',min_value=0.0,max_value=100.0,value=8.0,step=1.0)
        st.caption('Friday or pre-gap entry candidates are reviewed again at the next trading close before a later-open fill. Profit targets are net of modeled trading fees; slippage is included in execution. If a daily bar touches both stop and target after opening, the stop takes priority.')
        trailing_enabled=st.checkbox('Enable trailing stop',value=True,key='simulation_trailing_stop')
        trailing_multiple=st.number_input('Trailing distance (× ATR14 at entry signal)',min_value=0.5,max_value=10.0,value=2.0,step=0.5,disabled=not trailing_enabled)
        st.caption('A trailing stop follows the highest completed close since entry and never falls. Its ATR distance is fixed from the entry signal. Each increase applies from the next session; existing strategy and C2 exits still apply. Trailing can tighten your chosen initial stop; disable trailing if you want the initial stop price to stay fixed.')
        if is_c2:
            development_memory=st.checkbox('Mark as development replay if lesson training overlaps these dates',value=False,disabled=selected_book is None)
            if selected_book:st.caption('Pinned version: '+selected_book['sha256']+' · Lessons are conditional reminders; they cannot alter risk limits or force trades. Later-period evaluation must start after '+selected_book['trained_through']+'.')
            max_calls=st.number_input('Total inference allowance (requests or CLI invocations)',min_value=8,max_value=2400,value=48,step=8)
            review_every=st.number_input('Review each holding every N market sessions',min_value=1,max_value=60,value=5,step=1)
            if health.get('adverse_news_exit_supported'):st.caption('For NSE portfolios, dated issuer disclosures are also checked between scheduled reviews. A new candidate triggers C2 review; an empty check makes no generation call. This is a bounded source check, not a complete news feed.')
            c2_consent=st.checkbox('I authorize external inference for this historical portfolio, up to the displayed allowance',value=False)
        approve_rules=st.checkbox("I approve these stock-selection, risk and cost assumptions for automatic historical replay",value=False)
        if is_c2:st.caption('This approval includes fresh post-gap entry review, automatic historical entries, code stop/profit/strategy exits and accepted C2 EXIT decisions. No per-fill human pause; no live broker action; no forced end sale.')
        run_sim=st.form_submit_button("Run historical portfolio simulation",type="primary",use_container_width=True)
    if run_sim:
        if not approve_rules:st.error("Approve the displayed replay assumptions before running the historical simulation.")
        elif not health.get('configurable_stop_loss_supported',False):st.error('The backend has not loaded configurable initial stops yet. Finish or pause active work, then restart the API and dashboard together before starting a new run.')
        elif not health.get('fresh_adverse_profit_policy_supported',False):st.error('Restart the API and dashboard together to load fresh entry review, adverse-event research and take-profit rules before starting this new run.')
        elif trailing_enabled and not health.get('trailing_stop_supported',False):st.error('The running backend does not yet support trailing stops. Restart the API and dashboard together before starting this run.')
        elif is_c2 and (not reviewer_token or not c2_consent):st.error('Reviewer token and explicit paid C2 consent are required.')
        elif start_date>end_date:
            st.error("The simulation start date must be before the end date.")
        else:
            payload={"initial_capital":float(capital),"start_date":start_date.isoformat(),"end_date":end_date.isoformat(),
                     "risk_percent":float(risk_pct),"mode":sim_mode,"automatic_stock_selection":bool(automatic_selection),"fee_bps":float(fee_bps),"slippage_bps":float(slippage_bps),
                     "stop_loss_mode":"ATR" if stop_method=="ATR distance" else "PERCENT","initial_stop_atr_multiple":float(initial_atr),"stop_loss_percent":float(initial_percent),"take_profit_percent":float(take_profit),"review_after_gap":True,"trailing_stop_enabled":bool(trailing_enabled),"trailing_atr_multiple":float(trailing_multiple)}
            try:
                if is_c2:
                    payload.update(consent_to_paid_calls=True,approve_historical_rules=True,max_model_calls=int(max_calls),holding_review_sessions=int(review_every),portfolio_playbook_id=selected_book['id'] if selected_book else None,memory_allow_development_replay=bool(development_memory))
                    with st.spinner('Creating checkpointed C2 portfolio job...'):
                        st.session_state['simulation_result']=post('/simulation/c2/run',payload,reviewer_token,timeout=120)
                    st.session_state['c2_portfolio_id']=st.session_state['simulation_result']['run_id']
                    st.session_state['c2_job_input']=st.session_state['c2_portfolio_id']
                    st.success('C2 job started. Progress updates automatically every 5 seconds; the manual refresh button remains available.')
                else:
                    with st.spinner("Replaying the selected daily OHLCV period..."):
                        st.session_state["simulation_result"]=post("/simulation/run",payload,timeout=240)
                    st.success("Technical-only simulation completed and saved.")
            except Exception as exc:
                fail("Portfolio simulation failed. Try a longer date interval (at least 45 sessions).",exc)
    with st.expander('C2 portfolio progress, resume and saved jobs',expanded=is_c2):
        if st.session_state.get('c2_job_next'):st.session_state['c2_job_input']=st.session_state.pop('c2_job_next')
        st.session_state.setdefault('c2_job_input',st.session_state.get('c2_portfolio_id',''))
        job_id=st.text_input('C2 portfolio run ID',key='c2_job_input')
        try:
            jobs=get('/simulation/c2/recent').get('runs',[])
            if jobs:
                labels={x['created_utc'][:19]+' | '+x['status']+' | '+x['run_id']:x['run_id'] for x in jobs}
                choice=st.selectbox('Saved C2 portfolio',list(labels))
                if st.button('Open saved C2 portfolio'):
                    st.session_state['c2_portfolio_id']=labels[choice]
                    st.session_state['c2_job_next']=labels[choice]
                    st.session_state['simulation_result']=get('/simulation/c2/status/'+labels[choice]);st.rerun()
        except Exception as exc:fail('Could not list C2 jobs.',exc)
        if st.button('Refresh C2 progress',disabled=not bool(job_id)):
            try:
                st.session_state['simulation_result']=get('/simulation/c2/status/'+job_id)
                st.session_state['c2_portfolio_id']=job_id
            except Exception as exc:fail('Unable to load C2 job.',exc)
        more=st.number_input('Additional inference units on resume',min_value=0,max_value=2400,value=48,step=8)
        resume_consent=st.checkbox('I authorize resuming this historical job with the additional allowance',value=False)
        a,b=st.columns(2)
        if a.button('Resume C2 portfolio',disabled=not bool(job_id and reviewer_token and resume_consent)):
            try:st.session_state['simulation_result']=post('/simulation/c2/resume/'+job_id,{'additional_model_calls':int(more),'consent_to_paid_calls':True},reviewer_token)
            except Exception as exc:fail('Resume rejected; inspect configuration, run status and consent.',exc)
        if b.button('Pause C2 portfolio',disabled=not bool(job_id and reviewer_token)):
            try:post('/simulation/c2/pause/'+job_id,{},reviewer_token);st.info('Pause requested at the next safe boundary.')
            except Exception as exc:fail('Pause request failed.',exc)
    result=st.session_state.get("simulation_result")
    with st.expander("Open a previously saved simulation"):
        try:
            previous=get("/simulation/recent").get("runs",[])
            if previous:
                choices={f"{x['created_utc'][:19]} | ₹{x['settings']['initial_capital']:,.0f} | {x['period']['start']}–{x['period']['end']} | {x['run_id'][:8]}":x['run_id'] for x in previous}
                picked=st.selectbox("Saved simulation",list(choices),key="simulation_saved_run")
                if st.button("Load saved simulation"):
                    st.session_state["simulation_result"]=get("/simulation/result/"+choices[picked],timeout=60)
                    st.rerun()
            else: st.caption("No saved simulation runs yet.")
        except Exception as exc: fail("Unable to load saved run list.",exc)
    if result:
        st.divider()
        if result.get('data_provenance',{}).get('universe_id'):
            st.caption('Result universe: '+str(result['data_provenance'].get('universe_name') or result['data_provenance']['universe_id']))
        if result.get('initial_stop_loss'):
            with st.expander('Initial stop-loss settings'):st.json(result['initial_stop_loss'])
        c2_result='model_usage' in result
        st.markdown('#### Results — C2 historical portfolio' if c2_result else '#### Results — technical-only baseline')
        if c2_result:
            if result.get('portfolio_memory'):
                with st.expander('Pinned portfolio lesson memory'):st.json(result['portfolio_memory'])
            render_c2_progress(result,get)
            if result.get('research_configuration_changed'):
                st.info('This saved job uses an earlier research prompt version or simulation/exit-policy version. Its original results and usage are preserved. Start a new run to use the current rules; the earlier job cannot resume under changed rules.')
            if result['status']=='PAUSED_PROVIDER':
                failure=next((d for d in reversed(result.get('decisions',[])) if d.get('action')=='PROVIDER_FAILURE'),{})
                st.warning('; '.join(failure.get('errors',[])) or 'Inference paused. Inspect the saved error code before consenting to retry.')
                st.caption('The job is paused; no automatic retry or allowance increase. Timeout/response-format failures have different remedies from login or quota errors.')
            if result['status']=='PAUSED_BUDGET':st.info('The total call allowance is exhausted for another bounded case. Add allowance and consent to resume.')
            if not result.get('comparison_valid_for_full_period'):st.warning('Partial run: full-period reference metrics are withheld. Resume or refresh to complete the requested window.')
            st.caption('Provider cost is reported separately in USD; trading returns include trading fees/slippage and exclude model charges.')
            with st.expander('Open holdings, unrealized P&L and pending orders',expanded=True):
                render_table(result.get('open_holdings',[]),'Remaining holdings are marked to the last available close; no terminal liquidation.',height=230)
                st.json(result.get('accounting',{}))
                if result.get('pending_orders'):st.json(result['pending_orders'])
            with st.expander('Exit rules, profit target and stop adjustments'):
                st.json(result.get('exit_policy',{'trailing_stop_enabled':False}))
                render_table(result.get('stop_updates',[]),'Stop increases are calculated at the completed close and become effective from the next session.',height=240)
            with st.expander('C2 entry / holding-review decisions and traces'):
                decisions=result.get('decisions',[])
                st.caption('HOLD keeps the existing shares after a scheduled review; it creates no new trade. Code stops and strategy exits remain active.')
                if any('CONTEXT_BUDGET_EXCEEDED' in ' '.join(d.get('errors',[])) for d in decisions):
                    st.info('A context-budget failure concerns research input size, separately from your inference-call allowance. Refreshing or adding calls does not fix it. Inspect the research trace; after updating an affected backend, start a new run to re-evaluate previously blocked candidates.')
                render_table([{**{k:d.get(k) for k in ['date','symbol','purpose','action','llm_calls','failure_category']},
                               'evidence_policy':(d.get('company_assessment') or {}).get('adverse_risk',''),
                               'web_search':(d.get('dated_web_search') or {}).get('status',''),'reason':'; '.join(d.get('errors',[])) or d.get('explanation','')} for d in decisions],height=300)
                records=[d for d in decisions if d.get('id')]
                if result.get('news_checks'):
                    with st.expander('Dated issuer-disclosure checks between holding reviews'):
                        render_table([{'date':x.get('date'),'symbol':x.get('symbol'),'status':x.get('status'),
                            'candidates':len(x.get('candidates',[])),'error':x.get('error','')} for x in result['news_checks']])
                if records:
                    choices={d['date']+' '+d['symbol']+' '+d.get('purpose','')+' '+d['id']:d['id'] for d in records}
                    decision_choice=st.selectbox('C2 portfolio research record',list(choices))
                    selected_record=next(d for d in records if d['id']==choices[decision_choice])
                    company=selected_record.get('company_assessment') or {}
                    if company.get('breakout_support'):
                        st.write('**Breakout explanation:** '+company['breakout_support'])
                        if company.get('breakout_evidence'):
                            st.json(company['breakout_evidence'])
                            st.caption('Load the full research trace to inspect the critic\'s separate source corroboration.')
                        else:st.caption('This recorded explanation has no structured source quote. Inspect its saved policy version; current breakout entries require quoted corroboration.')
                    if selected_record.get('portfolio_memory'):
                        st.json(selected_record['portfolio_memory'])
                    if selected_record.get('portfolio_memory'):
                        st.json(selected_record['portfolio_memory'])
                    if selected_record.get('dated_web_search'):
                        st.write('Dated web-search evidence')
                        st.json(selected_record['dated_web_search'])
                    if selected_record.get('explanation'):
                        st.markdown('**Decision explanation**')
                        st.write(selected_record['explanation'])
                    if selected_record.get('errors'):
                        st.warning('; '.join(selected_record['errors']))
                    if selected_record.get('failure_category')=='SCHEMA':
                        st.caption('The model response did not fit a required field/schema. This is separate from account access or missing filings. Current prompts provide exact limits and field-specific correction feedback.')
                    if selected_record.get('failure',{}).get('source')=='saved_response_revalidation':
                        st.caption('Diagnosis reconstructed from the saved model response. The original result, calls and trading decisions are preserved.')
                    if selected_record.get('failure',{}).get('elapsed_seconds') is not None:
                        st.caption('Failed invocation elapsed time: '+str(selected_record['failure']['elapsed_seconds'])+' seconds.')
                    if selected_record.get('failure',{}).get('unproductive_revision_after_rejection'):
                        st.info('This older trace attempted another strategy call after the critic had rejected the case. The current workflow ends at critic rejection and saves that extra call.')
                    if st.button('Load C2 portfolio research trace'):
                        try:st.json(get('/simulation/c2/research/'+result['run_id']+'/'+choices[decision_choice]))
                        except Exception as exc:fail('Unable to read research trace.',exc)
        st.caption(f"Run ID: {result['run_id']} | Sessions: {result['sessions']} | Actual selected period: {result['period']['start']} to {result['period']['end']}")
        metrics=pd.DataFrame(result.get("metrics",[]))
        render_table(metrics, "C2 entries require completed research; code/risk exits and scheduled C2 reviews govern holdings." if c2_result else "No model calls: technical-only fills including selected fees and slippage.",height=250)
        if not metrics.empty:
            mode_list=list(metrics["mode"])
            selected=st.selectbox("Inspect portfolio / trading ledger for",mode_list,key="simulation_curve_pick")
            row=metrics[metrics["mode"]==selected].iloc[0]
            v1,v2,v3,v4=st.columns(4)
            v1.metric("Initial capital",f"₹{float(row['initial_capital']):,.0f}")
            v2.metric("Ending portfolio",f"₹{float(row['ending_equity']):,.0f}")
            v3.metric("Total return",metric_value(row.get("total_return_pct"),"%"))
            v4.metric("Max drawdown",metric_value(row.get("max_drawdown_pct"),"%"))
            if result.get('benchmark',{}).get('metrics'):
                st.caption("Passive benchmark: equal-weight buy at the first session open, same costs, no active stops/exposure cap.")
                render_table([{'mode':result['benchmark']['name'],**result['benchmark']['metrics']}],height=100)
            st.markdown("##### Portfolio equity curve")
            curves=[]
            for m,rows in result["curves"].items():
                for item in rows:curves.append({"date":item["date"],"strategy":m,"equity":item["equity"]})
            eq=pd.DataFrame(curves)
            if not eq.empty:
                chart=eq.pivot(index="date",columns="strategy",values="equity")
                chart.index=pd.to_datetime(chart.index)
                st.line_chart(chart,height=365,use_container_width=True)
            with st.expander("Cash balance and open positions over time"):
                port=pd.DataFrame(result["curves"][selected])
                if not port.empty:
                    port["date"]=pd.to_datetime(port["date"])
                    st.line_chart(port.set_index("date")[["cash","equity"]],height=250)
                    render_table(port.tail(40).iloc[::-1],height=250)
            selection=result.get('stock_selection',{})
            if selection.get('enabled'):
                with st.expander('Automatic stock-selection audit'):
                    st.caption('Ranks use only completed-session evidence. A shortlist is not C2 research or human approval.')
                    audit=selection.get('audits',{}).get(selected,[])
                    if audit:
                        dates=sorted({x['date'] for x in audit})
                        candidate_dates=sorted({x['date'] for x in audit if x['selected']})
                        default_date=candidate_dates[-1] if candidate_dates else dates[-1]
                        pick_date=st.selectbox('Inspect selection date',dates,index=dates.index(default_date))
                        selection_table([r for r in audit if r['date']==pick_date],height=280)
                        if selected!='ROUTER':st.caption('Choose the ROUTER audit to hand code-permitted candidates to C2; fixed strategies are comparison baselines.')
                        selected_here=[r for r in audit if r['date']==pick_date and r['selected']]
                        if st.button('Research automatically selected stocks with C2',disabled=selected!='ROUTER' or not bool(selected_here)):
                            st.session_state['selection_research_settings']={'start':result['period']['start'],'end':pick_date,'capital':result['settings']['initial_capital'],'run_id':result['run_id']}
                            st.session_state['open_research_workspace']=True
                            st.rerun()
            st.markdown("##### Simulated order ledger")
            ledger=result.get("ledgers",{}).get(selected,[])
            render_table(ledger,"BUY, SELL_SIGNAL, SELL_STOP are synthetic/historical fills; protective stops may gap through their levels.",height=320)
            if ledger: st.download_button("Download trade ledger CSV",pd.DataFrame(ledger).to_csv(index=False),file_name=f"aegistrade_{selected}_trades.csv",mime="text/csv")
            st.download_button("Download complete simulation JSON",json.dumps(result,indent=2),file_name=f"aegistrade_simulation_{result['run_id'][:8]}.json",mime="application/json")
    with st.expander("How should I interpret the backtest?",expanded=True):
        st.markdown("**Ending portfolio:** cash plus marked-to-market shares. **Total return:** percent change from starting capital. **Maximum drawdown:** worst peak-to-trough portfolio fall. **Sharpe:** ratio based on historical daily returns. **Fees/slippage:** reduce simulated outcomes. **Limitations:** no real fills, no live broker, no forecast of future profits. Use out-of-sample real data before making academic performance claims.")

elif page == "AI Agent Experiments":
    heading("GenAI and agentic AI experiments", "Compare strategy-routing research on the SAME scenarios. C0 uses no LLM; C1 is one tool-using agent; C2 coordinates market, strategy and critic specialists. Both share an eight-call ceiling per case. NO TRADES ARE PLACED.")
    st.info("This experiment evaluates AI decision support, not portfolio returns. Portfolio returns are evaluated in Strategy Backtests → C2 historical portfolio. Choose C2 to demonstrate model-selected tools and observation-driven decisions.")
    with st.container(border=True):
        a,b=st.columns(2)
        inference=health.get("inference",{})
        a.metric("Inference backend", inference.get("backend","openrouter"))
        b.metric("Inference enabled and ready", "Yes" if health.get("llm_experiments_enabled") else "No")
        st.caption(inference.get("reason", "Check the selected backend configuration."))
        if inference.get("backend")=="codex_cli":
            st.info("Uses your signed-in Codex CLI and ChatGPT plan allowance. Limits count CLI invocations, not internal provider requests. Response-token settings are guidance, not a hard provider token cap. Plus limits may pause the demo; per-run USD billing is unavailable.")
        if not health.get("llm_experiments_enabled"):
            st.caption("To activate C1/C2: select AEGIS_LLM_BACKEND, complete its key or Codex login setup, set AEGIS_ENABLE_LLM_EXPERIMENTS=true in .env, then restart the API. Never paste account credentials into this page.")
    from datetime import date
    selection_settings=st.session_state.get('selection_research_settings',{})
    st.info("C2 checks dated company evidence with a 15:30 IST cutoff. Strong trend and RSI-reversion entries may follow the technical signal with explicitly incomplete coverage after attempted research, provided no concrete adverse event remains unresolved. Breakouts require dated corroboration. A supported adverse finding blocks entry and requires an EXIT for a holding after critic validation. Independent press coverage is not assumed.")
    with st.expander('Historical company research — prepare before paid calls'):
        company_symbol=st.selectbox('Company evidence symbol',universe['symbols'],key='company_symbol')
        company_day=st.date_input('Company evidence decision date',value=date.fromisoformat(selection_settings.get('end') or universe['last_date']),key='company_day')
        st.caption('Prepares bounded official filings and issuer releases from a 180-day window, reusing cached attachments. Financial/news selections plus risk-matched sources can total up to 14 PDFs. No generation calls; extraction and coverage can remain incomplete. Choose a valid market session.')
        refresh_company=st.checkbox('Refresh existing company archive pack',value=False)
        b1,b2=st.columns(2)
        if b1.button('Prepare historical company evidence',disabled=not bool(reviewer_token)):
            try:
                with st.spinner('Reading historical exchange filings and issuer news...'):
                    st.session_state['company_pack']=post('/company/research/prepare',{'symbol':company_symbol,'signal_date':company_day.isoformat(),'refresh':refresh_company},reviewer_token,timeout=540)
            except Exception as exc:fail('Company archive preparation failed; no model calls were made.',exc)
        if b2.button('Inspect cached company evidence'):
            try:st.session_state['company_pack']=get('/company/research?symbol='+quote(company_symbol)+'&signal_date='+company_day.isoformat())
            except Exception as exc:fail('Could not inspect company evidence.',exc)
        pack=st.session_state.get('company_pack')
        if pack and pack.get('symbol')==company_symbol and pack.get('decision_at','')[:10]==company_day.isoformat():
            st.write(pack['symbol']+' financial coverage: '+pack['status']+' | Decision cutoff: '+pack['decision_at'])
            st.write('Adverse-disclosure scan ready: '+('Yes' if pack.get('adverse_scan',{}).get('ready') else 'No — eligible C2 cases can attempt dated web retrieval'))
            if pack.get('adverse_scan'):st.json(pack['adverse_scan'])
            if pack.get('web_scan'):
                st.write('Dated web scan: '+('Validated bounded evidence' if pack['web_scan'].get('ready') else 'Insufficient evidence after search'))
                st.json(pack['web_scan'])
            for reason in pack.get('reasons',[]):st.warning(reason)
            for doc in pack.get('documents',[]):
                st.markdown('**'+doc['id']+' — '+doc['kind']+'**')
                st.write(doc['title']);st.caption('Available '+doc['available_at']+' | '+doc['extraction_status'])
                st.link_button('Open original filing',doc['source_url'])
                st.write(doc.get('excerpt',''))
            st.caption(' '.join(pack.get('limitations',[])))
    with st.expander('Automatic stock shortlist before paid research'):
        screening_capital=st.number_input('Reference capital for stock screening (₹)',min_value=1000.,max_value=100000000.,value=float(selection_settings.get('capital',200000.)),step=10000.)
        if st.button('Inspect latest stock screening (no model calls)'):
            try:
                preview_date=st.session_state.get('ai_eval_end') or selection_settings.get('end') or universe['last_date']
                st.session_state['selection_preview']=post('/market/selection',{'asof':preview_date.isoformat() if hasattr(preview_date,'isoformat') else preview_date,'reference_capital':screening_capital})
            except Exception as exc:fail('Stock screening failed.',exc)
        if st.session_state.get('selection_preview'):
            st.caption('Screening as of '+st.session_state['selection_preview']['asof']+' (latest submitted case date).')
            selection_table(st.session_state['selection_preview']['audit'],height=300)
    try:
        memory_status=get('/research/experiments/preflight').get('memory',{})
    except Exception as exc:
        memory_status={'available':False,'reason':'Could not check the lesson playbook. Keep memory off and retry after checking the API.'}
    memory_available=bool(memory_status.get('available'))
    if not memory_available:st.session_state['ai_use_memory']=False
    with st.form("agent_comparison_form"):
        s1,s2,s3=st.columns(3)
        with s1:
            cfg=st.selectbox("Experiment configuration",["C2","C0","C1","ALL"],help="ALL runs the same cases through all three configurations (up to 16 total cloud calls per case).")
            count=st.number_input("Research cases to test",min_value=1,max_value=3,value=1,step=1,
                                   help="UI budget cap: at most 3 cases. Use CLI for larger controlled experiments.")
        with s2:
            first=date.fromisoformat(universe.get("provenance",{}).get("requested_start") or universe["first_date"]);last=date.fromisoformat(universe["last_date"])
            eval_start=st.date_input("Earliest case date",value=date.fromisoformat(selection_settings.get("end")) if selection_settings.get("end") else first,min_value=first,max_value=last,key="ai_eval_start")
            eval_end=st.date_input("Latest case date",value=date.fromisoformat(selection_settings.get("end")) if selection_settings.get("end") else last,min_value=first,max_value=last,key="ai_eval_end")
        with s3:
            token_cap=st.selectbox("Response-token budget per case (CLI: guidance)",[4800,6400],index=0)
            st.caption("Maximum attempted inference units: 0 for C0, 8 per case for C1 or C2, 16 per case for ALL. C2 normally uses six units. OpenRouter units are HTTP requests; Codex units are CLI invocations.")
        automatic_research_selection=st.checkbox("Research automatically ranked eligible stocks",value=True)
        use_memory=st.checkbox("Use frozen human-reviewed lessons",value=False,key="ai_use_memory",disabled=not memory_available)
        if not memory_available:st.caption(memory_status.get("reason","No frozen reviewed playbook is available."))
        is_paid=cfg!="C0"
        consent=st.checkbox("I authorize this run to use the selected inference backend, subject to the displayed allowance",value=False,disabled=not is_paid)
        preview_agent=st.form_submit_button("Preview selected-date stock shortlist (no model calls)",use_container_width=True)
        run_agent=st.form_submit_button("Run AI experiment",type="primary",use_container_width=True)
    budget_calls=int(count)*{"C0":0,"C1":8,"C2":8,"ALL":16}[cfg]
    st.caption(f"Maximum attempted inference units for these settings: {budget_calls}. Reported provider usage/cost may be incomplete.")
    with st.expander("Plan and permissions before running"):
        st.json({'configuration':cfg,'objective':'Explain a code-permitted historical strategy route',
                 'steps':['Market specialist: technical + dated company evidence MCP','Strategy specialist: strategy + policy MCP','Compliance critic: company + strategy + policy MCP','Deterministic final guard'] if cfg=='C2' else ['Single agent with all read tools'] if cfg=='C1' else ['Deterministic reference'],
                 'maximum_inference_units':budget_calls,'inference':health.get('inference'),'model':health.get('agent_model'),'writes_allowed':False})
    if preview_agent:
        if eval_start>eval_end:st.error('The earliest case date must be on or before the latest case date.')
        else:
            try:
                st.session_state['selection_preview']=post('/market/selection',{'asof':eval_end.isoformat(),'reference_capital':float(screening_capital)})
                st.success('Stock shortlist as of '+st.session_state['selection_preview']['asof']+'. No archive download or model call was made.')
                selection_table(st.session_state['selection_preview']['audit'],height=280)
            except Exception as exc:fail('Could not preview the selected-date shortlist.',exc)
    if run_agent:
        if eval_start>eval_end:st.error("Invalid experiment date range")
        elif is_paid and not consent:st.error("Explicit consent is needed before external inference")
        elif is_paid and not reviewer_token:st.error("Enter reviewer token in the sidebar before requesting external inference")
        elif is_paid and not health.get("llm_experiments_enabled"):st.error("The selected inference backend is not enabled and ready. Inspect its status, update .env or login, and restart.")
        else:
            payload={"configuration":cfg,"cases":int(count),"start_date":eval_start.isoformat(),"end_date":eval_end.isoformat(),
                     "consent_to_paid_calls":bool(consent),"max_output_tokens_per_case":int(token_cap),"use_memory":bool(use_memory),"automatic_stock_selection":bool(automatic_research_selection),"reference_capital":float(screening_capital),"selection_run_id":selection_settings.get("run_id") if automatic_research_selection else None}
            try:
                with st.spinner("Running research using the selected backend; this can take several minutes..."):
                    st.session_state["agent_experiment_result"]=post("/research/experiments/run",payload,reviewer_token if is_paid else "",timeout=max(540,int(count)*8*int(health.get("inference",{}).get("timeout_seconds",40))*(2 if cfg=="ALL" else 1)+90))
                st.success("Research comparison completed and saved locally.")
            except Exception as exc: fail("Research experiment could not complete.",exc)
    with st.expander("Load a previously saved agent experiment"):
        try:
            history=get("/research/experiments/recent",timeout=20).get("runs",[])
            if history:
                labels={f"{x['created_utc'][:19]} | {x['settings']['configuration']} | {x['run_id'][:8]}":x['run_id'] for x in history}
                key=st.selectbox("Saved research run",list(labels),key="saved_agent_run")
                if st.button("Load saved research results"):
                    st.session_state["agent_experiment_result"]=get("/research/experiments/result/"+labels[key])
                    st.rerun()
            else:st.caption("No saved research experiments yet.")
        except Exception as exc:fail("Unable to list saved research experiments.",exc)
    experiment=st.session_state.get("agent_experiment_result")
    if experiment:
        st.markdown("#### Research experiment results")
        st.caption(f"Run {experiment['run_id']} | Model: {experiment['model']} | Call budget: {experiment['max_possible_paid_calls']}")
        summary=pd.DataFrame(experiment.get("summary",[]))
        render_table(summary,"Guard pass means agreement with the deterministic routing reference and acceptable citations; not profitable performance.",height=210)
        outputs=experiment.get("outputs",[])
        render_table([{k:v for k,v in item.items() if k in ("case_id","config","market_regime","expected_strategy","selected_strategy","guard_pass","critic_accept","llm_calls","latency_s")} for item in outputs],height=250)
        provider_failures=[u for output in outputs for u in output.get('usage',[]) if u.get('error') or (u.get('http_status') or 0)>=400]
        if provider_failures:
            statuses=sorted({str(u.get('error_code') or u.get('http_status') or 'network/timeout') for u in provider_failures})
            st.error('Inference failed: '+', '.join('HTTP '+s if s.isdigit() else s for s in statuses)+'. No eligible research result was produced for the failed case.')
            if any(str(u.get('error_code','')).startswith('CODEX_') for u in provider_failures):st.info('Check Codex login status, ChatGPT usage allowance and the selected CLI model. Quota failures pause historical runs; restore access before consenting to resume. No automatic switch to OpenRouter occurs.')
            elif any(u.get('http_status')==402 for u in provider_failures):st.info('OpenRouter rejected payment/account access. Check credits, spending limits and model access in your OpenRouter account before another explicitly authorized run.')
            elif any(u.get('http_status')==401 for u in provider_failures):st.info('Check the private OpenRouter API key and restart the API after correcting it.')
            else:st.info('Inspect provider status, model access or connectivity before another explicitly authorized run. Provider requests are not silently retried.')
        elif any(x.get("model_errors") for x in outputs):
            st.warning("One or more model outputs failed validation or policy checks. Inspect details before claiming model improvement.")
        with st.expander("Full agent hand-offs, citations, usage and errors"):
            st.json(outputs)
        for output in outputs:
            if output.get('company_assessment'):
                with st.expander('Company research: '+output.get('case_id','')+' / '+output['config']):
                    st.json(output['company_assessment'])
                    st.caption('Evidence pack: '+str(output.get('company_research',{}).get('pack_sha256')))
                    for doc in output.get('company_research',{}).get('documents',[]):
                        st.write(doc['id']+' | '+doc['title'])
                        st.caption('Available: '+doc['available_at'])
                        st.link_button('Source '+doc['id'],doc['source_url'],key='source_'+output['config']+'_'+output.get('case_id','')+'_'+doc['id'])
        failed_dev=[x for x in outputs if x.get('config')=='C2' and x.get('model_errors')]
        if failed_dev and experiment.get('settings',{}).get('dataset_split')=='development':
            with st.expander("Generate a lesson from a development failure"):
                failure_id=st.selectbox("Failed development case",[x['case_id'] for x in failed_dev])
                reflect_consent=st.checkbox("Authorize one inference unit for reflection",value=False)
                if st.button("Draft lesson for human review",disabled=not (reflect_consent and reviewer_token)):
                    try:
                        draft=post('/lessons/reflect',{'run_id':experiment['run_id'],'case_id':failure_id,'consent_to_paid_calls':True},reviewer_token,timeout=660)
                        st.json(draft)
                        st.info('Review and accept/reject this pending lesson in Learning & Lessons before it can be retrieved.')
                    except Exception as exc:fail('Reflection could not create a lesson.',exc)
        eligible_ai=[x for x in outputs if x.get('config')=='C2' and x.get('guard_pass') and x.get('critic_accept') is True and set(x.get('handoffs',{}))=={'market','strategy','critic'} and x.get('snapshot') and x.get('company_assessment',{}).get('status') in {'SUFFICIENT','LIMITED'}]
        if eligible_ai:
            chosen_ai=st.selectbox("C2 case to review for a simulated proposal",[x['case_id'] for x in eligible_ai])
            if st.button("Use this C2 case in Supervised Trading"):
                st.session_state['linked_research']={'research_run_id':experiment['run_id'],'research_case_id':chosen_ai}
                st.session_state['open_supervised_workspace']=True
                st.rerun()
        st.download_button("Download research results JSON",json.dumps(experiment,indent=2),file_name=f"aegistrade_agents_{experiment['run_id'][:8]}.json",mime="application/json")
    with st.expander("What these experiments demonstrate",expanded=True):
        st.markdown("**C0:** fixed deterministic approved routing, zero LLM calls. **C1:** one agent has all read tools. **C2:** a deterministic LangGraph supervisor coordinates three LLM specialists: market, strategy and compliance critic. Each selects its own MCP tools and returns a typed hand-off. Both configurations share the same model, available tools and eight-call budget. Expand the full results to inspect its tool trace. ALL runs C0, C1 and C2 on identical cases. **Policy guard:** all proposals must match code-approved routing and cite retrieved policy IDs. **Research scope:** these agents never submit orders. Record success counts, model errors, latency, call totals and provider token usage. For the final capstone, you still need held-out cases, a different-family judge, three repeats and fair-budget comparisons.")

elif page == "Supervised Trading":
    heading("Supervised trade workflow", "Generate a simulated BUY proposal, inspect the exact payload and demonstrate approve / edit / reject.")
    st.warning("Approvals affect only the local simulated broker. This application cannot trade real securities.")
    st.caption("The capital reference below sizes ONE proposed order. It is not yet a persistent forward paper-trading portfolio or the historical simulation ledger.")
    with st.container(border=True):
        capital_ref=st.number_input("Reference capital for this supervised proposal (₹)",min_value=1000.0,max_value=100000000.0,
                                    value=float(st.session_state.get("simulation_result",{}).get("settings",{}).get("initial_capital",100000.0)),step=10000.0,key="trade_capital_reference")
        link=st.session_state.get('linked_research')
        if not link:st.info("Complete C2 in AI Agent Experiments, then select Use this C2 case in Supervised Trading. Approval is unavailable until research passes.")
        if link:st.info(f"Linked case: {link['research_case_id']}. Code will recheck the snapshot and entry signal before proposing an order.")
        stale = st.checkbox("Inject stale quote (expect rejection)", key="trade_stale")
        timeout = st.checkbox("Inject timeout after simulated commit (expect reconciliation)", key="trade_timeout")
        if st.button("Prepare researched order for human review", type="primary", use_container_width=True, disabled=not bool(link)):
            try:
                payload = {
                    "stale_seconds": 10000 if stale else 0,
                    "inject_timeout": timeout,
                    "disable_llm": True,
                    "capital_reference": float(capital_ref),
                }
                payload.update(link)
                with st.spinner("Generating the trade proposal..."):
                    st.session_state["aegis_workflow"] = post("/workflow/start", payload, timeout=120)
                st.success("Workflow created. Review its current state below.")
            except Exception as exc:
                fail("Could not prepare the researched order. Check C2 completion, critic acceptance and entry eligibility.", exc)
    with st.expander("Human emergency control"):
        try:
            controls=get('/controls')
            st.write('Kill switch: '+('ACTIVE' if controls['kill_switch_enabled'] else 'off'))
            stop_reason=st.text_input('Reason for changing the kill switch',key='kill_reason')
            desired_stop=st.checkbox('Block new proposals and simulated submissions',value=controls['kill_switch_enabled'])
            st.caption('Enabling this control invalidates outstanding approval tokens. Disabling it requires fresh order approval.')
            if st.button('Apply emergency control',disabled=not (reviewer_token and len(stop_reason)>=3)):
                post('/controls/kill-switch',{'enabled':desired_stop,'reason':stop_reason},reviewer_token)
                st.rerun()
        except Exception as exc:fail('Unable to load emergency control.',exc)
    result = st.session_state.get("aegis_workflow")
    if result:
        status = result.get("status", "unknown")
        st.markdown("#### Current workflow")
        st.write(f"**Status:** `{status}`")
        st.caption(f"Thread ID: {result.get('thread_id', 'not available')}")
        if status == "WAITING_HUMAN" and result.get("interrupts"):
            pending = result["interrupts"][0]
            order = pending.get("order", {})
            if pending.get('research'):
                st.write(pending.get('explanation',''))
                if pending['research'].get('company_assessment'):st.json(pending['research']['company_assessment'])
                for source in pending['research'].get('company_sources',[]):
                    st.caption(source['id']+' | Available '+source['available_at'])
                    st.link_button(source['title'],source['source_url'],key='approval_source_'+result['thread_id']+'_'+source['id'])
                st.caption('Research source: '+pending['research']['run_id']+' | Citations: '+', '.join(pending.get('citations',[])))
            with st.container(border=True):
                st.markdown("**Exact order awaiting approval**")
                brief = pd.DataFrame([{"Field": k.replace("_", " ").title(), "Value": str(v)} for k, v in order.items()])
                render_table(brief, height=310)
                with st.expander("Verify the complete order payload and approval hash"):
                    st.json(order)
                    st.code(pending.get("payload_hash", ""), language="text")
                if not reviewer_token:
                    st.info("Enter the private AEGIS_REVIEWER_TOKEN in the sidebar before submitting a decision.")
                decision = st.radio("Reviewer decision", ["reject", "approve", "edit"], horizontal=True, key="aegis_review_choice")
                changes = None
                if decision == "edit":
                    base = int(order.get("quantity", 1))
                    quantity = st.number_input("New quantity (requires another approval)", min_value=1, value=base + 1, step=1, key="aegis_revised_quantity")
                    changes = {"quantity": int(quantity)}
                if st.button("Submit reviewer decision", type="primary", disabled=not bool(reviewer_token)):
                    try:
                        st.session_state["aegis_workflow"] = post("/workflow/resume", {
                            "thread_id": result["thread_id"], "decision": decision,
                            "payload_hash": pending.get("payload_hash"), "changes": changes,
                        }, reviewer_token, timeout=120)
                        st.rerun()
                    except Exception as exc:
                        fail("The approval action failed.", exc)
        else:
            outcome = result.get("result", {})
            if status in {"ACCEPTED_SIMULATED", "RECOVERED_FROM_TIMEOUT"}:
                st.success("Authorized simulated order recorded. Inspect Broker Audit for the event.")
            elif status in {"BLOCKED", "REJECTED", "REJECT_STALE", "BLOCKED_NO_FRESH_QUOTE"} or "BLOCK" in status:
                st.warning("No valid execution occurred. The safety gate blocked or rejected this proposal.")
            with st.expander("Workflow trace / detailed response"):
                st.json(outcome or result)
        if result.get("thread_id") and st.button("Load persisted workflow state"):
            try:
                st.session_state["aegis_checkpoint"] = get("/workflow/status/" + result["thread_id"])
            except Exception as exc:
                fail("Could not inspect workflow state.", exc)
    if st.session_state.get("aegis_checkpoint"):
        with st.expander("Latest checkpoint state"):
            st.json(st.session_state["aegis_checkpoint"])
    with st.expander("Suggested safe test sequence", expanded=True):
        st.markdown("**Test A:** Start → Reject. **Test B:** Start → Edit quantity → inspect new hash → Approve or Reject again. **Test C:** Start with stale quote → Approve → inspect blocked result. **Test D:** Start with timeout injected → Approve → inspect reconciliation and audit events.")

elif page == "Policy Knowledge":
    heading("RAG policy knowledge", "Retrieve cited risk and execution rules. Retrieval evidence is separate from final policy enforcement by Python code.")
    status=get('/knowledge/status')
    a,b,c=st.columns(3)
    a.metric('Knowledge passages',status['corpus']['passages'])
    b.metric('Project policies',status['corpus']['project_policy_passages'])
    c.metric('Source-linked references',status['corpus']['external_reference_passages'])
    st.caption('Retrieval pipeline: '+status['pipeline'])
    if status['mode']=='neural' and status['verified_index_for_current_corpus']:
        st.success('Neural retrieval and persistent index verified for this corpus. Answer generation happens in C2 after retrieval.')
    elif status['mode']=='neural':st.info('Neural mode is configured; build/verify the current index before claiming measured quality.')
    else:st.info('Offline retrieval is active. It uses TF-IDF rather than neural embeddings; this status is shown explicitly.')
    st.caption('This is a policy/specification knowledge base. It is not a company-news or financial-statement research service. Searches use local retrieval models, with no paid OpenRouter generation on this screen.')
    query = st.text_input("Search policy documents", value="What happens if an approved order is edited?", key="policy_query")
    historical_sources=st.checkbox('Limit external reference availability to a historical date',value=False)
    if historical_sources:
        from datetime import date as source_date
        external_asof=st.date_input('Historical source cutoff',value=source_date.fromisoformat(universe['last_date']))
        st.caption('Project policies describe the experimental configuration. External references require an eligible publication date, or their first retrieval date when publication is unknown.')
    else:external_asof=None
    top_k = st.slider("Number of passages", min_value=1, max_value=8, value=5, key="policy_topk")
    if st.button("Search policy knowledge", type="primary"):
        try:
            st.session_state["aegis_passages"] = post("/knowledge/search", {"query": query, "top_k": top_k,"as_of":external_asof.isoformat() if external_asof else None})
        except Exception as exc:
            fail("Knowledge search failed.", exc)
    found = st.session_state.get("aegis_passages")
    if found:
        st.caption(f"Retrieval mode: {found.get('mode', 'unknown')} | Corpus: {found.get('corpus_sha256','unknown')[:12]}")
        for item in found.get("results", []):
            with st.expander(f"{item.get('id', 'passage')} — {item.get('title', 'Policy')}", expanded=True):
                st.write(item.get("text", ""))
                st.caption(f"Source: {item.get('source', 'unknown')} | Indexed/reviewed: {item.get('date', 'unknown')} | Type: {item.get('authority','unknown')}")
                if item.get('published_date'):st.caption('Original publication date: '+item['published_date'])
                if item.get('source_url'):st.markdown('[Open original source]('+item['source_url']+')')
                if item.get('source_locator'):st.caption('Code/document reference: '+item['source_locator'])
    else:
        st.info("Try searching for: 'stale quote', 'risk per trade', 'approval hash', or 'stop loss'.")
    st.caption("Citation existence is checked by code. Whether every generated claim is supported still needs human review or a calibrated semantic judge.")

elif page == "Learning & Lessons":
    heading("Portfolio lesson memory", "Completed portfolio → dated source review → accepted conditional lesson → immutable version → selected future C2 run. No generation calls for this workflow.")
    try:
        memory=get('/portfolio-lessons')
        completed=[r for r in get('/simulation/c2/recent').get('runs',[]) if r['status'].startswith('COMPLETED')]
        if completed:
            labels={f"{r['created_utc'][:19]} | {r['settings']['start_date']} to {r['settings']['end_date']} | {r['run_id']}":r['run_id'] for r in completed}
            source=st.selectbox('Completed portfolio to review',list(labels))
            if st.button('Draft portfolio lesson candidates',disabled=not bool(reviewer_token)):
                receipt=post('/portfolio-lessons/draft',{'run_id':labels[source]},reviewer_token)
                st.session_state['portfolio_draft_receipt']=receipt
                st.rerun()
        if st.session_state.get('portfolio_draft_receipt'):st.caption(f"Created {st.session_state['portfolio_draft_receipt']['candidate_count']} pending candidates; zero model calls. Repeated drafting does not duplicate them.")
        candidates=memory.get('candidates',[])
        if candidates:
            render_table([{k:c.get(k) for k in ('id','source_run_id','topic','status','trained_through','lesson')} for c in candidates], 'Review the source cases before accepting a general process lesson.',height=250)
            by_id={c['id']:c for c in candidates}
            cid=st.selectbox('Portfolio lesson candidate',list(by_id));candidate=by_id[cid]
            with st.expander('Dated source cases and original assessment',expanded=True):st.json(candidate['cases'])
            st.caption(candidate['scope'])
            if candidate['status']=='PENDING':
                text=st.text_area('Conditional portfolio lesson',value=candidate['lesson'],max_chars=500,key='portfolio_text_'+cid)
                condition=st.text_input('Applies when',value=candidate['applies_when'],max_chars=240,key='portfolio_condition_'+cid)
                decision=st.radio('Portfolio lesson decision',['REJECT','ACCEPT'],horizontal=True,key='portfolio_decision_'+cid)
                rationale=st.text_input('Portfolio review rationale',max_chars=800,key='portfolio_reason_'+cid)
                if not reviewer_token:
                    st.info('To enable Save, enter your AEGIS_REVIEWER_TOKEN from the project .env file in Reviewer token in the left sidebar, then press Enter. This is separate from your model API key.')
                if len(rationale.strip())<5:
                    st.caption('To enable Save, enter a review rationale of at least 5 characters, then press Enter or click outside the field.')
                if st.button('Save portfolio lesson review',disabled=not bool(reviewer_token) or len(rationale.strip())<5):
                    post('/portfolio-lessons/review',{'candidate_id':cid,'decision':decision,'reason':rationale,'lesson':text,'applies_when':condition},reviewer_token);st.rerun()
            else:st.write('Review: '+candidate.get('review_reason',''))
            accepted=[c['id'] for c in candidates if c['status']=='ACCEPTED']
            freeze_ids=st.multiselect('Accepted portfolio lessons for a new frozen version',accepted)
            if not accepted:
                st.caption('Freeze becomes available after you save at least one ACCEPT review and select that accepted lesson above.')
            elif not freeze_ids:
                st.caption('Select the accepted lessons above to enable Freeze; the reviewer token is also required.')
            if st.button('Freeze portfolio lesson version',disabled=not bool(reviewer_token) or not freeze_ids):
                post('/portfolio-lessons/freeze',{'candidate_ids':freeze_ids},reviewer_token);st.rerun()
        else:st.info('No portfolio lesson candidates yet. Draft from a completed run above; no candidate is automatically accepted.')
        if memory.get('versions'):render_table(memory['versions'],'Versions are immutable. Select one in Strategy Backtests before creating a new C2 run.',height=220)
    except Exception as exc:fail('Portfolio lesson workflow failed.',exc)
    st.divider()
    heading("Reviewed lessons", "Propose Reflexion lessons on development cases, review them as a human and freeze the playbook before held-out evaluation.")
    try:
        current = get("/lessons")
    except Exception as exc:
        fail("Unable to load lessons.", exc)
        st.stop()
    frozen = current.get("frozen")
    if frozen:
        st.success("Playbook frozen: new lessons cannot be accepted until a new experimental version is created.")
    else:
        st.info("A candidate lesson is not automatically trusted or applied. It must be reviewed.")
    with st.container(border=True):
        topic = st.selectbox("Select failure type", ["ROUTING_MISMATCH", "STALE_DATA", "CITATION_MISSING", "DUPLICATE_ORDER", "BAD_LESSON"], key="lesson_type")
        if st.button("Generate candidate lesson", disabled=not bool(reviewer_token) or bool(frozen)):
            try:
                post("/lessons/candidate", {"error_code": topic}, reviewer_token)
                st.success("Candidate created. Review it below.")
                st.rerun()
            except Exception as exc:
                fail("Cannot propose lesson.", exc)
    all_lessons = current.get("lessons", [])
    if all_lessons:
        render_table(all_lessons, "PENDING lessons require review. REJECTED lessons remain visible for audit.", height=350)
    else:
        st.caption("No lesson proposals yet.")
    pending = [item for item in all_lessons if item.get("status") == "PENDING"]
    if pending and not frozen:
        st.markdown("#### Review a pending lesson")
        id_to_item = {str(x["id"]): x for x in pending}
        lid = st.selectbox("Lesson ID", list(id_to_item), key="lesson_pending_id")
        st.write(id_to_item[lid].get("text", ""))
        review = st.radio("Review decision", ["REJECT", "ACCEPT"], horizontal=True, key="lesson_review_decision")
        reason = st.text_input("Review rationale", key="lesson_rationale", placeholder="e.g., Violates capital protection policy")
        if st.button("Save lesson review", disabled=not bool(reviewer_token) or not reason.strip()):
            try:
                post("/lessons/review", {"lesson_id": lid, "decision": review, "reason": reason}, reviewer_token)
                st.rerun()
            except Exception as exc:
                fail("Lesson review failed.", exc)
    st.divider()
    if not frozen:
        confirm = st.checkbox("I understand freezing prevents further updates to this experimental playbook", key="confirm_freeze")
        if st.button("Freeze approved playbook", disabled=not bool(reviewer_token) or not confirm):
            try:
                st.session_state["freeze_receipt"] = post("/lessons/freeze", {}, reviewer_token)
                st.rerun()
            except Exception as exc:
                fail("Could not freeze playbook.", exc)
    if frozen:
        with st.expander("Frozen playbook metadata"):
            st.json(frozen)
    if st.session_state.get("freeze_receipt"):
        with st.expander("Freeze receipt"):
            st.json(st.session_state["freeze_receipt"])

elif page == "Broker Audit":
    heading("Broker audit log", "Inspect simulated order decisions, exact-payload approval events and reconciliation records.")
    if st.button("Refresh audit events"):
        st.rerun()
    try:
        events = get("/audit/events")
    except Exception as exc:
        fail("Could not read the local event log.", exc)
        st.stop()
    if events:
        event_df = pd.DataFrame(events)
        render_table(event_df.iloc[::-1], "Most recent events first. The event ledger is stored locally in SQLite.", height=425)
        st.download_button("Export events as CSV", event_df.to_csv(index=False).encode("utf-8"), file_name="aegistrade_simulated_audit.csv", mime="text/csv")
        with st.expander("Inspect complete event records"):
            st.json(events[-25:])
    else:
        st.info("The event ledger is empty. Open Supervised Trading, generate an order and approve/reject it, then return here.")
    st.caption("All events in this table refer to a local simulated broker only. No actual trading account is used.")

st.divider()
st.caption("AegisTrade AI • local capstone prototype • synthetic data unless explicitly configured otherwise • not investment advice")
