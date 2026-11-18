"""Polling changes only the selected progress panel, never inference work."""
from copy import deepcopy
import pytest
from app import live_progress as live


def result(status='RUNNING',done=2):
    return {'run_id':'a'*32,'status':status,'progress':{'completed_sessions':done,'total_sessions':10,'current_date':'2024-03-04','phase':'CLOSE'},'model_usage':{'attempted_calls':done*6}}

class AppRerun(Exception):pass

class FakeStreamlit:
    def __init__(self):
        self.session_state={};self.interval=None;self.callback=None;self.bars=[];self.warnings=[];self.captions=[];self.tables=[];self.messages=[]
    def fragment(self,run_every):
        self.interval=run_every
        def decorate(fn):self.callback=fn;return fn
        return decorate
    def write(self,*a):self.messages.append(a)
    def dataframe(self,rows,**kw):self.tables.append(rows)
    def json(self,*a):pass
    def progress(self,fraction,**kw):self.bars.append(fraction)
    def caption(self,text):self.captions.append(text)
    def warning(self,text):self.warnings.append(text)
    def rerun(self):raise AppRerun()


def test_live_panel_polls_only_selected_status_and_updates_bar(monkeypatch):
    st=FakeStreamlit();monkeypatch.setattr(live,'st',st);responses=iter([result(done=2),result(done=3)]);reads=[]
    def fetch(path,**kw):reads.append(path);return next(responses)
    live.render_c2_progress(result(),fetch);st.callback()
    assert st.interval==5 and st.bars==[.2,.3]
    assert reads==['/simulation/c2/status/'+'a'*32]*2
    assert st.session_state['simulation_result']['progress']['completed_sessions']==3


@pytest.mark.parametrize('status',['COMPLETED','COMPLETED_WITH_GAPS','PAUSED_PROVIDER','PAUSED_BUDGET','PAUSED_USER','INTERRUPTED'])
def test_polling_stops_on_completion_or_pause_and_updates_full_page_once(monkeypatch,status):
    st=FakeStreamlit();monkeypatch.setattr(live,'st',st);reads=[]
    def fetch(*a,**kw):reads.append(a);return result(status)
    with pytest.raises(AppRerun):live.render_c2_progress(result(),fetch)
    assert len(reads)==1 and st.session_state['simulation_result']['status']==status
    live.render_c2_progress(st.session_state['simulation_result'],fetch)
    assert st.interval is None and len(reads)==1


def test_temporary_status_failure_keeps_last_bar_and_next_poll_recovers(monkeypatch):
    st=FakeStreamlit();monkeypatch.setattr(live,'st',st);reads=[]
    def fetch(*a,**kw):
        reads.append(a)
        if len(reads)==1:raise OSError('Local API temporarily unavailable')
        return result(done=4)
    initial=result(done=2);st.session_state['simulation_result']=deepcopy(initial)
    live.render_c2_progress(initial,fetch)
    assert st.warnings and st.bars==[.2] and st.session_state['simulation_result']==initial
    st.callback();assert st.bars==[.2,.4] and len(reads)==2


def test_wrong_run_response_is_not_displayed_or_stored(monkeypatch):
    st=FakeStreamlit();monkeypatch.setattr(live,'st',st);initial=result();st.session_state['simulation_result']=deepcopy(initial)
    other={**result('COMPLETED',done=10),'run_id':'b'*32}
    live.render_c2_progress(initial,lambda *a,**kw:other)
    assert st.warnings and st.bars==[.2] and st.session_state['simulation_result']==initial


def test_c1_live_progress_updates_activity_and_outcomes_within_same_session(monkeypatch):
    st=FakeStreamlit();monkeypatch.setattr(live,'st',st);reads=[]
    base={**result(),'research_flow':'C1','research_summary':{'company_screens':3,'evidence_passed':1,'signals_found':0,'buy_fills':0},
          'activity':{'stage':'LLM_REQUEST','symbol':'DEMO','agent':'single','turn':2,'updated_utc':'2026-11-13T01:00:00+00:00'},
          'decisions':[{'date':'2024-03-04','symbol':'DEMO','action':'NO_SMC_SIGNAL','smc_stage':'WAITING_RETEST'}]}
    second=deepcopy(base);second['research_summary']['signals_found']=1;second['activity']['stage']='CHECKING_SMC_SIGNAL';second['decisions'][0]['action']='ENTER'
    replies=iter([base,second])
    def fetch(path,**kw):reads.append(path);return next(replies)
    live.render_c2_progress(base,fetch);st.callback()
    assert st.bars==[.2,.2] # No invented session completion during research.
    assert reads==['/simulation/c1/status/'+'a'*32]*2
    assert st.tables[-1][0]['action']=='ENTER'
    assert any('06:30:00 IST' in c for c in st.captions)
    assert any('Signals: 1' in str(x) for x in st.messages)
    assert st.session_state['portfolio_results']['C1']['activity']['stage']=='CHECKING_SMC_SIGNAL'
