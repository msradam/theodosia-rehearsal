# theodosia-rehearsal

Fifteen [Theodosia](https://github.com/msradam/theodosia) MCP servers in one drop-in `.mcp.json`. Each example is a Burr `Application` mounted as its own MCP server. Five are real production agent workflows; two drive other MCP servers (docling, filesystem) as upstream and gate the agent's access to them; one is a Chekhov one-act; one is a Crowther/Woods cave adventure; six are classic computing demos reconstructed as finite state machines.

Every server runs offline against shipped synthetic data. No API keys.

## Install

```bash
git clone https://github.com/msradam/theodosia-rehearsal.git
cd theodosia-rehearsal
uv sync
```

The two upstream demos additionally need `uvx` (ships with `uv`) and `npx` on PATH so they can spawn the docling and filesystem MCP servers as child processes.

## Use with Claude Code

```bash
claude --mcp-config .mcp.json
```

For Cursor or fast-agent, see the [Theodosia deployment recipes](https://msradam.github.io/theodosia/deployment/).

## The fifteen servers

### Real agent workflows

| Server | Scenario |
|---|---|
| `rehearsal-coffee` | Coffee-order with the canonical refusal-recovery loop. Try `pay` before `take_order`. |
| `rehearsal-incident` | SRE incident investigation: shipped Alertmanager JSON, log slicing, hypothesis sub-application, mitigation, verification. |
| `rehearsal-git-review` | Real `git status` / `log` / `show` against the working repository. Phase-gated review. |
| `rehearsal-security-audit` | Real `bandit` + `detect-secrets` against a shipped vulnerable Python snippet. Patch-overlay never edits source. |
| `rehearsal-unix-health` | Real `df` / `ps` / `vm_stat` / `free` shellouts with phase-gated reporting. |

### Upstream MCP composition

Theodosia spawns the upstream MCP server as a child process and calls its tools from action bodies. The connected agent only sees Theodosia's `step` tool; the upstream tools are never exposed.

| Server | Upstream | What it gates |
|---|---|---|
| `rehearsal-document-pipeline` | [docling-mcp](https://github.com/docling-project/docling-mcp) (`uvx --from docling-mcp docling-mcp-server`) | receive PDF -> convert via docling -> review markdown -> tag -> save. Refuses tag before review, save before tag. |
| `rehearsal-code-audit` | [@modelcontextprotocol/server-filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) (`npx`) | start_audit -> read_file -> record_finding -> write_advisory. Refuses record_finding for files not yet read; refuses write_advisory before two findings. |

### Original

| Server | Scenario |
|---|---|
| `rehearsal-proposal` | Anton Chekhov, *The Proposal* (1889). Two terminals: accept, collapse. Press the same dispute three times and Lomov's nerves give out. Public-domain literary source. |

### Classic computing demos (original FSM implementations)

| Server | Drawn from |
|---|---|
| `rehearsal-adventure` | Colossal Cave-style room navigation (Crowther/Woods 1976; public domain via Don Woods). |
| `rehearsal-eliza` | Weizenbaum's pattern-reflecting psychiatrist (CACM 1966). `close` is unreachable before three reflection turns. |
| `rehearsal-hammurabi` | Sumerian kingdom-management (Dyment 1968; Ahl 1973 placed his BASIC games in the public domain). |
| `rehearsal-hanoi` | Towers of Hanoi (Lucas 1883). The cleanest refusal demo: `illegal_move`, `empty_source`, `same_peg`. |
| `rehearsal-wumpus` | Hunt the Wumpus (Yob, *Creative Computing* 1973). Dodecahedron cave, hazards, five arrows. |
| `rehearsal-quadrant-combat` | Sector combat in the Mayfield-1971 tradition. Energy-bounded beams, limited torpedoes, refuel at starports. No commercial trademarks used. |
| `rehearsal-lunar-lander` | Storer's *Lunar* (1969 PDP-8 FOCAL). Burn fuel against lunar gravity; land soft, hard, or crater. |

See `NOTICE.md` for full provenance.

## What gets demonstrated

- **Structured refusals**: every server returns `{"error": ..., "valid_next_actions": [...]}` on out-of-order calls. `rehearsal-hanoi` and `rehearsal-coffee` are the clearest first looks.
- **Upstream MCP composition**: `rehearsal-document-pipeline` and `rehearsal-code-audit` both spawn third-party MCP servers as child processes and route through them. The connected agent sees only `step`; the upstream tool surface stays inside Theodosia.
- **Hash-chained ledger**: every session writes `ledger.jsonl` next to the tracker log. Run `theodosia verify` to check a session.
- **Sub-applications**: `rehearsal-incident` spawns a sub-FSM for the investigation phase; both parent and child show up in `theodosia sessions show`.
- **Real shellouts on synthetic data**: `rehearsal-security-audit` runs `bandit` against a shipped vulnerable snippet; `rehearsal-unix-health` reads the host's actual metrics; `rehearsal-git-review` reads the rehearsal repo's own git history.

## License

Apache 2.0 (see `LICENSE` and `NOTICE.md`).
