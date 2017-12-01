import pandas as pd 
import os as os
import numpy as np 
from pylab import * 
from scipy import stats
import pickle

info_dir = '../Info/'
data_dir = '../Data/'
events_dir = info_dir + 'Events/'

#import test descriptions
test_des = pd.read_csv(info_dir+'Test_Description.csv',index_col = 'Test Name')

#import victim times
victim_times = pd.read_csv(info_dir+'Victim.csv', index_col = 'Event')

#import sensors error data
error_exps = pd.read_csv(info_dir + 'gas_errors.csv',index_col = 'Experiment')

test_events_dict = pickle.load(open(events_dir + 'events.dict', 'rb'))
FED_dict = pickle.load(open('../Tables/FED_gas.dict', 'rb'))
test_data_dict = pickle.load(open(data_dir + 'metric_test_data.dict', 'rb'))

print('assess repeatability of temperature measurements at victim locations at time of FF intervention')

#build dataframe for temp averages
N_rows=12
N_columns=5
Temps_tabe=pd.DataFrame(np.zeros((N_rows,N_columns)))
Temps_tabe.columns=['Experiment','Near Hall','Near Bedroom','Far Bedroom','Far Hall']
Exp_Names=[]
for f in test_des.index.values:
		Exp_Names.append(f)
Temps_tabe['Experiment']=Exp_Names
Temps_tabe=Temps_tabe.set_index('Experiment')

#import channel list
channels = pd.read_csv(info_dir+'FED_Channels.csv', index_col = 'Chart')

for experiment in Temps_tabe.index.values:
	# output_dir = '../Figures/by_experiment/'+experiment+'/'
	# if not os.path.exists(output_dir):
	# 	os.makedirs(output_dir)
	print()
	print(experiment)
	data_df = test_data_dict[experiment]
	events_df = test_events_dict[experiment]

	#find firefighter intervention time
	for event in events_df.index.values:
		if events_df['Event'][event] == 'Front Door Open' or events_df['Event'][event] == 'Water in Window':
			ff_int = event
			break	
	#find end of test data
	for event in events_df.index.values:
		if events_df['Event'][event] == 'End of Experiment' or events_df['Event'][event] == 'Data System Error':
			end_time = event
	side = test_des['Side'][experiment]

	for group in Temps_tabe.columns:
		dahtuh = data_df[channels[side+' Temp Name'][group]].loc[0:end_time]
		int_average=np.mean(dahtuh.loc[ff_int-30:ff_int])
		Temps_tabe.loc[experiment,group] = int_average

for column in Temps_tabe.columns:
	print(column)
	ave = np.mean(Temps_tabe[column])
	std = np.std(Temps_tabe[column])
	print(str(ave)+ ' =- '+str(std))
	print(std/ave)
	print()

# print(Temps_tabe)





