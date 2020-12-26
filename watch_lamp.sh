#!/bin/sh

while true ; do
  clear
  printf "[%s] Current lamp status:\n" "$(date)"
  ${SHELL-/bin/sh} -c "echo -e '$(cat lamp.txt)'"
  sleep 1
done
