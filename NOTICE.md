# Notice

This repository is licensed under Apache 2.0. The Python code under `examples/`
is original work. Each example's docstring credits the historical computing
demo it draws on, where applicable.

## Provenance of the classic demos

The mechanics of the eight games below are public-domain or freely distributed
within their decade of origin. Source code in this repository is original; the
docstrings cite the historical authors for attribution and context only.

| Example | Historical reference |
|---|---|
| `08_eliza.py` | Joseph Weizenbaum, *ELIZA: A Computer Program for the Study of Natural Language Communication Between Man and Machine*, CACM 9(1), January 1966. |
| `09_hammurabi.py` | Doug Dyment (1968, HP-2000) and David Ahl, *BASIC Computer Games* (1973). Ahl placed the collection in the public domain. |
| `10_hanoi.py` | Edouard Lucas, 1883 mathematical puzzle. No copyright on the puzzle. |
| `11_wumpus.py` | Gregory Yob, *Hunt the Wumpus*, *Creative Computing*, September-October 1973. |
| `12_quadrant_combat.py` | Inspired by Mike Mayfield's 1971 high-school BASIC space-combat game and the resource-bounded sector-combat tradition collected in Ahl, *BASIC Computer Games* (1973). Names and trademarks of any commercial entertainment franchise that game later became associated with are NOT used in this repository; this is a from-scratch implementation. |
| `13_lunar_lander.py` | Jim Storer, *Lunar*, Lexington High School Math Club (1969), FOCAL on a PDP-8. Published in Ahl (1973). |

## Upstream MCP servers used

These demos spawn third-party MCP servers as child processes via `mount(upstream=...)`. The upstream servers' tools are called from action bodies and never exposed to the connected agent. Each upstream server ships under its own license; this repository does not bundle their source.

| Example | Upstream server | License |
|---|---|---|
| `14_document_pipeline.py` | [docling-mcp](https://github.com/docling-project/docling-mcp), launched via `uvx --from docling-mcp docling-mcp-server` | MIT |
| `15_code_audit.py` | [@modelcontextprotocol/server-filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem), launched via `npx -y @modelcontextprotocol/server-filesystem <target>` | MIT |

## Theodosia examples lifted from upstream

`01_coffee.py`, `02_incident.py`, `03_git_review.py`, `04_security_audit.py`,
`05_unix_health.py`, `06_proposal.py`, and `07_adventure.py` are adapted from
the Apache-2.0 example set in [theodosia](https://github.com/msradam/theodosia),
which is itself licensed under Apache 2.0.

`02_incident.py`, `04_security_audit.py`, and the data files under
`examples/data/` ship synthetic fixtures (an Alertmanager JSON, sample logs,
a deliberately-vulnerable Python snippet, a small markdown corpus) authored
for use in those demos.

## Trademarks

Trademarks referenced in attribution remain the property of their respective
owners. This project does not use the marks of CBS Studios, Hasbro, Invicta
Plastics, IBM Corporation, or any commercial entertainment or game-publishing
company in its example names or in the user-visible MCP server names.

## Attribution

Theodosia is independent open-source work by Adam Munawar Rahman. This
demonstration repository does not represent the views of IBM Corporation or
any other employer.
