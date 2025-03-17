#!/bin/bash

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR | sed 's| |\\ |g')

echo "$STAGED_FILES" | grep -w "Jenkinsfile"
IS_JENKINSFILE_STAGED=$?

echo "$STAGED_FILES" | grep "Template"
IS_TEMPLATE_STAGES=$?

if [ "$IS_JENKINSFILE_STAGED" -eq 0 ] || [ "$IS_TEMPLATE_STAGES" -eq 0 ]; then
  echo "Changes in Jenkinsfile or template detected. Running test jenkinsfile generation."
  python tools/python/generate_test_jenkinsfile.py "$(pwd)"
  git add -f "Jenkinsfile" && git add -f "tools/jenkins/ParametrizedTestJenkinsfile"
else
  echo "No changes detected."
  exit 0
fi