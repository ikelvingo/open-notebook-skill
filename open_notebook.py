#!/usr/bin/env python3
"""
Open Notebook API CLI
=====================
Hermes/agent skill for managing notebooks, sources, notes, insights, and search.

Environment variables:
  OPEN_NOTEBOOK_BASE_URL - Base URL of the Open Notebook API (required)
  OPEN_NOTEBOOK_API_KEY  - Optional API key (sent as x-api-key header)

All commands output JSON to stdout for reliable agent parsing.
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

BASE_URL = os.environ.get("OPEN_NOTEBOOK_BASE_URL", "")
API_KEY = os.environ.get("OPEN_NOTEBOOK_API_KEY", "")


def api_request(method, path, body=None, params=None):
    """Make an API request and return parsed JSON."""
    url = urllib.parse.urljoin(BASE_URL, path)
    if params:
        qs = urllib.parse.urlencode(params)
        url += "?" + qs

    data = None
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["x-api-key"] = API_KEY

    if body is not None:
        data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            if not raw.strip():
                return {"success": True}
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        error_body = ""
        try:
            error_body = e.read().decode("utf-8")
        except:
            pass
        return {"error": True, "status": e.code, "message": error_body}
    except urllib.error.URLError as e:
        return {"error": True, "status": 0, "message": str(e.reason)}
    except Exception as e:
        return {"error": True, "status": 0, "message": str(e)}


def output(data):
    """Print JSON to stdout."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def bool_arg(val):
    """Parse boolean string."""
    if val.lower() in ("true", "1", "yes"):
        return True
    if val.lower() in ("false", "0", "no"):
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {val!r}")


# ─── NOTEBOOKS ────────────────────────────────────────────────────────────────

def notebook_list(args):
    params = {}
    if args.archived is not None:
        params["archived"] = str(args.archived).lower()
    if args.order_by:
        params["order_by"] = args.order_by
    output(api_request("GET", "/api/notebooks", params=params))


def notebook_get(args):
    output(api_request("GET", f"/api/notebooks/{args.notebook_id}"))


def notebook_create(args):
    body = {"name": args.name}
    if args.description:
        body["description"] = args.description
    output(api_request("POST", "/api/notebooks", body=body))


def notebook_update(args):
    body = {}
    if args.name is not None:
        body["name"] = args.name
    if args.description is not None:
        body["description"] = args.description
    if args.archived is not None:
        body["archived"] = args.archived
    output(api_request("PUT", f"/api/notebooks/{args.notebook_id}", body=body))


def notebook_delete(args):
    params = {}
    if args.delete_exclusive_sources is not None:
        params["delete_exclusive_sources"] = str(args.delete_exclusive_sources).lower()
    output(api_request("DELETE", f"/api/notebooks/{args.notebook_id}", params=params))


def notebook_preview(args):
    output(api_request("GET", f"/api/notebooks/{args.notebook_id}/delete-preview"))


def notebook_add_source(args):
    output(api_request("POST", f"/api/notebooks/{args.notebook_id}/sources/{args.source_id}"))


def notebook_remove_source(args):
    output(api_request("DELETE", f"/api/notebooks/{args.notebook_id}/sources/{args.source_id}"))


# ─── SOURCES ──────────────────────────────────────────────────────────────────

def source_list(args):
    params = {}
    if args.notebook_id:
        params["notebook_id"] = args.notebook_id
    if args.limit:
        params["limit"] = args.limit
    if args.offset is not None:
        params["offset"] = args.offset
    if args.sort_by:
        params["sort_by"] = args.sort_by
    if args.sort_order:
        params["sort_order"] = args.sort_order
    output(api_request("GET", "/api/sources", params=params))


def source_get(args):
    output(api_request("GET", f"/api/sources/{args.source_id}"))


def source_create(args):
    body = {"type": args.type}
    if args.url:
        body["url"] = args.url
    if args.content:
        body["content"] = args.content
    if args.title:
        body["title"] = args.title
    if args.notebook_id:
        body["notebook_id"] = args.notebook_id
    if args.file_path:
        body["file_path"] = args.file_path
    output(api_request("POST", "/api/sources/json", body=body))


def source_update(args):
    body = {}
    if args.title is not None:
        body["title"] = args.title
    output(api_request("PUT", f"/api/sources/{args.source_id}", body=body))


def source_delete(args):
    output(api_request("DELETE", f"/api/sources/{args.source_id}"))


def source_status(args):
    output(api_request("GET", f"/api/sources/{args.source_id}/status"))


def source_retry(args):
    output(api_request("POST", f"/api/sources/{args.source_id}/retry"))


# ─── NOTES ────────────────────────────────────────────────────────────────────

def note_list(args):
    params = {}
    if args.notebook_id:
        params["notebook_id"] = args.notebook_id
    output(api_request("GET", "/api/notes", params=params))


def note_get(args):
    output(api_request("GET", f"/api/notes/{args.note_id}"))


def note_create(args):
    body = {"title": args.title, "content": args.content}
    if args.note_type:
        body["note_type"] = args.note_type
    if args.notebook_id:
        body["notebook_id"] = args.notebook_id
    output(api_request("POST", "/api/notes", body=body))


def note_update(args):
    body = {}
    if args.title is not None:
        body["title"] = args.title
    if args.content is not None:
        body["content"] = args.content
    if args.note_type is not None:
        body["note_type"] = args.note_type
    output(api_request("PUT", f"/api/notes/{args.note_id}", body=body))


def note_delete(args):
    output(api_request("DELETE", f"/api/notes/{args.note_id}"))


# ─── INSIGHTS ─────────────────────────────────────────────────────────────────

def insight_list(args):
    output(api_request("GET", f"/api/sources/{args.source_id}/insights"))


def insight_get(args):
    output(api_request("GET", f"/api/insights/{args.insight_id}"))


def insight_create(args):
    body = {"transformation_id": args.transformation_id}
    if args.model_id:
        body["model_id"] = args.model_id
    output(api_request("POST", f"/api/sources/{args.source_id}/insights", body=body))


def insight_delete(args):
    output(api_request("DELETE", f"/api/insights/{args.insight_id}"))


def insight_save_as_note(args):
    body = {"notebook_id": args.notebook_id}
    output(api_request("POST", f"/api/insights/{args.insight_id}/save-as-note", body=body))


# ─── SEARCH ───────────────────────────────────────────────────────────────────

def search_query(args):
    body = {"query": args.query}
    if args.type:
        body["type"] = args.type
    if args.limit:
        body["limit"] = args.limit
    if args.search_sources is not None:
        body["search_sources"] = args.search_sources
    if args.search_notes is not None:
        body["search_notes"] = args.search_notes
    if args.minimum_score is not None:
        body["minimum_score"] = args.minimum_score
    output(api_request("POST", "/api/search", body=body))


# ─── PARSER ───────────────────────────────────────────────────────────────────

def main():
    if not BASE_URL:
        print(json.dumps({"error": True, "status": 0, "message": "OPEN_NOTEBOOK_BASE_URL env var is not set"}))
        sys.exit(1)
    parser = argparse.ArgumentParser(
        description="Open Notebook API CLI — manage notebooks, sources, notes, insights, search"
    )
    parser.set_defaults(func=lambda _: parser.print_help())

    sub = parser.add_subparsers(dest="resource")

    # ── notebooks ──
    nb = sub.add_parser("notebook", help="Manage notebooks")
    nb_sub = nb.add_subparsers(dest="action")

    p = nb_sub.add_parser("list", help="List notebooks")
    p.add_argument("--archived", type=bool_arg, default=None, help="Filter by archived status")
    p.add_argument("--order_by", default=None, help="Sort order (default: 'updated desc')")
    p.set_defaults(func=notebook_list)

    p = nb_sub.add_parser("get", help="Get a notebook")
    p.add_argument("notebook_id", help="Notebook ID")
    p.set_defaults(func=notebook_get)

    p = nb_sub.add_parser("create", help="Create a notebook")
    p.add_argument("--name", required=True, help="Notebook name")
    p.add_argument("--description", default=None, help="Notebook description")
    p.set_defaults(func=notebook_create)

    p = nb_sub.add_parser("update", help="Update a notebook")
    p.add_argument("notebook_id", help="Notebook ID")
    p.add_argument("--name", default=None, help="New name")
    p.add_argument("--description", default=None, help="New description")
    p.add_argument("--archived", type=bool_arg, default=None, help="Archive status")
    p.set_defaults(func=notebook_update)

    p = nb_sub.add_parser("delete", help="Delete a notebook")
    p.add_argument("notebook_id", help="Notebook ID")
    p.add_argument("--delete_exclusive_sources", type=bool_arg, default=False,
                   help="Also delete exclusive sources")
    p.set_defaults(func=notebook_delete)

    p = nb_sub.add_parser("preview-delete", help="Preview notebook deletion")
    p.add_argument("notebook_id", help="Notebook ID")
    p.set_defaults(func=notebook_preview)

    p = nb_sub.add_parser("add-source", help="Add source to notebook")
    p.add_argument("notebook_id", help="Notebook ID")
    p.add_argument("source_id", help="Source ID")
    p.set_defaults(func=notebook_add_source)

    p = nb_sub.add_parser("remove-source", help="Remove source from notebook")
    p.add_argument("notebook_id", help="Notebook ID")
    p.add_argument("source_id", help="Source ID")
    p.set_defaults(func=notebook_remove_source)

    # ── sources ──
    src = sub.add_parser("source", help="Manage sources")
    src_sub = src.add_subparsers(dest="action")

    p = src_sub.add_parser("list", help="List sources")
    p.add_argument("--notebook_id", default=None, help="Filter by notebook")
    p.add_argument("--limit", type=int, default=None, help="Page size")
    p.add_argument("--offset", type=int, default=None, help="Offset")
    p.add_argument("--sort_by", default=None, help="Sort field")
    p.add_argument("--sort_order", default=None, help="asc or desc")
    p.set_defaults(func=source_list)

    p = src_sub.add_parser("get", help="Get a source")
    p.add_argument("source_id", help="Source ID")
    p.set_defaults(func=source_get)

    p = src_sub.add_parser("create", help="Create a source")
    p.add_argument("--type", required=True, help="Source type (url, file, text)")
    p.add_argument("--url", default=None, help="URL for url-type sources")
    p.add_argument("--content", default=None, help="Content for text-type sources")
    p.add_argument("--title", default=None, help="Source title")
    p.add_argument("--notebook_id", default=None, help="Attach to notebook")
    p.add_argument("--file_path", default=None, help="Local file path")
    p.set_defaults(func=source_create)

    p = src_sub.add_parser("update", help="Update a source")
    p.add_argument("source_id", help="Source ID")
    p.add_argument("--title", default=None, help="New title")
    p.set_defaults(func=source_update)

    p = src_sub.add_parser("delete", help="Delete a source")
    p.add_argument("source_id", help="Source ID")
    p.set_defaults(func=source_delete)

    p = src_sub.add_parser("status", help="Get source processing status")
    p.add_argument("source_id", help="Source ID")
    p.set_defaults(func=source_status)

    p = src_sub.add_parser("retry", help="Retry source processing")
    p.add_argument("source_id", help="Source ID")
    p.set_defaults(func=source_retry)

    # ── notes ──
    nt = sub.add_parser("note", help="Manage notes")
    nt_sub = nt.add_subparsers(dest="action")

    p = nt_sub.add_parser("list", help="List notes")
    p.add_argument("--notebook_id", default=None, help="Filter by notebook")
    p.set_defaults(func=note_list)

    p = nt_sub.add_parser("get", help="Get a note")
    p.add_argument("note_id", help="Note ID")
    p.set_defaults(func=note_get)

    p = nt_sub.add_parser("create", help="Create a note")
    p.add_argument("--title", required=True, help="Note title")
    p.add_argument("--content", required=True, help="Note content")
    p.add_argument("--note_type", default=None, help="Note type")
    p.add_argument("--notebook_id", default=None, help="Attach to notebook")
    p.set_defaults(func=note_create)

    p = nt_sub.add_parser("update", help="Update a note")
    p.add_argument("note_id", help="Note ID")
    p.add_argument("--title", default=None, help="New title")
    p.add_argument("--content", default=None, help="New content")
    p.add_argument("--note_type", default=None, help="New note type")
    p.set_defaults(func=note_update)

    p = nt_sub.add_parser("delete", help="Delete a note")
    p.add_argument("note_id", help="Note ID")
    p.set_defaults(func=note_delete)

    # ── insights ──
    ins = sub.add_parser("insight", help="Manage insights")
    ins_sub = ins.add_subparsers(dest="action")

    p = ins_sub.add_parser("list", help="List insights for a source")
    p.add_argument("source_id", help="Source ID")
    p.set_defaults(func=insight_list)

    p = ins_sub.add_parser("get", help="Get an insight")
    p.add_argument("insight_id", help="Insight ID")
    p.set_defaults(func=insight_get)

    p = ins_sub.add_parser("create", help="Generate insight for a source")
    p.add_argument("source_id", help="Source ID")
    p.add_argument("--transformation_id", required=True, help="Transformation pipeline ID")
    p.add_argument("--model_id", default=None, help="Model override")
    p.set_defaults(func=insight_create)

    p = ins_sub.add_parser("delete", help="Delete an insight")
    p.add_argument("insight_id", help="Insight ID")
    p.set_defaults(func=insight_delete)

    p = ins_sub.add_parser("save-as-note", help="Convert insight to note")
    p.add_argument("insight_id", help="Insight ID")
    p.add_argument("--notebook_id", required=True, help="Target notebook ID")
    p.set_defaults(func=insight_save_as_note)

    # ── search ──
    srch = sub.add_parser("search", help="Search knowledge base")
    srch_sub = srch.add_subparsers(dest="action")

    p = srch_sub.add_parser("query", help="Text search or vector semantic search (vector recommended)")
    p.add_argument("--query", required=True, help="Search query")
    p.add_argument("--type", default="vector", help="Search type: vector (recommended) or text")
    p.add_argument("--limit", type=int, default=10, help="Max results")
    p.add_argument("--search-sources", type=bool_arg, default=True, help="Search sources")
    p.add_argument("--search-notes", type=bool_arg, default=True, help="Search notes")
    p.add_argument("--minimum-score", type=float, default=None, help="Min relevance score")
    p.set_defaults(func=search_query)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
