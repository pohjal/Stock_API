pip freeze > requirements.txt : to post new requirements to the txt file

pip install -r requirements.txt : to install requirements

# Database config

you can configure dbconfig.json or environment variable with the db credentials.

For env variables (linux):
export DB_USER=DB_USER_NAME
export DB_PASS=DB_PASSWORD

For dbconfig.json, change values in file.

# Run project locally

## Open poetry shell

poetry shell

## Install requirements

cat requirements.txt | xargs poetry add

## Start server

gunicorn app:app -b 0.0.0.0:5000 --threads 2

## Build docker image

docker build . -t cloudrun-cse-2024-g5-project

## Run docker image

docker run -d -p 127.0.0.1:5000:5000 cloudrun-cse-2024-g5-project

## List docker images and stop one

docker ps
docker stop 2522b0f1a0e7

## Publishing to Google Cloud

Change the last numbers to update the image version
docker tag cloudrun-cse-2024-g5-project:latest europe-north1-docker.pkg.dev/cse-2024-g5-api/cse-2024-g5-api/cloudrun-cse-2024-g5-project-image:1.ADD-NUMBER-HERE

Publish to cloud
docker push europe-north1-docker.pkg.dev/cse-2024-g5-api/cse-2024-g5-api/cloudrun-cse-2024-g5-project-image:1.ADD-NUMBER-HERE

Then you need to install it in cloud
