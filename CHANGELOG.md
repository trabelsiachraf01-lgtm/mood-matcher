# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning:
[SemVer](https://semver.org/) (`MAJOR.MINOR.PATCH`, tracked in `pyproject.toml`).

## [Unreleased]

## [0.1.0] - 2026-09-16

### Added
- Real ingestion (Jamendo songs, Openverse images) into a Postgres+pgvector catalog,
  ~100 rows each across 10 mood keywords.
- `/suggestions` matches an uploaded image/song or typed text against the catalog by
  embedding cosine distance (EBind), always returning both a matched image and song.
- Real playback: autoplay on match, ±10s skip controls.
- Museum-style presentation of the matched image (framed, full uncropped photo).
- Per-request timing and match-score logging; timeouts on captioning/embedding/transcoding.
- Semantic versioning, this changelog, `commit-msg`/`pre-commit` git hooks, CI (ruff +
  frontend typecheck/lint), and tag-triggered GitHub Releases.

### Changed
- Simplified the wizard to 2 steps — dropped mood-tag/energy filters that weren't
  actually used in matching.
- Captioning model switched to a benchmarked low-latency flash-lite model.
