# RAG implementation and knowledge-data guide

Updated 9 November 2026.

## Is RAG implemented?

Yes. C2's strategy and compliance-critic specialists call `search_policy` through an actual FastMCP connection. The tool retrieves source-labelled passages, and its observations are sent back to the LLM before it generates a cited typed response. Citations, required tool evidence, a project-policy source and the current corpus fingerprint are checked before a supervised proposal is allowed.

The earlier implementation had 16 short policies and an active BM25/TF-IDF teaching baseline. The project now has 81 curated passages, actual local neural embeddings, a neural reranker and persistent Chroma storage. The private retrieval mode has been changed to `neural` after successful index verification. Restart the running API/dashboard to load it.

The language generation still uses the project's OpenRouter integration and paid-run gates. The embedding and reranking models run locally on CPU; this update made no paid OpenRouter request. Retrieval is a component of GenAI, not proof of generation by itself: the Policy Knowledge page lists evidence, while C2 uses that evidence to generate an explanation.

## What data was added?

| Material | Count | Examples |
|---|---|---|
| Project policies and code-derived specifications | 72 passages | Exact EMA/RSI/breakout rules, regime precedence, top-20 liquidity selection, scoring weights, money/risk rules, C2 completion gate, approvals, stale quotes, reconciliation, memory and evaluation limits |
| Source-linked background references | 9 passages | Official Nifty 50/index-data descriptions, NSE daily-price field definitions and verified symbol-change circulars; upstream NSEPython project description |

The corpus is `knowledge/corpus.jsonl`, with a scope manifest in `knowledge/manifest.json`. The code-derived material is authored from the current implementation and explicitly marked pending team review. External summaries carry original-source URLs. They are not new trading rules, company research reports or independently reviewed gold labels.

The original POL-01 through POL-16 identifiers remain. Additional project passages extend through POL-72. Background references use REF-prefixed identifiers. Passage metadata retains title, source, date, date kind, authority, topic, code/document locator or original URL, publication/retrieval dates where known, and review status.

Close × Volume is a closing-price liquidity proxy, not the official VWAP-based rupee traded-value field.

More rows are not automatically better RAG data. The corpus adds relevant missing concepts rather than stuffing price tables into embeddings. The 26,580 OHLCV rows remain numerical data accessed by code; an LLM must not reconstruct prices or money from approximate vector matches.

## Retrieval and generation sequence

1. The specialist chooses its policy query inside its role/tool budget.
2. The runtime sends that query and the locked case date to the knowledge MCP server.
3. Controlled query rewriting expands a few known aliases while retaining the original query.
4. BM25 retrieves lexical matches. MiniLM embeds the query and searches the persistent cosine-vector index.
5. Reciprocal Rank Fusion combines the two rankings using 1/(60 + rank).
6. The cross-encoder scores the candidate query/passage pairs and reranks them. The configured top passages are returned with source and corpus metadata.
7. The tool observation is appended to the specialist conversation, linked by tool-call ID. The OpenRouter model reads the observations and generates its typed answer.
8. Code checks that cited IDs were actually retrieved and that at least one cited source is a project policy. Public background alone cannot ground route approval. Typed strategy/risk/approval checks remain independent controls.

Current models are `sentence-transformers/all-MiniLM-L6-v2` for 384-dimensional embeddings and `cross-encoder/ms-marco-MiniLM-L6-v2` for reranking. They use public pretrained weights, CPU execution and no remote custom model code. Exact cached model revisions are recorded by the index build. Model scores are ranking values, not calibrated confidence or a probability of profitable trading.

The persistent index is in `data/rag/chroma/`; reusable embeddings are in `data/rag/embedding_cache/`; public model weights are in `data/model_cache/`. `data/rag/index_status.json` records the verified corpus fingerprint, model identity, collection and smoke queries. The corpus is versioned source data; caches and weights are local runtime data.

Qdrant remains an alternative Docker/configured endpoint. Local Chroma was actually exercised. This does not claim that the Qdrant HTTP deployment or a clean-machine Docker run has been demonstrated.

## Historical availability and authority

An external reference is available to a historical case only if its verified publication date is on or before the case date. When publication is unknown, its retrieval date is used conservatively. The model cannot choose a later cutoff: the runtime takes the date from the locked case. The Policy Knowledge page also offers a historical cutoff for inspection.

Project policies describe the experiment's declared settings and are identified separately. They are not represented as company news published in a past market session. Current news, future returns and held-out answers have not been added to the historical decision corpus. A genuine historical-news or company-filings service would require separate point-in-time ingestion, licensing/provenance and evaluation; it is outside this RAG scope.

C2 results record the corpus SHA-256. Changing the corpus, or trying to approve an older result without corpus provenance, requires rerunning current C2 before a new supervised proposal/approval. This keeps an earlier explanation from silently becoming an approval under changed knowledge.

## Measured development results

`reports/rag_development.json` records the configurations and per-query results. The expanded development set contains 101 unique query IDs; the earlier file's repeated IDs were corrected while keeping its query text and labels. These are authored development candidates, not independently labelled held-out data.

| Same expanded corpus, 101 development queries | Passage Recall@5 |
|---|---|
| Offline BM25/TF-IDF plus rewriting | 0.9208 |
| Neural hybrid plus reranker, without rewriting | 0.9505 |
| Neural hybrid plus reranker, with rewriting | 0.9703 |

The rewriting comparison holds corpus, models, vector store and reranker fixed and changes only the query-side technique. MRR@5 and nDCG@5 are also recorded. These scores describe current-knowledge lookup without a historical cutoff; the temporal filter is separately contract-tested and exercised in the MCP path.

A regression is retained: on the old 36-query labels, the original 16-passage offline corpus scored 0.9444 Recall@5, while the expanded neural corpus scored 0.9167. More passages create competing evidence, and the legacy labels are not exhaustive across the expanded corpus. Do not claim universal improvement or silently change labels to make the score rise. The team should review relevance independently.

Retrieval scores do not establish generated-answer faithfulness, useful stock-selection performance, trading profitability or different-family judge calibration. Those still need actual funded C1/C2 runs, human/independent assessment and the capstone evaluation protocol.

## UI and viva demonstration

Open Policy Knowledge after restarting the app. It shows passage counts, project/reference counts, the active pipeline and whether the verified index matches the current corpus. Searches display passage text, authority, indexed/reviewed date, original publication date when known, and original-source/code links.

Useful queries include:

- “Is the RSI entry threshold 30 or 42?”
- “Why were these twenty stocks selected?”
- “What happens if C2 research changes before human approval?”
- “Are NSE prices adjusted for splits, bonuses and demergers?”

Then show a C2 trace containing a search_policy observation, source IDs, corpus fingerprint and typed specialist response. Be explicit about whether that trace is a real paid-provider run or a mocked contract test. Actual stdio MCP neural retrieval has passed with no paid generation. The UI's actual neural search and source display are verified separately; this is evidence of the retrieval path rather than a model-benefit claim.

A viva explanation is: “We retrieve lexical and semantic evidence, fuse and rerank it, then give source-labelled passages to the LLM. Code validates provenance and enforces policy. We measured retrieval separately from explanation quality.”

## Rebuild and extend

For a fresh environment install the project requirements. Linux/Docker/CI use CPU-only Torch to avoid unnecessary GPU dependencies. Model downloads need network access once; after successful caching the project sets HF_HUB_OFFLINE=1 for local model loading. OpenRouter generation still uses its normal internet connection.

```bash
.venv/bin/python -m scripts.build_rag_index --mode neural --activate
HF_HUB_OFFLINE=1 .venv/bin/python -m evaluation.run_rag_eval
```

If deliberately fetching new model weights, temporarily set HF_HUB_OFFLINE=0 for the build command. No OpenRouter key is needed to build or evaluate retrieval.

To curate a replacement corpus, preserve stable IDs and the core policies; add short, source-labelled passages with publication metadata rather than unreviewed prompts or draft proposal instructions. Validate JSON/JSONL with `scripts/ingest_policies.py`, set the intended corpus path, rebuild, repeat evaluation and obtain team review. A custom path replaces the corpus rather than appending hidden extra instructions.

For a new Docker data volume, populate the model/index cache before the paid demonstration, for example `docker compose run --rm -e HF_HUB_OFFLINE=0 api python -m scripts.build_rag_index --mode neural`. The local cache is not automatically copied into a Docker named volume. The existing neural Compose override selects Qdrant; that runtime path remains separately unverified.

## Evidence and remaining work

The source corpus, schema, index builder, persistent store, evaluation runner, MCP source metadata, historical cutoff and UI are implemented. Tests cover provenance, bad source links, corpus changes invalidating approval, background-only citations being rejected, date filtering, persistent-vector round trips and retrieval/UI integration.

The team still needs independent relevance review/held-out queries and calibrated semantic evaluation of real generated explanations. There is no need to add company news or thousands of price chunks merely to increase document count. Add such sources only if expanding the project's actual research question and point-in-time controls.


## Version 0.14 historical-company research update — 9 November 2026

C2 now requires dated company financial filings and issuer news through company_evidence on the existing market MCP. Market and critic independently observe the exact symbol/15:30 IST case pack. A qualifying financial-content citation and SUFFICIENT assessment are required before a proposal; missing/unreadable/future evidence fails closed. Company-pack changes invalidate research and pending approval. Normal generation remains six calls, with seven tool invocations; the shared eight-call ceiling and three specialists remain. The policy corpus is still81 passages; company packs are separate. Real TCS2026-10-23 evidence is cached; INFY is currently insufficient. No paid generation was made for this update. See HISTORICAL_COMPANY_RESEARCH.md and the current Detailed Design and Demo Guide for source bounds, reviewed news/newsletter imports and exact UI steps. Earlier policy-only descriptions are superseded by this section.


## Version 0.15 end-to-end C2 historical portfolio — 9 November 2026

The historical capability is now split explicitly: Technical-only baseline (zero generation) and C2 historical portfolio (dated C2 before prospective entries, scheduled HOLD/EXIT reviews, code risk/strategy exits and next-open accounting). Historical fills use upfront rule approval and a total paid-request allowance, with durable OPEN/CLOSE checkpoints and budget/provider pause/resume. The end date never forces a sale: open holdings retain last-known marks and unrealized P&L; final-close exit intentions remain unfilled. Separate supervised actions still require exact human approval.99 tests pass; actual NSE/MCP/neural integration was verified with explicitly mocked generation, not a paid profitability result. Current guide/viva use source0.15.0, six diagrams and80 questions. See C2_HISTORICAL_PORTFOLIO.md. Earlier descriptions that all historical replay is deterministic are superseded.
