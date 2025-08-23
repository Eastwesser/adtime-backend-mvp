#!/bin/bash

# Pull latest images
docker-compose pull

# Recreate containers
docker-compose up -d

# Cleanup old images
docker image prune -af

# Check status
docker-compose ps