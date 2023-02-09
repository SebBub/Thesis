import xarray as xr
from pathlib import Path
import logging
from tqdm import tqdm
from climpred.preprocessing.shared import set_integer_time_axis
import numpy as np

# Private helper functions
def _make_dir(path, to_netcdf):
    if to_netcdf and not path.exists():
        path.mkdir()
        logging.info(f"Created directory {path} \n")


def crop_netCDF(path, lat1, lat2, lon1, lon2, globpat=None, to_netcdf=False, var="tp"):
    """
    Check sign of lat increment in latlon grid before (see below!)
    """
    # TODO: first check if the files to be cropped are already stored in cropped_path

    x_slice = slice(lon1, lon2)
    y_slice = slice(lat2, lat1)  # ! reversed order because ERA5 has negative y-increment, check before

    path = Path(path)
    datasets = []  # empty list to store dataset(s) before cropping

    if globpat == None:  # single file provided
        cropped_path = path.parent / "Cropped"
        _make_dir(cropped_path, to_netcdf)

        ds = xr.open_dataset(path, chunks="auto")
        ds[var].encoding = {}  # delete encoing information before writing to_netcdf, now write uncompressed!
        datasets.append(ds)

    else:  # folder with multiple files provided
        cropped_path = path / "Cropped"
        _make_dir(cropped_path, to_netcdf)

        # note: open_mfdataset() does not work because no monotonic indexes to concatenate along for SEAS5 hindcasts -> use loop
        filelist = list(path.glob(globpat))
        for file in filelist:
            ds = xr.open_dataset(file, chunks="auto")
            ds[var].encoding = {}  # delete encoing information before writing to_netcdf, now write uncompressed!
            datasets.append(ds)

    for count, dataset in enumerate(datasets):
        try:
            logging.info("\n Trying slice with dim names 'latitude'&'longitude'")
            ds_crop = dataset.sel({"latitude": y_slice}).sel({"longitude": x_slice})
        except:
            logging.info("That didn't work. Trying slice with dim names 'lat'&'lon'")
            ds_crop = dataset.sel({"lat": y_slice}).sel({"lon": x_slice})

        if to_netcdf and globpat != None:
            filename = filelist[count].parts[-1][:-3] + "_box.nc"  # exrtacting filenames from glob list only required for multiple files
            ds_crop.to_netcdf(cropped_path / filename)
            logging.info(f"Wrote file {filename} to disk \n")

        if to_netcdf and globpat == None:
            filename = path.parts[-1][:-3] + "_box.nc"
            ds_crop.to_netcdf(cropped_path / filename)
            logging.info(f"Wrote file {filename} to disk\n")

    return ds_crop if (to_netcdf == False and globpat == None) else None  # only return cropped dataset when a single file was provided

def get_daily_tp_rate(path, outfolder, globpat=None, var="tp", to_netcdf=False):
    path = Path(path)
    outfolder = Path(outfolder)
    _make_dir(outfolder, to_netcdf)

    def helper(dataarray): #TODO define as private function?
        da = dataarray.diff("time")  # attrs are dropped
        da = xr.concat([dataarray.isel({"time": 0}), da], dim="time")  #carries over attrs from first element TODO could be the issue, carries over encoding?
        da.attrs["units"] = "mm"
        return da

    if (globpat == None):  # single file
        da = xr.open_dataset(path, chunks="auto")[var]
        da = helper(da)
        if to_netcdf:
            filename = path.parts[-1][:-3] +"_disaggregated.nc"
            da.to_netcdf(outfolder / filename)
            logging.info(f"Wrote file {filename} to disk.")

    else:  # list of files
        dataarrays = []
        files = list(path.glob(globpat))
        logging.info(f"Reading and processing {len(files)}")
        for file in files:
            da = xr.open_dataset(file, chunks="auto")[var]
            da = helper(da)
            dataarrays.append(da)

        if to_netcdf:
            for c, dataarray in enumerate(dataarrays):
                filename = files[c].parts[-1][:-3] + "_disaggregated.nc"
                dataarray.to_netcdf(outfolder / filename)
                logging.info(f"Wrote file {filename} to disk.")

    return da if (globpat == None and to_netcdf==False) else None


def ERA5_hourly_daily(path, globpat=None, to_netcdf=False):
    if globpat == None: #single file
        path = Path(path)
        ds = xr.open_dataset(path, chunks="auto")
        ds = ds.resample(time="1D").sum()  # aggregate hourly to daily
        if to_netcdf:
            ds.to_netcdf(path.parent / (path.parts[-1][:-3] + "_daily.nc"))

    else: # multiple files
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
    _make_dir(outfolder, to_netcdf)

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

