"""Synthetic company documents for contracts only; never real market evidence."""
from datetime import datetime,time
from zoneinfo import ZoneInfo
from aegistrade.company_research import prepare_company_research,read_company_research

class FakeArchive:
    def announcements(self,symbol,start,end):
        return [{'symbol':symbol,'an_dt':datetime.combine(start,time(10)).strftime('%d-%b-%Y %H:%M:%S'),
                 'desc':'Financial Results','attchmntText':'Contract-test financial results, not actual company facts.',
                 'attchmntFile':'https://nsearchives.nseindia.com/corporate/TEST_'+symbol+'_'+str(start)+'.pdf'}]
    def pdf_text(self,url):
        return ('CONTRACT TEST ONLY. Revenue 100.00 and profit 20.00 and income 120.00 are synthetic; no financial claims. '*12),'test-pdf-hash'

BREAKOUT_QUOTE='Revenue increased by 20% to INR 120.00 crore and net profit rose by 10% to INR 22.00 crore.'

class BreakoutArchive(FakeArchive):
    def pdf_text(self,url):
        return ('CONTRACT TEST ONLY. These are synthetic issuer results, not actual company facts. '+BREAKOUT_QUOTE+
                ' Total income INR 140.00 crore and cash flow INR 30.00 crore. ')*4,'test-pdf-hash'

def pack_for(snapshot):return prepare_company_research(snapshot['symbol'],snapshot['date'],provider=BreakoutArchive() if snapshot.get('regime')=='BREAKOUT' else FakeArchive())

def assessment(pack):
    return {'status':'SUFFICIENT','adverse_risk':'NO_MATERIAL_ADVERSE_FOUND','breakout_support':None,'breakout_evidence':None,'summary':'Synthetic test evidence interpretation only.',
            'citations':[pack['documents'][0]['id']],'event_risks':[],'limitations':['Synthetic contract evidence, not a real provider run.']}
