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
output_location='../Figures/'

channels=pd.read_csv('../Info/Channels.csv')
channels=channels.set_index('Chart')

Exp_Des=pd.read_csv('../Info/Description_of_Experiments.csv')
Exp_Des=Exp_Des.set_index('Experiment')

# channel_left='Bedroom67ft'
# channel_right='Bedroom17ft'
N_rows=358
N_columns=12

markers = ['s', '*', '^', 'o', '<', '>', '8', 'h','d','x','p','v','H', 'D', '1', '2', '3', '4', '|']
colors = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

# Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
for i in range(len(colors)):
    r, g, b = colors[i]
    colors[i] = (r / 255., g / 255., b / 255.)







for chart in channels.index.values:
	print(chart)
	Exp_Names=[]
	max_temp=0
	i=0
	temps=pd.DataFrame(np.zeros((N_rows,N_columns)))
	for f in os.listdir(data_location):
		if f.endswith('.csv'):
			data_file=pd.read_csv(data_location+f)
			data_file=data_file.set_index('Time')

			##NEED TO BE ABLE TO READ SIDE
			Test_Name=f[:-4]
			Exp_Names.append(Test_Name)
			Exp_Num=int(Test_Name[11:])

			## MUST LOAD IN EVENTS
			print(Test_Name)
			Events=pd.read_csv('../Info/Events/'+Test_Name+'_Events.csv')


			Events=Events.set_index('Event')

			if Exp_Num%2==0:
				Side='Right'
				channel=channels['Right_Channel'][chart]
				Ignition = datetime.datetime.strptime(Events['Time']['Ignition BR1'], '%Y-%m-%d-%H:%M:%S')
				Int_Time=Ignition+timedelta(seconds=359)
				# Locations=['LRFront','LRRear','DRFront','DRRear','HallRight','Bedroom2','Bedroom1','HallRightHF']

			elif Exp_Num%2==1:
				Side='Left'
				channel=channels['Left_Channel'][chart]
				Ignition = datetime.datetime.strptime(Events['Time']['Ignition BR6'], '%Y-%m-%d-%H:%M:%S')
				Int_Time=Ignition+timedelta(seconds=359)

				# Locations=['LRFront','LRRear','DRFront','DRRear','HallLeft','Bedroom5','Bedroom6','HallLeftHF']
			else:
				 print ('ERROR 1')

			temp_vec=data_file[channel][str(Ignition):str(Int_Time)]#Ig,Ig+358
			temp_vec=temp_vec.reset_index()
			max_temp=max([max_temp,max((temp_vec[channel]))])


			for j in range(len(temps[i])):
				if j<len(temp_vec):
					temps.loc[j,i]=temp_vec[channel][j]
				else:
					continue

			# print (temps)
			i=i+1
	time_vector=np.linspace(1,358,358)


	##2 x standard DEV
	fig = figure()
	for i in range(12):
		y = temps[i]
		plot(time_vector[0:len(time_vector)-1],y[0:len(time_vector)-1],color=colors[i],marker=markers[i],markevery=50,ms=8,label=Exp_Names[i])
	plot(time_vector[0:len(time_vector)-1],temps[0:len(time_vector)-1].mean(axis=1),'k',label='average'+'AVG',linewidth=3)
	plt.fill_between(time_vector[0:len(time_vector)-1] ,temps[0:len(time_vector)-1].mean(axis=1)+2*temps[0:len(time_vector)-1].std(axis=1), temps[0:len(time_vector)-1].mean(axis=1)-2*temps[0:len(time_vector)-1].std(axis=1), facecolor='gray',alpha=0.5, interpolate=True,linewidth=3)
	# plt.fill_between(time_vector[0:len(time_vector)-1],.9*temps[0:len(time_vector)-1].mean(axis=1), 1.1*temps[0:len(time_vector)-1].mean(axis=1), facecolor='gray',alpha=0.5, interpolate=True,linewidth=3)
	ax1 = gca()
	xlabel('Time (s)', fontsize=20)
	ylabel('Temperature (C)', fontsize=20)
	xticks(fontsize=16)
	yticks(fontsize=16)
	legend(numpoints=1,loc=1,ncol=2,fontsize=16)
	axis([0, 1.1*N_rows, 0, 1.1*max_temp])
	box = ax1.get_position()
	ax1.set_position([box.x0, box.y0, box.width * 0.75, box.height])
	# ax1.set_xlim([0,1.1*N_rows])

	# ax1.set_ylim([0,1.1*max_temp])
	ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	grid(True)

	savefig(output_location+ 'standard_dev/'+chart + '.pdf',format='pdf')
	close()

	##+- 10%

	fig = figure()
	for i in range(12):
		y = temps[i]
		plot(time_vector[0:len(time_vector)-1],y[0:len(time_vector)-1],color=colors[i],marker=markers[i],markevery=50,ms=8,label=Exp_Names[i].replace('_',' '))
	plot(time_vector[0:len(time_vector)-1],temps[0:len(time_vector)-1].mean(axis=1),'k',label='Average',linewidth=3)
	# plt.fill_between(time_vector[0:len(time_vector)-1] ,temps[0:len(time_vector)-1].mean(axis=1)+2*temps[0:len(time_vector)-1].std(axis=1), temps[0:len(time_vector)-1].mean(axis=1)-2*temps[0:len(time_vector)-1].std(axis=1), facecolor='gray',alpha=0.5, interpolate=True,linewidth=3)
	plt.fill_between(time_vector[0:len(time_vector)-1],.9*temps[0:len(time_vector)-1].mean(axis=1), 1.1*temps[0:len(time_vector)-1].mean(axis=1), facecolor='gray',alpha=0.5, interpolate=True,linewidth=3)
	ax1 = gca()
	xlabel('Time (s)', fontsize=20)
	ylabel('Temperature (C)', fontsize=20)
	xticks(fontsize=16)
	yticks(fontsize=16)
	legend(numpoints=1,loc=1,ncol=2,fontsize=16)
	axis([0, 1.1*N_rows, 0, 1.1*max_temp])
	box = ax1.get_position()
	ax1.set_position([box.x0, box.y0, box.width * 0.75, box.height])
	# ax1.set_xlim([0,1.1*N_rows])

	# ax1.set_ylim([0,1.1*max_temp])
	ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	grid(True)

	savefig(output_location+ '10percent_TC/'+ chart + '.pdf',format='pdf')
	close()