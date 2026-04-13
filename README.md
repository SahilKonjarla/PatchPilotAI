# PatchPilotAI

PatchPilotAI is a lightweight multi-agent code debugging and app review system built with FastAPI. The backend is focused on accepting code review events, moving them through a staged analysis pipeline, and returning useful review output without adding unnecessary infrastructure.

The first version is intentionally simple:

- FastAPI backend
- Route-first API design
- No database requirement
- In-memory or lightweight queue
- Worker-based execution
- Non-blocking stage progression
- Multi-agent analysis for diffs, code quality, bugs, security, tests, documentation, and summaries

## Goal

The goal of the backend is to build a small, practical multi-agent system for debugging code changes and reviewing app updates. It should be able to receive a request, analyze the commit or diff, route work to the right agents, and stream or return results as each stage completes.

The system should not bottleneck all work behind one long-running request. Once a request passes one stage, it should move to the next stage through the queue so workers can continue processing other jobs in parallel.

## Backend Architecture

PatchPilotAI will use FastAPI as the API layer and an orchestrator to coordinate the review workflow.

At a high level:

1. A client submits a review request through a FastAPI route.
2. The request is accepted and converted into a queued job.
3. The orchestrator determines which stages need to run.
4. Workers pick up queued stages and execute the relevant analyzer or agent.
5. When one stage completes, the orchestrator queues the next stage instead of blocking the whole pipeline.
6. Final output is collected into a review result that can include findings, risks, summaries, and recommended fixes.

## Pipeline Design

The pipeline should be staged so the backend can keep moving work forward without making one request wait on every agent synchronously.

Planned stages:

- Request intake
- Commit analysis
- Diff analysis
- Code quality review
- Bug detection
- Security review
- Test coverage review
- Documentation review
- PR summary generation
- Final result assembly

Each stage should be able to pass structured output to the next stage. For example, the diff analysis stage can identify changed files and risk areas, then downstream agents can use that context to focus their checks.

## Queue and Workers

The backend needs a queue and worker model so analysis work does not block API request handling.

Expected behavior:

- API routes should accept work quickly.
- Long-running analysis should run in workers.
- Workers should process jobs by stage.
- A completed stage should enqueue the next stage.
- Multiple requests should be able to progress through different stages at the same time.
- The orchestrator should coordinate stage transitions.

The first implementation can use a lightweight queue. A database is not required for the initial backend.

## Core Components

### FastAPI Routes

The backend should expose routes for submitting and checking review work. Initial routes may include:

- `POST /reviews` - submit a new review request
- `GET /reviews/{review_id}` - fetch review status and results
- `GET /reviews/{review_id}/events` - stream or poll stage updates
- `POST /reviews/{review_id}/cancel` - cancel a queued or running review if supported
- `GET /health` - health check

### Orchestrator

The orchestrator is not an agent. It coordinates execution.

Responsibilities:

- Accept review events from routes
- Create the pipeline plan
- Route stages to the correct workers
- Track stage status
- Pass outputs between stages
- Queue the next stage once the current stage completes
- Assemble final review results

### Commit Analyzer

The commit analyzer inspects commit-level context before deeper review begins.

Responsibilities:

- Read commit metadata
- Identify changed files
- Understand commit scope
- Detect large or risky changes
- Provide context to downstream agents

### Diff Analyzer

The diff analyzer focuses on the actual code changes.

Responsibilities:

- Parse changed lines and files
- Identify the scope of the diff
- Highlight high-risk files or patterns
- Summarize the areas affected by the change

## Agent Breakdown

### Diff Analysis Agent

Identifies changed files, scope, and risk.

### Code Review Agent

Evaluates readability, structure, and best practices.

### Bug Detection Agent

Finds logical errors and edge cases.

### Security Agent

Detects vulnerabilities and unsafe patterns.

### Test Coverage Agent

Assesses missing or weak test coverage.

### Documentation Agent

Flags unclear or undocumented code.

### PR Summary Agent

Generates a concise overview of changes and risks.

### Orchestrator

The orchestrator is not an agent. It routes events and coordinates agent execution.

## Review Output

The backend should produce structured review output that can be used by a UI, CLI, or GitHub integration later.

Example result sections:

- Changed files and risk level
- Code quality findings
- Possible bugs
- Security concerns
- Missing or weak tests
- Documentation gaps
- Summary of the pull request
- Recommended next actions

## Initial Scope

The initial backend should stay lightweight and focused.

In scope:

- FastAPI routes
- Request models
- Response models
- Queue abstraction
- Worker loop
- Orchestrator
- Agent interfaces
- Stage-based execution
- In-memory state for local development

Out of scope for the first version:

- Database persistence
- Full GitHub App installation flow
- User accounts
- Billing
- Complex distributed infrastructure

## Development Direction

PatchPilotAI should start as a clean backend service with clear boundaries between routes, orchestration, queueing, workers, and agents. The implementation should make it easy to replace the lightweight queue with a production queue later without rewriting the agent logic.

The important design principle is that each stage should complete independently and hand off to the next stage. This keeps the system responsive and avoids bottlenecking every request behind one synchronous review process.
