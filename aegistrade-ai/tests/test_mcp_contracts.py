"""Exercise every exposed MCP tool through the actual in-process protocol."""
import asyncio
from datetime import timedelta
from fastmcp import Client
from aegistrade.safety import RiskInputs,RiskParameters,make_demo_order,utc_now


def test_all_mcp_tool_contracts(tmp_path,monkeypatch):
    monkeypatch.setenv('AEGIS_DATA_DIR',str(tmp_path))
    from aegistrade.dated_web import PublicWeb
    monkeypatch.setattr(PublicWeb,'search',lambda self,query:[])

    from mcp_servers import market_server,strategy_server,risk_server,knowledge_server,records_server,action_server
    now=utc_now();inputs=RiskInputs(equity=100000,available_cash=100000,current_positions=0)
    order=make_demo_order('DEMO',100,2,'EMA_TREND','2024-01-01',inputs,RiskParameters())
    evidence={'symbol':'DEMO','date':'2024-01-01','regime':'TREND','Close':100.,'RSI14':55.,'ADX14':25.,'EMA20':99.,'EMA50':95.,'ATR14':2.}
    scenarios=[(market_server,{'list_symbols':{},'get_daily_bar':{'symbol':'RELIANCE','signal_date':'2022-01-03'},'assess_case':{'evidence':evidence},'company_evidence':{'symbol':'DEMO','signal_date':'2024-01-01'},'search_dated_web':{'evidence':evidence}}),
      (strategy_server,{'evaluate_regime':{'symbol':'RELIANCE','signal_date':'2022-10-03'},'check_case_strategy':{'evidence':evidence}}),
      (risk_server,{'policy_summary':{},'validate_simulated_buy':{'order':order.model_dump(mode='json'),'inputs':inputs.model_dump()}}),
      (knowledge_server,{'search_policy':{'query':'human approval'},'get_policy':{'passage_id':'POL-06'}}),
      (records_server,{'approved_lessons':{'topic':'grounding'},'simulated_order_status':{'request_id':'UNKNOWN'}}),
      (action_server,{'order_status':{'request_id':'UNKNOWN'},'submit_simulated_order':{'order':order.model_dump(mode='json'),
                     'approval_token':'INVALID','quote_price':100.,'quote_observed_utc':now.isoformat(),'risk_inputs':inputs.model_dump()}})]
    async def run():
        for module,cases in scenarios:
            async with Client(module.mcp) as client:
                tools=await client.list_tools()
                assert set(cases)=={t.name for t in tools},'Each newly exposed tool needs a contract test'
                for t in tools:
                    assert t.inputSchema['type']=='object'
                    result=await client.call_tool(t.name,cases[t.name])
                    assert not result.is_error,(t.name,result)
                if module is action_server:
                    result=await client.call_tool('submit_simulated_order',cases['submit_simulated_order'])
                    assert result.data['status']=='REJECTED'
                if module is knowledge_server:
                    assert not (await client.call_tool('search_policy',{'query':'a'})).data['ok']
                    cited=await client.call_tool('search_policy',{'query':'company evidence sufficiency',
                        'passage_ids':['POL-43','POL-10'],'as_of':'2023-12-01'})
                    assert [p['id'] for p in cited.data['results'][:2]]==['POL-43','POL-10']
                if module is market_server:
                    assert not (await client.call_tool('get_daily_bar',{'symbol':'RELIANCE','signal_date':'bad-date'})).data['ok']
    asyncio.run(run())
