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
attack_groups = test_des.groupby('Attack Type')
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
 
#build datuhframe for rates
Rates_tabe=pd.DataFrame(np.zeros((N_rows,N_columns)))
Rates_tabe.columns=['Experiment','Near Hall','Near Bedroom','Far Bedroom','Far Hall']
Rates_tabe['Experiment']=Exp_Names
Rates_tabe=Rates_tabe.set_index('Experiment')

Delta_t_df=pd.DataFrame(np.zeros((N_rows,N_columns)))
Delta_t_df.columns=['Experiment','Near Hall','Near Bedroom','Far Bedroom','Far Hall']
Delta_t_df['Experiment']=Exp_Names
Delta_t_df=Delta_t_df.set_index('Experiment')
#import channel list
channels = pd.read_csv(info_dir+'FED_Channels.csv', index_col = 'Chart')

window = 60

for experiment in Temps_tabe.index.values:
	print()
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
		#find average value in 30 s before ff intervention
		int_average=np.mean(dahtuh.loc[ff_int-window:ff_int])
		#place value in a table
		Temps_tabe.loc[experiment,group] = int_average
		#assemble rate of change list for window seconds before and after ff_int
		roc_ls =[0]
		elapsed_time=dahtuh.loc[ff_int-window:ff_int+window].index.values
		supp_ar =np.array(dahtuh.loc[ff_int-window:ff_int+window])
		for i in range(len(supp_ar)-1):
				roc_ls.append(supp_ar[i+1]-supp_ar[i])
		data = pd.Series(roc_ls,index = elapsed_time)

		mindex_rate = data.loc[ff_int:ff_int+window].idxmin()
		mindex_temp = dahtuh.loc[ff_int:ff_int+window].idxmin()


		# for t in data.index.values:
		# 	#only concenred with avlues after the absolute minimum
		# 	if t < mindex:
		# 		continue
		# 	if data[t] > 0.0:
		# 		delta_t = dahtuh.loc[ff_int]-dahtuh.loc[t]
		# 		break
		delta_t = (dahtuh.loc[ff_int]-dahtuh.loc[mindex_temp])
		decrease_time = mindex_rate#-ff_int
		# print(np.mean(data.loc[ff_int-30:ff_int]))
		# print(np.mean(data.loc[ff_int:ff_int+30]))
		Rates_tabe.loc[experiment,group] =decrease_time
		Delta_t_df.loc[experiment,group] =delta_t
		print()
for column in Temps_tabe.columns:
	print(column)
	ave = np.mean(Temps_tabe[column])
	std = np.std(Temps_tabe[column])
	print(str(ave)+ ' =- '+str(std))
	print(std/ave)
	print()
# print(Delta_t_df)
# print(Rates_tabe)

print('Near')
print(stats.ttest_ind(np.array(Temps_tabe['Near Bedroom']),np.array(Temps_tabe['Near Hall']),equal_var=False))
print('FAr')

print(stats.ttest_ind(np.array(Temps_tabe['Far Bedroom']),np.array(Temps_tabe['Far Hall']),equal_var=False))

print('---------------------------------------------------------')
print('Compare times to minimum rate of change')
for column in Rates_tabe.columns:
	if column ==0:
		continue
	print()
	print(column)
	print('Transitional')
	trans_ls = []
	for experiment in attack_groups.get_group('Transitional').index.values:
		if experiment in ['Experiment_03','Experiment_05']:
			continue
		trans_ls.append(Rates_tabe.loc[experiment,column])
	mean = np.mean(trans_ls)
	stdev = np.std(trans_ls)
	print('mean: '+str(mean)+'+-'+str(stdev))

	print('Interior')
	int_ls =[]
	for experiment in attack_groups.get_group('Interior').index.values:
		if str(error_exps['Skip'][experiment]) +' rate' == column:
			continue
		elif experiment in ['Experiment_03','Experiment_05']:
			continue
		int_ls.append(Rates_tabe.loc[experiment,column])
	mean = np.mean(int_ls)
	stdev = np.std(int_ls)
	print('mean: '+str(mean)+'+-'+str(stdev))

	print('t-test')
	print(stats.ttest_ind(np.array(trans_ls),np.array(int_ls),equal_var=False))

	print()


print('---------------------------------------------------------')
print('Compare temperature decreases')
for column in Delta_t_df.columns:
	if column ==0:
		continue
	print()
	print(column)
	print('Transitional')
	trans_ls = []
	for experiment in attack_groups.get_group('Transitional').index.values:
		if experiment in ['Experiment_03','Experiment_05']:
			continue
		trans_ls.append(Delta_t_df.loc[experiment,column])
	mean = np.mean(trans_ls)
	stdev = np.std(trans_ls)
	print('mean: '+str(mean)+'+-'+str(stdev))

	print('Interior')
	int_ls =[]
	for experiment in attack_groups.get_group('Interior').index.values:
		if str(error_exps['Skip'][experiment]) +' rate' == column:
			continue
		elif experiment in ['Experiment_03','Experiment_05']:
			continue
		int_ls.append(Delta_t_df.loc[experiment,column])
	mean = np.mean(int_ls)
	stdev = np.std(int_ls)
	print('mean: '+str(mean)+'+-'+str(stdev))

	print('t-test')
	print(stats.ttest_ind(np.array(trans_ls),np.array(int_ls),equal_var=False))

	print()
# print(Rates_tabe)





