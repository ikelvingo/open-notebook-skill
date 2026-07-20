---
name: open-notebook
en_name: "Open Notebook"
emoji: "📓"
description: "Manage Open Notebook knowledge base — notebooks, sources, notes, insights, search. Structured CLI-backed workflows for agent automation."
version: 1.1.2
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
source     list | get | create | update | delete | status | retry
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
2. **Prefer `file` over `text`.** Use `text` only for short single-line plain text. For markdown, code, tables, or any multi-line content, write to a temporary `.md` file in the workspace and use `--type file --file_path <path>`. Clean up the temp file after the source is created.
3. **Never put multi-line content in `--content`.** Shell escaping turns real newlines into literal `\n`, corrupting formatting.
4. **Synthesize discussions into clean Markdown.** Do not dump raw message history.

## Core Patterns

### Pattern A: Create → Poll → Use (sources, insights)

Sources and insights are processed asynchronously. Poll until status is `completed` or `failed`:

```bash
python open_notebook.py source create --type url --url "https://example.com" --notebook_id <id>
python open_notebook.py source status <source-id>
# if failed: python open_notebook.py source retry <source-id>

python open_notebook.py insight create <source-id> --transformation_id <transform-id>
python open_notebook.py insight list <source-id>  # poll until new insight appears
python open_notebook.py insight get <insight-id>
python open_notebook.py insight save-as-note <insight-id> --notebook_id <id>
```

Poll every few seconds.

### Pattern B: Search

Search supports two modes: **vector** (semantic, strongly recommended) and **text** (keyword). Default is vector.

```bash
# Vector semantic search (recommended)
python open_notebook.py search query --query "agent architecture" --limit 10

# Text keyword search
python open_notebook.py search query --query "API error" --type text --limit 10
```

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
