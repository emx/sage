FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install flask

RUN echo "LEVELUP{RHYEepo_oY7Q7rqwbH4sfi2A9Dy0rUof}" > /flag.txt && chmod 0400 /flag.txt

RUN python init_db.py

RUN rm -f Dockerfile /flag.txt

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]