<h1 align="center">
📖 LangChain-Chainlit-Docker-Deployment App Template
</h1>

![UI](ui.PNG?raw=true)


## 🔧 Features

- Basic Skeleton App configured with `openai` API
- A ChatBot using LangChain and Chainlit
- Docker Support with Optimisation Cache etc
- Deployment on Google Cloud App Engine
- Deployment on Google Cloud using `Cloud Run`

> Reference repository: https://github.com/cmatc13/langchain-chainlit-docker-deployment-template

This repo contains an `main.py` file which has a template for a chatbot implementation.

## Adding your chain
To add your chain, you need to change the `load_chain` function in `main.py`.
Depending on the type of your chain, you may also need to change the inputs/outputs that occur later on.


## 💻 Running Locally

1. Clone the repository📂

```bash
git clone https://github.com/cmatc13/langchain-chainlit-docker-deployment-template
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
This project includes `Dockerfile` to run the app in Docker container. In order to optimise the Docker Image
size and building time with cache techniques, I have follow tricks in below Article 
https://medium.com/@albertazzir/blazing-fast-python-docker-builds-with-poetry-a78a66f5aed0


for codespace you may run out of space. try 
docker system prune

to see space on codespace
df -h

remove all containers
docker container prune -f

remove image
docker rmi <image id>

docker build --force-rm --no-cache -t langchain-chainlit-chat-app:latest .


Build the docker container

``docker  build . -t langchain-chainlit-chat-app:latest``

run the docker image as a container in bash so you can be inside the container and find files
docker run -it <image id> /bin/bash


Build the docker container and view the logs of the build in docker_build.log file (auto created)

docker  build . -t langchain-chainlit-chat-app:latest > docker_build.log 2>&1

and without cache
docker  build . -t langchain-chainlit-chat-app:latest --no-cache > docker_build.log 2>&1



To generate Image with `DOCKER_BUILDKIT`, follow below command

```DOCKER_BUILDKIT=1 docker build --target=runtime . -t langchain-chainlit-chat-app:latest```

1. Run the docker container directly 

``docker run -d --name langchain-chainlit-chat-app -p 8000:8000 langchain-chainlit-chat-app ``

2. Run the docker container using docker-compose (Recommended)

``docker-compose up``


Deploy App on Google App Engine
--------------------------------
This app can be deployed on Google App Engine following below steps.

## Prerequisites

Follow below guide on basic Instructions.
[How to deploy Streamlit apps to Google App Engine](https://dev.to/whitphx/how-to-deploy-streamlit-apps-to-google-app-engine-407o)

We added below tow configurations files 

1. `app.yaml`: A Configuration file for `gcloud`
2. `.gcloudignore` : Configure the file to ignore file / folders to be uploaded

I have adopted `Dockerfile` to deploy the app on GCP APP Engine.

1. Initialise & Configure the App

``gcloud app create --project=[YOUR_PROJECT_ID]``

2. Deploy the App using

``gcloud app deploy``

3. Access the App using 

https://langchain-chat-app-ex6cbrefpq-ts.a.run.app/


Deploy App on Google Cloud using Cloud Run (RECOMMENDED)
--------------------------------------------------------
This app can be deployed on Google Cloud using Cloud Run following below steps.

## Prerequisites

Follow below guide on basic Instructions.
[How to deploy Streamlit apps to Google App Engine](https://dev.to/whitphx/how-to-deploy-streamlit-apps-to-google-app-engine-407o)

https://cloud.google.com/sdk/docs/install#linux

curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-474.0.0-linux-x86_64.tar.gz

tar -xf google-cloud-cli-474.0.0-linux-x86_64.tar.gz

./google-cloud-sdk/install.sh


Main steps to Deploy 🚀
Initialise & Configure the App
First create a project in GCP console

gcloud auth login
gcloud auth list
gcloud app create --project=[YOUR_PROJECT_ID]
gcloud config set project [YOUR_PROJECT_ID]
Provide billing account for this project by running gcloud beta billing accounts list OR you can do it manually from the GCP console.

Enable Services for the Project: We have to enable services for Cloud Run using below set of commands
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
#Create Service Accounts with Permissions
gcloud iam service-accounts create langchain-app-cr \
    --display-name="langchain-app-cr"

gcloud projects add-iam-policy-binding [YOUR_PROJECT_ID] \
    --member="serviceAccount:lano-ilo-app-service-account@rare-daylight-418614.iam.gserviceaccount.com" \
    --role="roles/run.invoker"    

gcloud projects add-iam-policy-binding [YOUR_PROJECT_ID] \
    --member="serviceAccount:lano-ilo-app-service-account@rare-daylight-418614.iam.gserviceaccount.com" \
    --role="roles/serviceusage.serviceUsageConsumer"


gcloud projects add-iam-policy-binding [YOUR_PROJECT_ID] \
    --member="serviceAccount:lano-ilo-app-service-account@rare-daylight-418614.iam.gserviceaccount.com" \
    --role="roles/run.admin"


    
# Check the artifacts location
gcloud artifacts locations list
# Generate Docker with Region
DOCKER_BUILDKIT=1 docker build --target=runtime . -t europe-west6-docker.pkg.dev/[YOUR_PROJECT_ID]/clapp/[YOUR_DOCKER_IMAGE]:latest
# Push Docker to Artifacts Registry
# Create a repository clapp
gcloud artifacts repositories create clapp \
    --repository-format=docker \
    --location=europe-west6 \
    --description="A Langachain Chainlit App" \
    --async
# Assign authuntication
gcloud auth configure-docker europe-west6-docker.pkg.dev

# Push the Container to Repository
docker images
docker push europe-west6-docker.pkg.dev/[YOUR_PROJECT_ID]/clapp/langchain-chainlit-chat-app:latest
# Deploy the App using Cloud Run
gcloud run deploy langchain-cl-chat-with-csv-app --image=europe-west6-docker.pkg.dev/langchain-cl-chat-with-csv/clapp/langchain-chainlit-chat-app:latest \
    --region=europe-west6 \
    --service-account=langchain-app-cr@langchain-cl-chat-with-csv.iam.gserviceaccount.com \
    --port=8000

gcloud run deploy lano-llm-app --image=europe-west6-docker.pkg.dev/rare-daylight-418614/clapp/langchain-chainlit-chat-app:latest \
    --region=europe-west6 \
    --service-account=lano-ilo-app-service-account@rare-daylight-418614.iam.gserviceaccount.com \
    --port=8000 \
    --memory=2G











We added below tow configurations files 

1. `cloudbuild.yaml`: A Configuration file for `gcloud`
2. `.gcloudignore` : Configure the file to ignore file / folders to be uploaded

we are going to use `Dockerfile` to deploy the app using Google Cloud Run.

1. Initialise & Configure the Google Project using Command Prompt

`gcloud app create --project=[YOUR_PROJECT_ID]`

2. Enable Services for the Project

```
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
```

3. Create Service Account

```
gcloud iam service-accounts create langchain-app-cr \
    --display-name="langchain-app-cr"

gcloud projects add-iam-policy-binding langchain-chat \
    --member="serviceAccount:langchain-app-cr@langchain-chat.iam.gserviceaccount.com" \
    --role="roles/run.invoker"

gcloud projects add-iam-policy-binding langchain-chat \
    --member="serviceAccount:langchain-app-cr@langchain-chat.iam.gserviceaccount.com" \
    --role="roles/serviceusage.serviceUsageConsumer"

gcloud projects add-iam-policy-binding langchain-chat \
    --member="serviceAccount:langchain-app-cr@langchain-chat.iam.gserviceaccount.com" \
    --role="roles/run.admin"
``` 

4. Generate the Docker

`DOCKER_BUILDKIT=1 docker build --target=runtime . -t australia-southeast1-docker.pkg.dev/langchain-chat/clapp/langchain-chainlit-chat-app:latest`

5. Push Image to Google Artifact's Registry

Create the repository with name `clapp`

```
gcloud artifacts repositories create clapp \
    --repository-format=docker \
    --location=australia-southeast1 \
    --description="A Langachain Chainlit App" \
    --async
```

Configure-docker 

`gcloud auth configure-docker australia-southeast1-docker.pkg.dev`

In order to push the `docker-image` to Artifact registry, first create app in the region of choice. 

Check the artifacts locations

`gcloud artifacts locations list`



Once ready, let us push the image to location

`docker push australia-southeast1-docker.pkg.dev/langchain-chat/clapp/langchain-chainlit-chat-app:latest`

6. Deploy using Cloud Run

Once image is pushed to Google Cloud Artifacts Registry. Let us deploy the image.

```
gcloud run deploy langchain-chat-app --image=australia-southeast1-docker.pkg.dev/langchain-chat/clapp/langchain-chainlit-chat-app:latest \
    --region=australia-southeast1 \
    --service-account=langchain-app-cr@langchain-chat.iam.gserviceaccount.com \
    --port=8000 \
    --memory=2GB
```

7. Test the App Yourself

You can try the app using below link 

https://langchain-chat-app-ex6cbrefpq-ts.a.run.app/


## Report Feedbacks

As `langchain-chainlit-docker-deployment-template` is a template project with minimal example. Report issues if you face any. 

## DISCLAIMER

This is a template App, when using with openai_api key, you will be charged a nominal fee depending
on number of prompts etc.

# To view the current memory limit settings for your Cloud Run service:
gcloud run services describe [SERVICE]

