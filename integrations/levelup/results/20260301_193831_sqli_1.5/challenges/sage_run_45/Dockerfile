FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Flag isolation: Read by root, stored in DB, file then protected
RUN echo "LEVELUP{pzocrVKbutCaS2UAbcM0GpsDH1B3SbpO}" > /flag.txt && chmod 0400 /flag.txt

# Initialize DB in /tmp (writable at runtime) 
# We run it here to ensure it works, then app.py will re-run it if /tmp is wiped (tmpfs)
RUN python init_db.py

RUN rm -f Dockerfile

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]