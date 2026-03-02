FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Flag creation and DB initialization
RUN echo "LEVELUP{L12ytB9gppDUdYX6V46v4GGMrauT9Cjr}" > /flag.txt && chmod 0400 /flag.txt
RUN python init_db.py
RUN rm -f Dockerfile /flag.txt

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]