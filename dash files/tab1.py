import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

# import data
user_clus = pd.read_csv("pivot_user_info_clustered.csv")


tab1_layout = html.Div([
    html.H5("Please select a user:"),
    dcc.Dropdown(
        id='user_dropdown',
        options=[{"label": str(i), "value": i} for i in user_clus["Internal_ID"]],
        value=1
    ),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="spending_graph", figure={}), width=8
        ),
        dbc.Col(
            dcc.Graph(id="ontime_graph", figure={}), width=4
        )]
    ),
    dbc.Row(
        dcc.Graph(id="essential_graph", figure={})
    )
])

