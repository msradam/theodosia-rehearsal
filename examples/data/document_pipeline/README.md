# Document-pipeline inbox

Drop PDFs into this folder, then drive the `rehearsal-document-pipeline`
MCP server with `receive(pdf_path="examples/data/document_pipeline/<your-file>.pdf")`.

The pipeline calls `docling-mcp` via `uvx` to convert, export to markdown,
tag, and save. Output filepaths come from docling's own `save_docling_document`
tool.
