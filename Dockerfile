# Dockerfile
# Uses multi-stage builds requiring Docker 17.05 or higher
# See https://docs.docker.com/develop/develop-images/multistage-build/

# Creating a python base with shared environment variables
FROM python:3.11-bookworm as python-base

# Non interactive frontend
ENV DEBIAN_FRONTEND=noninteractive

# Install requiremnts for python3.9
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    software-properties-common \
    git \
    curl \
    build-essential \
    libsqlite3-mod-spatialite \
    gdal-bin \
    gettext

ENV POETRY_VERSION=1.4.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Add poetry home to path
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install virtualenv
RUN pip install -U virtualenv

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python

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

# Install all dependencies
RUN poetry install --no-dev --extras asgi

ENTRYPOINT [ "/code/docker/entrypoint.prod.sh"]
