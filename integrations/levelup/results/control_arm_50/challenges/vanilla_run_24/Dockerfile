FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask
RUN python init_db.py
RUN echo "LEVELUP{JLPIOvqJoKKfVzuq9mB1oJ1iUTVN7DTy}" > /flag.txt && chmod 0400 /flag.txt
RUN python -c "import os; flag = open('/flag.txt').read().strip(); import sqlite3; conn = sqlite3.connect('/tmp/skyworks.db'); conn.execute('INSERT INTO system_config (key_name, key_value) VALUES (?, ?)', ('internal_master_secret', flag)); conn.commit(); conn.close()"

RUN rm -f Dockerfile /flag.txt init_db.py

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]