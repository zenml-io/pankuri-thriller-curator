"""Record the hand-authored thriller scenarios into Kitaru."""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

load_dotenv(os.path.join(ROOT, ".env"))

from thriller_curator.agent import run_request  # noqa: E402
from thriller_curator.scenarios import SCENARIOS  # noqa: E402


def main() -> None:
    if not os.environ.get("KITARU_AGENT_ID") and not os.environ.get(
        "KITARU_AGENT_VERSION_ID"
    ):
        raise SystemExit("Set KITARU_AGENT_ID or KITARU_AGENT_VERSION_ID first.")
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY missing from environment/.env")

    for scenario in SCENARIOS:
        print(f"Recording {scenario['request_id']} ...", flush=True)
        result = run_request(scenario)
        print(f"  done: {scenario['request_id']}", flush=True)
        # Keep stdout readable; full graph state can be large.
        if isinstance(result, dict) and "messages" in result:
            messages = result["messages"]
            last = messages[-1] if messages else None
            content = getattr(last, "content", None) or last
            print(f"  last message: {str(content)[:240]}")
        print()


if __name__ == "__main__":
    main()
