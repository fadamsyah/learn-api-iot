import json
import matplotlib.pyplot as plt
import numpy as np
import requests
import streamlit as st
import time
import yaml

from datetime import datetime, timedelta

config  = yaml.safe_load(open('config.yml').read())['arduino']
cfg_dht = config['dht']

st.title("Web App for Monitoring Temperature & Humidity using Pyserial, RabbitMQ, and Streamlit")

dht_interval = st.text_input("DHT Plot Interval (s)", "10")
try:
    dht_interval = int(dht_interval)
except:
    dht_interval = 10

hum_placeholder  = st.empty()
temp_placeholder = st.empty()

hum_fig, hum_ax   = plt.subplots()
temp_fig, temp_ax = plt.subplots()

cur_max_hum  = - np.Inf
cur_max_temp = - np.Inf
cur_min_hum  = np.Inf
cur_min_temp = np.Inf

dht_t_last = time.time()
while True:
    time.sleep(250 / 1000) # 250 ms
    
    # Loop plot Humidity & Temperature
    if (time.time() - dht_t_last) >= cfg_dht['sampling_time']:
        dht_t_last = time.time()
        
        t_end   = datetime.now()
        t_start = t_end - timedelta(seconds = dht_interval)
        t_end   = t_end.strftime("%Y-%m-%d %H:%M:%S")
        t_start = t_start.strftime("%Y-%m-%d %H:%M:%S")
        
        result = requests.post("http://127.0.0.1:5001/get_dht",
                               json={'t_start': t_start, 't_end'  : t_end})
        result = json.loads(result.text)
        
        cur_max_hum  = max(cur_max_hum, max(result['list_humidity']))
        cur_max_temp = max(cur_max_temp, max(result['list_celcius']))
        cur_min_hum  = min(cur_min_hum, min(result['list_humidity']))
        cur_min_temp = min(cur_min_temp, min(result['list_celcius']))
        
        temp_ax.cla()
        temp_ax.set_xlabel("Relative Time (s)")
        temp_ax.set_ylabel('Temperature (C)')
        temp_ax.set_ylim([cur_min_temp - 0.5, cur_max_temp + 0.5])
        temp_ax.plot(result['list_time_x'], result['list_celcius'])
        temp_placeholder.write(temp_fig)
        
        hum_ax.cla()
        hum_ax.set_xlabel("Relative Time (s)")
        hum_ax.set_ylabel("Humidity")
        hum_ax.set_ylim([cur_min_hum - 0.5, cur_max_hum + 0.5])
        hum_ax.plot(result['list_time_x'], result['list_humidity'])
        hum_placeholder.write(hum_fig)