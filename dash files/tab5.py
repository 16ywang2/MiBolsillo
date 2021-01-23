import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd

user_clus = pd.read_csv("pivot_user_info_clustered.csv")

tab5_layout = html.Div([
    html.H6("Please select a Macro Profile:"),
    dcc.Dropdown(
        id="tab5_profile",
        options=[
            {"label": "Group 1: Low spending customers", "value": "Group 1"},
            {"label": "Group 2: High credit limit, high spending customers", "value": "Group 2"},
            {"label": "Group 3: Early parents? (Many transactions, High essential purchase, Between 30 and 40)",
             "value": "Group 3"}
        ],
        value=None
    ),
    html.H6("(Optional) Additionally, you can further choose a financial health option"),
    dcc.Dropdown(
        id="tab5_financial_health",
        value="All"
    ),
    html.Div(id="tab5_num_users"),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="gender_pie", figure={})
        ),
        dbc.Col(
            dcc.Graph(id="geo_pie", figure={})
        )
    ]),
    dcc.Graph(id="age_scatter", figure={})
])
