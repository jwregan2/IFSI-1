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


for experiment in test_des.index.values:
	events_df = test_events_dict[experiment].reset_index()
	events_df = events_df.set_index('Event')
	if test_des['Attack Type'][experiment] == 'Transitional':
		ff_int = events_df['Time Elapsed']['Water in Window']
	elif test_des['Attack Type'][experiment] == 'Interior':
		ff_int = events_df['Time Elapsed']['Nozzle FF Reaches Hallway']
	# ff_int = events_df['Time Elapsed']['FD Dispatch']
	data_df = FED_dict[experiment]	
	for loc in data_df.columns:
		if 'rate' in loc:
			continue
		else:
			if error_exps['Skip'][experiment] == loc:
				FED_int_df.loc[experiment,loc]='n.a'
				continue
			int_data = max(data_df[loc])#[ff_int]
			FED_int_df.loc[experiment,loc]=np.round(int_data,2)

for loc in FED_int_df.columns:
	FED_ls = []
	for experiment in FED_int_df[loc].index.values:
		if error_exps['Skip'][experiment] == loc:
			print(experiment,loc)
			continue
		FED_ls.append(FED_int_df[loc][experiment])
	print(loc)
	print(str(np.mean(FED_ls))+' +- ' + str(np.std(FED_ls)))
	print(np.std(FED_ls)/np.mean(FED_ls))
	print('max: '+str(max(FED_ls)))
	print('min: '+str(min(FED_ls)))
	print()
print(FED_int_df)

print('-------------------------------------------------------------')
print('find time to inflection point in FED')

inflection_df = pd.DataFrame(np.zeros((nrows,1)))

inflection_df['Experiment']=Exp_Names
inflection_df = inflection_df.set_index('Experiment')

for experiment in test_des.index.values:
	events_df = test_events_dict[experiment].reset_index()
	events_df = events_df.set_index('Event')
	if test_des['Attack Type'][experiment] == 'Transitional':
		ff_int = events_df['Time Elapsed']['Water in Window']
	elif test_des['Attack Type'][experiment] == 'Interior':
		ff_int = events_df['Time Elapsed']['Front Door Open']

	data_df = FED_dict[experiment]

	
	for loc in data_df.columns:
		if 'rate' in loc:
			pass
		else:
			continue
		index = data_df[loc].idxmax(axis=0)
		inflection_df.loc[experiment,loc]=np.round(index-ff_int)

print()
attack_groups = test_des.groupby('Attack Type')
for column in inflection_df.columns:
	if column ==0:
		continue
	print()
	print(column)
	print('Transitional')
	trans_ls = []
	for experiment in attack_groups.get_group('Transitional').index.values:
		if str(error_exps['Skip'][experiment]) +' rate' == column:
			continue
		elif experiment in ['Experiment_03','Experiment_05']:
			continue
		trans_ls.append(inflection_df.loc[experiment,column])
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
		int_ls.append(inflection_df.loc[experiment,column])
	mean = np.mean(int_ls)
	stdev = np.std(int_ls)
	print('mean: '+str(mean)+'+-'+str(stdev))

	print('t-test')
	print(stats.ttest_ind(np.array(trans_ls),np.array(int_ls),equal_var=False))

	print()
# print(inflection_df)

output_table_loc='../Tables/'
if not os.path.exists(output_table_loc):
	os.makedirs(output_table_loc)
inflection_df.to_csv(output_table_loc+'time_to_inflection.csv')
