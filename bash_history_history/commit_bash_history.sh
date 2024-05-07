#!/usr/bin/env bash

set -e

repo_dpath="${1:-$HOME/.bash_history_history}"

if [ ! -d "$repo_dpath" ]; then
    git init "$repo_dpath"
fi


commit_bash_history ()
{
    git \
        -C "$repo_dpath" \
        commit \
        -m "uptime: $(uptime -p)" \
        bash_history
}


# save changes in potentially dirty tree
commit_bash_history || true

cp ~/.bash_history "$repo_dpath/bash_history"
commit_bash_history
