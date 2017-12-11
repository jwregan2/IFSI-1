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

data_dir = '../Data/'
info_dir = '../Info/'

#import events dictionary
events_dict = pickle.load(open(info_dir+'Events/events.dict', 'rb'))

#import channel list
channels = pd.read_csv(info_dir+'Channels.csv', index_col = 'Channel')

#import test descriptions
test_des = pd.read_csv(info_dir+'Test_Description.csv',index_col = 'Test Name')

#import offset times for wireless gas sensors
offsets = pd.read_csv(info_dir+'Remote_Sensor_Offsets.csv',index_col = 'Experiment')

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
			if not os.path.exists(data_dir+'Wireless_TC_Data/'+str(experiment)+'/'+channel+'.csv'):
				continue
			data_df = pd.read_csv(data_dir+'Wireless_TC_Data/'+str(experiment)+'/'+channel+'.csv',skiprows = 9)
			#define empty column for elapsed time
			elapsed_time_ls =[]
			for t in data_df['Time']:
				timestamp = t[:-3]
				hh,mm,ss = timestamp.split(':')
				elapsed_time = 3600*int(hh) + 60*int(mm) + int(ss) -int(ignition)
				elapsed_time_ls.append(elapsed_time)
			print(channel)

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

				test_df = pd.concat([test_df,data],axis=1)

		elif channels['Type'][channel] == 'Remote Gas':
			print(channel)
			if not os.path.exists(data_dir+'Wireless_Gas_Analyzers/'+str(experiment)+'/'+channels['Label'][channel].replace(' ','_')+'.csv'):
				continue
			data_df = pd.read_csv(data_dir+'Wireless_Gas_Analyzers/'+str(experiment)+'/'+channels['Label'][channel].replace(' ','_')+'.csv')
			#define empty column for elapsed time
			elapsed_time_ls =[]
			for event in exp_events.index.values:
				if 'Victim_Open' in channel:
					if exp_events['Event'][event] == 'Victim 1 Out':
						vic_time = event
				elif 'Victim_Closed' in channel:
					if exp_events['Event'][event] == 'Victim 2 Out':
						vic_time = event
			for t in data_df['Time']:
				timestamp = t.split(' ')[-2]
				# timestamp = timestamp[:-3]
				hh,mm,ss = timestamp.split(':')
				elapsed_time = 3600*int(hh) + 60*int(mm) + int(ss) -int(ignition)+int(offsets[channels['Label'][channel].replace(' ','_')][experiment])-int(vic_time)
				elapsed_time_ls.append(elapsed_time)
			# print(channel)

			data_df['Elapsed Time'] = elapsed_time_ls
			data_df = data_df.set_index('Elapsed Time')
			# print(data_df)
			# exit()



			#check if ignition exists in index of dataframe
			if 0 in data_df.index:
				ign_adj = 0
			else:
				for ix in data.index.values:
					if ix > 0:
						# print(ix-0)
						ign_adj = ix
						break

			#do the same with the end of experiment
			if end_time in data_df.index:
				end_adj = end_time
			else:
				for ix in data.index.values:
					if ix >end_time:
						# print(ix-end_time)
						end_adj = ix
					elif ix == data_df.index.values[-1]:
						# print(ix-end_time)
						end_adj = ix

			if channel[-3:]=='CO2':
				channel_type = 'Reading (Carbon Dioxide)'
			elif channel[-2:]=='CO':
				channel_type = 'Reading (Carbon Monoxide)'
			elif channel[-2:] == 'O2':
				channel_type = 'Reading (Oxygen)'

			data = data_df[channel_type].loc[ign_adj:end_adj]

			if df_flag == True:
				time_index = data.index.values
				test_df = pd.DataFrame(data={'Elapsed Time':time_index,channel:data})
				test_df = test_df.set_index('Elapsed Time')
				df_flag = False
			else:
				data = pd.Series(data, name = channel)
				test_df = pd.concat([test_df,data],axis=1)
				

		else:
			continue


	# print(test_df)
	wireless_dict[experiment] = test_df
	# print(wireless_dict[experiment])


pickle.dump(wireless_dict, open (data_dir+'metric_wireless_data.dict','wb'))







