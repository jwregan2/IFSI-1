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
wireless_data_dict = pickle.load(open(data_dir + 'metric_wireless_data.dict', 'rb'))

output_table_loc='../Tables/'

N_rows=12
N_columns=15
FEDs_table=pd.DataFrame(np.zeros((N_rows,N_columns)))
FEDs_table.columns=['Experiment','Attack Type','Test Length','Near Hall','Near Bedroom','Far Bedroom','Far Hall','Victim Open','Victim Closed','Near Hall Temp','Near Bedroom Temp','Far Bedroom Temp','Far Hall Temp','Victim Open Temp','Victim Closed Temp']
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
Gas_FED_dict = {}
Temp_FED_dict = {}
for experiment in test_des.index.values:
	print(experiment)
	side = test_des['Side'][experiment]

	#load slice of dictionary corresponding to expeiment
	data_df = test_data_dict[experiment]
	wireless_data = wireless_data_dict[experiment]
	events = test_events_dict[experiment]
	data_df = data_df.loc[0:]
	Gas_FED_df = pd.DataFrame(data={'Elapsed Time':data_df.index.values})
	Gas_FED_df = Gas_FED_df.set_index('Elapsed Time')
	Temp_FED_df = pd.DataFrame(data={'Elapsed Time':data_df.index.values})
	Temp_FED_df = Temp_FED_df.set_index('Elapsed Time')
	#find end of experiment or end of data recording in exp where data system failed
	for event in events.index.values:
			if events['Event'][event] == 'End of Experiment' or events['Event'][event] == 'Data System Error':
				end_time = event

	# loop through locations for each
	for chart in channels.index.values:
		if not channels[side+' Gas Name'][chart] + 'COV' in data_df.columns:
			# if not channels[side+' Gas Name'][chart] + '_CO':
			# 	FEDs_table.loc[experiment,chart] = 'No Data'
				continue
		if not channels[side+' Temp Name'][chart] in data_df.columns:
			# if not channels[side+' Temp Name'][chart]:
				FEDs_table.loc[experiment,chart+' Temp'] = 'No Data'
				continue
		if 'Victim' in chart:
			#for Victim gas and temps, consider using if statment
			CO_data = pd.Series(data_df[channels[side+' Gas Name'][chart]+ '_CO'].loc[0:end_time])
			CO2_data = pd.Series(data_df[channels[side+' Gas Name'][chart]+ '_CO2'].loc[0:end_time])
			O2_data = pd.Series(data_df[channels[side+' Gas Name'][chart]+ '_O2'].loc[0:end_time])
			temp_data = pd.Series(data_df[channels[side+' Temp Name'][chart]].loc[0:end_time])
		else:
			#for Victim gas and temps, consider using if statment
			CO_data = pd.Series(data_df[channels[side+' Gas Name'][chart]+ 'COV'].loc[0:end_time])
			CO2_data = pd.Series(data_df[channels[side+' Gas Name'][chart]+ 'CO2V'].loc[0:end_time])
			O2_data = pd.Series(data_df[channels[side+' Gas Name'][chart]+ 'O2V'].loc[0:end_time])
			temp_data = pd.Series(data_df[channels[side+' Temp Name'][chart]].loc[0:end_time])


		CO_FED=[]
		CO2_FED=[]
		O2_FED=[]
		FED_rate=[]
		FED_cum=[]

		Temps_conv=[]
		Temps_rad=[]
		Temps_rate=[]
		Temps_cum=[]

		#determine delta t for gas measurements
		
		
		#compute data for gas since delta t is =1, no need to compute
		for t in O2_data:
			O2_FED.append((1.0/60.0)*1/(exp(8.13-0.54*(20.9-t))))
		for t in CO2_data:
			CO2_FED.append(exp(t/5.0))
		for t in CO_data:
			CO_FED.append((1.0/60.0)*(t/35000.0))

		for i in range(min(len(O2_FED),len(CO2_FED),len(CO_FED))):
			FED_rate.append((O2_FED[i]+(CO2_FED[i]*CO_FED[i])))
			if i == 0:
				FED_cum.append((O2_FED[i]+(CO2_FED[i]*CO_FED[i])))
			# elif FED_cum[i-1] >1.0:
			# 	FEDs_table.loc[experiment,chart] = i
			# 	break
			elif i == min(len(O2_FED),len(CO2_FED),len(CO_FED))-1:
				FEDs_table.loc[experiment,chart] = ('NA: '+str(np.round(FED_cum[i-1],3)))
				break
			elif np.isnan(FED_cum[i-1]):
				FEDs_table.loc[experiment,chart] = ('NA: '+str(np.round(FED_cum[i-1],3)))
				break
			else:
				FED_cum.append((O2_FED[i]+(CO2_FED[i]*CO_FED[i]))+FED_cum[i-1])




		#compute data for temp
		for t in temp_data:
			if np.isnan(t):
				##If any of the temperatures are nans, act as if they are room temperature
				Temps_rad.append((2.72*10**14)/((25+273.0)**(1.35)))
				Temps_conv.append((5.0*10**7)*25)**(-3.4)
			else:
			# 	print(temp_data[1377:1380])		
				
				Temps_rad.append((2.72*10**14)/((max([t,0])+273.0)**(1.35)))
				Temps_conv.append((5.0*10**7)*max([t,0])**(-3.4))


		for i in range(min(len(Temps_rad),len(Temps_conv))):

			if i == 0:
				Temps_cum.append((1.0/60.0)*((1/Temps_rad[i])+(1/Temps_conv[i])))
				Temps_rate.append((1.0/60.0)*((1/Temps_rad[i])+(1/Temps_conv[i])))
			# elif Temps_cum[i-1] > 1.0:
			# 	label = str(chart+' Temp')
			# 	FEDs_table.loc[experiment,label] = i
			# 	print('1')
			# 	break
			elif i == min(len(Temps_rad),len(Temps_conv))-1:
				label = str(chart+' Temp')
				FEDs_table.loc[experiment,label] = str('NA: '+str(np.round(Temps_cum[i-1],3)))
				print('2')
				break
			elif np.isnan(Temps_cum[i-1]):
				label = str(chart+' Temp')
				FEDs_table.loc[experiment,label] = str('NA: '+str(np.round(Temps_cum[i-1],3)))
				print('3')
				break
			else:
				Temps_cum.append((1.0/60.0)*((1/Temps_rad[i])+(1/Temps_conv[i]))+Temps_cum[i-1])
				Temps_rate.append((1.0/60.0)*((1/Temps_rad[i])+(1/Temps_conv[i])))

		Gas_FED_df[chart] = pd.Series(FED_cum)
		Gas_FED_df[chart+' rate'] = pd.Series(FED_rate)
		Temp_FED_df[chart+' Temp'] = pd.Series(Temps_cum)
		Temp_FED_df[chart+' Temp rate'] = pd.Series(Temps_rate)
	Gas_FED_dict[experiment]=Gas_FED_df
	Temp_FED_dict[experiment] = Temp_FED_df
	print(Gas_FED_dict) 



pickle.dump(Gas_FED_dict, open (output_dir+'FED_gas.dict','wb'))
pickle.dump(Temp_FED_dict, open (output_dir+'FED_temp.dict','wb'))
# if not os.path.exists(output_table_loc):
# 	os.makedirs(output_table_loc)
# FEDs_table.to_csv(output_table_loc+'FED_Table_dict.csv')
