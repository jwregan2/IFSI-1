# Experiment Plotter IFSI Training Fires
#!/usr/bin/env python


import pandas as pd 
import os as os
import numpy as np 
from pylab import * 
from datetime import datetime, timedelta
import shutil
from itertools import cycle
import matplotlib.pyplot as plt
import pickle

#Flag to determine if secondary charts should be included
secondary_chart_flag = True

#Define directories for the info files, data files, and events files
info_dir = '../Info/'
data_dir = '../Data/'
events_dir = info_dir+'Events/'

#import channel list
channels = pd.read_csv(info_dir+'Channels.csv', index_col = 'Channel')

#import charts info
charts = pd.read_csv(info_dir+'Charts.csv', index_col = 'Chart')

#import test descriptions
test_des = pd.read_csv(info_dir+'Test_Description.csv',index_col = 'Test Name')


# Load data & event pickle dicts
test_data_dict = pickle.load(open(data_dir + 'metric_test_data.dict', 'rb'))
test_events_dict = pickle.load(open(events_dir + 'events.dict', 'rb'))
wireless_data_dict = pickle.load(open(data_dir + 'metric_wireless_data.dict', 'rb'))
#Define output directory
output_dir = '../Figures/by_experiment/'

#Loop through experiment files
for experiment in test_des.index.values:
	# if experiment == 'Experiment_04':
	# 	pass
	# else:
	# 	continue
	output_dir = '../Figures/by_experiment/'+experiment+'/'
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)
	print()
	print(experiment)
	data_df = test_data_dict[experiment]
	wireless_data = wireless_data_dict[experiment]
	events_df = test_events_dict[experiment]

	#find firefighter intervention time
	for event in events_df.index.values:
		if events_df['Event'][event] == 'Front Door Open' or events_df['Event'][event] == 'Water in Window':
			ff_int = event
			water = event
			break	
	#find door time for trans exps
	for event in events_df.index.values:
		if events_df['Event'][event] == 'Front Door Open':
			door =event
	#find end of test data
	for event in events_df.index.values:
		if events_df['Event'][event] == 'End of Experiment' or events_df['Event'][event] == 'Data System Error':
			end_time = event
	#Group channels b y the side of the structure that they were used on

	if test_des['Side'][experiment] == 'Left':
		if secondary_chart_flag == True:
			channel_groups = channels.groupby('Left Secondary Chart')
		else:
			channel_groups = channels.groupby('Left Chart')
	elif test_des['Side'][experiment] == 'Right':
		if secondary_chart_flag == True:
			channel_groups = channels.groupby('Right Secondary Chart')
		else:
			channel_groups = channels.groupby('Right Chart')

	for chart in channel_groups.groups:
		print(chart)
		fig=plt.figure()
		tableau20 = ([(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
						(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
						(148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
						(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
						(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)])
		for i in range(len(tableau20)):
			r, g, b = tableau20[i]
			tableau20[i] = (r / 255., g / 255., b / 255.)

		tableau20=cycle(tableau20)
		plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])
		for channel in channel_groups.get_group(chart).index.values:
			if secondary_chart_flag ==True:
				if test_des['Side'][experiment] == 'Left':
					supp_label =channels['Left Chart'][channel]
				elif test_des['Side'][experiment] == 'Right':
					supp_label =channels['Right Chart'][channel]
			if not channel in data_df.columns:
				if not channel in wireless_data.columns:
					continue

			# if 'Remote Gas' in channels['Type'][channel]:
			# 	data = wireless_data[channel].dropna(how='all')
			# 	data= data.rolling(window=5, center=True).mean()
			# else:
			# 	continue
			# print(channel)
			if 'Remote' in channels['Type'][channel]:
				data = wireless_data[channel].dropna(how='all')
				data= data.rolling(window=5, center=True).mean()

			else:
			#take 5 second moving average of the data for the channel
				data = data_df[channel].rolling(window=5, center=True).mean()

			#cut the pre-ignition data
			data = data.loc[0:]
			#adjust times where the intervention is not within the index to the next second
			if ff_int in data.index:
				pass
			else:
				for ix in data.index.values:
					if ix > ff_int:
						print(ix-ff_int)
						ff_int = ix 						
						break
			
			#divide data into pre- and post-ff intervention
			data_pre = data.loc[:ff_int]
			data_post = data.loc[ff_int:end_time]
			data_at = data.loc[ff_int]
			if test_des['Attack Type'][experiment] == 'Transitional':
				print(channel)
				print(data.loc[water])
				# print('400-500')
				# print(min(data.loc[400:500]))
				# print(max(data.loc[400:500]))
				# print()
				print('water-door')
				print(min(data.loc[water:door]))
				i_min= data.loc[water:door].idxmin()
				print(max(data.loc[i_min:door]))
				# if experiment == 'Experiment_03':

				print()
			##cycle plot markers and colors
			color=next(tableau20)
			marker=next(plot_markers)

			#Plot data

			if secondary_chart_flag== True:
				plt.plot(data_pre.index.values,data_pre,ls='-', marker=marker,markevery = 50,markersize=8,mew=1.5,mec='none',ms=7,label=supp_label+channels['Label'][channel] ,color=color)
			else:
				plt.plot(data_pre.index.values,data_pre,ls='-', marker=marker,markevery = 50,markersize=8,mew=1.5,mec='none',ms=7,label=channels['Label'][channel] ,color=color)
			plt.plot(data_post.index.values,data_post,ls='--',marker=marker,markevery = 50,markersize=8,mew=1.5,mec='none',ms=7,color=color,label='_nolegend_')
			plt.plot(ff_int,data_at,lw=3,ls='--',marker='o',markersize=5,markevery = 50,color='k',label='_nolegend_')
		for event in events_df.index.values:
			if events_df['Event'][event] == 'FD Dispatch':
				fd = event
				continue
		plt.grid(True)
		plt.xlabel('Time (s)', fontsize=16)
		plt.ylabel(charts['Y Label'][chart], fontsize=16)
		plt.xticks(fontsize=16)
		plt.yticks(fontsize=16)
		if secondary_chart_flag == True:
			plt.xlim([fd,600])
		else:
			plt.xlim([0,1000])
		plt.ylim([charts['Y Min'][chart],charts['Y Max'][chart]])
		ax1 = plt.gca()
		ax2=ax1.twiny()
		eventtime=list(range(len(events_df.index.values)))

		for i in events_df.index.values:
			plt.axvline(i,color='0',lw=1) 

		ax2.set_xticks(events_df.index.values)
		plt.setp(plt.xticks()[1], rotation=45)
		ax2.set_xticklabels(events_df['Event'], fontsize=14, ha='left')
		if secondary_chart_flag == True:
			ax2.set_xlim(fd,600)
		else:
			ax2.set_xlim(0,1000)

		
			
		handles1, labels1 = ax1.get_legend_handles_labels()		
		fig.set_size_inches(10, 7)				
		# plt.title('Experiment '+str(experiment)+' '+chart, y=1.08)
		plt.tight_layout()	
		plt.legend(handles1, labels1, fontsize=12,loc='upper left')	
		plt.savefig(output_dir + chart.replace(' ','_') + '.png')
		plt.close('all')	




