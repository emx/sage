FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir pycryptodome flask

# Copy source files
COPY app.py crypto_utils.py init_crypto.py ./

# Flag isolation
RUN echo "LEVELUP{TZ1AGqTN6JRl8KuSAlW6aU9ZGYECgEp_}" > /flag.txt \
    && chmod 0400 /flag.txt \
    && python3 init_crypto.py \
    && rm /flag.txt init_crypto.py

# Set up non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]