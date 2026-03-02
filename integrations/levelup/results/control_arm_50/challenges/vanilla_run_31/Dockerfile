FROM python:3.12-slim

WORKDIR /app

# Install flask
RUN pip install --no-cache-dir flask

# Copy application files
COPY . .

# Initialize the database as root (to read /flag.txt)
RUN echo "LEVELUP{8IC7n4bfHHZiJiIM_IOU7nP6WeXDH5hL}" > /flag.txt && chmod 0400 /flag.txt
RUN python init_db.py
RUN rm -f Dockerfile /flag.txt

# Set up non-root user
RUN useradd -m ctfuser
RUN chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]