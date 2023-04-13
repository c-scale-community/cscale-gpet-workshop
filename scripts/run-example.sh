#!/bin/bash

project_dir=$(realpath "$(dirname $(dirname "${BASH_SOURCE[0]}"))")
pushd "$project_dir" || exit

mkdir -p out
resample-stl1 resources/stl1_era5land_long_20211111_20211121.nc EU500M_E048N012T6 out

popd || exit