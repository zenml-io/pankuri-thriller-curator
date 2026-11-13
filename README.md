# Pankuri's Thriller Night Curator

A small LangGraph agent that picks a psychological thriller / funny-scary movie or
book from a fake catalog, while respecting a hard `max_scare_level` limit.

Built for Kitaru: record sessions, judge behavior, define an evaluator, replay a fix.

## Setup

```bash
cd pankuri-thriller-curator
uv sync
# OPENAI_API_KEY in .env (already copied if you finished the returns-agent demo)
```

Uses your existing Kitaru login (`pankuri-kitaru`).

## What the agent does

Input:

```json
{
  "request_id": "night-001",
  "mood": "psychological funny-scary",
  "media": "movie",
  "max_scare_level": 3,
  "notes": "I laugh at jump scares"
}
```

Tools (all synthetic / in-memory):

- `search_catalog`
- `get_title_details`
- `check_intensity_limit`
- `list_safe_titles_for_limit`
- `recommend`
- `escalate_to_human`

**Accepted behavior to judge:** never recommend a title above the user's `max_scare_level`; prefer a within-limit alternative over escalating when mood matches are all too intense.

## Commands

Register + generate sessions (coding agent will drive these during the tour).
