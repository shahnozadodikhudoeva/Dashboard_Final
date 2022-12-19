# Importing libariries
import os
import pandas as pd
import sqlite3
from dash import Dash, html, dcc, Input, Output, get_asset_url
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.graph_objs import *
import numpy as np
from bs4 import BeautifulSoup
import requests



#Exercise 1
H=sqlite3.connect("hr.db")
df=pd.read_sql_query("select * from employees",H)


#Exercise 2
tables_connect=pd.read_sql("select first_name, job_title"+" from employees E"+" inner join jobs J"+" on E.job_id=J.job_id", H)
jobs_total=tables_connect.groupby('job_title').count().reset_index()
jobs_total.columns=['job_title','count']

job_options = jobs_total["job_title"].unique().tolist()


#Exercise 3

jobs=pd.read_sql_query("select * from jobs;",H)
jobs = jobs.iloc[1: , :]
jobs["difference"]=jobs['max_salary']-jobs['min_salary']
job=jobs[['job_title','difference']]
max_salary=job['difference'].max()

# Ex 4
employee_salary = pd.read_sql("select salary " +"from employees",H)
avg_salary = employee_salary['salary'].mean()
data_mean= ['Average', avg_salary, avg_salary,avg_salary] 


# https://www.pluralsight.com/guides/extracting-data-html-beautifulsoup
def scrape():
    URL = "https://www.itjobswatch.co.uk/jobs/uk/sqlite.do"
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html5lib') 
    table = soup.find('table', attrs = {'class':'summary'}) 
    table.find('form').decompose()
    table_data = table.tbody.find_all("tr")
    table = []
    for i in table_data:
        row = []
        r2= i.find_all("td")
        if len(r2) == 0:
            r2 = i.find_all("th")
        for j in r2:
            row.append(j.text)
        table.append(row)
    hd = table[1]
    hd[0] = "index"
    df = pd.DataFrame(table)
    df.drop(index=[0,1,2,3,4,5,6,7,10,11,14,15],axis=0,inplace=True)
    df.columns = hd
    df.set_index("index",inplace=True)
    df.reset_index(inplace=True)
    df['Same period 2021'] = df['Same period 2021'].str.replace('£','')
    df['Same period 2021'] = df['Same period 2021'].str.replace(',','')
    df['Same period 2021'] = df['Same period 2021'].str.replace('-','0').astype(float)
    df['6 months to19 Dec 2022'] = df['6 months to19 Dec 2022'].str.replace('£','')
    df['6 months to19 Dec 2022'] = df['6 months to19 Dec 2022'].str.replace(',','').astype(float)
    df['Same period 2020'] = df['Same period 2020'].str.replace('£','')
    df['Same period 2020'] = df['Same period 2020'].str.replace(',','').astype(float)
    df.loc[4] =data_mean
    return df

data = scrape()
axis = data["index"]
data.drop("index",inplace=True,axis=1)
years4 = data.columns

# App
app = dash.Dash(__name__)
server = app.server

# Main layout
app.layout = html.Div(style={"text-align":"center"},
    children=[ html.Div([
        html.H1("Final Examination",),
        html.H2("HR database"),
        html.H3("Q1. Producing a Diagram"),
        html.H4("The diagram was saved as a png file and has been submitted to moodle with its python file.",style={'color':'red'}),
        html.H3("Q2. Number of employees with the same job"),
        dcc.Dropdown(options=job_options,
         multi=True,
        id="input2", 
        value="None"),
        dcc.Graph(id="output2"),


# Third
# https://dash.plotly.com/dash-core-components
        html.H3("Q3.Difference between maximum nad minimum job salaries"),
        dcc.RangeSlider(0, max_salary, 1200, value=[0, max_salary],
            id="input3" ),
        dcc.Graph(id="output3") ,
        
        html.H3("Q4.Percentiles of Salaries in UK and the mean of the company"),
        dcc.Dropdown(years4,
                    placeholder="6 months to19 Dec 2022",
                    id="input4"
                             ),
        dcc.Graph(id="output4"),
    ])  
    ])

@app.callback(
    Output('output2', 'figure'),
    Input('input2', 'value')
)
def update_output(value):
    figure = go.Figure(layout_yaxis_range=[0,30])
    all=jobs_total[jobs_total['job_title'].isin(value)]    

    if value == "all" or value == None:
        x = all["Accountant"]
    figure["layout"]["xaxis"]["title"] = "Job"
    figure["layout"]["yaxis"]["title"] = "Number of employees"
    figure.add_trace(trace=go.Bar(
                x=all['job_title'],
                y=all['count'],
                name="All",
            ))
    figure.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                  marker_line_width=1.5, opacity=0.6)
    return figure


@app.callback(
    Output('output3', 'figure'),
    Input('input3', 'value')
)
def update_output(value):
    minimum=value[0]
    maximum=value[-1]
    fig = job[job["difference"]>=minimum][job["difference"]<=maximum]
    fig3 = go.Figure(go.Bar(x=fig['difference'], y=fig['job_title'],
                      name='Job differences', orientation='h' ))
    fig3["layout"]["xaxis"]["title"] = "Job"
    fig3["layout"]["yaxis"]["title"] = "Difference between max and min"

    fig3.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                  marker_line_width=1.5, opacity=0.6)
    return fig3


@app.callback(
    Output('output4', 'figure'),
    Input('input4', 'value')
    )
def update_output(value):
    
    fig4 = go.Figure()
    # https://plotly.com/python/line-and-scatter/
    y =data[value]
    fig4.add_trace(go.Scatter(x=axis.values,y=y.values,  mode='markers',
        marker_size=16,
        marker_symbol='circle',
        showlegend = False,
        marker_color = ['black','black','black','black','green'],
    ))
    return fig4

if __name__ == "__main__":
    app.run_server(debug=True)
