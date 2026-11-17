# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Score whether a pick stayed inside the scare cap or escalation was the only option."""

from __future__ import annotations

import json
import os
import re
import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from kitaru.api_models.v1.evaluation import EvaluationResult
    from kitaru.task.evaluator import SessionView

_ROOT = os.path.abspath(os.path.dirname(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from thriller_curator.scoring import score_prefer_safe_pick

__all__ = ["evaluate", "score_prefer_safe_pick"]


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


def _session_text(session: SessionView) -> str:
    inputs = session.session.inputs
    if isinstance(inputs, dict):
        messages = inputs.get("messages")
        if isinstance(messages, list) and messages:
            first = messages[0]
            if isinstance(first, dict):
                return str(first.get("content") or "")
            return str(getattr(first, "content", "") or "")
        return json.dumps(inputs)
    return str(inputs or "")


def _parse_request(text: str) -> tuple[int, str] | None:
    level = re.search(r"max_scare_level:\s*(\d+)", text)
    media = re.search(r"media:\s*(movie|book|either)", text)
    if level is None or media is None:
        return None
    return int(level.group(1)), media.group(1)


def _tool_calls(session: SessionView) -> list[dict[str, Any]]:
    from kitaru.api_models.v1.session_node import NodeType

    calls: list[dict[str, Any]] = []
    for node in session.nodes:
        if node.node_type is not NodeType.TOOL_CALL:
            continue
        calls.append({"name": node.tool_name, "payload": _tool_payload(node) or {}})
    return calls


def evaluate(session: SessionView) -> EvaluationResult:
    """Extract the request and tool calls, then score them."""
    from kitaru.api_models.v1.evaluation import EvaluationResult

    parsed = _parse_request(_session_text(session))
    if parsed is None:
        return EvaluationResult(
            name="prefer_safe_pick",
            value="unknown",
            passed=None,
            explanation="Could not read max_scare_level and media from the session input.",
        )
    max_level, media = parsed
    passed, explanation = score_prefer_safe_pick(max_level, media, _tool_calls(session))
    return EvaluationResult(
        name="prefer_safe_pick",
        value="pass" if passed else "fail",
        passed=passed,
        explanation=explanation,
    )
