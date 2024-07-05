FROM python:3.11.8-slim-bullseye as builder

WORKDIR /app

COPY pyproject.toml ./

ENV POETRY_VERSION=1.7.1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

RUN pip install "poetry==$POETRY_VERSION"
RUN poetry install --no-interaction --no-ansi --verbose --without test\
     && rm -rf $POETRY_CACHE_DIR
RUN poetry env use 3.11

COPY . .
FROM python:3.11.8-slim-bullseye
ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    PATH="/app/.venv/bin:$PATH"
COPY --from=builder /app /app

EXPOSE 8080

ENTRYPOINT ["uvicorn", "index:app", "--reload", "--host", "0.0.0.0", "--port", "8080"]
