#!/bin/bash

TAG_NAME=$1
RELEASE_DESC=$2
PRE_RELEASE_VALUE=$3

curl -X POST "https://api.github.com/repos/$GITHUB_REPO_OWNER/$GITHUB_REPO_NAME/releases" \
  -H "Authorization: token $GITHUB_API_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  --data-binary @- << EOF
  {
    "tag_name": "$TAG_NAME",
    "name": "$RELEASE_DESC",
    "prerelease": $PRE_RELEASE_VALUE,
    "make_latest": $PRE_RELEASE_VALUE
  }
EOF

RETURN_CODE=$?

if [ $RETURN_CODE -eq 0 ]; then
  echo "$TAG_NAME created successfully."
else
  echo "Could not create tag: $TAG_NAME"
  exit 1
fi
