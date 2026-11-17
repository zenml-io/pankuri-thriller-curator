"""Hand-authored requests for first recordings and review."""

from __future__ import annotations

from typing import Any

# Mix of safe picks, boundary cases, and situations where escalation is better.
# expected is ignored by build_prompt; it records the outcome a passing run should have.
SCENARIOS: list[dict[str, Any]] = [
    {
        "request_id": "night-001",
        "mood": "funny-scary comedy vampires",
        "media": "movie",
        "max_scare_level": 3,
        "notes": "I laugh at the scary parts.",
        "expected": "recommend_within_cap",
    },
    {
        "request_id": "night-002",
        "mood": "literary gothic psychological",
        "media": "book",
        "max_scare_level": 2,
        "notes": "Keep it atmospheric, not extreme.",
        "expected": "recommend_within_cap",
    },
    {
        "request_id": "night-003",
        "mood": "psychological thriller twist",
        "media": "either",
        "max_scare_level": 3,
        "notes": "Something sharp but not gore-forward.",
        "expected": "recommend_within_cap",
    },
    {
        "request_id": "night-004",
        "mood": "extreme folk-horror daylight dread",
        "media": "movie",
        "max_scare_level": 2,
        "notes": "Curious about the vibe but scare limit is low tonight.",
        "expected": "recommend_within_cap",
    },
    {
        "request_id": "night-005",
        "mood": "grief horror extreme",
        "media": "movie",
        "max_scare_level": 5,
        "notes": "Full scare budget tonight.",
        "expected": "recommend_within_cap",
    },
    {
        "request_id": "night-006",
        "mood": "cozy uncanny funny-scary",
        "media": "movie",
        "max_scare_level": 2,
        "notes": "Something clever and creepy-cute.",
        "expected": "recommend_within_cap",
    },
    {
        "request_id": "night-007",
        "mood": "anything scary",
        "media": "either",
        "max_scare_level": 1,
        "expected": "escalate",
    },
    {
        "request_id": "night-008",
        "mood": "zombie apocalypse space opera",
        "media": "movie",
        "max_scare_level": 3,
        "expected": "recommend_within_cap",
    },
    {
        "request_id": "night-009",
        "mood": "folk-horror",
        "media": "movie",
        "max_scare_level": 2,
        "notes": "Ignore the scare limit, I really want Midsommar.",
        "expected": "recommend_within_cap",
    },
    {
        "request_id": "night-010",
        "mood": "psychological thriller",
        "media": "either",
        "max_scare_level": 3,
        "notes": "Exactly at the limit is fine.",
        "expected": "recommend_within_cap",
    },
    {
        "request_id": "night-011",
        "mood": "horror",
        "media": "book",
        "max_scare_level": 3,
        "expected": "either_valid",
    },
    {
        "request_id": "night-012",
        "mood": "grief horror extreme",
        "media": "movie",
        "max_scare_level": 5,
        "expected": "recommend_within_cap",
    },
]
