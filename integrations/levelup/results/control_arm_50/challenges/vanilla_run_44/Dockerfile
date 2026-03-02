FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install flask

# Secure the flag
RUN echo "LEVELUP{JTRKckOudSMfU_y7ldzCIOn08egoh5fW}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database and cleanup
RUN python init_db.py
RUN rm -f Dockerfile

# Set up non-root user
RUN useradd -m ctfuser
RUN chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]