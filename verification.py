"""Script with some supporting functions for the verification
"""
# TODO add logging messages for better usability

import xarray as xr
from pathlib import Path
import pandas as pd
from climpred.preprocessing.shared import set_integer_time_axis
import numpy as np


def get_inits(startyear: int = 1993, endyear: int = 2016, timestep="MS"):
    """ Constructs a pd.DatetimeIndex object to pass to climpred for the
    initialisation dates.
    Assumes that all forecasts / hindcasts are initialised on the first day
    of the month.

    See here for pd DateOffset objects:
    https://pandas.pydata.org/docs/user_guide/timeseries.html#dateoffset-objects
    :return:
    """
    start = f"{startyear}-01-01"
    end = f"{endyear}-12-01"
    dr = pd.date_range(start, end, freq=timestep)
    dti = pd.DatetimeIndex(dr)

    return dti


def load_hindcast_data(path, pattern, inits):
    """
    How to solve
    "Resulting object does not have monotonic global indexes along dimension time"
    for SEAS5?!

    Converts the time axis to a integer time axis and renames to lead.

    Adds init dimension and coordinates to each dataset and then
    concatenates along the init dimension.

    Returns the concatenated xr.DataSet which should hopefully work in
    climpred.

    #TODO complete docstring
    """
    paths = Path(path).glob(pattern)  # convert to pathlib object
    # ds = xr.open_mfdataset(pattern, chunks="auto", parallel=True)
    ds_list = []
    for init in inits:
        month = str(init.month).zfill(2) #add leading zeros for months
        filepath = path / f"system_5_seasonal-monthly-single-levels_" \
                      f"{init.year}_{month}_total_precipitation.nc"
        ds = xr.open_dataset(filepath)
        ds = ds.rename({"number": "member"})
        ds = ds.assign_coords(
        {"init": (ds.time[0].values - np.timedelta64(1, "D"))}).expand_dims(
        "init")
        ds = set_integer_time_axis(ds)
        ds = ds.rename({"time": "lead"})
        ds.lead.attrs["units"] = "days"  # update dictionary of the lead attrs
    # to timestep
        ds_list.append(ds)
        ds = xr.concat(ds_list, "init")
        ds["init"] = inits
    return ds


def load_verification_data(pattern):
    """
    #TODO complete docstring
    """
    ds = xr.open_mfdataset(pattern, parallel=True, chunks="auto")
    return ds
