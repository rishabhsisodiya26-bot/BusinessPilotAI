# Use official Python lightweight base image
FROM python:3.10-slim

# Set environment variables to optimize Python container runs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (build-essential needed for any compiled C dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to utilize Docker build layer caching
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project code into the container workdir
COPY . .

# Seed the SQLite database inside the image workspace
RUN python database/seed_data.py

# Expose Streamlit default network port
EXPOSE 8501

# Configure Streamlit health checks
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Launch the Streamlit application
ENTRYPOINT ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
