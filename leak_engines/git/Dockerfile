FROM python:3.10-alpine AS builder
WORKDIR /app
ADD pyproject.toml poetry.lock /app/

RUN apk add build-base libffi-dev
RUN pip install poetry
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-ansi

# ---

FROM python:3.10-alpine
WORKDIR /app

COPY --from=builder /app /app
COPY --from=trufflesecurity/trufflehog:3.6.11 /usr/bin/trufflehog /app/.venv/bin/trufflehog
ADD . /app

RUN adduser app -h /app -u 1000 -g 1000 -DH
USER 1000

ENTRYPOINT [ "/app/.venv/bin/python", "cli.py" ]