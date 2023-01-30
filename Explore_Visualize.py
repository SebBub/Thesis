import xarray as xr
from pathlib import Path
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from Dataprocessing import prep_hindcast
import seaborn as sns
import numpy as np
datapath = Path(r"Z:\Massendaten\ECMWF\SEAS5_Box\system_5_seasonal-monthly-single-levels_1994_01_total_precipitation.nc")
cm = 1/2.54  # centimeters in inches (for matplotlib figsize)
savefigsto = Path(r"C:\Users\sb123\Documents\OneDrive\04_SS22\climThesis\Figures\Hindcast_Histograms")

#%% plotting Histograms
leadtime = np.arange(0,200,10)
fig, ax = plt.subplots(figsize=(15*cm, 15*cm), ncols=4, nrows=5)
for i, lt in enumerate(leadtime):
    hc = prep_hindcast("Z:\Massendaten\ECMWF\SEAS5_Box", "*total_precipitation.nc", lt)["tp"]
    hc *= 1000 # convert to mm
    sns.histplot(hc.values.flat, bins=200, ax=ax.flat[i])
    ax.flat[i].set_xlim(left=0, right=1200)
    ax.flat[i].set(title=f"{lt+1}")
    ax.flat[i].set(ylabel=None)
fig.suptitle("Daily tp [mm] at lead day")
plt.tight_layout()
fig.savefig(savefigsto / f"SEAS5_lead_histograms.png", dpi=300)

#%%
fig, ax = plt.subplots(
    nrows=2, subplot_kw={"projection": ccrs.PlateCarree()}, figsize=(6, 10)
)
ERA5_Con[4, :, :].plot(ax=ax[0])
ERA5[4, :, :].plot(ax=ax[1])
for ax in ax:
    ax.add_feature(cfeature.BORDERS, linestyle="-")
    ax.add_feature(cfeature.COASTLINE, linestyle="-")
plt.tight_layout()
fig.show()
fig.savefig("regrid_conservative.png", dpi=500)
