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
		html.Tr([html.Td(['Arrival Month: ']), html.Td(dcc.Input(id='arrival_month', value='January', type='text'))]) ,
		html.Tr([html.Td(['City of Origin: ']), html.Td(dcc.Input(id='city_of_origin', value='Batam', type='text'))]) ,
		html.Tr([html.Td(['Purpose of Visit: ']), html.Td(dcc.Input(id='purpose_of_visit', value='Leisure', type='text'))]) ,
		html.Tr([html.Td(['Travel thru: ']), html.Td(dcc.Input(id='travel_thru', value='TMFT', type='text'))]) ,
		html.Tr([html.Td(['Length of Stay (Days):']), html.Td(dcc.Input(id='length_of_stay', value='2', type='number'))]) ,
		html.Tr([html.Td(['Travel Type:']), html.Td(dcc.Input(id='travel_type', value='Packaged', type='text'))]) ,
		html.Tr([html.Td(' ')]) ,
                html.Tr([html.Td(id='result')]) 
            ])
            
       ]),
       dcc.Tab(label='Malaysian Market', children=[
              ]),
	   dcc.Tab(label='China Market', children=[
		
        ]),
       dcc.Tab(label='India Market', children=[
        ])
    ])

])

@app.callback(
    Output('result', 'children'),
    [Input('arrival_month', 'value'),
    Input('city_of_origin', 'value'),
    Input('purpose_of_visit', 'value'),
    Input('travel_thru', 'value'),
    Input('length_of_stay', 'value'),
    Input('travel_type', 'value')]
)

def update_result(arrival_month,city_of_origin,purpose_of_visit,travel_thru,length_of_stay,travel_type):
    	# NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
	API_KEY = "KvRBi07e0ypCaGrSLk5H7X5dU7RY4l1SpkyUAaU_atPv"
	token_response = requests.post('https://iam.au-syd.bluemix.net/identity/token', data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
	mltoken = token_response.json()["access_token"]

	header 	= {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}
	
#	input_values = []
#	input_values += [length_of_stay]
#	listrest = list([0.748654,-0.203255,-0.683875,-0.295267,-0.317254,3.249265,-0.288455,-0.303911,-0.300307,-0.301141,-0.316448,-0.300028,-0.296392,-0.307214,-0.282692,-0.033567,-0.146826,-0.041123,-0.259359,-0.029066,-0.011862,-0.52787,-0.031397,-0.020548,-0.054435,-0.05941,-0.023729,-0.037535,-0.020548,-0.044424,-0.039369,1.142605,-0.047498,-0.05941,-0.020548,-0.011862,-0.011862,-0.065104,-0.020548,-0.020548,-0.033567,-0.011862,-0.041123,-0.026532,-0.062887,-0.050386,-0.016777,-0.033567,-0.011862,-0.183686,-0.058206,-0.016777,-0.080708,-0.011862,-0.020548,-0.060591,-0.041123,-0.056976,-0.023729,-0.023729,-0.098281,-0.080708,-0.011862,-0.026532,-0.042805,-0.011862,-0.302251,-0.026532,-0.044424,-0.104649,-0.154159,-0.011862,-0.033567,-0.175335,-0.400375,-0.152235,2.609787,-1.329629,-0.279487,-0.016777,-0.044424,-0.048963,-0.220651,-0.039369,-0.077097,-0.054435,-0.205868,-0.029066,-0.044424,-0.062887,-0.054435,-0.020548,-0.041123,-0.303082,-0.762669,-0.069328,-0.054435,-0.042805,-0.050386,-0.066184,-0.271507,-0.06175,3.552022,-0.026532,-0.05572,-0.142261,-0.087494,-0.074277,-0.120059,-0.041123,-0.026532,-0.048963,-0.016777,-0.016777,-0.011862,-0.208085,-0.070345,-0.092266,-0.437285,-0.324191,0.478221,-0.096811,-0.011862,-0.193682,-0.044424,-0.016777,-0.212463,-0.39777,0.513682,-0.278902,0.414926,-0.414926,-0.929859,0.929859,-0.194463,-0.075228,-0.147823,2.514018,-0.305841,-0.407913,-0.371249,-0.306665,-0.256256,-0.396107,-0.198709,-0.357625,-0.12767,-0.493925,-0.084167,-0.05941,-0.078015,-0.020548,-0.232659,1.033481,-0.056976,-0.065104,-0.101866,-0.168835,-0.503603,-0.020548,-0.691198,-0.236332,-0.101159,-0.100447,-0.096068,-0.044424,-0.067248,-0.354364,-0.047498,-0.141746,-0.149307,-0.353106,-0.134337,-0.188141,1.644388,-0.029066,-0.094565,-0.053119,-0.61986,-0.174052,-0.832336,-0.174052,1.986559,-0.200614,-0.031397])
#	input_values.append(listrest)

	new_cols = ["length_stay","TravelThruAir","TravelThruLand","TravelThruSea","R.mth_April","R.mth_August","R.mth_December","R.mth_February","R.mth_January","R.mth_July","R.mth_June","R.mth_March","R.mth_May","R.mth_November","R.mth_October","R.mth_September","City_residence_Aceh","City_residence_Bali","City_residence_Balikpapan","City_residence_Bandung","City_residence_Banjarmasin","City_residence_Banten","City_residence_Batam","City_residence_Bekasi","City_residence_Bengkulu","City_residence_Bintan","City_residence_Bogor","City_residence_Cirebon / Tjirebon","City_residence_Denpasar","City_residence_Dumai","City_residence_East Java","City_residence_Indonesia","City_residence_Jakarta","City_residence_Jambi / Telanaipura","City_residence_Java","City_residence_Java Timur","City_residence_Jawa Barat","City_residence_Jogjakarta","City_residence_Kalimantan","City_residence_Karimun","City_residence_Kupang","City_residence_Lampung","City_residence_Lingga Is.","City_residence_Lombok","City_residence_Magelang","City_residence_Makassar","City_residence_Malang","City_residence_Maluku","City_residence_Manado","City_residence_Mataram / Lombok Is.","City_residence_Medan","City_residence_Padang","City_residence_PalangKaraya","City_residence_Palembang","City_residence_Pangkal Pinang","City_residence_Papua/Irian Jaya","City_residence_Pekan Baru","City_residence_Pontianak","City_residence_Riau","City_residence_Samarinda","City_residence_Selat Panjang","City_residence_Semarang","City_residence_Solo","City_residence_Sukabumi","City_residence_Sulawesi","City_residence_Sumatra","City_residence_Sumbawa Is.","City_residence_Surabaya","City_residence_Surakarta","City_residence_Tangerang","City_residence_Tanjung Balai","City_residence_Tanjung Pinang","City_residence_Temburong","City_residence_West Java","City_residence_Yogyakarta","Purpose_grp_Business+Accompanying Pax","Purpose_grp_Education+Accompanying Pax","Purpose_grp_Healthcare+Accompanying Pax","Purpose_grp_Leisure","Purpose_grp_Others/ Refused","Purpose_Accompaning an international student studying in Singapore","Purpose_Accompanying a Healthcare/medical visitor for Day surgery","Purpose_Accompanying a Healthcare/medical visitor for In-patient treatment","Purpose_Accompanying a Healthcare/medical visitor for Outpatient consultation/treat","Purpose_Accompanying a business visitor","Purpose_Company sponsored holiday","Purpose_Convention/conference","Purpose_Corporate/business meetings","Purpose_Cultural Festivals","Purpose_Day-surgery","Purpose_Executive training, including training workshops and seminar","Purpose_Exhibition/Trade show","Purpose_Family Entertainment","Purpose_Gathering informations on the Education services in Singapor","Purpose_General business purpose","Purpose_Holiday/ Rest & Relax","Purpose_IR (e.g. MBS, RWS)","Purpose_In-house company training","Purpose_In-patient treatment","Purpose_Music-related","Purpose_Others","Purpose_Others - Personal (e.g. weddings, funerals, etc)","Purpose_Others - Work Related (e.g. visa, insurance, etc)","Purpose_Outpatient consultation/treatment","Purpose_Performing Arts","Purpose_School trips","Purpose_Sightseeing/ Attractions","Purpose_Skills development/skills training/vocational training","Purpose_Sporting","Purpose_Stopover","Purpose_Student enrichment programmes","Purpose_Student events","Purpose_Study mission","Purpose_To experience different cultures","Purpose_To experience the food/food events in Singapore","Purpose_To experience the nightlife in Singapore","Purpose_To shop/attend shopping events in Singapore","Purpose_To take or join a regional or international cruise","Purpose_Visiting an international student studying in Singapore","Purpose_Visiting friends/relatives","langint_Chinese","langint_English","langint_Hybrid Chinese","langint_Hybrid French","langint_Hybrid Indonesian","langint_Indonesian","langint_Japanese","langint_Malay","travel_type_Business (Non-Packaged)","travel_type_Non-Packaged","travel_type_Packaged","1st_visit_No","1st_visit_Yes","f1_gender_Female","f1_gender_Male","f3_occupation_Blue collar (technician, hairdresser, hawker, taxi drivers etc)","f3_occupation_Businessman (large company, > 250 people)","f3_occupation_Businessman (medium size company, 50 -250 people)","f3_occupation_Businessman (small company, <50 people)","f3_occupation_Executive (sales, administration)","f3_occupation_Homemaker (Full time)","f3_occupation_Mager (CEO, company director, senior mager)","f3_occupation_Other White collar (Teacher, Nurse, secretary, receptionist, cashier etc)","f3_occupation_Others (specify)","f3_occupation_Professiols (doctor, lawyer, lecturer, etc)","f3_occupation_Retired","f3_occupation_Student","f3_occupation_Unemployed","MainAccomm_Accommodation not required - Day Tripper","MainAccomm_Accommodation not required - On-board Cruise","MainAccomm_Accommodation not required - Others","MainAccomm_Homestay","MainAccomm_Hospital","MainAccomm_Hostel (Rental by bed)","MainAccomm_Hotel","MainAccomm_Other non-paid accommodations (e.g. religious places, camp,","MainAccomm_Other paid accommodations (e.g.chalets, country clubs, etc)","MainAccomm_Own Residence","MainAccomm_Service Apartment","MainAccomm_Stayed with relatives/ friends","MainAccomm_Student Hostel","travel_companion.1_Alone","travel_companion.1_Business associates/ Colleagues","travel_companion.1_Children aged 0-7 yrs","travel_companion.1_Children aged 13-19 yrs","travel_companion.1_Children aged 20-39 yrs","travel_companion.1_Children aged 40 yrs and above","travel_companion.1_Children aged 8-12 yrs","travel_companion.1_Friends","travel_companion.1_Grandparents/ Grandparents-in-law","travel_companion.1_Other relatives","travel_companion.1_Others","travel_companion.1_Parents/ Parents-in-law","travel_companion.1_Partner/ Boyfriend/ Girlfriend","travel_companion.1_Siblings","travel_companion.1_Spouse","Terminal_","Terminal_HCC","Terminal_MBCCS","Terminal_RFT","Terminal_TMFT","Terminal_Terminal 1","Terminal_Terminal 2","Terminal_Terminal 3","Terminal_Tuas","Terminal_Woodlands"]
	df1 = pd.DataFrame.from_records([(2,0.748654,-0.203255,-0.683875,-0.295267,-0.317254,3.249265,-0.288455,-0.303911,-0.300307,-0.301141,-0.316448,-0.300028,-0.296392,-0.307214,-0.282692,-0.033567,-0.146826,-0.041123,-0.259359,-0.029066,-0.011862,-0.52787,-0.031397,-0.020548,-0.054435,-0.05941,-0.023729,-0.037535,-0.020548,-0.044424,-0.039369,1.142605,-0.047498,-0.05941,-0.020548,-0.011862,-0.011862,-0.065104,-0.020548,-0.020548,-0.033567,-0.011862,-0.041123,-0.026532,-0.062887,-0.050386,-0.016777,-0.033567,-0.011862,-0.183686,-0.058206,-0.016777,-0.080708,-0.011862,-0.020548,-0.060591,-0.041123,-0.056976,-0.023729,-0.023729,-0.098281,-0.080708,-0.011862,-0.026532,-0.042805,-0.011862,-0.302251,-0.026532,-0.044424,-0.104649,-0.154159,-0.011862,-0.033567,-0.175335,-0.400375,-0.152235,2.609787,-1.329629,-0.279487,-0.016777,-0.044424,-0.048963,-0.220651,-0.039369,-0.077097,-0.054435,-0.205868,-0.029066,-0.044424,-0.062887,-0.054435,-0.020548,-0.041123,-0.303082,-0.762669,-0.069328,-0.054435,-0.042805,-0.050386,-0.066184,-0.271507,-0.06175,3.552022,-0.026532,-0.05572,-0.142261,-0.087494,-0.074277,-0.120059,-0.041123,-0.026532,-0.048963,-0.016777,-0.016777,-0.011862,-0.208085,-0.070345,-0.092266,-0.437285,-0.324191,0.478221,-0.096811,-0.011862,-0.193682,-0.044424,-0.016777,-0.212463,-0.39777,0.513682,-0.278902,0.414926,-0.414926,-0.929859,0.929859,-0.194463,-0.075228,-0.147823,2.514018,-0.305841,-0.407913,-0.371249,-0.306665,-0.256256,-0.396107,-0.198709,-0.357625,-0.12767,-0.493925,-0.084167,-0.05941,-0.078015,-0.020548,-0.232659,1.033481,-0.056976,-0.065104,-0.101866,-0.168835,-0.503603,-0.020548,-0.691198,-0.236332,-0.101159,-0.100447,-0.096068,-0.044424,-0.067248,-0.354364,-0.047498,-0.141746,-0.149307,-0.353106,-0.134337,-0.188141,1.644388,-0.029066,-0.094565,-0.053119,-0.61986,-0.174052,-0.832336,-0.174052,1.986559,-0.200614,-0.031397)], columns=new_cols)
        df1normalised = scaler.transform(df1)    



	input_values = [0.748654,-0.203255,-0.683875,-0.295267,-0.317254,3.249265,-0.288455,-0.303911,-0.300307,-0.301141,-0.316448,-0.300028,-0.296392,-0.307214,-0.282692,-0.033567,-0.146826,-0.041123,-0.259359,-0.029066,-0.011862,-0.52787,-0.031397,-0.020548,-0.054435,-0.05941,-0.023729,-0.037535,-0.020548,-0.044424,-0.039369,1.142605,-0.047498,-0.05941,-0.020548,-0.011862,-0.011862,-0.065104,-0.020548,-0.020548,-0.033567,-0.011862,-0.041123,-0.026532,-0.062887,-0.050386,-0.016777,-0.033567,-0.011862,-0.183686,-0.058206,-0.016777,-0.080708,-0.011862,-0.020548,-0.060591,-0.041123,-0.056976,-0.023729,-0.023729,-0.098281,-0.080708,-0.011862,-0.026532,-0.042805,-0.011862,-0.302251,-0.026532,-0.044424,-0.104649,-0.154159,-0.011862,-0.033567,-0.175335,-0.400375,-0.152235,2.609787,-1.329629,-0.279487,-0.016777,-0.044424,-0.048963,-0.220651,-0.039369,-0.077097,-0.054435,-0.205868,-0.029066,-0.044424,-0.062887,-0.054435,-0.020548,-0.041123,-0.303082,-0.762669,-0.069328,-0.054435,-0.042805,-0.050386,-0.066184,-0.271507,-0.06175,3.552022,-0.026532,-0.05572,-0.142261,-0.087494,-0.074277,-0.120059,-0.041123,-0.026532,-0.048963,-0.016777,-0.016777,-0.011862,-0.208085,-0.070345,-0.092266,-0.437285,-0.324191,0.478221,-0.096811,-0.011862,-0.193682,-0.044424,-0.016777,-0.212463,-0.39777,0.513682,-0.278902,0.414926,-0.414926,-0.929859,0.929859,-0.194463,-0.075228,-0.147823,2.514018,-0.305841,-0.407913,-0.371249,-0.306665,-0.256256,-0.396107,-0.198709,-0.357625,-0.12767,-0.493925,-0.084167,-0.05941,-0.078015,-0.020548,-0.232659,1.033481,-0.056976,-0.065104,-0.101866,-0.168835,-0.503603,-0.020548,-0.691198,-0.236332,-0.101159,-0.100447,-0.096068,-0.044424,-0.067248,-0.354364,-0.047498,-0.141746,-0.149307,-0.353106,-0.134337,-0.188141,1.644388,-0.029066,-0.094565,-0.053119,-0.61986,-0.174052,-0.832336,-0.174052,1.986559,-0.200614,-0.031397]
	input_values.insert(0, df1normalised[0][0])
	
	# NOTE: manually define and pass the array(s) of values to be scored in the next line
	payload_scoring = {
    	"input_data": [{
      		"fields": ["length_stay","TravelThruAir","TravelThruLand","TravelThruSea","R.mth_April","R.mth_August","R.mth_December","R.mth_February","R.mth_January","R.mth_July","R.mth_June","R.mth_March","R.mth_May","R.mth_November","R.mth_October","R.mth_September","City_residence_Aceh","City_residence_Bali","City_residence_Balikpapan","City_residence_Bandung","City_residence_Banjarmasin","City_residence_Banten","City_residence_Batam","City_residence_Bekasi","City_residence_Bengkulu","City_residence_Bintan","City_residence_Bogor","City_residence_Cirebon / Tjirebon","City_residence_Denpasar","City_residence_Dumai","City_residence_East Java","City_residence_Indonesia","City_residence_Jakarta","City_residence_Jambi / Telanaipura","City_residence_Java","City_residence_Java Timur","City_residence_Jawa Barat","City_residence_Jogjakarta","City_residence_Kalimantan","City_residence_Karimun","City_residence_Kupang","City_residence_Lampung","City_residence_Lingga Is.","City_residence_Lombok","City_residence_Magelang","City_residence_Makassar","City_residence_Malang","City_residence_Maluku","City_residence_Manado","City_residence_Mataram / Lombok Is.","City_residence_Medan","City_residence_Padang","City_residence_PalangKaraya","City_residence_Palembang","City_residence_Pangkal Pinang","City_residence_Papua/Irian Jaya","City_residence_Pekan Baru","City_residence_Pontianak","City_residence_Riau","City_residence_Samarinda","City_residence_Selat Panjang","City_residence_Semarang","City_residence_Solo","City_residence_Sukabumi","City_residence_Sulawesi","City_residence_Sumatra","City_residence_Sumbawa Is.","City_residence_Surabaya","City_residence_Surakarta","City_residence_Tangerang","City_residence_Tanjung Balai","City_residence_Tanjung Pinang","City_residence_Temburong","City_residence_West Java","City_residence_Yogyakarta","Purpose_grp_Business+Accompanying Pax","Purpose_grp_Education+Accompanying Pax","Purpose_grp_Healthcare+Accompanying Pax","Purpose_grp_Leisure","Purpose_grp_Others/ Refused","Purpose_Accompaning an international student studying in Singapore","Purpose_Accompanying a Healthcare/medical visitor for Day surgery","Purpose_Accompanying a Healthcare/medical visitor for In-patient treatment","Purpose_Accompanying a Healthcare/medical visitor for Outpatient consultation/treat","Purpose_Accompanying a business visitor","Purpose_Company sponsored holiday","Purpose_Convention/conference","Purpose_Corporate/business meetings","Purpose_Cultural Festivals","Purpose_Day-surgery","Purpose_Executive training, including training workshops and seminar","Purpose_Exhibition/Trade show","Purpose_Family Entertainment","Purpose_Gathering informations on the Education services in Singapor","Purpose_General business purpose","Purpose_Holiday/ Rest & Relax","Purpose_IR (e.g. MBS, RWS)","Purpose_In-house company training","Purpose_In-patient treatment","Purpose_Music-related","Purpose_Others","Purpose_Others - Personal (e.g. weddings, funerals, etc)","Purpose_Others - Work Related (e.g. visa, insurance, etc)","Purpose_Outpatient consultation/treatment","Purpose_Performing Arts","Purpose_School trips","Purpose_Sightseeing/ Attractions","Purpose_Skills development/skills training/vocational training","Purpose_Sporting","Purpose_Stopover","Purpose_Student enrichment programmes","Purpose_Student events","Purpose_Study mission","Purpose_To experience different cultures","Purpose_To experience the food/food events in Singapore","Purpose_To experience the nightlife in Singapore","Purpose_To shop/attend shopping events in Singapore","Purpose_To take or join a regional or international cruise","Purpose_Visiting an international student studying in Singapore","Purpose_Visiting friends/relatives","langint_Chinese","langint_English","langint_Hybrid Chinese","langint_Hybrid French","langint_Hybrid Indonesian","langint_Indonesian","langint_Japanese","langint_Malay","travel_type_Business (Non-Packaged)","travel_type_Non-Packaged","travel_type_Packaged","1st_visit_No","1st_visit_Yes","f1_gender_Female","f1_gender_Male","f3_occupation_Blue collar (technician, hairdresser, hawker, taxi drivers etc)","f3_occupation_Businessman (large company, > 250 people)","f3_occupation_Businessman (medium size company, 50 -250 people)","f3_occupation_Businessman (small company, <50 people)","f3_occupation_Executive (sales, administration)","f3_occupation_Homemaker (Full time)","f3_occupation_Mager (CEO, company director, senior mager)","f3_occupation_Other White collar (Teacher, Nurse, secretary, receptionist, cashier etc)","f3_occupation_Others (specify)","f3_occupation_Professiols (doctor, lawyer, lecturer, etc)","f3_occupation_Retired","f3_occupation_Student","f3_occupation_Unemployed","MainAccomm_Accommodation not required - Day Tripper","MainAccomm_Accommodation not required - On-board Cruise","MainAccomm_Accommodation not required - Others","MainAccomm_Homestay","MainAccomm_Hospital","MainAccomm_Hostel (Rental by bed)","MainAccomm_Hotel","MainAccomm_Other non-paid accommodations (e.g. religious places, camp,","MainAccomm_Other paid accommodations (e.g.chalets, country clubs, etc)","MainAccomm_Own Residence","MainAccomm_Service Apartment","MainAccomm_Stayed with relatives/ friends","MainAccomm_Student Hostel","travel_companion.1_Alone","travel_companion.1_Business associates/ Colleagues","travel_companion.1_Children aged 0-7 yrs","travel_companion.1_Children aged 13-19 yrs","travel_companion.1_Children aged 20-39 yrs","travel_companion.1_Children aged 40 yrs and above","travel_companion.1_Children aged 8-12 yrs","travel_companion.1_Friends","travel_companion.1_Grandparents/ Grandparents-in-law","travel_companion.1_Other relatives","travel_companion.1_Others","travel_companion.1_Parents/ Parents-in-law","travel_companion.1_Partner/ Boyfriend/ Girlfriend","travel_companion.1_Siblings","travel_companion.1_Spouse","Terminal_","Terminal_HCC","Terminal_MBCCS","Terminal_RFT","Terminal_TMFT","Terminal_Terminal 1","Terminal_Terminal 2","Terminal_Terminal 3","Terminal_Tuas","Terminal_Woodlands"],
      		"values": [input_values]
	}]}

	response_scoring = requests.post('https://jp-tok.ml.cloud.ibm.com/ml/v4/deployments/796d6827-8ef1-4ea9-a30b-ce162e70dc66/predictions?version=2021-02-07', json=payload_scoring, headers={'Authorization': 'Bearer ' + mltoken})
	#print("Scoring response")
	str1 = " " 
	str1.join(map(str, response_scoring.json()['predictions'][0]['values']))      
	
	prediction_output = response_scoring.json()
	json_data = []

	for i in prediction_output['predictions']: 
    		json_data.append( [i['values']])

	prediction_outputDF = pd.DataFrame.from_records( json_data )
	prediction_outputDF_mod = prediction_outputDF.rename(columns={0: "Val"})

	
	
	return "Tourist Receipt (Shopping) Prediction: $"+ str(round(inv_boxcox(prediction_outputDF_mod.iloc[0]['Val'][0][0],-0.7881123572908839),0))
	 





if __name__ == '__main__':
    app.run_server()
