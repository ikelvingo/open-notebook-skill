# 📓 Open Notebook Skill

`#skills` `#open-notebook` `#agent-skill`

Agent skill for managing an [Open Notebook](https://github.com/lfnovo/open-notebook) research knowledge base via its REST API. Designed for **Claude Code / Gemini CLI / Copilot CLI** agent automation.

## Requirements

- Python 3.8+
- An [Open Notebook](https://github.com/lfnovo/open-notebook) instance running

## Setup

```bash
export OPEN_NOTEBOOK_BASE_URL="http://localhost:8000"
export OPEN_NOTEBOOK_API_KEY="your-api-key"  # optional
```

## Quick Start

```bash
# List notebooks
python open_notebook.py notebook list

# Create a notebook
python open_notebook.py notebook create --name "Research"

# Ingest a web page
python open_notebook.py source create --type url --url "https://example.com" --notebook_id notebook:XXX

# Semantic search
python open_notebook.py search query --query "agent architecture" --type vector
```

## CLI Overview

```
notebook   list | get | create | update | delete | preview-delete | add-source | remove-source
source     list | get | create | update | delete | status | retry
note       list | get | create | update | delete
insight    list | get | create | delete | save-as-note
search     query
```

Use `python open_notebook.py --help` for full details.

## Author

ikelvingo — [github.com/ikelvingo/open-notebook-skill](https://github.com/ikelvingo/open-notebook-skill)
