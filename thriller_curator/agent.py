"""LangGraph thriller curator with Kitaru recording."""

from __future__ import annotations

import json
import os
import uuid
from typing import Any

from langchain.agents import create_agent
from kitaru.task import get_task_inputs
from kitaru_langgraph import KitaruGraphRunner

from thriller_curator.tools import TOOLS

MODEL = "openai:gpt-5-nano"

SYSTEM_PROMPT = """You are Pankuri's thriller-night curator.

You help pick ONE movie or book for tonight from a fake in-memory catalog.
The user provides mood, media preference, and a hard max_scare_level (1-5).

Rules:
1. Always search the catalog by mood before recommending.
2. Always call check_intensity_limit before recommend.
3. Never call recommend for a title that check_intensity_limit marks as not allowed.
4. If mood search only returns titles above max_scare_level, do NOT escalate yet.
   Call list_safe_titles_for_limit and recommend the best within-limit alternative
   (prefer funny-scary, literary, or psychological when possible). Explain that
   you stayed inside the scare limit.
5. Escalate only if there are truly no titles within max_scare_level for the media filter.
6. Keep the final assistant message short: what you picked (or that you escalated) and why.

All catalog data is synthetic. Do not invent title_ids.
"""


def build_prompt(payload: dict[str, Any]) -> str:
    """Render one curator request as the user message."""
    return (
        "Plan tonight's thriller pick.\n"
        f"request_id: {payload.get('request_id')}\n"
        f"mood: {payload.get('mood')}\n"
        f"media: {payload.get('media', 'either')}\n"
        f"max_scare_level: {payload.get('max_scare_level')}\n"
        f"notes: {payload.get('notes') or '(none)'}\n"
    )


def build_runner(
    *,
    agent_id: uuid.UUID | None = None,
    agent_version_id: uuid.UUID | None = None,
    session_name: str | None = None,
) -> KitaruGraphRunner[Any, Any]:
    """Build a Kitaru-wrapped LangGraph agent via the supported factory path."""
    return KitaruGraphRunner.from_agent_factory(
        create_agent,
        factory_kwargs={
            "model": MODEL,
            "tools": TOOLS,
            "system_prompt": SYSTEM_PROMPT,
        },
        agent_id=agent_id,
        agent_version_id=agent_version_id,
        session_name=session_name,
    )


def _optional_uuid(name: str) -> uuid.UUID | None:
    value = os.environ.get(name)
    if not value:
        return None
    return uuid.UUID(value)


def run_request(payload: dict[str, Any]) -> Any:
    """Run one curator request and record it in Kitaru when identity is available."""
    request_id = str(payload.get("request_id") or "thriller-night")
    runner = build_runner(
        agent_id=_optional_uuid("KITARU_AGENT_ID"),
        agent_version_id=_optional_uuid("KITARU_AGENT_VERSION_ID"),
        session_name=f"Thriller night: {request_id}",
    )
    return runner.invoke({"messages": [{"role": "user", "content": build_prompt(payload)}]})


def main() -> None:
    """Worker / CLI entrypoint."""
    if os.environ.get("KITARU_TASK_ID"):
        payload = get_task_inputs()
        if not isinstance(payload, dict):
            raise TypeError("Task inputs must be an object")
    else:
        raw = os.environ.get("THRILLER_REQUEST_JSON")
        if not raw:
            raise RuntimeError(
                "Set KITARU_TASK_ID (worker) or THRILLER_REQUEST_JSON (local run)"
            )
        payload = json.loads(raw)
    result = run_request(payload)
    print(result)


if __name__ == "__main__":
    main()
