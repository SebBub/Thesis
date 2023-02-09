"""
Downloads ERA5 datasets from the Copernicus C3S datastore (CDS)

"""
# TODO add docstring

import logging
from pathlib import Path
import cdsapi
from playsound import playsound

c = cdsapi.Client()

def download_era5(startyear, endyear, path, variable="total_precipitation",
                  area=None):
    """ Downloads data on single levels, i.e. surface variables.
    Single netCDF files for each year
    """
    path = Path(path)
    logging.info(f"Attempting to download files for years {startyear} to "
                 f"{endyear} to {path}")

    for year in range(startyear, endyear + 1):
        filename = f"ERA5-hourly-single-levels_{year}.nc"
        logging.info(f"Checking if {filename} already exists")

        if (path / filename).exists() and (path / filename).stat().st_size > 0:
            logging.info("File already exists!")

        else:
            parameters = {'product_type': 'reanalysis', 'format': 'netcdf',
                          'variable': variable, 'year': str(year),
                          'month':
                              ['01', '02', '03', '04', '05', '06',
                               '07', '08', '09', '10', '11', '12', ],
                          'day': ['01', '02', '03', '04', '05', '06', '07',
                                  '08', '09', '10', '11',
                                  '12', '13', '14', '15', '16', '17', '18',
                                  '19', '20', '21', '22',
                                  '23', '24', '25', '26', '27', '28', '29',
                                  '30', '31', ],
                          'time': ['00:00', '01:00', '02:00', '03:00', '04:00',
                                   '05:00', '06:00',
                                   '07:00', '08:00', '09:00', '10:00', '11:00',
                                   '12:00', '13:00',
                                   '14:00', '15:00', '16:00', '17:00', '18:00',
                                   '19:00', '20:00',
                                   '21:00', '22:00', '23:00', ],
                          "area": area, }

            if parameters["area"] == None:
                del parameters["area"]
            logging.info(f"Trying to download {filename}")
            c.retrieve("reanalysis-era5-single-levels", parameters,
                       path / filename)
            logging.info(f"Successfully downloaded {filename}")
            # playsound(r"C:\Users\sb123\Music\iphone-ding-sound.mp3")

    logging.info("Successfully processed all requests!")
    # playsound(r"C:\Users\sb123\Music\iphone-ding-sound.mp3")

def download_cerra(startyear, endyear, path, variable="total_precipitation"):
    """ Downloads data on single levels, i.e. surface variables.
    Single netCDF files for each year
    A cropping for a certain area is apparently not supported
    """
    path = Path(path)
    logging.info(f"Attempting to download files for years {startyear} to "
                 f"{endyear} to {path}")

    for year in range(startyear, endyear + 1):
        filename = f"CERRA-hourly-single-levels_{year}.nc"
        logging.info(f"Checking if {filename} already exists")

        if (path / filename).exists() and (path / filename).stat().st_size > 0:
            logging.info("File already exists!")

        else:
            parameters = {'variable': 'total_precipitation',
                          'level_type': 'surface',
                          'product_type': 'analysis',
                          'year': str(year),
                          'month': [
                              '01', '02', '03',
                              '04', '05', '06',
                              '07', '08', '09',
                              '10', '11', '12',
                          ],
                          'day': [
                              '01', '02', '03',
                              '04', '05', '06',
                              '07', '08', '09',
                              '10', '11', '12',
                              '13', '14', '15',
                              '16', '17', '18',
                              '19', '20', '21',
                              '22', '23', '24',
                              '25', '26', '27',
                              '28', '29', '30',
                              '31',
                          ],
                          'time': '06:00',
                          'format': 'netcdf', }

        logging.info(f"Trying to download {filename}")
        c.retrieve("reanalysis-cerra-land", parameters,
                   path / filename)
        logging.info(f"Successfully downloaded {filename}")

    logging.info("Successfully processed all requests!")
