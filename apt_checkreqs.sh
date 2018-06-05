#!/bin/bash

installed_pkg=$(apt list --installed)
for pkg in "$@"; do
  if ! echo "$installed_pkg" | grep -q $pkg; then
    echo "missing package: $pkg"
  else
    echo "satisfied: $pkg"
  fi
done
