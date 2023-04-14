import numpy as np
from eotransform.protocol.stream import StreamIn
from numpy.typing import NDArray


class MeanStreamIter(StreamIn[NDArray]):
    def __init__(self, shape):
        self.n = np.zeros(shape, dtype=np.uint32)
        self.running_sum = np.zeros(shape, dtype=np.float32)

    def send(self, new_obs: NDArray):
        is_nan = np.isnan(new_obs)
        self.n += (~is_nan).astype(np.uint32)
        new_obs = 10.0 ** (new_obs * 0.1)
        new_obs[is_nan] = 0
        self.running_sum += new_obs

    def close(self) -> NDArray:
        return 10 * np.log10(self.running_sum / self.n)
