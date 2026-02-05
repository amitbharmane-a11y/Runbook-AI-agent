from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional

from analyzer import RunbookAnalyzer
from agent import RunbookAgent


class RunbookChatbot:
    """Multi-modal chatbot wrapper used by the Streamlit UI.

    This version works fully offline:
    - Analysis mode: heuristic scoring via RunbookAnalyzer
    - Incident mode: keyword-based runbook matching via RunbookAgent
    - General mode: usage guidance
    """

    def __init__(self, runbook_dir: Optional[str] = None):
        self.runbook_dir = runbook_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "runbooks"
        )
        self.analyzer = RunbookAnalyzer()
        self.agent = RunbookAgent(self.runbook_dir)
        self._history: List[Dict[str, str]] = []

    def reset_conversation(self) -> None:
        self._history = []

    def process_message(self, message: str, uploaded_documents: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        uploaded_documents = uploaded_documents or []
        mode = self._detect_mode(message)
        self._history.append({"role": "user", "content": message})

        if mode == "analysis":
            response, analysis_data = self._analysis_response(message, uploaded_documents)
            self._history.append({"role": "assistant", "content": response})
            return {"response": response, "mode": mode, "analysis_data": analysis_data}

        if mode == "incident":
            response = self.agent.handle_alert(message)
            self._history.append({"role": "assistant", "content": response})
            return {"response": response, "mode": mode}

        response = self._general_response()
        self._history.append({"role": "assistant", "content": response})
        return {"response": response, "mode": "general"}

    # -----------------------
    # Mode handlers
    # -----------------------

    def _analysis_response(
        self, message: str, uploaded_documents: List[Dict[str, Any]]
    ) -> (str, Dict[str, Any]):
        analyses = []

        # Prefer uploaded markdown/text docs as ad-hoc runbooks
        for doc in uploaded_documents:
            name = doc.get("name", "uploaded")
            content = doc.get("content", "")
            if not content.strip():
                continue
            # Write to a temp file for the analyzer (keeps API stable)
            tmp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads_tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            tmp_path = os.path.join(tmp_dir, f"{name}.md")
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
            analyses.append(self.analyzer.analyze_runbook(tmp_path))

        # If no uploaded docs, analyze all built-ins
        if not analyses:
            analyses = self.analyzer.analyze_all_runbooks(self.runbook_dir)

        summary = self.analyzer.get_health_summary(analyses)

        lines = [
            "Runbook health analysis:",
            f"- Overall health: {summary['overall_health']:.1f}%",
            f"- Completeness: {summary['average_completeness']:.1f}%",
            f"- Structure: {summary['average_structure']:.1f}%",
            f"- Safety: {summary['average_safety']:.1f}%",
            f"- Clarity: {summary['average_clarity']:.1f}%",
            "",
        ]

        if analyses:
            top = analyses[0]
            lines += [
                f"Example: `{top.filename}` scored {top.overall_score:.1f}%.",
            ]
            if top.issues:
                lines.append("Top issues:")
                for issue in top.issues[:3]:
                    lines.append(f"- {issue}")
            if top.recommendations:
                lines.append("Top recommendations:")
                for rec in top.recommendations[:3]:
                    lines.append(f"- {rec}")

        analysis_data = {"analyses": analyses, "health_summary": summary}
        return "\n".join(lines), analysis_data

    def _general_response(self) -> str:
        return (
            "I can help with:\n"
            "- Runbook analysis (ask: 'analyze my runbook' or click Analyze All Runbooks)\n"
            "- Incident response (describe an alert, e.g. 'Database latency high')\n"
            "- General guidance on using the tool\n\n"
            "Try: `python cli.py --analyze` or launch the UI: `python cli.py --web`."
        )

    # -----------------------
    # Mode detection
    # -----------------------

    def _detect_mode(self, message: str) -> str:
        m = message.lower()
        if re.search(r"\b(analyz|health|score|review|assess|improv|recommend)\b", m):
            return "analysis"
        if re.search(r"\b(incident|alert|error|failure|latency|timeout|crash|outage)\b", m):
            return "incident"
        return "general"

