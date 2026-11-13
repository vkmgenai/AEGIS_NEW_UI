"""Read-only C1/C2 progress with live research activity and signal outcomes."""
from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
from app.portfolio_view import remember_result,flow_of

LIVE_STATUSES={'RUNNING','QUEUED'}
POLL_SECONDS=5


def render_c2_progress(initial_result,fetch_status):
    """Backward-compatible name. Only GETs: never start, resume or add allowance."""
    run_id=initial_result['run_id'];flow=flow_of(initial_result)
    polling=initial_result.get('status') in LIVE_STATUSES

    @st.fragment(run_every=POLL_SECONDS if polling else None)
    def panel():
        cached=st.session_state.get('simulation_result',{})
        result=cached if cached.get('run_id')==run_id else initial_result
        fresh=None
        if polling:
            try:
                candidate=fetch_status('/simulation/'+flow.lower()+'/status/'+run_id,timeout=10)
                if candidate.get('run_id')!=run_id or flow_of(candidate)!=flow or not isinstance(candidate.get('progress'),dict):
                    raise ValueError('Status response does not match the selected flow/run')
                fresh=candidate;result=fresh;remember_result(st.session_state,fresh)
            except Exception:
                st.warning('Automatic progress refresh is temporarily unavailable. Showing saved status; use Refresh AI progress.')
        progress=result['progress'];done=progress['completed_sessions'];total=progress['total_sessions']
        fraction=max(0.0,min(1.0,done/max(1,total)))
        st.write(flow+' status: '+result['status'])
        st.progress(fraction,text=f'{done}/{total} market sessions ({fraction:.1%})')
        st.caption(f"{progress['current_date']} | {progress['phase']} | Run {run_id[:12]}")
        activity=result.get('activity') or {}
        if activity:
            st.write('Current work: '+str(activity.get('stage','')).replace('_',' ').title())
            details=[str(activity[k]) for k in ('symbol','agent','tool') if activity.get(k)]
            if activity.get('turn'):details.append('model turn '+str(activity['turn']))
            if details:st.caption(' · '.join(details))
            if activity.get('updated_utc'):
                stamp=activity['updated_utc']
                try:
                    moment=datetime.fromisoformat(stamp.replace('Z','+00:00'))
                    if moment.tzinfo is not None:stamp=moment.astimezone(ZoneInfo('Asia/Kolkata')).strftime('%d %b %Y %H:%M:%S IST')
                except (ValueError,TypeError):pass
                st.caption('Last activity: '+stamp)
        summary=result.get('research_summary') or {}
        if flow=='C1':
            st.write('Company screens: '+str(summary.get('company_screens',0))+
                ' | Evidence passed: '+str(summary.get('evidence_passed',0))+
                ' | SMC checks: '+str(summary.get('signal_checks',summary.get('evidence_passed',0)))+
                ' | Signals: '+str(summary.get('signals_found',summary.get('entry_decisions',0)))+
                ' | Queued buys: '+str(summary.get('queued_buys',0))+
                ' | BUY fills: '+str(summary.get('buy_fills',0)))
            st.caption('Research blocked: '+str(summary.get('research_blocked',0))+
                ' · Evidence passed but no SMC entry: '+str(summary.get('no_smc_signal',0)))
        if flow=='C1' and summary.get('eligible_company_sessions'):
            st.caption('Research batch coverage: '+str(summary.get('shortlisted_company_sessions',0))+' shortlisted company-sessions out of '+str(summary['eligible_company_sessions'])+' eligible. A bounded rotating batch can miss a stock on its SMC signal date; incomplete evidence can also prevent a signal check.')
        latest=result.get('decisions',[])[-8:]
        if latest:
            st.dataframe([{k:d.get(k) for k in ['date','symbol','purpose','action','smc_stage','explanation']} for d in latest],
                         hide_index=True,use_container_width=True)
        if polling:
            checked=datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%H:%M:%S IST')
            st.caption(f'Live progress, activity and outcomes refresh every {POLL_SECONDS} seconds · Last checked {checked}')
            if result['status']=='QUEUED':st.caption('Queued behind the shared AI worker. No inference starts for this job until its turn.')
            st.caption('Session progress advances after the close finishes. Source downloads and model turns appear above while a session is in progress. Refresh AI progress reloads all detailed tables.')
        st.json(result['model_usage'])
        if fresh and fresh.get('status') not in LIVE_STATUSES:st.rerun()

    panel()
