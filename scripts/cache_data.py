from osgeo import gdal
import matplotlib.pyplot as plt
import numpy as np
import folium
from folium.plugins import Draw
from folium.plugins import DualMap
import matplotlib.colors
import matplotlib.pylab as pl
from matplotlib.colors import ListedColormap
import pickle
import re

import os

def data(path):
    ds = gdal.Warp("", path, format="vrt", dstSRS='EPSG:3857')
    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()
    return arr

def raster(data, colormap = 'Reds'):
    masked_data = np.ma.masked_array(data, data < 0)
    norm = matplotlib.colors.PowerNorm(1/3, masked_data.min(), masked_data.max())
    cmap = plt.get_cmap(colormap)
    my_cmap = cmap(np.arange(cmap.N))
    my_cmap[:,-1] = np.linspace(0, 1, cmap.N)
    my_cmap = ListedColormap(my_cmap)
    raster_data = my_cmap(norm(masked_data))
    return raster_data


GEOTIFF_PATH = './data/covid-eo-data/OMNO2d_HRM/'

image_data = {}
for root, dirs, files in os.walk(GEOTIFF_PATH):
    for volume, f in enumerate(files):
        if f.endswith(".tif"):
            array = data(os.path.join(root, f))
            image = raster(array, 'Reds')
            layer = folium.raster_layers.ImageOverlay(
                image, opacity=0.95, 
                bounds =[[-90, -180], [90, 180]], 
                name='Avg. NO2'
            )
            image_data[volume] = layer.url
pickle.dump(image_data, open( "./src/image_data/OMNO2d_HRM/{}.p".format('image_data'), "wb" ) )
