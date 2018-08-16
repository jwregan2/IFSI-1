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
FED_max_df =  pd.DataFrame(np.zeros((nrows,ncols)))
FED_max_df.columns = column_headers
FED_max_df['Experiment']=Exp_Names
FED_max_df = FED_max_df.set_index('Experiment')

#Find maximum FEDS for each static victim lcoation or FED at time of FF intervention
int_i=[]
int_t=[]
interior_ls=[]
trans_ls=[]
for experiment in test_des.index.values:
	events_df = test_events_dict[experiment].reset_index()
	events_df = events_df.set_index('Event')
	if test_des['Attack Type'][experiment] == 'Transitional':
		ff_int = events_df['Time Elapsed']['Water in Window']
		int_start =events_df['Time Elapsed']['Front Door Open']
		int_t.append(int_start)
		trans_ls.append(int_start-ff_int)

	elif test_des['Attack Type'][experiment] == 'Interior':
		ff_int = events_df['Time Elapsed']['Nozzle FF Reaches Hallway']
		int_start =events_df['Time Elapsed']['Front Door Open']
		int_i.append(int_start)
		interior_ls.append(ff_int-int_start)
	# ff_int = events_df['Time Elapsed']['FD Dispatch']
	data_df = FED_dict[experiment]	
	for loc in data_df.columns:
		if 'rate' in loc:
			continue
		else:
			if error_exps['Skip'][experiment] == loc:
				FED_int_df.loc[experiment,loc]='n.a'
				FED_max_df.loc[experiment,loc]='n.a'
				continue
			int_data = data_df[loc][ff_int]
			FED_int_df.loc[experiment,loc]=np.round(int_data,2)
			FED_max_df.loc[experiment,loc]=np.round(max(data_df[loc]),2)
			
print('max FEDs for each location')
for loc in FED_max_df.columns:
	FED_ls = []
	for experiment in FED_max_df[loc].index.values:
		if error_exps['Skip'][experiment] == loc:
			# print(experiment,loc)
			continue
		FED_ls.append(FED_max_df[loc][experiment])
	print(loc)
	print(str(np.mean(FED_ls))+' +- ' + str(np.std(FED_ls)))
	print(np.std(FED_ls)/np.mean(FED_ls))
	print('max: '+str(max(FED_ls)))
	print('min: '+str(min(FED_ls)))
	print()


print('max values')
print(FED_max_df)
print()
print('intervention values')
print(FED_int_df)
# exit()
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
	print('u-test')
	print(stats.ranksums(np.array(trans_ls),np.array(int_ls)))
	

	print()
# print(inflection_df)

output_table_loc='../Tables/'
if not os.path.exists(output_table_loc):
	os.makedirs(output_table_loc)
inflection_df.to_csv(output_table_loc+'time_to_inflection.csv')
print('-------------------------------------------------------------')
print('find time to inflection point in FED from Dispatch')

inflect_from_disp_df = pd.DataFrame(np.zeros((nrows,1)))

inflect_from_disp_df['Experiment']=Exp_Names
inflect_from_disp_df = inflect_from_disp_df.set_index('Experiment')

for experiment in test_des.index.values:
	events_df = test_events_dict[experiment].reset_index()
	events_df = events_df.set_index('Event')
	if test_des['Attack Type'][experiment] == 'Transitional':
		ff_int = events_df['Time Elapsed']['FD Dispatch']
	elif test_des['Attack Type'][experiment] == 'Interior':
		ff_int = events_df['Time Elapsed']['FD Dispatch']

	data_df = FED_dict[experiment]

	
	for loc in data_df.columns:
		if 'rate' in loc:
			pass
		else:
			continue
		index = data_df[loc].idxmax(axis=0)
		inflect_from_disp_df.loc[experiment,loc]=np.round(index-ff_int)

print()
attack_groups = test_des.groupby('Attack Type')
for column in inflect_from_disp_df.columns:
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
		trans_ls.append(inflect_from_disp_df.loc[experiment,column])
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
		int_ls.append(inflect_from_disp_df.loc[experiment,column])
	mean = np.mean(int_ls)
	stdev = np.std(int_ls)
	print('mean: '+str(mean)+'+-'+str(stdev))

	print('t-test')
	print(stats.ttest_ind(np.array(trans_ls),np.array(int_ls),equal_var=False))
	print('u-test')
	print(stats.ranksums(np.array(trans_ls),np.array(int_ls)))
	

	print()
# print(inflect_from_disp_df)

output_table_loc='../Tables/'
if not os.path.exists(output_table_loc):
	os.makedirs(output_table_loc)
inflect_from_disp_df.to_csv(output_table_loc+'time_to_inflection.csv')
print('-------------------------------------------------------------')
print('rate at time of door open and max time')

door_df = pd.DataFrame(np.zeros((nrows,7)))
door_df.columns = ['Experiment','Far Bedroom Rate at door open','Far Bedroom max rate','Delta','Rate at intervention','Near BR pre peak','Near BR post peak']
door_df['Experiment']=Exp_Names
door_df = door_df.set_index('Experiment')

for experiment in test_des.index.values:
	events_df = test_events_dict[experiment].reset_index()
	events_df = events_df.set_index('Event')
	ff_int = events_df['Time Elapsed']['FD Dispatch']
	if experiment == 'Experiment_01':
		end_time =  events_df['Time Elapsed']['Data System Error']
	else:
		end_time = events_df['Time Elapsed']['End of Experiment']

	data_df = FED_dict[experiment]	
	for loc in data_df.columns:

		if 'Temp rate' in loc:
			continue
		elif 'rate' in loc:
			pass
		else:
			continue
		if 'Far Bedroom' in loc or 'Far Closed Bedroom' in loc:
			if not np.isnan(victim_times[experiment]['Far BR Door Open']):
				door_time = victim_times[experiment]['Far BR Door Open']
				door_int = door_time + ff_int
				data= data_df[loc][0:end_time]
				data_at =data[int(door_int-90):int(door_int)]
				ff_int_rate = data[ff_int]
				data_at =np.mean(data_at)
				data_after = data[int(door_int):int(end_time)]
				post_mean = max(data_after)
				delta = (post_mean-data_at)/data_at*100

			#for experiments 1 and 5, where door was not opened, use the maximum rate as teh comparison
			else:
				# print(experiment)
				data=data_df[loc][0:end_time]
				data_at =data[ff_int]
				ff_int_rate = data[ff_int]
				post_mean = max(data)
				delta = (post_mean -data_at)/data_at*100

				# post_mean = data[int(door_int+60)]
			door_df.loc[experiment,'Far Bedroom Rate at door open'] = data_at
			door_df.loc[experiment,'Far Bedroom max rate'] = post_mean
			door_df.loc[experiment,'Delta'] = delta
			door_df.loc[experiment,'Rate at intervention'] = ff_int_rate


		elif 'Near Bedroom' in loc or 'Near Closed Bedroom' in loc:
			# print(loc, experiment)
			if not np.isnan(victim_times[experiment]['Near BR Door Open']):
				door_time = victim_times[experiment]['Near BR Door Open']
				door_int = door_time + ff_int
				data= data_df[loc][0:end_time]
				# data_at =data[int(door_int)]
				# data_at =np.mean(data_at)
				data_after = data.loc[int(door_int):int(end_time)]
				pre_peak = max(data[0:int(door_int)])
				post_mean = max(data_after)
				
			else:
				print('ERROR')
			door_df.loc[experiment,'Near BR pre peak'] = pre_peak
			door_df.loc[experiment,'Near BR post peak'] = post_mean
yes_close=[]
no_close=[]
ff_int_yes=[]
ff_int_no=[]
ave_increase=[]
near_pre=[]
near_post=[]
for experiment in test_des.index.values:
	if experiment in ['Experiment_10','Experiment_12']:
		continue
	elif experiment in ['Experiment_01','Experiment_05','Experiment_09']:
		yes_close.append(door_df.loc[experiment,'Far Bedroom max rate'])
		ff_int_yes.append(door_df.loc[experiment,'Rate at intervention'])
	else:
		no_close.append(door_df.loc[experiment,'Far Bedroom max rate'])
		ff_int_no.append(door_df.loc[experiment,'Rate at intervention'])
		ave_increase.append(door_df.loc[experiment,'Delta'])
print('Max rate average where door was not opened: '+str(np.mean(yes_close))+'+-'+str(np.std(yes_close)))
print('Max rate average where door was  opened: '+str(np.mean(no_close))+'+-'+str(np.std(no_close)))
print(stats.ttest_ind(np.array(yes_close),np.array(no_close),equal_var=False))
print(stats.ttest_ind(np.array(ff_int_yes),np.array(ff_int_no),equal_var=False))
print(stats.ranksums(np.array(ff_int_yes),np.array(ff_int_no)))
print('Average Rate % Increase following open: '+str(np.mean(ave_increase))+'+-'+str(np.std(ave_increase)))
# print(door_df)
for experiment in test_des.index.values:
	if experiment =='Experiment_11':
		continue
	else:
		near_pre.append((door_df.loc[experiment,'Near BR pre peak']))
		near_post.append((door_df.loc[experiment,'Near BR post peak']))
print('pre average: '+str(np.mean(near_pre))+'+-'+str(np.std(near_pre)))
print('post average: '+str(np.mean(near_post))+'+-'+str(np.std(near_post)))
print(stats.ranksums(np.array(near_pre),np.array(near_post)))
print(stats.ttest_ind(np.array(near_pre),np.array(near_post),equal_var=False))




#check if 
print('--------------------------------------------------------------------------------------------------')
print('Compare Finals FEDs')
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

print('Time to advance line')

hose_advance_df = pd.DataFrame(np.zeros((nrows,2)))
hose_advance_df.columns = ['Experiment','Advance Time']

hose_advance_df['Experiment']=Exp_Names
hose_advance_df = hose_advance_df.set_index('Experiment')

int_adv_ls=[]
trans_adv_ls=[]
all_ls = []
for experiment in test_des.index.values:
	events_df = test_events_dict[experiment].reset_index()
	events_df = events_df.set_index('Event')
	line_advance = events_df['Time Elapsed']['Nozzle FF Reaches Hallway']-events_df['Time Elapsed']['Front Door Open']
	hose_advance_df.loc[experiment,'Advance Time']=line_advance
	if experiment == 'Experiment_06':
		continue
	all_ls.append(line_advance)
	if test_des['Attack Type'][experiment] =='Transitional':
		trans_adv_ls.append(line_advance)

	elif test_des['Attack Type'][experiment] =='Interior':
		int_adv_ls.append(line_advance)
print(max(all_ls)/min(all_ls))
print('mean: '+str(np.mean(all_ls))+'+-'+str(np.std(all_ls)))
print('Int mean: '+str(np.mean(int_adv_ls))+'+-'+str(np.std(int_adv_ls)))
print('Trans mean: '+str(np.mean(trans_adv_ls))+'+-'+str(np.std(trans_adv_ls)))
print('t-test')
print(stats.ttest_ind(np.array(trans_adv_ls),np.array(int_adv_ls),equal_var=False))
	

print('---------------------------------------------------------------------------------')
#Build dataframe to hold results

nrows = 12
ncols = 5

column_headers = ['Experiment','Far Hall','Far Hall Time','Near Bedroom','Near Bedroom Time']
vic_removal_df = pd.DataFrame(np.zeros((nrows,ncols)))
vic_removal_df.columns = column_headers
Exp_Names=[]
for f in test_des.index.values:
	Exp_Names.append(f)
vic_removal_df['Experiment']=Exp_Names
vic_removal_df = vic_removal_df.set_index('Experiment')

# v1_max = max(V1_total_ls)
# v1_min = min(V1_total_ls)
# v1_increase_ls=[]
# v2_max = max(V2_total_ls)
# v2_min = min(V2_total_ls)
# v2_increase_ls=[]
# for experiment in test_des.index.values:
# 	if experiment in ['Experiment_01','Experiment_02']:
# 		continue
# 	print(experiment)
# 	events_df = test_events_dict[experiment].reset_index()
# 	events_df = events_df.set_index('Event')
# 	data_df = FED_dict[experiment]
# 	disp_time = events_df['Time Elapsed']['FD Dispatch']
# 	entry_time = victim_times.loc['Enter',experiment]
# 	v1_min_time = disp_time+entry_time+	v1_min	
# 	v1_max_time = disp_time+entry_time+	v1_max	
# 	v1_increase_ls.append(np.round((data_df.loc[v1_max_time,'Far Hall']-data_df.loc[v1_min_time,'Far Hall'])/data_df.loc[v1_min_time,'Far Hall'],2))
# 	v2_min_time = disp_time+entry_time+	v2_min	
# 	v2_max_time = disp_time+entry_time+	v2_max	
# 	v2_increase_ls.append(np.round((data_df.loc[v2_max_time,'Far Hall']-data_df.loc[v2_min_time,'Far Hall'])/data_df.loc[v2_min_time,'Far Hall'],2))	
# print(v1_increase_ls)
# print(v2_increase_ls)
# print(str(np.mean(v1_increase_ls))+'+-'+str(np.std((v1_increase_ls))))
# print(str(np.mean(v2_increase_ls))+'+-'+str(np.std((v2_increase_ls))))
v1_increase_ls=[]
v2_increase_ls=[]
rescue_times =[]
for experiment in vic_removal_df.index.values:
	events_df = test_events_dict[experiment].reset_index()
	events_df = events_df.set_index('Event')
	data_df = FED_dict[experiment]
	disp_time = events_df['Time Elapsed']['FD Dispatch']
	vic_2_out = victim_times.loc['Victim 2 Out',experiment]+disp_time
	vic_1_out = victim_times.loc['Victim 1 Found',experiment]+disp_time
	entry_time = victim_times.loc['Enter',experiment]+disp_time	

	rescue_times.append(vic_1_out-entry_time)
	for col in vic_removal_df.columns:
		if col == error_exps['Skip'][experiment]:
			continue
		if 'Time' in col:
			continue

		if col == 'Near Bedroom':
			vic_time = vic_2_out
			if experiment == 'Experiment_01':
				continue
		elif col == 'Far Hall':
			vic_time = vic_1_out

		entry_time=(vic_time-entry_time)
		if entry_time not in data_df.index.values:
			entry_time = entry_time+1
		vic_removal_df.loc[experiment,col+' Time']=entry_time
		vic_removal_df.loc[experiment, col]=(np.round((data_df.loc[vic_time,col]-data_df.loc[entry_time,col])/data_df.loc[entry_time,col],2))


output_dir = '../Figures/victim_removal/'
if not os.path.exists(output_dir):
		os.makedirs(output_dir)

# print(vic_removal_df)
for col in vic_removal_df.columns:
	if 'Time' in col:
		continue
	fig=plt.figure()
	ax = plt.gca()	
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
	plt.grid(True)
	plt.xlabel('Removal Time (s)', fontsize=16)
	plt.ylabel('FED increase (-/-)')

	plt.xlim([.9*min(vic_removal_df[col+' Time']),1.1*max(vic_removal_df[col+' Time'])])
	plt.ylim([0,1.1*max(vic_removal_df[col])])
	plt.xticks(fontsize=16)
	plt.yticks(fontsize=16)
	ax.scatter(vic_removal_df[col+' Time'],vic_removal_df[col])
	# handles1, labels1 = ax1.get_legend_handles_labels()		
	fig.set_size_inches(10, 7)				
	# plt.title('Experiment '+str(experiment)+' '+chart, y=1.08)
	plt.tight_layout()	
	# plt.legend(handles1, labels1, fontsize=12,loc='upper left')	
	plt.savefig(output_dir +col.replace(' ','_')+'.png')
	plt.close('all')

ncols = 12
nrows = len(rescue_times)

column_headers = rescue_times
removal_times_df = pd.DataFrame(np.zeros((nrows,ncols)))
removal_times_df.columns = test_des.index.values
removal_times_df['Times']=rescue_times
removal_times_df = removal_times_df.set_index('Times')	

# ncols = 51
# nrows = 12
# removal_times_df = pd.DataFrame(np.zeros((nrows,ncols)))
# column_headers = np.linspace(20,70,51)
# print(column_headers)
# removal_times_df.columns = column_headers
# Exp_Names=[]
# for f in test_des.index.values:
# 	Exp_Names.append(f)
# removal_times_df['Experiment']=Exp_Names
# removal_times_df = removal_times_df.set_index('Experiment')	
	

fig=plt.figure()
ax = plt.gca()	
tableau20 = ([(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
				(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
				(148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
				(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
				(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)])
for i in range(len(tableau20)):
	r, g, b = tableau20[i]
	tableau20[i] = (r / 255., g / 255., b / 255.)
tableau20=cycle(tableau20)
colors=cycle(['b','r','k','y','c','m','g'])
plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])
max_vals=[]
min_vals=[]
for i in rescue_times:
	for experiment in test_des.index.values:
		if experiment == 'Experiment_02':
			continue
		events_df = test_events_dict[experiment].reset_index()
		events_df = events_df.set_index('Event')
		data_df = FED_dict[experiment]
		data_df = data_df.reset_index().drop_duplicates(subset='Elapsed Time', keep='last').set_index('Elapsed Time')
		disp_time = events_df['Time Elapsed']['FD Dispatch']
		entry_time = victim_times.loc['Enter',experiment]+disp_time
		if entry_time not in data_df.index.values:
			entry_time = entry_time+1	
		vic_fed = []
		j=0
		if entry_time +i not in data_df.index.values:
			j=1	
		removal_times_df.loc[i,experiment]=(100*(data_df.loc[entry_time+i+j,'Far Hall']-data_df.loc[entry_time,'Far Hall'])/data_df.loc[entry_time,'Far Hall'])
		j=0
	
	# max_vals.append(max(vic_fed))
	# min_vals.append(min(vic_fed))
	# ax.scatter(rescue_times,vic_fed,c=next(colors),marker=next(plot_markers),label = 'Exp '+ experiment[-2:])
# print(removal_times_df)	
removal_times_df=removal_times_df.drop('Experiment_02',axis = 1)
# plt.boxplot(removal_times_df)
# print(removal_times_df.columns)
# removal_times_df.boxplot(column=list(removal_times_df.columns.values),positions=np.linspace(20,70,51))
removal_times_df.boxplot(fontsize=16,markersize=4)#column=list(removal_times_df.columns.values),positions = np.linspace(0,10,11))
# plt.boxplot(removal_times_df,np.linspace(20,70,51))

plt.grid(True)
plt.xlabel('Experiment', fontsize=16)
plt.ylabel('Percent Increase in FED from Entry to Victim Removal (%)')
# plt.xlim([.9*min(vic_removal_df[col+' Time']),1.1*max(vic_removal_df[col+' Time'])])
# plt.ylim([0,1.1*max(max_vals)])
# plt.xticks(np.linspace(0,10,11),list(removal_times_df.columns.values), fontsize=16)
# print(list(removal_times_df.columns.values))
labels = [' ']

for i in [1,3,4,5,6,7,8,9,10,11,12]:
	labels.append('E'+str(i) )
labels.append(' ')
print(labels) 
plt.xticks(np.arange(len(labels)),labels, fontsize=16)
plt.yticks(fontsize=16)
# ax.set_yscale('log')
# for axis in [ax.xaxis, ax.yaxis]:
# 	 axis.set_major_formatter(ScalarFormatter())

handles1, labels1 = ax.get_legend_handles_labels()		
fig.set_size_inches(10, 7)				
# plt.title('Experiment '+str(experiment)+' '+chart, y=1.08)
plt.tight_layout()	
plt.legend(handles1, labels1, fontsize=12,loc='upper left')	
plt.savefig(output_dir +'v1.png')
plt.close('all')


print(stats.ttest_ind(np.array(max_vals),np.array(min_vals),equal_var=False))
print('------------------------------------------------------------------------------')
print('ff_int times')
ff_int_int = []
ff_int_trans = []

for experiment in test_des.index.values:
	events_df = test_events_dict[experiment].reset_index()
	events_df = events_df.set_index('Event')
	if test_des['Attack Type'][experiment] == 'Transitional':
		ff_int = events_df['Time Elapsed']['Water in Window']
		ff_int_trans.append(ff_int)

	elif test_des['Attack Type'][experiment] == 'Interior':
		ff_int = events_df['Time Elapsed']['Front Door Open']
		interior_ls.append(ff_int-int_start)
		ff_int_int.append(ff_int)
print('trans int time')
print(str(np.mean(ff_int_trans))+'+-'+str(np.std(ff_int_trans)))
print()
print('int int time')
print(str(np.mean(ff_int_int))+'+-'+str(np.std(ff_int_int)))
print()

print('------------------------------------------------------------------------------')
print('door times')
ff_int_int = []
ff_int_trans = []

for experiment in test_des.index.values:
	events_df = test_events_dict[experiment].reset_index()
	events_df = events_df.set_index('Event')
	if test_des['Attack Type'][experiment] == 'Transitional':
		ff_int = events_df['Time Elapsed']['Front Door Open']
		ff_int_trans.append(ff_int)

	elif test_des['Attack Type'][experiment] == 'Interior':
		ff_int = events_df['Time Elapsed']['Front Door Open']
		interior_ls.append(ff_int-int_start)
		ff_int_int.append(ff_int)
print('trans door time')
print(str(np.mean(ff_int_trans))+'+-'+str(np.std(ff_int_trans)))
print()
print('int door time')
print(str(np.mean(ff_int_int))+'+-'+str(np.std(ff_int_int)))
print()
print('-------------------------------------------------------------------------------')
print('FED max comparison b/n attacks')
# print(FED_max_df)
# exit()
for col in FED_max_df.columns:
	print(col)
	FED_max_t_ls=[]
	FED_max_i_ls=[]
	for experiment in test_des.index.values:
		events_df = test_events_dict[experiment].reset_index()
		events_df = events_df.set_index('Event')
		if FED_max_df[col][experiment] == 'n.a':
			continue
		if test_des['Attack Type'][experiment] == 'Transitional':
			FED_max_t_ls.append(FED_max_df[col][experiment])

		elif test_des['Attack Type'][experiment] == 'Interior':
			FED_max_i_ls.append(FED_max_df[col][experiment])
	print('trans')
	print(str(np.mean(FED_max_t_ls))+'+-'+str(np.std(FED_max_t_ls)))
	print('int')
	print(str(np.mean(FED_max_i_ls))+'+-'+str(np.std(FED_max_i_ls)))
	print()
	print(stats.ttest_ind(np.array(FED_max_i_ls),np.array(FED_max_t_ls),equal_var=False))
	print(stats.ranksums(np.array(FED_max_i_ls),np.array(FED_max_t_ls)))
	print()

print('------------------------------------------------------------------------------')
print('compare near and far bedroom FED mags')
print(FED_max_df)

print('gas')
print(stats.ttest_ind(np.array(FED_max_df['Near Bedroom'].replace('n.a',0)),np.array(FED_max_df['Far Bedroom'].replace('n.a',0)),equal_var=False))
print(stats.ranksums(np.array(FED_max_df['Near Bedroom'].replace('n.a',0)),np.array(FED_max_df['Far Bedroom'].replace('n.a',0))))

print()
print('temp')
print(stats.ttest_ind(np.array(FED_max_df['Near Bedroom Temp']),np.array(FED_max_df['Far Bedroom Temp']),equal_var=False))
print(stats.ranksums(np.array(FED_max_df['Near Bedroom Temp']),np.array(FED_max_df['Far Bedroom Temp'])))