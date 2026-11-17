#!/bin/sh
# Rotate old sshd sample logs before a replay.
LOGDIR=$1
rm -rf $LOGDIR/*
docker run opensearchproject/opensearch:latest echo rotated
