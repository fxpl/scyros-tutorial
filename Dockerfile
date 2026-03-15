FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install dependencies

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl \
    build-essential \
    git \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Scyros

RUN curl --proto '=https' --tlsv1.2 -LsSf https://github.com/fxpl/scyros/releases/latest/download/scyros-installer.sh | sh

# Python

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# uv installs to ~/.local/bin by default
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app
COPY .python-version pyproject.toml ./

RUN uv python install && \
    uv venv &&\
    uv sync

ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false


COPY .streamlit ./.streamlit
COPY Scyros_Tutorial.py helpers.py ./


EXPOSE 8501
ENTRYPOINT [".venv/bin/python","-m","streamlit","run","Scyros_Tutorial.py","--server.address=0.0.0.0","--server.port=8501","--server.headless=true"]

