"""Prepare one named universe, preserving all other datasets; no LLM calls."""
from pathlib import Path
from datetime import date,timedelta
from zoneinfo import ZoneInfo
from datetime import datetime
import argparse,json,time
import pandas as pd
from aegistrade.dataset_jobs import prepare,status


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--universe',required=True,choices=['nifty20','nifty100','research30'])
    parser.add_argument('--data-root',type=Path,default=Path('data'))
    parser.add_argument('--start',type=date.fromisoformat)
    parser.add_argument('--end',type=date.fromisoformat)
    parser.add_argument('--force',action='store_true',help='Rebuild the selected universe using the requested evaluation dates, reusing validated cached bars where possible')
    args=parser.parse_args();old=args.data_root/'nse_nifty20'/'manifest.json'
    baseline=json.loads(old.read_text()) if old.exists() else {}
    end=args.end or (date.fromisoformat(baseline['requested_end']) if baseline.get('requested_end') else datetime.now(ZoneInfo('Asia/Kolkata')).date()-timedelta(days=1))
    start=args.start or (date.fromisoformat(baseline['requested_start']) if baseline.get('requested_start') else (pd.Timestamp(end)-pd.DateOffset(years=5)).date())
    reply=prepare(args.data_root,args.universe,start,end,force=args.force)
    if reply.get('already_prepared'):print('Already validated; activate explicitly in Market Data.');return
    last=None
    while True:
        job=status(args.data_root,args.universe)
        if job and job.get('message')!=last:print(job['message'],flush=True);last=job['message']
        if job and job['status'] not in {'QUEUED','PREPARING'}:
            if job['status']!='COMPLETE':raise SystemExit(job.get('error_detail') or job['status'])
            return
        time.sleep(1)

if __name__=='__main__':main()
