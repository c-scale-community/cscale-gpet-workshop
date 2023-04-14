#!/bin/bash

project_dir=$(realpath "$(dirname $(dirname "${BASH_SOURCE[0]}"))")
pushd "$project_dir" || exit

mkdir -p out
mmean resources/E048N012T3/ out

popd || exit