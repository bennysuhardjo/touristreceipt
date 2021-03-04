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
from scipy.special import inv_boxcox
from sklearn.preprocessing import StandardScaler
from pickle import load
import numpy as np

# load the scaler
scaler = load(open('scalerUsed.pkl', 'rb'))


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
#	    dcc.Input(
#        	id='input-x',
#        	placeholder='Insert x value',
#        	type='number',
#        	value='',
#    	    ),	
#	    html.Label('Arrival Month: '), dcc.Input(id='arrival_month', value='January', type='text'),
#	    html.Label('City of Origin: '), dcc.Input(id='city_of_origin', value='Batam', type='text'),
#	    html.Label('Purpose of Visit: '), dcc.Input(id='purpose_of_visit', value='Leisure', type='text'),
#	    html.Label('Travel thru: '), dcc.Input(id='travel_thru', value='Terminal 1', type='text'),
#	    html.Div(id='result'),
	    html.Table([
		html.Tr([html.Td(['Arrival Month: ']), html.Td(dcc.Dropdown(
        							options=[
            								{'label': 'January', 'value': 'January'},
            								{'label': 'February', 'value': 'February'},
									{'label': 'March', 'value': 'March'},
									{'label': 'April', 'value': 'April'},
									{'label': 'May', 'value': 'May'},
									{'label': 'June', 'value': 'June'},
									{'label': 'July', 'value': 'July'},
									{'label': 'August', 'value': 'August'},
									{'label': 'September', 'value': 'September'},
									{'label': 'October', 'value': 'October'},
									{'label': 'November', 'value': 'November'},
            								{'label': 'December', 'value': 'December'}
        								],
        							value='August',
								id='arrival_month'
    		))]) ,
		html.Tr([html.Td(['City of Origin: ']), html.Td(dcc.Dropdown(
        							options=[
            								{'label': 'Jakarta', 'value': 'Jakarta'},
            								{'label': 'Batam', 'value': 'Batam'},
            								{'label': 'Jogjakarta', 'value': 'Jogjakarta'}
        								],
        							value='Jakarta',
								id='city_of_origin'
    		))]) ,
		html.Tr([html.Td(['Purpose of Visit: ']), html.Td(dcc.Dropdown(
        							options=[
            								{'label': 'Business', 'value': 'Business+Accompanying Pax'},
            								{'label': 'Education', 'value': 'Education+Accompanying Pax'},
									{'label': 'Leisure', 'value': 'Leisure'},
									{'label': 'Healthcare', 'value': 'Healthcare+Accompanying Pax'},
            								{'label': 'Others', 'value': 'Others/ Refused'}
        								],
        							value='Leisure',
								id='purpose_of_visit'
    		))]) ,
		html.Tr([html.Td(['Occupation: ']), html.Td(dcc.Dropdown(
        							options=[
            								{'label': 'Businessman', 'value': 'Businessman (small company, <50 people)'},
            								{'label': 'Manager', 'value': 'Mager (CEO, company director, senior mager)'},
									{'label': 'Student', 'value': 'Student'},
									{'label': 'Professional', 'value': 'Professiols (doctor, lawyer, lecturer, etc)'},
            								{'label': 'Homemaker', 'value': 'Homemaker (Full time)'}
        								],
        							value='Businessman (small company, <50 people)',
								id='occupation'
    		))]) ,
		html.Tr([html.Td(['Length of Stay (Days):']), html.Td(dcc.Input(id='length_of_stay', value='2', type='number'))]) ,
		html.Tr([html.Td(['1st Visit:']), html.Td(dcc.Dropdown(
        							options=[
            								{'label': 'First Visit', 'value': 'Yes'},
            								{'label': 'Repeat Visit', 'value': 'No'}
        								],
        							value='Yes',
								id='first_visit'
    		))]) ,
		html.Tr([html.Td(['Main Accommodation:']), html.Td(dcc.Dropdown(
        							options=[
            								{'label': 'Hotel', 'value': 'Hotel'},
            								{'label': 'Service Apartment', 'value': 'Service Apartment'},
            								{'label': 'Stayed with relatives/friends', 'value': 'Stayed with relatives/friends'}
        								],
        							value='Hotel',
								id='main_accommodation'
    		))]) ,    
		html.Tr([html.Td(['Travel Type:']), html.Td(dcc.Dropdown(
        							options=[
            								{'label': 'Packaged', 'value': 'Packaged'},
            								{'label': 'Non-Packaged', 'value': 'Non-Packaged'},
            								{'label': 'Business (Non-Packaged)', 'value': 'Business (Non-Packaged)'}
        								],
        							value='Packaged',
								id='travel_type'
    		))]) ,
		html.Tr([html.Td('    ')]) ,
                html.Tr([html.Td(id='result')])  
            ]),
       	    html.Label('This is a sample application that STB Marketing Team would use to develop targeted campaigns to boost tourism from Indonesia once the travelling restrictions are lifted or relaxed. This application will access a machine learning model trained using data from Kaggle (https://www.kaggle.com/shweta2407/singapore-tourism-data). The model is hosted on IBM Watson Machine Learning and accessed thru an API.')     
       ]),
       dcc.Tab(label='Malaysian Market', children=[
              ]),
	   dcc.Tab(label='Chinese Market', children=[
		
        ]),
       dcc.Tab(label='Indian Market', children=[
        ])
    ])

])

@app.callback(
    Output('result', 'children'),
    [Input('arrival_month', 'value'),
    Input('city_of_origin', 'value'),
    Input('purpose_of_visit', 'value'),

    Input('occupation', 'value'),
    Input('length_of_stay', 'value'),
    Input('first_visit', 'value'),
    Input('main_accommodation', 'value'), 
     
    Input('travel_type', 'value')]
)

def update_result(arrival_month,city_of_origin,purpose_of_visit,occupation,length_of_stay,first_visit,main_accommodation,travel_type):
    	# NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
	API_KEY = "KvRBi07e0ypCaGrSLk5H7X5dU7RY4l1SpkyUAaU_atPv"
	token_response = requests.post('https://iam.au-syd.bluemix.net/identity/token', data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
	mltoken = token_response.json()["access_token"]

	header 	= {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}
	
	if (arrival_month == "April"): 
		arrivalApril = 1
	else:
		arrivalApril = 0
	
	if (arrival_month == "August"):
		arrivalAugust = 1
	else: 
		arrivalAugust = 0
	
	if (arrival_month == "December"):
		arrivalDecember = 1
	else: 
		arrivalDecember = 0
		
	if (arrival_month == "February"):
		arrivalFebruary = 1
	else: 
		arrivalFebruary = 0

	if (arrival_month == "January"):
		arrivalJanuary = 1
	else: 
		arrivalJanuary = 0
		
	if (arrival_month == "July"):
		arrivalJuly = 1
	else: 
		arrivalJuly = 0
		
	if (arrival_month == "June"):
		arrivalJune = 1
	else: 
		arrivalJune = 0
		
	if (arrival_month == "March"):
		arrivalMarch = 1
	else: 
		arrivalMarch = 0
		
	if (arrival_month == "May"):
		arrivalMay = 1
	else: 
		arrivalMay = 0
		
	if (arrival_month == "November"):
		arrivalNovember = 1
	else: 
		arrivalNovember = 0
	
	if (arrival_month == "October"):
		arrivalOctober = 1
	else: 
		arrivalOctober = 0
	
	if (arrival_month == "September"):
		arrivalSeptember = 1
	else: 
		arrivalSeptember = 0
		
	if (city_of_origin == "Jakarta"): 
		cityJakarta = 1
	else:
		cityJakarta = 0	
		
	if (city_of_origin == "Batam"): 
		cityBatam = 1
	else:
		cityBatam = 0	
		
	if (city_of_origin == "Jogjakarta"): 
		cityJogjakarta = 1
	else:
		cityJogjakarta = 0	
		
	if (travel_type == "Business (Non-Packaged)"): 
		traveltypebusiness = 1
	else:
		traveltypebusiness = 0
		
	if (travel_type == "Non-Packaged"): 
		traveltypenonpackage = 1
	else:
		traveltypenonpackage = 0
		
	if (travel_type == "Packaged"): 
		traveltypepackage = 1
	else:
		traveltypepackage = 0
	
	if (first_visit == "Yes"): 
		firstv = 1
	else:
		firstv = 0
		
	if (first_visit == "No"): 
		repeatv = 1
	else:
		repeatv = 0
		
	if (main_accommodation == "Hotel"): 
		mainaccomhotel = 1
	else:
		mainaccomhotel = 0
		
	if (main_accommodation == "Service Apartment"): 
		mainaccomservapr = 1
	else:
		mainaccomservapr = 0
		
	if (main_accommodation == "Stayed with relatives/friends"): 
		mainaccomrelative = 1
	else:
		mainaccomrelative = 0	
	
	if (purpose_of_visit == "Business+Accompanying Pax"): 
		purposegrpbiz = 1
	else:
		purposegrpbiz = 0
		
	if (purpose_of_visit == "Education+Accompanying Pax"): 
		purposegrpedu = 1
	else:
		purposegrpedu = 0
		
	if (purpose_of_visit == "Healthcare+Accompanying Pax"): 
		purposegrpmed = 1
	else:
		purposegrpmed = 0		
		
	if (purpose_of_visit == "Leisure"): 
		purposegrplei = 1
	else:
		purposegrplei = 0	
		
	if (purpose_of_visit == "Others/ Refused"): 
		purposegrpoth = 1
	else:
		purposegrpoth = 0	
		
	if (occupation == "Businessman (small company, <50 people)"): 
		occupationbiz = 1
	else:
		occupationbiz = 0	
		
	if (occupation == "Mager (CEO, company director, senior mager)"): 
		occupationman = 1
	else:
		occupationman = 0	
		
	if (occupation == "Student"): 
		occupationstu = 1
	else:
		occupationstu = 0	
		
	if (occupation == "Professiols (doctor, lawyer, lecturer, etc)"): 
		occupationpro = 1
	else:
		occupationpro = 0	
		
	if (occupation == "Homemaker (Full time)"): 
		occupationhom = 1
	else:
		occupationhom = 0	
	
	new_cols = ['length_stay', 'TravelThruAir', 'TravelThruLand', 'TravelThruSea', 'R.mth_April', 'R.mth_August', 'R.mth_December', 'R.mth_February', 'R.mth_January', 'R.mth_July', 'R.mth_June', 'R.mth_March', 'R.mth_May', 'R.mth_November', 'R.mth_October', 'R.mth_September', 'City_residence_Aceh', 'City_residence_Bali', 'City_residence_Balikpapan', 'City_residence_Bandung', 'City_residence_Banjarmasin', 'City_residence_Banten', 'City_residence_Batam', 'City_residence_Bekasi', 'City_residence_Bengkulu', 'City_residence_Bintan', 'City_residence_Bogor', 'City_residence_Cirebon / Tjirebon', 'City_residence_Denpasar', 'City_residence_Dumai', 'City_residence_East Java', 'City_residence_Indonesia', 'City_residence_Jakarta', 'City_residence_Jambi / Telanaipura', 'City_residence_Java', 'City_residence_Java Timur', 'City_residence_Jawa Barat', 'City_residence_Jogjakarta', 'City_residence_Kalimantan', 'City_residence_Karimun', 'City_residence_Kupang', 'City_residence_Lampung', 'City_residence_Lingga Is.', 'City_residence_Lombok', 'City_residence_Magelang', 'City_residence_Makassar', 'City_residence_Malang', 'City_residence_Maluku', 'City_residence_Manado', 'City_residence_Mataram / Lombok Is.', 'City_residence_Medan', 'City_residence_Padang', 'City_residence_PalangKaraya', 'City_residence_Palembang', 'City_residence_Papua/Irian Jaya', 'City_residence_Pekan Baru', 'City_residence_Pontianak', 'City_residence_Riau', 'City_residence_Samarinda', 'City_residence_Selat Panjang', 'City_residence_Semarang', 'City_residence_Solo', 'City_residence_Sukabumi', 'City_residence_Sulawesi', 'City_residence_Sumatra', 'City_residence_Sumbawa Is.', 'City_residence_Surabaya', 'City_residence_Surakarta', 'City_residence_Tangerang', 'City_residence_Tanjung Balai', 'City_residence_Tanjung Pinang', 'City_residence_Temburong', 'City_residence_West Java', 'City_residence_Yogyakarta', 'Purpose_grp_Business+Accompanying Pax', 'Purpose_grp_Education+Accompanying Pax', 'Purpose_grp_Healthcare+Accompanying Pax', 'Purpose_grp_Leisure', 'Purpose_grp_Others/ Refused', 'Purpose_Accompaning an international student studying in Singapore', 'Purpose_Accompanying a Healthcare/medical visitor for Day surgery', 'Purpose_Accompanying a Healthcare/medical visitor for In-patient treatment', 'Purpose_Accompanying a Healthcare/medical visitor for Outpatient consultation/treat', 'Purpose_Accompanying a business visitor', 'Purpose_Company sponsored holiday', 'Purpose_Convention/conference', 'Purpose_Corporate/business meetings', 'Purpose_Cultural Festivals', 'Purpose_Day-surgery', 'Purpose_Executive training, including training workshops and seminar', 'Purpose_Exhibition/Trade show', 'Purpose_Family Entertainment', 'Purpose_Gathering informations on the Education services in Singapor', 'Purpose_General business purpose', 'Purpose_Holiday/ Rest & Relax', 'Purpose_IR (e.g. MBS, RWS)', 'Purpose_In-house company training', 'Purpose_In-patient treatment', 'Purpose_Music-related', 'Purpose_Others', 'Purpose_Others - Personal (e.g. weddings, funerals, etc)', 'Purpose_Others - Work Related (e.g. visa, insurance, etc)', 'Purpose_Outpatient consultation/treatment', 'Purpose_Performing Arts', 'Purpose_School trips', 'Purpose_Sightseeing/ Attractions', 'Purpose_Skills development/skills training/vocational training', 'Purpose_Sporting', 'Purpose_Stopover', 'Purpose_Student enrichment programmes', 'Purpose_Student events', 'Purpose_Study mission', 'Purpose_To experience different cultures', 'Purpose_To experience the food/food events in Singapore', 'Purpose_To shop/attend shopping events in Singapore', 'Purpose_To take or join a regional or international cruise', 'Purpose_Visiting an international student studying in Singapore', 'Purpose_Visiting friends/relatives', 'langint_Chinese', 'langint_English', 'langint_Hybrid Chinese', 'langint_Hybrid Indonesian', 'langint_Indonesian', 'langint_Japanese', 'langint_Malay', 'travel_type_Business (Non-Packaged)', 'travel_type_Non-Packaged', 'travel_type_Packaged', '1st_visit_No', '1st_visit_Yes', 'f1_gender_Female', 'f1_gender_Male', 'f3_occupation_Blue collar (technician, hairdresser, hawker, taxi drivers etc)', 'f3_occupation_Businessman (large company, > 250 people)', 'f3_occupation_Businessman (medium size company, 50 -250 people)', 'f3_occupation_Businessman (small company, <50 people)', 'f3_occupation_Executive (sales, administration)', 'f3_occupation_Homemaker (Full time)', 'f3_occupation_Mager (CEO, company director, senior mager)', 'f3_occupation_Other White collar (Teacher, Nurse, secretary, receptionist, cashier etc)', 'f3_occupation_Others (specify)', 'f3_occupation_Professiols (doctor, lawyer, lecturer, etc)', 'f3_occupation_Retired', 'f3_occupation_Student', 'f3_occupation_Unemployed', 'MainAccomm_Accommodation not required - Day Tripper', 'MainAccomm_Accommodation not required - On-board Cruise', 'MainAccomm_Accommodation not required - Others', 'MainAccomm_Homestay', 'MainAccomm_Hospital', 'MainAccomm_Hostel (Rental by bed)', 'MainAccomm_Hotel', 'MainAccomm_Other non-paid accommodations (e.g. religious places, camp,', 'MainAccomm_Other paid accommodations (e.g.chalets, country clubs, etc)', 'MainAccomm_Own Residence', 'MainAccomm_Service Apartment', 'MainAccomm_Stayed with relatives/ friends', 'MainAccomm_Student Hostel', 'travel_companion.1_Alone', 'travel_companion.1_Business associates/ Colleagues', 'travel_companion.1_Children aged 0-7 yrs', 'travel_companion.1_Children aged 13-19 yrs', 'travel_companion.1_Children aged 20-39 yrs', 'travel_companion.1_Children aged 40 yrs and above', 'travel_companion.1_Children aged 8-12 yrs', 'travel_companion.1_Friends', 'travel_companion.1_Grandparents/ Grandparents-in-law', 'travel_companion.1_Other relatives', 'travel_companion.1_Others', 'travel_companion.1_Parents/ Parents-in-law', 'travel_companion.1_Partner/ Boyfriend/ Girlfriend', 'travel_companion.1_Siblings', 'travel_companion.1_Spouse', 'Terminal_', 'Terminal_HCC', 'Terminal_MBCCS', 'Terminal_RFT', 'Terminal_TMFT', 'Terminal_Terminal 1', 'Terminal_Terminal 2', 'Terminal_Terminal 3', 'Terminal_Tuas', 'Terminal_Woodlands']
	df1 = pd.DataFrame.from_records([(length_of_stay,1.0,0.0,0.0,arrivalApril,arrivalAugust,arrivalDecember,arrivalFebruary,arrivalJanuary,arrivalJuly,arrivalJune,arrivalMarch,arrivalMay,arrivalNovember,arrivalOctober,arrivalSeptember,0,0,0,0,0,0,cityBatam,0,0,0,0,0,0,0,0,0,cityJakarta,0,0,0,0,cityJogjakarta,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,purposegrpbiz,purposegrpedu,purposegrpmed,purposegrplei,purposegrpoth,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,traveltypebusiness,traveltypenonpackage,traveltypepackage,repeatv,firstv,1,0,0,0,0,occupationbiz,0,occupationhom,occupationman,0,0,occupationpro,0,occupationstu,0,0,0,0,0,0,0,mainaccomhotel,0,0,0,mainaccomservapr,mainaccomrelative,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0)], columns=new_cols)
        
	
	df1.loc[:, ['length_stay']] = scaler.transform(df1.loc[:, ['length_stay']])   
	

	input_values = [1.0,0.0,0.0,arrivalApril,arrivalAugust,arrivalDecember,arrivalFebruary,arrivalJanuary,arrivalJuly,arrivalJune,arrivalMarch,arrivalMay,arrivalNovember,arrivalOctober,arrivalSeptember,0,0,0,0,0,0,cityBatam,0,0,0,0,0,0,0,0,0,cityJakarta,0,0,0,0,cityJogjakarta,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,purposegrpbiz,purposegrpedu,purposegrpmed,purposegrplei,purposegrpoth,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,traveltypebusiness,traveltypenonpackage,traveltypepackage,repeatv,firstv,1,0,0,0,0,occupationbiz,0,occupationhom,occupationman,0,0,occupationpro,0,occupationstu,0,0,0,0,0,0,0,mainaccomhotel,0,0,0,mainaccomservapr,mainaccomrelative,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0]
	input_values.insert(0, float(df1.iloc[:, 0][0]))
	
	# NOTE: manually define and pass the array(s) of values to be scored in the next line
	payload_scoring = {
    	"input_data": [{
      		"fields": ['length_stay', 'TravelThruAir', 'TravelThruLand', 'TravelThruSea', 'R.mth_April', 'R.mth_August', 'R.mth_December', 'R.mth_February', 'R.mth_January', 'R.mth_July', 'R.mth_June', 'R.mth_March', 'R.mth_May', 'R.mth_November', 'R.mth_October', 'R.mth_September', 'City_residence_Aceh', 'City_residence_Bali', 'City_residence_Balikpapan', 'City_residence_Bandung', 'City_residence_Banjarmasin', 'City_residence_Banten', 'City_residence_Batam', 'City_residence_Bekasi', 'City_residence_Bengkulu', 'City_residence_Bintan', 'City_residence_Bogor', 'City_residence_Cirebon / Tjirebon', 'City_residence_Denpasar', 'City_residence_Dumai', 'City_residence_East Java', 'City_residence_Indonesia', 'City_residence_Jakarta', 'City_residence_Jambi / Telanaipura', 'City_residence_Java', 'City_residence_Java Timur', 'City_residence_Jawa Barat', 'City_residence_Jogjakarta', 'City_residence_Kalimantan', 'City_residence_Karimun', 'City_residence_Kupang', 'City_residence_Lampung', 'City_residence_Lingga Is.', 'City_residence_Lombok', 'City_residence_Magelang', 'City_residence_Makassar', 'City_residence_Malang', 'City_residence_Maluku', 'City_residence_Manado', 'City_residence_Mataram / Lombok Is.', 'City_residence_Medan', 'City_residence_Padang', 'City_residence_PalangKaraya', 'City_residence_Palembang', 'City_residence_Papua/Irian Jaya', 'City_residence_Pekan Baru', 'City_residence_Pontianak', 'City_residence_Riau', 'City_residence_Samarinda', 'City_residence_Selat Panjang', 'City_residence_Semarang', 'City_residence_Solo', 'City_residence_Sukabumi', 'City_residence_Sulawesi', 'City_residence_Sumatra', 'City_residence_Sumbawa Is.', 'City_residence_Surabaya', 'City_residence_Surakarta', 'City_residence_Tangerang', 'City_residence_Tanjung Balai', 'City_residence_Tanjung Pinang', 'City_residence_Temburong', 'City_residence_West Java', 'City_residence_Yogyakarta', 'Purpose_grp_Business+Accompanying Pax', 'Purpose_grp_Education+Accompanying Pax', 'Purpose_grp_Healthcare+Accompanying Pax', 'Purpose_grp_Leisure', 'Purpose_grp_Others/ Refused', 'Purpose_Accompaning an international student studying in Singapore', 'Purpose_Accompanying a Healthcare/medical visitor for Day surgery', 'Purpose_Accompanying a Healthcare/medical visitor for In-patient treatment', 'Purpose_Accompanying a Healthcare/medical visitor for Outpatient consultation/treat', 'Purpose_Accompanying a business visitor', 'Purpose_Company sponsored holiday', 'Purpose_Convention/conference', 'Purpose_Corporate/business meetings', 'Purpose_Cultural Festivals', 'Purpose_Day-surgery', 'Purpose_Executive training, including training workshops and seminar', 'Purpose_Exhibition/Trade show', 'Purpose_Family Entertainment', 'Purpose_Gathering informations on the Education services in Singapor', 'Purpose_General business purpose', 'Purpose_Holiday/ Rest & Relax', 'Purpose_IR (e.g. MBS, RWS)', 'Purpose_In-house company training', 'Purpose_In-patient treatment', 'Purpose_Music-related', 'Purpose_Others', 'Purpose_Others - Personal (e.g. weddings, funerals, etc)', 'Purpose_Others - Work Related (e.g. visa, insurance, etc)', 'Purpose_Outpatient consultation/treatment', 'Purpose_Performing Arts', 'Purpose_School trips', 'Purpose_Sightseeing/ Attractions', 'Purpose_Skills development/skills training/vocational training', 'Purpose_Sporting', 'Purpose_Stopover', 'Purpose_Student enrichment programmes', 'Purpose_Student events', 'Purpose_Study mission', 'Purpose_To experience different cultures', 'Purpose_To experience the food/food events in Singapore', 'Purpose_To shop/attend shopping events in Singapore', 'Purpose_To take or join a regional or international cruise', 'Purpose_Visiting an international student studying in Singapore', 'Purpose_Visiting friends/relatives', 'langint_Chinese', 'langint_English', 'langint_Hybrid Chinese', 'langint_Hybrid Indonesian', 'langint_Indonesian', 'langint_Japanese', 'langint_Malay', 'travel_type_Business (Non-Packaged)', 'travel_type_Non-Packaged', 'travel_type_Packaged', '1st_visit_No', '1st_visit_Yes', 'f1_gender_Female', 'f1_gender_Male', 'f3_occupation_Blue collar (technician, hairdresser, hawker, taxi drivers etc)', 'f3_occupation_Businessman (large company, > 250 people)', 'f3_occupation_Businessman (medium size company, 50 -250 people)', 'f3_occupation_Businessman (small company, <50 people)', 'f3_occupation_Executive (sales, administration)', 'f3_occupation_Homemaker (Full time)', 'f3_occupation_Mager (CEO, company director, senior mager)', 'f3_occupation_Other White collar (Teacher, Nurse, secretary, receptionist, cashier etc)', 'f3_occupation_Others (specify)', 'f3_occupation_Professiols (doctor, lawyer, lecturer, etc)', 'f3_occupation_Retired', 'f3_occupation_Student', 'f3_occupation_Unemployed', 'MainAccomm_Accommodation not required - Day Tripper', 'MainAccomm_Accommodation not required - On-board Cruise', 'MainAccomm_Accommodation not required - Others', 'MainAccomm_Homestay', 'MainAccomm_Hospital', 'MainAccomm_Hostel (Rental by bed)', 'MainAccomm_Hotel', 'MainAccomm_Other non-paid accommodations (e.g. religious places, camp,', 'MainAccomm_Other paid accommodations (e.g.chalets, country clubs, etc)', 'MainAccomm_Own Residence', 'MainAccomm_Service Apartment', 'MainAccomm_Stayed with relatives/ friends', 'MainAccomm_Student Hostel', 'travel_companion.1_Alone', 'travel_companion.1_Business associates/ Colleagues', 'travel_companion.1_Children aged 0-7 yrs', 'travel_companion.1_Children aged 13-19 yrs', 'travel_companion.1_Children aged 20-39 yrs', 'travel_companion.1_Children aged 40 yrs and above', 'travel_companion.1_Children aged 8-12 yrs', 'travel_companion.1_Friends', 'travel_companion.1_Grandparents/ Grandparents-in-law', 'travel_companion.1_Other relatives', 'travel_companion.1_Others', 'travel_companion.1_Parents/ Parents-in-law', 'travel_companion.1_Partner/ Boyfriend/ Girlfriend', 'travel_companion.1_Siblings', 'travel_companion.1_Spouse', 'Terminal_', 'Terminal_HCC', 'Terminal_MBCCS', 'Terminal_RFT', 'Terminal_TMFT', 'Terminal_Terminal 1', 'Terminal_Terminal 2', 'Terminal_Terminal 3', 'Terminal_Tuas', 'Terminal_Woodlands'],
      		"values": [input_values]
	}]}

	response_scoring = requests.post('https://jp-tok.ml.cloud.ibm.com/ml/v4/deployments/d8c62c08-2f01-44c2-9f11-e76a750a1831/predictions?version=2021-02-16', json=payload_scoring, headers={'Authorization': 'Bearer ' + mltoken})
	#print("Scoring response")
	str1 = " " 
	str1.join(map(str, response_scoring.json()['predictions'][0]['values']))      
	
	prediction_output = response_scoring.json()
	json_data = []

	for i in prediction_output['predictions']: 
    		json_data.append( [i['values']])

	prediction_outputDF = pd.DataFrame.from_records( json_data )
	prediction_outputDF_mod = prediction_outputDF.rename(columns={0: "Val"})

	
	
	return "Tourist Receipt (Shopping) Prediction: $"+ str(round(np.expm1(prediction_outputDF_mod.iloc[0]['Val'][0][0]),0))
	 





if __name__ == '__main__':
    app.run_server()
