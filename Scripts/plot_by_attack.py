import pandas as pd 
import os as os
import numpy as np 
from pylab import * 
from datetime import datetime, timedelta
import shutil
from itertools import cycle
import matplotlib.pyplot as plt
import pickle
##FLAG##
seperate_charts = True

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
test_groups = test_des.groupby('Attack Type')

#import list of sensors that are to be compared
sensors = pd.read_csv(info_dir+'Sensors_to_compare.csv',index_col = 'Sensor')

# Load data & event pickle dicts
test_data_dict = pickle.load(open(data_dir + 'metric_test_data.dict', 'rb'))
test_events_dict = pickle.load(open(events_dir + 'events.dict', 'rb'))


for chart in sensors.index.values:
	if seperate_charts ==False:
		output_dir = '../Figures/by_attack/'

		if not os.path.exists(output_dir):
				os.makedirs(output_dir)
		fig = plt.figure()
		#print sensor name
		print()
		print(chart)
		fig=plt.figure()
		tableau20 = ([(31, 119, 180),  (214, 39, 40), (199, 199, 199),(197, 176, 213),(174, 199, 232), (255, 127, 14), (255, 187, 120),
						(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
						(148, 103, 189),  (140, 86, 75), (196, 156, 148),
						(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
						(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)])
		for i in range(len(tableau20)):
			r, g, b = tableau20[i]
			tableau20[i] = (r / 255., g / 255., b / 255.)

		tableau20=cycle(tableau20)
		plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])

	#cycle through exeriments
	for group in test_groups.groups:
		if seperate_charts ==True:
			output_dir = '../Figures/by_attack/'+group+'/'

			if not os.path.exists(output_dir):
					os.makedirs(output_dir)
			fig = plt.figure()
			#print sensor name
			print()
			print(chart)
			fig=plt.figure()
			tableau20 = ([(31, 119, 180),  (214, 39, 40), (199, 199, 199),(197, 176, 213),(174, 199, 232), (255, 127, 14), (255, 187, 120),
							(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
							(148, 103, 189),  (140, 86, 75), (196, 156, 148),
							(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
							(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)])
			for i in range(len(tableau20)):
				r, g, b = tableau20[i]
				tableau20[i] = (r / 255., g / 255., b / 255.)

			tableau20=cycle(tableau20)
			plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])
		else:
			color=next(tableau20)
		for experiment in test_groups.get_group(group).index.values:
			data_df = test_data_dict[experiment]
			events_df = test_events_dict[experiment]

			if test_des['Side'][experiment] == 'Left':
				channel = sensors['Left Sensor'][chart]
			elif test_des['Side'][experiment] == 'Right':
				channel = sensors['Right Sensor'][chart]

			if not channel in data_df.columns:
	 			continue

			#find firefighter intervention time
			for event in events_df.index.values:
				if events_df['Event'][event] == 'Front Door Open' or events_df['Event'][event] == 'Water in Window':
					ff_int = event
					break	
			#find end of test data
			for event in events_df.index.values:
				if events_df['Event'][event] == 'End of Experiment' or events_df['Event'][event] == 'Data System Error':
					end_time = event

			data = data_df[channel]
			#take 5 second moving average of the data for the channel
			data = data_df[channel].rolling(window=5, center=True).mean()

			#cut the pre-ignition data
			data = data.loc[0:]

			#divide data into pre- and post-ff intervention
			data_pre = data.loc[:ff_int]
			data_post = data.loc[ff_int:end_time]
			data_at = data.loc[ff_int]

			##cycle plot markers and colors
			if seperate_charts ==True:
				color=next(tableau20)


			marker=next(plot_markers)

			#Plot data
			plt.plot(data_pre.index.values,data_pre,ls='-', marker=marker,markevery=500,markersize=8,mew=1.5,mec='none',ms=7,label=experiment[-2:]+' ('+str(test_des['Attack Type'][experiment])+')',color=color)
			plt.plot(data_post.index.values,data_post,ls='--',marker=marker,markevery=500,markersize=8,mew=1.5,mec='none',ms=7,color=color,label='_nolegend_')
			plt.plot(ff_int,data_at,lw=3,ls='--',marker='o',markersize=5,color='k',label='_nolegend_')
		if seperate_charts == True:
			plt.grid(True)
			plt.xlabel('Time (s)', fontsize=16)
			plt.ylabel(sensors['Y Label'][chart], fontsize=16)
			plt.xticks(fontsize=16)
			plt.yticks(fontsize=16)
			plt.xlim([0,1000])
			plt.ylim([sensors['Y Min'][chart],sensors['Y Max'][chart]])
			ax1 = plt.gca()
			handles1, labels1 = ax1.get_legend_handles_labels()		
			fig.set_size_inches(10, 7)				
			# plt.title('Experiment '+str(experiment)+' '+chart, y=1.08)
			plt.tight_layout()	
			plt.legend(handles1, labels1, fontsize=12,ncol = 2)	
			plt.savefig(output_dir + chart.replace(' ','_') + '.png')
			plt.close('all')	
			plt.grid(True)
	if seperate_charts == False:
		plt.xlabel('Time (s)', fontsize=16)
		plt.ylabel(sensors['Y Label'][chart], fontsize=16)
		plt.xticks(fontsize=16)
		plt.yticks(fontsize=16)
		plt.xlim([0,1000])
		plt.ylim([sensors['Y Min'][chart],sensors['Y Max'][chart]])
		ax1 = plt.gca()
		handles1, labels1 = ax1.get_legend_handles_labels()		
		fig.set_size_inches(10, 7)				
		# plt.title('Experiment '+str(experiment)+' '+chart, y=1.08)
		plt.tight_layout()	
		plt.legend(handles1, labels1, fontsize=12,ncol = 2)	
		plt.savefig(output_dir + chart.replace(' ','_') + '.png')
		plt.close('all')	




