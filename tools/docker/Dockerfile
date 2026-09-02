FROM python:3.12-slim

WORKDIR /workspace

RUN apt-get update \
    && apt-get install --no-install-recommends --yes git shellcheck \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README_EN.md ./
COPY tools ./tools

RUN pip install --no-cache-dir ".[dev]" yamllint
