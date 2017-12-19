import pandas as pd 
import os as os
import numpy as np 
from pylab import * 
from scipy import stats

info_dir = '../Info/'

#import test descriptions
test_des = pd.read_csv(info_dir+'Test_Description.csv',index_col = 'Test Name')

#import victim times
victim_times = pd.read_csv(info_dir+'Victim.csv', index_col = 'Event')

#import attack times
attack_times = pd.read_csv(info_dir+'Fire_attack.csv',index_col = 'Event')

#import water times
water_times = pd.read_csv(info_dir+'Suppression.csv',index_col = 'Experiment')

#Build dataframe to hold results

nrows = 12
ncols = 7

column_headers = ['Experiment','Dispatch to entry','Time to find V1','Time to remove V1','Time to find V2','Time to remove V2','Total time to find V2']
stats_df = pd.DataFrame(np.zeros((nrows,ncols)))
stats_df.columns = column_headers
Exp_Names=[]
for f in test_des.index.values:
	Exp_Names.append(f)
stats_df['Experiment']=Exp_Names
stats_df = stats_df.set_index('Experiment')
#loop through columns of victim times to fill in the dataframe
#the time at which the search crew entered the building will be considered the "start time"
V1_total_ls=[]
V2_total_ls=[]
for experiment in test_des.index.values:
	entry = victim_times[experiment]['Enter']
	rentry =victim_times[experiment]['Re-Enter']
	pre_entry = entry-victim_times[experiment]['Dispatch']
	V1_found = victim_times[experiment]['Victim 1 Found']-entry
	V1_out = victim_times[experiment]['Victim 1 Out'] - victim_times[experiment]['Victim 1 Found']
	V2_rentry = victim_times[experiment]['Victim 2 Found'] - rentry
	V2_abs = victim_times[experiment]['Victim 2 Found'] - entry
	V2_out = victim_times[experiment]['Victim 2 Out'] - victim_times[experiment]['Victim 2 Found']
	# print(pre_entry)
	stats_df.loc[experiment,'Dispatch to entry']= pre_entry
	stats_df.loc[experiment,'Time to find V1']= V1_found
	stats_df.loc[experiment,'Time to remove V1']= V1_out
	stats_df.loc[experiment,'Time to find V2']= V2_rentry
	stats_df.loc[experiment,'Time to remove V2']= V2_out
	stats_df.loc[experiment,'Total time to find V2']= V2_abs
	V1_total_ls.append(V1_found+V1_out)
	V2_total_ls.append(V2_abs+V2_out)
print(max(V1_total_ls),min(V1_total_ls))
print(max(V2_total_ls),min(V2_total_ls))
exit()
# print(stats_df)
print('V1 found')
print('mean: '+str(np.mean(stats_df['Time to find V1']))+'+-'+str(np.std(stats_df['Time to find V1'])))

print('V1 out')
print('mean: '+str(np.mean(stats_df['Time to remove V1']))+'+-'+str(np.std(stats_df['Time to remove V1'])))
print(max(stats_df['Time to remove V1']),min(stats_df['Time to remove V1']))
print('V2 found')
print('mean: '+str(np.mean(stats_df['Time to find V2']))+'+-'+str(np.std(stats_df['Time to find V2'])))

print('V2 out')
print('mean: '+str(np.mean(stats_df['Time to remove V2']))+'+-'+str(np.std(stats_df['Time to remove V2'])))


print(max(stats_df['Time to remove V2']),min(stats_df['Time to remove V2']))

#obtain mean, sd for two attack types and perform a t-test
print('----------------------------------------------------------------------------')
attack_groups = test_des.groupby('Attack Type')
for column in stats_df.columns:
	print()
	print(column)
	print('Transitional')
	Trans_ls = []
	for experiment in attack_groups.get_group('Transitional').index.values:
		Trans_ls.append(stats_df.loc[experiment,column])
	mean = np.mean(Trans_ls)
	stdev = np.std(Trans_ls)
	print('mean: '+str(mean)+'+-'+str(stdev))

	print('Interior')
	int_ls =[]
	for experiment in attack_groups.get_group('Interior').index.values:
		int_ls.append(stats_df.loc[experiment,column])
	mean = np.mean(int_ls)
	stdev = np.std(int_ls)
	print('mean: '+str(mean)+'+-'+str(stdev))

	print('t-test')
	print(stats.ttest_ind(np.array(Trans_ls),np.array(int_ls),equal_var=False))

	print()

print('----------------------------------------------------------------------------')
attack_groups = test_des.groupby('Side')
for column in stats_df.columns:
	print()
	print(column)
	print('Left')
	left_ls = []
	for experiment in attack_groups.get_group('Left').index.values:
		left_ls.append(stats_df.loc[experiment,column])
	mean = np.mean(left_ls)
	stdev = np.std(left_ls)
	print('mean: '+str(mean)+'+-'+str(stdev))

	print('Right')
	right_ls =[]
	for experiment in attack_groups.get_group('Right').index.values:
		right_ls.append(stats_df.loc[experiment,column])
	mean = np.mean(right_ls)
	stdev = np.std(right_ls)
	print('mean: '+str(mean)+'+-'+str(stdev))

	print('t-test')
	print(stats.ttest_ind(np.array(left_ls),np.array(right_ls),equal_var=False))

	print()
print('----------------------------------------------------------------------------')
attack_groups = test_des.groupby('Order')
for column in stats_df.columns:
	print()
	print(column)
	print('First')
	First_ls = []
	for experiment in attack_groups.get_group('First').index.values:
		First_ls.append(stats_df.loc[experiment,column])
	mean = np.mean(First_ls)
	stdev = np.std(First_ls)
	print('mean: '+str(mean)+'+-'+str(stdev))

	print('Second')
	Second_ls =[]
	for experiment in attack_groups.get_group('Second').index.values:
		Second_ls.append(stats_df.loc[experiment,column])
	mean = np.mean(Second_ls)
	stdev = np.std(Second_ls)
	print('mean: '+str(mean)+'+-'+str(stdev))

	print('t-test')
	print(stats.ttest_ind(np.array(First_ls),np.array(Second_ls),equal_var=False))

	print()
print('----------------------------------------------------------------------------')
attack_groups = test_des.groupby('Group')
for column in stats_df.columns:
	print()
	print(column)
	print('A1')
	A1_ls = []
	for experiment in attack_groups.get_group('A1').index.values:
		A1_ls.append(stats_df.loc[experiment,column])
	mean = np.mean(A1_ls)
	stdev = np.std(A1_ls)
	print('mean: '+str(mean)+'+-'+str(stdev))

	print('A2')
	A2_ls =[]
	for experiment in attack_groups.get_group('A2').index.values:
		A2_ls.append(stats_df.loc[experiment,column])
	mean = np.mean(A2_ls)
	stdev = np.std(A2_ls)
	print('mean: '+str(mean)+'+-'+str(stdev))

	print('B1')
	B1_ls = []
	for experiment in attack_groups.get_group('B1').index.values:
		B1_ls.append(stats_df.loc[experiment,column])
	mean = np.mean(B1_ls)
	stdev = np.std(B1_ls)
	print('mean: '+str(mean)+'+-'+str(stdev))

	print('B2')
	B2_ls =[]
	for experiment in attack_groups.get_group('B1').index.values:
		B2_ls.append(stats_df.loc[experiment,column])
	mean = np.mean(B2_ls)
	stdev = np.std(B2_ls)
	print('mean: '+str(mean)+'+-'+str(stdev))

	print('C1')
	C1_ls = []
	for experiment in attack_groups.get_group('C1').index.values:
		C1_ls.append(stats_df.loc[experiment,column])
	mean = np.mean(C1_ls)
	stdev = np.std(C1_ls)
	print('mean: '+str(mean)+'+-'+str(stdev))

	print('C2')
	C2_ls =[]
	for experiment in attack_groups.get_group('C2').index.values:
		C2_ls.append(stats_df.loc[experiment,column])
	mean = np.mean(C2_ls)
	stdev = np.std(C2_ls)
	print('mean: '+str(mean)+'+-'+str(stdev))

	print('t-test')	
	print(stats.ttest_ind(np.array(A1_ls),np.array(A2_ls),equal_var=False))
	print(stats.ttest_ind(np.array(A1_ls),np.array(B1_ls),equal_var=False))
	print(stats.ttest_ind(np.array(A1_ls),np.array(B2_ls),equal_var=False))
	print(stats.ttest_ind(np.array(A1_ls),np.array(C1_ls),equal_var=False))
	print(stats.ttest_ind(np.array(A1_ls),np.array(C2_ls),equal_var=False))
	print(stats.ttest_ind(np.array(A2_ls),np.array(B1_ls),equal_var=False))
	print(stats.ttest_ind(np.array(A2_ls),np.array(B2_ls),equal_var=False))
	print(stats.ttest_ind(np.array(A2_ls),np.array(C1_ls),equal_var=False))
	print(stats.ttest_ind(np.array(A2_ls),np.array(C2_ls),equal_var=False))
	
	print()
print('----------------------------------------------------------------------------')
V1_mean = np.mean(stats_df['Time to remove V1'])
V1_stdev = np.std(stats_df['Time to remove V1'])
print('mean: '+str(V1_mean)+'+-'+str(V1_stdev))
V2_mean = np.mean(stats_df['Time to remove V2'])
V2_stdev = np.std(stats_df['Time to remove V2'])
print('mean: '+str(V2_mean)+'+-'+str(V2_stdev))
print(stats.ttest_ind(np.array(stats_df['Time to remove V1']),np.array(stats_df['Time to remove V2']),equal_var=False))
print('----------------------------------------------------------------------------')
print('Fire attack')
attack_groups = test_des.groupby('Side')

print()
print('Left')
ls=[]
left_ls = []
for experiment in attack_groups.get_group('Left').index.values:
	left_ls.append(attack_times.loc['Delta',experiment])
	ls.append(attack_times.loc['Delta',experiment])
mean = np.mean(left_ls)
stdev = np.std(left_ls)
print('mean: '+str(mean)+'+-'+str(stdev))

print('Right')
right_ls =[]
for experiment in attack_groups.get_group('Right').index.values:
	right_ls.append(attack_times.loc['Delta',experiment])
	ls.append(attack_times.loc['Delta',experiment])
mean = np.mean(right_ls)
stdev = np.std(right_ls)
print('mean: '+str(mean)+'+-'+str(stdev))

print('t-test')
print(stats.ttest_ind(np.array(left_ls),np.array(right_ls),equal_var=False))
print(stats.shapiro(ls))

print()
ls=[]
attack_groups = test_des.groupby('Attack Type')
print()
print('Transitional')
trans_ls = []
for experiment in attack_groups.get_group('Transitional').index.values:
	trans_ls.append(attack_times.loc['Delta',experiment])
	ls.append(attack_times.loc['Delta',experiment])
mean = np.mean(trans_ls)
stdev = np.std(trans_ls)
print('mean: '+str(mean)+'+-'+str(stdev))

print('Interior')
int_ls =[]
for experiment in attack_groups.get_group('Interior').index.values:
	int_ls.append(attack_times.loc['Delta',experiment])
	ls.append(attack_times.loc['Delta',experiment])
mean = np.mean(int_ls)
stdev = np.std(int_ls)
print('mean: '+str(mean)+'+-'+str(stdev))

print('t-test')
print(stats.ttest_ind(np.array(trans_ls),np.array(int_ls),equal_var=False))
print(stats.shapiro(trans_ls))
print(stats.shapiro(int_ls))
print()
('Entry')
print()
ls=[]
attack_groups = test_des.groupby('Attack Type')
print()
print('Transitional')
trans_ls = []
for experiment in attack_groups.get_group('Transitional').index.values:
	trans_ls.append(attack_times.loc['Entry',experiment])
	ls.append(attack_times.loc['Entry',experiment])
mean = np.mean(trans_ls)
stdev = np.std(trans_ls)
print('mean: '+str(mean)+'+-'+str(stdev))

print('Interior')
int_ls =[]
for experiment in attack_groups.get_group('Interior').index.values:
	int_ls.append(attack_times.loc['Entry',experiment])
	ls.append(attack_times.loc['Entry',experiment])
mean = np.mean(int_ls)
stdev = np.std(int_ls)
print('mean: '+str(mean)+'+-'+str(stdev))

print('t-test')
print(stats.ttest_ind(np.array(trans_ls),np.array(int_ls),equal_var=False))
print(stats.shapiro(trans_ls))
print(stats.shapiro(int_ls))
print()
print('---------------------------------------------------------------------------------------')
attack_groups = test_des.groupby('Attack Type')
print('Trans')
water_1=[]
water_2=[]
trans_times=[]

for experiment in attack_groups.get_group('Transitional').index.values:
	water_1.append(water_times['Water 1 (BR A)'][experiment])
	water_2.append(water_times['Water 2 (BR B)'][experiment])
	trans_times.append(water_times['Time after door open'][experiment])
print(str(np.mean(water_1))+'+-'+str(np.std(water_1)))
print(str(np.mean(water_2))+'+-'+str(np.std(water_2)))
print(str(np.mean(trans_times))+'+-'+str(np.std(trans_times)))
print()
print('Int')
int_times=[]
water_1 =[]
for experiment in attack_groups.get_group('Interior').index.values:
	water_1.append(water_times['Water 1 (BR A)'][experiment])
	int_times.append(water_times['Time after door open'][experiment])
print(str(np.mean(int_times))+'+-'+str(np.std(int_times)))
print(str(np.mean(water_1))+'+-'+str(np.std(water_1)))
print(stats.ttest_ind(np.array(trans_times),np.array(int_times),equal_var=False))

