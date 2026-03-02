FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install pycryptodome flask

# Copy source files
COPY app.py crypto_utils.py init_crypto.py ./

# Flag Isolation: Build-time crypto setup
RUN echo "LEVELUP{gr_8uvjFTXpRFZOAwekJVn33COB3kf5o}" > /flag.txt && chmod 0400 /flag.txt \
    && python3 init_crypto.py \
    && rm /flag.txt init_crypto.py

# Switch to non-root user
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]