#!/bin/bash

project_dir=$(realpath "$(dirname $(dirname "${BASH_SOURCE[0]}"))")
pushd "$project_dir" || exit

mkdir -p out
nsys profile -o profile-gauss-blur-gpu gauss-blur resources/SIG0-MMEAN_20180101T050937_20180131T170558_VV_MMEAN_E048N012T3_EU020M_V1M0R1_S1AIWGRDH-S1BIWGRDH_TUWIEN.tif out/blurred.tif --kernel-size 25 --sigma 7

popd || exit