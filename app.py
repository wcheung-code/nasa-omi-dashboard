
from flask import Flask, request, render_template, json

import os
from glob import glob
import folium
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from concurrent.futures import ThreadPoolExecutor

class NCFileProcessor():
    def __init__(self):
        self.BASE_PATH = './OMNO2d_HRM/'
        self.THREAD_POOL = 16
        glob_pattern = os.path.join(self.BASE_PATH, '*')
        self.files = sorted(glob(glob_pattern), key=os.path.getctime)
        self.mapping = {}
        for i, f in enumerate(self.files):
            year, month = divmod(int(f.split('_')[4]), 100)
            self.mapping[i] = (year, month)
        self.images = {}
    
    def process(self):
       with ThreadPoolExecutor(max_workers=self.THREAD_POOL) as executor:
           for i, response in enumerate(executor.map(self._process, self.files)):
               self.images[i] = response

    def _process(self, path):
        array = self._get_data(path)
        raster_data = self._get_raster_data(array)
        return self._get_image_url(raster_data)        

    def _get_data(self, path):
        nc_file = xr.open_dataset(path)
        return nc_file['TroposphericNO2'].to_numpy()

    def _get_raster_data(self, array):
        masked_data = np.ma.masked_array(array/1e15, array < 0)
        default_cmap = plt.get_cmap('Reds')
        new_cmap = default_cmap(np.arange(default_cmap.N))
        new_cmap[:,-1] = np.linspace(0, 1, default_cmap.N)
        raster_data = ListedColormap(new_cmap)(masked_data)
        return raster_data

    def _get_image_url(self, raster_data):
        return folium.raster_layers.ImageOverlay(
            raster_data, opacity=0.95, 
            bounds =[[-90, -180], [90, 180]], 
            name='Tropospheric NO2'
        ).url

app = Flask(__name__)
@app.before_first_request
def download_data():
    global image_data, nc_files
    nc_files = NCFileProcessor()
    nc_files.process()
    image_data = nc_files.images 

@app.route('/', methods=['GET', 'POST'])
def control_panel():
#    print('request.form:', request.form)
    if request.method == 'POST':
        volume = request.form.get('slide')
        year, month = nc_files.mapping[volume]
        year, month = str(year), str(month).zfill(2)
        #return jsonify({'volume': volume})
        return json.dumps({'year': year, 'month': month, 'html': image_data[int(volume)]})

    print('render')
    return render_template('index.html', asdf = image_data[len(nc_files.files) - 1])

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)