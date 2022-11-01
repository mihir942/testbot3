FROM python:3.10-alpine AS builder
WORKDIR /app
ADD pyproject.toml poetry.lock /app/
RUN apk add build-base libffi-dev
RUN pip install poetry==1.2.0a2
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-ansi


FROM python:3.10-alpine
WORKDIR /app
COPY --from=builder /app /app
ADD main.py /app
RUN adduser app -h /app -u 1000 -g 1000 -DH
USER 1000
CMD ["/app/.venv/bin/python", "main.py"]
