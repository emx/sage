FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Initialize the database as root so it can read /flag.txt
RUN echo "LEVELUP{EWSfXgxNe6gwXSzeKKuOsdBdVQEZ4xgo}" > /flag.txt && chmod 0400 /flag.txt
RUN python init_db.py
RUN rm -f /flag.txt
RUN rm -f Dockerfile

# Secure the application environment
RUN useradd -m ctfuser
RUN chown -R ctfuser:ctfuser /app
RUN chmod -R 555 /app
# SQLite DB must be in /tmp for runtime writes in a read-only FS environment
RUN mv /app/verdant_logix.db /tmp/verdant_logix.db && chown ctfuser:ctfuser /tmp/verdant_logix.db

USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]