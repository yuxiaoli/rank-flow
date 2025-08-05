REM https://python-poetry.org/docs/cli/#export
REM poetry self add poetry-plugin-export
poetry export -f requirements.txt --without-hashes --without-urls -o requirements.txt