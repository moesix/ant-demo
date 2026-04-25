FROM python:3.11-slim AS builder

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt

FROM python:3.11-slim

WORKDIR /home/appuser/app

RUN useradd --create-home appuser

COPY --from=builder /usr/src/app/requirements.txt .
COPY --from=builder /usr/src/app/wheels /wheels

RUN pip install --no-cache /wheels/*

COPY . .

USER appuser

EXPOSE 5000 50052

CMD ["python", "app.py"]