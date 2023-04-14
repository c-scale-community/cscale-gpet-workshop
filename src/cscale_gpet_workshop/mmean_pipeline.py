from concurrent.futures import ThreadPoolExecutor

from dask.array import array
from eotransform.protocol.transformer import Transformer
from eotransform.transformers.send_to_stream import SendToStream
from eotransform.sinks.sink_to_progress_report import SinkToProgressReport
from eotransform.streamed_process import streamed_process
from eotransform_xarray.transformers.send_to_stream import StreamIn
from numpy.typing import NDArray
from tqdm import tqdm
from xarray import Dataset

from cscale_gpet_workshop.streams.mean_stream import MeanStreamIter


def streamed_mean(da: array, axis: int):
    assert axis == 0, f"currently streamed mean expects the accumulation axis to be 0, but received {axis}."
    mean_stream = MeanStreamIter(da.shape[1:])
    with ThreadPoolExecutor(max_workers=2) as ex, tqdm(desc=f"processing month", total=da.shape[0]) as reporter:
        streamed_process(source_dask_chunks(da),
                         SendToStream(mean_stream),
                         SinkToProgressReport(reporter), ex)
    return mean_stream.close()


def source_dask_chunks(da: array) -> NDArray:
    for i in range(da.shape[0]):
        yield da[i].compute()


def monthly_mean(src_data_cube: Dataset) -> Dataset:
    ds_month = src_data_cube.resample(time='M')
    ds_month = ds_month.reduce(streamed_mean, dim='time')
    return ds_month.rio.set_encoding(dict(dtype='int16', _FillValue=-9999, scale_factor=0.1))
