# Use the official Python image as the base image
FROM python:3.11-slim-buster as builder

# Set environment variables to avoid creating .pyc files and to hide terminal buffering
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies required for Chrome, Chromedriver, and installing Poetry
RUN apt-get update && \
    apt-get install -y wget unzip jq curl libglib2.0-0 libnss3 libnspr4 libxss1 libx11-xcb1 xdg-utils


RUN curl -LO https://github.com/tonymet/gcloud-lite/releases/download/472.0.0/google-cloud-cli-472.0.0-linux-x86_64-lite.tar.gz
RUN tar -zxf *gz

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
COPY pyproject.toml poetry.lock chainlit.md ./
#COPY /public /public
RUN poetry install --no-root --no-dev --no-interaction --no-ansi --no-plugins


# Optionally, install requirements.txt if not all packages are managed by Poetry
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY llm-app-project-26a82e769088.json ./
COPY google-cloud-sdk ./
COPY google-cloud-cli-472.0.0-linux-x86_64-lite.tar.gz ./
COPY download ./download/
COPY .chainlit/config.toml .chainlit/
COPY public ./public/
COPY chroma ./chroma/

# Copy the application code to the container
COPY ./demo_app ./demo_app

# Start a new stage from scratch to create a smaller final image
FROM python:3.11-slim-buster as runtime

# Copy the prebuilt binary files from the builder stage
COPY --from=builder /opt /opt
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app
#COPY --from=builder /public /public
COPY .env /app




# Set up environment variables for the virtual environment
ENV VIRTUAL_ENV="/app/.venv"
ENV PATH="$VIRTUAL_ENV/bin:/root/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# Define the command to run the application
CMD ["bash", "-c", "chainlit run demo_app/main.py"]
