# AI Agent Case Studies

Sanitized architecture and delivery notes for private AI-agent projects. The code and data are private, but the case studies document the engineering shape, tradeoffs, and delivery workflow.

## Case Study: Telegram / LLM Knowledge System

### Problem

Large Telegram communities contain useful operational knowledge, but the raw export is hard to search, summarize, or use inside a runtime assistant. The goal was to turn chat history into a structured local knowledge system with explainable pipeline stages and a control surface for long LLM runs.

### Solution

Built a SQL-first pipeline that processes Telegram exports into structured artifacts:

- import and normalize Telegram message history;
- split history into stable blocks for LLM processing;
- run staged LLM extraction for topics, questions, cases, people, and taxonomy;
- store intermediate and final results in SQLite;
- generate Markdown wiki outputs from SQL;
- expose a Control Center UI for run status, stage progress, token spend, retries, and diagnostics;
- compile runtime policy files for assistant routing.

### Architecture

```text
Telegram export
  -> SQLite ingestion
  -> block queue
  -> LLM1 extraction
  -> LLM2 merge and question/case generation
  -> taxonomy and topic grouping
  -> people/contact wiki
  -> scope evaluation and repair
  -> runtime policy and answer routing
```

The system is intentionally local-first. SQLite is the source of truth for pipeline state, generated Markdown is treated as a readable projection, and the UI reads live state instead of scraping logs.

### Control Center

The Control Center was built to make long-running agent/LLM jobs observable:

- live pipeline status and current stage;
- progress counters per stage;
- reused vs newly generated work;
- token totals and per-stage spend;
- retry and failure counters;
- stale heartbeat detection;
- diagnostic links to generated artifacts.

### Agent Workflow

The project also includes agent guardrails for working safely in a long-running local pipeline:

- pre-action checks for git status, worktrees, and pipeline status;
- explicit protection for local chat config changes;
- no accidental use of obsolete worktrees;
- tests and lints for guardrail scripts;
- small commits after complete, reviewable changes.

### Technologies

Python, SQLite, SQL-first pipeline design, LLM provider routing, local web UI, Markdown artifact generation, unittest, ruff, shell automation, agent workflow guardrails.

### What This Demonstrates

- Designing LLM pipelines that are restartable, inspectable, and cost-aware.
- Using SQL as a stable coordination layer between LLM stages and UI.
- Building operational tools for real pipeline runs instead of relying on terminal logs.
- Working with agents in a disciplined loop: plan, delegate, inspect, patch, test, commit.

## Case Study: Codex / Gemini Workflow Automation

### Problem

When multiple agent models and provider accounts are used in daily development, the bottleneck becomes routing work to the right model, tracking quota state, and keeping local sessions manageable.

### Solution Shape

A private local toolset coordinates developer-agent workflows:

- local tray/control UI;
- account and quota visibility;
- model/provider switching;
- shell and browser checks;
- small automation hooks for repeatable validation tasks;
- experiments with delegating implementation and verification to weaker/faster coding agents.

### What This Demonstrates

- Practical model orchestration around real developer workflows.
- Knowing when to use a stronger reviewer model and when to delegate bounded implementation.
- Automation around lint/test/review loops rather than one-shot prompting.

## Public Projects

Related public repositories:

- [native-audio-translator](https://github.com/Dmitry-dev-pet/native-audio-translator)
- [dodo-table-events](https://github.com/Dmitry-dev-pet/dodo-table-events)
- [hotwills](https://github.com/Dmitry-dev-pet/hotwills)
- [mermaid-compiler](https://github.com/Dmitry-dev-pet/mermaid-compiler)

## Notes

These notes intentionally omit private chat content, credentials, client details, and source code from private repositories. They are written to show architecture, delivery habits, and agent workflow maturity without exposing confidential material.
