import argparse
import logging
from pathlib import Path

import xarray as xr
from equi7grid.equi7grid import Equi7Tile, Equi7Grid

from cscale_gpet_workshop.cpu.resample import resample_lonlat_to_equi7


def main():
    parser = argparse.ArgumentParser(description="Resample ERA5-Land surface temperature data to Equi7Tile.")
    parser.add_argument('era5_nc', type=Path, help="NetCDF file containing ERA5-Land surface temperature data.")
    parser.add_argument('tile', type=str, help='long name of the destination tile, i.e. "EU500M_E036N006T6"')
    parser.add_argument('out', type=Path, help="output path to put the GeoTiff stack to")
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    resample_lonlat_to_equi7(xr.open_dataset(args.era5_nc), make_e7tile_from_long_name(args.tile), args.out)


def make_e7tile_from_long_name(name: str) -> Equi7Tile:
    sampling = int(name[2:5])
    return Equi7Grid(sampling).create_tile(name)


if __name__ == "__main__":
    main()
