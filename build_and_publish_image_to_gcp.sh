#!/bin/bash
set -e

# === CONFIGURATION ===
PROJECT_ID="finitec-python-developer"
REGION="europe-west3"
REPO_NAME="fastapi-repo"
IMAGE_NAME="fastapi-app"
TAG="v7"
ENVIRONMENT="prod"

# === ENABLE REQUIRED SERVICE ===
echo "Enabling Artifact Registry API..."
gcloud services enable artifactregistry.googleapis.com --project "${PROJECT_ID}"

# === CREATE REPOSITORY IF NOT EXISTS ===
if ! gcloud artifacts repositories describe "${REPO_NAME}" \
    --location="${REGION}" \
    --project="${PROJECT_ID}" >/dev/null 2>&1; then
  echo "📦 Creating Artifact Registry repository '${REPO_NAME}'..."
  gcloud artifacts repositories create "${REPO_NAME}" \
    --repository-format=docker \
    --location="${REGION}" \
    --description="Repository for FastAPI Docker images" \
    --project="${PROJECT_ID}"
else
  echo "Repository '${REPO_NAME}' already exists."
fi

# === AUTHENTICATE DOCKER TO ARTIFACT REGISTRY ===
echo "🔐 Configuring Docker authentication for Artifact Registry..."
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

# === BUILD DOCKER IMAGE ===
FULL_IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${TAG}"

echo "Building Docker image '${FULL_IMAGE_NAME}'..."
docker build --platform linux/amd64 -f Dockerfile."${ENVIRONMENT}" -t "${FULL_IMAGE_NAME}" .

# === PUSH IMAGE TO ARTIFACT REGISTRY ===
echo "Pushing Docker image to Artifact Registry..."
docker push "${FULL_IMAGE_NAME}"

echo "Image successfully pushed to:"
echo "${FULL_IMAGE_NAME}"