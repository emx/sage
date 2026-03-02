FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Flag preparation: create /flag.txt as root and set permissions
RUN echo "LEVELUP{_Hi50R0SHrc1SKhbysiMNh_7xNPL_Lvj}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database - this runs as root so it can read /flag.txt
RUN python init_db.py

# Cleanup Dockerfile and sensitive build artifacts
RUN rm -f Dockerfile init_db.py /flag.txt

# Set up non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]