#!/bin/bash

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR | sed 's| |\\ |g')

echo "$STAGED_FILES" | grep -w -q "Jenkinsfile"
IS_JENKINSFILE_STAGED=$?

echo "$STAGED_FILES" | grep -w -q "tools/jenkins/CarelessVaquitaTestJenkinsfile"
IS_TEMPLATE_STAGES=$?

if [ "$IS_JENKINSFILE_STAGED" -eq 0 ] | [ "$IS_TEMPLATE_STAGES" -eq 0 ]; then
  echo "Changes in Jenkinsfile or template detected. Running test jenkinsfile generation."
  python tools/python/generate_test_jenkinsfile.py "$(pwd)"
else
  echo "No changes detected."
  exit 0
fi
