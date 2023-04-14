import numpy as np
from eotransform_xarray.transformers.send_to_stream import StreamIn
from numpy._typing import NDArray


class MeanStreamIter(StreamIn):
    def __init__(self, shape):
        self.n = np.zeros(shape, dtype=np.uint32)
        self.running_sum = np.zeros(shape, dtype=np.float32)

    def send(self, new_obs: NDArray):
        is_nan = np.isnan(new_obs)
        self.n += (~is_nan).astype(np.uint32)
        new_obs[is_nan] = 0
        self.running_sum += new_obs

    def close(self) -> NDArray:
        return self.running_sum / self.n
