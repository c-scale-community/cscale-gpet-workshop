from typing import Dict

import numpy as np
from numpy._typing import NDArray
from scipy.signal import convolve2d
from xarray import DataArray


def gauss_blur(raster: DataArray, kernel_size: int, sigma: float) -> DataArray:
    kernel = make_gauss_kernel(kernel_size, sigma)
    da = DataArray(convolve2d(raster.values[0], kernel, mode='same', boundary='symm')[np.newaxis, ...],
                      coords=raster.coords, dims=raster.dims, attrs=raster.attrs, name=raster.name)
    maybe_del(da.attrs, 'dtype')
    maybe_del(da.attrs, '_FillValue')
    maybe_del(da.attrs, 'scale_factor')
    return da.rio.update_encoding(dict(dtype='int16', _FillValue=-9999, scale_factor=0.1))


def maybe_del(attrs: Dict, key: str):
    if key in attrs:
        del attrs[key]


def make_gauss_kernel(size: int, sigma: float) -> NDArray:
    size = size // 2
    x, y = np.mgrid[-size:size + 1, -size:size + 1]
    normal = 1 / (2.0 * np.pi * sigma ** 2)
    return np.exp(-((x ** 2 + y ** 2) / (2.0 * sigma ** 2))) * normal
