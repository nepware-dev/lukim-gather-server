#!/bin/sh
uv sync --frozen
uv run ./manage.py collectstatic --no-input
uv run ./manage.py test -v 3
