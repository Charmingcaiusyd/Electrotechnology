# Electrotechnology

Electrotechnology course-wide knowledge cards and local DeepTutor support scripts.

## Static Website

GitHub Pages entry point:

https://charmingcaiusyd.github.io/Electrotechnology/

The hosted learning interface lives in `docs/index.html`. It contains 1,391 S1-S10 knowledge cards with topic search, core/detail filters, remembered/forgotten tracking, forgotten-card review, and progress import/export. All modules have source-reviewed cards; S7-S10 were expanded to 84/72/66/84.

Download the generated textbook explanation PDF:

https://charmingcaiusyd.github.io/Electrotechnology/downloads/Electrotechnology_教材全解_合订版.pdf

## Repository Contents

- `docs/index.html` - GitHub Pages knowledge-card entry.
- `docs/cards-data.js` - course-wide knowledge-card data.
- `docs/cards-expansion-s7-s10.js` - source-reviewed S7-S10 expansion loaded after the original cards to preserve progress IDs.
- `docs/downloads/Electrotechnology_教材全解_合订版.pdf` - generated textbook explanation PDF.
- `.github/workflows/pages.yml` - automatic GitHub Pages deployment from `docs/`.
- `output/learning_package_official/` - official knowledge-card package and course support materials.
- `output/pdf/` - generated PDF study materials.
- `scripts/` - local generation and DeepTutor helper scripts.
- `Start_DeepTutor.bat` / `Stop_DeepTutor.bat` - local launcher helpers.

## Privacy

The original PDF textbook/source file, runtime databases, logs, local model settings, and API keys are intentionally excluded from this public repository.
