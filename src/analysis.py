import numpy as np
import os
import pandas as pd
import pdb

dataFile = '../data/COVID-19-master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
df = pd.read_csv(dataFile)

columns = df.columns

#sum cases in all counties per state
sum_states = df.groupby(df.columns[6]).sum() 
columns = list(sum_states)
#sum confirmed cases for each state
sum_cases_states = sum_states[columns[5:]].sum(axis=1)

#confirmed cases by state, descending order
print(sum_cases_states.sort_values(ascending=False))

