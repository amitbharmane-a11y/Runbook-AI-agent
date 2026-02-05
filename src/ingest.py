from __future__ import annotations

import json
import os
from typing import Dict, List


DEFAULT_RUNBOOK_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "runbooks")
DEFAULT_INDEX_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vector_db", "index.json")


def ingest_runbooks(runbook_dir: str = DEFAULT_RUNBOOK_DIR, index_path: str = DEFAULT_INDEX_PATH) -> Dict[str, int]:
    """Lightweight ingestion: builds a simple JSON index of markdown runbooks.

    This keeps the repo runnable without requiring a vector database. If you later
    want embeddings + similarity search, this function is the natural extension
    point.
    """
    if not os.path.isdir(runbook_dir):
        return {"runbooks_indexed": 0}

    runbooks: List[Dict[str, str]] = []
    for name in sorted(os.listdir(runbook_dir)):
        if not name.lower().endswith(".md"):
            continue
        path = os.path.join(runbook_dir, name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        runbooks.append({"filename": name, "path": path, "content": content})

    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump({"runbooks": runbooks}, f, indent=2)

    return {"runbooks_indexed": len(runbooks)}

