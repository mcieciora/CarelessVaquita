#!/bin/bash

# shellcheck source=/dev/null
source .env

JENKINS_FILE_CHECK_FILE=$(mktemp XXXXX)
find . -name "*Jenkinsfile" > "$JENKINS_FILE_CHECK_FILE"

echo "Found $(cat "$JENKINS_FILE_CHECK_FILE")"

NUMBER_OF_JENKINS_FILES=$(wc -l "$JENKINS_FILE_CHECK_FILE" | awk '{ print $1 }')

echo "Running Jenkinsfiles linting on $JENKINS_SERVER_HOST"
CURL_LOG_FILE=$(mktemp XXXXX)
cat < "$JENKINS_FILE_CHECK_FILE" | xargs -I {} curl --user "admin_user:password" -X POST -F "jenkinsfile=<{}" "$JENKINS_SERVER_HOST"/pipeline-model-converter/validate > "$CURL_LOG_FILE"

NUMBER_OF_OCCURRENCES=$(grep -c "Jenkinsfile successfully validated." "$CURL_LOG_FILE")

cat "$CURL_LOG_FILE"

rm "$CURL_LOG_FILE"
rm "$JENKINS_FILE_CHECK_FILE"

if [ "$NUMBER_OF_OCCURRENCES" -eq "$NUMBER_OF_JENKINS_FILES" ]; then
  exit 0
else
  exit 1
fi