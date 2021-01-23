import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

tab3_layout = html.Div([
    html.H6("Please select a Macro Profile:"),
    dcc.Dropdown(
        id="tab3_profile",
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
        id="tab3_financial_health",
        value="All"
    ),
    html.Div(id="tab3_num_users"),
    dcc.Graph(id="tab3_spending", figure={}),
    dbc.Row([
        dbc.Col(width=9),
        dbc.Col(
            dcc.Checklist(
                id="tab3_checkbox",
                options=[{"label": "Show average of all users of the selected financial health option", "value": "show"}],
                value=[]
            )
        )
    ]),
    dcc.Graph(id="tab3_spending vs limit", figure={})
])
