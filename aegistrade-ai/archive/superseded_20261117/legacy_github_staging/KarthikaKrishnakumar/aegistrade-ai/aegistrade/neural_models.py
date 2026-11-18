"""One cached CPU embedding/reranker pair per process, public weights only."""
from functools import lru_cache
from pathlib import Path
import os

EMBEDDING_MODEL='sentence-transformers/all-MiniLM-L6-v2'
RERANKER_MODEL='cross-encoder/ms-marco-MiniLM-L6-v2'


def model_cache():
    return str(Path(os.getenv('AEGIS_MODEL_CACHE',str(Path(os.getenv('AEGIS_DATA_DIR','data'))/'model_cache'))).resolve())


@lru_cache(maxsize=2)
def load_models(cache_folder):
    from sentence_transformers import SentenceTransformer,CrossEncoder
    import torch
    torch.set_num_threads(min(4,os.cpu_count() or 1))
    embedder=SentenceTransformer(EMBEDDING_MODEL,cache_folder=cache_folder,device='cpu',trust_remote_code=False,token=False,model_kwargs={'use_safetensors':True})
    reranker=CrossEncoder(RERANKER_MODEL,cache_folder=cache_folder,device='cpu',trust_remote_code=False,token=False,
                         model_kwargs={'use_safetensors':True})
    import re
    for instance,identifier in ((embedder,EMBEDDING_MODEL),(reranker,RERANKER_MODEL)):
        ref=Path(cache_folder)/('models--'+identifier.replace('/','--'))/'refs'/'main'
        revision=ref.read_text().strip() if ref.exists() else ''
        instance._aegis_revision=revision if re.fullmatch(r'[0-9a-f]{40}',revision) else 'unknown'
    return embedder,reranker
