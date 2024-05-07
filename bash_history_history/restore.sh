#!/usr/bin/env bash

set -ex

git_rootdir="$(git rev-parse --show-toplevel)"
cp "$git_rootdir/bash_history" ~/.bash_history
