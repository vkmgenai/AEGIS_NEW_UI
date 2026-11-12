"""Optional persistent Qdrant index for the neural retrieval path."""
import hashlib,json
import requests
import numpy as np

class QdrantIndex:
    def __init__(self,url,docs,vectors):
        digest=hashlib.sha256(json.dumps(docs,sort_keys=True).encode()).hexdigest()[:16]
        self.base=url.rstrip('/')+'/collections/aegis_policy_'+digest
        self.count=len(docs)
        response=requests.put(self.base,json={'vectors':{'size':int(vectors.shape[1]),'distance':'Cosine'}},timeout=20)
        if response.status_code not in {200,409}:
            # Qdrant versions may return 400 for an existing collection; verify rather than assume success.
            check=requests.get(self.base,timeout=10);check.raise_for_status()
        response=requests.put(self.base+'/points',params={'wait':'true'},json={'points':[
            {'id':i,'vector':vectors[i].tolist(),'payload':d} for i,d in enumerate(docs)]},timeout=30)
        response.raise_for_status()

    def scores(self,embedding):
        response=requests.post(self.base+'/points/query',json={'query':embedding.tolist(),'limit':self.count},timeout=20)
        response.raise_for_status()
        scores=np.full(self.count,-1.0)
        for hit in response.json()['result']['points']:scores[int(hit['id'])]=float(hit['score'])
        return scores


class ChromaIndex:
    """Local persistent cosine index; embeddings always come from the configured model."""
    def __init__(self,path,docs,vectors,embedding_identity):
        import chromadb
        from chromadb.config import Settings
        from pathlib import Path
        from .corpus import corpus_digest
        identity=hashlib.sha256((corpus_digest(docs)+embedding_identity).encode()).hexdigest()[:20]
        self.path=str(Path(path).resolve())
        self.client=chromadb.PersistentClient(path=self.path,settings=Settings(anonymized_telemetry=False))
        self.collection=self.client.get_or_create_collection(name='aegis_rag_'+identity,embedding_function=None,
            metadata={'hnsw:space':'cosine','corpus_sha256':corpus_digest(docs),'embedding_identity':embedding_identity})
        self.ids=[d['id'] for d in docs];self.positions={p:i for i,p in enumerate(self.ids)}
        if self.collection.count()!=len(docs):
            self.collection.upsert(ids=self.ids,embeddings=vectors.tolist(),documents=[d['text'] for d in docs],
                metadatas=[{k:str(d.get(k,'')) for k in ('title','date','source','authority','source_url')} for d in docs])
        self.count=len(docs);self.name=self.collection.name

    def scores(self,embedding):
        result=self.collection.query(query_embeddings=[embedding.tolist()],n_results=self.count,include=['distances'])
        scores=np.full(self.count,-1.0)
        for ident,distance in zip(result['ids'][0],result['distances'][0]):scores[self.positions[ident]]=1-float(distance)
        return scores
