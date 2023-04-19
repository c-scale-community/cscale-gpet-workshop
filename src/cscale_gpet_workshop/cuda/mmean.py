from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import pandas as pd
from dask.array import array
from eotransform.sinks.sink_to_progress_report import SinkToProgressReport
from eotransform.streamed_process import streamed_process
from eotransform.transformers.send_to_stream import SendToStream
from geopathfinder.naming_conventions.yeoda_naming import YeodaFilename
from numba import cuda
from tqdm import tqdm
from xarray import DataArray

from cscale_gpet_workshop.cuda.streams.mean_stream import MeanStreamIterCuda


def streamed_mean(da: array, axis: int):
    assert axis == 0, f"currently streamed mean expects the accumulation axis to be 0, but received {axis}."
    mean_stream = MeanStreamIterCuda(da.shape[1:])
    with ThreadPoolExecutor(max_workers=2) as ex, tqdm(desc=f"processing month", total=da.shape[0]) as reporter:
        streamed_process(source_dask_chunks_and_move_to_cuda(da),
                         SendToStream(mean_stream),
                         SinkToProgressReport(reporter), ex)
    return mean_stream.close()


def source_dask_chunks_and_move_to_cuda(da: array) -> Any:
    for i in range(da.shape[0]):
        yield da[i].compute()


def monthly_mean(src_data_cube: DataArray, out_put: Path) -> None:
    ds_month = src_data_cube.resample(time='M')
    ds_month = ds_month.reduce(streamed_mean, dim='time')

    yeoda_fields = dict(var_name='SIG0-MMEAN', extra_field='MMEAN', creator='TUWIEN')
    for t in ds_month.time:
        ts = pd.to_datetime(t.item())
        yeoda_fields['datetime_1'] = ts
        smart_name = YeodaFilename(yeoda_fields)
        ds_month.sel(time=ts).rio.set_encoding(dict(dtype='int16', _FillValue=-9999, scale_factor=0.1)) \
            .rio.to_raster(out_put / str(smart_name), compress='ZSTD')
