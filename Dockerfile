# Dockerfile
# Uses multi-stage builds requiring Docker 17.05 or higher
# See https://docs.docker.com/develop/develop-images/multistage-build/

# Creating a python base with shared environment variables
FROM python:3.13-bullseye as python-base

# Non interactive frontend
ENV DEBIAN_FRONTEND=noninteractive

# Install requirements for python3.13
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    software-properties-common \
    git \
    curl \
    build-essential \
    libsqlite3-mod-spatialite \
    gdal-bin \
    gettext

ENV UV_LINK_MODE=copy \
    PYTHONPATH="/code" \
    VIRTUAL_ENV="/code/.venv"

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install astral uv
COPY --from=ghcr.io/astral-sh/uv:0.5.26 /uv /uvx /bin/

# Testing stage
FROM python-base as testing

WORKDIR /code

ENTRYPOINT ["/code/docker/entrypoint.test.sh"]

# Development stage
FROM python-base as development

WORKDIR /code

ENTRYPOINT ["/code/docker/entrypoint.dev.sh"]

# Production stage
FROM python-base as production

WORKDIR /code

COPY . /code/

# Install dependencies
RUN uv sync --frozen --no-dev --all-extras

ENTRYPOINT [ "/code/docker/entrypoint.prod.sh"]
