---
name: open-notebook
en_name: "Open Notebook"
emoji: "📓"
description: "Manage Open Notebook knowledge base — notebooks, sources, notes, insights, search. Structured CLI-backed workflows for agent automation."
version: 1.0.0
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

## Core Patterns

### Pattern A: Create → Poll → Use (sources, insights)

Sources and insights are processed asynchronously. After creation, poll until ready:

```bash
python open_notebook.py source create --type url --url "https://example.com" --notebook_id <id>
python open_notebook.py source status <source-id>
# if failed → python open_notebook.py source retry <source-id>

python open_notebook.py insight create <source-id> --transformation_id <transform-id>
python open_notebook.py insight list <source-id>       # poll until new insight appears
python open_notebook.py insight get <insight-id>
python open_notebook.py insight save-as-note <insight-id> --notebook_id <id>
```

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

## Agent Rules

1. **Always use the CLI.** The CLI guarantees stable field names and auth.
2. **Always capture `id`** from `create` and `list` responses. It is needed for all subsequent operations.
3. **Poll async operations.** `source create` → `source status`; `insight create` → `insight list`. Do not assume instant completion.
4. **Check before delete.** Use `notebook preview-delete` to see cascading impact before `notebook delete`.
5. **Set env vars in profile** (`.agent/env` or shell config) for cross-session persistence.
