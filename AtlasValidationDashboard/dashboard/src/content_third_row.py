##################
# Import modules #
##################
from dash import dcc
import dash_bootstrap_components as dbc


################################
# Create content for third row #
################################
content_third_row = dbc.Row(
    [
        dbc.Col(			
            dcc.Graph(id='graph_4'), md=4,
        ),
        
        dbc.Col(
            dcc.Graph(id='graph_5'), md=4
        ),
        
        dbc.Col(
            dcc.Graph(id='graph_6'), md=4
        )
        
    ]
)