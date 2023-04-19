import math
from typing import Any

import numpy as np
from eotransform.protocol.stream import StreamIn
from numba import guvectorize, float32, cuda
from numpy.typing import NDArray


@guvectorize([(float32[:], float32, float32)], '(n),()->()', target='cuda')
def add_observation(src, new, dst):
    is_nan =  math.isnan(new)
    src[..., 0] = src[..., 0] + (~is_nan)
    src[..., 1] = src[..., 1] + (0 if is_nan else (10.0 ** (new * 0.1)))


class MeanStreamIterCuda(StreamIn[NDArray]):
    def __init__(self, shape):
        self.running_data = cuda.to_device(np.zeros((*shape, 2), dtype=np.float32))
        self._new_obs_buffer = cuda.device_array(shape, dtype=np.float32)

    def send(self, new_obs):
        self._new_obs_buffer.copy_to_device(new_obs)
        add_observation(self.running_data, self._new_obs_buffer)

    def close(self) -> NDArray:
        return 10 * np.log10(self.running_data.copy_to_host()[..., 1] / self.running_data.copy_to_host()[..., 0])
