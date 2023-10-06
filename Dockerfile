# Use Python base image
FROM python:3.11-alpine

COPY finance-utils /app/finance-utils

# Create data directory
RUN mkdir /app/data

# Set working directory
WORKDIR /app

# Install required Python packages
RUN pip install pandas StrEnum

# Set entrypoint to run Python script
ENTRYPOINT ["python", "/app/finance-utils/run.py"]