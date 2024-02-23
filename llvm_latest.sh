#!/usr/bin/env bash

set -ex

curl -s https://api.github.com/repos/llvm/llvm-project/releases/latest \
	| jq -r ".assets[].browser_download_url" \
	| grep -E "llvm-project-[0-9.]+\.src\.tar\.xz$" \
	| xargs curl -L \
	| tar -xJf -

src_glob=llvm-project-*/llvm
build_dpath=build-llvm-project
install_prefix="$HOME/.local"
cmake \
	-S $src_glob \
	-B "$build_dpath" \
	-G Ninja \
	-DLLVM_PARALLEL_LINK_JOBS=2 \
	-DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra" \
	-DCMAKE_BUILD_TYPE=Release
cmake --build "$build_dpath" --parallel 32
cmake --install "$build_dpath" "--prefix=$install_prefix"

rm -rf $src_glob "$build_dpath"
