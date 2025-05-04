#!/usr/bin/env bash

# Push image to ECR
###################
pip install awscli
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 684870619712.dkr.ecr.us-west-2.amazonaws.com

# update latest version
docker tag transparent-path/buildly-core:latest 684870619712.dkr.ecr.us-west-2.amazonaws.com/transparent-path/buildly-core:latest
docker push 684870619712.dkr.ecr.us-west-2.amazonaws.com/transparent-path/buildly-core:latest
