"""Ingest reviewed JSONL policy passages; never execute instructions in documents."""
import argparse,json
from pathlib import Path
from aegistrade.corpus import validate_passages

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True,type=Path)
    p.add_argument('--output',type=Path,default=Path('data/policy_corpus.json'))
    a=p.parse_args()
    from aegistrade.corpus import load_corpus
    rows=load_corpus(a.input)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(rows,indent=2))
    print(f'Ingested {len(rows)} passages with source/date metadata into {a.output}')
if __name__=='__main__':main()
