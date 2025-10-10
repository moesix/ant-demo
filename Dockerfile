FROM python:3.11-slim as builder

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt

FROM python:3.11-slim

RUN useradd --create-home appuser
WORKDIR /home/appuser/app

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY app.py .

USER appuser

EXPOSE 5000

CMD ["python", "./app.py"]