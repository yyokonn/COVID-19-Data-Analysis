import numpy as np
import os
import pandas as pd
import pdb
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
'''
#datasets
df_d = pd.read_csv('../data/time_series_covid19_deaths_global.csv') #deathsFile
df_v = pd.read_csv('../data/time_series_covid19_vaccine_doses_admin_global.csv') #vaccinesFile 
df_p = pd.read_csv('../data/population_by_country_2020.csv') #populationFile
df_c = pd.read_csv('../data/continents.csv') #countryFile

#Calculate death rate for each country, May'21-Oct.'21
#combine no. cases for all regions within each country
timeFrame_d = df_d.groupby(df_d.columns[1]).sum().reset_index()
timeFrame_v = df_v.groupby(df_v.columns[7]).sum().reset_index()

start = timeFrame_d.columns.get_loc('4/1/21')
end = timeFrame_d.columns.get_loc('10/31/21')
timeFrame_d['totalDeaths'] = timeFrame_d.iloc[:, start:end+1].sum(axis=1)
timeFrame_d = timeFrame_d.merge(df_p[['Country (or dependency)','Population (2020)']], left_on='Country/Region', right_on='Country (or dependency)')
timeFrame_d.rename(columns={'Population (2020)':'Population'}, inplace=True)
timeFrame_d['DeathRate'] = timeFrame_d['totalDeaths'] / timeFrame_d['Population']

#Calculate vaccine rate for each country, May'21-Oct.'21
timeFrame_v.drop(columns=['Population'], inplace=True)
timeFrame_v = timeFrame_v.merge(df_p[['Country (or dependency)','Population (2020)']], left_on='Country_Region', right_on='Country (or dependency)')
timeFrame_v.rename(columns={'Population (2020)':'Population', 'Country_Region':'Country/Region'}, inplace=True)
timeFrame_v['VaccineRate'] = timeFrame_v['2021-10-31'] / timeFrame_v['Population']

mergeDf = timeFrame_d[['Country/Region','DeathRate']].merge(timeFrame_v[['Country/Region','VaccineRate', 'Population']], left_on='Country/Region', right_on='Country/Region')
mergeDf['ratioRates'] = (mergeDf['DeathRate'] / mergeDf['VaccineRate'])*1000000
mergeDf = mergeDf.merge(df_c[['name','region']], left_on='Country/Region', right_on='name')
mergeDf.drop(columns=['name'], inplace=True)
mergeDf['scaled_Population'] = np.log10(mergeDf['Population'])

fig1 = px.scatter(mergeDf, x="DeathRate", y="VaccineRate", color="region",\
                 size="scaled_Population", \
                 hover_data=['region', 'Country/Region'], log_x=True)

fig1.write_html("../output/plot1.html")
fig1.write_image("../output/fig1.png")
'''
#Cases vs. Vaccine Distribution
dfCases = pd.read_csv('../data/COVID-19-master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv')
dfVac = pd.read_csv('../data/time_series_covid19_vaccine_doses_admin_US.csv')[:-5] #only include 50 states
dfStates = pd.read_csv('../data/states.csv')

#aggregated confirmed cases - sum cases in all counties per state
sum_states = dfCases.groupby(dfCases.columns[6]).sum().reset_index()
dfCases_T = sum_states.T
dfCases_T.columns = dfCases_T.iloc[0,:]
dfCases_T = dfCases_T.reset_index()
dfCases_T.rename(columns={'index':'date'}, inplace=True)
dfCases_T = dfCases_T.iloc[6:]
dfCases_T['allStates'] = dfCases_T[dfCases_T.columns[1:]].sum(axis=1).astype(int)
dfCases_ = dfCases_T.iloc[:,1:].astype(int)
dfCases_['date'] = dfCases_T.iloc[:,0]

#daily confirmed cases
diff = np.diff(dfCases_T.to_numpy()[:,1:], axis=0) 
diffDf = pd.DataFrame(diff)
diffDf.columns = dfCases_T.columns.values[1:]
diffDf = pd.concat([diffDf.reset_index(drop=True), dfCases_T[['date']].iloc[1:,:].reset_index(drop=True)],axis=1, ignore_index=True, keys=diffDf.columns + ['date'])
diffDf.columns = np.append(dfCases_T.columns.values[1:], 'date')
temp = diffDf.iloc[:,:-1].astype(int)
temp['date'] = diffDf.iloc[:,-1]
diffDf = temp
fig2 = px.line(diffDf, x='date', y=diffDf.columns)
fig2.show()

dfVac_T = dfVac.T
dfVac_T.columns = dfVac.iloc[:,6]
dfVac_T = dfVac_T.reset_index()
dfVac_T = (dfVac_T.iloc[12:]).reset_index(drop=True)
dfVac_T.rename(columns={'index':'date'}, inplace=True)
dfVac_T = dfVac_T.fillna(0)
dfVac_T['allStates_V'] = dfVac_T[dfVac_T.columns[1:]].sum(axis=1)
dfVac_ = dfVac_T.iloc[:,1:].astype(int)
dfVac_['date'] = dfVac_T.iloc[:,0]

pdb.set_trace()
allStates = pd.concat([diffDf['allStates'].reset_index(drop=True), \
                        dfVac_[['allStates_V','date']][39:].reset_index(drop=True)], \
                        axis=1, ignore_index=True, keys=['cases', 'vaccines', 'date'], join='outer')

allStates.columns = ['cases', 'vaccines', 'date']
fig3 = make_subplots(specs=[[{"secondary_y": True}]])
fig3.add_trace(
    go.Bar(x=allStates['date'], y=allStates['cases'], name="Cases"),
    secondary_y = False,
)

fig3.add_trace(
    go.Scatter(x=allStates['date'], y=allStates['vaccines'], name="Vaccines"),
    secondary_y=True,
)

fig3.update_layout(
    title_text="Confirmed Cases and Vaccine Rollout"
)

# Set x-axis title
fig3.update_xaxes(title_text="date")
# Set y-axes titles
fig3.update_yaxes(title_text="<b>Confirmed Daily Cases</b>", secondary_y=False)
fig3.update_yaxes(title_text="<b>Administered Number of Vaccines</b>", secondary_y=True)

fig3.show()

#confirmed Deaths vs. Vaccines


