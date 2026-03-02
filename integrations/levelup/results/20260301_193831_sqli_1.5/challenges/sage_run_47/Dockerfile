FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir flask

# Secure the flag
RUN echo "LEVELUP{Jx2GdjiGAoMbYJp7oPHcEczhdDkIr_i_}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database (creates /tmp/verdant_pulse.db)
RUN python init_db.py

# Clean up sensitive build files
RUN rm -f Dockerfile /flag.txt

# Non-root user setup
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]