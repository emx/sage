FROM python:3.12-slim

WORKDIR /app

COPY . .
RUN rm -f Dockerfile

RUN pip install --no-cache-dir flask

# Secure the flag
RUN echo "LEVELUP{JfrRH2_KOEbpj36CdMJ21sdn2zhx2aa0}" > /flag.txt && \
    chmod 0400 /flag.txt && \
    python init_db.py && \
    rm -f Dockerfile /flag.txt

RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]