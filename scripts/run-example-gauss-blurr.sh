#!/bin/bash

project_dir=$(realpath "$(dirname $(dirname "${BASH_SOURCE[0]}"))")
pushd "$project_dir" || exit

mkdir -p out
resample-stl1 resources/SIG0-MMEAN_20180101T050937_20180131T170558_VV_MMEAN_E048N012T3_EU020M_V1M0R1_S1AIWGRDH-S1BIWGRDH_TUWIEN.tif out/blurred.tif --kernel-size 25 --sigma 7

popd || exit