import numpy as np
import pytest
import rioxarray
from eotransform.utilities.profiling import PerformanceClock
from numpy._typing import NDArray
from pytest_approvaltests_geo import GeoOptions

from cscale_gpet_workshop.cpu.gaussian_blur import gauss_blur


@pytest.fixture
def high_freq_raster(approval_geo_input_directory):
    return rioxarray.open_rasterio(
        approval_geo_input_directory / "SIG0-MMEAN_20180101T050937_20180131T170558_VV_MMEAN_E048N012T6_EU500M_V1M0R1_S1AIWGRDH-S1BIWGRDH_TUWIEN.tif",
        mask_and_scale=True)


def test_approve_gaussian_blurr(high_freq_raster, verify_raster_as_geo_tif):
    clock = PerformanceClock()

    with clock.measure():
        low_freq = gauss_blur(high_freq_raster, kernel_size=6, sigma=1.5)

    print(f"\nruntime: {clock.total_measures}s")
    verify_raster_as_geo_tif(low_freq, options=GeoOptions().with_tif_writer(write_compressed)
                             .with_tolerance(rel_tol=0.1, abs_tol=0.1))


def write_compressed(file, a) -> None:
    a.rio.to_raster(file, compress='ZSTD')

from numba import cuda

@cuda.jit
def add_vec_cuda_kernel(a, b, out):
    out[cuda.threadIdx.x] = a[cuda.threadIdx.x] + b[cuda.threadIdx.x]

def add_vec(a: NDArray, b: NDArray) -> NDArray:
    out = cuda.device_array(a.shape, dtype=a.dtype)
    add_vec_cuda_kernel[1, 3](cuda.to_device(a), cuda.to_device(b), out)
    return out.copy_to_host()

def test_cuda_hello_world():
    a = np.full((3,), 2)
    b = np.full((3,), 3)
    np.testing.assert_array_equal(add_vec(a, b), np.full((3,), 5))