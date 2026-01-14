#!/bin/bash

BRANCH=$1
STATE=$2

CONTEXT="ci/pipeline-passed"
DESCRIPTION="All checks passed"
TARGET_URL="https://github.com/mcieciora/CarelessVaquita/pulls"

PR_NUMBER=$(curl -s -H "Authorization: Bearer $GITHUB_API_TOKEN" \
  "https://api.github.com/repos/$GITHUB_REPO_OWNER/$GITHUB_REPO_NAME/pulls?head=$GITHUB_REPO_OWNER:$BRANCH&state=open" \
  | jq -r '.[0].number')

if [[ "$PR_NUMBER" == "null" || -z "$PR_NUMBER" ]]; then
  echo "No open PR for branch: $BRANCH"
  exit 0
fi

SHA=$(curl -s -H "Authorization: Bearer $GITHUB_API_TOKEN" \
  "https://api.github.com/repos/$GITHUB_REPO_OWNER/$GITHUB_REPO_NAME/pulls/$PR_NUMBER" \
  | jq -r '.head.sha')

RETURN_VALUE=$(curl -s -X POST -H "Authorization: Bearer $GITHUB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"state\": \"$STATE\",
    \"context\": \"$CONTEXT\",
    \"description\": \"$DESCRIPTION\",
    \"target_url\": \"$TARGET_URL\"
  }" \
  "https://api.github.com/repos/$GITHUB_REPO_OWNER/$GITHUB_REPO_NAME/statuses/$SHA" | jq -r '.state')

if [ "$RETURN_VALUE" == "$STATE" ]; then
  echo "Status '$CONTEXT' updated to '$STATE' on PR #$PR_NUMBER"
  exit 0
else
  echo "Could not update #$PR_NUMBER state"
  exit 1
fi
