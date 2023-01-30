import xarray as xr
from pathlib import Path
import logging
from climpred.preprocessing.shared import set_integer_time_axis
import numpy as np


def crop_netCDF(path, lat1, lat2, lon1, lon2, globpat=None, to_netcdf=False):
    """
    Check sign of lat increment in latlon grid before (see below!)
    # TODO: first check if the files to be cropped are already stored in cropped_path

    :param path:
    :param lat1:
    :param lat2:
    :param lon1:
    :param lon2:
    :param globpat:
    :param to_netcdf:
    :return:
    """
    x_slice = slice(lon1, lon2)
    y_slice = slice(lat2, lat1)  # ! reversed order because ERA5 has
    # negative y-increment, check before

    path = Path(path)
    cropped_path = path / "Cropped"
    logging.info(f"Testing if path {cropped_path} existis.")
    if to_netcdf and not cropped_path.exists():
        cropped_path.mkdir()
        logging.info(f"Created directory {cropped_path} \n")

    if globpat == None: # single file
        ds = xr.open_dataset(path, chunks="auto")
    else:
        ds = xr.open_mfdataset(path.glob(globpat), chunks="auto")

        try:
            logging.info("Trying slice with dim names 'latitude'&'longitude'")
            ds_crop = ds.sel({"latitude": y_slice}).sel({"longitude": x_slice})
        except:
            logging.info("That didn't work. Trying slice with dim names "
                         "'lat'&'lon'")
            ds_crop = ds.sel({"lat": y_slice}).sel({"lon": x_slice})

        if to_netcdf:
            filename = path.parts[-1][:-3] + "_box.nc"
            logging.info(f"Writing file {filename} to {cropped_path}")
            ds_crop.to_netcdf(
                cropped_path / filename
            )


def ERA5_hourly_daily(path, globpat=None, to_netcdf=False):

    if globpat == None:
        path = Path(path)
        ds = xr.open_dataset(path, chunks="auto")
        ds = ds.resample(time="1D").sum()  # aggregate hourly to daily
        if to_netcdf:
            ds.to_netcdf(path.parent / (path.parts[-1][:-3] + "_daily.nc"))

    else:
        files = list(Path(path).glob(globpat))
        for file in files:
            ds = xr.open_dataset(file, chunks="auto")
            ds = ds.resample(time="1D").sum()  # aggregate hourly to daily
            if to_netcdf:
                ds.to_netcdf(file.parent / (file.parts[-1][:-3] + "_daily.nc"))


def prep_hindcast(path, globpat, leadtime, to_netcdf=False, outfolder=None,
                  filename="hc.nc"):
    path = Path(path)
    outfolder = path / "climpred_hindcast"
    logging.info(f"Checking if {outfolder} exists.")
    if not outfolder.exists() and to_netcdf:
        outfolder.mkdir()
        logging.info(f"Folder {outfolder} created.\n")

    files = list(path.glob(globpat))
    logging.info(f"Processing multiple files {files}.")
    datasets = []
    for file in files:
        # ds = xr.open_dataset(file, chunks="auto")
        ds = xr.open_dataset(file).isel({"time": leadtime}) #pick leadtime
        # ds = ds.rename({"number": "member"})
        # ds = ds.assign_coords({"init": (ds.time.values[0] - np.timedelta64(1, "D"))})
        #.expand_dims("init") #TODO check if we need to actively expand the dims
        # ds = set_integer_time_axis(ds)
        # ds = ds.rename({"time": "lead"})
        # ds.lead.attrs["units"] = "days"
        datasets.append(ds)
    hc = xr.concat(datasets, dim="time")

    if to_netcdf:
        fname = outfolder / filename
        hc.to_netcdf()
        logging.info(f"Wrote {filename} to folder {outfolder} \n")
    return hc
