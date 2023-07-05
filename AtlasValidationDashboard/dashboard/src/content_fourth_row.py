##################
# Import modules #
##################
import dash_bootstrap_components as dbc


#################################
# Create content for fourth row #
#################################
content_fourth_row = dbc.Row(
    [
        dbc.Col(
            #dcc.Graph(id='graph_5'), md=6
        ),
        dbc.Col(
            #dcc.Graph(id='graph_6'), md=6
        )
    ]
)