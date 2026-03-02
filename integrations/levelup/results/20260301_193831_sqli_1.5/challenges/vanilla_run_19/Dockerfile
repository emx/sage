FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Secure the flag and initialize DB
RUN echo "LEVELUP{Gg6CmVuiqFw4wB3CGpL8zoBtb11nf6yL}" > /flag.txt && chmod 0400 /flag.txt
RUN python init_db.py
RUN chmod 666 /tmp/velopath.db
RUN rm -f Dockerfile /flag.txt

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]