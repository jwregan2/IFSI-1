from __future__ import division
import numpy as np
import os as os
import numpy.ma as ma
import pandas as pd
import itertools
from pylab import *
from matplotlib import rcParams
import pandas as pd 
from dateutil.relativedelta import relativedelta
from scipy.signal import butter, filtfilt
from itertools import cycle
from datetime import timedelta

data_location='../Data/'

transport_times=pd.read_csv('../Info/Gas_Transport.csv')
transport_times=transport_times.set_index('Room')

channels=pd.read_csv('../Info/FED_Channels.csv')
channels=channels.set_index('Chart')

output_table_loc='../Tables/'

N_rows=12
N_columns=15

##SPECIFY DESIRED HEIGHTS FOR TEMP FED COMPUTATIONS##
conv_height='7ft'
rad_height='7ft'

FEDs_df=pd.DataFrame(np.zeros((N_rows,N_columns)))
FEDs_df.columns=['Experiment','FD Dispatch','Water in Window','Water in BR','Front Door','Nozzle FF Reaches Hallway','Victim 1 Out','Victim 2 Out','FD Dispatch (Temp)','Water in Window (Temp)','Water in BR (Temp)','Front Door (Temp)','Nozzle FF Reaches Hallway (Temp)','Victim 1 Out (Temp)','Victim 2 Out (Temp)']
Exp_Names=[]
for f in os.listdir(data_location):
	if f.endswith('.csv'):
		Exp_Names.append(f[:-4])
for i in range(len(FEDs_df)):
	FEDs_df.loc[i,'Experiment']=Exp_Names[i]

FEDs_df=FEDs_df.set_index('Experiment')
Near_Hall_df=FEDs_df.copy()
Far_Hall_df=FEDs_df.copy()
events_of_interest=['FD Dispatch','Water in Window','Water in BR','Front Door','Nozzle FF Reaches Hallway','Victim 1 Out','Victim 2 Out']


Exp_Names=[]
for f in os.listdir(data_location):
	if f.endswith('.csv'):
			data_file=pd.read_csv(data_location+f,low_memory=False)
			for i in range(len(data_file['Elapsed Time'])):

				if pd.isnull(data_file['Elapsed Time'][i]):

					data_file=data_file.ix[:i-1]
					break
				else:
					continue

			data_file=data_file.set_index('Time')

			##NEED TO BE ABLE TO READ SIDE
			Test_Name=f[:-4]
			Exp_Names.append(Test_Name)
			Exp_Num=int(Test_Name[11:])
			print(Test_Name)

			## MUST LOAD IN EVENTS

			Events=pd.read_csv('../Info/Events/'+Test_Name+'_Events.csv')
			Events=Events.set_index('Event')

			if Exp_Num%2==0:
				Side='Right'
				Temp_label='Right Temp Name'
				Gas_label='Right Gas Name'
				Ignition_mdy = datetime.datetime.strptime(Events['Time']['Ignition BR1'], '%Y-%m-%d-%H:%M:%S')
				Ignition_elapsed=data_file['Elapsed Time'][str(Ignition_mdy)]
			elif Exp_Num%2==1:
				Side='Left'
				Temp_label='Left Temp Name'
				Gas_label='Left Gas Name'
				Ignition_mdy = datetime.datetime.strptime(Events['Time']['Ignition BR6'], '%Y-%m-%d-%H:%M:%S')
				Ignition_elapsed=data_file['Elapsed Time'][str(Ignition_mdy)]
			else:
				 print ('ERROR 1')
			
			try:
				End_Experiment_mdy=datetime.datetime.strptime(Events['Time']['End of Experiment'], '%Y-%m-%d-%H:%M:%S')
				End_Experiment_elapsed=data_file['Elapsed Time'][str(End_Experiment_mdy)]
			except:
				End_Experiment_mdy=datetime.datetime.strptime(Events['Time']['Data System Error'], '%Y-%m-%d-%H:%M:%S')
				End_Experiment_elapsed=data_file['Elapsed Time'][str(End_Experiment_mdy)]








			Time = [datetime.datetime.strptime(t, '%H:%M:%S') for t in data_file['Elapsed Time']]
			Time = [((t - datetime.datetime.strptime(Ignition_elapsed, '%H:%M:%S')).total_seconds()) for t in Time]
		
			End_Time=(datetime.datetime.strptime(End_Experiment_elapsed, '%H:%M:%S')-datetime.datetime.strptime(Ignition_elapsed, '%H:%M:%S')).total_seconds()


			for loc in channels.index.values:
				if 'Hall' in loc:
					print(loc)
					CO_FED=[]
					CO2_FED=[]
					O2_FED=[]
					FED_cum=[]
					Temps_conv=[]
					Temps_rad=[]
					Temps_cum=[]
					##Compute ign time for each Gas
					#Reset Ignition time so that FED will be computed from the actual ignition time, considering transport time of O2
					O2_ign=Ignition_mdy+timedelta(seconds=(int(transport_times['Time (s) O2'][channels[Gas_label][loc]])))
					O2_end=End_Experiment_mdy-timedelta(seconds=60)+timedelta(seconds=(int(transport_times['Time (s) O2'][channels[Gas_label][loc]])))

					#Reset Ignition time so that FED will be computed from the actual ignition time, considering transport time of O2
					CO2_ign=Ignition_mdy+timedelta(seconds=int(transport_times['Time (s) CO2'][channels[Gas_label][loc]]))
					CO2_end=End_Experiment_mdy-timedelta(seconds=60)+timedelta(seconds=(int(transport_times['Time (s) CO2'][channels[Gas_label][loc]])))


					#Reset Ignition time so that FED will be computed from the actual ignition time, considering transport time of O2
					CO_ign=Ignition_mdy+timedelta(seconds=int(transport_times['Time (s) CO'][channels[Gas_label][loc]]))
					CO_end=End_Experiment_mdy-timedelta(seconds=60)+timedelta(seconds=(int(transport_times['Time (s) CO'][channels[Gas_label][loc]])))


					##Compute O2 Fractions
					if channels[Gas_label][loc]=='Victim1'or 'Victim2':
						try:
							for x in data_file[channels[Gas_label][loc]+'O2'][str(O2_ign):str(O2_end)]:	
								O2_FED.append((1.0/60.0)*1/(exp(8.13-0.54*(20.9-float(x)))))
							
							##CO Fraction
							for x in data_file[channels[Gas_label][loc]+'CO2'][str(CO2_ign):str(CO2_end)]:
								CO2_FED.append(exp(x/5))
							##CO2Fraction
							for x in data_file[channels[Gas_label][loc]+'CO'][str(CO_ign):str(CO_end)]:
								CO_FED.append((1.0/60.0)*(x/35000.0))
							FEDs_df.loc[Test_Name,'Test Length']=min([len(CO2_FED),len(O2_FED),len(CO_FED)])
						except:
							print('NO DATA FOR ' +channels[Gas_label][loc])
							FEDs_df.loc[Test_Name,loc]=('No Data')
					else:				
						try:
							for x in data_file[channels[Gas_label][loc]+'O2V'][str(O2_ign):str(O2_end)]:
								O2_FED.append((1.0/60.0)*1/(exp(8.13-0.54*(20.9-float(5.0*x)))))
							
							##CO Fraction
							for x in data_file[channels[Gas_label][loc]+'CO2V'][str(CO2_ign):str(CO2_end)]:
								CO2_FED.append(exp(5.0*x/5))
							##CO2Fraction
							for x in data_file[channels[Gas_label][loc]+'COV'][str(CO_ign):str(CO_end)]:
								CO_FED.append((1.0/60.0)*(10000.0*x/35000.0))
							FEDs_df.loc[Test_Name,'Test Length']=min([len(CO2_FED),len(O2_FED),len(CO_FED)])
						except:
							print('NO DATA FOR ' +channels[Gas_label][loc])
							FEDs_df.loc[Test_Name,loc]=('No Data')



					for i in range(min([len(CO2_FED),len(O2_FED),len(CO_FED)])):
						if i==0:	
							FED_cum.append(CO2_FED[i]*CO_FED[i]+O2_FED[i])
						elif i==min([len(CO2_FED),len(O2_FED),len(CO_FED)])-1:

							continue
						else:
							FED_cum.append((CO2_FED[i]*CO_FED[i]+O2_FED[i])+FED_cum[i-1])

					EventTime=list(range(len(Events.index.values)))

					for i in range(len(Events.index.values)):
						if loc=='Near Hall':
							for column in Near_Hall_df:
								if column in Events.index.values[i]:
									try:
										j = (datetime.datetime.strptime(Events['Time'][Events.index.values[i]], '%Y-%m-%d-%H:%M:%S')-Ignition_mdy).total_seconds()
										Near_Hall_df.loc[Test_Name,column]=round(FED_cum[int(j)],5)
									except:
										Far_Hall_df.loc[Test_Name,column]='No Sensor'
						else:
							for column in Far_Hall_df:
								if column in Events.index.values[i]:
									try:	
										j = (datetime.datetime.strptime(Events['Time'][Events.index.values[i]], '%Y-%m-%d-%H:%M:%S')-Ignition_mdy).total_seconds()
										Far_Hall_df.loc[Test_Name,column]=round(FED_cum[int(j)],5)
									except:
										Far_Hall_df.loc[Test_Name,column]='No Sensor'


					##GAS FEDS COMPLETE
					##COMPUTE TEMPS FEDs
					try:
						for x in data_file[channels[Temp_label][loc]][str(Ignition_mdy):str(End_Experiment_mdy)]:
							if np.isnan(x):
								##If any of the temperatures are nans, act as if they are room temperature
								# Temps_rad.append((2.72*10**14)/((25+273.0)**(1.35)))
								Temps_conv.append((5.0*10**7)*25)**(-3.4)
							else:
								# Temps_rad.append((2.72*10**14)/((max([x,0])+273.0)**(1.35)))
								Temps_conv.append((5.0*10**7)*max([x,0])**(-3.4))
						# rad_loc=channels[Temp_label][loc][:-3]+'7ft'

						# for x in data_file[rad_loc][str(Ignition_mdy):str(End_Experiment_mdy)]:
						for x in data_file[channels[Temp_label][loc]][str(Ignition_mdy):str(End_Experiment_mdy)]:					
							if np.isnan(x):
								##If any of the temperatures are nans, act as if they are room temperature
								Temps_rad.append((2.72*10**14)/((25+273.0)**(1.35)))
								# Temps_conv.append((5.0*10**7)*25)**(-3.4)
							else:
								Temps_rad.append((2.72*10**14)/((max([x,0])+273.0)**(1.35)))
								# Temps_conv.append((5.0*10**7)*max([x,0])**(-3.4))
						
					except:
						print('NO DATA FOR ' +channels[Temp_label][loc])
						FEDs_df.loc[Test_Name,loc+' Temp']=('No Data')
				

					for i in range(min([len(Temps_conv),len(Temps_rad)])):

						if i==0:	
							# Temps_cum.append((1/60)*((1/Temps_conv[i])+(1/Temps_rad[i])))
							Temps_cum.append((1/60)*((1/Temps_conv[i])))
						elif i==min([len(Temps_conv),len(Temps_rad)])-1:
							# FEDs_df.loc[Test_Name,loc+' Temp']=('N/A '+str(round((1/60)*((1/Temps_conv[i])+(1/Temps_rad[i]))+Temps_cum[i-1],3)))
							# FEDs_df.loc[Test_Name,loc+' Temp']=('N/A ('+str(round((1/60)*((1/Temps_conv[i]))+Temps_cum[i-1],3))+')')
							continue
						else:
							# Temps_cum.append((1/60)*((1/Temps_conv[i])+(1/Temps_rad[i]))+Temps_cum[i-1])
							Temps_cum.append((1/60)*((1/Temps_conv[i]))+Temps_cum[i-1])

					EventTime=list(range(len(Events.index.values)))

					for i in range(len(Events.index.values)):
						if loc=='Near Hall':
							for column in Near_Hall_df:
								if column in Events.index.values[i]:
									try:
										j = (datetime.datetime.strptime(Events['Time'][Events.index.values[i]], '%Y-%m-%d-%H:%M:%S')-Ignition_mdy).total_seconds()
										Near_Hall_df.loc[Test_Name,column+' (Temp)']=round(Temps_cum[int(j)],5)
									except:
										Far_Hall_df.loc[Test_Name,column+' (Temp)']='No Sensor'
						elif loc =='Far Hall':
							for column in Far_Hall_df:
								if column in Events.index.values[i]:
									try:
										j = (datetime.datetime.strptime(Events['Time'][Events.index.values[i]], '%Y-%m-%d-%H:%M:%S')-Ignition_mdy).total_seconds()
										Far_Hall_df.loc[Test_Name,column+' (Temp)']=round(Temps_cum[int(j)],5)
									except:
										Far_Hall_df.loc[Test_Name,column+' (Temp)']='No Sensor'
						else:
							print('Error Temp')

				else: 
					continue

				#add FEDs
print(Near_Hall_df)
print(Far_Hall_df)
if not os.path.exists(output_table_loc):
	os.makedirs(output_table_loc)
Near_Hall_df.to_csv(output_table_loc+'Near_Hall_Table.csv')
Far_Hall_df.to_csv(output_table_loc+'Far_Hall_Table.csv')