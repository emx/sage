FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir pycryptodome flask

# Copy source files to the app directory
COPY app.py crypto_utils.py init_crypto.py /app/

# Flag isolation
RUN echo "LEVELUP{PM1AlhbdCw6Sihqse9r3iVLDtgZMvfdm}" > /flag.txt && \
    chmod 0400 /flag.txt && \
    python3 init_crypto.py && \
    rm /flag.txt init_crypto.py

# Create non-root user and set permissions
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]