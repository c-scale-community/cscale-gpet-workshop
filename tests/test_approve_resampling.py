import pytest
import xarray as xr
from eotransform_pandas.filesystem.gather import gather_files
from eotransform_pandas.filesystem.naming.geopathfinder_conventions import yeoda_naming_convention
from equi7grid.equi7grid import Equi7Grid

from cscale_gpet_workshop.resample_pipeline import resample_lonlat_to_equi7


@pytest.fixture
def era5l_stl1(approval_geo_input_directory):
    return xr.open_dataset(approval_geo_input_directory / "stl1_era5land_20211111.nc")


def test_approve_resampled_era5_land_data(era5l_stl1, verify_data_frame_using, verify_geo_tif, out_put):
    resample_lonlat_to_equi7(era5l_stl1, Equi7Grid(500).create_tile("EU500M_E048N012T6"), out_put)
    resampled_data_cube = gather_files(out_put, yeoda_naming_convention)
    verify_data_frame_using(verify_geo_tif, 'datetime_1')(resampled_data_cube)
