"""Download NSEPython history for a pre-period-selected top-20 Nifty universe."""
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
import argparse
import pandas as pd
from aegistrade.nse_data import build_dataset

def main():
    today=datetime.now(ZoneInfo('Asia/Kolkata')).date()
    end=today-timedelta(days=1);start=(pd.Timestamp(end)-pd.DateOffset(years=5)).date()
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--start',type=lambda s:datetime.fromisoformat(s).date(),default=start)
    p.add_argument('--end',type=lambda s:datetime.fromisoformat(s).date(),default=end)
    p.add_argument('--output',type=Path,default=Path('data/nse_nifty20'))
    p.add_argument('--constituents',type=Path)
    p.add_argument('--membership-asof',type=lambda s:datetime.fromisoformat(s).date())
    p.add_argument('--top',type=int,default=20)
    a=p.parse_args()
    if a.membership_asof and not a.constituents:p.error('A dated membership snapshot requires --constituents')
    result=build_dataset(a.output,a.start,a.end,top_n=a.top,constituent_path=a.constituents,
                         membership_asof=a.membership_asof,progress=lambda s:print(s,flush=True))
    print('Completed:',result['rows'],'rows for',len(result['symbols']),'stocks')
    print('Survivorship bias:',result['survivorship_bias'])
if __name__=='__main__':main()
