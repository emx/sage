FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Create flag and secure it
RUN echo "LEVELUP{jpvLwTrfzjWEhTquNw482jp_tZXIzLw_}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database (creates /tmp/verdant.db)
RUN python init_db.py

# Cleanup sensitive build files
RUN rm -f Dockerfile init_db.py /flag.txt

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]