import numpy as np
import os
import pandas as pd
import pdb
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

'''
Calculate the daily counts of confirmed cases or deaths (instead of cumulative counts).
'''
def calc_diffDf(df):
    diff = np.diff(df.to_numpy()[:,1:], axis=0) 
    diffDf = pd.DataFrame(diff)
    diffDf.columns = df.columns.values[1:]
    diffDf = pd.concat([diffDf.reset_index(drop=True), df[['date']].iloc[1:,:].reset_index(drop=True)],axis=1, \
                        ignore_index=True, keys=diffDf.columns + ['date'])
    diffDf.columns = np.append(df.columns.values[1:], 'date')
    temp = diffDf.iloc[:,:-1].astype(int)
    temp['date'] = diffDf.iloc[:,-1]
    return temp

#US
def analyze_US():
    #datasets
    dfCases = pd.read_csv('data/US/time_series_covid19_confirmed_US.csv')
    dfDeaths = pd.read_csv('data/US/time_series_covid19_deaths_US.csv')
    dfStates = pd.read_csv('data/US/states.csv')
    dfVac = pd.read_csv('data/US/time_series_covid19_vaccine_doses_admin_US.csv')[:-5] #only include 50 states

    #Total Vaccine Rollout
    dfVac_T = dfVac.T
    dfVac_T.columns = dfVac.iloc[:,6]
    dfVac_T = dfVac_T.reset_index()
    dfVac_T = (dfVac_T.iloc[12:]).reset_index(drop=True)
    dfVac_T.rename(columns={'index':'date'}, inplace=True)
    dfVac_T = dfVac_T.fillna(0)
    dfVac_T['allStates_V'] = dfVac_T[dfVac_T.columns[1:]].sum(axis=1)
    dfVac_ = dfVac_T.iloc[:,1:].astype(int)
    dfVac_['date'] = dfVac_T.iloc[:,0]

    #aggregated confirmed cases - sum up cases in all counties per state
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
    diffDf = calc_diffDf(dfCases_T)
    fig1 = px.line(diffDf, x='date', y=diffDf.columns)
    fig1.write_html("output/us_cases.html")
    #Plot Vaccine Rollout and Daily Cases
    allStates = pd.concat([diffDf['allStates'].reset_index(drop=True), \
                            dfVac_[['allStates_V','date']][39:].reset_index(drop=True)], \
                            axis=1, ignore_index=True, keys=['cases', 'vaccines', 'date'], join='outer')
    allStates.columns = ['cases', 'vaccines', 'date']
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    fig2.add_trace(
        go.Bar(x=allStates['date'], y=allStates['cases'], name="Cases"),
        secondary_y = False,
    )
    fig2.add_trace(
        go.Scatter(x=allStates['date'], y=allStates['vaccines'], name="Vaccines"),
        secondary_y=True,
    )
    fig2.update_layout(
        title_text="Confirmed Cases and Vaccine Rollout"
    )
    fig2.update_xaxes(title_text="<b>Date</b>")# Set x-axis title
    fig2.update_yaxes(title_text="<b>Confirmed Daily Cases</b>", secondary_y=False) # Set y-axes titles
    fig2.update_yaxes(title_text="<b>Administered No. of Vaccines</b>", secondary_y=True)
    fig2.write_html("output/us_VacAndCases.html")

    #aggregated confirmed death cases - sum up cases in all counties per state
    sum = dfDeaths.groupby(dfDeaths.columns[6]).sum().reset_index()
    dfDeaths_T = sum.T
    dfDeaths_T.columns = dfDeaths_T.iloc[0,:]
    dfDeaths_T = dfDeaths_T.reset_index()
    dfDeaths_T.rename(columns={'index':'date'}, inplace=True)
    dfDeaths_T = dfDeaths_T.iloc[7:]
    dfDeaths_T['allStates'] = dfDeaths_T[dfDeaths_T.columns[1:]].sum(axis=1).astype(int)
    dfDeaths_ = dfDeaths_T.iloc[:,1:].astype(int)
    dfDeaths_['date'] = dfDeaths_T.iloc[:,0]

    #daily confirmed cases
    diffDf = calc_diffDf(dfDeaths_T)
    fig3 = px.line(diffDf, x='date', y=diffDf.columns)
    fig3.write_html("output/us_deaths.html")
    
    #Plot Vaccine Rollout and Death Cases
    allStates = pd.concat([diffDf['allStates'].reset_index(drop=True), \
                            dfVac_[['allStates_V','date']][39:].reset_index(drop=True)], \
                            axis=1, ignore_index=True, keys=['cases', 'vaccines', 'date'], join='outer')
    allStates.columns = ['cases', 'vaccines', 'date']
    fig4 = make_subplots(specs=[[{"secondary_y": True}]])
    fig4.add_trace(
        go.Bar(x=allStates['date'], y=allStates['cases'], name="Cases"),
        secondary_y = False,
    )
    fig4.add_trace(
        go.Scatter(x=allStates['date'], y=allStates['vaccines'], name="Vaccines"),
        secondary_y=True,
    )
    fig4.update_layout(
        title_text="Confirmed Deaths and Vaccine Rollout"
    )
    fig4.update_xaxes(title_text="<b>Date</b>")# Set x-axis title
    fig4.update_yaxes(title_text="<b>Confirmed Daily Counts of Deaths</b>", secondary_y=False) # Set y-axes titles
    fig4.update_yaxes(title_text="<b>Administered No. of Vaccines</b>", secondary_y=True)
    fig4.write_html("output/us_VacAndDeaths.html")
   

#Global
def analyze_Global():
    #datasets
    df_c = pd.read_csv('data/Global/continents.csv') #countryFile
    df_d = pd.read_csv('data/Global/time_series_covid19_deaths_global.csv') #deathsFile
    df_p = pd.read_csv('data/Global/population_by_country_2020.csv') #populationFile
    df_v = pd.read_csv('data/Global/time_series_covid19_vaccine_doses_admin_global.csv') #vaccinesFile 
    
    #Calculate death rate for each country, May'21-Oct.'21
    #combine no. cases for all regions within each country
    timeFrame_d = df_d.groupby(df_d.columns[1]).sum().reset_index()
    #timeFrame_v = df_v.groupby(df_v.columns[7]).sum().reset_index()
    timeFrame_v = df_v.groupby(df_v.columns[7]).first().reset_index()

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

    fig1.write_html("output/global_VacAndDeaths.html")

if __name__ == '__main__':
    analyze_US()
    analyze_Global()