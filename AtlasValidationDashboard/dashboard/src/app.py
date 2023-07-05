###########################################################################
#Author: Cary Randazzo, Louisiana Tech University                                                                                                   
#Date: 11-13-2020                                                                                                                                   
###########################################################################


##########################
# Import modules for app #
##########################
import os
import time
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


###############################
# Import python files for app #
###############################
from styles import *
from controls import *
from content_first_row import *
from content_second_row import *
from content_third_row import *
from content_fourth_row import *


########################################
# Create the Parameters Area (sidebar) #
########################################

sidebar = html.Div(
    [
        html.H2('Parameters', style=TEXT_STYLE), #see styles.py
        html.Hr(),
        controls # see controls.py
    ],
    style=SIDEBAR_STYLE, #see styles.py
)


################################
# Create the main content area #
################################
content = html.Div( children=
    [
        html.H2('Atlas Validation Dashboard', style=TEXT_STYLE),
        html.Hr(),
        content_first_row, #see content_first_row.py
        dcc.Tabs(id='tabs-example', value='tab-1', children=[
            dcc.Tab(label='Distributions', value='tab-1', children=[
                content_second_row,]),
            dcc.Tab(label='Chi2/NDF vs Hists', value='tab-2', children=[
                content_third_row]),
        ]),

        #content_second_row, #see content_second_row.py
        #content_third_row, #see content_third_row.py
        content_fourth_row, #see content_fourth_row.py
        # Hidden div inside the app that stores the intermediate value
        html.Div(id='transfer_val1', style={'display': 'none'}),
        html.Div(id='transfer_val2', style={'display': 'none'}),
        html.Div(id='transfer_val_df', style={'display': 'none'})
    ],
    style=CONTENT_STYLE
)


##########################
# App and Layout Handles #
##########################
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([sidebar, content]) #see sidebar.py  #BOTH
#app.layout = html.Div([content]) #see sidebar.py   #JUST CONTENT


######################################
# Import callbacks from callbacks.py #
######################################
# from file_callbacks import *

@app.callback(
    Output('output-data-upload','children'),
    Input('submit-button', 'n_clicks'),
    State('upload-data-1', 'contents'),
    State('upload-data-2', 'contents'),
    State('upload-data-1', 'last_modified'),
    State('upload-data-2', 'last_modified'),
    State('upload-data-1','filename'),
    State('upload-data-2','filename'),
    )

def parse_dropdowns(n_clicks, contents1, contents2, last_modified1, last_modified2, filename1, filename2):

    if n_clicks == 0:
        return ''

    if not filename1 or not filename2:
        try:
            print(filename1)
        except:
            print(filename2)
        return 'Please upload two ROOT TFile files.'

    print('FILENAME1:',filename1)
    print('FILENAME2:',filename2)
    try:
        os.remove('/app/data/fileOne.txt')
    except:
        with open ('/app/data/fileOne.txt','a+') as f:
            f.write(filename1) 
    try:
        os.remove('/app/data/fileTwo.txt')
    except:
        with open ('/app/data/fileTwo.txt','a+') as f:
            f.write(filename2)

    # children = [
        # zip(n_clicks, filename1, filename2)
    # ]

    # n_clicks = 0

    return html.P(filename1),'\n',html.P(filename2),'\nUpload Successful.'
        # html.Div([
        # html.H6(filename1, filename2),
        # html.P('Last modified: ' + str(last_modified1)) + '\n',
        # html.P('Last modified: ' + str(last_modified2)),
        # html.P('File successfully uploaded!')
    # ]) # children

@app.callback(
    Output('upload-data-1', 'children'),
    Input('upload-data-1', 'contents')
)
def update_status1(contents):

    if contents is None:
        return "Drag/Drop or Select File1"
    else:
        return html.Div([
        html.P('File1 Uploaded')
        ])

@app.callback(
    Output('upload-data-2', 'children'),
    Input('upload-data-2', 'contents')
)
def update_status2(contents):

    if contents is None:
        return "Drag/Drop or Select File2"
    else:
        return html.Div([
        html.P('File2 Uploaded')
        ])

from callbacks import *

# @app.callback(
#     Output('submit-button', 'n_clicks'),
#     Input('url', 'pathname'),
# )
# def refresh_page(pathname):
#     return time.time()




######################
# Run the app server #
######################
server = app.server
if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port='1337')
