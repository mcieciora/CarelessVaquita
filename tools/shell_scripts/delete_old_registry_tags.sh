#!/bin/bash

CURRENT_DATE=$(date +%s)
echo "CURRENT_DATE: $CURRENT_DATE"

DAYS_TO_KEEP_REGISTRY_IMAGES_POLICY=$1

curl -s -X GET "$REGISTRY_URL/v2/$REGISTRY_REPO/tags/list" > all_tags.json

jq -c '.tags[]' all_tags.json | while read -r TAG; do
  TAG_BLOB_VALUE=$(curl -s -X POST "$REGISTRY_URL/v2/$REGISTRY_REPO/manifests/$TAG" -H "Accept: application/vnd.docker.distribution.manifest.v2+json" | jq .config.digest)
  echo "TAG_BLOB_VALUE: $TAG_BLOB_VALUE"
  TAG_CREATED=$(curl -s "$REGISTRY_URL/v2/$REGISTRY_REPO/blobs/sha256:$TAG_BLOB_VALUE | jq -r .created")
  echo "TAG_CREATED: $TAG_CREATED"
  TAG_CREATED_TIMESTAMP=$(date -d "$TAG_CREATED" +%s)
  echo "TAG_CREATED_TIMESTAMP: $TAG_CREATED_TIMESTAMP"
  DATE_DIFF=$(( (CURRENT_DATE - TAG_CREATED_TIMESTAMP) / 86400 ))
  echo "DATE_DIFF: $DATE_DIFF"
  echo "Processing tag: $TAG which is $DATE_DIFF days old..."

  if [ $DATE_DIFF -ge "$DAYS_TO_KEEP_REGISTRY_IMAGES_POLICY" ]; then
    echo "$TAG is $DATE_DIFF days old. It will be deleted."
    curl -X DELETE "$REGISTRY_URL/v2/$REGISTRY_REPO/manifests/$TAG_BLOB_VALUE"

    RETURN_CODE=$?
    if [ $RETURN_CODE -eq 0 ]; then
      echo "$TAG deleted successfully."
    else
      echo "Could not delete tag: $TAG"
    fi
  fi
done
