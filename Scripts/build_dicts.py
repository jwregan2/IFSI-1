from __future__ import division
import numpy as np
import os as os
import numpy.ma as ma
import pandas as pd
import itertools
from pylab import *
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import pickle

##Build dictionary of events for each experimetns named events_dict

#Define directories for the info files, data files, and events files
info_dir = '../Info/'
data_dir = '../Data/'
events_dir = info_dir+'Events/'

#import channel list

channels = pd.read_csv(info_dir+'Channels.csv', index_col = 'Channel')

#import test descriptions

test_des = pd.read_csv(info_dir+'Test_Description.csv',index_col = 'Test Name')

events_dict = {}
data_dict = {}

for test in test_des.index.values:
	print(test)
	events_df = pd.read_csv(events_dir+test+'_Events.csv')
	ignition = events_df['Time'][0].split('-')[-1]
	hh,mm,ss = ignition.split(':')
	ignition = 3600*int(hh) + 60*int(mm) + int(ss)
	event_times = []
	for time in events_df['Time']:
		timestamp = time.split('-')[-1]
		hh,mm,ss = timestamp.split(':')
		timestamp = 3600*int(hh)+60*int(mm)+int(ss)-int(ignition)
		event_times.append(timestamp)
	events_df['Time Elapsed']=event_times
	events_df = events_df.set_index('Time Elapsed')
	events_dict[test] = events_df
	#Read data dataframe 
	data_df = pd.read_csv(data_dir+test+'.csv')

	#Make a list of elapsed time

	elasped_time = []
	for t in data_df['Time']:

		# if np.isnan(t)==True:
		# 	continue
		# print(t)
		timestamp = t.split(' ')[-1]

		hh,mm,ss = timestamp.split(':')
		timestamp = 3600*int(hh)+60*int(mm)+int(ss)-int(ignition)
		elasped_time.append(timestamp)
	#Set index as elapsed time
	data_df['Elapsed Time'] = elasped_time
	data_df = data_df.set_index('Elapsed Time')

	#Divide data datafrane into
	pre_exp_data = data_df.loc[:-1,:]
	exp_data = data_df.loc[0:,:]

	test_df = pd.DataFrame(data={'Elapsed Time':data_df.index.values,'Time':data_df['Time']})
	test_df = test_df.set_index('Elapsed Time')

	for channel in channels.index.values:
		#If channel not in df, continue
		if not channel in data_df.columns:
			continue
		scale_factor = channels['Scale Factor'][channel]
		offset = channels['Offset'][channel]	
		if channels['Type'][channel] == 'Temperature':
			scaled_data = data_df[channel].round(1)

		elif channels['Type'][channel] == 'Heat Flux':
			zero_data = data_df[channel] - np.average(pre_exp_data[channel])
			scaled_data = zero_data * scale_factor + offset
			scaled_data = scaled_data.round(2)
		elif channels['Type'][channel] == 'Gas':
			transport_time = channels['Transport'][channel]
			scaled_data = data_df[channel].iloc[int(transport_time):]*scale_factor+offset
			scaled_data = scaled_data.round(2)
			nan_array = np.empty(len(data_df.index.values)-len(scaled_data.index.values))
			nan_array[:] =  np.NaN
			scaled_data = pd.Series(np.concatenate([scaled_data.tolist(),nan_array]), index = test_df.index.values)

		elif channels['Type'][channel] == 'Gas (PPM)':
			transport_time = channels['Transport'][channel]
			scaled_data = data_df[channel].iloc[int(transport_time):]*scale_factor+offset
			scaled_data = scaled_data.round(2)
			nan_array = np.empty(len(data_df.index.values)-len(scaled_data.index.values))
			nan_array[:] =  np.NaN
			scaled_data = pd.Series(np.concatenate([scaled_data.tolist(),nan_array]), index = test_df.index.values)
		elif channels['Type'][channel] == 'Pressure':
			scaled_data = data_df[channel] * scale_factor + offset
			scaled_data =scaled_data - np.average(scaled_data.loc[:-1])
			scaled_data = scaled_data.round(1)


		test_df[channel] = scaled_data
	data_dict[test] = test_df
pickle.dump(events_dict, open (events_dir+'events.dict','wb'))
pickle.dump(data_dict, open (data_dir+'metric_test_data.dict','wb'))






