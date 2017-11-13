# Experiment Plotter IFSI Training Fires
#!/usr/bin/env python


import pandas as pd 
import os as os
import numpy as np 
from pylab import * 
from datetime import datetime, timedelta
import shutil
from dateutil.relativedelta import relativedelta
from scipy.signal import butter, filtfilt
from itertools import cycle
from dateutil.relativedelta import relativedelta
from scipy.signal import butter, filtfilt, resample
from nptdms import TdmsFile
import matplotlib.pyplot as plt
import pickle

#Define directories for the info files, data files, and events files
info_dir = '../Info/'
data_dir = '../Data/'
events_dir = info_dir+'Events/'

#import channel list
channels = pd.read_csv(info_dir+'Channels.csv', index_col = 'Channel')
channel_groups = channels.groupby('Primary Chart')

#import test descriptions
test_des = pd.read_csv(info_dir+'Test_Description.csv',index_col = 'Test Name')


# Load data & event pickle dicts
test_data_dict = pickle.load(open(data_dir + 'metric_test_data.dict', 'rb'))
test_events_dict = pickle.load(open(events_dir + 'events.dict', 'rb'))
output_dir = '../Figures/by_experiment/'

for experiment in test_des.index.values:
	 print(experiment)
	 data_df = test_data_dict[experiment]
	 events_df = test_events_dict[experiment]
	 #find firefighter intervention time
	 for event in events_df.index.values:
 				if events_df['Event'][event] == 'Front Door Open' or events_df['Event'][event] == 'Water in Window':
 					ff_int = event
 					break	
	 # data_df =data_df.loc[0:,:]
	 for chart in channel_groups.groups:
	 	fig=plt.figure()
	 	tableau20 = ([(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
							(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
							(148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
							(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
							(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)])
	 	for i in range(len(tableau20)):
	 		r, g, b = tableau20[i]
	 		tableau20[i] = (r / 255., g / 255., b / 255.)
 		# print(events_df)
 		tableau20=cycle(tableau20)
 		plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])
 		for channel in channel_groups.get_group(chart).index.values:
 			if not channel in data_df.columns:
 				continue
 			data = data_df[channel].rolling(window=5, center=True).mean()
 			data = data.loc[0:]
 			data_pre = data.loc[:ff_int]
 			data_post = data.loc[ff_int:]
 			data_at = data.loc[ff_int]
 			




