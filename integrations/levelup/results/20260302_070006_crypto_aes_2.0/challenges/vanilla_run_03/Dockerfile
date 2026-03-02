FROM python:3.12-slim

WORKDIR /app

# Install dependencies inline
RUN pip install pycryptodome flask

# Copy application files
COPY app.py init_crypto.py ./

# Flag Isolation: Write flag, encrypt it, then remove plaintext and script
RUN echo "LEVELUP{iv1oJhTiCK3juwpBy4uqGVQX2Ldwdt4m}" > /flag.txt && \
    chmod 0400 /flag.txt && \
    python3 init_crypto.py && \
    rm /flag.txt init_crypto.py

# Configure non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]