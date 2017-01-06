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

channel_left='Bedroom67ft'
channel_right='Bedroom17ft'
N_rows=358
N_columns=12


i=0
temps=pd.DataFrame(np.zeros((N_rows,N_columns)))
for f in os.listdir(data_location):
	if f.endswith('.csv'):
		data_file=pd.read_csv(data_location+f)
		data_file=data_file.set_index('Time')

		##NEED TO BE ABLE TO READ SIDE
		Test_Name=f[:-4]
		Exp_Num=int(Test_Name[11:])

		## MUST LOAD IN EVENTS
		print(Test_Name)
		Events=pd.read_csv('../Info/Events/'+Test_Name+'_Events.csv')


		Events=Events.set_index('Event')

		if Exp_Num%2==0:
			Side='Right'
			channel=channel_right
			Ignition = datetime.datetime.strptime(Events['Time']['Ignition BR1'], '%Y-%m-%d-%H:%M:%S')
			# Locations=['LRFront','LRRear','DRFront','DRRear','HallRight','Bedroom2','Bedroom1','HallRightHF']

		elif Exp_Num%2==1:
			Side='Left'
			channel=channel_left
			Ignition = datetime.datetime.strptime(Events['Time']['Ignition BR6'], '%Y-%m-%d-%H:%M:%S')
			Int_Time=Ignition+timedelta(seconds=359)
			print(Int_Time,Ignition)
			# Locations=['LRFront','LRRear','DRFront','DRRear','HallLeft','Bedroom5','Bedroom6','HallLeftHF']
		else:
			 print ('ERROR 1')

		temp_vec=data_file[channel][str(Ignition):str(Int_Time)]#Ig,Ig+358
		print(temp_vec)
		exit()
		for j in range(len(temps[i])):
			temps.loc[j,i]=temp_vec[j]
		print(len(temp_vec))
		print(len(temps[i]))
		temps[:][i]=temp_vec
		# print (temps)
		print(channel)
		i=i+1
