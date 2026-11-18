# AegisTrade retrieval corpus

`corpus.jsonl` contains 87 deliberately short passages: 78 project policies/code-derived specifications and nine source-linked background references. `manifest.json` records scope and review status. The existing 16 passage IDs are retained; strategy, selection, data-quality, research-gate, execution and evaluation details are now covered.

The project material is experimental configuration, not NSE regulation. External material is a paraphrased primary/upstream-source summary and cannot override project policy. Original publication dates are stored only where verified; retrieval dates are not presented as publication dates. Unknown-date external references are conservatively unavailable to a historical case before their first retrieval date. Code-derived policies remain the declared rules of the experiment.

No raw OHLCV rows, later returns, held-out labels, private tokens, contemporary company news or draft-proposal instructions are ingested here. Numerical market evidence comes through the locked market tool. This is not a company-fundamentals/news knowledge base.

To add material, curate a short passage with stable ID, title, text, source, date/date-kind, authority and source URL or code locator. Use `scripts/ingest_policies.py` to validate a JSON/JSONL corpus. Set `AEGIS_POLICY_CORPUS_PATH` only when intentionally replacing the complete corpus; preserve required project-policy passages. Rebuild the index and repeat retrieval evaluation. A changed corpus invalidates outstanding research-linked approvals and requires fresh C2 research.

All labels and summaries remain subject to team review. Development retrieval scores do not establish independent gold quality or generated-answer faithfulness.
