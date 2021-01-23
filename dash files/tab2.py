import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

# import data
user_clus = pd.read_csv("pivot_user_info_clustered.csv")
trans_clus = pd.read_csv("trans_clustered.csv")

# data wrangling
user_clus.rename(columns={"Limite_Total": "Average Credit Limit", "Idade": "Age"}, inplace=True)


fig1 = px.scatter(user_clus, x="Monthly_Transactions", y="Monthly_Spending",
                  color="Cluster", title="User Average Monthly Spending vs. Average Monthly Transactions")
fig1.update_traces(marker=dict(size=15), hovertemplate="Monthly Transactions: %{x: .1f}"
                                                       + "<Br>Monthly Spending: $%{y: .0f}<extra></extra>")

fig2 = px.scatter(user_clus, x="NonEssential_Percentage", y="Average Credit Limit",
                  color="Cluster", title="User Average Credit Limit vs. %Spending on Non-Essential Goods")
fig2.update_traces(marker=dict(size=15), hovertemplate="Non-Essential Spending: %{x: .1f}"
                                                       + "<Br>Average Credit Limit: $%{y: .0f}<extra></extra>")

fig3 = px.scatter(user_clus, x="Age", y="Average Credit Limit",
                  color="Cluster", title="User Average Credit Limit vs. Average Age")
fig3.update_traces(marker=dict(size=15), hovertemplate="Age: %{x: .0f}"
                                                       + "<Br>Average Credit Limit: $%{y: .0f}<extra></extra>")

fig4 = go.Figure(data=[go.Table(
  header=dict(
    values=['User ID', 'Low Health', "Medium Health", "High Health"],
    line_color='darkslategray',
    fill_color=['grey', 'royalblue'],
    font=dict(color='white', size=14),
    height=50,
    align="center"
  ),
  cells=dict(
    values=[
        ["Group 1", "Group 2", "Group 3"],
        ["8, 9, 12, 14, 28, 29", "", "7, 11, 21, 27"],
        ["2, 6, 10, 13, 18, 19, 23", "", ""],
        ["1, 4, 5, 15, 16, 22, 24, 26", "3, 17", "25"]
    ],
    line_color='darkslategray',
    fill=dict(color=['paleturquoise', 'white', 'white', 'white']),
    font_size=16,
    align="center",
    height=70
    ))
])
fig4.update_layout(title_text="User Grouping Summary")

tab2_layout = html.Div([
    html.Br(),
    html.H6("Model: Hierarchical Clustering with Weighted Gower's Score"),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="Spending vs Transaction", figure=fig1)
        ),
        dbc.Col(
            dcc.Graph(id="Limit vs Spending", figure=fig2)
        )
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="Limit vs Age", figure=fig3)
        ),
        dbc.Col(
            dcc.Graph(id="health vs cluster table", figure=fig4)
        )
    ])
])
