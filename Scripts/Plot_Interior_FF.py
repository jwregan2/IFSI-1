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
output_location_init='../Figures/'
FF_Times=pd.read_csv('../Info/FF_Times.csv')
FF_Times=FF_Times.set_index('Experiment')

channels=pd.read_csv('../Info/Channels.csv')
channels=channels.set_index('Chart')

Exp_Des=pd.read_csv('../Info/Description_of_Experiments.csv')
Exp_Des=Exp_Des.set_index('Experiment')

##FIND MAXIMUM EXPERIMENT LENGTH##
Test_Length=[]
for f in os.listdir(data_location):
	if f.endswith('.csv'):
		Test_Name=f[:-4]
		Exp_Num=int(Test_Name[11:])
		Events=pd.read_csv('../Info/Events/'+Test_Name+'_Events.csv')
		Events=Events.set_index('Event')

		if Exp_Num%2==0:
			Side='Right'
			Ignition = datetime.datetime.strptime(Events['Time']['Front Door Open'], '%Y-%m-%d-%H:%M:%S')
			# Locations=['LRFront','LRRear','DRFront','DRRear','HallRight','Bedroom2','Bedroom1','HallRightHF']
			# try:
			# 	End_Experiment=datetime.datetime.strptime(Events['Time']['End of Experiment'], '%Y-%m-%d-%H:%M:%S')
			# 	# End_Experiment_elapsed=data_file['Elapsed Time'][str(End_Experiment_mdy)]
			# except:
			# 	End_Experiment=datetime.datetime.strptime(Events['Time']['Data System Error'], '%Y-%m-%d-%H:%M:%S')
			# 	# End_Experiment_elapsed=data_file['Elapsed Time'][str(End_Experiment_mdy)]
		elif Exp_Num%2==1:
			Side='Left'
			Ignition = datetime.datetime.strptime(Events['Time']['Front Door Open'], '%Y-%m-%d-%H:%M:%S')
			# try:
			# 	End_Experiment=datetime.datetime.strptime(Events['Time']['End of Experiment'], '%Y-%m-%d-%H:%M:%S')
			# 	# End_Experiment_elapsed=data_file['Elapsed Time'][str(End_Experiment_mdy)]
			# except:
			# 	End_Experiment=datetime.datetime.strptime(Events['Time']['Data System Error'], '%Y-%m-%d-%H:%M:%S')
			# 	# End_Experiment_elapsed=data_file['Elapsed Time'][str(End_Experiment_mdy)]
		else:
			 print ('ERROR 1')		
		# Test_Length.append((End_Experiment-Ignition).total_seconds())
# print(Test_Length)

N_rows=600#max(Test_Length)
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



channel_list=['Attack FF','Search FF']
interior_exps = [2,4,5,7,9,12]



for chart in channels.index.values:
	if chart in channel_list:
		print(chart)

		Exp_Names=[]
		max_temp=0
		i=0

		temps=np.empty((N_rows,N_columns))
		temps[:]=np.NaN
		temps=pd.DataFrame(temps)


		temps_left=np.empty((N_rows,.5*N_columns))
		temps_left[:]=np.nan
		temps_left=pd.DataFrame(temps)

		temps_right=np.empty((N_rows,.5*N_columns))
		temps_right[:]=np.nan
		temps_right=pd.DataFrame(temps_right)

		for f in os.listdir(data_location):
			if f.endswith('.csv'):
				# try:
					data_file=pd.read_csv(data_location+f,low_memory=False)
					data_file=data_file.set_index('Time')

					if channels['Gas'][chart]=='Y':
						data_copy = data_file.drop('Elapsed Time', axis=1)
						data_copy = data_copy.rolling(window=15, center=True).mean()
						data_copy.insert(0, 'Elapsed Time', data_file['Elapsed Time'])
						data_file = data_copy


					##NEED TO BE ABLE TO READ SIDE
					Test_Name=f[:-4]
					Exp_Names.append(Test_Name)
					Exp_Num=int(Test_Name[11:])
					print(Exp_Num)
					if Exp_Num in interior_exps:

						## MUST LOAD IN EVENTS

						Events=pd.read_csv('../Info/Events/'+Test_Name+'_Events.csv')
						Events=Events.set_index('Event')



						if Exp_Num%2==0:
							Side='Right'
							channel=channels['Right_Channel'][chart] 
							Ignition = datetime.datetime.strptime(Events['Time']['Front Door Open'], '%Y-%m-%d-%H:%M:%S')+timedelta(seconds=FF_Times[chart+' Enters'][Exp_Num])

							End_Chart = datetime.datetime.strptime(Events['Time']['Front Door Open'], '%Y-%m-%d-%H:%M:%S')+timedelta(seconds=FF_Times[chart+' Exits'][Exp_Num])

							# if channels['Gas'][chart]=='Y':
							# 	Ignition=Ignition+timedelta(seconds=int(channels['Right Transport'][chart]))
							Factor=channels['Right Factor'][chart]
							# Int_Time=Ignition+timedelta(seconds=int(N_rows))
							# Locations=['LRFront','LRRear','DRFront','DRRear','HallRight','Bedroom2','Bedroom1','HallRightHF']

						elif Exp_Num%2==1:
							Side='Left'
							channel=channels['Left_Channel'][chart]
							Ignition = datetime.datetime.strptime(Events['Time']['Front Door Open'], '%Y-%m-%d-%H:%M:%S')+timedelta(seconds=FF_Times[chart+' Enters'][Exp_Num])

							End_Chart = datetime.datetime.strptime(Events['Time']['Front Door Open'], '%Y-%m-%d-%H:%M:%S')+timedelta(seconds=FF_Times[chart+' Exits'][Exp_Num])
							# if channels['Gas'][chart]=='Y':
							# 	Ignition=Ignition+timedelta(seconds=int(channels['Left Transport'][chart]))
							Factor=channels['Left Factor'][chart]											
							# Int_Time=Ignition+timedelta(seconds=int(N_rows))

							# Locations=['LRFront','LRRear','DRFront','DRRear','HallLeft','Bedroom5','Bedroom6','HallLeftHF']
						else:
							 print ('ERROR 1')
						# if Exp_Num==1:
						# 	if channels['Gas'][chart]=='Y':
						# 		End_Chart=Ignition+timedelta(seconds=Test_Length[i])-timedelta(seconds=60)

						# 	else:
						# 		End_Chart=Ignition+timedelta(seconds=Test_Length[i])

						# else:
						# 	End_Chart=Int_Time
						temp_vec=data_file[channel][str(Ignition):str(End_Chart)]#Ig,Ig+358
						temp_vec=temp_vec.reset_index()



						# if channels['Gas'][chart]=='Y':
						for j in range(len(temps[i])):
							if j<len(temp_vec):
								temps.loc[j,i]=Factor*temp_vec[channel][j]
							else:
								continue
						# else:
						# 	for j in range(len(temps[i])):
						# 		if j<len(temp_vec):
						# 			temps.loc[j,i]=temp_vec[channel][j]
						# 		else:
						# 			continue	
						# print (temps)
						i=i+1
					else:
						continue
					# except:
					# 	print(chart+' '+Test_Name+' DNE')
					# 	i=i+1
		time_vector=np.linspace(1,N_rows,N_rows)

		av_temps_df=temps.dropna(axis=1,how='all')
		print(av_temps_df)
# print(temps)
		max_temp=max(av_temps_df.max())
##+- 10%

		fig = figure()
		for i in range(12):
			y = temps[i]
			plot(time_vector[0:len(time_vector)-1],y[0:len(time_vector)-1],color=colors[i],marker=markers[i],markevery=50,ms=8,label=Exp_Names[i].replace('_',' '))
		plot(time_vector[0:len(time_vector)-1],av_temps_df[0:len(time_vector)-1].mean(axis=1),'k',label='Average',linewidth=3)
		# plt.fill_between(time_vector[0:len(time_vector)-1] ,temps[0:len(time_vector)-1].mean(axis=1)+2*temps[0:len(time_vector)-1].std(axis=1), temps[0:len(time_vector)-1].mean(axis=1)-2*temps[0:len(time_vector)-1].std(axis=1), facecolor='gray',alpha=0.5, interpolate=True,linewidth=3)
		# plt.fill_between(time_vector[0:len(time_vector)-1],(1-channels['Error'][chart])*av_temps_df[0:len(time_vector)-1].mean(axis=1), (1+channels['Error'][chart])*av_temps_df[0:len(time_vector)-1].mean(axis=1), facecolor='gray',alpha=0.5, interpolate=True,linewidth=3)
		ax1 = gca()
		xlabel('Time (s)', fontsize=16)
		ylabel(str(channels['Y Axis'][chart]), fontsize=16)
		xticks(fontsize=16)
		yticks(fontsize=16)

		axis([0, 1.1*N_rows, 0, 1.1*max_temp])
		box = ax1.get_position()
		ax1.set_position([box.x0, box.y0, box.width * 0.75, box.height])
		# ax1.set_xlim([0,1.1*N_rows])

		# ax1.set_ylim([0,1.1*max_temp])
		# legend(numpoints=1,loc=1,ncol=2,fontsize=8)	
		ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=8)
		grid(True)
		output_location=output_location_init+ '10percent_TC/'
		if not os.path.exists(output_location):
			os.makedirs(output_location)
		savefig(output_location+ chart + '.pdf',format='pdf')
		close()


		fig = figure()
		for i in range(12):
			y = temps[i]
			plot(time_vector[0:len(time_vector)-1],y[0:len(time_vector)-1],color=colors[i],marker=markers[i],markevery=50,ms=8,label=Exp_Names[i].replace('_',' '))
		plot(time_vector[0:len(time_vector)-1],av_temps_df[0:len(time_vector)-1].mean(axis=1),'k',label='Average',linewidth=3)
		# plt.fill_between(time_vector[0:len(time_vector)-1] ,temps[0:len(time_vector)-1].mean(axis=1)+2*temps[0:len(time_vector)-1].std(axis=1), temps[0:len(time_vector)-1].mean(axis=1)-2*temps[0:len(time_vector)-1].std(axis=1), facecolor='gray',alpha=0.5, interpolate=True,linewidth=3)
		# plt.fill_between(time_vector[0:len(time_vector)-1],(1-channels['Error'][chart])*av_temps_df[0:len(time_vector)-1].mean(axis=1), (1+channels['Error'][chart])*av_temps_df[0:len(time_vector)-1].mean(axis=1), facecolor='gray',alpha=0.5, interpolate=True,linewidth=3)
		ax1 = gca()
		xlabel('Time (s)', fontsize=16)
		ylabel(str(channels['Y Axis'][chart]), fontsize=16)
		xticks(fontsize=16)
		yticks(fontsize=16)

		axis([0, 0.5*N_rows, 0, 1.1*max_temp])
		box = ax1.get_position()
		ax1.set_position([box.x0, box.y0, box.width * 0.75, box.height])
		# ax1.set_xlim([0,1.1*N_rows])

		# ax1.set_ylim([0,1.1*max_temp])
		# legend(numpoints=1,loc=1,ncol=2,fontsize=8)	
		ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=8)
		grid(True)
		output_location=output_location_init+ 'special_shorter/'
		if not os.path.exists(output_location):
			os.makedirs(output_location)
		savefig(output_location+ chart + '_short.pdf',format='pdf')
		close()

		#average lines
		fig = figure()
		# for i in range(12):
		# 	y = temps[i]
		# 	plot(time_vector[0:len(time_vector)-1],y[0:len(time_vector)-1],color=colors[i],marker=markers[i],markevery=50,ms=8,label=Exp_Names[i].replace('_',' '))
		plot(time_vector[0:len(time_vector)-1],av_temps_df[0:len(time_vector)-1].mean(axis=1),'k',label='Average',linewidth=3)
		# plt.fill_between(time_vector[0:len(time_vector)-1] ,temps[0:len(time_vector)-1].mean(axis=1)+2*temps[0:len(time_vector)-1].std(axis=1), temps[0:len(time_vector)-1].mean(axis=1)-2*temps[0:len(time_vector)-1].std(axis=1), facecolor='gray',alpha=0.5, interpolate=True,linewidth=3)
		# plt.fill_between(time_vector[0:len(time_vector)-1],(1-channels['Error'][chart])*av_temps_df[0:len(time_vector)-1].mean(axis=1), (1+channels['Error'][chart])*av_temps_df[0:len(time_vector)-1].mean(axis=1), facecolor='gray',alpha=0.5, interpolate=True,linewidth=3)
		ax1 = gca()
		xlabel('Time (s)', fontsize=16)
		ylabel(str(channels['Y Axis'][chart]), fontsize=16)
		xticks(fontsize=16)
		yticks(fontsize=16)
		axis([0, 1.1*N_rows, 0, 1.1*max_temp])
		box = ax1.get_position()
		ax1.set_position([box.x0, box.y0, box.width * 0.75, box.height])
		# ax1.set_xlim([0,1.1*N_rows])

		# ax1.set_ylim([0,1.1*max_temp])
		ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=8)
		# legend(numpoints=1,loc=1,ncol=2,fontsize=8)	
		grid(True)
		output_location=output_location_init+ 'Average_Value/'
		if not os.path.exists(output_location):
			os.makedirs(output_location)
		savefig(output_location+ chart + '.pdf',format='pdf')
		close()

##PLOT ODDS (Right Side)
			# j=0
			# k=0
			# for column in temps:

			# 	if column%2==1:
			# 		temps_right[j]=temps[column]
			# 		j=j+1


				# 	if column%2==0:
				# 		temps_left[k]=temps[column]
				# 		k=k+1


				# 	# else:
				# 	# 	print('ERROR')


				# fig = figure()
				# for i in range(12):
				# 	if i%2==1:
				# 		y = temps[i]
				# 		plot(time_vector[0:len(time_vector)-1],y[0:len(time_vector)-1],color='red',marker=markers[i],markevery=50,ms=8,label=Exp_Names[i].replace('_',' '))
				# for i in range(12):
				# 	if i%2==0:
				# 		y = temps[i]
				# 		plot(time_vector[0:len(time_vector)-1],y[0:len(time_vector)-1],color='blue',marker=markers[i],markevery=50,ms=8,label=Exp_Names[i].replace('_',' '))
				# plot(time_vector[0:len(time_vector)-1],temps_left[0:len(time_vector)-1].mean(axis=1),'k',label='Left Side Average',linewidth=3)
				# plot(time_vector[0:len(time_vector)-1],temps_right[0:len(time_vector)-1].mean(axis=1),'k',label='Right Side Average',linewidth=3)	
				# # plt.fill_between(time_vector[0:len(time_vector)-1] ,temps[0:len(time_vector)-1].mean(axis=1)+2*temps[0:len(time_vector)-1].std(axis=1), temps[0:len(time_vector)-1].mean(axis=1)-2*temps[0:len(time_vector)-1].std(axis=1), facecolor='gray',alpha=0.5, interpolate=True,linewidth=3)
				# plt.fill_between(time_vector[0:len(time_vector)-1],.85*temps_left[0:len(time_vector)-1].mean(axis=1), 1.15*temps_left[0:len(time_vector)-1].mean(axis=1), facecolor='green',alpha=0.5, interpolate=True,linewidth=3)	
				# plt.fill_between(time_vector[0:len(time_vector)-1],.85*temps_right[0:len(time_vector)-1].mean(axis=1), 1.15*temps_right[0:len(time_vector)-1].mean(axis=1), facecolor='gray',alpha=0.5, interpolate=True,linewidth=3)
				# ax1 = gca()
				# xlabel('Time (s)', fontsize=20)
				# ylabel(str(channels['Y Axis'][chart]), fontsize=20)
				# xticks(fontsize=16)
				# yticks(fontsize=16)
				# legend(numpoints=1,loc=1,ncol=2,fontsize=16)
				# axis([0, 1.1*N_rows, 0, 1.1*max_temp])
				# box = ax1.get_position()
				# ax1.set_position([box.x0, box.y0, box.width * 0.75, box.height])
				# # ax1.set_xlim([0,1.1*N_rows])
				# # ax1.set_ylim([0,1.1*max_temp])
				# ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
				# grid(True)
				# output_location=output_location_init+ 'Side_Comparison/'
				# if not os.path.exists(output_location):
				# 	os.makedirs(output_location)
				# savefig(output_location+ chart + '.pdf',format='pdf')
				# close()
