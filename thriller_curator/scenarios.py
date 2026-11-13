"""Hand-authored requests for first recordings and review."""

from __future__ import annotations

from typing import Any

# Mix of safe picks, boundary cases, and situations where escalation is better.
SCENARIOS: list[dict[str, Any]] = [
    {
        "request_id": "night-001",
        "mood": "funny-scary comedy vampires",
        "media": "movie",
        "max_scare_level": 3,
        "notes": "I laugh at the scary parts.",
    },
    {
        "request_id": "night-002",
        "mood": "literary gothic psychological",
        "media": "book",
        "max_scare_level": 2,
        "notes": "Keep it atmospheric, not extreme.",
    },
    {
        "request_id": "night-003",
        "mood": "psychological thriller twist",
        "media": "either",
        "max_scare_level": 3,
        "notes": "Something sharp but not gore-forward.",
    },
    {
        "request_id": "night-004",
        "mood": "extreme folk-horror daylight dread",
        "media": "movie",
        "max_scare_level": 2,
        "notes": "Curious about the vibe but scare limit is low tonight.",
    },
    {
        "request_id": "night-005",
        "mood": "grief horror extreme",
        "media": "movie",
        "max_scare_level": 5,
        "notes": "Full scare budget tonight.",
    },
    {
        "request_id": "night-006",
        "mood": "cozy uncanny funny-scary",
        "media": "movie",
        "max_scare_level": 2,
        "notes": "Something clever and creepy-cute.",
    },
]
