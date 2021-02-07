import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import requests
import plotly.express as px
from dash.dependencies import Input, Output, State
import time
import dash_table
import zipfile, urllib.request, shutil
import dash_bootstrap_components as dbc
import os
import psycopg2

########### Define your variables
mytitle='Tourist Receipt Prediction'
tabtitle='Tourist Receipt Prediction'
myheading='Tourist Receipt Prediction'

########### Initiate the app
external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

########### Set up the layout
app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Indonesian Market', children=[
            

            html.Label('Please enter the tourist profile: '),
            
       ]),
       dcc.Tab(label='Malaysian Market', children=[
              ]),
	   dcc.Tab(label='China Market', children=[
		
        ]),
       dcc.Tab(label='India Market', children=[
        ])
    ])

])

if __name__ == '__main__':
    app.run_server()
