REM Generate output/extracted_data.json
poetry run python src/rank_flow extract temp/resumes/
REM Generate output/generated_rubric.json
poetry run python src/rank_flow generate-rubric -r data/job_description.txt -m qwen3 --timeout 120
REM Generate output/ranked_data.json
poetry run python src/rank_flow rank -i output/extracted_data.json --rubric-file output/generated_rubric.json -m qwen3 --timeout 60
REM Convert output/ranked_data.json to output/ranked_data.csv
poetry run python src/rank_flow convert -i output/ranked_data.json -o output/ranked_data.csv
REM Copy top candidates to output/top_candidates/
poetry run python src/rank_flow copy