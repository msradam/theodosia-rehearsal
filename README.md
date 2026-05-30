# theodosia-rehearsal

Fifteen [Theodosia](https://github.com/msradam/theodosia) MCP servers in one drop-in `.mcp.json`. Each example is a Burr `Application` mounted as its own MCP server. Five are real production agent workflows; eight are classic computing demos lifted from public-domain sources, reconstructed as finite state machines; one is a Chekhov one-act; one is the Crowther/Woods cave adventure.

Every server runs offline against shipped synthetic data. No API keys.

## Install

```bash
git clone https://github.com/msradam/theodosia-rehearsal.git
cd theodosia-rehearsal
uv sync
```

## Use with Claude Code

The bundled `.mcp.json` registers all fifteen servers. Open the directory in Claude Code and they auto-register, or pass the file explicitly:

```bash
claude --mcp-config .mcp.json
```

For Cursor or fast-agent, see the [Theodosia deployment recipes](https://msradam.github.io/theodosia/deployment/).

## The fifteen servers

### Real agent workflows

| Server | Scenario |
|---|---|
| `rehearsal-coffee` | Coffee-order with the canonical refusal-recovery loop. Try `pay` before `take_order` and read the structured refusal. |
| `rehearsal-incident` | SRE incident investigation. Reads a shipped Alertmanager JSON, slices a service log, spawns a sub-application for hypothesis formation, mitigates, verifies. |
| `rehearsal-git-review` | Real `git status` / `log` / `show` against the working repository. Phase-gated review (read commits before commenting). |
| `rehearsal-security-audit` | Real `bandit` + `detect-secrets` against a shipped vulnerable Python snippet. Patch-overlay loop never edits the source. |
| `rehearsal-unix-health` | Real `df` / `ps` / `vm_stat` / `free` shellouts. System-health classifier with phase-gated reporting. |

### Original

| Server | Scenario |
|---|---|
| `rehearsal-proposal` | Anton Chekhov, *The Proposal* (1889). Two terminals (accept, collapse). Press the same dispute three times and Lomov's nerves give out. Public-domain literary source. |

### Classic computing demos (original FSM implementations)

| Server | Drawn from |
|---|---|
| `rehearsal-adventure` | Colossal Cave-style room navigation (Crowther/Woods 1976; public domain via Don Woods). |
| `rehearsal-eliza` | Weizenbaum's pattern-reflecting psychiatrist (1966 CACM paper). Reflections must accumulate before close is reachable. |
| `rehearsal-hammurabi` | Sumerian kingdom-management (Dyment 1968, Ahl 1973; Ahl placed his BASIC games in the public domain). |
| `rehearsal-hanoi` | Towers of Hanoi (Lucas 1883 mathematical puzzle). The cleanest refusal demo: `illegal_move`, `empty_source`, `same_peg`. |
| `rehearsal-wumpus` | Hunt the Wumpus (Yob 1972, *Creative Computing* 1973). Dodecahedron cave, hazards, five arrows. |
| `rehearsal-quadrant-combat` | Sector combat in the Mayfield-1971 tradition. Energy-bounded beams, limited torpedoes, refuel at starports. No trademark mark used. |
| `rehearsal-lunar-lander` | Storer's *Lunar* (1969 PDP-8 FOCAL). Burn fuel against lunar gravity; land soft (≤5 m/s), hard, or crater. |
| `rehearsal-bulls-and-cows` | Centuries-old code-breaking pencil game. Guess a four-digit secret; each guess returns bulls and cows. |
| `rehearsal-animal` | Luehrmann's *Animal* (c. 1973). Twenty-questions decision tree that learns when it loses. |

See `NOTICE.md` for full provenance.

## What gets demonstrated

- **Structured refusals**: every server returns `{"error": ..., "valid_next_actions": [...]}` on out-of-order calls. `rehearsal-hanoi` and `rehearsal-coffee` are the clearest demonstrations; `rehearsal-eliza` shows a multi-turn gate (cannot `close` before three `reflect` turns).
- **Hash-chained ledger**: every session writes `ledger.jsonl` next to the tracker log. Run `theodosia verify` to check a session.
- **Sub-applications**: `rehearsal-incident` spawns a sub-FSM for the investigation phase; both the parent and the child show up in `theodosia sessions show`.
- **Real shellouts on synthetic data**: `rehearsal-security-audit` runs `bandit` against the shipped vulnerable snippet; `rehearsal-unix-health` reads the host's actual metrics; `rehearsal-git-review` reads the rehearsal repo's own git history.

## License

Apache 2.0 (see `LICENSE` and `NOTICE.md`).
