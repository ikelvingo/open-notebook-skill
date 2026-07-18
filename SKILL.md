---
name: open-notebook
en_name: "Open Notebook"
emoji: "📓"
description: "Manage Open Notebook knowledge base — notebooks, sources, notes, insights, search. Structured CLI-backed workflows for agent automation."
author: ikelvingo
github: https://github.com/ikelvingo/open-notebook-skill
category: productivity
tags: ["notebook", "research", "knowledge-base", "search", "insights", "notes"]
---

# Open Notebook Skill

Agent skill for managing an [Open Notebook](https://github.com/lfnovo/open-notebook) research knowledge base via its REST API.

A Python CLI (`open_notebook.py`) wraps every endpoint. **All data operations go through the CLI** — never raw HTTP calls. The CLI guarantees:
- Consistent error handling (always JSON output)
- Stable field mapping (no LLM hallucination on field names)
- Subcommand completion (no URL construction mistakes)

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPEN_NOTEBOOK_BASE_URL` | **Yes** | — | Base URL of the Open Notebook API |
| `OPEN_NOTEBOOK_API_KEY` | No | _(empty)_ | API key (sent as `x-api-key` header) |

**Name collision note:** The prefix `OPEN_NOTEBOOK_` is namespaced to the product itself — no other tool uses this prefix.

---

## CLI Reference

```
python open_notebook.py <resource> <action> [options]
```

### Notebooks

```
notebook list [--archived true|false] [--order_by "updated desc"]
notebook get <notebook_id>
notebook create --name NAME [--description DESC]
notebook update <notebook_id> [--name NAME] [--description DESC] [--archived true|false]
notebook delete <notebook_id> [--delete_exclusive_sources true|false]
notebook preview-delete <notebook_id>
notebook add-source <notebook_id> <source_id>
notebook remove-source <notebook_id> <source_id>
```

### Sources

```
source list [--notebook_id ID] [--limit N] [--offset N] [--sort_by FIELD] [--sort_order asc|desc]
source get <source_id>
source create --type TYPE [--url URL] [--content CONTENT] [--title TITLE] [--notebook_id ID] [--file_path PATH]
source update <source_id> [--title TITLE]
source delete <source_id>
source status <source_id>
source retry <source_id>
```

### Notes

```
note list [--notebook_id ID]
note get <note_id>
note create --title TITLE --content CONTENT [--note_type TYPE] [--notebook_id ID]
note update <note_id> [--title TITLE] [--content CONTENT] [--note_type TYPE]
note delete <note_id>
```

### Insights

```
insight list <source_id>
insight get <insight_id>
insight create <source_id> --transformation_id ID [--model_id ID]
insight delete <insight_id>
insight save-as-note <insight_id> --notebook_id ID
```

### Search

```
search query --query QUERY [--type text|vector] [--limit N] [--search-sources true|false] [--search-notes true|false] [--minimum-score N]
```

---

## Workflows

### 1. Ingest a new source into a notebook

**Goal:** Add a URL or text content to a notebook for processing.

```bash
# Step 1: Create the source and attach to notebook
python open_notebook.py source create --type url --url "https://example.com/article" --title "My Article" --notebook_id notebook:XXX

# Step 2: Poll until processing completes
python open_notebook.py source status <source_id>
# → check "status" field: "completed" | "processing" | "failed"

# Step 3: If failed, retry
python open_notebook.py source retry <source_id>
```

### 2. Generate insights from a source

**Goal:** Run a transformation pipeline on a source to extract structured insights.

```bash
# Step 1: Check what insights already exist
python open_notebook.py insight list <source_id>

# Step 2: Create insight (async — returns immediately)
python open_notebook.py insight create <source_id> --transformation_id transform:XXX

# Step 3: Poll insight list until new insight appears
python open_notebook.py insight list <source_id>

# Step 4: Read the insight
python open_notebook.py insight get <insight_id>

# Step 5 (optional): Convert insight to a note
python open_notebook.py insight save-as-note <insight_id> --notebook_id notebook:XXX
```

### 3. Search and ask the knowledge base

**Goal:** Find relevant content or get AI-generated answers.

```bash
# Full-text search
python open_notebook.py search query --query "agent architecture" --limit 5 --type text

# Vector semantic search
python open_notebook.py search query --query "neural networks" --type vector --limit 10
```

### 4. Curate notes from insights

**Goal:** Convert AI-generated insights into permanent notes.

```bash
# Step 1: List all insights for a source
python open_notebook.py insight list <source_id>

# Step 2: Read specific insight
python open_notebook.py insight get <insight_id>

# Step 3: Save as note in the right notebook
python open_notebook.py insight save-as-note <insight_id> --notebook_id notebook:XXX

# Step 4: Find the new note and update if needed
python open_notebook.py note list --notebook_id notebook:XXX
python open_notebook.py note update <note_id> --content "Refined content..."
```

### 5. Notebook lifecycle

**Goal:** Create → use → archive (or delete) a notebook.

```bash
# Create
python open_notebook.py notebook create --name "Project X" --description "Research on X"

# Update
python open_notebook.py notebook update notebook:XXX --name "Project X v2"

# Archive (soft-delete keeps data)
python open_notebook.py notebook update notebook:XXX --archived true

# Preview what will be deleted
python open_notebook.py notebook preview-delete notebook:XXX

# Delete (with cascade)
python open_notebook.py notebook delete notebook:XXX --delete_exclusive_sources true
```

### 6. Source management across notebooks

**Goal:** Add/remove sources from notebooks (without deleting the source itself).

```bash
# Add existing source to another notebook
python open_notebook.py notebook add-source notebook:YYY <source_id>

# Remove source from a notebook (source itself is preserved)
python open_notebook.py notebook remove-source notebook:YYY <source_id>
```

---

## Output Conventions

- **Success:** JSON object/array with data. Resource IDs are in format `{type}:{ulid}` (e.g., `notebook:mpfijmdb9haubbpljpr7`).
- **Error:** JSON object with `{"error": true, "status": N, "message": "..."}`.
- **Empty body success:** `{"true": true}`.

---

## Error Handling

When the CLI returns `"error": true`:

| Status | Meaning | Action |
|--------|---------|--------|
| `404` | Resource not found | Check the ID exists via `list` or `get` |
| `422` | Validation error | Read `message` for field-level details |
| `500` | Server error | Retry once; if persists, surface to user |
| `0` | Connection refused | Check `OPEN_NOTEBOOK_API_URL` and server status |

---

## ID Formats

| Resource | ID Prefix | Example |
|----------|-----------|---------|
| Notebook | `notebook:` | `notebook:mpfijmdb9haubbpljpr7` |
| Source | `source:` | `source:q3dgc5m1vafwdp4xozkc` |
| Note | `note:` | `note:wnvem2324tu6956dngp9` |
| Insight | `insight:` | `insight:abc123def456` |

---

## Notes for Agent Use

1. **Always use the CLI** — never construct raw HTTP requests. The CLI handles auth, URL encoding, and JSON parsing.
2. **Always parse the `id` field** from `create` list responses — you need it for subsequent operations.
3. **Source processing is async** — after `source create`, poll `source status` until `completed`.
4. **Insight generation is async** — after `insight create`, poll `insight list <source_id>` to see results.
5. **Search types:** Use `text` keyword search, `vector` for semantic similarity. Default is `text`.
6. **Deletion is permanent** — use `notebook preview-delete` before `notebook delete`.
7. **Environment variables** should be set in profile (e.g., `.agent/env` or shell config) so the skill works across sessions without re-configuration.
