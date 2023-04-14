import argparse
import logging
from pathlib import Path

import xarray as xr
from eotransform_pandas.filesystem.gather import gather_files
from eotransform_pandas.filesystem.naming.geopathfinder_conventions import yeoda_naming_convention
from pandas import DataFrame
from xarray import DataArray

from cscale_gpet_workshop.mmean_pipeline import monthly_mean


def main():
    parser = argparse.ArgumentParser(description="Calculate monthly means from a stack of GeoTiffs data-cube.")
    parser.add_argument('tiff_stack', type=Path, help="Path to folder containing stack of GeoTiffs")
    parser.add_argument('out', type=Path, help="output path to put the monthly mean GeoTiff stack")
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    df = gather_files(args.tiff_stack, yeoda_naming_convention, index='datetime_1')
    monthly_mean(load_data_cube(df), args.out)


def load_data_cube(df: DataFrame) -> DataArray:
    ds = xr.open_mfdataset(df['filepath'], concat_dim='band', combine='nested').rename_dims(band='time')
    ds['time'] = df.index.to_list()
    return ds['band_data']


if __name__ == "__main__":
    main()
