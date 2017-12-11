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

#import attack time
attack_times = pd.read_csv(info_dir+'Fire_attack.csv',index_col = 'Event')

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
				FED_int_df.loc[experiment,loc]='n.a'
				continue
			int_data = max(data_df[loc])#[ff_int]
			FED_int_df.loc[experiment,loc]=np.round(int_data,2)
print(np.mean(interior_ls))
print(np.mean(trans_ls))

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
exit()
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

print('-------------------------------------------------------------')
print('rate at time of door open and average rate in 60 s after')

FED_int_df = pd.DataFrame(np.zeros((nrows,5)))
FED_int_df.columns = ['Experiment','Near Bedroom Rate at door open','Near Bedroom average rate+ 1 min','Far Bedroom Rate at door open','Far Bedroom average rate+ 1 min']
FED_int_df['Experiment']=Exp_Names
FED_int_df = FED_int_df.set_index('Experiment')

for experiment in test_des.index.values:
	events_df = test_events_dict[experiment].reset_index()
	events_df = events_df.set_index('Event')
	ff_int = events_df['Time Elapsed']['FD Dispatch']
	if experiment == 'Experiment_01':
		end_time =  events_df['Time Elapsed']['Data System Error']
	else:
		end_time = events_df['Time Elapsed']['Victim 2 Out']

	data_df = FED_dict[experiment]	
	for loc in data_df.columns:
		if 'Temp rate' in loc:
			continue
		elif 'rate' in loc:
			pass
		else:
			continue
		
		if 'Near Bedroom' in loc or 'Near Closed Bedroom' in loc:
			print(loc)
			if not np.isnan(victim_times[experiment]['Near BR Door Open']):
				door_time = victim_times[experiment]['Near BR Door Open']
				door_int = door_time + ff_int
				data= data_df[loc][0:end_time]
				data_at =data[int(door_int)]
				data_at =np.mean(data_at)
				data_after = data[int(door_int):int(door_int+90)]
				post_mean = np.mean(data_after)
				post_mean = max(data)
				# if experiment == 'Experiment_01':
				# 	data_after = data[int(door_int):int(door_int+60)]
				# 	post_mean = np.mean(data_after)
				# else:
				# 	post_mean = np.mean(data[int(door_int+60)])
			else:
				data_at =data[ff_int]
				post_mean = max(data)
			FED_int_df.loc[experiment,'Near Bedroom Rate at door open'] = data_at
			FED_int_df.loc[experiment,'Near Bedroom average rate+ 1 min'] = post_mean

		elif 'Far Bedroom' in loc or 'Far Closed Bedroom' in loc:
			print(loc)
			if not np.isnan(victim_times[experiment]['Far BR Door Open']):
				door_time = victim_times[experiment]['Far BR Door Open']
				door_int = door_time + ff_int
				data= data_df[loc][0:end_time]
				data_at =data[int(door_int-90):int(door_int)]
				data_at =np.mean(data_at)
				data_after = data[int(door_int):int(door_int+90)]
				post_mean = np.mean(data_after)
				post_mean = max(data)
			#for experiments 1 and 5, where door was not opened, use the maximum rate as teh comparison
			else:
				print(experiment)
				data_at =data[ff_int]
				post_mean = max(data)

				# post_mean = data[int(door_int+60)]
			FED_int_df.loc[experiment,'Far Bedroom Rate at door open'] = data_at
			FED_int_df.loc[experiment,'Far Bedroom average rate+ 1 min'] = post_mean				
		else:
			continue
		
near_BR_ls = []
far_open_BR_ls = []
far_shut_BR_ls =[]

af_near_BR_ls = []
af_far_open_BR_ls = []
af_far_shut_BR_ls =[]
for experiment in FED_int_df.index.values:
	if experiment in ['Experiment_10','Experiment_12']:
		near_BR_ls.append(FED_int_df.loc[experiment,'Near Bedroom Rate at door open'])
		af_near_BR_ls.append(FED_int_df.loc[experiment,'Near Bedroom average rate+ 1 min'])
	elif experiment in ['Experiment_11']:
		far_open_BR_ls.append(FED_int_df.loc[experiment,'Far Bedroom Rate at door open'])
		af_far_open_BR_ls.append(FED_int_df.loc[experiment,'Far Bedroom average rate+ 1 min'])
	elif experiment in ['Experiment_01','Experiment_05','Experiment_09']:
		if experiment in ['Experiment_05','Experiment_09']:
			near_BR_ls.append(FED_int_df.loc[experiment,'Near Bedroom Rate at door open'])
			af_near_BR_ls.append(FED_int_df.loc[experiment,'Near Bedroom average rate+ 1 min'])		
		far_shut_BR_ls.append(FED_int_df.loc[experiment,'Far Bedroom Rate at door open'])
		af_far_shut_BR_ls.append(FED_int_df.loc[experiment,'Far Bedroom average rate+ 1 min'])
	else:
		near_BR_ls.append(FED_int_df.loc[experiment,'Near Bedroom Rate at door open'])
		af_near_BR_ls.append(FED_int_df.loc[experiment,'Near Bedroom average rate+ 1 min'])
		far_open_BR_ls.append(FED_int_df.loc[experiment,'Far Bedroom Rate at door open'])
		af_far_open_BR_ls.append(FED_int_df.loc[experiment,'Far Bedroom average rate+ 1 min'])

print('compare closed to open for far BR')		
print(af_far_open_BR_ls)
print(af_far_shut_BR_ls)
print(stats.ttest_ind(np.array(af_far_open_BR_ls),np.array(af_far_shut_BR_ls),equal_var=False))
print()

print('compare average 1 min after to time at for far BR (for exps where door opened')		
print(stats.ttest_ind(np.array(far_open_BR_ls),np.array(af_far_shut_BR_ls),equal_var=False))
print()

print('compare average 1 min after to time at for near BR (for exps where door opened')		
print(stats.ttest_ind(np.array(near_BR_ls),np.array(af_near_BR_ls),equal_var=False))
print()

#check if 

int_ls=[1.0,.562,.765,.678,.433,.714]
trans_ls=[1.0,.869,.243,.291,.425,.862]
print('Far Hall')
print(str(np.mean(int_ls))+'+-'+str(np.std(int_ls)))
print(str(np.mean(trans_ls))+'+-'+str(np.std(trans_ls)))
print(stats.ttest_ind(np.array(int_ls),np.array(trans_ls),equal_var=False))
print()

print('Near Hall')
int_ls=[344,300,341,346,225,373]
trans_ls=[300,345,344,262,365,315]
print(str(np.mean(int_ls))+'+-'+str(np.std(int_ls)))
print(str(np.mean(trans_ls))+'+-'+str(np.std(trans_ls)))
print(stats.ttest_ind(np.array(int_ls),np.array(trans_ls),equal_var=False))
