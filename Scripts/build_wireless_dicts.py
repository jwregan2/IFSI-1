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

data_dir = '../Data/Wireless_TC_Data/'
info_dir = '../Info/'

#import events dictionary
events_dict = pickle.load(open(info_dir+'Events/events.dict', 'rb'))

#import channel list
channels = pd.read_csv(info_dir+'Channels.csv', index_col = 'Channel')

#import test descriptions
test_des = pd.read_csv(info_dir+'Test_Description.csv',index_col = 'Test Name')

#define a dicitonary for wireless TC dahtuh
wireless_dict = {}
for experiment in test_des.index.values:
	#define events for the experiment
	exp_events = events_dict[experiment]
	print(experiment)
	ignition = exp_events['Time'][0].split('-')[-1]
	hh,mm,ss = ignition.split(':')
	ignition = 3600*int(hh) + 60*int(mm) + int(ss)
	for event in exp_events.index.values:
		if exp_events['Event'][event] == 'End of Experiment' or exp_events['Event'][event] == 'Data System Error':
			end_time = event


	#insert flag to know when to create dataframe
	df_flag = True
	#loop through channels and skip those not remote
	for channel in channels.index.values:

		if channels['Type'][channel] == 'Remote Temperature':
			pass
		else:
			continue
		print(channel)
		data_df = pd.read_csv(data_dir+str(experiment)+'/'+channel+'.csv',skiprows = 9)
		#define empty column for elapsed time
		elapsed_time_ls =[]
		for t in data_df['Time']:
			timestamp = t[:-3]
			hh,mm,ss = timestamp.split(':')
			elapsed_time = 3600*int(hh) + 60*int(mm) + int(ss) -int(ignition)
			elapsed_time_ls.append(elapsed_time)
		data_df['Elapsed Time'] = elapsed_time_ls
		data_df = data_df.set_index('Elapsed Time')



		#check if ignition exists in index of dataframe
		if 0 in data_df.index:
			ign_adj = 0
		elif 1 in data_df.index:
			ign_adj = 1
		else:
			print('panic')

		#do the same with the end of experiment
		if end_time in data_df.index:
			end_adj = end_time
		elif end_time + 1 in data_df.index:
			end_adj = end_time +1
		else:
			end_adj = data_df.index.values[-1]
			# print('error '+str(channel))
			# print()
			# print(data_df)
			# print('panic')
			# exit()

		data = data_df['Process'].loc[ign_adj:end_adj]

		if df_flag == True:
			time_index = data.index.values
			test_df = pd.DataFrame(data={'Elapsed Time':time_index,channel:data})
			test_df = test_df.set_index('Elapsed Time')
			df_flag = False
		else:
			data = pd.Series(data, name=channel)
			# data = 	data.reset_index()
			# print(len(data),len(time_index))
			# data['Elapsed Time'] = time_index[0:len(data)]
			# data = data.set_index('Elapsed Time')

			# data = pd.Series(data, index = time_index[0:len(data)])
			test_df = pd.concat([test_df,data],axis=1)

	# print(test_df)
	wireless_dict[experiment] = test_df
	print()

pickle.dump(wireless_dict, open (data_dir+'metric_wireless_data.dict','wb'))







