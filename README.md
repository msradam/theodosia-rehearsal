# theodosia-rehearsal

Ten [Theodosia](https://github.com/msradam/theodosia) examples wired as a drop-in `.mcp.json` for Claude Code, Cursor, or any MCP client. Each example is a Burr `Application` mounted as its own MCP server; together they exercise the whole Theodosia surface: refusals, streaming, forking, sub-applications, typed state, multi-graph mounts, OpenTelemetry, real shellouts, and parallel work.

## Setup

```bash
git clone https://github.com/msradam/theodosia-rehearsal.git
cd theodosia-rehearsal
uv sync
```

Then point Claude Code at the bundled `.mcp.json`:

```bash
claude --mcp-config .mcp.json
```

Or open the directory and Claude Code picks `.mcp.json` up automatically. Cursor and fast-agent read the same shape (see the [Theodosia deployment recipes](https://msradam.github.io/theodosia/deployment/) for client-specific config locations).

## The ten examples

| Server name | File | What it exercises |
|---|---|---|
| `rehearsal-coffee` | `examples/01_coffee.py` | The canonical refusal-recovery loop. Pay before ordering, see the `invalid_transition` refusal with `valid_next_actions`, recover. |
| `rehearsal-streaming` | `examples/02_streaming.py` | `@streaming_action`. The narrator yields chunks; the MCP client sees them as progress notifications in real time. |
| `rehearsal-forking` | `examples/03_forking.py` | `fork_at` and `fork_from_past`. Branch a budget-planning session at any past step to explore an alternative without losing the original. |
| `rehearsal-typed-state` | `examples/04_typed_state.py` | Pydantic-typed state via Burr's `PydanticTypingSystem`. JSON schema in `theodosia://graph`; Pydantic validation surfaces as `action_error` refusals. |
| `rehearsal-multi-graph` | `examples/05_multi_graph.py` | `mount_multi`. Two graphs (orders, tickets) on one MCP server; namespaced tools (`orders_step`, `tickets_step`) and resources (`theodosia://orders/graph`). |
| `rehearsal-shell` | `examples/06_local_shell.py` | Real `/bin/sh -c` against a per-session temp sandbox seeded from `examples/data/local_shell/`. Sandbox-escape patterns refused. |
| `rehearsal-git` | `examples/07_git_review.py` | Real `git status` / `log` / `show` via subprocess. Defaults to its own checkout; set `GIT_REPO` to point elsewhere. |
| `rehearsal-otel` | `examples/08_otel.py` | `OpenTelemetryBridge` wired in. Every action emits OTel spans; capture them with any OTel collector. |
| `rehearsal-research` | `examples/09_parallel_research.py` | `asyncio.gather` fan-out over the shipped markdown corpus in `examples/data/parallel_research/`. Five sources searched in parallel. |
| `rehearsal-incident` | `examples/10_incident.py` | Sub-application investigation (`spawn_subapp`). Reads real Alertmanager JSON + service logs from `examples/data/incident_response/`, opens a sub-FSM for the investigation phase, mitigates, and verifies. |

## Try it

Once Claude Code is running with the config loaded, try these in chat:

- **`rehearsal-coffee`**: "Pay for a coffee." Watch the refusal name what's reachable. Then: "Order a mocha and pay $5." Watch the recovery.
- **`rehearsal-streaming`**: "Tell me what you find about a missing Postgres replica." Watch chunks arrive in real time.
- **`rehearsal-forking`**: Build a budget, then ask the agent to fork three steps back and try a different category.
- **`rehearsal-incident`**: "Investigate the active alert and propose a mitigation." The agent will read the alert JSON, slice the log file, spawn a sub-application to form a hypothesis, and recommend a rollback.

Run `theodosia sessions show <id>` or `theodosia ui` afterward to replay any of them step-by-step with state diffs.

## What this demonstrates

- **One agent surface (`step`) across every workflow.** The agent never needs a per-FSM SDK.
- **Refusals are recoverable**, not exceptions. Every refusal carries `valid_next_actions`.
- **Recorded by default**. Every successful step and every refused attempt is in Burr's tracker and in Theodosia's `refusals.jsonl` sidecar, with a hash-chained `ledger.jsonl` next to them.
- **Replayable and forkable**. Any session in any example can be replayed (`theodosia sessions show`) or branched (`fork_at`).
- **Composable through `upstream`**. A Theodosia action body can call tools on other MCP servers (filesystem, browser, etc.) and the agent only sees `step`.

## License

Apache 2.0. The examples are derivative work of [Theodosia's shipped examples](https://github.com/msradam/theodosia/tree/main/examples) and share its license.
