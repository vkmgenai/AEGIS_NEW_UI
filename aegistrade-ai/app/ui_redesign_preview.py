"""Separate capstone-demo UI proposal. It does not replace app/ui.py."""
from __future__ import annotations

from datetime import date, timedelta
import json
import os
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

API = os.getenv("AEGIS_API_URL", "http://127.0.0.1:8000").rstrip("/")
ROOT = Path(__file__).resolve().parents[1]

st.set_page_config(
    page_title="AegisTrade AI · Demo UI Preview",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(
    """
<style>
:root {--navy:#0b1f3a;--blue:#174ea6;--sky:#eaf2ff;--red:#d64545;--ink:#13233a;}
[data-testid="stAppViewContainer"] {background:linear-gradient(135deg,#eaf2ff 0%,#f8fbff 55%,#edf4ff 100%);color:var(--ink)}
[data-testid="stHeader"] {background:rgba(234,242,255,.94);border-bottom:1px solid #cad8ec}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#071a33 0%,#0c2e5a 56%,#0b3d78 100%);border-right:1px solid #315b8f}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {color:#f5f9ff!important}
[data-testid="stSidebar"] div.stButton > button {
  width:100%;min-height:48px;text-align:left;white-space:normal;border-radius:10px;
  border:1px solid rgba(180,211,255,.32);background:rgba(16,61,112,.62)!important;
  color:#fff!important;font-size:.96rem;font-weight:650;padding:.62rem .8rem;box-shadow:none;
}
[data-testid="stSidebar"] div.stButton > button:hover {
  border-color:#8fc0ff;background:#1659a3!important;color:#fff!important;transform:none;
}
.block-container {max-width:1250px;padding-top:1.7rem;padding-bottom:3rem}
.hero {background:linear-gradient(120deg,#071a33,#0d4385 58%,#1768bc);padding:2rem 2.2rem;border-radius:20px;color:#fff;margin-bottom:1.35rem;box-shadow:0 12px 30px #0b2e5a30;border:1px solid #3978bb}
.hero h1 {margin:0;color:#fff;font-size:2.3rem}.hero p{margin:.35rem 0 0;color:#d9e7ff}
.section-kicker {color:#45617f;text-transform:uppercase;letter-spacing:.08em;font-size:.78rem;font-weight:700}
.status-card {background:linear-gradient(145deg,#f7fbff,#e4efff);border:1px solid #bfd1e9;border-radius:14px;padding:1rem 1.1rem;min-height:105px;box-shadow:0 5px 16px #102a4314}
.status-card strong {font-size:1.35rem;color:#0b1f3a}.muted{color:#60738a;font-size:.9rem}
[data-testid="stMain"] div.stButton > button[kind="primary"] {
  width:100%;min-height:138px;text-align:left;white-space:pre-line;border-radius:18px;
  border:1px solid #4f8ed3;background:linear-gradient(135deg,#0c3568,#145ba8 68%,#1976c9)!important;
  color:#fff!important;font-size:1.08rem;font-weight:700;padding:1.15rem 1.25rem;
  box-shadow:0 9px 22px #10386630;
}
[data-testid="stMain"] div.stButton > button[kind="primary"]:hover {
  border-color:#8bc2ff;background:linear-gradient(135deg,#10427d,#1d6dc1)!important;
  color:#fff!important;transform:translateY(-2px);box-shadow:0 12px 25px #1038663d;
}
[data-testid="stMain"] div.stButton > button[kind="secondary"] {border-color:#9db4d1;color:#123a68;background:#f8fbff}
.topline {display:flex;justify-content:space-between;align-items:center;margin-bottom:.4rem}
.badge {display:inline-block;background:#ffe9e9;color:#a51f1f;border-radius:999px;padding:.24rem .55rem;font-weight:700;font-size:.78rem}
[data-testid="stMetric"] {background:linear-gradient(145deg,#f9fcff,#e8f2ff);border:1px solid #c2d4ea;padding:.75rem 1rem;border-radius:12px}
[data-testid="stDataFrame"], [data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] {border-color:#bfd0e5!important}
</style>
""",
    unsafe_allow_html=True,
)


def get(path: str, default=None):
    try:
        response = requests.get(API + path, timeout=8)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return default


def page_button(label: str, page: str, *, key: str):
    if st.button(label, key=key, use_container_width=True, type="primary"):
        st.session_state.preview_page = page
        st.rerun()


def table(rows, *, height=290):
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True, height=height)
    else:
        st.info("No retained records are available for this view.")


def header(title: str, subtitle: str):
    left, right = st.columns([8, 1])
    with left:
        st.markdown(f"<div class='section-kicker'>AegisTrade AI · preview</div><h1>{title}</h1><p class='muted'>{subtitle}</p>", unsafe_allow_html=True)
    with right:
        if st.button("⌂ Home", use_container_width=True):
            st.session_state.preview_page = "Home"
            st.rerun()
    st.divider()


def experiment_rows(run: dict):
    rows = []
    for item in run.get("outputs", []):
        if item.get("config") not in {"C1", "C2"}:
            continue
        outcome = item.get("forward_outcome", {})
        rows.append(
            {
                "Case": item.get("case_id"),
                "Architecture": "Single agent" if item.get("config") == "C1" else "Multi-agent team",
                "Decision": outcome.get("decision"),
                "Guard": "PASS" if item.get("guard_pass") else "ABSTAIN / FAIL",
                "Calls": item.get("llm_calls"),
                "P&L ₹": outcome.get("pnl"),
                "Return %": outcome.get("return_pct"),
            }
        )
    return rows


st.session_state.setdefault("preview_page", "Home")
health = get("/health", {}) or {}
notifications = get("/simulation/c2/notifications", {"notifications": []}) or {"notifications": []}
pending = notifications.get("notifications", [])

with st.sidebar:
    st.markdown("## 🛡️ AegisTrade AI")
    st.caption("DEMO UI REDESIGN · ORIGINAL UI UNCHANGED")
    st.markdown("---")
    for label, target in (
        ("⌂ Home", "Home"),
        ("▦ Data & Stock", "Data"),
        ("▰ C2 Portfolio", "Portfolio"),
        ("◎ Agent Comparison", "Experiment"),
        ("✓ Evaluation Evidence", "Evaluation"),
        ("▤ Knowledge & Lessons", "Knowledge"),
    ):
        if st.button(label, key="side_" + target, use_container_width=True):
            st.session_state.preview_page = target
            st.rerun()
    st.markdown("---")
    st.caption("SIMULATION ONLY\n\nNo exchange or broker connection")
    st.caption("API: " + ("connected" if health else "offline"))

page = st.session_state.preview_page

if page == "Home":
    st.markdown("<div class='hero'><h1>AegisTrade AI</h1><p>Grounded multi-agent equity research · historical simulation · human-governed uncertainty</p></div>", unsafe_allow_html=True)
    st.markdown("<div class='topline'><div><span class='section-kicker'>Demo home</span><h2>What do you want to show?</h2></div>" + (f"<span class='badge'>🔔 {len(pending)} review needed</span>" if pending else "<span class='muted'>🔔 No pending reviews</span>") + "</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        page_button("▦  Data & Stock\n\nConfirm the active universe, coverage and one stock snapshot.", "Data", key="tile_data")
        page_button("◎  Agent Comparison\n\nCompare the C1 single agent with the C2 specialist team.", "Experiment", key="tile_exp")
    with c2:
        page_button("▰  C2 Portfolio\n\nRun and inspect the complete governed historical workflow.", "Portfolio", key="tile_port")
        page_button("✓  Evaluation Evidence\n\nReview retained experiments, limitations and minimum-bar proof.", "Evaluation", key="tile_eval")
    st.markdown("### What needs attention")
    a, b, c = st.columns(3)
    recent_c2 = (get("/simulation/c2/recent", {"runs": []}) or {}).get("runs", [])
    fresh = (get("/research/experiments/recent", {"runs": []}) or {}).get("runs", [])
    with a:
        st.markdown(f"<div class='status-card'><span class='section-kicker'>Human intervention</span><br><strong>{len(pending)}</strong><br><span class='muted'>C2 checkpoints awaiting review</span></div>", unsafe_allow_html=True)
    with b:
        paused = sum(str(x.get("status", "")).startswith("PAUSED") for x in recent_c2)
        st.markdown(f"<div class='status-card'><span class='section-kicker'>Paused portfolios</span><br><strong>{paused}</strong><br><span class='muted'>Resume only after checking the reason</span></div>", unsafe_allow_html=True)
    with c:
        st.markdown(f"<div class='status-card'><span class='section-kicker'>Current AI evidence</span><br><strong>{len(fresh)}</strong><br><span class='muted'>UI-visible architecture runs</span></div>", unsafe_allow_html=True)

elif page == "Data":
    header("Data & Stock", "Know the dataset before interpreting any model or financial result.")
    universe = get("/market/universe", {}) or {}
    cols = st.columns(4)
    values = [("Source", universe.get("source", "—")), ("Instruments", len(universe.get("symbols", []))), ("First date", universe.get("first_date", "—")), ("Last date", universe.get("last_date", "—"))]
    for col, (label, value) in zip(cols, values): col.metric(label, value)
    st.warning("Current or curated membership applied backward creates survivorship bias. Raw NSE prices may contain unresolved corporate actions.")
    symbols = universe.get("symbols", [])
    if symbols:
        symbol = st.selectbox("Inspect one stock", symbols)
        history = get("/market/history?symbol=" + symbol, {}) or {}
        rows = history.get("rows", history if isinstance(history, list) else [])
        if rows:
            frame = pd.DataFrame(rows)
            date_col = next((x for x in ("Date", "date") if x in frame.columns), None)
            close_col = next((x for x in ("Close", "close") if x in frame.columns), None)
            if date_col and close_col:
                frame[date_col] = pd.to_datetime(frame[date_col])
                st.line_chart(frame.set_index(date_col)[close_col])

elif page == "Portfolio":
    header("C2 Historical Portfolio", "The complete demo: screen → research → critic → code checks → simulated fills → holding reviews.")
    st.info("This preview keeps configuration short. Start, pause, resume and human-override execution remain in the existing C2 engine; no duplicate trading engine is introduced.")
    left, right = st.columns([2, 1])
    with left:
        with st.container(border=True):
            st.markdown("### Guided run settings")
            capital = st.number_input("Starting capital (₹)", min_value=100_000, value=300_000, step=50_000)
            d1, d2 = st.columns(2)
            with d1: start = st.date_input("Start date", value=date(2023, 9, 1))
            with d2: end = st.date_input("End date", value=date(2023, 11, 30))
            allowance = st.radio("Inference allowance", [24, 48, 96], horizontal=True, index=1)
            st.checkbox("I approve the fixed historical simulation rules")
            st.checkbox("I authorize model requests up to this allowance")
            st.caption("Risk, stops, delivery fees, slippage, candidate pool and review cadence use the documented reproducible defaults.")
            st.button("Start C2 portfolio in final workflow", type="primary", use_container_width=True, disabled=True, help="Preview only. Execution remains disabled until this design is approved.")
    with right:
        st.markdown("### Run summary")
        st.metric("Capital", f"₹{capital:,.0f}")
        st.metric("Window", f"{(end-start).days} days")
        st.metric("Allowance", f"{allowance} requests")
        st.caption("The end date does not force a sale. Open positions remain marked in the result.")
    st.markdown("### Retained C2 portfolio runs")
    runs = (get("/simulation/c2/recent", {"runs": []}) or {}).get("runs", [])
    table([{"Run": x.get("run_id", "")[:12], "Created": x.get("created_utc", "")[:19], "Status": x.get("status"), "Progress": x.get("progress", {})} for x in runs])

elif page == "Experiment":
    header("C1 vs C2 Agent Comparison", "Primary capstone evidence: same cases, model, evidence capabilities and total budget.")
    runs = (get("/research/experiments/recent", {"runs": []}) or {}).get("runs", [])
    if runs:
        choice = st.selectbox("Retained experiment", runs, format_func=lambda x: f"{x.get('created_utc','')[:19]} · {x.get('run_id','')[:12]}")
        run = get("/research/experiments/result/" + choice["run_id"], {}) or {}
        st.caption("C0 remains a deterministic reference. It is not the single-agent baseline.")
        table(experiment_rows(run), height=310)
        s1, s2 = st.columns(2)
        summaries = {x.get("config"): x for x in run.get("summary", [])}
        for col, name in ((s1, "C1"), (s2, "C2")):
            item = summaries.get(name, {})
            with col:
                st.markdown("### " + ("C1 · Single agent" if name == "C1" else "C2 · Multi-agent team"))
                a, b = st.columns(2)
                a.metric("Guard passes", f"{item.get('guard_pass_count',0)}/{item.get('cases',0)}")
                b.metric("Model calls", item.get("model_calls", 0))
                a.metric("Forward P&L", f"₹{item.get('forward_pnl',0):,.2f}")
                b.metric("Median latency", f"{item.get('median_latency_s',0):.2f}s")
        st.warning("Three development cases are not final held-out proof. The 102 independent labels still gate final E1/E2/E3.")
    else:
        st.info("No active AI Experiment record is available.")

elif page == "Evaluation":
    header("Evaluation Evidence", "Retained runs, reproducibility and honest limits in one reviewer-facing view.")
    status_path = ROOT / "reports" / "report_ai_repeat_status.json"
    if status_path.exists():
        status = json.loads(status_path.read_text())
        st.progress(min(1.0, status.get("completed_repeats", 0) / max(1, status.get("target_repeats", 3))))
        st.caption(f"Development E1 repeats: {status.get('completed_repeats',0)}/{status.get('target_repeats',3)} · {status.get('status')}")
    runs = (get("/evaluation/capstone/runs", {"runs": []}) or {}).get("runs", [])
    table(runs, height=330)
    st.markdown("### Minimum-bar boundary")
    st.error("Final held-out E1/E2/E3 cannot be claimed until the 102 case/security records are independently reviewed and frozen.")
    st.success("Implemented evidence includes typed orchestration, same-budget C1/C2 code, RAG evaluation, checkpointed C2 portfolio, human override lifecycle, tests and retained negative results.")

else:
    header("Knowledge & Lessons", "Inspect the evidence policy and governed memory without adding another demo workflow.")
    status = get("/knowledge/status", {}) or {}
    st.json(status, expanded=False)
    lessons = (get("/portfolio-lessons", {"lessons": []}) or {}).get("lessons", [])
    st.markdown("### Reviewed portfolio lessons")
    table(lessons)
    st.caption("Lessons never enter prompts automatically. They require review, acceptance and a frozen version before an evaluation run may use them.")

