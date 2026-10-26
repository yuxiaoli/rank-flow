# Command reference. Copy individual Bash examples from the repository root.
# Never execute/source this whole file. Static review only; no candidate data,
# model calls, ranking, installations, or copies were performed for this file.
# Python >=3.11 and Poetry. No installed rank-flow console script is defined.
poetry install
poetry run python -m rank_flow --help

# Privacy and decision boundary: extraction stores full text and paths; rubric
# generation sends requirements to the hardcoded remote gateway in scoring.py,
# and ranking sends document content, rubric and optional requirements there.
# Obtain appropriate consent/authority before disclosure; requests may cost money.
# AI scores are unvalidated suggestions, not automatic hiring decisions. Use
# meaningful human review and relevant criteria; no fairness safeguards exist.
# No dry run, redaction, request-count cap, offline scoring, or endpoint CLI flag.
# Outputs overwrite without confirmation. Use separate new paths and backups.

# === Extract locally: directory OR ZIP; a single PDF path is NOT accepted ===
# Recurses all files. Only PDF text and UTF-8 .txt extraction are implemented;
# DOCX/XLSX/CSV/image/video/audio are placeholders. No OCR for scanned PDFs.
poetry run python -m rank_flow extract "YOUR_INPUT_DIRECTORY" --output "YOUR_NEW_OUTPUT_DIRECTORY/extracted.json"
poetry run python -m rank_flow extract "YOUR_INPUT_DIRECTORY" --verbose --output "YOUR_NEW_OUTPUT_DIRECTORY/extracted.json"
poetry run python -m rank_flow extract "YOUR_TRUSTED_ARCHIVE.zip" --output "YOUR_NEW_OUTPUT_DIRECTORY/extracted.json"
# ZIP writes beside input to ARCHIVE_STEM_extracted, can overwrite existing
# extracted files, and is not cleaned up. Review archive contents before use.
# Even with --output, extract ALWAYS overwrites output/file_list.txt and exposes
# scanned paths. Keep outputs outside the scanned tree to avoid re-ingestion.
# Extraction failures can become empty-text/status entries; inspect JSON statuses.

# === Credentials/model prerequisites for the following remote operations ===
# main loads .env. Set credentials privately, never commit or print them.
# Actual names differ from README's API_KEY_* examples:
# JIUTIAN_API_KEY -> jiutian-lan
# QWEN3_API_KEY -> qwen3
# DEEPSEEK_R1_API_KEY -> deepseek-r1
# --model choices depend on which keys are present at startup. Default is
# jiutian-lan if configured, otherwise first configured model. Supplying a key
# does not verify gateway authorization, endpoint availability, or cost.

# === Generate rubric: required requirements file; default score range 0..100 ===
poetry run python -m rank_flow generate-rubric --requirements "YOUR_REQUIREMENTS.txt" --output "YOUR_NEW_OUTPUT_DIRECTORY/rubric.json"
poetry run python -m rank_flow generate-rubric -r "YOUR_REQUIREMENTS.txt" -m qwen3 --timeout 120 --score-range 0 10 -o "YOUR_NEW_OUTPUT_DIRECTORY/rubric.json"
# jiutian-lan/deepseek-r1 are alternative models when their keys are configured.
# Timeout is seconds (float, default 30); score-range has exactly two integers.
# Range order/weights/schema are not validated. Failed generation can silently
# save the built-in default rubric instead of the requested custom score range.

# === Rank: default rubric, requirements-aware, or custom rubric ===
poetry run python -m rank_flow rank --input-data "YOUR_NEW_OUTPUT_DIRECTORY/extracted.json" --output "YOUR_NEW_OUTPUT_DIRECTORY/ranked.json"
poetry run python -m rank_flow rank -i "YOUR_NEW_OUTPUT_DIRECTORY/extracted.json" -r "YOUR_REQUIREMENTS.txt" -m deepseek-r1 --timeout 60 -o "YOUR_NEW_OUTPUT_DIRECTORY/ranked.json"
poetry run python -m rank_flow rank -i "YOUR_NEW_OUTPUT_DIRECTORY/extracted.json" --rubric-file "YOUR_NEW_OUTPUT_DIRECTORY/rubric.json" -m qwen3 --timeout 60 -o "YOUR_NEW_OUTPUT_DIRECTORY/ranked.json"
poetry run python -m rank_flow rank -i "YOUR_NEW_OUTPUT_DIRECTORY/extracted.json" -r "YOUR_REQUIREMENTS.txt" --rubric-file "YOUR_NEW_OUTPUT_DIRECTORY/rubric.json" -m qwen3 --timeout 60 -o "YOUR_NEW_OUTPUT_DIRECTORY/ranked.json"
# Missing rubric file only warns and falls back; malformed rubric can fail.
# Total scores are accepted from model JSON, not recomputed or range-validated.
# Failed calls return 0/manual_review but the command may still exit successfully.
# Resume/retry variant: only records with score == 0 or missing are rescored.
# Existing nonzero scores (even negative/invalid values) are not intentionally
# refreshed. There is no --force or --rescore; model/rubric changes do not reset.
poetry run python -m rank_flow rank -i "YOUR_NEW_OUTPUT_DIRECTORY/ranked.json" --rubric-file "YOUR_NEW_OUTPUT_DIRECTORY/rubric.json" -m qwen3 -o "YOUR_NEW_OUTPUT_DIRECTORY/ranked-retry.json"

# === Local conversion and selection; review scores and provenance first ===
# CSV includes only file_path, score, recommendation, overall_assessment.
poetry run python -m rank_flow convert --input-file "YOUR_NEW_OUTPUT_DIRECTORY/ranked.json" --output "YOUR_NEW_OUTPUT_DIRECTORY/ranked.csv"
# Copy's --num and --min-score are mutually exclusive. No filter by file type:
# any referenced local file may be copied; use trusted, reviewed ranked JSON.
poetry run python -m rank_flow copy --input-file "YOUR_NEW_OUTPUT_DIRECTORY/ranked.json" --output-dir "YOUR_NEW_OUTPUT_DIRECTORY/top"
poetry run python -m rank_flow copy -i "YOUR_NEW_OUTPUT_DIRECTORY/ranked.json" --num 10 -o "YOUR_NEW_OUTPUT_DIRECTORY/top-ten"
poetry run python -m rank_flow copy -i "YOUR_NEW_OUTPUT_DIRECTORY/ranked.json" --min-score 75 -o "YOUR_NEW_OUTPUT_DIRECTORY/above-threshold"
# Default top count 5; use positive --num (negative slicing is not rejected).
# Choose thresholds matching the actual rubric, not blindly 75 for a 0..10 scale.
# Copies are named SCORE_originalname; duplicate names/scores overwrite silently.
# copy_summary.json is overwritten; copied_files lists all qualified candidates,
# including failed copies. Individual copy failures may not produce nonzero exit.

# Default paths when options are omitted: extracted_data/generated_rubric/
# ranked_data JSON under output/, ranked_data.csv, output/top_candidates/.
# They may already contain private real results; do not run defaults casually.
# scripts/run.bat runs the full fixed-path workflow, including remote API calls
# and copying; it is Windows cmd.exe syntax, NOT a safe preview. Prefer explicit
# individual commands above rather than executing that batch file.
# Dependency export from scripts/export_requirements.bat (optional prerequisite:
# an installed poetry-plugin-export version supporting these options).
# Writes/overwrites requirements.txt; does not run the application.
# poetry export -f requirements.txt --without-hashes --without-urls -o requirements.txt
# No project-defined test/lint/deployment command; tests contains only __init__.py.
