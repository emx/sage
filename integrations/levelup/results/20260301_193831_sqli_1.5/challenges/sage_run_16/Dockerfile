FROM python:3.12-slim

WORKDIR /app

# Install Flask
RUN pip install --no-cache-dir flask

# Copy application files
COPY . .
RUN rm -f Dockerfile

# Flag Isolation: Create flag, initialize DB as root, then cleanup
RUN echo "LEVELUP{MOkCJr08R9gIzH3NyBrq24RxmL3HYXHL}" > /flag.txt && \
    chmod 0400 /flag.txt && \
    python init_db.py && \
    rm -f /flag.txt && \
    rm -f Dockerfile

# Set up non-root user
RUN useradd -m ctfuser && \
    chown -R ctfuser:ctfuser /app /tmp

USER ctfuser
EXPOSE 5000

CMD ["python", "app.py"]