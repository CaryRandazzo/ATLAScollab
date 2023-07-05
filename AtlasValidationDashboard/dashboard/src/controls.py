##################
# Import modules #
##################
from dash import html, dcc
import dash_bootstrap_components as dbc


###############################
# Create controls for Sidebar #
###############################
controls = html.Div(
    [
        # html.Div(
        #     [
        #         dbc.Input(id="text_input1", value="data15_13TeV.00276689.physics_Main.merge.HIST.f1051_h335._0001.1", type="text"),#, placeholder='' ),
        #     ]
        # ),
        # html.Div(
        #     [
        #         dbc.Input(id="text_input2", value="data15_13TeV.00276689.physics_Main.merge.HIST.f1052_h335._0001", type="text")#, placeholder='' ),
        #     ]
        # ),
        # html.Br(),
        
        # html.P('Dropdown', style={
        #     'textAlign': 'center'
        # }),
        dcc.Upload(
            id='upload-data-1', max_size = -1, children=html.Div([
                'Drag and Drop or ', html.A('Select Files'), 
                html.Div(id='upload-status-1')
            ]),
            style = {
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple = False
        ),
        dcc.Upload(
            id='upload-data-2',max_size = -1, children=html.Div([
                'Drag and Drop or ', html.A('Select Files'),
                html.Div(id='upload-status-2')
            ]),
            style = {
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple = False
        ),
        html.Div(id='tmp'),
        html.Div(id='output-data-upload'),
        html.Button('Submit', id='submit-button', type='submit', n_clicks=0),
        html.P('NOTE: Submit when both uploaded.'),

        # dcc.Dropdown(
        #     id='dropdown',
        #     options=[{
        #         'label': 'Value One',
        #         'value': 'value1'
        #     }, {
        #         'label': 'Value Two',
        #         'value': 'value2'
        #     },
        #         {
        #             'label': 'Value Three',
        #             'value': 'value3'
        #         }
        #     ],
        #     value=['value1'],  # default value
        #     multi=True
        # ),
        # html.Br(),
        # html.P('Range Slider', style={
        #     'textAlign': 'center'
        # }),
        # dcc.RangeSlider(
        #     id='range_slider',
        #     min=0,
        #     max=20,
        #     step=0.5,
        #     value=[5, 15]
        # ),
        # html.P('Check Box', style={
        #     'textAlign': 'center'
        # }),
        # dbc.Card([dbc.Checklist(
        #     id='check_list',
        #     options=[{
        #         'label': 'Value One',
        #         'value': 'value1'
        #     },
        #         {
        #             'label': 'Value Two',
        #             'value': 'value2'
        #         },
        #         {
        #             'label': 'Value Three',
        #             'value': 'value3'
        #         }
        #     ],
        #     value=['value1', 'value2'],
        #     inline=True
        # )]),
        # html.Br(),
        # html.P('Radio Items', style={
            # 'textAlign': 'center'
        # }),
        # dbc.Card([dbc.RadioItems(
        #     id='radio_items',
        #     options=[{
        #         'label': 'Value One',
        #         'value': 'value1'
        #     },
        #         {
        #             'label': 'Value Two',
        #             'value': 'value2'
        #         },
        #         {
        #             'label': 'Value Three',
        #             'value': 'value3'
        #         }
        #     ],
        #     value='value1',
        #     style={
        #         'margin': 'auto'
        #     }
        # )]),
        # html.Br(),
        # dbc.Button(
        #     id='submit_button',
        #     n_clicks=0,
        #     children='Submit',
        #     color='primary'
        # ),
    ]
)