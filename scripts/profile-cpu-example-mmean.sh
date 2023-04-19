#!/bin/bash

project_dir=$(realpath "$(dirname $(dirname "${BASH_SOURCE[0]}"))")
pushd "$project_dir" || exit

mkdir -p out
py-spy record --format speedscope -o profile-mmean-cpu.json -- python src/cscale_gpet_workshop/mmean.py resources/E048N012T3/ out

popd || exit