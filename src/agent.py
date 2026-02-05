from __future__ import annotations

import os
import re
from typing import List, Optional, Tuple

from analyzer import RunbookAnalyzer


class RunbookAgent:
    """Incident response agent (offline-capable).

    For now this does retrieval using simple keyword matching over built-in
    runbooks. This keeps the agent usable without any API keys or vector DB.
    """

    def __init__(self, runbook_dir: Optional[str] = None):
        self.runbook_dir = runbook_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "runbooks"
        )
        self.analyzer = RunbookAnalyzer()

    def handle_alert(self, alert_text: str) -> str:
        runbook_path = self._find_best_runbook(alert_text)
        if not runbook_path:
            return (
                "I couldn't find a matching runbook for this alert.\n\n"
                "Try running `python cli.py --analyze` to see available runbooks, "
                "or add a new markdown runbook under `runbooks/`."
            )

        content = self._read_text(runbook_path)
        _, body = self.analyzer._parse_frontmatter(content)  # reuse parser
        steps = self._extract_sections(body)

        title = os.path.basename(runbook_path)
        response_lines: List[str] = [
            f"Matched runbook: {title}",
            "",
            "## Diagnosis",
            steps[0] or "No explicit Diagnosis steps found.",
            "",
            "## Remediation",
            steps[1] or "No explicit Remediation steps found.",
            "",
            "## Rollback",
            steps[2] or "No explicit Rollback steps found.",
            "",
            "Safety note: confirm impact/approvals before any destructive action.",
        ]
        return "\n".join(response_lines)

    # -----------------------
    # Retrieval + parsing
    # -----------------------

    def _find_best_runbook(self, alert_text: str) -> Optional[str]:
        if not os.path.isdir(self.runbook_dir):
            return None

        alert_tokens = self._tokens(alert_text)
        best: Tuple[int, Optional[str]] = (0, None)

        for name in os.listdir(self.runbook_dir):
            if not name.lower().endswith(".md"):
                continue
            path = os.path.join(self.runbook_dir, name)
            content = self._read_text(path)
            score = self._keyword_score(alert_tokens, content)
            if score > best[0]:
                best = (score, path)

        return best[1]

    def _keyword_score(self, alert_tokens: List[str], content: str) -> int:
        hay = content.lower()
        return sum(1 for t in alert_tokens if t and t in hay)

    def _tokens(self, text: str) -> List[str]:
        toks = re.findall(r"[a-zA-Z0-9_]+", text.lower())
        # drop very short tokens
        return [t for t in toks if len(t) >= 3]

    def _extract_sections(self, body: str) -> Tuple[str, str, str]:
        def section(name: str) -> str:
            # Grab everything after "## Name" until next "## "
            pattern = re.compile(rf"^\s*##\s+{re.escape(name)}\s*$\n(.*?)(?=^\s*##\s+|\Z)", re.M | re.S)
            m = pattern.search(body)
            return (m.group(1).strip() if m else "")

        return section("Diagnosis"), section("Remediation"), section("Rollback")

    def _read_text(self, path: str) -> str:
        for enc in ("utf-8", "utf-8-sig", "cp1252"):
            try:
                with open(path, "r", encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

