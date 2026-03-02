FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Secure the flag and initialize DB
RUN echo "LEVELUP{wT5XqRzBplj3IMAt1D36674u1qFRTmdA}" > /flag.txt && chmod 0400 /flag.txt
RUN python init_db.py && rm -f /flag.txt

RUN rm -f Dockerfile

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]