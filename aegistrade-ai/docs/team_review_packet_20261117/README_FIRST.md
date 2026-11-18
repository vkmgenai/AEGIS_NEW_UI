# AegisTrade distributed team-review packet — 20261117

## Correct order of use

1. Each reviewer records the Git commit they pulled.
2. **Before viewing results**, complete assigned files in `blinded_review/` and sign with name/date/reason.
3. Return blinded reviews to Karthika. Preserve the originals and resolve disagreements explicitly.
4. Freeze reviewed cases and hashes. Only then run paid E1/E2/E3.
5. Open `observed_results/` for metric, trace, safety and limitation review.
6. Complete the role questionnaire. PENDING is required when evidence is absent.

## Why no additional paid run was added

The present blocker is independent review, not run count. Running E1/E2/E3 before reviewers freeze labels would undermine the held-out protocol. Current runs are sufficient for the team to perform phase-one review and inspect implementation/development evidence. They are not sufficient to claim the minimum bar is closed.

## Included evidence

- E4 run `20261117T105811-138ef587` (completed; synthetic deterministic ablation)
- Deterministic neural run `20261117T110205-1c7df087` (completed; candidate labels)
- Neural RAG development report `rag_development_20261117.json` (101 authored queries)
- AI experiment `026512e1f9054db09011c4e9e611ef8d` summary (three cases; C0/C1/C2; one C1 and one C2 model error)
- C2 portfolio `dc354841097240e0bc88d8430953fa22` review extract (development evidence and human overrides)
- Local intentional-CI failure record (not hosted failed-CI evidence)

## Still required after review

- Reviewed/frozen 20 development and 40 held-out golden cases with family separation.
- Independently authored/reviewed 32 attack and 10 clean labels.
- At least 20 human judge-calibration labels and a different-family judge run.
- Paid E1 development, then three untouched held-out repetitions.
- Actual model-level E2 defence off/on and clean false-block evaluation.
- A human-reviewed frozen playbook, including accepted and rejected lessons, followed by E3 off/on.
- Hosted failed-CI evidence, fired-alert evidence, contribution records, final slides and video.

## Security

This packet excludes `.env`, API keys, reviewer tokens, SQLite databases and cached/licensed source documents. The full raw local databases remain on Karthika's machine and should not be emailed.
