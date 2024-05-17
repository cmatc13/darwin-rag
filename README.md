<h1 align="center">
📖 Lano LLM app using Langchain, Chainlit and Docker Deployment
</h1>


## 🔧 Features

- Configured with `openai` API
- A ChatBot using LangChain and Chainlit
- Docker Support
- Deployment on Google Cloud using `Cloud Run`

> Heavily influenced by repository:  https://github.com/amjadraza/langchain-chainlit-docker-deployment-template


## 💻 Running Locally

1. Clone the repository📂

```bash
git clone https://github.com/cmatc13/lano-llm-app
```

2. Install dependencies with [Poetry](https://python-poetry.org/) and activate virtual environment🔨

```bash
poetry install
poetry shell
```

3. Run the Chainlit server🚀

```bash
chainlit run demo_app/main.py
```

Run App using Docker
--------------------

for codespace you may run out of space. occasionally use to clean up containers etc. 
docker system prune 

to see space on codespace
df -h

remove all containers
docker container prune -f

remove image
docker rmi <image id>

build the docker image without cache
docker build --force-rm --no-cache -t [IMAGE_NAME]:latest .


run a container in bash so you can be inside the container and find files
docker run -it <image id> /bin/bash

Build the docker container and view the logs of the build in docker_build.log file (auto created)
docker  build . -t [IMAGE_NAME]:latest > docker_build.log 2>&1

and without cache
docker  build . -t [IMAGE_NAME]:latest --no-cache > docker_build.log 2>&1

run a temporary cntainer for testing
docker run --rm lano-llm-app

To generate Image with `DOCKER_BUILDKIT`, follow below command
```DOCKER_BUILDKIT=1 docker build --target=runtime . -t [IMAGE_NAME]:latest```

1. Run the docker container directly 
``docker run -d --name [IMAGE_NAME] -p 8000:8000 [IMAGE_NAME] ``


2. Run the docker container using docker-compose (Recommended)
``docker-compose up``


Deploy App on Google Cloud using Cloud Run (RECOMMENDED)
--------------------------------------------------------
This app can be deployed on Google Cloud using Cloud Run following below steps.

## Prerequisites

Google's gcloud CLI distribution is bloated with unnecessary dependencies including a complete python3 installation and large anthos binary. This results in slower instance boot times, and costly storage & transfer fees
Reference: https://github.com/tonymet/gcloud-lite

Google's gcloud CLI distribution
#curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-474.0.0-linux-x86_64.tar.gz
#tar -xf google-cloud-cli-474.0.0-linux-x86_64.tar.gz

GCloud-Lite is a distribution of the CLI that strips these unnessary dependencies to reduce the size by > 75%
GCloud-Lite
curl -LO https://github.com/tonymet/gcloud-lite/releases/download/472.0.0/google-cloud-cli-472.0.0-linux-x86_64-lite.tar.gz
tar -zxf *gz

./google-cloud-sdk/install.sh


Main steps to Deploy
Initialise & Configure the App
First create a project in GCP console

gcloud auth login
gcloud auth list
# for new project
gcloud app create --project=[YOUR_PROJECT_ID]
gcloud config set project [YOUR_PROJECT_ID]
#gcloud config set project llm-app-project
Provide billing account for this project by running gcloud beta billing accounts list OR you can do it manually from the GCP console.

# for new project
Enable Services for the Project: We have to enable services for Cloud Run using below set of commands
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
#Create Service Accounts with Permissions

gcloud iam service-accounts create [YOUR_PROJECT_ID] \
    --display-name="[YOUR_PROJECT_ID]"
e.g.
gcloud iam service-accounts create lano-llm-app \
    --display-name="lano-llm-app"

gcloud projects add-iam-policy-binding [YOUR_PROJECT_ID] \
    --member="serviceAccount:[YOUR_SERVICE_ACCOUNT_EMAIL]" \
    --role="roles/run.invoker"    

e.g.
gcloud projects add-iam-policy-binding llm-app-project \
    --member="serviceAccount:lano-llm-app@llm-app-project.iam.gserviceaccount.com" \
    --role="roles/run.invoker"	

gcloud projects add-iam-policy-binding llm-app-project \
    --member="serviceAccount:[YOUR_SERVICE_ACCOUNT_EMAIL]" \
    --role="roles/serviceusage.serviceUsageConsumer"

gcloud projects add-iam-policy-binding [YOUR_PROJECT_ID] \
    --member="serviceAccount:[YOUR_SERVICE_ACCOUNT_EMAIL]" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding [YOUR_PROJECT_ID] \
    --member="serviceAccount:[YOUR_SERVICE_ACCOUNT_EMAIL]" \
    --role="roles/storage.objectViewer"

    
# Check the artifacts location
gcloud artifacts locations list
# Generate Docker with Region
DOCKER_BUILDKIT=1 docker build --target=runtime . -t [YOUR_PROJECT_LOCATION]-docker.pkg.dev/[YOUR_PROJECT_ID]/clapp/[YOUR_DOCKER_IMAGE]:latest


# Push Docker to Artifacts Registry
# Create a repository clapp
gcloud artifacts repositories create clapp \
    --repository-format=docker \
    --location=[YOUR_PROJECT_LOCATION] \
    --description="A Langachain Chainlit LLM App" \
    --async
    
# Assign authuntication
gcloud auth configure-docker [YOUR_PROJECT_LOCATION]-docker.pkg.dev

# Push the Container to Repository
docker images
docker push [YOUR_PROJECT_LOCATION]-docker.pkg.dev/[YOUR_PROJECT_ID]/clapp/[YOUR_PROJECT_ID]:latest


# Deploy the App using Cloud Run

gcloud run deploy [YOUR_PROJECT_ID] --image=[YOUR_PROJECT_LOCATION]-docker.pkg.dev/[YOUR_PROJECT_ID]/clapp/[YOUR_PROJECT_ID]:latest \
    --region=[YOUR_PROJECT_LOCATION] \
    --service-account=[YOUR_SERVICE_ACCOUNT_EMAIL] \
    --port=8000 \
    --memory=2G

