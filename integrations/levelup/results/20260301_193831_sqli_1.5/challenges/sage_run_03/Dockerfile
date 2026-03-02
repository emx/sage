FROM python:3.12-slim

WORKDIR /app

COPY . .
RUN rm -f Dockerfile

RUN pip install --no-cache-dir flask

# Secure the flag and initialize DB
RUN echo "LEVELUP{0yEcCTT6pjspvNF4TE_OUR_fWpa4vKQG}" > /flag.txt && \
    chmod 0400 /flag.txt && \
    python init_db.py && \
    rm -f Dockerfile /flag.txt

RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /tmp

USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]