FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Secure the flag and initialize database
RUN echo "LEVELUP{HPImXbbCERulZppwVCLNY90SaYdDS8B5}" > /flag.txt && \
    chmod 0400 /flag.txt && \
    python init_db.py && \
    rm -f /flag.txt

RUN rm -f Dockerfile

RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]