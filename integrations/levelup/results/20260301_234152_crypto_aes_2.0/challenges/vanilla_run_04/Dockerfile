FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir pycryptodome flask

COPY app.py init_crypto.py ./

# Flag Isolation: Create flag, run init script, and cleanup in one layer
RUN echo "LEVELUP{YBxapSJNVUu86lS1ri6Kqp23pamj_qzU}" > /flag.txt && \
    chmod 0400 /flag.txt && \
    python3 init_crypto.py && \
    rm /flag.txt init_crypto.py

RUN useradd -m ctfuser && \
    chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]