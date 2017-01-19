import pandas as pd 
import os as os
import numpy as np 
import matplotlib.pyplot as plt
from pylab import * 
import datetime
import shutil
from dateutil.relativedelta import relativedelta
from scipy.signal import butter, filtfilt
from itertools import cycle
from datetime import timedelta

data_location='../Data/'
output_location='../Tables/'
overhaul_times=pd.read_csv('../Info/Events/Overhaul_Times.csv')

N_rows = 12
N_cols_base = 7
N_cols_HF=8
N_Events=3

pre_ff_temp_7ft  = pd.DataFrame(np.zeros((N_rows, N_cols_base)))
pre_ff_temp_5ft  = pd.DataFrame(np.zeros((N_rows, N_cols_HF)))
pre_ff_temp_3ft  = pd.DataFrame(np.zeros((N_rows, N_cols_HF)))
hall_ff_temp_7ft = pd.DataFrame(np.zeros((N_rows, N_cols_base)))
hall_ff_temp_5ft = pd.DataFrame(np.zeros((N_rows, N_cols_HF)))
hall_ff_temp_3ft = pd.DataFrame(np.zeros((N_rows, N_cols_HF)))
#Column Header Format will be Ignition Intervention Time, Hallway Time
Events_of_interest=['Ignition #1','FF Intervention Time', 'Nozzle FF at Hallway Time']
Intervention_Times=pd.DataFrame(np.zeros((N_rows,N_Events)))
#Ext Temps, Int Temps
Environmental_Temps=pd.DataFrame(np.zeros((N_rows,2)))



Test_Names=[]
for f in os.listdir(data_location):
	if f.endswith('.csv'):
		Exp_data=pd.read_csv(data_location+f)
		# Overhaul_data=Exp_data
		Overhaul_data=Exp_data.set_index('Elapsed Time')
		Exp_data=Exp_data.set_index('Time')
		
		experiment=f
		print (experiment)

		Test_Name=experiment[:-4]
		print()
		print()
		print(Test_Name)

		Exp_Num=int(Test_Name[11:])
		
		Events=pd.read_csv('../Info/Events/'+Test_Name+'_Events.csv')


		Events=Events.set_index('Event')

		if Exp_Num%2==0:
			Side='Right'
			Ignition = datetime.datetime.strptime(Events['Time']['Ignition BR1'], '%Y-%m-%d-%H:%M:%S')
			Locations=['LRFront','LRRear','DRFront','DRRear','HallRight','Bedroom2','Bedroom1','HallRightHF']

		elif Exp_Num%2==1:
			Side='Left'
			Ignition = datetime.datetime.strptime(Events['Time']['Ignition BR6'], '%Y-%m-%d-%H:%M:%S')
			Locations=['LRFront','LRRear','DRFront','DRRear','HallLeft','Bedroom5','Bedroom6','HallLeftHF']
		else:
			 print ('ERROR 1')

		if Exp_Num in [1,3,6,8,10,11]:
			Int_time=datetime.datetime.strptime(Events['Time']['Water in Window'], '%Y-%m-%d-%H:%M:%S')
		elif Exp_Num in [2,4,5,7,9,12]:
			Int_time=datetime.datetime.strptime(Events['Time']['Front Door Open'], '%Y-%m-%d-%H:%M:%S')
		else:
			print('ERROR')

		FF_time=datetime.datetime.strptime(Events['Time']['Nozzle FF Reaches Hallway'], '%Y-%m-%d-%H:%M:%S')
		
		Intervention_Times.loc[Exp_Num-1,0]=str(Ignition)
		Intervention_Times.loc[Exp_Num-1,1]=str(Int_time)
		Intervention_Times.loc[Exp_Num-1,2]=str(FF_time)


		Dispatch_1=datetime.datetime.strptime(Events['Time']['FD Dispatch'], '%Y-%m-%d-%H:%M:%S')

		# Offsets=pd.read_csv('../Info/Events/Overhaul_Offsets.csv')
		# Offsets=Offsets.set_index('Experiment')


		# if Offsets['Operation'][Exp_Num]=='Add':

		# 	Dispatch_Time=(datetime.datetime.strptime(overhaul_times['FD Dispatch'][Exp_Num-1], '%H:%M:%S')+timedelta(seconds=Offsets['Offset s'][Exp_Num]))#datetime.datetime.strptime(Offsets['Offset'][Exp_Num], '%H:%M:%S')))#datetime.datetime.strptime(overhaul_times['FD Dispatch'][Exp_Num-1], '%H:%M:%S')
		# 	Command_Transfer=(datetime.datetime.strptime(overhaul_times['Command Transfer'][Exp_Num-1], '%H:%M:%S')+datetime.datetime.strptime(Offsets['Offset'][Exp_Num], '%H:%M:%S'))#datetime.datetime.strptime(overhaul_times['Command Transfer'][Exp_Num-1], '%H:%M:%S')
		# 	Overhaul_Enter_Time=(datetime.datetime.strptime(overhaul_times['OH Enter'][Exp_Num-1], '%H:%M:%S')+datetime.datetime.strptime(Offsets['Offset'][Exp_Num], '%H:%M:%S'))#datetime.datetime.strptime(overhaul_times['OH Enter'][Exp_Num-1], '%H:%M:%S')
		# 	Overhaul_Exit_Time=(datetime.datetime.strptime(overhaul_times['OH Exit'][Exp_Num-1], '%H:%M:%S')+datetime.datetime.strptime(Offsets['Offset'][Exp_Num], '%H:%M:%S'))#, '%H:%M:%S'datetime.datetime.strptime(overhaul_times['OH Exit'][Exp_Num-1], '%H:%M:%S')
		# elif Offsets['Operation'][Exp_Num]=='Subract':
		# 	Dispatch_Time=(datetime.datetime.strptime(overhaul_times['FD Dispatch'][Exp_Num-1], '%H:%M:%S')-datetime.datetime.strptime(Offsets['Offset'][Exp_Num], '%H:%M:%S'))#datetime.datetime.strptime(overhaul_times['FD Dispatch'][Exp_Num-1], '%H:%M:%S')
		# 	Command_Transfer=(datetime.datetime.strptime(overhaul_times['Command Transfer'][Exp_Num-1], '%H:%M:%S')-datetime.datetime.strptime(Offsets['Offset'][Exp_Num], '%H:%M:%S'))#datetime.datetime.strptime(overhaul_times['Command Transfer'][Exp_Num-1], '%H:%M:%S')
		# 	Overhaul_Enter_Time=(datetime.datetime.strptime(overhaul_times['OH Enter'][Exp_Num-1], '%H:%M:%S')-datetime.datetime.strptime(Offsets['Offset'][Exp_Num], '%H:%M:%S'))#datetime.datetime.strptime(overhaul_times['OH Enter'][Exp_Num-1], '%H:%M:%S')
		# 	Overhaul_Exit_Time=(datetime.datetime.strptime(overhaul_times['OH Exit'][Exp_Num-1], '%H:%M:%S')-datetime.datetime.strptime(Offsets['Offset'][Exp_Num], '%H:%M:%S'))
		# else:
		# 	print('ERROR ADD')

		Dispatch_Time=overhaul_times['FD Dispatch'][Exp_Num-1]#datetime.datetime.strptime(overhaul_times['FD Dispatch'][Exp_Num-1], '%H:%M:%S')
		Command_Transfer=overhaul_times['Command Transfer'][Exp_Num-1]#datetime.datetime.strptime(overhaul_times['Command Transfer'][Exp_Num-1], '%H:%M:%S')
		Overhaul_Enter_Time=overhaul_times['OH Enter'][Exp_Num-1]#datetime.datetime.strptime(overhaul_times['OH Enter'][Exp_Num-1], '%H:%M:%S')
		Overhaul_Exit_Time=overhaul_times['OH Exit'][Exp_Num-1]#, '%H:%M:%S'datetime.datetime.strptime(overhaul_times['OH Exit'][Exp_Num-1], '%H:%M:%S')
		






		heights=['3ft','5ft','7ft']
		for height in heights:
			if height=='3ft':
				for i in range(len(Locations)):
					try:
						pre_ff_temp_3ft.loc[Exp_Num-1,i] = max(Exp_data[str(Locations[i])+str(height)][str(Ignition):str(Int_time)])
						hall_ff_temp_3ft.loc[Exp_Num-1,i]=Exp_data[str(Locations[i])+str(height)][str(FF_time)]
					except:
					 	pre_ff_temp_3ft.loc[Exp_Num-1,i] = 'NaN'
					 	hall_ff_temp_3ft.loc[Exp_Num-1,i]= 'NaN'
			if height=='5ft':
				for i in range(len(Locations)):
					try:
						pre_ff_temp_5ft.loc[Exp_Num-1,i] = max(Exp_data[str(Locations[i])+str(height)][str(Ignition):str(Int_time)])
						hall_ff_temp_5ft.loc[Exp_Num-1,i]=Exp_data[str(Locations[i])+str(height)][str(FF_time)]
					except:
					 	pre_ff_temp_5ft.loc[Exp_Num-1,i] = 'NaN'
					 	hall_ff_temp_5ft.loc[Exp_Num-1,i]= 'NaN'
			if height=='7ft':
				for i in range(len(Locations)):
					try						
						pre_ff_temp_7ft.loc[Exp_Num-1,i] = max(Exp_data[str(Locations[i])+str(height)][str(Ignition):str(Int_time)])
						hall_ff_temp_7ft.loc[Exp_Num-1,i]=Exp_data[str(Locations[i])+str(height)][str(FF_time)]
					except:
					 	pre_ff_temp_7ft.loc[Exp_Num-1,i] = 'NaN'
					 	hall_ff_temp_7ft.loc[Exp_Num-1,i]= 'NaN'
		#Ext Temp ()
		
		#Int Temp (HW5ft)

		# if Exp_Num==1:
		# 	Environmental_Temps.loc[Exp_Num-1,0]=0
		# 	Environmental_Temps.loc[Exp_Num-1,1]=0
		# if Exp_Num==12:

		if Side=='Left':
			if Exp_Num==1:
				Environmental_Temps.loc[Exp_Num-1,1]=0
				Environmental_Temps.loc[Exp_Num-1,0]=np.mean(Exp_data['Bedroom11ft'][str(Dispatch_1):str(datetime.datetime.strptime(Events['Time']['Data System Error'], '%Y-%m-%d-%H:%M:%S'))])
			# try:
			else:
				try:
					print(Overhaul_Enter_Time,Overhaul_Exit_Time)
					print(Overhaul_data.index.values)
					Environmental_Temps.loc[Exp_Num-1,1]=np.mean(Overhaul_data['HallLeft5ft'][str(Overhaul_Enter_Time):str(Overhaul_Exit_Time)])
					Environmental_Temps.loc[Exp_Num-1,0]=np.mean(Overhaul_data['Bedroom11ft'][str(Dispatch_Time):str(Command_Transfer)])
					print(Environmental_Temps)
				except:
					pass
		elif Side=='Right':
			try:
				print(Overhaul_Enter_Time,Overhaul_Exit_Time)
				print(Overhaul_data.index.values)
				Environmental_Temps.loc[Exp_Num-1,1]=np.mean(Overhaul_data['HallRight5ft'][str(Overhaul_Enter_Time):str(Overhaul_Exit_Time)])
				Environmental_Temps.loc[Exp_Num-1,0]=np.mean(Overhaul_data['Bedroom61ft'][str(Dispatch_Time):str(Command_Transfer)])
				print(Environmental_Temps)
			except:
				pass
		else:
			print('ERROR 3')
		Test_Names.append(Exp_Num)






print('saving'+'pre_ff_temp_7ft')

# pre_ff_temp_7ft =pre_ff_temp_7ft.set_index(int(Test_Names))
pre_ff_temp_7ft.columns=['LRFront','LRRear','DRFront','DRRear','Hall','Bedroom2/5','Bedroom1/6','HallHF']
pre_ff_temp_7ft.to_csv(output_location+'pre_ff_temp_7ft.csv')

print('saving'+'pre_ff_temp_5ft')
pre_ff_temp_5ft.rows=Test_Names
pre_ff_temp_5ft.columns=['LRFront','LRRear','DRFront','DRRear','Hall','Bedroom2/5','Bedroom1/6','HallHF']
pre_ff_temp_5ft.to_csv(output_location+'pre_ff_temp_5ft.csv')

print('saving'+'pre_ff_temp_3ft')
pre_ff_temp_3ft.rows=Test_Names
pre_ff_temp_3ft.columns=['LRFront','LRRear','DRFront','DRRear','Hall','Bedroom2/5','Bedroom1/6','HallHF']
pre_ff_temp_3ft.to_csv(output_location+'pre_ff_temp_3ft.csv')

print('saving'+'hall_ff_temp_7ft')
hall_ff_temp_7ft.rows=Test_Names
hall_ff_temp_7ft.columns=['LRFront','LRRear','DRFront','DRRear','Hall','Bedroom2/5','Bedroom1/6','HallHF']
hall_ff_temp_7ft.to_csv(output_location+'hall_ff_temp_7ft.csv')

print('saving'+'hall_ff_temp_5ft')
hall_ff_temp_5ft.rows=Test_Names
hall_ff_temp_5ft.columns=['LRFront','LRRear','DRFront','DRRear','Hall','Bedroom2/5','Bedroom1/6','HallHF']
hall_ff_temp_5ft.to_csv(output_location+'hall_ff_temp_5ft.csv')

print('saving'+'hall_ff_temp_3ft')
hall_ff_temp_3ft.rows=Test_Names
hall_ff_temp_3ft.columns=['LRFront','LRRear','DRFront','DRRear','Hall','Bedroom2/5','Bedroom1/6','HallHF']
hall_ff_temp_3ft.to_csv(output_location+'hall_ff_temp_3ft.csv')

print('saving Intervention Times')
Intervention_Times.columns=[Events_of_interest]
Intervention_Times.to_csv(output_location+'Intervention_Times.csv')

print('saving Events')
Environmental_Temps.columns=['Exterior Ave','Interior Ave']
Environmental_Temps.to_csv(output_location+'Environmental_Temps.csv')


