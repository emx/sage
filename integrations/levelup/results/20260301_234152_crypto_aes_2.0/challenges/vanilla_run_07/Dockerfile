FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install pycryptodome flask

# Copy source and utilities
COPY app.py crypto_utils.py init_crypto.py ./

# Initialize challenge data: write flag, run script, then cleanup
RUN echo "LEVELUP{PVh_j1miI0MLarMIJCwNw0DRkh7R29ZU}" > /flag.txt && \
    python3 init_crypto.py && \
    rm /flag.txt init_crypto.py

# Security setup
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]