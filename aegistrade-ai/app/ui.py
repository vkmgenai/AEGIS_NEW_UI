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
    div[class*="st-key-strategy_tile_"] button {min-height:170px; padding:24px; text-align:left; justify-content:flex-start; align-items:flex-start;}
    div[class*="st-key-strategy_tile_"] button p {font-size:1.08rem; line-height:1.65; text-align:left;}
    </style>""",
    unsafe_allow_html=True,
)

from app.client_errors import APIError
from app.live_progress import render_c2_progress
from app.portfolio_view import restore_flow,remember_result,flow_of
from app.backend_compat import compatible_backend,UI_API_CONTRACT

API = os.getenv("AEGIS_API_URL", "http://127.0.0.1:8000").rstrip("/")
PAGES = (
    "Market Data",
    "Overview",
    "Strategy Backtests",
    "AI Agent Experiments",
    "Capstone Evaluation",
    "Policy Knowledge",
    "Learning & Lessons",
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
    labels={'ALREADY_HELD_OR_PENDING':'Already held or pending','ALREADY_HELD':'Already held','INSUFFICIENT_HISTORY':'Insufficient warm-up history',
            'LOW_LIQUIDITY':'Below turnover threshold','REGIME_ABSTAIN':'Regime requires abstention',
            'VOLATILITY_LIMIT':'Volatility limit','UNREVIEWED_PRICE_DISCONTINUITY':'Unreviewed price discontinuity',
            'NO_ENTRY_SIGNAL':'No entry signal','CAPITAL_OR_RISK_LIMIT':'Capital/risk cannot fund one share',
            'POSITION_LIMIT':'Portfolio position limit','DAILY_LOSS_LIMIT':'Daily-loss circuit breaker'}
    display=[]
    for row in rows:
        before_signal=row.get('research_order')=='EVIDENCE_BEFORE_SIGNAL'
        reason='Selected for pre-signal screening; signal and quantity are evaluated later' if row.get('selected') else 'Eligible for a later screening batch'
        display.append({'Stock':row['symbol'],'Rank':row.get('rank'),'Selected':row.get('selected',False),
            'Stage':'Before SMC signal' if before_signal else 'Technical signal shortlist',
            'Strategy':'Not evaluated yet' if before_signal else row.get('strategy','NONE'),
            'Score':None if before_signal else row.get('score'),
            'Estimated shares':None if before_signal else row.get('estimated_quantity_at_signal_close'),
            'Reason':'; '.join(labels.get(r,r) for r in row.get('reasons',[])) or (reason if before_signal else 'Eligible at signal close')})
    render_table(display,caption,height)


def architecture_capability_rows(summary,outputs):
    """Separate reference agreement, evidence work and genuine failures."""
    rows=[]
    for metric in summary.to_dict('records'):
        config=metric.get('config');cases=int(metric.get('cases') or 0)
        items=[x for x in outputs if x.get('config')==config]
        if config=='C0':
            rows.append({'Architecture':'C0 — deterministic reference','Role':'No LLM; secondary reference',
                'Route validation':'Reference by construction','Grounded company evidence':'N/A',
                'Adverse-risk flags':'N/A','Decision coverage':f'{cases}/{cases} routed',
                'Safe evidence abstentions':'N/A','Hard model/policy failures':0})
            continue
        grounded=sum(bool((x.get('company_assessment') or {}).get('citations')) for x in items)
        adverse=sum((x.get('company_assessment') or {}).get('adverse_risk') in {'ADVERSE_EVENT_FOUND','MATERIAL_ADVERSE','CONFIRMED_ADVERSE'} for x in items)
        decisions=sum((x.get('portfolio_action') or x.get('handoffs',{}).get('strategy',{}).get('payload',{}).get('portfolio_action')) in {'ENTER','EXIT','HOLD'} for x in items)
        abstain=sum((x.get('failure') or {}).get('category')=='EVIDENCE' for x in items)
        hard=sum(bool(x.get('model_errors')) and (x.get('failure') or {}).get('category')!='EVIDENCE' for x in items)
        rows.append({'Architecture':('C1 — single-agent baseline' if config=='C1' else 'C2 — multi-agent team'),
            'Role':'One agent with the complete shared tool set' if config=='C1' else 'Supervisor + market, strategy and critic specialists',
            'Route validation':f"{int(metric.get('guard_pass_count') or 0)}/{cases-abstain} decided cases passed"+(f", {abstain} abstained" if abstain else ''),
            'Grounded company evidence':f'{grounded}/{cases}','Adverse-risk flags':adverse,
            'Decision coverage':f'{decisions}/{cases}','Safe evidence abstentions':abstain,
            'Hard model/policy failures':hard})
    return rows


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


@st.fragment(run_every="15s")
def notification_bell(workspace_key: str):
    """Read-only local alert inbox; approvals remain on Strategy Backtests."""
    try:inbox=get('/simulation/c2/notifications',timeout=8)
    except Exception:return
    alerts=inbox.get('notifications',[]);ids={x['notification_id'] for x in alerts}
    seen=set(st.session_state.get('seen_human_override_notifications',[]));new=ids-seen
    if new:
        st.toast('🔔 C2 requires human review for '+str(len(new))+' decision'+('s' if len(new)!=1 else '')+'.')
        st.session_state['seen_human_override_notifications']=sorted(seen|new)
    with st.popover('🔔 '+str(len(alerts)) if alerts else '🔔',help='C2 human-review notifications'):
        st.markdown('**Human-review inbox**')
        if not alerts:st.caption('No C2 run is waiting for human intervention.')
        for alert in alerts:
            label=str(alert.get('symbol'))+' · '+str(alert.get('proposed_action'))+' · '+str(alert.get('signal_date'))
            st.write('**'+label+'**')
            if alert.get('signal_close_price') is not None:
                price_note='Signal close ₹'+f"{float(alert['signal_close_price']):,.2f}"
                if alert.get('entry_price') is not None:price_note+=' · Entry ₹'+f"{float(alert['entry_price']):,.2f}"
                st.caption(price_note)
            st.caption(('Linked exit confirmation' if alert.get('review_trigger')=='LINKED_POSITION_EXIT' else 'Evidence-block review')+' · Run '+alert['run_id'][:12])
            if st.button('Open review',key='open_override_'+alert['notification_id'],use_container_width=True):
                result=get('/simulation/c2/status/'+alert['run_id'],timeout=60)
                remember_result(st.session_state,result)
                st.session_state['portfolio_job_C2_next']=alert['run_id']
                st.session_state['portfolio_new_session_C2']=False
                st.session_state['strategy_backtest_view']='portfolio'
                st.session_state[workspace_key]='Strategy Backtests'
                st.rerun()


# Navigation is in the main content area so it remains accessible even when the
# sidebar collapses on a narrow or zoomed browser viewport.
with st.sidebar:
    st.title("🛡️ AegisTrade AI")
    st.caption("CAPSTONE • RESEARCH PROTOTYPE")
    st.info("SIMULATION ONLY — No live broker connection.")
    reviewer_token = os.getenv('AEGIS_REVIEWER_TOKEN','')
    st.caption('Local reviewer authentication: '+('configured' if reviewer_token else 'not configured'))
    if not reviewer_token:st.warning('Set AEGIS_REVIEWER_TOKEN in the private .env and restart. The secret is intentionally not entered or displayed in the UI.')
    st.divider()
    st.caption("Local API")
    st.code(API, language="text")
    st.caption("If controls are hidden, widen the browser, use 100% zoom, or expand the sidebar with the arrow at the top left.")

title_column,bell_column=st.columns([12,1],vertical_alignment='top')
with title_column:
    st.title("AegisTrade AI")
    st.caption("Automatic stock screening · C2 evidence research · Human-governed simulated actions")
with bell_column:
    st.write('')
    with st.container(key='notification_anchor'):
        notification_bell('aegis_workspace')
if st.session_state.pop('open_research_workspace',False):
    st.session_state['aegis_workspace']='AI Agent Experiments'
    params=st.session_state.get('selection_research_settings',{})
    if params:
        from datetime import date as research_date
        st.session_state['ai_eval_start']=research_date.fromisoformat(params['start'])
        st.session_state['ai_eval_end']=research_date.fromisoformat(params['end'])
if st.session_state.pop('open_supervised_workspace',False):
    st.session_state['aegis_workspace']='AI Agent Experiments'
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

PROVIDER_LABELS={'claude_cli':'Claude (Claude CLI login)','codex_cli':'ChatGPT (Codex CLI login)','openrouter':'OpenRouter (API key)'}
PROVIDER_NOTES={
    'claude_cli':'Uses your signed-in Claude CLI and Claude plan allowance. Limits count CLI invocations, not internal provider requests. Response-token settings are guidance, not a hard provider token cap. Plan limits may pause a run; the USD figure the CLI reports is notional and is not billed.',
    'codex_cli':'Uses your signed-in Codex CLI and ChatGPT plan allowance. Limits count CLI invocations, not internal provider requests. Response-token settings are guidance, not a hard provider token cap. Plus limits may pause the demo; per-run USD billing is unavailable.',
    'openrouter':'Uses the OpenRouter API key in .env. Limits count HTTP model requests and cost is the usage the provider reports.'}


def provider_selector(place):
    """Dropdown to run the AI flows on Claude, ChatGPT or OpenRouter. Returns the active backend name."""
    active=health.get('inference',{}).get('backend','openrouter')
    if not health.get('inference_backend_switch_supported'):
        st.caption('Inference provider: '+PROVIDER_LABELS.get(active,active)+'. Restart the API from this project folder to choose the provider here.')
        return active
    try:listing=get('/inference/backends',timeout=40)
    except Exception as exc:
        fail('Could not load the inference providers.',exc);return active
    options={o['backend']:o for o in listing.get('options',[])}
    names=[n for n in PROVIDER_LABELS if n in options]
    if not names:return active
    active=listing.get('selected',active)
    key='provider_'+place
    def apply_choice():
        # Runs only when the person changes the dropdown, so a run can never start on the previous provider by mistake.
        wanted=st.session_state.get(key)
        if not reviewer_token:
            st.session_state['provider_notice']='The provider has NOT changed: reviewer authorization is not configured.';return
        try:
            post('/inference/backend',{'backend':wanted},reviewer_token,timeout=40)
            st.session_state['provider_notice']='Provider changed to '+PROVIDER_LABELS.get(wanted,str(wanted))+'. New runs use it.'
        except Exception as exc:st.session_state['provider_notice']='The provider could NOT be changed: '+str(exc)[:200]
    st.session_state[key]=active if active in names else names[0]
    a,b=st.columns([3,1])
    chosen=a.selectbox('Run AI agents using',names,key=key,on_change=apply_choice,
        format_func=lambda n:PROVIDER_LABELS[n]+(' — ready' if options[n].get('ready') else ' — not ready'),
        help='The choice applies as soon as you pick it. Claude and ChatGPT use the login of their command-line tool on this computer. OpenRouter uses the API key in .env. No key or password is entered here.')
    picked=options[chosen]
    b.write('');b.write('');b.success('Active')
    notice=st.session_state.pop('provider_notice',None)
    if notice:(st.error if 'NOT' in notice else st.success)(notice)
    st.caption(('Ready. ' if picked.get('ready') else 'Not ready. ')+str(picked.get('reason',''))+' Model: '+str(picked.get('model','unknown'))+'.')
    st.caption(PROVIDER_NOTES[chosen]+' A saved C1 or C2 run stays tied to the provider it started on: switch back to resume it, or start a new run.')
    return active


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
        st.info("Next: run Strategy Backtests, inspect the stock-selection audit, then send selected candidates through C2. AI Agent Experiments run to completion without pausing. Human intervention is available only in a C2 portfolio run in Strategy Backtests with HUMAN_EVIDENCE_OVERRIDE enabled.")

elif page == "Strategy Backtests":
    heading("C2 historical portfolio", "Run the end-to-end multi-agent portfolio simulation with dated evidence, deterministic financial controls and optional human evidence overrides.")
    is_c2=True
    is_ai=True
    if is_ai:
        with st.container(border=True):provider_selector('backtest')
    flow_label='C2'
    view_flow=flow_label if is_ai else 'TECHNICAL'
    new_session_key='portfolio_new_session_'+view_flow
    if is_ai and st.button('Start a new '+flow_label+' session',help='Clears the displayed selection only. Saved runs remain available below and no model call is made.'):
        results=dict(st.session_state.get('portfolio_results',{}));results.pop(view_flow,None)
        st.session_state['portfolio_results']=results
        if flow_of(st.session_state.get('simulation_result'))==view_flow:st.session_state.pop('simulation_result',None)
        st.session_state.pop('portfolio_job_'+flow_label,None)
        st.session_state[new_session_key]=True
        st.rerun()
    try:current=restore_flow(st.session_state,view_flow,get,auto_restore_saved=not st.session_state.get(new_session_key,False))
    except Exception as exc:
        current=st.session_state.get('portfolio_results',{}).get(view_flow)
        fail('Could not restore the selected flow. Use its saved-run controls below.',exc)
    if is_ai:
        prefix='/simulation/'+flow_label.lower()
        def load_ai_job(value):
            loaded=get(prefix+'/status/'+value)
            if flow_of(loaded)!=flow_label:raise ValueError('This run belongs to a different flow. Select that flow to open it.')
            return remember_result(st.session_state,loaded)
        st.caption('Technical shortlist → dated RAG/web evidence → market specialist → strategy specialist → independent critic → code checks → later-open fill')
        with st.container(border=True):
            st.subheader(flow_label+' live run progress')
            if current:render_c2_progress(current,get)
            else:
                st.progress(0,text='No '+flow_label+' run selected')
                st.info('Start one below or open a saved '+flow_label+' run. No inference is started automatically.')
            with st.expander(flow_label+' saved runs, refresh, pause and resume',expanded=current is None):
                job_key='portfolio_job_'+flow_label;next_key=job_key+'_next'
                if st.session_state.get(next_key):st.session_state[job_key]=st.session_state.pop(next_key)
                st.session_state.setdefault(job_key,current['run_id'] if current else '')
                job_id=st.text_input(flow_label+' portfolio run ID',key=job_key)
                try:
                    jobs=[x for x in get(prefix+'/recent').get('runs',[]) if x.get('settings',{}).get('research_flow','C2')==flow_label]
                    if jobs:
                        labels={x['created_utc'][:19]+' | '+x['status']+' | '+x['run_id']:x['run_id'] for x in jobs}
                        choice=st.selectbox('Saved '+flow_label+' portfolio',list(labels),key='saved_job_'+flow_label)
                        if st.button('Open saved '+flow_label+' portfolio'):
                            load_ai_job(labels[choice]);st.session_state[next_key]=labels[choice];st.rerun()
                except Exception as exc:fail('Could not list saved '+flow_label+' runs.',exc)
                if st.button('Refresh AI progress',disabled=not bool(job_id)):
                    try:load_ai_job(job_id);st.rerun()
                    except Exception as exc:fail('Unable to load '+flow_label+' progress.',exc)
                more=st.number_input('Additional inference units on resume',min_value=0,max_value=2400,value=48,step=8,key='resume_units_'+flow_label)
                resume_consent=st.checkbox('I authorize resuming this historical job with the additional allowance',value=False,key='resume_consent_'+flow_label)
                c_resume,c_pause=st.columns(2)
                if c_resume.button('Resume '+flow_label+' portfolio',disabled=not bool(job_id and reviewer_token and resume_consent)):
                    try:
                        load_ai_job(job_id)
                        remember_result(st.session_state,post(prefix+'/resume/'+job_id,{'additional_model_calls':int(more),'consent_to_paid_calls':True},reviewer_token));st.rerun()
                    except Exception as exc:fail('Resume rejected; inspect run status, configuration and consent.',exc)
                if c_pause.button('Pause '+flow_label+' portfolio',disabled=not bool(job_id and reviewer_token)):
                    try:load_ai_job(job_id);post(prefix+'/pause/'+job_id,{},reviewer_token);st.info('Pause requested at the next safe boundary.')
                    except Exception as exc:fail('Pause request failed.',exc)
    st.caption('This page is the end-to-end C2 portfolio demonstration. The controlled C0/C1/C2 architecture comparison belongs only in AI Agent Experiments. No live order is placed.')
    if is_ai:
        inf=health.get('inference',{})
        st.caption('Long C2 periods consume provider allowance. Start with a short window; paused runs can be resumed from the progress panel.')
    from datetime import date, timedelta
    first = date.fromisoformat(universe.get("provenance",{}).get("requested_start") or universe["first_date"])
    last = date.fromisoformat(universe["last_date"])
    selected_book=None
    human_override_mode=False
    if is_c2:
        with st.expander('Optional evaluation controls',expanded=False):
            if health.get('portfolio_memory_supported'):
                try:
                    books=get('/portfolio-lessons').get('versions',[])
                    choices={'No reviewed lesson memory':None,**{f"{b['created_at'][:19]} | {b['lesson_count']} lessons | trained through {b['trained_through']} | {b['id'][:8]}":b for b in books}}
                    selected_book=choices[st.selectbox('Frozen portfolio lesson version',list(choices))]
                    st.caption('Leave this off for the standard demo. Select a frozen version only for the documented memory-on evaluation.')
                except Exception as exc:fail('Could not load portfolio lesson versions.',exc)
            human_override_mode=st.checkbox('Enable HUMAN_EVIDENCE_OVERRIDE study',value=False,
                help='Pauses only evidence-insufficient technical BUY/SELL blocks. Stops, targets and hard safety blocks cannot be overridden.')
    # Fixed capstone policy: these constants remain in the submitted payload and
    # saved ledger, but are deliberately not tunable in the demonstration UI.
    risk_pct=1.0; automatic_selection=True; sim_mode='ROUTER'; slippage_bps=10.0
    stop_enabled=True; stop_method='ATR distance'; initial_atr=2.0; initial_percent=5.0
    take_profit=8.0; trailing_enabled=True; trailing_multiple=2.0
    smc_reentry_enabled=True; smc_reentry_window=10
    breakout_risk=.5; breakout_method='ATR distance'; breakout_atr=2.5
    breakout_percent=5.; breakout_trail=2.5; breakout_activation=1.; breakout_reentry=True
    screen_count=3; review_every=5; development_memory=False
    with st.expander('Fixed, reproducible simulation policy',expanded=False):
        st.markdown('''
- ROUTER selects among EMA trend, EMA pullback, RSI reversion, breakout and SMC.
- Normal risk budget: **1% per trade**; breakout risk budget: **0.5%**.
- Protective stop: **2× ATR14**; breakout stop: **2.5× ATR14**.
- Trailing stop: **2× ATR14**; breakout trail: **2.5× ATR14 after 1R**.
- Net take-profit target: **8%**; one confirmed stopped-setup recovery within **10 sessions**.
- Slippage: **10 bps per transaction** plus fixed modeled NSE delivery charges.
- C2 screens up to **3 candidates per session** and reviews holdings every **5 sessions**.
''')
        st.caption('These assumptions are recorded in every result and fixed to prevent post-hoc tuning of the C2 portfolio demonstration.')
    with st.form("capital_simulation_form"):
        st.markdown("#### Run settings")
        c1,c2=st.columns(2)
        with c1:
            capital=st.number_input("Initial capital (₹)",min_value=1000.0,max_value=100000000.0,value=200000.0,step=10000.0)
        with c2:
            start_date=st.date_input("Simulation start",value=first,min_value=first,max_value=last)
            end_date=st.date_input("Simulation end",value=last,min_value=first,max_value=last)
        if is_ai:
            max_calls=st.number_input('Total inference allowance (requests or CLI invocations)',min_value=8,max_value=2400,value=48,step=8)
            if selected_book:
                development_memory=st.checkbox('This is a development replay whose dates may overlap lesson training',value=False)
                st.caption('Pinned lesson version: '+selected_book['sha256']+' · trained through '+selected_book['trained_through'])
            c2_consent=st.checkbox('I authorize external inference for this historical portfolio, up to the displayed allowance',value=False)
        approve_rules=st.checkbox("I approve these stock-selection, risk and cost assumptions for automatic historical replay",value=False)
        run_sim=st.form_submit_button("Run C2 backtest" if is_ai else "Run C0 backtest",type="primary",use_container_width=True)
    if run_sim:
        if not approve_rules:st.error("Approve the displayed replay assumptions before running the historical simulation.")
        elif smc_reentry_enabled and not health.get('smc_reentry_supported',False):st.error('Restart API/dashboard to load SMC recovery support before starting this run.')
        elif not health.get('breakout_reentry_supported',False):st.error('Restart the API and dashboard to load breakout risk and re-entry support before starting a new run.')
        elif not health.get('configurable_stop_loss_supported',False):st.error('The backend has not loaded configurable initial stops yet. Finish or pause active work, then restart the API and dashboard together before starting a new run.')
        elif not health.get('fresh_adverse_profit_policy_supported',False):st.error('Restart the API and dashboard together to load fresh entry review, adverse-event research and take-profit rules before starting this new run.')
        elif trailing_enabled and not health.get('trailing_stop_supported',False):st.error('The running backend does not yet support trailing stops. Restart the API and dashboard together before starting this run.')
        elif is_ai and (not reviewer_token or not c2_consent):st.error('Configured reviewer authorization and explicit inference consent are required.')
        elif start_date>end_date:
            st.error("The simulation start date must be before the end date.")
        else:
            payload={"initial_capital":float(capital),"start_date":start_date.isoformat(),"end_date":end_date.isoformat(),
                     "stop_loss_enabled":bool(stop_enabled),"smc_reentry_enabled":bool(stop_enabled and smc_reentry_enabled),"smc_reentry_window_sessions":int(smc_reentry_window),"breakout_risk_percent":float(breakout_risk),"breakout_stop_loss_mode":"ATR" if breakout_method=='ATR distance' else "PERCENT","breakout_stop_loss_percent":float(breakout_percent),"breakout_initial_stop_atr_multiple":float(breakout_atr),"breakout_trailing_atr_multiple":float(breakout_trail),"breakout_trailing_activation_r":float(breakout_activation),"breakout_reentry_enabled":bool(stop_enabled and breakout_reentry),"risk_percent":float(risk_pct),"mode":sim_mode,"automatic_stock_selection":bool(automatic_selection),"slippage_bps":float(slippage_bps),
                     "stop_loss_mode":"ATR" if stop_method=="ATR distance" else "PERCENT","initial_stop_atr_multiple":float(initial_atr),"stop_loss_percent":float(initial_percent),"take_profit_percent":float(take_profit),"review_after_gap":True,"trailing_stop_enabled":bool(stop_enabled and trailing_enabled),"trailing_atr_multiple":float(trailing_multiple)}
            try:
                if is_ai:
                    payload.update(consent_to_paid_calls=True,approve_historical_rules=True,max_model_calls=int(max_calls),holding_review_sessions=int(review_every),portfolio_playbook_id=selected_book['id'] if selected_book else None,memory_allow_development_replay=bool(development_memory),human_override_mode=bool(human_override_mode))
                    if is_ai:payload['screening_candidates_per_session']=int(screen_count)
                    with st.spinner('Creating checkpointed '+flow_label+' portfolio job...'):
                        st.session_state['simulation_result']=post('/simulation/'+flow_label.lower()+'/run',payload,reviewer_token,timeout=120)
                    remember_result(st.session_state,st.session_state['simulation_result'])
                    st.session_state.pop(new_session_key,None)
                    st.session_state['portfolio_job_'+flow_label+'_next']=st.session_state['simulation_result']['run_id']
                    st.rerun()
                else:
                    with st.spinner("Replaying the selected daily OHLCV period..."):
                        st.session_state["simulation_result"]=post("/simulation/run",payload,timeout=240)
                    remember_result(st.session_state,st.session_state["simulation_result"])
                    st.success("C0 Technical baseline completed and saved.")
            except Exception as exc:
                fail("Portfolio simulation failed. Try a longer date interval (at least 45 sessions).",exc)
    result=st.session_state.get("portfolio_results",{}).get(view_flow)
    with st.expander("Open a previously saved simulation"):
        try:
            previous=get("/simulation/recent").get("runs",[])
            if previous:
                choices={f"{x['created_utc'][:19]} | ₹{x['settings']['initial_capital']:,.0f} | {x['period']['start']}–{x['period']['end']} | {x['run_id'][:8]}":x['run_id'] for x in previous}
                picked=st.selectbox("Saved simulation",list(choices),key="simulation_saved_run")
                if st.button("Load saved simulation"):
                    remember_result(st.session_state,get("/simulation/result/"+choices[picked],timeout=60))
                    st.rerun()
            else: st.caption("No saved simulation runs yet.")
        except Exception as exc: fail("Unable to load saved run list.",exc)
    if result:
        st.divider()
        if result.get('data_provenance',{}).get('universe_id'):
            st.caption('Result universe: '+str(result['data_provenance'].get('universe_name') or result['data_provenance']['universe_id']))
        if result.get('strategy_policies'):
            with st.expander('Strategy risk settings and breakout re-entry watch'):
                st.json(result['strategy_policies'])
                st.json(result.get('breakout_reentry_watches',[]))
        if result.get('smc_reentry_watches'):
            with st.expander('SMC stopped-position recovery watches',expanded=True):
                st.json(result['smc_reentry_watches'])
        if result.get('initial_stop_loss'):
            with st.expander('Initial stop-loss settings'):st.json(result['initial_stop_loss'])
        c2_result='model_usage' in result
        result_flow=result.get('research_flow','C2')
        st.markdown('#### Results — '+result_flow+' historical portfolio' if c2_result else '#### Results — C0 Technical baseline')
        if c2_result and result_flow=='C1':st.caption('Evidence-first single-agent research, followed by code SMC checks. No independent LLM critic. NO_SMC_SIGNAL means evidence passed but price structure did not qualify.')
        if c2_result:
            orchestration=result.get('orchestration',{})
            if orchestration:
                st.caption('Orchestration: '+str(orchestration.get('framework'))+' · '+str(orchestration.get('graph') or 'legacy saved run')+
                    ' · checkpointer: '+str(orchestration.get('checkpointer'))+' · thread: '+str(orchestration.get('thread_id') or 'not applicable'))
            pending_override=result.get('pending_human_override')
            if pending_override:
                if pending_override.get('review_trigger')=='LINKED_POSITION_EXIT':
                    st.warning('C2 recommends SELL for a position opened through HUMAN_EVIDENCE_OVERRIDE. Confirm the linked exit or keep holding; protective code exits never wait.')
                else:
                    st.warning('C2 blocked a technically positive '+pending_override['proposed_action']+' because evidence is insufficient. The original C2 decision remains BLOCKED.')
                with st.container(border=True):
                    st.markdown('#### HUMAN_EVIDENCE_OVERRIDE review')
                    st.write('**'+pending_override['symbol']+' · '+pending_override['proposed_action']+' · '+str(pending_override.get('technical_strategy'))+'**')
                    price_columns=st.columns(3 if pending_override.get('entry_price') is not None else 1)
                    signal_price=pending_override.get('signal_close_price')
                    price_columns[0].metric('Signal-date close',f"₹{float(signal_price):,.2f}" if signal_price is not None else 'Not recorded')
                    if pending_override.get('entry_price') is not None:
                        price_columns[1].metric('Position entry price',f"₹{float(pending_override['entry_price']):,.2f}")
                        change=pending_override.get('gross_position_return_pct_at_signal')
                        price_columns[2].metric('Change since entry',f"{float(change):+.2f}%" if change is not None else 'Not recorded')
                        gross=pending_override.get('gross_position_pnl_at_signal')
                        st.caption('Held quantity: '+str(pending_override.get('quantity'))+' · Gross mark-to-market at signal close: '+(f"₹{float(gross):+,.2f}" if gross is not None else 'not recorded')+'. Actual later-open execution, fees and slippage can change realized P&L.')
                    else:
                        st.caption('This is the completed signal-date close, not the later-open simulated BUY fill price.')
                    st.write(pending_override['blocking_reason'])
                    override_choices=['KEEP_HOLDING','APPROVE_EXIT'] if pending_override.get('review_trigger')=='LINKED_POSITION_EXIT' else ['KEEP_BLOCKED','APPROVE_OVERRIDE']
                    override_display=st.radio('Human intervention',override_choices,horizontal=True,key='portfolio_override_decision')
                    override_decision={'KEEP_HOLDING':'KEEP_BLOCKED','APPROVE_EXIT':'APPROVE_OVERRIDE'}.get(override_display,override_display)
                    override_reviewer=st.text_input('Reviewer name or initials',key='portfolio_override_reviewer')
                    override_reason=st.text_input('Override rationale',key='portfolio_override_reason')
                    st.caption('Protective stop, trailing stop and take-profit exits remain automatic. An approved BUY is linked to all later reviews and its eventual exit.')
                    if st.button('Record HUMAN_EVIDENCE_OVERRIDE decision',type='primary',disabled=not bool(reviewer_token and len(override_reviewer.strip())>=2 and len(override_reason.strip())>=3)):
                        try:
                            updated=post('/simulation/c2/human-override/'+result['run_id'],{'override_id':pending_override['override_id'],'decision':override_decision,
                                'reviewer':override_reviewer,'rationale':override_reason},reviewer_token)
                            remember_result(st.session_state,updated);st.rerun()
                        except Exception as exc:fail('Human evidence override could not be recorded.',exc)
            if result.get('portfolio_memory'):
                with st.expander('Pinned portfolio lesson memory'):st.json(result['portfolio_memory'])
            if result_flow=='C1':
                st.write('**C1 evidence-first signal checks**')
                render_table(result.get('signal_checks',[]),'Only cases that passed dated evidence are checked for SMC. An evidence block is not a negative price signal.',height=240)
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
            with st.expander('AI evidence / entry / holding-review decisions and traces'):
                decisions=result.get('decisions',[])
                st.caption('HOLD keeps the existing shares after a scheduled review; it creates no new trade. Code stops and strategy exits remain active.')
                if any('CONTEXT_BUDGET_EXCEEDED' in ' '.join(d.get('errors',[])) for d in decisions):
                    st.info('A context-budget failure concerns research input size, separately from your inference-call allowance. Refreshing or adding calls does not fix it. Inspect the research trace; after updating an affected backend, start a new run to re-evaluate previously blocked candidates.')
                render_table([{**{k:d.get(k) for k in ['date','symbol','purpose','action','llm_calls','failure_category','research_order','smc_signal','smc_stage']},
                               'evidence_policy':(d.get('company_assessment') or {}).get('adverse_risk',''),
                               'web_search':(d.get('dated_web_search') or {}).get('status',''),'reason':'; '.join(d.get('errors',[])) or d.get('explanation','')} for d in decisions],height=300)
                records=[d for d in decisions if d.get('id')]
                if result.get('news_checks'):
                    with st.expander('Dated issuer-disclosure checks between holding reviews'):
                        render_table([{'date':x.get('date'),'symbol':x.get('symbol'),'status':x.get('status'),
                            'candidates':len(x.get('candidates',[])),'error':x.get('error','')} for x in result['news_checks']])
                if records:
                    choices={d['date']+' '+d['symbol']+' '+d.get('purpose','')+' '+d['id']:d['id'] for d in records}
                    decision_choice=st.selectbox('AI portfolio research record',list(choices))
                    selected_record=next(d for d in records if d['id']==choices[decision_choice])
                    if selected_record.get('smc_context'):
                        st.write('**Code-confirmed SMC setup after company screening**');st.json(selected_record['smc_context'])
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
                    if st.button('Load AI portfolio research trace'):
                        try:st.json(get('/simulation/c2/research/'+result['run_id']+'/'+choices[decision_choice]))
                        except Exception as exc:fail('Unable to read research trace.',exc)
            if result.get('human_override_ledger'):
                with st.expander('HUMAN_EVIDENCE_OVERRIDE lifecycle ledger',expanded=True):
                    render_table(result['human_override_ledger'],'Entry, human decisions, automatic risk exits and later SELL overrides share an immutable override/position ID.',height=300)
                    render_table(result.get('human_override_outcomes',[]),'Only closed positions become eligible for human lesson review. Open positions remain inconclusive.',height=220)
        st.caption(f"Run ID: {result['run_id']} | Sessions: {result['sessions']} | Actual selected period: {result['period']['start']} to {result['period']['end']}")
        metrics=pd.DataFrame(result.get("metrics",[]))
        render_table(metrics, "AI entries require completed dated research; code risk/target exits and holding reviews govern holdings." if c2_result else "C0 uses zero model calls; results include modeled fees and slippage.",height=250)
        if c2_result and 'human_override_total_pnl' in metrics.columns:
            st.caption('Human-override P&L is the contribution of positions opened after HUMAN_EVIDENCE_OVERRIDE approval. It is already included in C2 P&L and must not be added again.')
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
                    st.caption('Pre-signal rows have no estimated share quantity. In C1, these candidates undergo company research before SMC checks; sizing follows only after evidence and signal pass. A shortlist is not an executed order.')
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
    heading("Single-agent versus multi-agent experiments", "C1 is one agent with the complete shared tool set. C2 is a supervisor coordinating market, strategy and critic specialists through typed hand-offs. C0 is a secondary deterministic reference. No live trades are placed.")
    st.info("This is the guideline-required C1 single-agent versus C2 multi-agent comparison. Both receive identical cases, model, dated evidence, available read tools and case-level budget. Human-in-the-loop remains in the C2 portfolio workspace.")
    with st.container(border=True):
        a,b=st.columns(2)
        inference=health.get("inference",{})
        a.metric("Inference provider", PROVIDER_LABELS.get(inference.get("backend","openrouter"),inference.get("backend","openrouter")).split(" (")[0])
        b.metric("Inference enabled and ready", "Yes" if health.get("llm_experiments_enabled") else "No")
        provider_selector('experiments')
        if not health.get("llm_experiments_enabled"):
            st.caption("To activate C1/C2: choose a provider above that shows ready (Claude: run claude auth login in Terminal; ChatGPT: run codex login; OpenRouter: set OPENROUTER_API_KEY in .env), set AEGIS_ENABLE_LLM_EXPERIMENTS=true in .env, then restart the API. Never paste account credentials into this page.")
    from datetime import date, timedelta
    if False:  # Legacy single-stock widgets are hidden; the live comparison is in Strategy Backtests.
        st.markdown('### Single-stock C0 / C2 portfolio comparison')
        st.caption('Runs one stock over one historical window. C0 is the deterministic four-strategy ROUTER; C2 adds dated research, the market/strategy/critic team and SMC. Both share capital, costs, target and stop settings.')
        comparison=st.session_state.get('portfolio_comparison_result')
        top1,top2=st.columns(2)
        if top1.button('Start a new comparison session'):
            st.session_state.pop('portfolio_comparison_result',None);st.session_state.pop('portfolio_comparison_id',None);st.rerun()
        if top2.button('Refresh comparison progress',disabled=not bool(comparison)):
            try:
                run_id=comparison['run_id'];st.session_state['portfolio_comparison_result']=get('/research/portfolio-comparison/status/'+run_id,timeout=90);st.rerun()
            except Exception as exc:fail('Could not refresh the C0/C2 comparison.',exc)
        comp_first=date.fromisoformat(universe.get('provenance',{}).get('requested_start') or universe['first_date'])
        comp_last=date.fromisoformat(universe['last_date'])
        with st.form('single_stock_comparison_form'):
            a,b,c=st.columns(3)
            with a:
                comparison_symbol=st.selectbox('Stock to compare',universe['symbols'],key='comparison_symbol')
                comparison_capital=st.number_input('Comparison capital (₹)',min_value=1000.,max_value=100000000.,value=200000.,step=10000.)
            with b:
                comparison_start=st.date_input('Comparison start',value=comp_first,min_value=comp_first,max_value=comp_last)
                comparison_end=st.date_input('Comparison end',value=comp_last,min_value=comp_first,max_value=comp_last)
            with c:
                comparison_risk=st.number_input('Maximum risk per trade (%)',min_value=.25,max_value=3.,value=1.,step=.25)
                comparison_calls=st.number_input('Inference allowance per AI flow',min_value=8,max_value=2400,value=240,step=8)
            comparison_stop=st.checkbox('Enable comparison stop loss',value=True)
            comparison_stop_pct=st.number_input('Comparison stop loss (%)',min_value=.1,max_value=50.,value=5.,step=.5,disabled=not comparison_stop)
            comparison_profit=st.number_input('Comparison take-profit target (% net)',min_value=.1,max_value=100.,value=8.,step=1.)
            comparison_slippage=st.number_input('Comparison slippage (basis points per transaction)',min_value=0.,max_value=100.,value=10.,step=5.)
            comparison_review=st.number_input('AI holding review interval (sessions)',min_value=1,max_value=60,value=5,step=1)
            comparison_approve=st.checkbox('I approve automatic historical fills under these shared rules')
            comparison_consent=st.checkbox('I authorize C2 inference up to the displayed allowance')
            run_comparison=st.form_submit_button('Run single-stock C0 / C2 comparison',type='primary',use_container_width=True)
        if run_comparison:
            if comparison_start>comparison_end:st.error('Comparison start must be on or before its end.')
            elif not comparison_approve:st.error('Approve the shared historical rules before starting.')
            elif not comparison_consent or not reviewer_token:st.error('Configured reviewer authorization and explicit C2 inference consent are required.')
            elif not health.get('llm_experiments_enabled'):st.error('The selected inference backend is not enabled and ready.')
            else:
                payload={'symbol':comparison_symbol,'start_date':comparison_start.isoformat(),'end_date':comparison_end.isoformat(),
                    'initial_capital':float(comparison_capital),'risk_percent':float(comparison_risk),'stop_loss_enabled':bool(comparison_stop),
                    'stop_loss_percent':float(comparison_stop_pct),'take_profit_percent':float(comparison_profit),'slippage_bps':float(comparison_slippage),
                    'holding_review_sessions':int(comparison_review),'max_model_calls_per_flow':int(comparison_calls),
                    'consent_to_paid_calls':True,'approve_historical_rules':True}
                try:
                    with st.spinner('Creating C0 and checkpointed C2 runs...'):
                        comparison=post('/research/portfolio-comparison/run',payload,reviewer_token,timeout=240)
                    st.session_state['portfolio_comparison_result']=comparison;st.session_state['portfolio_comparison_id']=comparison['run_id'];st.rerun()
                except Exception as exc:fail('Could not start the single-stock comparison.',exc)
        with st.expander('Open a saved single-stock comparison'):
            try:
                saved_comparisons=get('/research/portfolio-comparison/recent').get('runs',[])
                if saved_comparisons:
                    labels={f"{x['created_utc'][:19]} | {x['settings']['symbol']} | {x['settings']['start_date']}–{x['settings']['end_date']} | {x['run_id'][:8]}":x['run_id'] for x in saved_comparisons}
                    selected_comparison=st.selectbox('Saved C0/C2 comparison',list(labels),key='saved_portfolio_comparison')
                    if st.button('Open saved comparison'):
                        st.session_state['portfolio_comparison_result']=get('/research/portfolio-comparison/status/'+labels[selected_comparison],timeout=90);st.rerun()
                else:st.caption('No saved single-stock comparisons yet.')
            except Exception as exc:fail('Could not list saved comparisons.',exc)
        comparison=st.session_state.get('portfolio_comparison_result')
        if comparison:
            st.write('**Comparison status:** '+comparison['status']+' | Run '+comparison['run_id'][:12])
            progress_rows=[]
            for name,flow in comparison['flows'].items():
                metric=flow.get('metrics',{});progress=flow.get('progress',{})
                progress_rows.append({'Flow':name,'Status':flow['status'],'Sessions':f"{progress.get('completed_sessions','all')}/{progress.get('total_sessions','all')}",
                    'Ending equity':metric.get('ending_equity'),'Total return %':metric.get('total_return_pct'),'Max drawdown %':metric.get('max_drawdown_pct'),
                    'Completed trades':metric.get('completed_trades'),'Inference units':flow.get('model_usage',{}).get('attempted_calls',0)})
            render_table(progress_rows,'Partial C2 figures cover processed sessions only. Compare final returns after C2 completes.',height=210)
            curve_rows=[];ledger_rows=[]
            for name,flow in comparison['flows'].items():
                curve_rows.extend({'Date':r['date'],'Flow':name,'Equity':r['equity']} for r in flow.get('curve',[]))
                ledger_rows.extend({'Flow':name,**r} for r in flow.get('ledger',[]))
            if curve_rows:
                chart=pd.DataFrame(curve_rows);chart['Date']=pd.to_datetime(chart['Date'])
                st.line_chart(chart.pivot_table(index='Date',columns='Flow',values='Equity',aggfunc='last'),use_container_width=True)
            with st.expander('Combined C0 / C2 trade ledger',expanded=True):
                render_table(ledger_rows,'Open holdings are marked to the latest processed close; there is no forced terminal sale.',height=340)
                if ledger_rows:st.download_button('Download comparison ledger CSV',pd.DataFrame(ledger_rows).to_csv(index=False),file_name='aegistrade_c0_c2_'+comparison['run_id'][:8]+'.csv',mime='text/csv')
            st.download_button('Download complete comparison JSON',json.dumps(comparison,indent=2),file_name='aegistrade_c0_c2_'+comparison['run_id'][:8]+'.json',mime='application/json')
            st.caption(comparison['comparison_design']['interpretation']+' Use the case experiment below for the fair same-case, same-budget multi-agent evaluation.')
    selection_settings=st.session_state.get('selection_research_settings',{})
    st.caption("The experiment automatically ranks eligible stocks and retrieves dated evidence. It runs to completion without approval pauses; use the C2 portfolio for HUMAN_EVIDENCE_OVERRIDE. Detailed traces remain in the saved result.")
    screening_capital=float(selection_settings.get('capital',200000.))
    with st.form("agent_comparison_form"):
        s1,s2=st.columns(2)
        with s1:
            cfg=st.selectbox("Experiment configuration",["ALL","C1","C2","C0"],
                format_func=lambda x:{'ALL':'All: C0 reference + C1 single agent + C2 multi-agent','C1':'C1 — single-agent baseline','C2':'C2 — multi-agent team','C0':'C0 — deterministic reference'}[x],
                help="The primary comparison is C1 versus C2. ALL also includes C0 as a zero-LLM reference.")
            count=st.number_input("Research cases to test",min_value=1,max_value=3,value=1,step=1,
                                   help="UI budget cap: at most 3 cases. Use CLI for larger controlled experiments.")
        with s2:
            first=date.fromisoformat(universe.get("provenance",{}).get("requested_start") or universe["first_date"]);last=date.fromisoformat(universe["last_date"])
            latest_outcome_case=max(first,last-timedelta(days=35))
            configured_case=date.fromisoformat(selection_settings.get("end")) if selection_settings.get("end") else latest_outcome_case
            default_case=min(configured_case,latest_outcome_case)
            eval_start=st.date_input("Earliest case date",value=default_case,min_value=first,max_value=last,key="ai_eval_start")
            eval_end=st.date_input("Latest case date",value=default_case,min_value=first,max_value=last,key="ai_eval_end")
            st.caption('Choose a case at least 20 trading sessions before the dataset ends to receive the standardized forward P&L outcome.')
        is_paid=cfg!="C0"
        consent=st.checkbox("I authorize this run to use the selected inference backend, subject to the displayed allowance",value=False,disabled=not is_paid)
        run_agent=st.form_submit_button("Run AI experiment",type="primary",use_container_width=True)
    budget_calls=int(count)*{"C0":0,"C1":8,"C2":8,"ALL":16}[cfg]
    st.caption(f"Maximum attempted inference units for these settings: {budget_calls}. Reported provider usage/cost may be incomplete.")
    if run_agent:
        if eval_start>eval_end:st.error("Invalid experiment date range")
        elif is_paid and not consent:st.error("Explicit consent is needed before external inference")
        elif is_paid and not reviewer_token:st.error("Configure AEGIS_REVIEWER_TOKEN in .env and restart before requesting external inference")
        elif is_paid and not health.get("llm_experiments_enabled"):st.error("The selected inference provider is not enabled and ready. Choose a ready provider in the dropdown above, or fix its login or key.")
        else:
            payload={"configuration":cfg,"cases":int(count),"start_date":eval_start.isoformat(),"end_date":eval_end.isoformat(),
                     "consent_to_paid_calls":bool(consent),"max_output_tokens_per_case":3600,"use_memory":False,"automatic_stock_selection":True,"reference_capital":screening_capital,"selection_run_id":selection_settings.get("run_id")}
            payload['research_purpose']='ENTRY'
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
        st.caption(f"Run {experiment['run_id']} | Status: {experiment.get('status','COMPLETED')} | Model: {experiment['model']} | Call budget: {experiment['max_possible_paid_calls']}")
        summary=pd.DataFrame(experiment.get("summary",[]))
        outputs=experiment.get("outputs",[])
        st.write('**Primary comparison — C1 single agent versus C2 multi-agent team**')
        capability=architecture_capability_rows(summary,outputs)
        render_table([r for r in capability if not r['Architecture'].startswith('C0')],
            'C1 and C2 receive identical cases, model, evidence, available read tools and case-level budget. Safe evidence abstentions are separated from hard failures.',height=190)
        c0_rows=[r for r in capability if r['Architecture'].startswith('C0')]
        if c0_rows:
            with st.expander('C0 deterministic reference',expanded=False):
                render_table(c0_rows,'C0 uses no LLM and is not the single-agent baseline.',height=120)
        outcome_rows=[]
        for item in outputs:
            outcome=item.get('forward_outcome',{})
            outcome_rows.append({'Case':item.get('case_id'),'Architecture':item.get('config'),
                'Research decision':'ENTER' if outcome.get('participated') else 'STAY_CASH',
                'Outcome available':outcome.get('available',False),'Entry date':outcome.get('entry_date'),
                'Exit date':outcome.get('exit_date'),'Net P&L (₹)':outcome.get('pnl'),
                'Return on ₹100k (%)':outcome.get('return_pct')})
        if any(r['Outcome available'] for r in outcome_rows):
            st.write('**Secondary forward outcome — fixed 20-session paper measurement**')
            render_table(outcome_rows,'Calculated after research using ₹100,000 independently per case, next-open entry, the 20th-session close, 10 bps slippage and modeled NSE delivery charges. Blocked or failed entries remain cash. This is not a persistent portfolio and is not the architecture-quality score.',height=230)
        with st.expander('Technical audit metrics: agreement, errors, calls and latency',expanded=False):
            render_table(summary,'The primary comparison is C1 versus C2. Forward P&L is a fixed secondary outcome; task success, grounding and safety remain the architecture measures.',height=230)
            if not summary.empty and {'config','model_calls','median_latency_s','p95_latency_s'}.issubset(summary.columns):
                st.write('**Cost and latency by architecture**')
                st.bar_chart(summary.set_index('config')[['model_calls','median_latency_s','p95_latency_s']],use_container_width=True)
                st.caption('These quantities use different units; inspect the table for exact values. Provider cost remains unknown unless every call reports it.')
        render_table([{**{k:v for k,v in item.items() if k in ("case_id","config","market_regime","expected_strategy","selected_strategy","guard_pass","critic_accept","llm_calls","latency_s")},
            'forward_pnl':item.get('forward_outcome',{}).get('pnl'),'forward_return_pct':item.get('forward_outcome',{}).get('return_pct')} for item in outputs],height=250)
        provider_failures=[u for output in outputs for u in output.get('usage',[]) if u.get('error') or (u.get('http_status') or 0)>=400]
        if provider_failures:
            statuses=sorted({str(u.get('error_code') or u.get('http_status') or 'network/timeout') for u in provider_failures})
            st.error('Inference failed: '+', '.join('HTTP '+s if s.isdigit() else s for s in statuses)+'. No eligible research result was produced for the failed case.')
            if any(str(u.get('error_code','')).startswith('CLAUDE_') for u in provider_failures):st.info('Check Claude CLI login status (claude auth status), your Claude plan usage allowance and the selected model. Quota failures pause historical runs; restore access before consenting to resume.')
            elif any(str(u.get('error_code','')).startswith('CODEX_') for u in provider_failures):st.info('Check Codex login status, ChatGPT usage allowance and the selected CLI model. Quota failures pause historical runs; restore access before consenting to resume. No automatic switch to OpenRouter occurs.')
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
        review_gate_failures=[x for x in outputs if x.get('human_review_gate_error')]
        if review_gate_failures:
            with st.expander('C2 evidence-gate diagnostics',expanded=False):
                render_table([{'case_id':x.get('case_id'),'reason':x.get('human_review_gate_error')} for x in review_gate_failures],
                             'These diagnostics explain model/evidence exclusions; they do not create a second approval workflow.',height=180)
        st.caption('Human intervention is tested only inside Strategy Backtests with HUMAN_EVIDENCE_OVERRIDE. It reuses the completed C2 research and pauses eligible evidence-blocked BUY/SELL cases without making another research call.')
        st.download_button("Download research results JSON",json.dumps(experiment,indent=2),file_name=f"aegistrade_agents_{experiment['run_id'][:8]}.json",mime="application/json")
    with st.expander('Human C2 decisions and simulated-action audit',expanded=False):
        try:
            reviews=get('/research/experiments/reviews').get('reviews',[])
            events=get('/audit/events')
            render_table(list(reversed(reviews)),'Grounded C2 BUY/SELL decisions reviewed by a human; no live broker exists.',height=260)
            render_table(list(reversed(events[-25:])),'Latest internal approval and simulated-action events.',height=240)
            if reviews:st.download_button('Export human C2 decisions',pd.DataFrame(reviews).to_csv(index=False),file_name='aegistrade_human_c2_decisions.csv',mime='text/csv')
        except Exception as exc:fail('Could not load the human decision audit.',exc)
    st.caption("C1 is the capstone single-agent baseline; C2 is the supervisor-led three-specialist system. C0 is only a deterministic zero-LLM reference. Human-in-the-loop evidence overrides remain in the C2 portfolio.")

elif page == "Capstone Evaluation":
    heading("Capstone experiment ledger", "View retained deterministic and E1–E4 evaluation runs, lifecycle events, metrics and downloadable reports. This workspace is read-only and makes no model calls.")
    if st.button("Refresh capstone run ledger"):
        st.rerun()
    try:
        ledger=get('/evaluation/capstone/runs')
    except Exception as exc:
        fail('Could not read the capstone experiment ledger.',exc);st.stop()
    runs=ledger.get('runs',[])
    if not runs:
        st.info('No retained capstone experiment runs were found. Launch one with evaluation/experiment_ledger.py, then refresh this workspace.')
        st.code('.venv/bin/python evaluation/experiment_ledger.py list',language='bash')
    else:
        render_table(runs,'Newest retained run first. A completed process is not automatically independently reviewed evidence.',height=260)
        labels={f"{r.get('created_at_utc','unknown')[:19]} | {r.get('experiment','UNKNOWN')} | {r.get('status','UNKNOWN')} | {r['run_id']}":r['run_id'] for r in runs}
        chosen_label=st.selectbox('Retained experiment run',list(labels),key='capstone_ledger_run')
        run_id=labels[chosen_label]
        try:detail=get('/evaluation/capstone/runs/'+quote(run_id,safe=''))
        except Exception as exc:fail('Could not load the selected experiment.',exc);st.stop()
        manifest=detail.get('manifest',{});cfg=manifest.get('configuration',{})
        provenance=manifest.get('provenance',{})
        a,b,c,d=st.columns(4)
        a.metric('Experiment',cfg.get('experiment','UNKNOWN'))
        b.metric('Status',manifest.get('status','UNKNOWN'))
        c.metric('Exit code',metric_value(manifest.get('exit_code')))
        c.caption('0 means the background process completed successfully.')
        d.metric('Report rows',metric_value((detail.get('report_preview') or {}).get('row_count')))
        if manifest.get('status')=='COMPLETED':st.success('Background process completed and the retained report hash is available.')
        elif manifest.get('status')=='FAILED':st.error('The run failed. Keep its logs and failure evidence; do not delete an unfavourable run.')
        else:st.info('Current ledger state: '+str(manifest.get('status','UNKNOWN'))+'. Refresh to read the latest persisted status.')
        if cfg.get('experiment') in {'DETERMINISTIC','E4'}:
            st.warning('This is a zero-generation or synthetic reference result. It is not a measured C1/C2 model comparison or proof of profitability.')
        if not manifest.get('paid_inference_authorized'):
            st.caption('No paid/external inference was authorized for this run.')
        if provenance:
            st.markdown('#### Contribution and review provenance')
            st.write('**Requested/authorized by:** '+str(provenance.get('requested_by','Unspecified')))
            if provenance.get('request_note'):st.write('**Purpose:** '+str(provenance['request_note']))
            st.caption(str(provenance.get('execution_assistance',''))+' · Human review: '+str(provenance.get('human_review_status','PENDING'))+' · Independent validation: '+str(provenance.get('independent_validation_status','PENDING')))
            st.info(str(provenance.get('statement','Automated execution is separate from human review and sign-off.')))
        preview=detail.get('report_preview')
        if preview:
            st.markdown('#### Result summary')
            if isinstance(preview.get('summary'),dict):
                summary_rows=[]
                for variant,values in preview['summary'].items():
                    summary_rows.append({'variant':variant,**(values if isinstance(values,dict) else {'value':values})})
                render_table(summary_rows,height=260)
            elif isinstance(preview.get('case_results'),dict):
                result=preview['case_results'];x,y,z=st.columns(3)
                x.metric('Cases',metric_value(result.get('count')));y.metric('Correct',metric_value(result.get('correct')));z.metric('Accuracy',metric_value(result.get('accuracy')))
                if result.get('errors'):render_table(result['errors'],'Mismatches are retained for review.',height=220)
            with st.expander('Complete report preview',expanded=False):st.json(preview)
        events=detail.get('events',[])
        if events:
            st.markdown('#### Background-run lifecycle')
            render_table(events,'Queued, started and finished events retained by the experiment ledger.',height=220)
        with st.expander('Manifest, configuration, hashes and retained files'):
            st.json(manifest);st.write('**Retained files:** '+', '.join(detail.get('files',[])))
        if detail.get('report_download_available'):
            try:
                response=requests.get(API+'/evaluation/capstone/runs/'+quote(run_id,safe='')+'/report',timeout=90)
                if not response.ok:raise APIError.from_response(response)
                st.download_button('Download complete experiment report',response.content,
                    file_name=f'aegistrade_capstone_{run_id}.json',mime='application/json')
            except Exception as exc:fail('The report exists but could not be prepared for download.',exc)
        st.markdown('#### Terminal inspection and replay')
        st.code(f'.venv/bin/python evaluation/experiment_ledger.py show {run_id}\n.venv/bin/python evaluation/experiment_ledger.py replay {run_id}',language='bash')
        st.caption('Replay creates a new run directory and never overwrites this evidence. Paid experiments require fresh explicit consent and all label/evidence preconditions.')

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
    st.caption('The policy search below retrieves project rules and background. Dated company filings are a separate evidence layer, shown in the library panel. This screen makes no paid generation calls.')
    with st.expander('Historical company evidence library',expanded=True):
        try:
            library=get('/company/evidence-library/status')
            if library.get('report'):
                report=library['report'];totals=report['totals']
                st.write(str(report['unique_stocks'])+' distinct stocks across the configured universes')
                st.write(str(totals['metadata_rows'])+' dated announcement records · '+str(totals['readable_documents'])+' readable selected documents · '+str(totals['financial_documents'])+' financial sources')
                st.caption('Company filings are retrieved separately for the selected decision date through company_evidence. They are not mixed into the timeless policy search below. Readable/OCR text is not independently verified financial accuracy or proof of no adverse news.')
                render_table([{k:r.get(k) for k in ['symbol','selected_documents','financial_documents','unavailable_documents','financial_coverage_pct','existing_packs','packs_financial_ready','packs_adverse_ready']} for r in report['stocks']],height=260)
                st.download_button('Download evidence coverage report',json.dumps(report,indent=2),file_name='aegistrade_evidence_coverage.json',mime='application/json')
            elif library.get('progress'):st.json(library['progress'])
            else:st.caption('No audited company library is prepared yet. Company research can still prepare bounded evidence on demand.')
        except Exception as exc:fail('Company evidence library status is unavailable.',exc)
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
    heading("Human decision outcomes", "C2 BUY/SELL approvals and rejections are recorded separately from model traces. A fixed 10-session outcome is shown as review evidence; it is not proof that a decision was universally right or wrong.")
    try:
        decision_reviews=get('/research/experiments/reviews').get('reviews',[])
        if decision_reviews:
            render_table([{k:r.get(k) for k in ('created_utc','reviewer','symbol','signal_date','strategy','action','decision','holding_return_pct','outcome_assessment','lesson_candidate_status')} for r in reversed(decision_reviews)],
                         'Eligible rows may inform a future conditional lesson only after human review. They are never learned automatically.',height=260)
        else:st.info('No C2 human decisions have been recorded yet. Review an actionable C2 result in AI Agent Experiments first.')
    except Exception as exc:fail('Unable to load C2 human-decision outcomes.',exc)
    st.divider()
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
                    st.info('To enable Save, configure AEGIS_REVIEWER_TOKEN in the project .env file and restart the app. This is separate from your model API key.')
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
