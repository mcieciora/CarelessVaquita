#!/bin/bash

RETURN_VALUE=0
ALL_DOCKERFILES=$(find . -name "*Dockerfile")

echo "$ALL_DOCKERFILES"

for DOCKERFILE_VALUE in $ALL_DOCKERFILES
do
  echo "Checking: $DOCKERFILE_VALUE"
  docker run --rm -i hadolint/hadolint:"$HADOLINT_VERSION" < "$DOCKERFILE_VALUE"
  RETURN_CODE=$?
  if [ $RETURN_CODE -ne 0 ]; then
      echo "$DOCKERFILE_VALUE check failed."
      RETURN_VALUE=1
  fi
done

exit "$RETURN_VALUE"
