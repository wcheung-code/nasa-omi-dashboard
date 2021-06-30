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
import wget

from flask import Flask, request, redirect, url_for, render_template, json, render_template_string, jsonify


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def control_panel():
    print('request.form:', request.form)
    if not os.path.exists("./image_data/OMNO2d_HRM/{}.p".format('image_data')):
        os.makedirs("./image_data/OMNO2d_HRM/", exist_ok=True)
        wget.download('https://eo-dashboard-nasa.s3.amazonaws.com/image_data.p', out = "./image_data/OMNO2d_HRM/")
    image_data = pickle.load(open( "./image_data/OMNO2d_HRM/{}.p".format('image_data'), "rb" ))
    if request.method == 'POST':
        volume = request.form.get('slide')
        convert = lambda x: tuple(sum(y) for y in zip((2016, 1), divmod(int(x), 12)))
        year, month = convert(volume)
        year, month = str(year), str(month).zfill(2)
        #return jsonify({'volume': volume})
        return json.dumps({'year': year, 'month': month, 'html': image_data[int(volume)]})

    print('render')
    return render_template('index.html', asdf = image_data[int('64')])

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)