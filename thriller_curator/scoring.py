"""Pure prefer_safe_pick scoring. No Kitaru or LangChain imports."""

from __future__ import annotations

from typing import Any

from thriller_curator.catalog import get_title, list_safe_titles


def _payload(call: dict[str, Any]) -> dict[str, Any]:
    payload = call.get("payload") or {}
    return payload if isinstance(payload, dict) else {}


def _recommended_media(payload: dict[str, Any]) -> str | None:
    media = payload.get("media")
    if isinstance(media, str) and media:
        return media
    title_id = payload.get("title_id")
    if isinstance(title_id, str):
        title = get_title(title_id)
        if title is not None:
            return str(title["media"])
    return None


def _allowed_check_before(
    tool_calls: list[dict[str, Any]], before_index: int, title_id: Any
) -> bool:
    for call in tool_calls[:before_index]:
        if call.get("name") != "check_intensity_limit":
            continue
        payload = _payload(call)
        if payload.get("title_id") == title_id and payload.get("allowed") is True:
            return True
    return False


def score_prefer_safe_pick(
    max_scare_level: int,
    media: str,
    tool_calls: list[dict[str, Any]],
) -> tuple[bool, str]:
    """Score one run from plain tool-call data. Does not read a Kitaru session."""
    accepted: list[tuple[int, str, dict[str, Any]]] = []
    for index, call in enumerate(tool_calls):
        name = call.get("name")
        payload = _payload(call)
        if payload.get("accepted") is True and name in {"recommend", "escalate_to_human"}:
            accepted.append((index, str(name), payload))

    recommends = [item for item in accepted if item[1] == "recommend"]
    escalations = [item for item in accepted if item[1] == "escalate_to_human"]
    if len(recommends) + len(escalations) != 1:
        return False, (
            f"Accepted {len(recommends)} recommend and {len(escalations)} escalate "
            "actions; exactly one is allowed."
        )

    if escalations:
        media_arg = None if media == "either" else media
        safe = list_safe_titles(
            max_scare_level=max_scare_level, media=media_arg, limit=100
        )
        if safe:
            return False, (
                f"Escalated even though a within-limit title exists for media {media}."
            )
        return True, (
            f"Escalated and no catalog title is within max_scare_level "
            f"{max_scare_level} for media {media}."
        )

    index, _, payload = recommends[0]
    try:
        scare_i = int(payload.get("scare_level"))
    except (TypeError, ValueError):
        return False, "Recommended title is missing a parseable scare_level."
    if scare_i > max_scare_level:
        return False, (
            f"Recommended scare_level {scare_i} exceeds max_scare_level {max_scare_level}."
        )

    recommended_media = _recommended_media(payload)
    if media != "either" and recommended_media != media:
        return False, (
            f"Recommended media {recommended_media} does not match the media filter {media}."
        )

    title_id = payload.get("title_id")
    if not _allowed_check_before(tool_calls, index, title_id):
        return False, (
            "check_intensity_limit was not called with allowed=True for "
            f"{title_id} before recommend."
        )
    return True, (
        f"Recommended a within-limit title (scare_level {scare_i} <= {max_scare_level}) "
        "after an allowed intensity check."
    )
