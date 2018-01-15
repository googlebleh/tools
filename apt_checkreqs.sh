#!/bin/bash

for pkg in "$@"; do
  if ! apt list --installed | grep -q $pkg; then
    echo "Missing package: $pkg"
  fi
done
