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


# Load data & event pickle dicts
test_data_dict = pickle.load(open(data_dir + 'metric_test_data.dict', 'rb'))
test_events_dict = pickle.load(open(events_dir + 'events.dict', 'rb'))

output_table_loc='../Tables/'

N_rows=12
N_columns=15
FEDs_table=pd.DataFrame(np.zeros((N_rows,N_columns)))
FEDs_table.columns=['Experiment','Attack Type','Test Length','Near Hall','Near Bedroom','Far Bedroom','Far Hall','Victim 1','Victim 2','Near Hall Temp','Near Bedroom Temp','Far Bedroom Temp','Far Hall Temp','Victim 1 Temp','Victim 2 Temp']
Exp_Names=[]
for f in test_des.index.values:
		Exp_Names.append(f)
Attack_Type=['Transitional','Interior','Transitional','Interior','Interior','Transitional','Interior','Transitional','Interior','Transitional','Transitional','Interior']
for i in range(len(FEDs_table)):
	FEDs_table.loc[i,'Experiment']=Exp_Names[i]
	FEDs_table.loc[i,'Attack Type']=Attack_Type[i]
FEDs_table=FEDs_table.set_index('Experiment')

#Define output directory
output_dir = '../Tables/'
FED_dict = {}
for experiment in test_des.index.values:
	print(experiment)
	side = test_des['Side'][experiment]

	#load slice of dictionary corresponding to expeiment
	data_df = test_data_dict[experiment]
	events = test_events_dict[experiment]
	#find end of experiment or end of data recording in exp where data system failed
	for event in events.index.values:
			if events['Event'][event] == 'End of Experiment' or events['Event'][event] == 'Data System Error':
				end_time = event

	# loop through locations for each
	for chart in channels.index.values:
		if not channels[side+' Gas Name'][chart] + 'COV' in data_df.columns:
			continue
		if not channels[side+' Temp Name'][chart] in data_df.columns:
			continue
		#for Victim gas and temps, consider using if statment
		CO_data = pd.Series(data_df[channels[side+' Gas Name'][chart]+ 'COV'].loc[0:])
		CO2_data = pd.Series(data_df[channels[side+' Gas Name'][chart]+ 'CO2V'].loc[0:])
		O2_data = pd.Series(data_df[channels[side+' Gas Name'][chart]+ 'O2V'].loc[0:])
		temp_data = pd.Series(data_df[channels[side+' Temp Name'][chart]].loc[0:])
		FED_df = pd.DataFrame(data={'Elapsed Time':CO_data.index.values})

		CO_FED=[]
		CO2_FED=[]
		O2_FED=[]
		FED_cum=[]
		Temps_conv=[]
		Temps_rad=[]
		Temps_cum=[]
		#compute data for gas since delta t is =1, no need to compute
		for t in CO_data.index.values:

			O2_FED.append((1.0/60.0)*1/(exp(8.13-0.54*(20.9-O2_data[t]))))
			CO2_FED.append(exp(CO2_data[t]/5))
			CO_FED.append((1.0/60.0)*(CO_data[t]/35000.0))
		#compute data for temp
		for t in temp_data.index.values:
			if np.isnan(t):
				##If any of the temperatures are nans, act as if they are room temperature
				Temps_rad.append((2.72*10**14)/((25+273.0)**(1.35)))
				Temps_conv.append((5.0*10**7)*25)**(-3.4)
			else:
			# 	print(temp_data[1377:1380])		
				print(temp_data[t])	
				Temps_rad.append((2.72*10**14)/((max([temp_data[t],0])+273.0)**(1.35)))
				Temps_conv.append((5.0*10**7)*max([temp_data[t],0])**(-3.4))

		#compute cumulative gas FEDs
		for t in range(len(CO_FED)):
			
			if t==0:	
				FED_cum.append(CO2_FED[t]*CO_FED[t]+O2_FED[t])
			elif t == len(CO_FED):
				break
			elif np.isnan(FED_cum[j]):
				FEDs_table.loc[experiment,chart]=('Sensor Malfunction at '+str(t))
				break
			elif FED_cum[j]>1.0:
				FEDs_table.loc[experiment,chart]=t
				FED_cum.append((CO2_FED[t]*CO_FED[t]+O2_FED[t])+FED_cum[j])
			elif t==end_time:
			# 	continue
				print('end')
				FEDs_table.loc[experiment,chart]=('N/A ('+str(round((CO2_FED[t]*CO_FED[t]+O2_FED[t])+FED_cum[j],3))+')')
				FED_cum.append((CO2_FED[t]*CO_FED[t]+O2_FED[t])+FED_cum[j])
			else:
				FED_cum.append((CO2_FED[t]*CO_FED[t]+O2_FED[t])+FED_cum[j])
			j=t
			# print(j,t,len(CO_FED))


		for t in range(len(Temps_rad)):
			if t==0:	
				Temps_cum.append((1/60)*((1/Temps_conv[t])+(1/Temps_rad[t])))
				# Temps_cum.append((1/60)*((1/Temps_conv[i])))
			elif t==len(Temps_rad):
				break
			elif Temps_cum[j]>1.0:
				FEDs_table.loc[experiment,chart+' Temp']=t
				Temps_cum.append((1/60)*((1/Temps_conv[t])+(1/Temps_rad[t]))+Temps_cum[j])
			
			elif t==end_time:
				FEDs_table.loc[experiment,chart+' Temp']=('N/A '+str(round((1/60)*((1/Temps_conv[t])+(1/Temps_rad[t]))+Temps_cum[j],3)))
				print('NO INCAP')
				Temps_cum.append((1/60)*((1/Temps_conv[t])+(1/Temps_rad[t]))+Temps_cum[j])
			else:
				Temps_cum.append((1/60)*((1/Temps_conv[t])+(1/Temps_rad[t]))+Temps_cum[j])
			j=t

		FED_df['CO FED'] = pd.Series(CO_FED)
		FED_df['CO2 FED'] = pd.Series(CO2_FED)
		FED_df['O2 FED'] = pd.Series(O2_FED)
		FED_df['Gas Cumulative'] = pd.Series(FED_cum)
		FED_df['Radiative FED'] = pd.Series(Temps_rad)
		FED_df['Convective FED'] = pd.Series(Temps_conv)
		FED_df['Temp Cumulative'] = pd.Series(Temps_cum)
		FED_dict[experiment]=FED_df


pickle.dump(FED_dict, open (output_dir+'FED.dict','wb'))
if not os.path.exists(output_table_loc):
	os.makedirs(output_table_loc)
FEDs_table.to_csv(output_table_loc+'FED_Table_dict.csv')
