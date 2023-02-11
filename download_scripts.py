"""
Downloads ERA5 datasets from the Copernicus C3S datastore (CDS)

"""
# TODO add docstring

import logging
from pathlib import Path
import cdsapi
from playsound import playsound

c = cdsapi.Client()

def _get_years(startyear, endyear):
    years = []
    for year in range(startyear, endyear + 1):
        years.append(str(year))
    return years

def download_era5(startyear, endyear, path, variable="total_precipitation", area=None):
    """Downloads data on single levels, i.e. surface variables.
    Single netCDF files for each year
    """
    path = Path(path)
    logging.info(
        f"Attempting to download files for years {startyear} to " f"{endyear} to {path}"
    )

    for year in range(startyear, endyear + 1):
        filename = f"ERA5-hourly-single-levels_{year}.nc"
        logging.info(f"Checking if {filename} already exists")

        if (path / filename).exists() and (path / filename).stat().st_size > 0:
            logging.info("File already exists!")

        else:
            parameters = {
                "product_type": "reanalysis",
                "format": "netcdf",
                "variable": variable,
                "year": str(year),
                "month": [
                    "01",
                    "02",
                    "03",
                    "04",
                    "05",
                    "06",
                    "07",
                    "08",
                    "09",
                    "10",
                    "11",
                    "12",
                ],
                "day": [
                    "01",
                    "02",
                    "03",
                    "04",
                    "05",
                    "06",
                    "07",
                    "08",
                    "09",
                    "10",
                    "11",
                    "12",
                    "13",
                    "14",
                    "15",
                    "16",
                    "17",
                    "18",
                    "19",
                    "20",
                    "21",
                    "22",
                    "23",
                    "24",
                    "25",
                    "26",
                    "27",
                    "28",
                    "29",
                    "30",
                    "31",
                ],
                "time": [
                    "00:00",
                    "01:00",
                    "02:00",
                    "03:00",
                    "04:00",
                    "05:00",
                    "06:00",
                    "07:00",
                    "08:00",
                    "09:00",
                    "10:00",
                    "11:00",
                    "12:00",
                    "13:00",
                    "14:00",
                    "15:00",
                    "16:00",
                    "17:00",
                    "18:00",
                    "19:00",
                    "20:00",
                    "21:00",
                    "22:00",
                    "23:00",
                ],
                "area": area,
            }

            if parameters["area"] == None:
                del parameters["area"]
            logging.info(f"Trying to download {filename}")
            c.retrieve("reanalysis-era5-single-levels", parameters, path / filename)
            logging.info(f"Successfully downloaded {filename}")
            # playsound(r"C:\Users\sb123\Music\iphone-ding-sound.mp3")

    logging.info("Successfully processed all requests!")
    # playsound(r"C:\Users\sb123\Music\iphone-ding-sound.mp3")


def download_cerra(startyear, endyear, path, variable="total_precipitation"):
    """Downloads data on single levels, i.e. surface variables.
    Single netCDF files for each year
    A cropping for a certain area is apparently not supported
    """
    path = Path(path)
    logging.info(
        f"Attempting to download files for years {startyear} to " f"{endyear} to {path}"
    )

    for year in range(startyear, endyear + 1):
        filename = f"CERRA-hourly-single-levels_{year}.nc"
        logging.info(f"Checking if {filename} already exists")

        if (path / filename).exists() and (path / filename).stat().st_size > 0:
            logging.info("File already exists!")

        else:
            parameters = {
                "variable": "total_precipitation",
                "level_type": "surface",
                "product_type": "analysis",
                "year": str(year),
                "month": [
                    "01",
                    "02",
                    "03",
                    "04",
                    "05",
                    "06",
                    "07",
                    "08",
                    "09",
                    "10",
                    "11",
                    "12",
                ],
                "day": [
                    "01",
                    "02",
                    "03",
                    "04",
                    "05",
                    "06",
                    "07",
                    "08",
                    "09",
                    "10",
                    "11",
                    "12",
                    "13",
                    "14",
                    "15",
                    "16",
                    "17",
                    "18",
                    "19",
                    "20",
                    "21",
                    "22",
                    "23",
                    "24",
                    "25",
                    "26",
                    "27",
                    "28",
                    "29",
                    "30",
                    "31",
                ],
                "time": "06:00",
                "format": "netcdf",
            }

        logging.info(f"Trying to download {filename}")
        c.retrieve("reanalysis-cerra-land", parameters, path / filename)
        logging.info(f"Successfully downloaded {filename}")

    logging.info("Successfully processed all requests!")


def download_seasonal(
    startyear,
    endyear,
    path,
    system="5",
    form="netcdf",
    variable="total_precipitation",
    months=[
        "01",
        "02",
        "03",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        "10",
        "11",
        "12",
    ],
    grid=None,
    area=None,
):
    """Downloads data on single levels, i.e. surface variables."""
    path = Path(path)
    years = _get_years(startyear,endyear)

    for year in years:  # to split up on more single requests
        for month in months:  # same
            name = f"system_{system}_seasonal-monthly-single-levels_{year}_{month}_{variable}."

            if form == "grib":
                filename = name + "grib"
            elif form == "netcdf":
                filename = name + "nc"

            logging.info(f"Checking if {filename} already exists \n")
            if (path / filename).exists() and (path / filename).stat().st_size > 0:
                logging.info(f"{filename} already exists! \n")

            else:
                logging.info(f"{filename} not found, trying to download file!")
                parameters = {
                    "format": form,
                    "originating_centre": "ecmwf",
                    "system": system,
                    "variable": variable,
                    "year": year,
                    "month": month,
                    "leadtime_hour": [
                        "24",
                        "48",
                        "72",
                        "96",
                        "120",
                        "144",
                        "168",
                        "192",
                        "216",
                        "240",
                        "264",
                        "288",
                        "312",
                        "336",
                        "360",
                        "384",
                        "408",
                        "432",
                        "456",
                        "480",
                        "504",
                        "528",
                        "552",
                        "576",
                        "600",
                        "624",
                        "648",
                        "672",
                        "696",
                        "720",
                        "744",
                        "768",
                        "792",
                        "816",
                        "840",
                        "864",
                        "888",
                        "912",
                        "936",
                        "960",
                        "984",
                        "1008",
                        "1032",
                        "1056",
                        "1080",
                        "1104",
                        "1128",
                        "1152",
                        "1176",
                        "1200",
                        "1224",
                        "1248",
                        "1272",
                        "1296",
                        "1320",
                        "1344",
                        "1368",
                        "1392",
                        "1416",
                        "1440",
                        "1464",
                        "1488",
                        "1512",
                        "1536",
                        "1560",
                        "1584",
                        "1608",
                        "1632",
                        "1656",
                        "1680",
                        "1704",
                        "1728",
                        "1752",
                        "1776",
                        "1800",
                        "1824",
                        "1848",
                        "1872",
                        "1896",
                        "1920",
                        "1944",
                        "1968",
                        "1992",
                        "2016",
                        "2040",
                        "2064",
                        "2088",
                        "2112",
                        "2136",
                        "2160",
                        "2184",
                        "2208",
                        "2232",
                        "2256",
                        "2280",
                        "2304",
                        "2328",
                        "2352",
                        "2376",
                        "2400",
                        "2424",
                        "2448",
                        "2472",
                        "2496",
                        "2520",
                        "2544",
                        "2568",
                        "2592",
                        "2616",
                        "2640",
                        "2664",
                        "2688",
                        "2712",
                        "2736",
                        "2760",
                        "2784",
                        "2808",
                        "2832",
                        "2856",
                        "2880",
                        "2904",
                        "2928",
                        "2952",
                        "2976",
                        "3000",
                        "3024",
                        "3048",
                        "3072",
                        "3096",
                        "3120",
                        "3144",
                        "3168",
                        "3192",
                        "3216",
                        "3240",
                        "3264",
                        "3288",
                        "3312",
                        "3336",
                        "3360",
                        "3384",
                        "3408",
                        "3432",
                        "3456",
                        "3480",
                        "3504",
                        "3528",
                        "3552",
                        "3576",
                        "3600",
                        "3624",
                        "3648",
                        "3672",
                        "3696",
                        "3720",
                        "3744",
                        "3768",
                        "3792",
                        "3816",
                        "3840",
                        "3864",
                        "3888",
                        "3912",
                        "3936",
                        "3960",
                        "3984",
                        "4008",
                        "4032",
                        "4056",
                        "4080",
                        "4104",
                        "4128",
                        "4152",
                        "4176",
                        "4200",
                        "4224",
                        "4248",
                        "4272",
                        "4296",
                        "4320",
                        "4344",
                        "4368",
                        "4392",
                        "4416",
                        "4440",
                        "4464",
                        "4488",
                        "4512",
                        "4536",
                        "4560",
                        "4584",
                        "4608",
                        "4632",
                        "4656",
                        "4680",
                        "4704",
                        "4728",
                        "4752",
                        "4776",
                        "4800",
                        "4824",
                        "4848",
                        "4872",
                        "4896",
                        "4920",
                        "4944",
                        "4968",
                        "4992",
                        "5016",
                        "5040",
                        "5064",
                        "5088",
                        "5112",
                        "5136",
                        "5160",
                    ],
                    "grid": grid,
                    "area": area,
                    "day": "01",  # SEAS5 always initialised on 1st DOM
                }

                # if grid == "av":  # archived grid, should equal grid=None
                #     logging.info("Downloading in archived resolution!")
                #     c.retrieve(
                #         "seasonal-original-single-levels", parameters, path / filename
                #     )
                #     logging.info(f"Successfully downloaded {filename}")
                # TODO I think grid = av and specifying no grid parameter is the same... check!

                if grid == None:
                    del parameters["grid"]
                    c.retrieve(
                        "seasonal-original-single-levels", parameters, path / filename
                    )
                    logging.info(f"Successfully downloaded {filename} \n")


def download_seasonal_climatology(
    path, startyear, endyear, system=5, form="netcdf", variable="total_precipitation"
):
    years = _get_years(startyear, endyear)
    logging.info(f"Will try downloading SEAS5 climatology for years {startyear} - {endyear} \n \n")

    for year in years:
        parameters = {
            "format": form,
            "originating_centre": "ecmwf",
            "system": system,
            "variable": variable,
            "product_type": "monthly_mean",
            "year": [year],
            "month": ["01", "02", "03",
                      "04", "05", "06",
                      "07", "08", "09",
                      "10", "11", "12", ],
            "leadtime_month": ["1", "2", "3", "4", "5", "6", ],
        }
        filename = Path(path) / ("SEAS5_climatology_" + year + ".nc")
        logging.info(f"Trying to download {filename} \n")
        c.retrieve("seasonal-monthly-single-levels", parameters, filename)
        logging.info(f"Successfully downloaded {filename}! \n")
