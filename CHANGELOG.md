# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning:
[SemVer](https://semver.org/) (`MAJOR.MINOR.PATCH`, tracked in `pyproject.toml`).

## [Unreleased]

## [0.2.0] - 2026-09-18

### Added
- Generate an original song via ElevenLabs Music instead of a catalog match
- Real generated caption for text input (previously just echoed the raw text)
- Progress bar with status text while waiting, replacing the static button
- Architecture and sequence diagrams in `docs/`

## [0.1.0] - 2026-09-16

### Added
- Real Jamendo/Openverse ingestion into a Postgres+pgvector catalog
- Cross-modal matching via `/suggestions` (image, song, or text input)
- Real audio playback with autoplay and ±10s skip
- Museum-style match presentation
- Per-request timing/score logging and call timeouts
- Semantic versioning, changelog, git hooks, CI, tag-triggered releases

### Changed
- Simplify wizard to 2 steps, drop unused mood-tag/energy filters
- Switch captioning to a faster flash-lite model
