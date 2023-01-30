from pathlib import Path
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

#%%
path = Path(r"C:\Users\sb123\Desktop\ERA5_Box.nc")
ds_ERA = xr.open_dataset(path, chunks="auto")

path = Path(r"C:\Users\sb123\Desktop\ERA5_Box_regrid.nc")
ds_ERA_Regrid = xr.open_dataset(path, chunks="auto")

path = Path(r"C:\Users\sb123\Desktop\SEAS5_box.nc")
ds_SEAS = xr.open_dataset(path, chunks="auto")
del path

#%%
fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(14, 4))
ds.latitude.plot(ax=ax1)
ds.longitude.plot(ax=ax2)
fig.show()

#%%
fig, ax = plt.subplots(ncols=3, figsize=(20,5))
ds_ERA.tp[0,:,:].plot(ax=ax[0])
ds_ERA_Regrid.tp[0,:,:].plot(ax=ax[1])
ds_SEAS.tp[0,0,:,:].plot(ax=ax[2])
plt.tight_layout()
fig.show()
fig.savefig("compare.png", dpi=300)
#%%
fig = plt.figure(figsize=(14, 6))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_global()
ds.tp[0,:,:].plot.pcolormesh(
    ax=ax, transform=ccrs.PlateCarree(), x="longitude", y="latitude",
    add_colorbar=False
)
ax.coastlines()
# ax.set_ylim([0, 90])
fig.show()
