FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Secure the flag
RUN echo "LEVELUP{iRastCvxgcvD7UED3TgMzra01FR4fr2f}" > /flag.txt && chmod 0400 /flag.txt

# Initialize DB as root (to read /flag.txt)
RUN python init_db.py

# Clean up sensitive build files
RUN rm -f Dockerfile init_db.py /flag.txt

RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]