#!/bin/bash

PROTECTED_TAGS=("latest" "merge_bot" "test_image")
CURRENT_DATE=$(date +%s)

echo "{'username': $USERNAME, 'password': $PASSWORD}" > token_creds.json

curl -s -X POST https://hub.docker.com/v2/users/login/ -d @token_creds.json -H "Content-Type: application/json" > token.json

TOKEN=$(jq -r '.token' token.json)

curl https://registry.hub.docker.com/v2/repositories/"$DOCKERHUB_REPO"/tags > all_tags.json

jq -c '.results[]' all_tags.json | while read -r TAG; do
  TAG_NAME=$(echo "$TAG" | jq -r '.name')
  TAG_LAST_PULLED=$(echo "$TAG" | jq -r '.tag_last_pulled')
  TAG_LAST_PULLED_TIMESTAMP=$(date -d "$TAG_LAST_PULLED" +%s)
  DATE_DIFF=$(( (CURRENT_DATE - TAG_LAST_PULLED_TIMESTAMP) / 86400 ))

  if [ $DATE_DIFF -gt "$DAYS_TO_KEEP_DOCKERHUB_IMAGES_POLICY" ] && ! [[ "${PROTECTED_TAGS[*]}" =~ $TAG_NAME ]]; then
    echo "$TAG_NAME is $DATE_DIFF days old. It will be deleted."
    curl --fail -X DELETE -H "Authorization: JWT $TOKEN" "https://hub.docker.com/v2/repositories/$DOCKERHUB_REPO/tags/$TAG_NAME/"

    RETURN_CODE=$?
    if [ $RETURN_CODE -eq 0 ]; then
      echo "$TAG_NAME deleted successfully."
    else
      echo "Could not delete tag: $TAG_NAME"
    fi
  fi
done
