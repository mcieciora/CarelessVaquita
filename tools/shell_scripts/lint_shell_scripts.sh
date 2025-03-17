#!/bin/bash

RETURN_VALUE=0
ALL_SHELL_FILES=$(find . -name "*.sh")

curl -OL https://github.com/koalaman/shellcheck/releases/download/"$SHELLCHECK_VERSION"/shellcheck-"$SHELLCHECK_VERSION".linux.x86_64.tar.xz
tar xf shellcheck-"$SHELLCHECK_VERSION".linux.x86_64.tar.xz

echo "$ALL_SHELL_FILES"

for SHELL_SCRIPT_NAME in $ALL_SHELL_FILES
do
  echo "Checking: $SHELL_SCRIPT_NAME"
  shellcheck-"$SHELLCHECK_VERSION"/shellcheck "$SHELL_SCRIPT_NAME"
  RETURN_CODE=$?
  if [ $RETURN_CODE -ne 0 ]; then
      echo "$SHELL_SCRIPT_NAME check failed."
      RETURN_VALUE=1
  fi
done

exit "$RETURN_VALUE"
