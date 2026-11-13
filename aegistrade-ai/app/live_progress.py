"""Read-only live C2 progress, isolated from run/consent form widgets."""
from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st

LIVE_STATUSES={'RUNNING','QUEUED'}
POLL_SECONDS=5


def render_c2_progress(initial_result,fetch_status):
    """Only GET status. Never submit, resume, retry or increase inference allowance."""
    run_id=initial_result['run_id']
    polling=initial_result.get('status') in LIVE_STATUSES

    @st.fragment(run_every=POLL_SECONDS if polling else None)
    def panel():
        cached=st.session_state.get('simulation_result',{})
        result=cached if cached.get('run_id')==run_id else initial_result
        fresh=None
        if polling:
            try:
                candidate=fetch_status('/simulation/c2/status/'+run_id,timeout=10)
                if candidate.get('run_id')!=run_id or not isinstance(candidate.get('progress'),dict):
                    raise ValueError('Status response does not match the selected portfolio')
                fresh=candidate;result=fresh;st.session_state['simulation_result']=fresh
            except Exception:
                st.warning('Automatic progress refresh is temporarily unavailable. Showing the last saved status; you can still use Refresh AI progress.')
        progress=result['progress']
        done=progress['completed_sessions'];total=progress['total_sessions']
        fraction=max(0.0,min(1.0,done/max(1,total)))
        st.write('Status: '+result['status'])
        st.progress(fraction,text=f'{done}/{total} market sessions ({fraction:.1%})')
        st.caption(f"{done}/{total} sessions | {progress['current_date']} | {progress['phase']}")
        if polling:
            checked=datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%H:%M:%S IST')
            if fresh:st.caption(f'Live progress updates every {POLL_SECONDS} seconds · Last checked {checked}')
            if result['status']=='QUEUED':st.caption('Queued jobs wait for the shared AI portfolio worker; no research calls start for this job until its turn.')
            st.caption('The session counter advances after a market session finishes. AI research can take several calls. Refresh AI progress also reloads the other result tables.')
        st.json(result['model_usage'])
        if fresh and fresh.get('status') not in LIVE_STATUSES:
            # One app rerun updates final tables/warnings and removes the polling timer.
            st.rerun()

    panel()
