#!/usr/bin/env python
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from flask import Flask, abort, request
from uuid import uuid4
import requests
import requests.auth
import urllib
CLIENT_ID = 'c205ebf1-c7d7-4bf5-bc18-1af048aafa8f'
CLIENT_SECRET = '7c41e408-104e-49af-ba26-5ab71d95bb20'
REDIRECT_URI = "https://bankapitest.herokuapp.com/"


#def user_agent():
#    '''reddit API clients should each have their own, unique user-agent
#    Ideally, with contact info included.
#    
#    e.g.,
#    return "oauth2-sample-app by /u/%s" % your_reddit_username
#    '''
#    raise NotImplementedError()

#def base_headers():
#    return {"User-Agent": user_agent()}


#app = Flask(__name__)

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

def make_authorization_url():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    #state = str(uuid4())
    #save_created_state(state)
    params = {"client_id": CLIENT_ID,
              "response_type": "code",
              "state": "0399",
              "scope": "Read"}
    url = "https://www.dbs.com/sandbox/api/sg/v1/oauth/authorize?" + urllib.parse.urlencode(params) + '&redirect_uri=https://bankapitest.herokuapp.com/'
    return url

#make_authorization_url()

########### Set up the layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),    
    
    html.A("Open Banking (DBS)", href=make_authorization_url(), target="_blank"),
#    html.Table([
#                html.Tr([html.Td(['']), html.Td(id='news1')])
#        
#
#            ])
    
    html.Div(id='page-content')
])


#@app.route('/')
#def homepage():
#    text = '<a href="%s">Authenticate with DBS</a>'
#    return text % make_authorization_url()





# Left as an exercise to the reader.
# You may want to store valid states in a database or memcache.
#def save_created_state(state):
#    pass
#def is_valid_state(state):
#    return True

@app.callback(
               dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'search')]
)
def display_page(pathname):
    
    vars = pathname.split('&')[0].split('=')
    
    url = "https://www.dbs.com/sandbox/api/sg/v1/oauth/tokens"

    payload = "code="+ vars[1] +"&redirect_uri=https://bankapitest.herokuapp.com/&grant_type=token"

    headers = {
        'authorization': "Basic YzIwNWViZjEtYzdkNy00YmY1LWJjMTgtMWFmMDQ4YWFmYThmOjdjNDFlNDA4LTEwNGUtNDlhZi1iYTI2LTVhYjcxZDk1YmIyMA==",
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    
    urlcredit = "https://www.dbs.com/sandbox/api/sg/v1/parties/" + response.text.split(',')[1].split(':')[1].split('"')[1] + "/cards"

    payloadcredit = "cursor=1&amount=0"

    headerscredit = {
        'clientId': "c205ebf1-c7d7-4bf5-bc18-1af048aafa8f",
        'accessToken': response.text.split(',')[0].split(':')[1].split('"')[1],
        'uuid': "IW036"
        
    }

#    responsecredit = requests.request("GET", urlcredit,  data=payloadcredit, headers=headerscredit)
    responsecredit = requests.get(urlcredit, 
#                                  params={'cursor': '1', 'amount': 0},
                                  headers={'clientId': 'c205ebf1-c7d7-4bf5-bc18-1af048aafa8f',
                                           'accessToken': response.text.split(',')[0].split(':')[1].split('"')[1]
                                           ,
                                           'uuid': '123e4567-e89b-12d3-a456-426614174000'
                                          })
    
    return html.Div([
        html.H3('Authorisation Code: {}'.format(vars[1])),
        html.H3('Token: {}'.format(response.text)),
        html.H3('Access Token: {}'.format(response.text.split(',')[0].split(':')[1].split('"')[1])),
        html.H3('Party ID: {}'.format(response.text.split(',')[1].split(':')[1].split('"')[1])),
        html.H3('URL Credit: {}'.format(urlcredit)),
        html.H3('Credit Card Summary: {}'.format(responsecredit.text))
        
    ])

#def update_output_div():
#    error = request.args.get('error', '')
#    if error:
#        return "Error: " + error
#    state = request.args.get('state', '')
#    if not is_valid_state(state):
        # Uh-oh, this request wasn't started by us!
#        abort(403)
#    code = request.args.get('code')
#    access_token = get_token(code)
    # Note: In most cases, you'll want to store the access token, in, say,
    # a session for use in other parts of your web app.
#    return "Your reddit username is: " 

#def get_token(code):
#    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
#    post_data = {"grant_type": "authorization_code",
#                 "code": code,
#                 "redirect_uri": REDIRECT_URI}
#    headers = base_headers()
#    response = requests.post("https://www.dbs.com/sandbox/api/sg/v1/oauth/tokens",
#                             auth=client_auth,
#                             headers=headers,
#                             data=post_data)
#    token_json = response.json()
#    return token_json["access_token"]

#update_output_div()


#def get_username(access_token):
#    headers = base_headers()
#    headers.update({"Authorization": "bearer " + access_token})
#    response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
#    me_json = response.json()
#    return me_json['name']


if __name__ == '__main__':
    app.run_server()
