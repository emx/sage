FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Initialize database and flag
RUN echo "LEVELUP{M4V32z_j0P7WiHbEUZTjroNFa_y4dPzs}" > /flag.txt && chmod 0400 /flag.txt
RUN python init_db.py
RUN rm -f Dockerfile /flag.txt

# Secure permissions
RUN useradd -m ctfuser
RUN chown -R root:root /app && chmod -R 755 /app
# Ensure the database is writable by the non-root user
RUN chmod 666 /tmp/verdaroot.db

USER ctfuser
EXPOSE 5000

CMD ["python", "app.py"]