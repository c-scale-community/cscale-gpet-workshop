import pytest
import xarray as xr
from eotransform_pandas.filesystem.gather import gather_files
from eotransform_pandas.filesystem.naming.geopathfinder_conventions import yeoda_naming_convention

from cscale_gpet_workshop.cpu.mmean import monthly_mean


@pytest.fixture
def src_data_cube(approval_geo_input_directory):
    df = gather_files(approval_geo_input_directory / "E048N012T6", yeoda_naming_convention, index='datetime_1')
    ds = xr.open_mfdataset(df['filepath'], concat_dim='band', combine='nested').rename_dims(band='time')
    ds['time'] = df.index.to_list()
    return ds['band_data']


def test_approve_calculating_monthly_means(src_data_cube, out_put, verify_geo_tif):
    monthly_mean(src_data_cube, out_put)
    verify_geo_tif(next(out_put.glob("*.tif")))
