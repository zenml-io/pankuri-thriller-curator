"""Pure prefer_safe_pick scoring. No model calls and no Kitaru session."""

from __future__ import annotations

from typing import Any

from thriller_curator.scoring import score_prefer_safe_pick


def _call(name: str, **payload: Any) -> dict[str, Any]:
    return {"name": name, "payload": payload}


def _check(title_id: str, *, allowed: bool = True) -> dict[str, Any]:
    return _call(
        "check_intensity_limit",
        title_id=title_id,
        allowed=allowed,
        found=True,
    )


def _recommend(title_id: str, scare_level: int, media: str) -> dict[str, Any]:
    return _call(
        "recommend",
        accepted=True,
        title_id=title_id,
        scare_level=scare_level,
        media=media,
        action="recommend",
    )


def _escalate() -> dict[str, Any]:
    return _call("escalate_to_human", accepted=True, action="escalate", reason="none")


def test_escalation_at_cap_1_passes() -> None:
    passed, explanation = score_prefer_safe_pick(
        1,
        "either",
        [_call("search_catalog", titles=[]), _escalate()],
    )
    assert passed is True
    assert "no catalog title is within max_scare_level 1" in explanation


def test_escalation_when_safe_titles_exist_fails() -> None:
    passed, explanation = score_prefer_safe_pick(
        2,
        "movie",
        [_call("search_catalog", titles=[]), _escalate()],
    )
    assert passed is False
    assert "within-limit title exists for media movie" in explanation


def test_over_cap_recommendation_fails() -> None:
    passed, explanation = score_prefer_safe_pick(
        2,
        "movie",
        [_check("t-midsommar", allowed=True), _recommend("t-midsommar", 5, "movie")],
    )
    assert passed is False
    assert "scare_level 5 exceeds max_scare_level 2" in explanation


def test_recommendation_without_prior_allowed_check_fails() -> None:
    passed, explanation = score_prefer_safe_pick(
        3,
        "movie",
        [_recommend("t-coraline", 2, "movie"), _check("t-coraline")],
    )
    assert passed is False
    assert "not called with allowed=True for t-coraline before recommend" in explanation


def test_wrong_media_fails() -> None:
    passed, explanation = score_prefer_safe_pick(
        3,
        "movie",
        [_check("t-rebecca"), _recommend("t-rebecca", 2, "book")],
    )
    assert passed is False
    assert "media book does not match the media filter movie" in explanation


def test_empty_search_then_valid_recommend_passes() -> None:
    passed, explanation = score_prefer_safe_pick(
        3,
        "movie",
        [
            _call("search_catalog", titles=[], found=False, count=0),
            _check("t-coraline"),
            _recommend("t-coraline", 2, "movie"),
        ],
    )
    assert passed is True
    assert "scare_level 2 <= 3" in explanation


def test_both_actions_fail() -> None:
    passed, explanation = score_prefer_safe_pick(
        3,
        "movie",
        [_check("t-coraline"), _recommend("t-coraline", 2, "movie"), _escalate()],
    )
    assert passed is False
    assert "exactly one is allowed" in explanation


def test_neither_action_fails() -> None:
    passed, explanation = score_prefer_safe_pick(
        3, "movie", [_call("search_catalog", titles=[])]
    )
    assert passed is False
    assert "Accepted 0 recommend and 0 escalate" in explanation
