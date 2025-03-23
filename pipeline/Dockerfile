FROM python:3.11-slim AS python-base
#goal here is to replicate the structure as in project folder
RUN mkdir /app
ENV PROJECT_NAME="pipeline"
ENV APP_DIR="/app"
ENV MODULE_DIR="/app/src"
ENV PYTHONBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_HOME="/opt/poetry" \
    VENV_PATH="/app/.venv" \
    POETRY_VIRTUALENVS_IN_PROJECT=true

ENV PATH="${POETRY_HOME}/bin:${VENV_PATH}/bin:${PATH}"

FROM python-base AS builder-base

# get essential packages to build / compile python packages
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*



ENV POETRY_VERSION=1.8.4
RUN curl -sSL https://install.python-poetry.org | python3 -

# remove temporarily installed build essential and curl since we dont need it anymore
# -y for autoaccept and -q for less verbose

RUN apt-get purge --auto-remove -y -q build-essential curl
WORKDIR ${APP_DIR}
COPY poetry.lock pyproject.toml ./
RUN poetry lock
RUN poetry install --no-root --only main
COPY . .

FROM python:3.11-slim as runtime
ENV PATH="${POETRY_HOME}/bin:${VENV_PATH}/bin:${PATH}"
COPY --from=builder-base app/.venv app/.venv
ENV PYTHONOPTIMIZE=2
COPY --from=builder-base app/src app/src
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR app/src
ENTRYPOINT ["python","-m", "pipeline"]


