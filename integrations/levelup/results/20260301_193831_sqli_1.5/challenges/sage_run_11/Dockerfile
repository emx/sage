FROM python:3.12-slim

WORKDIR /app

COPY . .
RUN rm -f Dockerfile

RUN pip install --no-cache-dir flask

# Secure the flag
RUN echo "LEVELUP{v_bqJbvEQcu7ugpS6h1K5gkbT6g7JQyx}" > /flag.txt && \
    chmod 0400 /flag.txt && \
    python3 init_db.py && \
    rm /flag.txt && \
    rm -f Dockerfile

RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp

USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]