#!/bin/sh
uv pip freeze | uv run safety check --stdin
