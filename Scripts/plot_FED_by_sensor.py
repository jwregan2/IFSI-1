import pandas as pd 
import os as os
import numpy as np 
from pylab import * 
from datetime import datetime, timedelta
import shutil
from itertools import cycle
import matplotlib.pyplot as plt
import pickle

#Define directories for the info files, data files, and events files
info_dir = '../Info/'
data_dir = '../Data/'
events_dir = info_dir+'Events/'

#import channel list
channels = pd.read_csv(info_dir+'FED_Channels.csv', index_col = 'Chart')

#import charts info
# charts = pd.read_csv(info_dir+'Charts.csv', index_col = 'Chart')

#import test descriptions
test_des = pd.read_csv(info_dir+'Test_Description.csv',index_col = 'Test Name')
test_groups = test_des.groupby('Attack Type')

#import victim times
victim_times = pd.read_csv(info_dir+'Victim.csv', index_col = 'Event')

output_dir = '../Figures/by_FED_location/'
if not os.path.exists(output_dir):
	os.makedirs(output_dir)

# Load data & event pickle dicts
test_data_dict = pickle.load(open(data_dir + 'metric_test_data.dict', 'rb'))
test_events_dict = pickle.load(open(events_dir + 'events.dict', 'rb'))
FED_dict = pickle.load(open('../Tables/FED_gas.dict', 'rb'))

for chart in channels.index.values:
	fig = plt.figure()
	#print sensor name
	print()
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
	for experiment in test_des.index.values:
		data_df = FED_dict[experiment]
		events_df = test_events_dict[experiment]
		for event in events_df.index.values:
			#find FD Dispatch
			if events_df['Event'][event] == 'FD Dispatch':
				disp_time = event
			#find firefighter intervention time
			if events_df['Event'][event] == 'Front Door Open' or events_df['Event'][event] == 'Water in Window':
				ff_int = event
				break	
		#find end of test data
		for event in events_df.index.values:
			if events_df['Event'][event] == 'End of Experiment' or events_df['Event'][event] == 'Data System Error':
				end_time = event	
		if chart not in data_df.columns:
			continue

		#add markers for bedroom ventilaltion

		if 'Near Bedroom' in chart or 'Near Closed Bedroom' in chart:
			if not np.isnan(victim_times[experiment]['Near BR Door Open']):
				door_time = victim_times[experiment]['Near BR Door Open']
				door_int = door_time + disp_time
				door_flag =True
		elif 'Far Bedroom' in chart or 'Far Closed Bedroom' in chart:
			if not np.isnan(victim_times[experiment]['Far BR Door Open']):
				door_time = victim_times[experiment]['Far BR Door Open']
				door_int = door_time + disp_time
				door_flag =True

		data = data_df[chart]
		#divide data into pre- and post-ff intervention
		data_pre = data.loc[:ff_int]
		data_post = data.loc[ff_int:end_time]
		data_at = data.loc[ff_int]
		if door_flag == True:
			if door_int in data.index:
				pass
			else:
				for ix in data.index.values:
					if ix > door_int:
						print(ix-door_int)
						door_int = ix 						
						break
			data_door = data.loc[door_int]
		##cycle plot markers and colors
		color=next(tableau20)
		marker=next(plot_markers)

		#Plot data
		plt.plot(data_pre.index.values,data_pre,ls='-', marker=marker,markevery=500,markersize=8,mew=1.5,mec='none',ms=7,label=experiment.replace('_',' '),color=color)
		plt.plot(data_post.index.values,data_post,ls='--',marker=marker,markevery=500,markersize=8,mew=1.5,mec='none',ms=7,color=color,label='_nolegend_')
		plt.plot(ff_int,data_at,lw=3,ls='--',marker='o',markersize=5,color='k',label='_nolegend_')
		if door_flag == True:
			plt.plot(door_int,data_door,lw=3,ls='--',marker='^',markersize=5,color='r',label='_nolegend_')
			door_flag = False

	plt.grid(True)
	plt.xlabel('Time (s)', fontsize=16)
	# plt.ylabel(charts['Y Label'][chart], fontsize=16)
	plt.xticks(fontsize=16)
	plt.yticks(fontsize=16)
	plt.xlim([0,1000])
	# plt.ylim([charts['Y Min'][chart],charts['Y Max'][chart]])
	ax1 = plt.gca()
	handles1, labels1 = ax1.get_legend_handles_labels()		
	fig.set_size_inches(10, 7)				
	# plt.title('Experiment '+str(experiment)+' '+chart, y=1.08)
	plt.tight_layout()	
	plt.legend(handles1, labels1, loc = 'upper left', fontsize=12)	
	plt.savefig(output_dir + chart+'.png')
	plt.close('all')	

##PLOT FED RATE OF CHANGE##

print('---------------------------------------------------------------')
output_dir = '../Figures/rate_by_FED_location_/'
if not os.path.exists(output_dir):
	os.makedirs(output_dir)
for chart in channels.index.values:
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
	for group in test_groups.groups:
		print(group)
		color = next(tableau20)
		#define name of "water on" event
		if group =='Transitional':
			supp_event = 'Water in Window'
		elif group =='Interior':
			supp_event = 'Nozzle FF Reaches Hallway'
		else:
			print('break')
		for experiment in test_groups.get_group(group).index.values:
			print(experiment)
			data_df = FED_dict[experiment]
			events_df = test_events_dict[experiment]
			for event in events_df.index.values:
				#find FD Dispatch
				if events_df['Event'][event] == 'FD Dispatch':
					disp_time = event				
				#find firefighter intervention time
				if events_df['Event'][event] == 'Front Door Open' or events_df['Event'][event] == 'Water in Window':
					ff_int = event
					break	
			#find end of test data
			for event in events_df.index.values:
				if events_df['Event'][event] == supp_event:
					supp_time = event	
				if events_df['Event'][event] == 'End of Experiment' or events_df['Event'][event] == 'Data System Error':
					end_time = event	
			if chart not in data_df.columns:
				continue
			print(supp_time,ff_int)
			#add markers for bedroom ventilaltion

			if 'Near Bedroom' in chart or 'Near Closed Bedroom' in chart:
				if not np.isnan(victim_times[experiment]['Near BR Door Open']):
					door_time = victim_times[experiment]['Near BR Door Open']
					door_int = door_time + disp_time
					door_flag =True
			elif 'Far Bedroom' in chart or 'Far Closed Bedroom' in chart:
				if not np.isnan(victim_times[experiment]['Far BR Door Open']):
					door_time = victim_times[experiment]['Far BR Door Open']
					door_int = door_time + disp_time
					door_flag =True

			data = data_df[chart+' rate']
			#divide data into pre- and post-ff intervention
			data_pre = data.loc[:ff_int]
			data_post = data.loc[ff_int:end_time]
			data_at = data.loc[ff_int]
			data_supp = data.loc[supp_time]
			if door_flag == True:
				if door_int in data.index:
					pass
				else:
					for ix in data.index.values:
						if ix > door_int:
							print(ix-door_int)
							door_int = ix 						
							break
				data_door = data.loc[door_int]
			##cycle plot markers and colors

			marker=next(plot_markers)

			#Plot data
			plt.plot(data_pre.index.values,data_pre,ls='-', marker=marker,markevery=500,markersize=8,mew=1.5,mec='none',ms=7,label=experiment.replace('_',' '),color=color)
			plt.plot(data_post.index.values,data_post,ls='--',marker=marker,markevery=500,markersize=8,mew=1.5,mec='none',ms=7,color=color,label='_nolegend_')
			plt.plot(supp_time,data_supp,lw=3,ls='--',marker='s',markersize=7,color='b',label='_nolegend_')
			plt.plot(ff_int,data_at,lw=3,ls='--',marker='o',markersize=5,color='k',label='_nolegend_')

			if door_flag == True:
				plt.plot(door_int,data_door,lw=3,ls='--',marker='^',markersize=7,color='r',label='_nolegend_')
				door_flag = False

	plt.grid(True)
	plt.xlabel('Time (s)', fontsize=16)
	# plt.ylabel(charts['Y Label'][chart], fontsize=16)
	plt.xticks(fontsize=16)
	plt.yticks(fontsize=16)
	plt.xlim([0,1000])
	# plt.ylim([charts['Y Min'][chart],charts['Y Max'][chart]])
	ax1 = plt.gca()
	handles1, labels1 = ax1.get_legend_handles_labels()		
	fig.set_size_inches(10, 7)				
	# plt.title('Experiment '+str(experiment)+' '+chart, y=1.08)
	plt.tight_layout()	
	plt.legend(handles1, labels1, loc = 'upper left', fontsize=12)	
	plt.savefig(output_dir + chart+'_rate.png')
	plt.close('all')	