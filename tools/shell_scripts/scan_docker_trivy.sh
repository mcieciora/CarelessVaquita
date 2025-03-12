#!/bin/bash

TAG=$1

echo "Running docker trivy on $TAG image"
docker run --rm aquasec/trivy:"$TRIVY_VERSION" image "$DOCKERHUB_REPO":"$TAG" > scan_trivy_"$TAG".txt
grep "HIGH: 0" scan_trivy_"$TAG".txt
HIGH_VULNERABILITIES=$?
grep "CRITICAL: 0" scan_trivy_"$TAG".txt
CRITICAL_VULNERABILITIES=$?
if [ "$HIGH_VULNERABILITIES" -ne 0 ] || [ "$CRITICAL_VULNERABILITIES" -ne 0 ]; then
  echo "Script failed, because vulnerabilities were found. Please fix them according to given recommendations."
fi
