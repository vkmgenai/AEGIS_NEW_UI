"""Standalone deterministic reviewed-lesson demonstration, no LLM tokens."""
import tempfile
from pathlib import Path
from aegistrade.lessons import ReviewedPlaybook,propose_failure_lesson

def main():
    with tempfile.TemporaryDirectory() as d:
        store=ReviewedPlaybook(Path(d)/'lessons.sqlite')
        for error,decision,reason in [
            ('BAD_LESSON','REJECT','Unsafe loss-chasing; violates bounded risk policy'),
            ('STALE_DATA','ACCEPT','Consistent with quote freshness policy')]:
            proposal=propose_failure_lesson(error)
            idx=store.propose(proposal['topic'],proposal['lesson'],proposal['applies_when'])
            store.review(idx,decision,reason)
            print(error,'->',decision, 'reason:',reason)
        print('Approved lessons:',store.accepted('data_freshness'))
        print('Frozen manifest:',store.freeze('CLI_HUMAN_REVIEW_SIMULATION'))
if __name__=='__main__':main()
