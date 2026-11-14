from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlsplit
import json

from fastapi.testclient import TestClient


def retained_run(root:Path,run_id='20261114T153948-test0001'):
    folder=root/run_id;folder.mkdir(parents=True)
    manifest={'schema':'aegistrade-capstone-ledger-v1','run_id':run_id,
      'created_at_utc':'2026-11-14T10:09:48+00:00','finished_at_utc':'2026-11-14T10:10:00+00:00',
      'status':'COMPLETED','exit_code':0,'paid_inference_authorized':False,
      'report_sha256':'abc','configuration':{'experiment':'E4','split':'development','repeats':1}}
    (folder/'manifest.json').write_text(json.dumps(manifest))
    (folder/'events.jsonl').write_text(json.dumps({'at_utc':manifest['created_at_utc'],'event':'queued'})+'\n'+json.dumps({'at_utc':manifest['finished_at_utc'],'event':'finished','status':'COMPLETED'})+'\n')
    (folder/'report.json').write_text(json.dumps({'experiment':'E4','limitation':'Synthetic deterministic ablation.','rows':[{'variant':'ROUTER','output':{'model_errors':[]}}]}))
    return run_id


def test_capstone_ledger_api_is_read_only_and_path_safe(monkeypatch,tmp_path):
    import app.api as api
    ledger=tmp_path/'runs';run_id=retained_run(ledger)
    monkeypatch.setenv('AEGIS_CAPSTONE_LEDGER_DIR',str(ledger))
    client=TestClient(api.app)
    listing=client.get('/evaluation/capstone/runs')
    assert listing.status_code==200 and listing.json()['read_only'] is True
    assert listing.json()['runs'][0]['run_id']==run_id
    detail=client.get('/evaluation/capstone/runs/'+run_id)
    assert detail.status_code==200 and detail.json()['report_preview']['row_count']==1
    assert detail.json()['report_preview']['variants']==['ROUTER']
    report=client.get('/evaluation/capstone/runs/'+run_id+'/report')
    assert report.status_code==200 and report.json()['experiment']=='E4'
    assert client.get('/evaluation/capstone/runs/..%2Fsecret').status_code in {404,422}


def test_capstone_ledger_workspace_displays_retained_run(monkeypatch,tmp_path):
    from streamlit.testing.v1 import AppTest
    import app.api as api
    import requests
    ledger=tmp_path/'runs';run_id=retained_run(ledger)
    monkeypatch.setenv('AEGIS_CAPSTONE_LEDGER_DIR',str(ledger))
    client=TestClient(api.app)
    def adapt(r):return SimpleNamespace(ok=r.status_code<400,status_code=r.status_code,text=r.text,content=r.content,json=r.json)
    def get(url,**kw):
        u=urlsplit(url);return adapt(client.get(u.path+('?' +u.query if u.query else '')))
    monkeypatch.setattr(requests,'get',get)
    at=AppTest.from_file(Path(__file__).resolve().parents[1]/'app'/'ui.py',default_timeout=30).run()
    at.selectbox(key='aegis_workspace').select('Capstone Evaluation').run()
    assert not at.exception
    assert run_id in at.selectbox(key='capstone_ledger_run').value
    assert any('Synthetic' in warning.value or 'zero-generation' in warning.value for warning in at.warning)
    assert any('Replay creates a new run directory' in caption.value for caption in at.caption)
