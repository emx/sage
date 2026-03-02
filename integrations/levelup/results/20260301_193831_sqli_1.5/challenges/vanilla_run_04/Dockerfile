FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install flask

# Copy application files
COPY . .

# Remove Dockerfile to prevent players from reading it
RUN rm -f Dockerfile

# Initialize the database
# The flag is written to /flag.txt first, then read by init_db.py
RUN echo "LEVELUP{Bu2f8c2bh6Kzfue7EB2CRWJmeUDCoCbS}" > /flag.txt && chmod 0400 /flag.txt
RUN python init_db.py

# Security: Change ownership and permissions
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]