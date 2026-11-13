"""Synthetic thriller catalog. No external APIs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

Media = Literal["movie", "book"]


@dataclass(frozen=True)
class Title:
    title_id: str
    name: str
    media: Media
    scare_level: int  # 1 calm literary tension … 5 extreme
    moods: tuple[str, ...]
    why_it_fits_pankuri: str
    gore: bool
    funny_scary: bool


CATALOG: tuple[Title, ...] = (
    Title(
        "t-rebecca",
        "Rebecca",
        "book",
        2,
        ("literary", "psychological", "gothic"),
        "Dark literary suspense with atmosphere over gore.",
        False,
        False,
    ),
    Title(
        "t-shadows",
        "What We Do in the Shadows",
        "movie",
        2,
        ("funny-scary", "comedy", "vampire"),
        "Horror-adjacent, but you laugh at the scary parts.",
        False,
        True,
    ),
    Title(
        "t-coraline",
        "Coraline",
        "movie",
        2,
        ("uncanny", "coming-of-age", "funny-scary"),
        "Creepy and witty without extreme intensity.",
        False,
        True,
    ),
    Title(
        "t-gone-girl",
        "Gone Girl",
        "movie",
        3,
        ("psychological", "thriller", "marriage"),
        "Sharp psychological thriller; tension over jump scares.",
        False,
        False,
    ),
    Title(
        "t-silent-patient",
        "The Silent Patient",
        "book",
        3,
        ("psychological", "thriller", "twist"),
        "Literary-leaning psychological suspense.",
        False,
        False,
    ),
    Title(
        "t-hill-house",
        "The Haunting of Hill House",
        "movie",
        3,
        ("gothic", "psychological", "haunting"),
        "Atmospheric dread; still within mid intensity.",
        False,
        False,
    ),
    Title(
        "t-sharp-objects",
        "Sharp Objects",
        "book",
        4,
        ("psychological", "dark", "literary"),
        "Dark literary crime; heavier than mid-scare nights.",
        True,
        False,
    ),
    Title(
        "t-mexican-gothic",
        "Mexican Gothic",
        "book",
        4,
        ("gothic", "horror", "literary"),
        "Lush gothic horror that escalates past cozy scary.",
        True,
        False,
    ),
    Title(
        "t-hereditary",
        "Hereditary",
        "movie",
        5,
        ("horror", "grief", "extreme"),
        "Extremely intense; only for max scare nights.",
        True,
        False,
    ),
    Title(
        "t-midsommar",
        "Midsommar",
        "movie",
        5,
        ("folk-horror", "daylight-dread", "extreme"),
        "Daylight horror at the top of the scare scale.",
        True,
        False,
    ),
)


def search_titles(
    *,
    mood: str,
    media: str | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Rank catalog titles by simple mood keyword overlap."""
    tokens = {token.strip().lower() for token in mood.replace("/", " ").split() if token}
    results: list[tuple[int, Title]] = []
    for title in CATALOG:
        if media in {"movie", "book"} and title.media != media:
            continue
        score = sum(1 for token in tokens if any(token in m for m in title.moods))
        if title.funny_scary and {"funny", "funny-scary", "laugh", "comedy"} & tokens:
            score += 2
        if score > 0:
            results.append((score, title))
    results.sort(key=lambda item: (-item[0], item[1].scare_level, item[1].name))
    return [_public(title) for _, title in results[:limit]]


def list_safe_titles(
    *,
    max_scare_level: int,
    media: str | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """List catalog titles that stay within a scare limit, ignoring mood fit."""
    results: list[Title] = []
    for title in CATALOG:
        if media in {"movie", "book"} and title.media != media:
            continue
        if title.scare_level <= max_scare_level:
            results.append(title)
    results.sort(key=lambda item: (item.scare_level, item.name))
    return [_public(title) for title in results[:limit]]


def get_title(title_id: str) -> dict[str, Any] | None:
    for title in CATALOG:
        if title.title_id == title_id:
            return {
                **_public(title),
                "why_it_fits_pankuri": title.why_it_fits_pankuri,
                "gore": title.gore,
                "funny_scary": title.funny_scary,
            }
    return None


def _public(title: Title) -> dict[str, Any]:
    data = asdict(title)
    data.pop("why_it_fits_pankuri")
    data.pop("gore")
    data.pop("funny_scary")
    return data
