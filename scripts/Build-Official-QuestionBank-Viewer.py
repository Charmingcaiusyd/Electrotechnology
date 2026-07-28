#!/usr/bin/env python3
"""Rebuild the official question bank as a clean student-facing practice app."""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "output" / "learning_package_official"
EXPORT_FILE = PACKAGE_DIR / "exports" / "all_questions.json"
MODULES_DIR = PACKAGE_DIR / "modules"
HTML_DIR = PACKAGE_DIR / "html"
HTML_FILE = HTML_DIR / "question_bank.html"


TYPE_LABELS = {
    "multiple_choice": "选择题",
    "short_answer": "简答题",
    "scenario": "情境题",
    "fault_finding": "故障诊断",
}

DIFFICULTY_LABELS = {
    "foundation": "基础",
    "applied": "应用",
    "advanced": "进阶",
    "chapter": "章节综合",
    "fault_finding": "排故",
    "integrated": "综合",
    "easy": "简单",
    "medium": "中等",
    "hard": "困难",
}

TYPE_ORDER = ["multiple_choice", "short_answer", "scenario", "fault_finding"]
DIFFICULTY_ORDER = [
    "foundation",
    "applied",
    "advanced",
    "chapter",
    "fault_finding",
    "integrated",
    "easy",
    "medium",
    "hard",
]


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(str(item).strip() for item in value if str(item).strip())
    return str(value).strip()


def scrub_student_text(value: Any) -> str:
    text = clean_text(value)
    if not text:
        return ""

    replacements = [
        (r"\s*原题\s*/\s*种子问题\s*[：:]\s*", " "),
        (r"\s*种子问题\s*[：:]\s*", " "),
        (r"\s*PDF\s*原题\s*[：:]\s*", " "),
        (r"\s*教材原题线索\s*[：:]\s*", " "),
        (r"\s*原题线索\s*[：:]\s*", " "),
        (r"教材原题\s*", ""),
        (r"PDF\s*原题\s*", ""),
        (r"原题\s*", ""),
        (r"种子问题\s*", ""),
        (r"DeepSeek\s*语义重写\s*", ""),
        (r"语义重写\s*", ""),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    text = text.replace(" 。", "。").replace(" ，", "，").replace(" ：", "：")
    return text.strip()


def module_sort_key(module_id: str) -> int:
    match = re.search(r"(\d+)", module_id or "")
    return int(match.group(1)) if match else 999


def option_sort_key(key: str) -> tuple[int, str]:
    key = str(key).strip().upper()
    if len(key) == 1 and key.isalpha():
        return (0, key)
    if key.isdigit():
        return (1, f"{int(key):04d}")
    return (2, key)


def normalize_options(options: Any) -> list[dict[str, str]]:
    if not isinstance(options, dict) or not options:
        return []
    rows: list[dict[str, str]] = []
    for key, text in sorted(options.items(), key=lambda item: option_sort_key(str(item[0]))):
        key_text = str(key).strip().upper()
        option_text = scrub_student_text(text)
        if key_text and option_text:
            rows.append({"key": key_text, "text": option_text})
    return rows


def module_titles() -> dict[str, str]:
    titles: dict[str, str] = {}
    for quiz_file in MODULES_DIR.glob("S*/quiz.json"):
        try:
            module_data = read_json(quiz_file)
        except json.JSONDecodeError:
            continue
        module_id = clean_text(module_data.get("module")) or quiz_file.parent.name
        titles[module_id] = clean_text(module_data.get("title")) or module_id
    return titles


def normalize_question(raw: dict[str, Any], index: int, titles: dict[str, str]) -> dict[str, Any]:
    raw_id = clean_text(raw.get("id")) or f"Q{index + 1:04d}"
    display_id = re.sub(r"^V3-", "", raw_id, flags=re.IGNORECASE)
    module = clean_text(raw.get("module"))
    question_type = clean_text(raw.get("type")) or "short_answer"
    difficulty = clean_text(raw.get("difficulty")) or "foundation"
    options = normalize_options(raw.get("options"))
    answer_key = clean_text(raw.get("answer_key")).upper()
    answer_text = scrub_student_text(raw.get("answer_text")) or scrub_student_text(raw.get("answer"))

    if answer_key and options:
        selected_option = next((item for item in options if item["key"] == answer_key), None)
        if selected_option and not answer_text:
            answer_text = selected_option["text"]

    knowledge_details = []
    for item in raw.get("knowledge_points_detailed") or []:
        if not isinstance(item, dict):
            continue
        knowledge_details.append(
            {
                "concept": scrub_student_text(item.get("concept")),
                "detail": scrub_student_text(item.get("detail")),
                "application": scrub_student_text(item.get("field_application")),
                "commonError": scrub_student_text(item.get("common_error")),
                "verification": scrub_student_text(item.get("verification")),
            }
        )

    distractors = []
    rationale = raw.get("distractor_rationale")
    if isinstance(rationale, dict):
        for key, text in sorted(rationale.items(), key=lambda item: option_sort_key(str(item[0]))):
            detail = scrub_student_text(text)
            if detail:
                distractors.append({"key": str(key).strip().upper(), "text": detail})

    return {
        "uid": raw_id,
        "displayId": display_id,
        "module": module,
        "moduleTitle": titles.get(module, module),
        "section": clean_text(raw.get("section")),
        "sectionTitle": scrub_student_text(raw.get("section_title")) or clean_text(raw.get("section")),
        "type": question_type,
        "typeLabel": TYPE_LABELS.get(question_type, question_type),
        "difficulty": difficulty,
        "difficultyLabel": DIFFICULTY_LABELS.get(difficulty, difficulty),
        "cognitiveSkill": scrub_student_text(raw.get("cognitive_skill")),
        "primaryKnowledgePoint": scrub_student_text(raw.get("primary_knowledge_point")),
        "question": scrub_student_text(raw.get("question")),
        "options": options,
        "answerKey": answer_key,
        "answerText": answer_text,
        "answer": answer_text or scrub_student_text(raw.get("answer")),
        "explanation": scrub_student_text(raw.get("explanation")),
        "knowledgePoints": [
            scrub_student_text(point)
            for point in raw.get("knowledge_points", [])
            if scrub_student_text(point)
        ],
        "knowledgeDetails": knowledge_details,
        "distractorRationale": distractors,
        "commonWrongAnswers": [
            scrub_student_text(item)
            for item in raw.get("common_wrong_answers", [])
            if scrub_student_text(item)
        ],
        "safetyNote": scrub_student_text(raw.get("safety_boundary_note")),
        "order": index,
    }


def build_payload() -> dict[str, Any]:
    raw_questions = read_json(EXPORT_FILE)
    if not isinstance(raw_questions, list):
        raise ValueError(f"Expected a list of questions in {EXPORT_FILE}")

    titles = module_titles()
    questions = [normalize_question(raw, index, titles) for index, raw in enumerate(raw_questions)]
    question_counts = Counter(question["module"] for question in questions)

    modules = []
    for module_id in sorted(question_counts, key=module_sort_key):
        modules.append(
            {
                "id": module_id,
                "title": titles.get(module_id, module_id),
                "count": question_counts[module_id],
            }
        )

    type_options = [
        {"id": key, "label": TYPE_LABELS.get(key, key)}
        for key in TYPE_ORDER
        if any(question["type"] == key for question in questions)
    ]
    difficulty_options = [
        {"id": key, "label": DIFFICULTY_LABELS.get(key, key)}
        for key in DIFFICULTY_ORDER
        if any(question["difficulty"] == key for question in questions)
    ]

    return {
        "title": "Electrotechnology 正式版 3000 题库",
        "subtitle": "覆盖 S1-S10 的交互式练习题库",
        "version": "electrotechnology-official-student-ui-20260726",
        "storageKey": "electrotechnology-official-practice-progress",
        "legacyStorageKeys": [],
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "modules": modules,
        "questions": questions,
        "typeOptions": type_options,
        "difficultyOptions": difficulty_options,
    }


HTML_TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Electrotechnology 正式版 3000 题库</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f4f6f2;
      --surface: #ffffff;
      --surface-soft: #f7faf7;
      --ink: #1f271f;
      --muted: #657068;
      --line: #d7ded5;
      --line-strong: #b8c4bb;
      --teal: #0f766e;
      --teal-soft: #dff3ef;
      --green: #237a3b;
      --green-soft: #e3f3e6;
      --red: #b42318;
      --red-soft: #ffe5e0;
      --amber: #a15c10;
      --amber-soft: #fff0d6;
      --blue: #2f6282;
      --blue-soft: #e6f0f5;
      --violet: #6a4b8f;
      --violet-soft: #eee8f5;
      --shadow: 0 12px 30px rgba(38, 47, 40, 0.08);
    }

    * {
      box-sizing: border-box;
    }

    html {
      scroll-behavior: smooth;
    }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", system-ui, -apple-system, sans-serif;
      letter-spacing: 0;
    }

    button,
    input,
    select,
    textarea {
      font: inherit;
    }

    button {
      cursor: pointer;
    }

    button:disabled {
      cursor: not-allowed;
      opacity: 0.45;
    }

    .app {
      display: grid;
      grid-template-columns: 328px minmax(0, 1fr);
      min-height: 100vh;
    }

    .sidebar {
      position: sticky;
      top: 0;
      height: 100vh;
      overflow: auto;
      border-right: 1px solid var(--line);
      background: #fbfcfa;
      padding: 18px 14px;
    }

    .brand {
      padding: 4px 4px 14px;
      border-bottom: 1px solid var(--line);
    }

    .brand h1 {
      margin: 0;
      font-size: 22px;
      line-height: 1.12;
      font-weight: 800;
      letter-spacing: 0;
    }

    .brand p {
      margin: 8px 0 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }

    .side-section {
      padding: 14px 0;
      border-bottom: 1px solid var(--line);
    }

    .side-heading {
      margin: 0 0 8px;
      color: #3d483f;
      font-size: 12px;
      font-weight: 800;
    }

    .mini-stats {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }

    .mini-stat {
      min-height: 68px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
      padding: 10px;
    }

    .mini-stat strong {
      display: block;
      font-size: 22px;
      line-height: 1;
      color: var(--teal);
    }

    .mini-stat span {
      display: block;
      margin-top: 6px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.2;
    }

    .field {
      display: grid;
      gap: 5px;
      margin-top: 10px;
    }

    .field label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }

    .field input,
    .field select {
      width: 100%;
      min-height: 40px;
      border: 1px solid var(--line-strong);
      border-radius: 7px;
      background: var(--surface);
      color: var(--ink);
      padding: 8px 10px;
    }

    .field input:focus,
    .field select:focus,
    textarea:focus {
      outline: 2px solid #a9ded5;
      outline-offset: 1px;
      border-color: var(--teal);
    }

    .quick-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }

    .button,
    .chip,
    .module-button,
    .option-button {
      -webkit-tap-highlight-color: transparent;
    }

    .button {
      min-height: 38px;
      border: 1px solid var(--line-strong);
      border-radius: 7px;
      background: var(--surface);
      color: var(--ink);
      padding: 8px 12px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      line-height: 1.15;
      white-space: nowrap;
    }

    .button:hover {
      border-color: var(--teal);
    }

    .button.primary {
      background: var(--teal);
      border-color: var(--teal);
      color: #ffffff;
    }

    .button.warning {
      background: var(--amber-soft);
      border-color: #e2ba78;
      color: #7c4309;
    }

    .button.danger {
      background: var(--red-soft);
      border-color: #efafa6;
      color: var(--red);
    }

    .chip {
      min-height: 34px;
      border: 1px solid var(--line-strong);
      border-radius: 999px;
      background: var(--surface);
      color: var(--ink);
      padding: 7px 10px;
      font-size: 12px;
      font-weight: 700;
      text-align: center;
    }

    .chip.active {
      border-color: #8fd1c7;
      background: var(--teal-soft);
      color: #0d514c;
    }

    .module-list {
      display: grid;
      gap: 8px;
      max-height: 42vh;
      overflow: auto;
      padding-right: 2px;
    }

    .module-button {
      width: 100%;
      min-height: 54px;
      border: 1px solid transparent;
      border-radius: 8px;
      background: transparent;
      color: var(--ink);
      display: grid;
      grid-template-columns: 45px minmax(0, 1fr) auto;
      gap: 9px;
      align-items: center;
      padding: 8px 9px;
      text-align: left;
    }

    .module-button:hover {
      background: #eef3ef;
    }

    .module-button.active {
      background: var(--teal-soft);
      border-color: #8fd1c7;
    }

    .module-code {
      width: 40px;
      min-height: 31px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 6px;
      background: #edf1ec;
      font-size: 13px;
      font-weight: 800;
    }

    .module-button.active .module-code {
      background: #ffffff;
      color: #0d514c;
    }

    .module-title {
      min-width: 0;
      font-size: 13px;
      font-weight: 750;
      line-height: 1.28;
    }

    .module-progress {
      color: var(--muted);
      font-size: 12px;
      white-space: nowrap;
    }

    .side-actions {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }

    .side-actions .button {
      min-width: 0;
      white-space: normal;
    }

    .main {
      min-width: 0;
      padding: 24px clamp(14px, 3vw, 38px) 46px;
    }

    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 16px;
      align-items: start;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--line);
    }

    .hero h2 {
      margin: 0;
      font-size: clamp(28px, 3.6vw, 42px);
      line-height: 1.08;
      font-weight: 850;
      letter-spacing: 0;
    }

    .hero p {
      max-width: 880px;
      margin: 10px 0 0;
      color: var(--muted);
      line-height: 1.62;
      font-size: 15px;
    }

    .hero-count {
      min-width: 150px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
      padding: 14px;
      text-align: right;
      box-shadow: 0 10px 22px rgba(38, 47, 40, 0.05);
    }

    .hero-count strong {
      display: block;
      font-size: 32px;
      line-height: 1;
      color: var(--teal);
    }

    .hero-count span {
      display: block;
      margin-top: 6px;
      color: var(--muted);
      font-size: 12px;
    }

    .toolbar {
      display: grid;
      grid-template-columns: repeat(4, minmax(130px, 1fr));
      gap: 10px;
      align-items: end;
      padding: 16px 0;
      border-bottom: 1px solid var(--line);
    }

    .toolbar .button {
      width: 100%;
    }

    .pager {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      padding: 14px 0 10px;
    }

    .page-info {
      color: #405047;
      font-size: 14px;
      font-weight: 700;
    }

    .page-controls {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
    }

    .page-jump {
      width: 78px;
      min-height: 38px;
      border: 1px solid var(--line-strong);
      border-radius: 7px;
      background: var(--surface);
      padding: 7px 9px;
      text-align: center;
    }

    .question-list {
      display: grid;
      gap: 12px;
      padding-top: 4px;
    }

    .card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
      box-shadow: var(--shadow);
      overflow: hidden;
    }

    .card.correct {
      border-color: #8bcf98;
    }

    .card.incorrect {
      border-color: #f1a297;
    }

    .card.flagged {
      border-color: #e4b56f;
    }

    .card-head {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 14px 16px 10px;
      border-bottom: 1px solid var(--line);
      background: #fbfcfa;
    }

    .badges {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      min-width: 0;
    }

    .badge {
      min-height: 24px;
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      background: #eef1ed;
      color: #4d584f;
      padding: 4px 8px;
      font-size: 12px;
      font-weight: 700;
      line-height: 1.1;
    }

    .badge.type {
      background: var(--blue-soft);
      color: var(--blue);
    }

    .badge.diff {
      background: var(--amber-soft);
      color: #7c4309;
    }

    .badge.good {
      background: var(--green-soft);
      color: var(--green);
    }

    .qid {
      color: var(--muted);
      font-size: 12px;
      white-space: nowrap;
    }

    .card-body {
      padding: 16px;
    }

    .question-text {
      margin: 0;
      font-size: 16px;
      font-weight: 720;
      line-height: 1.72;
      word-break: break-word;
    }

    code {
      border-radius: 4px;
      background: #eef2ef;
      padding: 1px 4px;
      font-family: "Cascadia Mono", "Consolas", monospace;
      font-size: 0.94em;
      white-space: normal;
    }

    .options {
      display: grid;
      gap: 8px;
      margin-top: 14px;
    }

    .option-button {
      width: 100%;
      min-height: 50px;
      display: grid;
      grid-template-columns: 36px minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      border: 1px solid var(--line-strong);
      border-radius: 8px;
      background: #ffffff;
      color: var(--ink);
      padding: 9px 11px;
      text-align: left;
    }

    .option-button:hover {
      border-color: var(--teal);
      background: #f8fbf8;
    }

    .option-button.selected {
      border-color: var(--teal);
      background: #eefaf7;
    }

    .option-button.correct-option {
      border-color: #7fc28b;
      background: var(--green-soft);
    }

    .option-button.wrong-option {
      border-color: #eb9286;
      background: var(--red-soft);
    }

    .option-key {
      width: 30px;
      height: 30px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      background: #edf1ec;
      font-size: 13px;
      font-weight: 850;
    }

    .option-text {
      min-width: 0;
      line-height: 1.52;
      word-break: break-word;
    }

    .option-status {
      min-width: 36px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      text-align: right;
    }

    .free-work {
      display: grid;
      gap: 8px;
      margin-top: 14px;
    }

    .free-work textarea {
      width: 100%;
      min-height: 112px;
      resize: vertical;
      border: 1px solid var(--line-strong);
      border-radius: 8px;
      background: #ffffff;
      color: var(--ink);
      padding: 10px 12px;
      line-height: 1.55;
    }

    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin-top: 14px;
    }

    .feedback {
      margin-top: 12px;
      border-radius: 8px;
      padding: 10px 12px;
      background: #eef1ed;
      color: #435045;
      font-size: 13px;
      font-weight: 800;
    }

    .feedback.good {
      background: var(--green-soft);
      color: var(--green);
    }

    .feedback.bad {
      background: var(--red-soft);
      color: var(--red);
    }

    .feedback.review {
      background: var(--amber-soft);
      color: #7c4309;
    }

    .answer-panel {
      margin-top: 12px;
      border-left: 4px solid var(--teal);
      background: #f5faf8;
      padding: 12px;
      line-height: 1.65;
    }

    .answer-panel[hidden] {
      display: none;
    }

    .answer-title {
      margin: 0 0 6px;
      font-weight: 850;
    }

    .answer-line {
      margin: 6px 0;
      word-break: break-word;
    }

    .details {
      margin-top: 10px;
      border-top: 1px solid var(--line);
      padding-top: 10px;
    }

    .details summary {
      color: var(--blue);
      cursor: pointer;
      font-weight: 750;
    }

    .detail-grid {
      display: grid;
      gap: 8px;
      margin-top: 10px;
    }

    .detail-item {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcfb;
      padding: 10px;
      line-height: 1.55;
    }

    .detail-item strong {
      display: block;
      margin-bottom: 4px;
    }

    .detail-item p {
      margin: 5px 0;
    }

    .empty {
      border: 1px dashed var(--line-strong);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.6);
      color: var(--muted);
      padding: 26px;
      text-align: center;
    }

    .sr-only {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }

    @media (max-width: 1120px) {
      .toolbar {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }

    @media (max-width: 900px) {
      .app {
        grid-template-columns: 1fr;
      }

      .sidebar {
        position: relative;
        height: auto;
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }

      .module-list {
        grid-auto-flow: column;
        grid-auto-columns: minmax(220px, 1fr);
        overflow-x: auto;
        max-height: none;
      }
    }

    @media (max-width: 640px) {
      .main {
        padding: 18px 12px 34px;
      }

      .hero {
        grid-template-columns: 1fr;
      }

      .hero-count {
        text-align: left;
      }

      .toolbar {
        grid-template-columns: 1fr;
      }

      .pager {
        align-items: stretch;
      }

      .page-controls,
      .actions {
        width: 100%;
      }

      .page-controls .button,
      .actions .button {
        flex: 1 1 120px;
      }

      .card-head {
        flex-direction: column;
      }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside class="sidebar" aria-label="题库筛选">
      <div class="brand">
        <h1>Electrotechnology<br>正式版 3000 题库</h1>
        <p>选择题即时判题，开放题可填写作答并对照参考答案自评。</p>
      </div>

      <section class="side-section">
        <p class="side-heading">学习进度</p>
        <div class="mini-stats" id="sideStats"></div>
      </section>

      <section class="side-section">
        <p class="side-heading">快速筛选</p>
        <div class="quick-grid" id="quickFilters"></div>
        <div class="field">
          <label for="searchInput">搜索</label>
          <input id="searchInput" type="search" placeholder="题干、答案、知识点、题号">
        </div>
      </section>

      <section class="side-section">
        <p class="side-heading">模块</p>
        <div class="module-list" id="moduleList"></div>
      </section>

      <section class="side-section">
        <p class="side-heading">记录</p>
        <div class="side-actions">
          <button class="button" type="button" id="exportProgress">导出记录</button>
          <button class="button" type="button" id="importProgress">导入记录</button>
          <button class="button danger" type="button" id="resetProgress">清空记录</button>
          <button class="button" type="button" id="resetFilters">重置筛选</button>
        </div>
        <input class="sr-only" id="progressFile" type="file" accept="application/json">
      </section>
    </aside>

    <main class="main">
      <header class="hero">
        <div>
          <h2>Electrotechnology 正式版 3000 题库</h2>
          <p>按模块、题型、难度和掌握状态练习。所有题目直接呈现为学生练习题，答案与解析只在需要时展开。</p>
        </div>
        <div class="hero-count">
          <strong id="heroTotal">3000</strong>
          <span>练习题</span>
        </div>
      </header>

      <section class="toolbar" aria-label="题目筛选">
        <div class="field">
          <label for="typeFilter">题型</label>
          <select id="typeFilter"></select>
        </div>
        <div class="field">
          <label for="difficultyFilter">难度</label>
          <select id="difficultyFilter"></select>
        </div>
        <div class="field">
          <label for="statusFilter">状态</label>
          <select id="statusFilter">
            <option value="ALL">全部状态</option>
            <option value="TODO">未练习</option>
            <option value="ANSWERED">已练习</option>
            <option value="CORRECT">正确/掌握</option>
            <option value="REVIEW">错题/需复习</option>
            <option value="FLAGGED">已收藏</option>
            <option value="CHOICE">选择题</option>
            <option value="OPEN">开放题</option>
          </select>
        </div>
        <div class="field">
          <label for="pageSize">每页</label>
          <select id="pageSize">
            <option value="25">25 题</option>
            <option value="50">50 题</option>
            <option value="100">100 题</option>
            <option value="200">200 题</option>
          </select>
        </div>
      </section>

      <nav class="pager" aria-label="分页">
        <div class="page-info" id="pageInfo">第 1 / 1 页，显示 0 / 0</div>
        <div class="page-controls">
          <button class="button" type="button" id="firstPage">首页</button>
          <button class="button" type="button" id="prevPage">上一页</button>
          <input class="page-jump" id="pageJump" type="number" min="1" value="1" aria-label="页码">
          <button class="button" type="button" id="goPage">跳转</button>
          <button class="button" type="button" id="nextPage">下一页</button>
          <button class="button" type="button" id="lastPage">末页</button>
          <button class="button" type="button" id="shuffleToggle">随机顺序</button>
        </div>
      </nav>

      <section class="question-list" id="questionList" aria-label="题目列表"></section>
    </main>
  </div>

  <script id="data" type="application/json">__DATA_JSON__</script>
  <script>
    const DATA = JSON.parse(document.getElementById("data").textContent);
    const QUESTIONS = DATA.questions;
    const STORAGE_KEY = DATA.storageKey || "electrotechnology-official-practice-progress";
    const LEGACY_STORAGE_KEYS = [
      ...(DATA.legacyStorageKeys || []),
      "electrotechnology-" + "v" + "32" + "-practice-progress"
    ];
    const byId = new Map(QUESTIONS.map((question) => [question.uid, question]));

    const state = {
      module: "ALL",
      type: "ALL",
      difficulty: "ALL",
      status: "ALL",
      search: "",
      page: 1,
      pageSize: 25,
      randomized: false,
      shuffleKey: "steady"
    };

    let progress = loadProgress();
    let lastPageCount = 1;

    const el = {
      sideStats: document.getElementById("sideStats"),
      quickFilters: document.getElementById("quickFilters"),
      searchInput: document.getElementById("searchInput"),
      moduleList: document.getElementById("moduleList"),
      exportProgress: document.getElementById("exportProgress"),
      importProgress: document.getElementById("importProgress"),
      resetProgress: document.getElementById("resetProgress"),
      resetFilters: document.getElementById("resetFilters"),
      progressFile: document.getElementById("progressFile"),
      typeFilter: document.getElementById("typeFilter"),
      difficultyFilter: document.getElementById("difficultyFilter"),
      statusFilter: document.getElementById("statusFilter"),
      pageSize: document.getElementById("pageSize"),
      pageInfo: document.getElementById("pageInfo"),
      firstPage: document.getElementById("firstPage"),
      prevPage: document.getElementById("prevPage"),
      nextPage: document.getElementById("nextPage"),
      lastPage: document.getElementById("lastPage"),
      goPage: document.getElementById("goPage"),
      pageJump: document.getElementById("pageJump"),
      shuffleToggle: document.getElementById("shuffleToggle"),
      questionList: document.getElementById("questionList"),
      heroTotal: document.getElementById("heroTotal")
    };

    const quickFilters = [
      { id: "ALL", label: "全部" },
      { id: "TODO", label: "未练习" },
      { id: "REVIEW", label: "错题/复习" },
      { id: "FLAGGED", label: "收藏" },
      { id: "CHOICE", label: "选择题" },
      { id: "OPEN", label: "开放题" }
    ];

    function loadProgress() {
      const keys = [STORAGE_KEY, ...LEGACY_STORAGE_KEYS];
      for (const key of keys) {
        try {
          const raw = localStorage.getItem(key);
          if (!raw) {
            continue;
          }
          const parsed = JSON.parse(raw);
          if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
            if (key !== STORAGE_KEY) {
              localStorage.setItem(STORAGE_KEY, JSON.stringify(parsed));
            }
            return parsed;
          }
        } catch (error) {
          continue;
        }
      }
      return {};
    }

    function saveProgress() {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
    }

    function ensureProgress(uid) {
      progress[uid] = progress[uid] || {};
      return progress[uid];
    }

    function escapeHtml(value) {
      return String(value || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    }

    function escapeAttr(value) {
      return escapeHtml(value).replace(/`/g, "&#096;");
    }

    function formatText(value) {
      return escapeHtml(value || "")
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/\$([^$]+)\$/g, "<code>$1</code>")
        .replace(/\n/g, "<br>");
    }

    function selectMarkup(id, options, allLabel) {
      return [
        `<option value="ALL">${escapeHtml(allLabel)}</option>`,
        ...options.map((option) => `<option value="${escapeAttr(option.id)}">${escapeHtml(option.label)}</option>`)
      ].join("");
    }

    function getProgress(question) {
      return progress[question.uid] || {};
    }

    function isAnswered(question) {
      const item = getProgress(question);
      return Boolean(item.selected || item.self || item.revealed || item.answered);
    }

    function isCorrect(question) {
      const item = getProgress(question);
      return item.correct === true || item.self === "mastered";
    }

    function needsReview(question) {
      const item = getProgress(question);
      return item.correct === false || item.self === "review";
    }

    function isFlagged(question) {
      return Boolean(getProgress(question).flagged);
    }

    function cardClass(question) {
      if (isCorrect(question)) {
        return "correct";
      }
      if (needsReview(question)) {
        return "incorrect";
      }
      if (isFlagged(question)) {
        return "flagged";
      }
      return "";
    }

    function hash(value) {
      let h = 2166136261;
      const text = String(value);
      for (let i = 0; i < text.length; i += 1) {
        h ^= text.charCodeAt(i);
        h = Math.imul(h, 16777619);
      }
      return h >>> 0;
    }

    function searchableText(question) {
      return [
        question.uid,
        question.displayId,
        question.module,
        question.moduleTitle,
        question.sectionTitle,
        question.typeLabel,
        question.difficultyLabel,
        question.cognitiveSkill,
        question.primaryKnowledgePoint,
        question.question,
        question.answerText,
        question.explanation,
        ...(question.knowledgePoints || []),
        ...question.options.map((option) => `${option.key} ${option.text}`)
      ].join(" ").toLowerCase();
    }

    function matches(question) {
      const search = state.search.trim().toLowerCase();
      if (state.module !== "ALL" && question.module !== state.module) {
        return false;
      }
      if (state.type !== "ALL" && question.type !== state.type) {
        return false;
      }
      if (state.difficulty !== "ALL" && question.difficulty !== state.difficulty) {
        return false;
      }
      if (state.status === "TODO" && isAnswered(question)) {
        return false;
      }
      if (state.status === "ANSWERED" && !isAnswered(question)) {
        return false;
      }
      if (state.status === "CORRECT" && !isCorrect(question)) {
        return false;
      }
      if (state.status === "REVIEW" && !needsReview(question)) {
        return false;
      }
      if (state.status === "FLAGGED" && !isFlagged(question)) {
        return false;
      }
      if (state.status === "CHOICE" && question.options.length === 0) {
        return false;
      }
      if (state.status === "OPEN" && question.options.length > 0) {
        return false;
      }
      if (search && !searchableText(question).includes(search)) {
        return false;
      }
      return true;
    }

    function filteredQuestions() {
      let rows = QUESTIONS.filter(matches);
      if (state.randomized) {
        rows = rows.slice().sort((a, b) => hash(a.uid + state.shuffleKey) - hash(b.uid + state.shuffleKey));
      } else {
        rows = rows.slice().sort((a, b) => a.order - b.order);
      }
      return rows;
    }

    function answerLine(question) {
      if (question.answerKey) {
        const option = question.options.find((item) => item.key === question.answerKey);
        return `${question.answerKey}. ${option ? option.text : question.answerText || question.answer}`;
      }
      return question.answerText || question.answer || "";
    }

    function renderSideStats(rows) {
      const answered = QUESTIONS.filter(isAnswered).length;
      const correct = QUESTIONS.filter(isCorrect).length;
      const review = QUESTIONS.filter(needsReview).length;
      const flagged = QUESTIONS.filter(isFlagged).length;
      el.sideStats.innerHTML = `
        <div class="mini-stat"><strong>${answered.toLocaleString("zh-CN")}</strong><span>已练习</span></div>
        <div class="mini-stat"><strong>${correct.toLocaleString("zh-CN")}</strong><span>正确/掌握</span></div>
        <div class="mini-stat"><strong>${review.toLocaleString("zh-CN")}</strong><span>需复习</span></div>
        <div class="mini-stat"><strong>${rows.length.toLocaleString("zh-CN")}</strong><span>当前筛选</span></div>
      `;
      el.heroTotal.textContent = QUESTIONS.length.toLocaleString("zh-CN");
      return { answered, correct, review, flagged };
    }

    function renderQuickFilters() {
      el.quickFilters.innerHTML = quickFilters.map((filter) => `
        <button class="chip ${state.status === filter.id ? "active" : ""}" type="button" data-action="quick-filter" data-status="${escapeAttr(filter.id)}" aria-pressed="${state.status === filter.id}">
          ${escapeHtml(filter.label)}
        </button>
      `).join("");
    }

    function renderModules() {
      const modules = [{ id: "ALL", title: "全部模块", count: QUESTIONS.length }, ...DATA.modules];
      el.moduleList.innerHTML = modules.map((module) => {
        const moduleQuestions = module.id === "ALL"
          ? QUESTIONS
          : QUESTIONS.filter((question) => question.module === module.id);
        const answered = moduleQuestions.filter(isAnswered).length;
        return `
          <button class="module-button ${state.module === module.id ? "active" : ""}" type="button" data-action="module" data-module="${escapeAttr(module.id)}" aria-pressed="${state.module === module.id}">
            <span class="module-code">${escapeHtml(module.id)}</span>
            <span class="module-title">${escapeHtml(module.title)}</span>
            <span class="module-progress">${answered}/${module.count}</span>
          </button>
        `;
      }).join("");
    }

    function feedbackMarkup(question) {
      const item = getProgress(question);
      if (item.selected && question.answerKey && item.revealed) {
        return item.correct
          ? '<div class="feedback good">判断结果：答对了</div>'
          : '<div class="feedback bad">判断结果：答错了，下面是正确答案与解析。</div>';
      }
      if (item.selected && question.answerKey) {
        return '<div class="feedback review">已选择。需要时可展开答案与解析。</div>';
      }
      if (item.self === "mastered") {
        return '<div class="feedback good">自评结果：已掌握</div>';
      }
      if (item.self === "review") {
        return '<div class="feedback review">自评结果：需要复习</div>';
      }
      if (item.revealed) {
        return '<div class="feedback review">已展开参考答案，请对照检查。</div>';
      }
      return "";
    }

    function renderOption(question, option) {
      const item = getProgress(question);
      const selected = item.selected === option.key;
      const reveal = Boolean(item.revealed);
      const correct = reveal && question.answerKey === option.key;
      const wrong = reveal && selected && question.answerKey && question.answerKey !== option.key;
      const classes = [
        "option-button",
        selected ? "selected" : "",
        correct ? "correct-option" : "",
        wrong ? "wrong-option" : ""
      ].filter(Boolean).join(" ");
      let status = "";
      if (correct) {
        status = "正确";
      } else if (wrong || selected) {
        status = "已选";
      }
      return `
        <button class="${classes}" type="button" data-action="select" data-uid="${escapeAttr(question.uid)}" data-option="${escapeAttr(option.key)}">
          <span class="option-key">${escapeHtml(option.key)}</span>
          <span class="option-text">${formatText(option.text)}</span>
          <span class="option-status">${escapeHtml(status)}</span>
        </button>
      `;
    }

    function renderDetails(question) {
      const points = (question.knowledgeDetails || [])
        .filter((item) => item.concept || item.detail || item.commonError || item.verification)
        .map((item) => `
          <div class="detail-item">
            <strong>${escapeHtml(item.concept || "知识点")}</strong>
            ${item.detail ? `<p>${formatText(item.detail)}</p>` : ""}
            ${item.application ? `<p><b>应用：</b>${formatText(item.application)}</p>` : ""}
            ${item.commonError ? `<p><b>易错：</b>${formatText(item.commonError)}</p>` : ""}
            ${item.verification ? `<p><b>检查：</b>${formatText(item.verification)}</p>` : ""}
          </div>
        `).join("");

      const distractors = (question.distractorRationale || [])
        .map((item) => `<div class="detail-item"><strong>${escapeHtml(item.key)} 选项</strong><p>${formatText(item.text)}</p></div>`)
        .join("");

      const wrongAnswers = (question.commonWrongAnswers || [])
        .map((text) => `<div class="detail-item">${formatText(text)}</div>`)
        .join("");

      const safety = question.safetyNote
        ? `<div class="detail-item"><strong>安全边界</strong><p>${formatText(question.safetyNote)}</p></div>`
        : "";

      const content = [points, distractors, wrongAnswers, safety].filter(Boolean).join("");
      if (!content) {
        return "";
      }

      return `
        <details class="details">
          <summary>知识点与易错点</summary>
          <div class="detail-grid">${content}</div>
        </details>
      `;
    }

    function renderQuestion(question) {
      const item = getProgress(question);
      const reveal = Boolean(item.revealed || item.self);
      const hasOptions = question.options.length > 0;
      const optionBlock = hasOptions
        ? `<div class="options" role="radiogroup" aria-label="${escapeAttr(question.displayId)} 选项">${question.options.map((option) => renderOption(question, option)).join("")}</div>`
        : `<div class="free-work"><textarea data-action="draft" data-uid="${escapeAttr(question.uid)}" placeholder="在这里写下你的作答，再对照参考答案。">${escapeHtml(item.draft || "")}</textarea></div>`;

      const answerButtonText = reveal ? "收起答案" : (hasOptions ? "显示答案" : "查看参考答案");
      const flagButtonText = item.flagged ? "取消收藏" : "收藏本题";
      const answerPanel = `
        <div class="answer-panel" ${reveal ? "" : "hidden"}>
          <p class="answer-title">正确答案 / 参考答案</p>
          <p class="answer-line">${formatText(answerLine(question))}</p>
          ${question.explanation ? `<p class="answer-title">解析</p><p class="answer-line">${formatText(question.explanation)}</p>` : ""}
          ${question.knowledgePoints.length ? `<div class="badges">${question.knowledgePoints.map((point) => `<span class="badge good">${escapeHtml(point)}</span>`).join("")}</div>` : ""}
        </div>
      `;

      return `
        <article class="card ${cardClass(question)}" data-uid="${escapeAttr(question.uid)}">
          <div class="card-head">
            <div class="badges">
              <span class="badge">${escapeHtml(question.module)} ${escapeHtml(question.moduleTitle)}</span>
              <span class="badge">${escapeHtml(question.sectionTitle)}</span>
              <span class="badge type">${escapeHtml(question.typeLabel)}</span>
              <span class="badge diff">${escapeHtml(question.difficultyLabel)}</span>
              ${question.primaryKnowledgePoint ? `<span class="badge good">${escapeHtml(question.primaryKnowledgePoint)}</span>` : ""}
            </div>
            <div class="qid">${escapeHtml(question.displayId)}</div>
          </div>
          <div class="card-body">
            <p class="question-text">${formatText(question.question)}</p>
            ${optionBlock}
            <div class="actions">
              <button class="button primary" type="button" data-action="toggle-answer" data-uid="${escapeAttr(question.uid)}">${answerButtonText}</button>
              ${hasOptions ? "" : `
                <button class="button" type="button" data-action="mastered" data-uid="${escapeAttr(question.uid)}">已掌握</button>
                <button class="button warning" type="button" data-action="review" data-uid="${escapeAttr(question.uid)}">需要复习</button>
              `}
              <button class="button" type="button" data-action="flag" data-uid="${escapeAttr(question.uid)}">${flagButtonText}</button>
              <button class="button" type="button" data-action="clear-question" data-uid="${escapeAttr(question.uid)}">重做本题</button>
            </div>
            ${feedbackMarkup(question)}
            ${answerPanel}
            ${renderDetails(question)}
          </div>
        </article>
      `;
    }

    function renderQuestions() {
      const rows = filteredQuestions();
      const pageSize = Number(state.pageSize);
      lastPageCount = Math.max(1, Math.ceil(rows.length / pageSize));
      state.page = Math.min(Math.max(1, state.page), lastPageCount);
      const start = (state.page - 1) * pageSize;
      const visible = rows.slice(start, start + pageSize);

      renderSideStats(rows);
      renderQuickFilters();
      renderModules();

      el.pageInfo.textContent = `第 ${state.page} / ${lastPageCount} 页，显示 ${visible.length} / ${rows.length}`;
      el.pageJump.value = String(state.page);
      el.pageJump.max = String(lastPageCount);
      el.firstPage.disabled = state.page <= 1;
      el.prevPage.disabled = state.page <= 1;
      el.nextPage.disabled = state.page >= lastPageCount;
      el.lastPage.disabled = state.page >= lastPageCount;
      el.shuffleToggle.classList.toggle("primary", state.randomized);

      el.questionList.innerHTML = visible.length
        ? visible.map(renderQuestion).join("")
        : '<div class="empty">当前筛选没有题目。可以重置筛选或换一个关键词。</div>';
    }

    function setState(next) {
      Object.assign(state, next);
      state.page = 1;
      renderQuestions();
      window.scrollTo({ top: 0, behavior: "smooth" });
    }

    function updateQuestion(uid, next) {
      progress[uid] = { ...(progress[uid] || {}), ...next, updatedAt: new Date().toISOString() };
      saveProgress();
      renderQuestions();
    }

    function clearQuestion(uid) {
      delete progress[uid];
      saveProgress();
      renderQuestions();
    }

    function goToPage(page) {
      state.page = Math.min(Math.max(1, Number(page) || 1), lastPageCount);
      renderQuestions();
      window.scrollTo({ top: 0, behavior: "smooth" });
    }

    function exportProgress() {
      const payload = {
        title: DATA.title,
        exportedAt: new Date().toISOString(),
        storageKey: STORAGE_KEY,
        progress
      };
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "electrotechnology-official-progress.json";
      link.click();
      URL.revokeObjectURL(url);
    }

    function resetFilters() {
      state.module = "ALL";
      state.type = "ALL";
      state.difficulty = "ALL";
      state.status = "ALL";
      state.search = "";
      state.page = 1;
      state.randomized = false;
      el.searchInput.value = "";
      el.typeFilter.value = "ALL";
      el.difficultyFilter.value = "ALL";
      el.statusFilter.value = "ALL";
      renderQuestions();
    }

    function bindEvents() {
      el.quickFilters.addEventListener("click", (event) => {
        const button = event.target.closest("[data-action='quick-filter']");
        if (button) {
          el.statusFilter.value = button.dataset.status;
          setState({ status: button.dataset.status });
        }
      });

      el.moduleList.addEventListener("click", (event) => {
        const button = event.target.closest("[data-action='module']");
        if (button) {
          setState({ module: button.dataset.module });
        }
      });

      el.searchInput.addEventListener("input", (event) => setState({ search: event.target.value }));
      el.typeFilter.addEventListener("change", (event) => setState({ type: event.target.value }));
      el.difficultyFilter.addEventListener("change", (event) => setState({ difficulty: event.target.value }));
      el.statusFilter.addEventListener("change", (event) => setState({ status: event.target.value }));
      el.pageSize.addEventListener("change", (event) => setState({ pageSize: Number(event.target.value) }));

      el.firstPage.addEventListener("click", () => goToPage(1));
      el.prevPage.addEventListener("click", () => goToPage(state.page - 1));
      el.nextPage.addEventListener("click", () => goToPage(state.page + 1));
      el.lastPage.addEventListener("click", () => goToPage(lastPageCount));
      el.goPage.addEventListener("click", () => goToPage(el.pageJump.value));
      el.pageJump.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
          goToPage(el.pageJump.value);
        }
      });
      el.shuffleToggle.addEventListener("click", () => {
        state.randomized = !state.randomized;
        state.shuffleKey = String(Date.now());
        goToPage(1);
      });

      el.resetFilters.addEventListener("click", resetFilters);
      el.exportProgress.addEventListener("click", exportProgress);
      el.importProgress.addEventListener("click", () => el.progressFile.click());
      el.progressFile.addEventListener("change", async (event) => {
        const file = event.target.files && event.target.files[0];
        if (!file) {
          return;
        }
        try {
          const parsed = JSON.parse(await file.text());
          const imported = parsed.progress && typeof parsed.progress === "object" ? parsed.progress : parsed;
          progress = imported && typeof imported === "object" && !Array.isArray(imported) ? imported : {};
          saveProgress();
          renderQuestions();
        } catch (error) {
          alert("导入失败：请选择有效的记录文件。");
        } finally {
          event.target.value = "";
        }
      });

      el.resetProgress.addEventListener("click", () => {
        if (confirm("确定清空当前浏览器里的答题记录？")) {
          progress = {};
          saveProgress();
          renderQuestions();
        }
      });

      el.questionList.addEventListener("click", (event) => {
        const button = event.target.closest("button[data-action]");
        if (!button) {
          return;
        }
        const uid = button.dataset.uid;
        const question = byId.get(uid);
        if (!question) {
          return;
        }
        if (button.dataset.action === "select") {
          const selected = button.dataset.option;
          updateQuestion(uid, {
            selected,
            answered: true,
            revealed: true,
            correct: selected === question.answerKey
          });
        }
        if (button.dataset.action === "toggle-answer") {
          const item = getProgress(question);
          updateQuestion(uid, { revealed: !item.revealed });
        }
        if (button.dataset.action === "mastered") {
          updateQuestion(uid, { answered: true, self: "mastered", correct: true, revealed: true });
        }
        if (button.dataset.action === "review") {
          updateQuestion(uid, { answered: true, self: "review", correct: false, revealed: true });
        }
        if (button.dataset.action === "flag") {
          const item = getProgress(question);
          updateQuestion(uid, { flagged: !item.flagged });
        }
        if (button.dataset.action === "clear-question") {
          clearQuestion(uid);
        }
      });

      el.questionList.addEventListener("input", (event) => {
        const textarea = event.target.closest("textarea[data-action='draft']");
        if (!textarea) {
          return;
        }
        const item = ensureProgress(textarea.dataset.uid);
        item.draft = textarea.value;
        item.updatedAt = new Date().toISOString();
        saveProgress();
      });
    }

    function init() {
      el.typeFilter.innerHTML = selectMarkup("typeFilter", DATA.typeOptions, "全部题型");
      el.difficultyFilter.innerHTML = selectMarkup("difficultyFilter", DATA.difficultyOptions, "全部难度");
      bindEvents();
      renderQuestions();
    }

    init();
  </script>
</body>
</html>
"""


def main() -> None:
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    data_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace(
        "</", "<\\/"
    )
    html = HTML_TEMPLATE.replace("__DATA_JSON__", data_json)
    HTML_FILE.write_text(html, encoding="utf-8")

    print(f"Built: {HTML_FILE}")
    print(f"Questions: {len(payload['questions'])}")
    print(f"Modules: {len(payload['modules'])}")
    print(f"Selectable: {sum(1 for q in payload['questions'] if q['options'])}")


if __name__ == "__main__":
    main()
