#!/usr/bin/env bash

# Tag image and push to Docker Hub
if [ -z "$TRAVIS_TAG" ]; then
  TRAVIS_TAG="latest"
fi

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
docker tag "$DOCKER_REPO" "$DOCKER_REPO:$TRAVIS_TAG"
docker push "$DOCKER_REPO:$TRAVIS_TAG"

if [ "$TRAVIS_TAG" == "latest" ]; then
  # Download and set up kubectl
  curl -Lo kubectl https://storage.googleapis.com/kubernetes-release/release/v1.7.0/bin/linux/amd64/kubectl
  chmod +x kubectl
  sudo mv kubectl /usr/local/bin/

  kubectl --server="$K8S_SERVER" --token="$K8S_ACCESS_TOKEN" set image deployment/buildly-core buildly-core="buildly/buildly" --namespace=development
fi