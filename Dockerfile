# Use the official Python image as the base image
FROM python:3.11-slim-buster as builder

# Set environment variables to avoid creating .pyc files and to hide terminal buffering
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies required for Chrome, Chromedriver, and installing Poetry
RUN apt-get update && \
    apt-get install -y wget unzip jq curl libglib2.0-0 libnss3 libnspr4 libxss1 libx11-xcb1 xdg-utils


# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
# Add Poetry to the PATH explicitly
ENV PATH="/root/.local/bin:${PATH}"

# Create a virtual environment and activate it
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Set the working directory
WORKDIR /app

# Install Python dependencies via Poetry
COPY pyproject.toml poetry.lock rare-daylight-418614-e1907d935d97.json chainlit.md ./
COPY /public /public
RUN poetry install --no-root --no-dev --no-interaction --no-ansi --no-plugins

# Optionally, install requirements.txt if not all packages are managed by Poetry
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install Google Chrome
RUN wget -qO /tmp/versions.json https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json && \
    CHROME_URL=$(jq -r '.channels.Stable.downloads.chrome[] | select(.platform=="linux64") | .url' /tmp/versions.json) && \
    wget -q --continue -O /tmp/chrome-linux64.zip $CHROME_URL && \
    unzip /tmp/chrome-linux64.zip -d /opt/chrome && \
    chmod +x /opt/chrome/chrome-linux64/chrome

# Install Chromedriver
RUN CHROMEDRIVER_URL=$(jq -r '.channels.Stable.downloads.chromedriver[] | select(.platform=="linux64") | .url' /tmp/versions.json) && \
    wget -q --continue -O /tmp/chromedriver-linux64.zip $CHROMEDRIVER_URL && \
    unzip /tmp/chromedriver-linux64.zip -d /opt/chromedriver && \
    chmod +x /opt/chromedriver/chromedriver-linux64/chromedriver

# Clean up to reduce image size
RUN rm /tmp/chrome-linux64.zip /tmp/chromedriver-linux64.zip /tmp/versions.json

# Copy the application code to the container
COPY ./demo_app ./demo_app

# Start a new stage from scratch to create a smaller final image
FROM python:3.11-slim-buster as runtime

# Copy the prebuilt binary files from the builder stage
COPY --from=builder /opt /opt
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app
COPY --from=builder /public /public
COPY .env /app


# Install system dependencies required for Chrome and Chromedriver
RUN apt-get update && apt-get install -y \
    wget \
    libglib2.0-dev \
    libnss3 \
    libnss3-dev \  
    libnspr4 \
    libxcb1 \
    libc6 \  
    libdbus-1-3 \
    libatk1.0-dev \
    libatk-bridge2.0-dev \
    libcups2 \
    libdrm2 \
    libatspi2.0-dev \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libpango1.0-dev \
    libcairo2 \
    libasound2


# Set up environment variables for the virtual environment
ENV VIRTUAL_ENV="/app/.venv"
ENV PATH="$VIRTUAL_ENV/bin:/opt/chromedriver/chromedriver-linux64:/opt/chrome/chrome-linux64:/root/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# Define the command to run the application
CMD ["bash", "-c", "chainlit run demo_app/main.py"]
