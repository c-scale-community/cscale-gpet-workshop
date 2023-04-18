import math
from typing import Dict

import numpy as np
from numba import cuda
from numpy.typing import NDArray
from xarray import DataArray

THREADS_PER_BLOCK = (16, 16)


@cuda.jit
def convolve2d_cuda_naive(a, kernel, out):
    x = cuda.blockIdx.x * cuda.blockDim.x + cuda.threadIdx.x
    y = cuda.blockIdx.y * cuda.blockDim.y + cuda.threadIdx.y
    size_x = a.shape[0]
    size_y = a.shape[1]

    kernel_sum = 0

    kr_x = kernel.shape[0] // 2
    kr_y = kernel.shape[1] // 2
    for i in range(-kr_x, kr_x + 1):
        for j in range(-kr_y, kr_y + 1):
            xx = x + i
            yy = y + j
            if 0 <= xx < size_x and 0 <= yy < size_y:
                kernel_sum += a[xx, yy] * kernel[kr_x + i, kr_y + j]
    out[x, y] = kernel_sum


def convolve2d(a: NDArray, kernel: NDArray):
    block_per_grid = calc_cuda_blocks_per_grid2d(a.shape, THREADS_PER_BLOCK)
    out_device = cuda.device_array(a.shape, a.dtype)
    convolve2d_cuda_naive[block_per_grid, THREADS_PER_BLOCK](cuda.to_device(a),
                                                             cuda.to_device(kernel),
                                                             out_device)
    return out_device.copy_to_host()


def calc_cuda_blocks_per_grid2d(shape, threads_per_block):
    blocks_per_grid_x = math.ceil(shape[0] / threads_per_block[0])
    blocks_per_grid_y = math.ceil(shape[1] / threads_per_block[1])
    return blocks_per_grid_x, blocks_per_grid_y


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
