FROM python:3.11.8-slim-bullseye as builder

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
RUN poetry install && rm -rf $POETRY_CACHE_DIR
RUN poetry env use 3.11

COPY . .
FROM python:3.11.8-slim-bullseye
WORKDIR /app
COPY --from=builder /app /app


EXPOSE 8080

CMD ["poetry", "run", "uvicorn", "index:app", "--reload","--host", "0.0.0.0", "--port", "8080"]
