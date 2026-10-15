---
name: open-notebook
en_name: "Open Notebook"
emoji: "📓"
description: "Manage Open Notebook knowledge base — notebooks, sources, notes, insights, search. Structured CLI-backed workflows for agent automation."
version: 1.2.0
author: ikelvingo
github: https://github.com/ikelvingo/open-notebook-skill
category: productivity
tags: ["notebook", "research", "knowledge-base", "search", "insights", "notes"]
---

# Open Notebook Skill

Agent skill for managing an [Open Notebook](https://github.com/lfnovo/open-notebook) research knowledge base via its REST API.

A Python CLI (`open_notebook.py`) wraps every endpoint. **All data operations go through the CLI** — never raw HTTP calls. The CLI handles auth, URL encoding, and JSON parsing.

## Environment Variables

- `OPEN_NOTEBOOK_BASE_URL` (**required**) — API base URL
- `OPEN_NOTEBOOK_API_KEY` (optional) — sent as `x-api-key` header

## Command Tree

```
notebook   list | get | create | update | delete | preview-delete | add-source | remove-source
source     list | get | create | update | delete | status | retry | download
note       list | get | create | update | delete
insight    list | get | create | delete | save-as-note
search     query
```

Use `python open_notebook.py --help` or `python open_notebook.py <resource> <action> --help` for full argument details.

## Agent Decision Harness

### 1. Entry point

Every operation starts with `python open_notebook.py <resource> <action>`. If unsure which action to call, run `python open_notebook.py <resource> --help`.

### 2. Resolve notebook references

A notebook reference is either an **id** or a **name**:

- Starts with `notebook:` (e.g. `notebook:abc123`) → use it as an id directly.
- Plain text (e.g. "Research") → it is a **name**, not an id. Resolve it strictly:
  1. `python open_notebook.py notebook list`
  2. Find the entry whose `name` matches **exactly**.
  3. If no exact match exists, ask the user whether to create a new notebook or clarify the name.
  4. Capture the `id` field and use it for the next command.

Never pass a plain notebook name to `--notebook_id`.

### 3. Route by intent

| User intent | Route |
|-------------|-------|
| "create notebook X" | `notebook create --name "X"` |
| "save/add ... to notebook X" | `notebook list` → exact name match → `source create ... --notebook_id <resolved_id>` |
| "save to notebook:id" | `source create ... --notebook_id notebook:id` |

Only create a notebook when the user explicitly says **create**. For save/add intents, always look up the notebook first and then create the source.

## Source Ingestion Rules

When saving content to Open Notebook:

1. **Strip internal reasoning.** Keep only final conclusions, decisions, facts, and user-facing content. Remove reasoning chains and tool-call traces.
2. **Pick the type by content shape; only three exist: `link`, `upload`, `text`.** (`url` and `file` still work as aliases.) The server rejects anything else with 400.
   - `--type text --content "..."` — short plain/markdown content you already have in hand.
   - `--type upload --file_path /abs/path.md` — **any file from disk** (md, pdf, docx, …). This works: the CLI posts multipart to `POST /api/sources`, which is the only endpoint that accepts a file body.
   - `--type link --url "https://..."` — a web page.
3. **Never put multi-line content in `--content`.** Shell escaping turns real newlines into literal `\n`, corrupting formatting. Prefer `--type upload --file_path` for any multi-line markdown.
4. **Always keep `--embed` on (default true).** The server's own default is `embed=false`, which stores the source with `embedded: false, embedded_chunks: 0` — it looks saved and is searchable by keyword, but vector search can never reach it. The CLI defaults this to true; only pass `--embed false` deliberately.
5. **Synthesize discussions into clean Markdown.** Do not dump raw message history.
6. **NEVER write to Open Notebook without explicit user instruction.** Open Notebook is the **user's** knowledge base, not an agent backup. Do not auto-archive conversation summaries, reflection threads, or session artifacts unless the user explicitly says "write to open notebook" / "save this as a source" / "log this in notebook X". General instructions like "remember this discussion" are memory writes, not open-notebook writes. **State what you would write, where, and why, then wait for explicit approval.** (2026-07-18 correction: agent over-eagerly archived a Pi/OMP reflection thread without waiting for approval, and the user pushed back — "未经明确指令不应写入".)

## Core Patterns

### Pattern A: Create → Poll → Use (sources, insights)

Sources and insights are processed asynchronously. Poll until status is `completed` or `failed`:

```bash
python open_notebook.py source create --type link --url "https://example.com" --notebook_id <id>
python open_notebook.py source status <source-id>
# if failed: python open_notebook.py source retry <source-id>

python open_notebook.py insight create <source-id> --transformation_id <transform-id>
python open_notebook.py insight list <source-id>  # poll until new insight appears
python open_notebook.py insight get <insight-id>
python open_notebook.py insight save-as-note <insight-id> --notebook_id <id>
```

Poll every few seconds.

### Pattern B: Search — text vs vector (2026-07-18 correction)

`search query` now **defaults to `vector`**, which is the right default for this corpus. Two things to know:

- **The text search backend does NOT tokenize Chinese** — Chinese keyword queries can return 0 hits even when sources clearly contain the term. Use `--type vector` for any CJK / mixed / uncertain query. (2026-10-16 re-verified: vector search returns CJK sources correctly, top hit `similarity: 0.70`.)
- **Response shape differs by mode.** Both return `results`, but vector results carry `matches` + `similarity`; text results carry `relevance` + `total_count` + `search_type`. Read `results`, not `items`.

```bash
# Vector semantic search (default; use for Chinese / mixed / uncertain)
python open_notebook.py search query --query "agent architecture" --type vector --limit 10

# Text keyword search (English-only, fast, exact match)
python open_notebook.py search query --query "API error" --type text --limit 10

# Verify a corpus before declaring search "broken":
python open_notebook.py search query --query "Pi OMP" --type text --limit 5 | python3 -c \
  "import json,sys; d=json.load(sys.stdin); print('total:', d.get('total_count'), 'search_type:', d.get('search_type'))"
```

**Heuristic**: when the query contains any CJK characters, **always pass `--type vector`** explicitly. When a notebook has very few sources (< 50), 0-hit may simply mean the corpus is sparse — not a search bug. Don't diagnose "search broken" until you've seeded enough sources to disambiguate corpus-empty from search-broken.

**Verification recipe before declaring search broken**:

1. Run a pure-English `--type text` query that should obviously match (e.g. a known source's title) — if it hits, vector pipeline is OK
2. Run the same query as `--type vector` — confirms vector pipeline
3. Inspect `embedded_chunks` on a recent source via `source get <id>` — `0` means the source was stored without embeddings, so vector search **cannot** reach it. Pass `--embed true` (CLI default) when creating it.
4. Only after these three steps → declare actual broken

### Pattern C: Real file ingestion

```bash
python open_notebook.py source create --type upload \
  --file_path /opt/data/cache/scratch/2026-10-16-title.md \
  --title "2026-10-16-title" --notebook_id <id>

# retrieve the original file back
python open_notebook.py source download <source-id> --out ./roundtrip.md
```

Verified round-trip on 2026-10-16: CJK content uploads byte-identical and downloads byte-identical.

### CRUD

Standard `list | get | create | update | delete` for notebooks, sources, and notes. Always capture the `id` field from `create`/`list` responses for subsequent operations.

## Output Format

- **Success:** JSON object/array with data. Resource IDs use format `{type}:{ulid}`.
- **Empty body success:** `{"success": true}`.
- **Error:** `{"error": true, "status": N, "message": "..."}`.

## Error Handling

| Status | Meaning | Action |
|--------|---------|--------|
| `0` | Connection refused | Verify `OPEN_NOTEBOOK_BASE_URL` and server status |
| `404` | Not found | Check the resource exists via `list` or `get` |
| `422` | Validation error | Read `message` field for details |
| `500` | Server error | Retry once; if persists, notify user |

## Reminders

- **Capture `id`** from `create` and `list` responses; all subsequent operations need it.
- **Check before delete.** Use `notebook preview-delete` to see cascading impact before `notebook delete`.
