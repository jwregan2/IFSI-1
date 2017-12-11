import pandas as pd 
import os as os
import numpy as np 
from pylab import * 
from scipy import stats
import pickle
from itertools import cycle
import matplotlib.pyplot as plt

info_dir = '../Info/'
data_dir = '../Data/'
events_dir = info_dir + 'Events/'

#import test descriptions
test_des = pd.read_csv(info_dir+'Test_Description.csv',index_col = 'Test Name')

#import victim times
victim_times = pd.read_csv(info_dir+'Victim.csv', index_col = 'Event')

#import attack time
attack_times = pd.read_csv(info_dir+'Fire_attack.csv',index_col = 'Event')

#import sensors error data
error_exps = pd.read_csv(info_dir + 'gas_errors.csv',index_col = 'Experiment')

output_location = '../Figures/br_compare/'
#Build dataframe to hold results

nrows = 12
ncols = 5


column_headers = ['Experiment','Near Hall','Far Hall','Near Bedroom','Far Bedroom']
FED_int_df = pd.DataFrame(np.zeros((nrows,ncols)))
FED_int_df.columns = column_headers
Exp_Names=[]
for f in test_des.index.values:
	Exp_Names.append(f)
FED_int_df['Experiment']=Exp_Names
FED_int_df = FED_int_df.set_index('Experiment')
test_events_dict = pickle.load(open(events_dir + 'events.dict', 'rb'))
FED_dict = pickle.load(open('../Tables/FED_gas.dict', 'rb'))

#Find maximum FEDS for each static victim lcoation or FED at time of FF intervention
interior_ls=[]
trans_ls=[]
for experiment in test_des.index.values:
	events_df = test_events_dict[experiment].reset_index()
	events_df = events_df.set_index('Event')
	if test_des['Attack Type'][experiment] == 'Transitional':
		ff_int = events_df['Time Elapsed']['Water in Window']
		int_start =events_df['Time Elapsed']['Front Door Open']
		print(experiment)
		trans_ls.append(int_start-ff_int)

	elif test_des['Attack Type'][experiment] == 'Interior':
		ff_int = events_df['Time Elapsed']['Nozzle FF Reaches Hallway']
		int_start =events_df['Time Elapsed']['Front Door Open']
		print(experiment)
		interior_ls.append(ff_int-int_start)
	# ff_int = events_df['Time Elapsed']['FD Dispatch']
	data_df = FED_dict[experiment]	
	for loc in data_df.columns:
		if 'rate' in loc:
			continue
		else:
			if error_exps['Skip'][experiment] == loc:
				# FED_int_df.loc[experiment,loc]='n.a'
				continue
			int_data = max(data_df[loc])#[ff_int]
			FED_int_df.loc[experiment,loc]=np.round(int_data,2)

for loc in ['Near','Far']:

	fig=plt.figure()
	plt.xlabel('Maximum Gas FED',fontsize=18)
	plt.ylabel('Maximum Temperature FED',fontsize=18)
	ax =plt.gca()
	ax.set_axisbelow(True)
	plt.grid(linestyle='-',linewidth = 1.5)
	ax.set_xscale('log')
	ax.set_yscale('log')
	ax.set_xlim([.01,50])
	ax.set_ylim([.01,50])
	for axis in [ax.xaxis, ax.yaxis]:
		 axis.set_major_formatter(ScalarFormatter())
	plt.xticks(fontsize=16)
	plt.yticks(fontsize=16)
	tableau20 = [(31, 119, 180), (255, 187, 120), (196, 156, 148),(140, 86, 75), (158, 218, 229), (23, 190, 207),(174, 199, 232), (255, 127, 14), (255, 187, 120),
		(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
		(148, 103, 189), (197, 176, 213), 
		(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
		(188, 189, 34), (219, 219, 141)  ]
	for i in range(len(tableau20)):
		r, g, b = tableau20[i]
		tableau20[i] = (r / 255., g / 255., b / 255.)
	tableau20=cycle(tableau20)
	plot_markers = cycle(['s','8',  '^', 'x', 'd', 'h', 'p','v','D','*','<','>','H'])

	for room in [' Bedroom',' Hall']:
		if 'Hall' in room:
			group = 'Exposed'
		elif 'Bedroom' in room:
			group = 'Isolated'
		xerr=[]
		yerr=[]
		gas_fed = FED_int_df[loc+room]
		temp_fed= FED_int_df[loc+room+' Temp']
		for gas in gas_fed:
			xerr.append(0.35*gas)
		for temp in temp_fed:
			yerr.append(0.35*temp)
		ax.errorbar(gas_fed, temp_fed, yerr = yerr, xerr =xerr, color = next(tableau20), markersize = 5, marker = next(plot_markers),  label = group, fmt ='o')
	fig.set_size_inches(10, 7)
	plt.tight_layout()
	plt.plot([1.0,1.0],[0,1.0],color='r',lw=2)
	plt.plot([0,1.0],[1.0,1.0],color='r',lw=2)
	handles1, labels1 = ax.get_legend_handles_labels()
	plt.legend(handles1, labels1, loc ='upper left',  fontsize=15)	
	if not os.path.exists(output_location):
		os.makedirs(output_location)
	plt.savefig(output_location +loc+'.pdf')
	plt.close('all')
print('BR gas')
print(stats.ttest_ind(np.array(FED_int_df['Near Bedroom']),np.array(FED_int_df['Far Bedroom']),equal_var=False))
print()
print('BR temp')
print(stats.ttest_ind(np.array(FED_int_df['Near Bedroom Temp']),np.array(FED_int_df['Far Bedroom Temp']),equal_var=False))
print()
print('far temp')
print(stats.ttest_ind(np.array(FED_int_df['Far Hall Temp']),np.array(FED_int_df['Far Bedroom Temp']),equal_var=False))
print()
print()
print('far gas')
print(stats.ttest_ind(np.array(FED_int_df['Far Hall']),np.array(FED_int_df['Far Bedroom']),equal_var=False))
print()
print('near BR')
print(stats.ttest_ind(np.array(FED_int_df['Near Hall']),np.array(FED_int_df['Near Hall Temp']),equal_var=False))
print()
print('far BR')
print(stats.ttest_ind(np.array(FED_int_df['Far Hall']),np.array(FED_int_df['Far Hall Temp']),equal_var=False))
print()