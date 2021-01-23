import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd

trans_clus = pd.read_csv("trans_clustered.csv")

tab4_layout = html.Div([
    html.H6("Please select a Macro Profile:"),
    dcc.Dropdown(
        id="tab4_profile",
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
        id="tab4_financial_health",
        value="All"
    ),
    html.Div(id="tab4_num_users"),
    dbc.Row([
        dbc.Col(width=6),
        dbc.Col(
            dcc.Checklist(
                id="tab4_checkbox",
                options=[
                    {"label": "Show average of all users of the selected financial health option", "value": "show"}],
                value=[]
            )
        )
    ]),
    dcc.Graph(id="tab4_NonEssential", figure={}),
    html.H6("Pick a time period for the Breakdown Analysis:"),
    dbc.Row([
        dbc.Col(
            dcc.DatePickerRange(
                id="tab4_date_picker",
                min_date_allowed=trans_clus["Fixed_Date"].min(),
                max_date_allowed=trans_clus["Fixed_Date"].max(),
                start_date=trans_clus["Fixed_Date"].min(),
                end_date=trans_clus["Fixed_Date"].max(),
                initial_visible_month="2019-10-01"
            )
        ),
        dbc.Col(
            html.Button(
                "Reset Time Period",
                id="tab4_button",
                n_clicks=0
            )
        ),
        dbc.Col(width=6)
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="tab4_pop_Cate", figure={}),
            width=4
        ),
        dbc.Col(
            dcc.Graph(id="tab4_group_Cate", figure={}),
            width=4
        ),
        dbc.Col(
            dcc.Graph(id="tab4_health_Cate", figure={}),
            width=4
        )
    ])
])
