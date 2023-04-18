from typing import Dict

import numpy as np
from numba import njit, prange
from numpy.typing import NDArray
from xarray import DataArray


@njit(parallel=True)
def convolve2d_numba(a: NDArray, kernel: NDArray, out: NDArray) -> None:
    kr_x = kernel.shape[0] // 2
    kr_y = kernel.shape[1] // 2

    for x in prange(a.shape[0]):
        for y in prange(a.shape[1]):
            kernel_sum = 0
            for i in range(-kr_x, kr_x + 1):
                for j in range(-kr_y, kr_y + 1):
                    xx = x + i
                    yy = y + j
                    if 0 <= xx < a.shape[0] and 0 <= yy < a.shape[1]:
                        kernel_sum += a[xx, yy] * kernel[kr_x + i, kr_y + j]
            out[x, y] = kernel_sum



def convolve2d(a: NDArray, kernel: NDArray) -> NDArray:
    out = np.empty(a.shape)
    convolve2d_numba(a, kernel, out)
    return out


def gauss_blur(raster: DataArray, kernel_size: int, sigma: float) -> DataArray:
    kernel = make_gauss_kernel(kernel_size, sigma)
    da = DataArray(convolve2d(raster.values[0], kernel)[np.newaxis, ...],
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
