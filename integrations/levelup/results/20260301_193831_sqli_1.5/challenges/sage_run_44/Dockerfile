FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Secure the flag and initialize database
RUN echo "LEVELUP{oKn2knhlcH9_1SBtoHsLSh0chiB_BLns}" > /flag.txt && chmod 0400 /flag.txt
RUN python init_db.py
RUN rm -f Dockerfile /flag.txt init_db.py

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]