"""Synthetic tools for the thriller curator."""

from __future__ import annotations

from typing import Any, Literal

from langchain.tools import tool

from thriller_curator.catalog import get_title, list_safe_titles, search_titles

MediaFilter = Literal["movie", "book", "either"]


@tool
def search_catalog(mood: str, media: MediaFilter = "either", limit: int = 5) -> dict[str, Any]:
    """Search the fake catalog by mood keywords and optional media filter."""
    media_arg = None if media == "either" else media
    matches = search_titles(mood=mood, media=media_arg, limit=limit)
    return {
        "found": bool(matches),
        "count": len(matches),
        "titles": matches,
        "message": "Catalog search complete." if matches else "No titles matched those mood keywords.",
    }


@tool
def list_safe_titles_for_limit(
    max_scare_level: int, media: MediaFilter = "either", limit: int = 5
) -> dict[str, Any]:
    """List titles within max_scare_level when mood search only returns over-limit matches."""
    media_arg = None if media == "either" else media
    matches = list_safe_titles(
        max_scare_level=max_scare_level, media=media_arg, limit=limit
    )
    return {
        "found": bool(matches),
        "count": len(matches),
        "titles": matches,
        "max_scare_level": max_scare_level,
        "message": (
            "Safe titles within the scare limit."
            if matches
            else "No titles exist within that scare limit for this media filter."
        ),
    }


@tool
def get_title_details(title_id: str) -> dict[str, Any]:
    """Get scare level and detail for one catalog title."""
    title = get_title(title_id)
    if title is None:
        return {"found": False, "message": f"Unknown title_id {title_id!r}."}
    return {"found": True, "title": title, "message": "Title details loaded."}


@tool
def check_intensity_limit(title_id: str, max_scare_level: int) -> dict[str, Any]:
    """Check whether a title stays within the user's max scare level."""
    title = get_title(title_id)
    if title is None:
        return {
            "found": False,
            "allowed": False,
            "message": f"Unknown title_id {title_id!r}.",
        }
    allowed = int(title["scare_level"]) <= int(max_scare_level)
    return {
        "found": True,
        "allowed": allowed,
        "title_id": title_id,
        "scare_level": title["scare_level"],
        "max_scare_level": max_scare_level,
        "message": (
            "Within the user's scare limit."
            if allowed
            else "Above the user's scare limit; do not recommend this title."
        ),
    }


@tool
def recommend(title_id: str, reason: str) -> dict[str, Any]:
    """Lock in one recommendation for tonight. Only call after an allowed intensity check."""
    title = get_title(title_id)
    if title is None:
        return {
            "accepted": False,
            "action": "recommend",
            "message": f"Unknown title_id {title_id!r}.",
        }
    return {
        "accepted": True,
        "action": "recommend",
        "title_id": title_id,
        "name": title["name"],
        "media": title["media"],
        "scare_level": title["scare_level"],
        "reason": reason,
        "message": f"Recommended {title['name']}.",
    }


@tool
def escalate_to_human(reason: str) -> dict[str, Any]:
    """Escalate when no safe title fits the mood and scare limit."""
    return {
        "accepted": True,
        "action": "escalate",
        "reason": reason,
        "message": "Escalated to a human for a custom pick.",
    }


TOOLS = [
    search_catalog,
    list_safe_titles_for_limit,
    get_title_details,
    check_intensity_limit,
    recommend,
    escalate_to_human,
]
