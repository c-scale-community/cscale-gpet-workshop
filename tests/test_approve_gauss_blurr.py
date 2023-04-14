import pytest
import rioxarray
from pytest_approvaltests_geo import GeoOptions

from cscale_gpet_workshop.gaussian_blurr_pipeline import gauss_blur


@pytest.fixture
def high_freq_raster(approval_geo_input_directory):
    return rioxarray.open_rasterio(
        approval_geo_input_directory / "SIG0-MMEAN_20180101T050937_20180131T170558_VV_MMEAN_E048N012T6_EU500M_V1M0R1_S1AIWGRDH-S1BIWGRDH_TUWIEN.tif")


def test_approve_gaussian_blurr(high_freq_raster, verify_raster_as_geo_tif):
    low_freq = gauss_blur(high_freq_raster, kernel_size=6, sigma=1.5)
    verify_raster_as_geo_tif(low_freq, options=GeoOptions().with_tif_writer(write_compressed))


def write_compressed(file, a) -> None:
    a.rio.to_raster(file, compress='ZSTD')
