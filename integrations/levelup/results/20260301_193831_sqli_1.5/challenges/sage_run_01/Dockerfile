FROM python:3.12-slim

WORKDIR /app

COPY . .
RUN rm -f Dockerfile

RUN pip install --no-cache-dir flask

# Secure the flag and initialize DB
RUN echo "LEVELUP{Fk6gmQmQycn_IJvhNxgqcDW9htUENbgt}" > /flag.txt && \
    chmod 0400 /flag.txt && \
    python init_db.py && \
    rm -f /flag.txt && \
    rm -f Dockerfile

# Create non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]