from datetime import datetime

import pandas as pd

from aegistrade.research_service import attach_forward_outcomes


def market(sessions=20):
    dates=pd.bdate_range('2024-01-02',periods=sessions)
    return pd.DataFrame({'Date':dates,'Symbol':['DEMO']*sessions,'Open':[100.0]*sessions,
                         'Close':[110.0]*sessions})


def row(config, *, passed=True):
    return {'snapshot':{'symbol':'DEMO','date':'2024-01-01'},'case_id':'DEMO-2024-01-01',
            'config':config,'guard_pass':passed,'selected_strategy':'EMA_TREND',
            **({'portfolio_action':'ENTER'} if config!='C0' else {})}


def test_fixed_forward_outcome_is_identical_for_eligible_c0_c1_c2_and_cash_for_block():
    outputs=[row('C0'),row('C1'),row('C2'),row('C2',passed=False)]
    policy=attach_forward_outcomes(outputs,market())
    assert policy['sessions']==20 and policy['notional_per_case']==100000
    assert outputs[0]['forward_outcome']['pnl']==outputs[1]['forward_outcome']['pnl']==outputs[2]['forward_outcome']['pnl']
    assert outputs[0]['forward_outcome']['pnl']>0
    assert outputs[3]['forward_outcome']['decision']=='STAY_CASH'
    assert outputs[3]['forward_outcome']['pnl']==0


def test_incomplete_future_window_is_unavailable_not_partial_pnl():
    outputs=[row('C1')]
    attach_forward_outcomes(outputs,market(19))
    assert outputs[0]['forward_outcome']['available'] is False
    assert 'pnl' not in outputs[0]['forward_outcome']
