#!/usr/bin/env bash
docker --version  # document the version travis is using
pip install --user awscli # install aws cli w/o sudo
export PATH=$PATH:$HOME/.local/bin # put aws in the path
eval $(aws ecr get-login --region us-west-2) #needs AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY envvars
docker build -t buildly-core .
docker tag buildly-core:latest 684870619712.dkr.ecr.us-west-2.amazonaws.com/transparent-path/buildly-core:latest
docker push 684870619712.dkr.ecr.us-west-2.amazonaws.com/transparent-path/buildly-core:latest
