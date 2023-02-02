#!/usr/bin/env bash

set -e


wd=/tmp/fun/mail

mkdir -p "$wd"
cd "$wd"

if [ ! -f "$wd/Pipfile" ] || [ ! -f "$wd/Pipfile.lock" ]; then
  pipenv install oauth2token
fi

pipenv run $@
