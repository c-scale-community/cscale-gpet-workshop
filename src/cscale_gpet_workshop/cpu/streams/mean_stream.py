from typing import Any

import numpy as np
from eotransform.protocol.stream import StreamIn
from numba import guvectorize, float32
from numpy.typing import NDArray


@guvectorize([(float32[:], float32, float32[:])], '(n),()->(n)', target='parallel')
def add_observation(src, new, dst):
    is_nan = np.isnan(new)
    dst[..., 0] = src[..., 0] + (~is_nan)
    dst[..., 1] = src[..., 1] + (0 if is_nan else (10.0 ** (new * 0.1)))


class MeanStreamIter(StreamIn[NDArray]):
    def __init__(self, shape):
        self.running_data = np.zeros((*shape, 2), dtype=np.float32)

    def send(self, new_obs: NDArray):
        self.running_data = add_observation(self.running_data, new_obs)

    def close(self) -> NDArray:
        return 10 * np.log10(self.running_data[..., 1] / self.running_data[..., 0])
