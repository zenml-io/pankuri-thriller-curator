"""Catalog helpers and the scare-check tool. No model calls."""

from __future__ import annotations

from thriller_curator.catalog import list_safe_titles, search_titles
from thriller_curator.tools import check_intensity_limit


def test_check_intensity_limit_at_cap() -> None:
    result = check_intensity_limit.invoke(
        {"title_id": "t-coraline", "max_scare_level": 2}
    )
    assert result["found"] is True
    assert result["allowed"] is True
    assert result["scare_level"] == 2


def test_check_intensity_limit_one_above_cap() -> None:
    result = check_intensity_limit.invoke(
        {"title_id": "t-coraline", "max_scare_level": 1}
    )
    assert result["allowed"] is False
    assert result["scare_level"] == 2


def test_check_intensity_limit_below_cap() -> None:
    result = check_intensity_limit.invoke(
        {"title_id": "t-coraline", "max_scare_level": 3}
    )
    assert result["allowed"] is True
    assert result["scare_level"] == 2


def test_check_intensity_limit_unknown_title() -> None:
    result = check_intensity_limit.invoke(
        {"title_id": "t-missing", "max_scare_level": 3}
    )
    assert result["found"] is False
    assert result["allowed"] is False


def test_list_safe_titles_cap_1_is_empty() -> None:
    assert list_safe_titles(max_scare_level=1) == []


def test_list_safe_titles_cap_2_movies_in_name_order() -> None:
    titles = list_safe_titles(max_scare_level=2, media="movie")
    assert [item["name"] for item in titles] == [
        "Coraline",
        "What We Do in the Shadows",
    ]


def test_list_safe_titles_book_filter() -> None:
    titles = list_safe_titles(max_scare_level=3, media="book")
    assert [item["name"] for item in titles] == ["Rebecca", "The Silent Patient"]
    assert all(item["media"] == "book" for item in titles)


def test_search_titles_known_mood() -> None:
    titles = search_titles(mood="vampire")
    assert any(item["title_id"] == "t-shadows" for item in titles)


def test_search_titles_nonsense_mood_is_empty() -> None:
    assert search_titles(mood="zombie apocalypse space opera") == []
