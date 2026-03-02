FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Flag isolation: root-owned, non-readable by ctfuser
RUN echo "LEVELUP{q2xxeaKFBddCV3XJZUsSOHAy4bFdw1od}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database as root to read /flag.txt, then store in /tmp
RUN python init_db.py

RUN rm -f Dockerfile

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]