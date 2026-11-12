"""Build/verify local neural RAG. No OpenRouter calls or trade actions."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,os
from aegistrade.corpus import corpus_info
from aegistrade.knowledge import PolicyRetriever


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=['offline','neural'],default='neural')
    p.add_argument('--activate',action='store_true',help='After successful verification, update only the private retrieval-mode setting')
    a=p.parse_args()
    print('Validated corpus:',corpus_info()['passages'],'passages',flush=True)
    print('Loading local retrieval models and index...',flush=True)
    r=PolicyRetriever(mode=a.mode)
    probes={q:[d['id'] for d in r.search(q,5)] for q in [
        'Which RSI threshold permits a reversion entry?',
        'What happens if completed C2 research changes before human approval?',
        'Do raw NSE prices account for bonus issues and demergers?']}
    result={'created_utc':datetime.now(timezone.utc).isoformat(),'mode':a.mode,'corpus':corpus_info(),
        'embedding_model':'sentence-transformers/all-MiniLM-L6-v2' if a.mode=='neural' else None,
        'reranker_model':'cross-encoder/ms-marco-MiniLM-L6-v2' if a.mode=='neural' else None,
        'reranker_revision':getattr(r.cross_encoder,'_aegis_revision',None),
        'embedding_dimensions':int(r.neural_vectors.shape[1]) if r.neural_vectors is not None else None,
        'vector_store':type(r.vector_store).__name__ if r.vector_store else 'TF-IDF in-memory',
        'persisted_collection':getattr(r.vector_store,'name',None),
        'storage_path':getattr(r.vector_store,'path',None),
        'embedding_identity':r.vector_store.collection.metadata.get('embedding_identity') if hasattr(r.vector_store,'collection') else None,
        'smoke_queries':probes,'paid_llm_calls':0,'independently_labelled_quality':'not established'}
    target=Path(os.getenv('AEGIS_DATA_DIR','data'))/'rag'/'index_status.json';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2))
    if a.activate:
        root=Path(__file__).resolve().parents[1];path=root/'.env'
        lines=path.read_text().splitlines() if path.exists() else []
        lines=[line for line in lines if not line.strip().startswith(('AEGIS_RETRIEVAL_MODE=','HF_HUB_OFFLINE='))]
        path.write_text('\n'.join(lines)+f'\nAEGIS_RETRIEVAL_MODE={a.mode}\n'+('HF_HUB_OFFLINE=1\n' if a.mode=='neural' else ''))
        result['activation']='Updated private retrieval mode; restart existing API/dashboard to load it'
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
