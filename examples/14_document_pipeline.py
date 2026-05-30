"""Document pipeline: gate an agent's access to docling-mcp.

Theodosia drives [docling-mcp](https://github.com/docling-project/docling-mcp)
as an upstream MCP server. The agent connects only to this FSM and only
sees ``step``. Document conversion, markdown export, and persistence
happen inside action bodies via ``call_upstream("docling", ...)``.

Phases enforced by the graph:
  receive -> convert -> review -> tag -> save (terminal)

The FSM refuses ``tag`` before ``review`` has produced a markdown preview,
and refuses ``save`` before tags are recorded. Every upstream docling call
is one ledger entry; the audit trail covers every document touched.

Requires ``uvx`` on PATH so the upstream docling server can boot:

    uvx --from docling-mcp docling-mcp-server --transport stdio

Drop a PDF into ``examples/data/document_pipeline/`` and call
``receive(path=...)`` to start.
"""

from __future__ import annotations

from pathlib import Path

from burr.core import ApplicationBuilder, Condition, State, action

from theodosia import ServingMode, call_upstream, mount

_DEFAULT_INBOX = str(Path(__file__).parent / "data" / "document_pipeline")


@action(reads=[], writes=["pdf_path", "doc_key", "phase", "log"])
async def receive(state: State, pdf_path: str) -> State:
    """Open a PDF for processing. The path must exist on disk."""
    p = Path(pdf_path).expanduser()
    if not p.exists():
        raise ValueError(f"pdf_path does not exist: {pdf_path}")
    if p.suffix.lower() != ".pdf":
        raise ValueError(f"expected a .pdf, got {p.suffix}")
    return state.update(
        pdf_path=str(p),
        doc_key=None,
        phase="received",
        log=[f"received {p.name}"],
    )


@action(reads=["pdf_path", "log"], writes=["doc_key", "phase", "log"])
async def convert(state: State) -> State:
    """Convert the PDF to a DoclingDocument via docling-mcp."""
    result = await call_upstream(
        "docling",
        "convert_pdf_to_docling_document",
        {"source": state["pdf_path"]},
    )
    doc_key = result.get("document_key") if isinstance(result, dict) else None
    if not doc_key:
        raise ValueError(f"docling did not return a document_key; got: {result!r}")
    return state.update(
        doc_key=doc_key,
        phase="converted",
        log=[*state["log"], f"converted -> doc_key={doc_key}"],
    )


@action(reads=["doc_key", "log"], writes=["markdown_preview", "phase", "log"])
async def review(state: State) -> State:
    """Export the converted document to markdown for human or agent review."""
    md = await call_upstream(
        "docling",
        "export_docling_document_to_markdown",
        {"document_key": state["doc_key"]},
    )
    text = md if isinstance(md, str) else str(md)
    return state.update(
        markdown_preview=text[:4000],
        phase="reviewed",
        log=[*state["log"], f"reviewed ({len(text)} chars)"],
    )


@action(reads=["markdown_preview", "log"], writes=["tags", "phase", "log"])
async def tag(state: State, tags: list[str]) -> State:
    """Attach tags to the document. Must run after review."""
    if not isinstance(tags, list) or not tags:
        raise ValueError("tags must be a non-empty list of strings")
    clean = [t.strip() for t in tags if t.strip()]
    if not clean:
        raise ValueError("tags must contain at least one non-empty string")
    return state.update(
        tags=clean,
        phase="tagged",
        log=[*state["log"], f"tagged: {','.join(clean)}"],
    )


@action(reads=["doc_key", "tags", "log"], writes=["saved_path", "phase", "log"])
async def save(state: State) -> State:
    """Persist the document via docling-mcp and finish the pipeline."""
    if not state.get("tags"):
        raise ValueError("save requires tags; call tag(tags=[...]) first")
    result = await call_upstream(
        "docling",
        "save_docling_document",
        {"document_key": state["doc_key"]},
    )
    saved = result.get("filepath") if isinstance(result, dict) else str(result)
    return state.update(
        saved_path=saved,
        phase="saved",
        log=[*state["log"], f"saved -> {saved}"],
    )


_OPEN = Condition.expr("phase != 'saved'")


def build_application():
    return (
        ApplicationBuilder()
        .with_actions(
            receive=receive, convert=convert, review=review, tag=tag, save=save,
        )
        .with_transitions(
            ("receive", "convert", _OPEN),
            ("convert", "review", _OPEN),
            ("review", "tag", _OPEN),
            ("tag", "save", _OPEN),
        )
        .with_state(
            pdf_path=None,
            doc_key=None,
            markdown_preview=None,
            tags=[],
            saved_path=None,
            phase="empty",
            log=[],
        )
        .with_entrypoint("receive")
        .build()
    )


def build_server():
    return mount(
        build_application,
        mode=ServingMode.STEP,
        name="document-pipeline",
        upstream={
            "docling": {
                "command": "uvx",
                "args": ["--from", "docling-mcp", "docling-mcp-server", "--transport", "stdio"],
            }
        },
        instructions=(
            "A phase-gated document-processing FSM that drives docling-mcp "
            "underneath. The walk is receive(pdf_path) -> convert() -> "
            "review() -> tag(tags=[...]) -> save(). docling tools are not "
            "exposed directly; they are called from this server's action "
            "bodies. Read state.markdown_preview after review to decide on "
            "tags. Drop a PDF at the inbox path printed in the log to begin: "
            f"{_DEFAULT_INBOX}"
        ),
    )


if __name__ == "__main__":
    build_server().run()
