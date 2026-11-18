# Post-UI-freeze evaluation plan

Updated: 18 November 2026

## Why no new final run is being started yet

The v0.35 redesign is still a proposal. Running final held-out inference before
the interface, prompts, policy corpus, validation schemas and experiment contract
are frozen would create another intermediate result. That would spend provider
allowance and require another review cycle.

The existing 102 templates under `evaluation/agentic_candidates_20261117/` remain
unchanged in their original location. They are retained as historical candidate
material and are not moved to archive, deleted, relabelled or silently reused as
independent final evidence.

## Freeze boundary

After the redesigned UI is approved:

1. Freeze the application version, prompt version, policy-corpus hash, evidence
   view, model/adapter, schemas, tool inventory and financial outcome policy.
2. Record those fingerprints in a new evaluation manifest.
3. Generate a new versioned case directory; do not overwrite the 20261117 set.
4. Review the new development, held-out, attack and clean cases without viewing
   model outputs.
5. Validate completeness, family separation, evidence hashes and reviewer fields.
6. Freeze and hash the reviewed records.

## Required final runs after review

| Run | Required comparison | Repetitions | Main measurements |
|---|---|---:|---|
| E1 | C1 single agent vs C2 multi-agent; C0 reference | 3 | task/guard success, grounding, abstentions, errors, calls, cost, median/p95 latency, standardized outcome |
| E2 | C2 defences off vs on; attacks plus clean controls | 1 or 3 as budget permits | attack success, forbidden tool/text attempts, clean false-block rate, cost and latency |
| E3 | C2 reviewed memory off vs on | 3 | held-out task success, regressions, applicability, calls, lesson-generation cost |
| E4 | critic/retrieval ablation and deterministic routing reference | 1 | citation support, validation, cost/latency; financial return secondary |

Failures, timeouts and quota interruptions remain in the report. A resumable
ledger must store every completed repetition so a quota reset never requires
repeating valid paid work.

## What remains valid now

- Three v0.34/v0.35 development E1 repetitions remain engineering evidence.
- The fresh deterministic E4 artifact remains a reproducible negative result.
- C2 portfolio runs remain workflow and simulated-financial evidence.
- The 377-test regression result remains implementation evidence.

None of these substitutes for newly reviewed final held-out evidence after the
code freeze.
