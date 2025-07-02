FROM python:3.11.11-slim-bullseye

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl=7.74.0-1.3+deb11u14 \
        tini \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME=/opt/poetry
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org/ | python -
ENV PATH="${PATH}:${POETRY_HOME}/bin"

WORKDIR /app
COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml
COPY README.md README.md

RUN poetry config virtualenvs.create false --local && chmod +r /app/poetry.toml
RUN poetry install --no-root

COPY fastapi_template fastapi_template
RUN poetry install

# load file to parse certificates from base64 envs
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

EXPOSE 8000 

# start from entrypoint to parse cert envs
ENTRYPOINT [ "/usr/bin/tini", "--" ]
CMD ["/entrypoint.sh"]