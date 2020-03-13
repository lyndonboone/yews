import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from yews.datasets.utils import stream2array
from haversine import haversine

def plot_waveform(st, fs, pick_results, df_picks, df_cat, station_coords):
    # radius of earth in km
    R = 6371
    
    t0 = st[0].stats.starttime.timestamp
    array = stream2array(st)
       
    ts = np.linspace(0, (len(array[0]) - 1)/fs, len(array[0])) + t0
    ts_dates = [dt.datetime.fromtimestamp(timestamp) for timestamp in ts]
    ts_datenums = mdates.date2num(ts_dates)
    
    tp = np.linspace(5, (len(array[0]) - 1)/fs - 15, len(pick_results['cf_p'])) + t0
    tp_dates = [dt.datetime.fromtimestamp(timestamp) for timestamp in tp]
    tp_datenums = mdates.date2num(tp_dates)
    
    fig, ax = plt.subplots(4, 1, figsize=(12,12), sharex=True)
    
    # plot waveforms
    for i, axis in enumerate(ax):
        if i != 3:
            axis.plot(ts_datenums, array[i], 'k')
            axis.set_ylabel('Amplitude (' + st[i].stats.channel + ')')
        axis.grid()
    
    ax[3].plot(tp_datenums, pick_results['cf_p'], c='tab:blue', label='P')
    ax[3].plot(tp_datenums, pick_results['cf_s'], c='tab:red', label='S')
    ax[3].set_ylabel('Probability Ratio (log10)')
    
    # plot picks from CPIC
    datestr_list = list(df_picks['pick time'])
    phase_list = list(df_picks['phase'])
    for i, datestr in enumerate(datestr_list):
        phase = phase_list[i]
        if phase == 'p':
            color = 'tab:blue'
        else:
            color = 'tab:red'
        for axis in ax:
            axis.axvline(mdates.datestr2num(datestr), c=color, ls='--',
                         alpha=1.0)
       
    datestr_list = list(df_cat['time'])
    lat_list = list(df_cat['latitude'])
    long_list = list(df_cat['longitude'])
    mag_list = list(df_cat['mag'])
    for i, datestr in enumerate(datestr_list):
        event_coords = (lat_list[i], long_list[i])
        dist = haversine(station_coords, event_coords)
        alpha = 1 - (np.pi*R)**(-1)*haversine(station_coords, event_coords)
        mag = mag_list[i]
        for axis in ax:
            axis.axvline(mdates.datestr2num(datestr), c='tab:green', ls='--',
                         alpha=alpha)
            axis.annotate('mag {:.2f} event\n{:.0f} km away'.format(mag, dist), (mdates.datestr2num(datestr),100),
                          c='tab:green')
    
    fig.autofmt_xdate()
    myFmt = mdates.DateFormatter('%Y-%m-%dT%H:%M:%S')
    plt.gca().xaxis.set_major_formatter(myFmt)
    
    fig.tight_layout()
    plt.show()