"""The AI-experiment comparison separates a safe evidence abstention from a hard model/policy failure."""
from pathlib import Path
import pandas as pd
import pytest

ROOT=Path(__file__).resolve().parents[1]


def load(name):
    source=(ROOT/'app'/name).read_text()
    start=source.index('def architecture_capability_rows');end=source.index('\ndef heading',start)
    scope={};exec(source[start:end],scope)
    return scope['architecture_capability_rows']


def case(config,symbol,*,guard=True,failure=None,errors=(),adverse=None,cited=True,action='ENTER'):
    item={'config':config,'case_id':symbol,'guard_pass':guard,'model_errors':list(errors),'failure':failure,
          'portfolio_action':action if guard else None}
    if config!='C0':item['company_assessment']={'adverse_risk':adverse,'citations':['DOC-1'] if cited else []}
    return item


OUTPUTS=[
    case('C0','BHARTIARTL'),case('C0','LT'),case('C0','TCS'),
    case('C1','BHARTIARTL',guard=False,failure={'category':'POLICY','code':'STRATEGY_ROUTE_CONFLICT'},
         errors=['STRATEGY_ROUTE_CONFLICT: Strategy conflicts with code'],cited=False),
    case('C1','LT',adverse='NO_MATERIAL_ADVERSE_FOUND'),case('C1','TCS',adverse='COVERAGE_LIMITED'),
    case('C2','BHARTIARTL',guard=False,failure={'category':'EVIDENCE','code':'COMPANY_ASSESSMENT_BLOCKED'},
         errors=['COMPANY_ASSESSMENT_BLOCKED: review required'],adverse='ADVERSE_EVENT_FOUND'),
    case('C2','LT',adverse='NO_MATERIAL_ADVERSE_FOUND'),case('C2','TCS',adverse='NO_MATERIAL_ADVERSE_FOUND'),
]
SUMMARY=pd.DataFrame([{'config':c,'cases':3,'guard_pass_count':g} for c,g in (('C0',3),('C1',2),('C2',2))])


@pytest.mark.parametrize('name',['ui.py','ui_blue_preview.py'])
def test_abstention_is_not_reported_as_a_hard_failure(name):
    rows={r['Architecture']:r for r in load(name)(SUMMARY,OUTPUTS)}
    assert rows['C0']['Route validation']=='Reference by construction' and rows['C0']['Grounded company evidence']=='N/A'
    assert rows['C0']['Hard model/policy failures']==0 and rows['C0']['Decision coverage']=='3/3 routed'
    # C1: a route conflict is a genuine policy failure, never an abstention.
    assert rows['C1']['Hard model/policy failures']==1 and rows['C1']['Safe evidence abstentions']==0
    assert rows['C1']['Route validation']=='2/3 decided cases passed' and rows['C1']['Grounded company evidence']=='2/3'
    # C2: the cited adverse finding is one flag and one safe abstention, and is left out of the route denominator.
    assert rows['C2']['Adverse-risk flags']==1 and rows['C2']['Safe evidence abstentions']==1
    assert rows['C2']['Hard model/policy failures']==0 and rows['C2']['Grounded company evidence']=='3/3'
    assert rows['C2']['Route validation']=='2/2 decided cases passed, 1 abstained' and rows['C2']['Decision coverage']=='2/3'


def test_both_dashboards_keep_the_raw_metrics_in_a_collapsed_audit():
    for name in ('ui.py','ui_blue_preview.py'):
        source=(ROOT/'app'/name).read_text()
        assert 'Capability-oriented architecture comparison' in source and 'Technical audit metrics' in source
        assert 'Quality and reliability by architecture' not in source
