# Mood Matcher

Cross-modal mood-matching app — an image, a song, or text in; a generated caption plus a
real matched song/image out. See `README.md` for setup and run steps.

## Code style

- SOLID, object-oriented: model real entities as classes, not loose functions passed around.
- Modular: small functions/classes, each with one clear responsibility, and a clean
  separation between layers (API, embedding, captioning, ingestion, storage).
- Comments and docstrings: short and general — explain *why*, not *what*; skip anything the
  code already says on its own.
- Tests: focused and relevant — real behavior, not incidental implementation detail.

## Before you build

- Ground every decision in a real constraint, not a guess — say why.
- Ask before picking a new tech stack, or adding a feature that isn't already scoped.
- Keep anwsers consise and in simple terms