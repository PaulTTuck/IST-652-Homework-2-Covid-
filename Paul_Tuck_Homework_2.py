# Paul Tuck
# Homework 2
# 11/29/2021

# Needed libraries------------------------------------------------------------

import pymongo
from pymongo import MongoClient
import json
import urllib.request
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import csv

# Gathering data--------------------------------------------------------------

# Setting up the database

client = MongoClient('localhost', 27017)

db = client.covid
covid = db.covid

# Retrieving the json data

OH_url = 'https://api.covidtracking.com/v1/states/oh/daily.json'
NY_url = 'https://api.covidtracking.com/v1/states/ny/daily.json'
CA_url = 'https://api.covidtracking.com/v1/states/ca/daily.json'
TX_url = 'https://api.covidtracking.com/v1/states/tx/daily.json'

urllist = [OH_url, NY_url, CA_url, TX_url]

# Adding the json data to the database

for url in urllist:
    request = urllib.request.urlopen(url)
    json_string = request.read().decode('utf-8')
    covid_json = json.loads(json_string)
    covid.insert_many(covid_json)

covid19 = covid.find()

# Creating pandas dataframe---------------------------------------------------

# Creating lists for the dataframe

date = []
state = []
positive = []
increase = []
hospital = []

for r in covid19:
    date.append(r['date'])
    state.append(r['state'])
    positive.append(r['positive'])
    increase.append(r['positiveIncrease'])
    hospital.append(r['hospitalizedCurrently'])

covid.drop()

# Converting the date list to datetime

date = pd.to_datetime(date, format = '%Y%m%d')

# Creating the dataframe

df_list = [date, state, positive, increase, hospital]
covid_data = pd.DataFrame(df_list)

# Switching the rows and columns

covid_data = covid_data.transpose()

# Adding the column names

covid_data.columns = ['Date', 'State', 'Positive_cases', 'Positive_increase', 'Hospital']

# Null values-----------------------------------------------------------------

# Searching for nulls

print(covid_data.info())

# 1 null in positive_cases and mostly null in hospitalizations

Null_pos = covid_data.loc[(covid_data.Positive_cases.isnull())]
print(Null_pos)

# Nulls are likely the result of no cases

covid_data = covid_data.fillna(0)
print(covid_data.info())

# Hospitalizations per new cases

covid_data['Hospital_per_positive'] = covid_data['Hospital']/covid_data['Positive_increase']
print(covid_data.info())

# Null values likely due to div by 0

covid_data = covid_data.fillna(0)
print(covid_data.info())

# Exporting the dataframe to an Excel file

newfile = './Covid_Data.csv'
covid_data.to_csv(path_or_buf = newfile)

# Graphing the data-----------------------------------------------------------

# Separating the states

OH = covid_data.loc[(covid_data['State'] == 'OH')]
NY = covid_data.loc[(covid_data['State'] == 'NY')]
TX = covid_data.loc[(covid_data['State'] == 'TX')]
CA = covid_data.loc[(covid_data['State'] == 'CA')]

# Graphing the state cases

plt.plot(OH.Date, OH.Positive_cases, label = 'Ohio')
plt.plot(NY.Date, NY.Positive_cases, label = 'New York')
plt.plot(TX.Date, TX.Positive_cases, label = 'Texas')
plt.plot(CA.Date, CA.Positive_cases, label = 'California')

plt.xlabel('Date')
plt.ylabel('Positive Cases (Cumulative)')
plt.title('Number of Positive Cases\nBy State')
plt.legend()
plt.show()

# Graphing Hospitalizations

plt.plot(OH.Date, OH.Hospital, label = 'Ohio')
plt.plot(NY.Date, NY.Hospital, label = 'New York')
plt.plot(TX.Date, TX.Hospital, label = 'Texas')
plt.plot(CA.Date, CA.Hospital, label = 'California')

plt.xlabel('Date')
plt.ylabel('Hospitalizations (by date)')
plt.title('Number of Hospitalizations\nBy State')
plt.legend()
plt.show()

# Graphing Hospitalizations per positive case

plt.plot(OH.Date, OH.Hospital_per_positive, label = 'Ohio')
plt.plot(NY.Date, NY.Hospital_per_positive, label = 'New York')
plt.plot(TX.Date, TX.Hospital_per_positive, label = 'Texas')
plt.plot(CA.Date, CA.Hospital_per_positive, label = 'California')

plt.xlabel('Date')
plt.ylabel('Hospitalizations\nper New Positive')
plt.title('Number of Hospitalizations\nper New Positive Cases')
plt.legend()
plt.show()