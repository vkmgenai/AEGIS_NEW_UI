# AegisTrade v0.19.1 — current documentation set

Prepared 11 November 2026. Read in this order:

1. [Project Design and Orchestration](AegisTrade_v0_19_1_Project_Design_and_Orchestration.docx): current architecture, five diagrams, exact LLM/MCP flow, evidence, memory, exits, audit and limitations.
2. [UI Demo and Test Guide](AegisTrade_v0_19_1_UI_Demo_and_Test_Guide.docx): prerequisites, one settings profile, short smoke test, three-month replay, saved example, pauses and a 15-minute exam sequence.
3. [Fresh Viva Questions and Answers](AegisTrade_v0_19_1_Viva_Questions_and_Answers.docx): 72 questions across nine topics with source-grounded answers.

Editable Markdown sources accompany the Word files; standalone diagrams are in assets/. Rebuild with `.venv/bin/python -m scripts.build_current_version_documents` from the project root. Documentation checks are in documentation_verification.json. Existing application runs and credentials were not changed; documentation generation starts no inference calls.

Subsequent v0.19.2 update: [Configurable Initial Stop-Loss UI](../AegisTrade_Configurable_Stop_Loss_UI_Guide.docx). The v0.19.1 set remains the design snapshot before initial stops became configurable.
