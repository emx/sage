FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask
RUN rm -f Dockerfile

# Flag creation and isolation
RUN echo "LEVELUP{bBzR701Tvps8tPQV17uhL8vcm6VWQQtI}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database (creates /tmp/logistics.db)
RUN python init_db.py

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]