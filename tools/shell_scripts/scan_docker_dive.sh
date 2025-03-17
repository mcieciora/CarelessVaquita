#!/bin/bash

TAG=$1

echo "Running docker dive on $TAG image"
docker run --rm -u root -v /var/run/docker.sock:/var/run/docker.sock wagoodman/dive:"$DIVE_VERSION" --ci "$DOCKERHUB_REPO":"$TAG" > scan_dive_"$TAG".txt
grep "Failed:0" scan_dive_"$TAG".txt
HIGH_VULNERABILITIES=$?
if [ "$HIGH_VULNERABILITIES" -ne 0 ]; then
  echo "Script failed, because vulnerabilities were found. Please fix them according to given recommendations."
fi
