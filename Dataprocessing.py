import xarray as xr
from pathlib import Path
import logging
from tqdm import tqdm
from climpred.preprocessing.shared import set_integer_time_axis
import numpy as np


def get_daily_tp_rate(path, outfolder, globpat=None, var="tp"):
    path = Path(path)
    outfolder = Path(outfolder)

    if not outfolder.exists():
        outfolder.mkdir()

    dataarrays = []

    if (globpat == None):  # single file
        da = xr.open_dataset(path, chunks="auto")[var]
        dataarrays.append(da)

    else:  # list of files
        files = list(path.glob(globpat))
        logging.info(f"Reading {len(files)} files into memory:")
        for file in tqdm(files):
            da = xr.open_dataset(file, chunks="auto")[var]
            dataarrays.append(da)

    logging.info(f"\n Processing {len(dataarrays)} DataArrays:")
    for c, dataarray in enumerate(tqdm(dataarrays)):  # see https://confluence.ecmwf.int/pages/viewpage.action?pageId=197702790
        attrs = dataarray.attrs
        da = dataarray.diff("time") # attrs are dropped
        da.attrs = attrs
        da = xr.concat([dataarray.isel({"time":0}), da], dim="time")
        da.to_netcdf(outfolder / (files[c].parts[-1][:-3] + "_disaggregated.nc"))

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

    if to_netcdf and not cropped_path.exists():
        cropped_path.mkdir()
        logging.info(f"Created directory {cropped_path} \n")

    datasets = []
    if globpat == None:  # single file
        ds = xr.open_dataset(path, chunks="auto")
        datasets.append(ds)

    else:  # note: open_mfdataset() does not work because no monotonic indexes to concatenate along for SEAS5 hindcasts -> use loop
        filelist = list(path.glob(globpat))
        logging.info("Reading multiple datasets:")
        for file in tqdm(filelist):
            ds = xr.open_dataset(file, chunks="auto")
            datasets.append(ds)

    logging.info("Cropping multiple datasets:")
    for count, dataset in enumerate(tqdm(datasets)):
        try:
            logging.info("\n Trying slice with dim names 'latitude'&'longitude'")
            ds_crop = dataset.sel({"latitude": y_slice}).sel({"longitude": x_slice})
        except:
            logging.info("That didn't work. Trying slice with dim names 'lat'&'lon'")
            ds_crop = dataset.sel({"lat": y_slice}).sel({"lon": x_slice})

        if to_netcdf:
            filename = filelist[count].parts[-1][:-3] + "_box.nc"
            ds_crop.to_netcdf(cropped_path / filename)
            logging.info(f"Wrote file {filename} to {cropped_path} \n")


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


def prep_hindcast(path, globpat, to_netcdf=False, filename="prepped_hindcast.nc"):
    """
    Be careful with the selection of the index of the timestamp for the init dimension! When the data was diff()ed from accumulated to daily tp rate, this needs
    to be shifted one up!
    """
    path = Path(path)
    outfolder = path / "climpred_hindcast"
    logging.info(f"Checking if {outfolder} exists.")
    if not outfolder.exists() and to_netcdf:
        outfolder.mkdir()
        logging.info(f"Folder {outfolder} created.\n")

    files = list(path.glob(globpat))
    logging.info(f"Processing {len(files)} files.")
    datasets = []
    for file in tqdm(files):
        ds = xr.open_dataset(file, chunks="auto")
        ds = ds.rename({"number": "member"})
        ds = ds.assign_coords({"init": (ds.time.values[0] - np.timedelta64(1, "D"))}).expand_dims("init")
        ds = set_integer_time_axis(ds)
        ds = ds.rename({"time": "lead"})
        ds.lead.attrs["units"] = "days"
        datasets.append(ds)
    hc = xr.concat(datasets, dim="init")

    if to_netcdf:
        fname = outfolder / filename
        hc.to_netcdf(fname)
        logging.info(f"Wrote {filename} to folder {outfolder} \n")

    return hc