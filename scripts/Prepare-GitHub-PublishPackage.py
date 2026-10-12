from __future__ import annotations

import re
import shutil
import stat
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / ".publish" / "Electrotechnology"
OFFICIAL_PACKAGE = ROOT / "output" / "learning_package_official"
OFFICIAL_HTML = OFFICIAL_PACKAGE / "html" / "index.html"
OFFICIAL_CARD_DATA = OFFICIAL_PACKAGE / "html" / "cards-data.js"
EXPLANATION_PDF = ROOT / "output" / "pdf" / "Electrotechnology_教材全解_合订版.pdf"

SECRET_RE = re.compile(rb"sk-[A-Za-z0-9_-]{16,}")
TEXT_SUFFIXES = {
    ".bat",
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".txt",
}


def copy_file(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns(
            "*.pdf",
            "*.db",
            "*.sqlite",
            "*.sqlite3",
            "*.log",
            "__pycache__",
            "*.pyc",
            "node_modules",
        ),
    )


def assert_safe_package_dir(path: Path) -> None:
    resolved = path.resolve()
    expected_parent = (ROOT / ".publish").resolve()
    if resolved.parent != expected_parent or resolved.name != "Electrotechnology":
        raise RuntimeError(f"Refusing to replace unexpected path: {resolved}")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def remove_tree(path: Path) -> None:
    def handle_remove_error(function, failing_path, exc_info):
        failing = Path(failing_path)
        failing.chmod(stat.S_IWRITE)
        function(failing_path)

    shutil.rmtree(path, onerror=handle_remove_error)


def clear_package_contents(path: Path) -> None:
    """Regenerate tracked content without deleting an existing Git repository."""
    for child in path.iterdir():
        if child.name == ".git":
            continue
        if child.is_dir():
            remove_tree(child)
        else:
            child.unlink()


def create_package() -> None:
    if not OFFICIAL_HTML.exists():
        raise FileNotFoundError(f"Official knowledge-card entry not found: {OFFICIAL_HTML}")
    if not OFFICIAL_CARD_DATA.exists():
        raise FileNotFoundError(f"Knowledge-card data not found: {OFFICIAL_CARD_DATA}")

    assert_safe_package_dir(PACKAGE)
    if PACKAGE.exists():
        clear_package_contents(PACKAGE)
    else:
        PACKAGE.mkdir(parents=True)

    copy_file(ROOT / "README_DeepTutor_中文.txt", PACKAGE / "README_DeepTutor_中文.txt")
    copy_file(ROOT / "Start_DeepTutor.bat", PACKAGE / "Start_DeepTutor.bat")
    copy_file(ROOT / "Stop_DeepTutor.bat", PACKAGE / "Stop_DeepTutor.bat")

    scripts = [
        "LocalEmbeddingServer.py",
        "Prepare-GitHub-PublishPackage.py",
        "Set-DeepSeek-API-Key.ps1",
        "Start-DeepTutor.ps1",
        "Stop-DeepTutor.ps1",
        "Test-DeepSeek-API.ps1",
    ]
    for script in scripts:
        copy_file(ROOT / "scripts" / script, PACKAGE / "scripts" / script)

    copy_tree(OFFICIAL_PACKAGE, PACKAGE / "output" / "learning_package_official")

    copy_file(OFFICIAL_HTML, PACKAGE / "docs" / "index.html")
    copy_file(OFFICIAL_CARD_DATA, PACKAGE / "docs" / "cards-data.js")
    copy_file(ROOT / "docs" / "cards-expansion-s7-s10.js", PACKAGE / "docs" / "cards-expansion-s7-s10.js")
    write_text(PACKAGE / "docs" / ".nojekyll", "")
    if EXPLANATION_PDF.exists():
        copy_file(EXPLANATION_PDF, PACKAGE / "docs" / "downloads" / EXPLANATION_PDF.name)
        copy_file(EXPLANATION_PDF, PACKAGE / "output" / "pdf" / EXPLANATION_PDF.name)
    write_text(
        PACKAGE / ".github" / "workflows" / "pages.yml",
        """name: Deploy static site to GitHub Pages

on:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Configure Pages
        uses: actions/configure-pages@v5
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
""",
    )

    write_text(
        PACKAGE / ".gitignore",
        """# Local and secret files
.env
.env.*
!.env.example
*.key
*.secret
credentials*
secrets*
model_catalog.json

# Runtime data
data/
logs/
run/
tmp/
.publish/
*.log
*.db
*.sqlite
*.sqlite3

# Dependencies and caches
.venv/
node_modules/
__pycache__/
**/__pycache__/
*.pyc

# Original source materials are intentionally not public
*.pdf
!docs/downloads/Electrotechnology_教材全解_合订版.pdf
!output/pdf/Electrotechnology_教材全解_合订版.pdf
""",
    )

    write_text(
        PACKAGE / "README.md",
        """# Electrotechnology

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
""",
    )


def validate_package() -> tuple[int, int]:
    forbidden_suffixes = {".pdf", ".db", ".sqlite", ".sqlite3", ".log"}
    forbidden_names = {"model_catalog.json"}
    allowed_pdfs = {
        Path("docs/downloads/Electrotechnology_教材全解_合订版.pdf"),
        Path("output/pdf/Electrotechnology_教材全解_合订版.pdf"),
    }
    file_count = 0
    total_bytes = 0
    secret_hits: list[Path] = []
    forbidden_hits: list[Path] = []

    for path in PACKAGE.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(PACKAGE)
        file_count += 1
        total_bytes += path.stat().st_size

        if (path.suffix.lower() in forbidden_suffixes and rel not in allowed_pdfs) or path.name in forbidden_names:
            forbidden_hits.append(rel)

        if path.suffix.lower() in TEXT_SUFFIXES and SECRET_RE.search(path.read_bytes()):
            secret_hits.append(rel)

    if forbidden_hits:
        raise RuntimeError("Forbidden files in package: " + ", ".join(map(str, forbidden_hits)))
    if secret_hits:
        raise RuntimeError("Potential API keys in package: " + ", ".join(map(str, secret_hits)))

    return file_count, total_bytes


def main() -> None:
    create_package()
    file_count, total_bytes = validate_package()
    print(f"Package: {PACKAGE}")
    print(f"Files: {file_count}")
    print(f"Size: {total_bytes / 1024 / 1024:.2f} MB")
    print("Validation: no PDF/database/log/model config files and no sk-* API key patterns")


if __name__ == "__main__":
    main()
