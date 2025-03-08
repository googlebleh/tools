#!/usr/bin/env bash

set -e

docker system prune -f

dotnet nuget locals all --clear || echo "no dotnet nuget"
nuget locals all -clear || echo "no nuget"
# rm -rf ~/.nuget/packages

yes | paru -Scd
