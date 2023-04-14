import pytest
import xarray as xr
from eotransform_pandas.filesystem.gather import gather_files
from eotransform_pandas.filesystem.naming.geopathfinder_conventions import yeoda_naming_convention
from pytest_approvaltests_geo import GeoOptions

from cscale_gpet_workshop.mmean_pipeline import monthly_mean


@pytest.fixture
def src_data_cube(approval_geo_input_directory):
    df = gather_files(approval_geo_input_directory / "E048N012T3", yeoda_naming_convention, index='datetime_1')
    ds = xr.open_mfdataset(df['filepath'], concat_dim='band', combine='nested').rename_dims(band='time')
    ds['time'] = df.index.to_list()
    return ds


def test_approve_calculating_monthly_means(src_data_cube, verify_raster_as_geo_tif):
    m_mean = monthly_mean(src_data_cube)
    verify_raster_as_geo_tif(m_mean['band_data'], options=GeoOptions().with_tif_writer(write_compressed))


def write_compressed(file, da):
    da.rio.to_raster(file, compress='ZSTD')