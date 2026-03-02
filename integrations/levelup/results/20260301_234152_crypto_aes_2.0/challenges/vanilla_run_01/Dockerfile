FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && rm -rf /var/lib/apt/lists/*

RUN pip install flask pycryptodome

WORKDIR /app
COPY . .

RUN echo "LEVELUP{BRhtwps5U9DbATfo8s4YiupUoIUBeh8R}" > /flag.txt && chmod 0400 /flag.txt

RUN python3 init_crypto.py
RUN rm /flag.txt init_crypto.py Dockerfile

RUN chown root:root /app/internal_key.bin && chmod 0400 /app/internal_key.bin

RUN useradd -m ctfuser

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python3", "app.py"]