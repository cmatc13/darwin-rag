LangChain-Chainlit RAG Application

#### 1. Introduction
This ReadMe details the development, deployment, and maintenance of a Retrieval-Augmented Generation (RAG) application built using LangChain and Chainlit. The application is containerised using Docker and can be deployed locally or on Google Cloud using Cloud Run.

#### 2. Technology Stack
- **LangChain:** A framework for developing applications powered by language models.
- **Chainlit:** A tool for creating chat-based interfaces.
- **Docker:** A containerization platform that ensures consistency across environments.
- **Google Cloud Run:** A serverless container deployment service for scalable cloud deployment.
- **Poetry:** A dependency management and packaging tool for Python projects.

#### 3. Local Development

##### 3.1 Environment Setup
The application leverages Poetry for dependency management. Follow these steps to set up the local development environment:

```bash
poetry install
poetry shell
```

To update dependencies after modifying `pyproject.toml`:

```bash
poetry install
poetry lock
poetry shell
```

##### 3.2 Running the Application
To run the Chainlit server locally:

```bash
chainlit run demo_app/main.py
```

This command initiates the Chainlit server, allowing local testing and development.

#### 4. Docker Implementation

##### 4.1 Building the Docker Image
To containerise the application, build the Docker image with the following commands:

```bash
docker build --force-rm --no-cache -t [IMAGE_NAME]:latest .
DOCKER_BUILDKIT=1 docker build --target=runtime . -t [IMAGE_NAME]:latest
```

These commands create a Docker image tagged as `latest`, ensuring a clean and optimised build process.

##### 4.2 Running the Docker Container
Run the Docker container directly or using `docker-compose`:

```bash
docker run -d --name [IMAGE_NAME] -p 8000:8000 [IMAGE_NAME]
docker-compose up
```

These commands start the container, making the application accessible on port 8000.

#### 5. Google Cloud Deployment

##### 5.1 Prerequisites
Ensure the following are set up:
- **Google Cloud CLI (gcloud)** or **gcloud-lite**
- A Google Cloud project with billing enabled
- Necessary Google Cloud APIs enabled:
  - Cloud Build
  - Cloud Run

##### 5.2 Configuration
Key configuration steps include:
1. Creating a new project.
2. Setting up service accounts with appropriate permissions.
3. Enabling required services.

##### 5.3 Container Registry
Push the Docker image to Google Cloud Artifacts Registry:
1. Create a repository.
2. Configure Docker authentication.
3. Push the container image:

```bash
gcloud auth configure-docker
docker tag [IMAGE_NAME]:latest [YOUR_PROJECT_LOCATION]-docker.pkg.dev/[YOUR_PROJECT_ID]/[REPOSITORY]/[IMAGE_NAME]:latest
docker push [YOUR_PROJECT_LOCATION]-docker.pkg.dev/[YOUR_PROJECT_ID]/[REPOSITORY]/[IMAGE_NAME]:latest
```

##### 5.4 Cloud Run Deployment
Deploy the application using Cloud Run with the following command:

```bash
gcloud run deploy [YOUR_PROJECT_ID] \
  --image=[YOUR_PROJECT_LOCATION]-docker.pkg.dev/[YOUR_PROJECT_ID]/[REPOSITORY]/[IMAGE_NAME]:latest \
  --region=[YOUR_PROJECT_LOCATION] \
  --service-account=[YOUR_SERVICE_ACCOUNT_EMAIL] \
  --port=8000 \
  --memory=2G
```

This command deploys the containerized application, specifying region, service account, port, and memory allocation.

#### 6. Maintenance and Troubleshooting

- For Codespace users: Regularly clean up Docker resources to manage space.
- Use the command `docker system prune` to clean up unused Docker resources.
- Monitor Cloud Run logs to troubleshoot deployment issues:

```bash
gcloud logs read --project=[YOUR_PROJECT_ID] --resource-type=cloud_run_revision
```

#### 7. Conclusion
This RAG application showcases a robust implementation using modern tools and cloud deployment techniques. It offers flexibility in deployment options, leveraging LangChain and Chainlit for building interactive, AI-powered chat interfaces. Docker ensures consistency across different environments, while Google Cloud deployment provides scalability and ease of management. Continuous improvement and monitoring will ensure the application's effectiveness and performance in production environments.

### Appendix: Commands and Configurations

#### Poetry Commands
- **Install dependencies:** `poetry install`
- **Activate virtual environment:** `poetry shell`
- **Update dependencies:** `poetry lock && poetry install`

#### Docker Commands
- **Build image:** `docker build --force-rm --no-cache -t [IMAGE_NAME]:latest .`
- **Run container:** `docker run -d --name [IMAGE_NAME] -p 8000:8000 [IMAGE_NAME]`
- **Push to registry:** `docker push [YOUR_PROJECT_LOCATION]-docker.pkg.dev/[YOUR_PROJECT_ID]/[REPOSITORY]/[IMAGE_NAME]:latest`

#### Google Cloud Commands
- **Configure Docker authentication:** `gcloud auth configure-docker`
- **Deploy to Cloud Run:** `gcloud run deploy [YOUR_PROJECT_ID] --image=[IMAGE] --region=[YOUR_PROJECT_LOCATION] --service-account=[YOUR_SERVICE_ACCOUNT_EMAIL] --port=8000 --memory=2G`
