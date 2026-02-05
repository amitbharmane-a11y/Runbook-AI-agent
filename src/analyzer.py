from __future__ import annotations

from dataclasses import dataclass, field
import os
import re
from typing import Dict, List, Optional, Tuple


@dataclass
class RunbookAnalysis:
    filename: str
    overall_score: float
    completeness_score: float
    structure_score: float
    safety_score: float
    clarity_score: float
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)


class RunbookAnalyzer:
    """Offline runbook analyzer and health scorer.

    This intentionally avoids heavyweight ML dependencies so the project can run
    out-of-the-box. Scoring is heuristic-based and aligned with the README's
    criteria (completeness/structure/safety/clarity).
    """

    REQUIRED_SECTIONS = ("diagnosis", "remediation", "rollback")
    REQUIRED_METADATA_KEYS = ("title", "version", "service_owner", "severity", "trigger_criteria")

    _H2_RE = re.compile(r"^\s*##\s+(.+?)\s*$", re.MULTILINE)
    _YAML_FRONTMATTER_RE = re.compile(r"^\s*---\s*\n(.*?)\n---\s*\n", re.DOTALL)

    def analyze_runbook(self, runbook_path: str) -> RunbookAnalysis:
        if not os.path.exists(runbook_path):
            raise FileNotFoundError(runbook_path)

        content = self._read_text(runbook_path)
        metadata, body = self._parse_frontmatter(content)
        headings = [h.strip().lower() for h in self._H2_RE.findall(body)]

        completeness, completeness_issues, completeness_recs = self._score_completeness(
            metadata, body, headings
        )
        structure, structure_issues, structure_recs = self._score_structure(metadata, body, headings)
        safety, safety_issues, safety_recs = self._score_safety(body, headings)
        clarity, clarity_issues, clarity_recs = self._score_clarity(body)

        issues = [*completeness_issues, *structure_issues, *safety_issues, *clarity_issues]
        recommendations = [*completeness_recs, *structure_recs, *safety_recs, *clarity_recs]

        overall = (completeness + structure + safety + clarity) / 4.0

        return RunbookAnalysis(
            filename=os.path.basename(runbook_path),
            overall_score=overall,
            completeness_score=completeness,
            structure_score=structure,
            safety_score=safety,
            clarity_score=clarity,
            issues=issues,
            recommendations=recommendations,
            metadata=metadata,
        )

    def analyze_all_runbooks(self, runbook_dir: str) -> List[RunbookAnalysis]:
        if not os.path.isdir(runbook_dir):
            return []
        analyses: List[RunbookAnalysis] = []
        for name in sorted(os.listdir(runbook_dir)):
            if not name.lower().endswith(".md"):
                continue
            path = os.path.join(runbook_dir, name)
            try:
                analyses.append(self.analyze_runbook(path))
            except Exception:
                # Keep batch analysis resilient: skip bad files.
                continue
        return analyses

    def get_health_summary(self, analyses: List[RunbookAnalysis]) -> Dict[str, float]:
        if not analyses:
            return {
                "overall_health": 0.0,
                "average_completeness": 0.0,
                "average_structure": 0.0,
                "average_safety": 0.0,
                "average_clarity": 0.0,
            }

        def avg(values: List[float]) -> float:
            return sum(values) / len(values)

        return {
            "overall_health": avg([a.overall_score for a in analyses]),
            "average_completeness": avg([a.completeness_score for a in analyses]),
            "average_structure": avg([a.structure_score for a in analyses]),
            "average_safety": avg([a.safety_score for a in analyses]),
            "average_clarity": avg([a.clarity_score for a in analyses]),
        }

    # -----------------------
    # Scoring helpers
    # -----------------------

    def _score_completeness(
        self, metadata: Dict[str, str], body: str, headings: List[str]
    ) -> Tuple[float, List[str], List[str]]:
        issues: List[str] = []
        recs: List[str] = []
        score = 0.0

        # Trigger criteria (metadata or text)
        if metadata.get("trigger_criteria") or re.search(r"trigger\s*criteria", body, re.I):
            score += 25.0
        else:
            issues.append("Missing trigger criteria (when to use this runbook).")
            recs.append("Add `trigger_criteria` in frontmatter and describe clear activation conditions.")

        # Required sections
        section_points = 25.0
        present = {s: (s in headings) for s in self.REQUIRED_SECTIONS}
        if all(present.values()):
            score += 25.0
        else:
            missing = [s.title() for s, ok in present.items() if not ok]
            issues.append(f"Missing required sections: {', '.join(missing)}.")
            recs.append("Add the missing required sections: Diagnosis, Remediation, Rollback.")

        # Validation steps
        if re.search(r"\b(validate|verification|verify|confirm|check)\b", body, re.I):
            score += 25.0
        else:
            issues.append("No explicit validation/verification steps found.")
            recs.append("Add a 'Validation' step after remediation to confirm the issue is resolved.")

        # Escalation contacts / owner
        if metadata.get("service_owner") or re.search(r"\b(escalat|on[- ]call|owner|contact)\b", body, re.I):
            score += 25.0
        else:
            issues.append("No service owner / escalation contact found.")
            recs.append("Add `service_owner` in frontmatter and escalation/on-call contact info.")

        return score, issues, recs

    def _score_structure(
        self, metadata: Dict[str, str], body: str, headings: List[str]
    ) -> Tuple[float, List[str], List[str]]:
        issues: List[str] = []
        recs: List[str] = []
        score = 0.0

        # Frontmatter presence and required keys
        if metadata:
            score += 40.0
            missing_keys = [k for k in self.REQUIRED_METADATA_KEYS if not metadata.get(k)]
            if missing_keys:
                issues.append(f"Frontmatter is missing keys: {', '.join(missing_keys)}.")
                recs.append("Add missing required frontmatter keys (title, version, service_owner, severity, trigger_criteria).")
                score -= min(40.0, 8.0 * len(missing_keys))
        else:
            issues.append("Missing YAML frontmatter metadata block.")
            recs.append("Add a YAML frontmatter block (`--- ... ---`) with runbook metadata.")

        # Heading structure
        if headings:
            score += 30.0
        else:
            issues.append("No H2 sections (##) detected; runbook may be poorly structured.")
            recs.append("Use consistent headings like '## Diagnosis', '## Remediation', and '## Rollback'.")

        # Version and ownership are explicitly highlighted in README
        if metadata.get("version"):
            score += 15.0
        else:
            issues.append("No version found in metadata.")
            recs.append("Add a `version` field in frontmatter for runbook change control.")

        if metadata.get("service_owner"):
            score += 15.0
        else:
            issues.append("No service owner found in metadata.")
            recs.append("Add `service_owner` in frontmatter.")

        return min(100.0, score), issues, recs

    def _score_safety(self, body: str, headings: List[str]) -> Tuple[float, List[str], List[str]]:
        issues: List[str] = []
        recs: List[str] = []
        score = 100.0

        destructive_patterns = [
            r"\brm\s+-rf\b",
            r"\b(drop\s+database|drop\s+table)\b",
            r"\b(delete\s+from)\b",
            r"\b(kill\s+-9)\b",
            r"\bshutdown\b",
            r"\breboot\b",
        ]
        destructive_found = any(re.search(p, body, re.I) for p in destructive_patterns)
        if destructive_found:
            if not re.search(r"\b(confirm|are you sure|double[- ]check|approval)\b", body, re.I):
                score -= 35.0
                issues.append("Potentially destructive actions detected without an explicit confirmation/approval step.")
                recs.append("Add a confirmation/approval step before any destructive command.")

        if "rollback" not in headings:
            score -= 40.0
            issues.append("No rollback section found (required for safe operations).")
            recs.append("Add a Rollback section with clear recovery steps.")

        if not re.search(r"\b(safety|warning|caution)\b", body, re.I):
            score -= 15.0
            issues.append("No safety warnings/cautions found.")
            recs.append("Add a short 'Safety' note (permissions, impact, maintenance window, backups).")

        return max(0.0, min(100.0, score)), issues, recs

    def _score_clarity(self, body: str) -> Tuple[float, List[str], List[str]]:
        issues: List[str] = []
        recs: List[str] = []

        lines = [ln.rstrip("\n") for ln in body.splitlines()]
        non_empty = [ln for ln in lines if ln.strip()]
        if not non_empty:
            return 0.0, ["Runbook content is empty."], ["Add clear, step-by-step runbook content."]

        # Step presence: numbered lists or bullet lists
        has_steps = any(re.match(r"^\s*(\d+\.|\-|\*)\s+", ln) for ln in non_empty)
        # Code fences: improve clarity for commands
        has_code_fences = "```" in body
        # Overlong lines can reduce readability
        long_lines = [ln for ln in non_empty if len(ln) > 140]

        score = 0.0
        score += 45.0 if has_steps else 20.0
        score += 30.0 if has_code_fences else 15.0
        score += 25.0 if len(long_lines) <= max(3, len(non_empty) // 10) else 10.0

        if not has_steps:
            issues.append("No step-by-step list detected (harder to follow during incidents).")
            recs.append("Use numbered steps for Diagnosis/Remediation/Rollback procedures.")
        if not has_code_fences:
            issues.append("No fenced code blocks found for commands.")
            recs.append("Wrap commands in fenced code blocks (```bash ... ```).")
        if long_lines:
            issues.append("Runbook contains very long lines that may reduce readability.")
            recs.append("Wrap long lines and keep steps concise (aim for <140 chars per line).")

        return min(100.0, score), issues, recs

    # -----------------------
    # Parsing helpers
    # -----------------------

    def _read_text(self, path: str) -> str:
        # Most runbooks will be UTF-8; fall back to Windows-1252 if needed.
        for enc in ("utf-8", "utf-8-sig", "cp1252"):
            try:
                with open(path, "r", encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    def _parse_frontmatter(self, content: str) -> Tuple[Dict[str, str], str]:
        m = self._YAML_FRONTMATTER_RE.match(content)
        if not m:
            return {}, content
        raw = m.group(1)
        body = content[m.end() :]
        metadata = self._parse_yaml_kv(raw)
        return metadata, body

    def _parse_yaml_kv(self, raw: str) -> Dict[str, str]:
        # Minimal YAML key:value parser (no nested structures)
        meta: Dict[str, str] = {}
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                continue
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
        return meta

