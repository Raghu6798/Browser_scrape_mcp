FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir \
    fastmcp \
    firecrawl \
    tavily-python \
    rich \
    beautifulsoup4 \
    python-dotenv \
    requests

# Expose the port if needed (optional)
EXPOSE 8080

# Default command
CMD ["python", "main.py"]
