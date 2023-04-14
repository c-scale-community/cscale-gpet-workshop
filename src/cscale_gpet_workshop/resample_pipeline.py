from pathlib import Path
from typing import Tuple

import pandas as pd
from affine import Affine
from equi7grid.equi7grid import Equi7Tile
from geopathfinder.naming_conventions.yeoda_naming import YeodaFilename
from pyresample import SwathDefinition, AreaDefinition, kd_tree
from xarray import Dataset, DataArray


def resample_lonlat_to_equi7(src_ds: Dataset, dst_tile: Equi7Tile, out_path: Path) -> None:
    src_ds = src_ds.stack(lonlat=['longitude', 'latitude'])
    src_swath = SwathDefinition(lons=src_ds.longitude, lats=src_ds.latitude)
    dst_area = AreaDefinition(dst_tile.name, "", "proj_id", dst_tile.core.projection.wkt, dst_tile.x_size_px,
                              dst_tile.y_size_px, extent_of_e7tile(dst_tile))
    tile_transform = Affine.from_gdal(*dst_tile.geotransform())
    grid, tile = dst_tile.name.split('_')
    yeoda_fields = dict(var_name='ST1', grid_name=grid, tile_name=tile, sensor_field='ERA5L')

    src_stl1 = src_ds['stl1']
    for t in src_stl1.time:
        ts = pd.to_datetime(t.item())
        resampled = kd_tree.resample_gauss(src_swath, src_stl1.sel(time=ts).values, dst_area,
                                           radius_of_influence=10000, sigmas=9e3)
        yeoda_fields['datetime_1'] = ts
        smart_name = YeodaFilename(yeoda_fields)
        da = DataArray(resampled, dims=['y', 'x']).rio.write_transform(tile_transform).rio.write_crs(dst_area.proj_str)
        da = da.rio.set_encoding(dict(dtype='int16', _FillValue=-9999, scale_factor=0.01))
        da.rio.to_raster(out_path / str(smart_name), compress='ZSTD')


def extent_of_e7tile(tile: Equi7Tile) -> Tuple[float, float, float, float]:
    return tile.llx, tile.lly, tile.llx + tile.core.tile_xsize_m, tile.lly + tile.core.tile_ysize_m
