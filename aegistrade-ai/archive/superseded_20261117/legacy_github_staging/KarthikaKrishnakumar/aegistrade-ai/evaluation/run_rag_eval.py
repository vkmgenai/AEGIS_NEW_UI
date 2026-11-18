"""Compare retrieval configurations on authored development queries; no paid LLM calls."""
from pathlib import Path
import json,math,argparse,time
from aegistrade.knowledge import PolicyRetriever,POLICIES,evaluate_retrieval
from aegistrade.corpus import corpus_info


def score(retriever,queries,rewrite):
    started=time.perf_counter();result=evaluate_retrieval(retriever,queries,5,rewrite=rewrite)
    mrr=[];ndcg=[]
    for row in result['rows']:
        relevant=set(row['relevant']);positions=[i for i,p in enumerate(row['returned'],1) if p in relevant]
        mrr.append(1/min(positions) if positions else 0.)
        dcg=sum(1/math.log2(i+1) for i in positions)
        ideal=sum(1/math.log2(i+1) for i in range(1,min(5,len(relevant))+1))
        ndcg.append(dcg/ideal)
    return {'queries':len(queries),'recall_at_5':result['recall_at_k'],'hit_at_5':result['hit_at_k'],
            'mrr_at_5':round(sum(mrr)/max(1,len(mrr)),4),'ndcg_at_5':round(sum(ndcg)/max(1,len(ndcg)),4),
            'elapsed_seconds':round(time.perf_counter()-started,3),'rows':result['rows']}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=Path('reports/rag_development.json'))
    p.add_argument('--offline-only',action='store_true');a=p.parse_args()
    here=Path(__file__).parent/'retrieval'
    read=lambda name:[json.loads(line) for line in (here/name).read_text().splitlines() if line.strip()]
    old=read('queries_36.jsonl');queries=read('queries_expanded_dev.jsonl')
    if len({q['id'] for q in queries})!=len(queries):raise ValueError('Retrieval case IDs must be unique')
    info=corpus_info();offline=PolicyRetriever(mode='offline')
    if any(set(q['relevant_ids'])-{p['id'] for p in offline.docs} for q in queries):raise ValueError('Label references an unknown corpus ID')
    print('Evaluating legacy and expanded offline retrieval...',flush=True)
    results={'legacy_16_offline_legacy_queries':score(PolicyRetriever(docs=POLICIES),old,True),
             'expanded_offline_legacy_queries':score(offline,old,True),
             'expanded_offline_dev_queries':score(offline,queries,True)}
    if not a.offline_only:
        print('Evaluating neural retrieval without and with query rewriting...',flush=True)
        neural=PolicyRetriever(mode='neural')
        results['expanded_neural_before_rewrite']=score(neural,queries,False)
        results['expanded_neural_after_rewrite']=score(neural,queries,True)
        results['expanded_neural_legacy_queries']=score(neural,old,True)
    report={'date':'2026-11-09','corpus':info,'results':results,'paid_llm_calls':0,
            'label_status':'Authored development candidates; independent human relevance review and held-out evaluation remain outstanding.',
            'limitations':['No claim of LLM explanation faithfulness or judge calibration from retrieval scores.',
                'Legacy relevance labels are not exhaustive across the expanded corpus.',
                'Rewriting comparison holds corpus, models, reranker and store fixed; the query-side technique is the changed component.']}
    a.output.parent.mkdir(exist_ok=True,parents=True);a.output.write_text(json.dumps(report,indent=2))
    print(json.dumps({k:{a:b for a,b in v.items() if a!='rows'} for k,v in results.items()},indent=2))

if __name__=='__main__':main()
