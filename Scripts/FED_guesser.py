import pandas as pd 
import os as os
import numpy as np 
from pylab import * 
from datetime import datetime, timedelta
import shutil
from itertools import cycle
import matplotlib.pyplot as plt
import pickle

CO = 8500
O2 = 19
CO2 = 1.0

time_period = 50
fed_last=0
for i in range(time_period):
	fed_i=(1/60)*((1/(exp(8.13-0.54*(20.9-O2))))+(exp(CO2/5.0))*(CO/35000.0))+fed_last
	fed_last=fed_i
print(fed_i)


	# 	for t in O2_data:
	# 		O2_FED.append((1.0/60.0)*1/(exp(8.13-0.54*(20.9-t))))
	# 	for t in CO2_data:
	# 		CO2_FED.append(exp(t/5.0))
	# 	for t in CO_data:
	# 		CO_FED.append((1.0/60.0)*(t/35000.0))

