# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Fail when the agent escalates after finding only over-limit mood matches."""

from __future__ import annotations

import json
import re
from typing import Any

from kitaru.api_models.v1.evaluation import EvaluationResult
from kitaru.api_models.v1.session_node import NodeType
from kitaru.task.evaluator import SessionView


def _as_dict(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def _tool_payload(node: Any) -> dict[str, Any] | None:
    outputs = _as_dict(node.outputs)
    if outputs is None:
        return None
    if outputs.get("kind") == "tool_message":
        payload = _as_dict(outputs.get("payload")) or {}
        content = payload.get("content")
        return _as_dict(content) or payload
    return outputs


def _max_scare_level(session: SessionView) -> int | None:
    inputs = session.session.inputs
    text = ""
    if isinstance(inputs, dict):
        messages = inputs.get("messages")
        if isinstance(messages, list) and messages:
            first = messages[0]
            if isinstance(first, dict):
                text = str(first.get("content") or "")
            else:
                text = str(getattr(first, "content", "") or "")
        else:
            text = json.dumps(inputs)
    else:
        text = str(inputs or "")
    match = re.search(r"max_scare_level:\s*(\d+)", text)
    return int(match.group(1)) if match else None


def evaluate(session: SessionView) -> EvaluationResult:
    """Prefer within-limit recommendations over escalate-after-over-limit-search."""
    max_level = _max_scare_level(session)
    if max_level is None:
        return EvaluationResult(
            name="prefer_safe_pick",
            value="unknown",
            passed=None,
            explanation="Could not read max_scare_level from the session input.",
        )

    tool_nodes = [n for n in session.nodes if n.node_type is NodeType.TOOL_CALL]
    searched_titles: list[dict[str, Any]] = []
    escalated = False
    recommended: dict[str, Any] | None = None

    for node in tool_nodes:
        payload = _tool_payload(node) or {}
        name = node.tool_name
        if name == "search_catalog" and isinstance(payload.get("titles"), list):
            for title in payload["titles"]:
                if isinstance(title, dict):
                    searched_titles.append(title)
        elif name == "escalate_to_human" and payload.get("accepted") is True:
            escalated = True
        elif name == "recommend" and payload.get("accepted") is True:
            recommended = payload

    if recommended is not None:
        scare = recommended.get("scare_level")
        try:
            scare_i = int(scare)
        except (TypeError, ValueError):
            return EvaluationResult(
                name="prefer_safe_pick",
                value="unknown",
                passed=None,
                explanation="Recommended title is missing a parseable scare_level.",
            )
        if scare_i > max_level:
            return EvaluationResult(
                name="prefer_safe_pick",
                value="fail",
                passed=False,
                explanation=(
                    f"Recommended scare_level {scare_i} exceeds max_scare_level {max_level}."
                ),
            )
        return EvaluationResult(
            name="prefer_safe_pick",
            value="pass",
            passed=True,
            explanation=(
                f"Recommended a within-limit title (scare_level {scare_i} <= {max_level})."
            ),
        )

    if escalated:
        if not searched_titles:
            return EvaluationResult(
                name="prefer_safe_pick",
                value="unknown",
                passed=None,
                explanation="Escalated without recorded search titles to judge against.",
            )
        within = [
            t
            for t in searched_titles
            if isinstance(t.get("scare_level"), int) and t["scare_level"] <= max_level
        ]
        over = [
            t
            for t in searched_titles
            if isinstance(t.get("scare_level"), int) and t["scare_level"] > max_level
        ]
        if over and not within:
            return EvaluationResult(
                name="prefer_safe_pick",
                value="fail",
                passed=False,
                explanation=(
                    "Escalated after a search that only returned over-limit titles; "
                    "prefer broadening to a within-limit recommendation instead."
                ),
            )
        return EvaluationResult(
            name="prefer_safe_pick",
            value="pass",
            passed=True,
            explanation="Escalation did not follow an over-limit-only search result set.",
        )

    return EvaluationResult(
        name="prefer_safe_pick",
        value="unknown",
        passed=None,
        explanation="No accepted recommend or escalate action was recorded.",
    )
