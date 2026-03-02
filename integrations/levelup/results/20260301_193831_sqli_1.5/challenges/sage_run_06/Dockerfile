FROM python:3.12-slim

WORKDIR /app

COPY . .
RUN rm -f Dockerfile

RUN pip install --no-cache-dir flask

# Secure the flag
RUN echo "LEVELUP{3vS0UqU5HOf9nGBZF9n_MtvlH6eaSboZ}" > /flag.txt && \
    chmod 0400 /flag.txt && \
    python init_db.py && \
    rm -f Dockerfile /flag.txt

RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /tmp/ /app/
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]