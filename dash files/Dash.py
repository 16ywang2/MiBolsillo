import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import tab1
import tab2
import tab3
import tab4
import tab5

# read in the data
trans_clus = pd.read_csv("trans_clustered.csv")
payments_clus = pd.read_csv("payments_clustered.csv")
user_clus = pd.read_csv("pivot_user_info_clustered.csv")
monthly_data = pd.read_csv("monthly_data.csv")

# app
app = dash.Dash("BancoPan Visualization", external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    html.H2("BancoPan Visualization"),
    dcc.Tabs(id="tabs", value="tab1", children=[
        dcc.Tab(label="Individual User Summary", value="tab1"),
        dcc.Tab(label="What are our Macro Profiles?", value="tab2"),
        dcc.Tab(label="Macro Profiles Summary Stats", value="tab3"),
        dcc.Tab(label="Macro Profiles Spending Behavior", value="tab4"),
        dcc.Tab(label="Demographics", value="tab5")
    ]),
    html.Div(id="content")
])


# render tabs
@app.callback(
    Output("content", "children"),
    Input("tabs", "value")
)
def render_content(tab):
    if tab == "tab1":
        return tab1.tab1_layout
    elif tab == "tab2":
        return tab2.tab2_layout
    elif tab == "tab3":
        return tab3.tab3_layout
    elif tab == "tab4":
        return tab4.tab4_layout
    elif tab == "tab5":
        return tab5.tab5_layout


# Tab 1 callbacks
# the payment on time pie chart
@app.callback(
    Output("ontime_graph", "figure"),
    Input("user_dropdown", "value")
)
def graph_ontime_percentage(user_selected):
    late_df = pd.pivot_table(payments_clus, values="Year-Month", index=["Internal_ID", "Latency"],
                             aggfunc="count").reset_index()
    filtered = late_df[late_df["Internal_ID"] == user_selected]

    fig = px.pie(data_frame=filtered, names="Latency", values="Year-Month",
                 title="User Payment History")
    fig.update_traces(hovertemplate="Number of month: %{value}")

    return fig


# Monthly spending graph
@app.callback(
    Output(component_id="spending_graph", component_property="figure"),
    Input(component_id="user_dropdown", component_property="value")
)
def graph_monthly_spending(user_selected):
    monthly_spending = trans_clus.groupby(["Internal_ID", "Year-Month"])["Value"].sum().reset_index()
    trans_filtered = monthly_spending[monthly_spending["Internal_ID"] == user_selected]

    fig = go.Figure(go.Scatter(x=trans_filtered["Year-Month"], y=trans_filtered["Value"],
                               marker=dict(size=15), hovertemplate="Spending: $%{y} <extra></extra>"))
    fig.update_layout(title="User Monthly Spending", xaxis_title="Year-Month",
                      yaxis_title="Value")
    return fig


# Essential/Non-essential spending
@app.callback(
    Output(component_id="essential_graph", component_property="figure"),
    Input(component_id="user_dropdown", component_property="value")
)
def graph_essential_spending(user_selected):
    essential_spending = pd.pivot_table(trans_clus, values="Value", index=["Internal_ID", "Year-Month"],
                                        columns="Expense_Importance", aggfunc="sum").reset_index()
    # fill NA values with 0, as it means no purchase
    essential_spending = essential_spending.fillna(0)
    filtered = essential_spending[essential_spending["Internal_ID"] == user_selected]

    trace1 = go.Scatter(x=filtered["Year-Month"], y=filtered["Essential"], name="Essential", mode="markers",
                        marker=dict(color="rgb(0,0,230)", size=17), hovertemplate="$%{y}")
    trace2 = go.Scatter(x=filtered["Year-Month"], y=filtered["Non-Essential"], name="Non-Essential", mode="markers",
                        marker=dict(color="rgb(230,0,0)", size=17), hovertemplate="$%{y}")
    fig = go.Figure()
    fig.add_trace(trace1)
    fig.add_trace(trace2)
    fig.update_layout(title="User Monthly Essential and Non-Essential Spending",
                      xaxis_title="Year-Month", yaxis_title="Value", width=1300)

    return fig


# Tab 3 callbacks
# all options for financial health
health_dic = {"high": "High Financial Health", "medium": "Medium Financial Health",
              "low": "Low Financial Health"}


# Callback to generate the second dropdown based on the first dropdown
@app.callback(
    Output(component_id="tab3_financial_health", component_property="options"),
    Input(component_id="tab3_profile", component_property="value")
)
def return_selection(user_selected):
    filtered = user_clus[user_clus["Cluster"] == user_selected]
    unique_keys = filtered["overall_health"].unique()
    if len(unique_keys) == 1:
        options = [{"label": "All Users", "value": "All"}]
    else:
        options = [{"label": health_dic[unique_key], "value": unique_key} for unique_key in unique_keys]
        options.append({"label": "All Users", "value": "All"})
    return options


# Reset the second dropdown whether the user changes the first
@app.callback(
    Output(component_id="tab3_financial_health", component_property="value"),
    Input(component_id="tab3_profile", component_property="value")
)
def reset(user_selected):
    return "All"


# Print how many users are selected
@app.callback(
    Output(component_id="tab3_num_users", component_property="children"),
    [Input(component_id="tab3_profile", component_property="value"),
     Input(component_id="tab3_financial_health", component_property="value")]
)
def print_num_users(profile, financial_health):
    if profile is None:
        num = user_clus.shape[0]
    else:
        if financial_health is None or financial_health == "All":
            filtered1 = user_clus[user_clus["Cluster"] == profile]
            num = filtered1.shape[0]
        else:
            filtered1 = user_clus[user_clus["Cluster"] == profile]
            filtered2 = filtered1[filtered1["overall_health"] == financial_health]
            num = filtered2.shape[0]
    return f"Number of users selected: {num}"


@app.callback(
    Output(component_id="tab3_spending", component_property="figure"),
    [
        Input(component_id="tab3_profile", component_property="value"),
        Input(component_id="tab3_financial_health", component_property="value"),
        Input(component_id="tab3_checkbox", component_property="value")
    ]
)
def spending_graph(profile, financial_health, checkbox):
    pop_average = (monthly_data.groupby("Year-Month")["Spending"].sum() /
                   monthly_data.groupby("Year-Month")["Spending"].count()).reset_index()
    fig = go.Figure()
    trace1 = go.Scatter(x=pop_average["Year-Month"], y=pop_average["Spending"], name="All users",
                        marker=dict(color="rgb(96,96,96)", size=10), hovertemplate="Spending: $%{y: .0f}")
    fig.add_trace(trace1)
    if profile is not None:
        profile_filtered = monthly_data[monthly_data["Cluster"] == profile]
        group_average = (profile_filtered.groupby("Year-Month")["Spending"].sum() /
                         profile_filtered.groupby("Year-Month")["Spending"].count()).reset_index()
        trace2 = go.Scatter(x=group_average["Year-Month"], y=group_average["Spending"],
                            name=f"All {profile} users",
                            marker=dict(color="rgb(0,0,210)", size=10), hovertemplate="Spending: $%{y: .0f}")
        if financial_health == "All":
            fig.add_trace(trace2)

        else:
            final_filtered = profile_filtered[profile_filtered["overall_health"] == financial_health]
            final_average = (final_filtered.groupby("Year-Month")["Spending"].sum() /
                             final_filtered.groupby("Year-Month")["Spending"].count()).reset_index()
            trace3 = go.Scatter(x=final_average["Year-Month"], y=final_average["Spending"],
                                name=f"All {financial_health} financial health users in {profile}",
                                marker=dict(color="rgb(102,204,0)", size=10), hovertemplate="Spending: $%{y: .0f}")
            if not checkbox:
                fig.add_trace(trace3)
                fig.add_trace(trace2)
            else:
                health_filtered = monthly_data[monthly_data["overall_health"] == financial_health]
                health_average = (health_filtered.groupby("Year-Month")["Spending"].sum() /
                                  health_filtered.groupby("Year-Month")["Spending"].count()).reset_index()
                trace4 = go.Scatter(x=health_average["Year-Month"], y=health_average["Spending"],
                                    name=f"All {financial_health} financial health users",
                                    marker=dict(color="rgb(255,128,0)", size=10), hovertemplate="Spending: $%{y: .0f}")
                fig.add_trace(trace3)
                fig.add_trace(trace2)
                fig.add_trace(trace4)

    fig.update_layout(title="Average Monthly Spending Per User", xaxis_title="Month", yaxis_title="Spending")
    return fig


@app.callback(
    Output(component_id="tab3_spending vs limit", component_property="figure"),
    [
        Input(component_id="tab3_profile", component_property="value"),
        Input(component_id="tab3_financial_health", component_property="value"),
        Input(component_id="tab3_checkbox", component_property="value")
    ]
)
def spending_limit_graph(profile, financial_health, checkbox):
    pop_average = monthly_data.groupby("Year-Month")["Spending to Limit"].mean().reset_index()
    fig = go.Figure()
    trace1 = go.Scatter(x=pop_average["Year-Month"], y=pop_average["Spending to Limit"], name="All users",
                        marker=dict(color="rgb(96,96,96)", size=10), hovertemplate="Spending/Total Limit:%{y: .2f}")
    fig.add_trace(trace1)
    if profile is not None:
        profile_filtered = monthly_data[monthly_data["Cluster"] == profile]
        group_average = profile_filtered.groupby("Year-Month")["Spending to Limit"].mean().reset_index()
        trace2 = go.Scatter(x=group_average["Year-Month"], y=group_average["Spending to Limit"],
                            name=f"All {profile} users",
                            marker=dict(color="rgb(0,0,210)", size=10), hovertemplate="Spending/Total Limit:%{y: .2f}")
        if financial_health == "All":
            fig.add_trace(trace2)

        else:
            final_filtered = profile_filtered[profile_filtered["overall_health"] == financial_health]
            final_average = final_filtered.groupby("Year-Month")["Spending to Limit"].mean().reset_index()
            trace3 = go.Scatter(x=final_average["Year-Month"], y=final_average["Spending to Limit"],
                                name=f"All {financial_health} financial health users in {profile}",
                                marker=dict(color="rgb(102,204,0)", size=10),
                                hovertemplate="Spending/Total Limit:%{y: .2f}")
            if not checkbox:
                fig.add_trace(trace3)
                fig.add_trace(trace2)
            else:
                health_filtered = monthly_data[monthly_data["overall_health"] == financial_health]
                health_average = health_filtered.groupby("Year-Month")["Spending to Limit"].mean().reset_index()
                trace4 = go.Scatter(x=health_average["Year-Month"], y=health_average["Spending to Limit"],
                                    name=f"All {financial_health} financial health users",
                                    marker=dict(color="rgb(255,128,0)", size=10),
                                    hovertemplate="Spending/Total Limit:%{y: .2f}")
                fig.add_trace(trace3)
                fig.add_trace(trace2)
                fig.add_trace(trace4)

    fig.update_layout(title="Average Spending/Total Limit Per User", xaxis_title="Month", yaxis_title="Percentage")
    return fig


# callbacks for tab 4
# Callback to generate the second dropdown based on the first dropdown
@app.callback(
    Output(component_id="tab4_financial_health", component_property="options"),
    Input(component_id="tab4_profile", component_property="value")
)
def return_selection(user_selected):
    filtered = user_clus[user_clus["Cluster"] == user_selected]
    unique_keys = filtered["overall_health"].unique()
    if len(unique_keys) == 1:
        options = [{"label": "All Users", "value": "All"}]
    else:
        options = [{"label": health_dic[unique_key], "value": unique_key} for unique_key in unique_keys]
        options.append({"label": "All Users", "value": "All"})
    return options


# Reset the second dropdown whether the user changes the first
@app.callback(
    Output(component_id="tab4_financial_health", component_property="value"),
    Input(component_id="tab4_profile", component_property="value")
)
def reset(user_selected):
    return "All"


# Print how many users are selected
@app.callback(
    Output(component_id="tab4_num_users", component_property="children"),
    [Input(component_id="tab4_profile", component_property="value"),
     Input(component_id="tab4_financial_health", component_property="value")]
)
def print_num_users(profile, financial_health):
    if profile is None:
        num = user_clus.shape[0]
    else:
        if financial_health is None or financial_health == "All":
            filtered1 = user_clus[user_clus["Cluster"] == profile]
            num = filtered1.shape[0]
        else:
            filtered1 = user_clus[user_clus["Cluster"] == profile]
            filtered2 = filtered1[filtered1["overall_health"] == financial_health]
            num = filtered2.shape[0]
    return f"Number of users selected: {num}"


# generate the nonessential plot
@app.callback(
    Output(component_id="tab4_NonEssential", component_property="figure"),
    [
        Input(component_id="tab4_profile", component_property="value"),
        Input(component_id="tab4_financial_health", component_property="value"),
        Input(component_id="tab4_checkbox", component_property="value")
    ]
)
def nonessential_graph(profile, financial_health, checkbox):
    pop_average = monthly_data.groupby("Year-Month")["NonEssential_Percentage"].mean().reset_index()
    fig = go.Figure()
    trace1 = go.Scatter(x=pop_average["Year-Month"], y=pop_average["NonEssential_Percentage"], name="All users",
                        marker=dict(color="rgb(96,96,96)", size=10),
                        hovertemplate="Non-Essential Spending:%{y: .2f}")
    fig.add_trace(trace1)
    if profile is not None:
        profile_filtered = monthly_data[monthly_data["Cluster"] == profile]
        group_average = profile_filtered.groupby("Year-Month")["NonEssential_Percentage"].mean().reset_index()
        trace2 = go.Scatter(x=group_average["Year-Month"], y=group_average["NonEssential_Percentage"],
                            name=f"All {profile} users",
                            marker=dict(color="rgb(0,0,210)", size=10),
                            hovertemplate="Non-Essential Spending:%{y: .2f}")
        if financial_health == "All":
            fig.add_trace(trace2)

        else:
            final_filtered = profile_filtered[profile_filtered["overall_health"] == financial_health]
            final_average = final_filtered.groupby("Year-Month")["NonEssential_Percentage"].mean().reset_index()
            trace3 = go.Scatter(x=final_average["Year-Month"], y=final_average["NonEssential_Percentage"],
                                name=f"All {financial_health} financial health users in {profile}",
                                marker=dict(color="rgb(102,204,0)", size=10),
                                hovertemplate="Non-Essential Spending:%{y: .2f}")
            if not checkbox:
                fig.add_trace(trace3)
                fig.add_trace(trace2)
            else:
                health_filtered = monthly_data[monthly_data["overall_health"] == financial_health]
                health_average = health_filtered.groupby("Year-Month")["NonEssential_Percentage"].mean().reset_index()
                trace4 = go.Scatter(x=health_average["Year-Month"], y=health_average["NonEssential_Percentage"],
                                    name=f"All {financial_health} financial health users",
                                    marker=dict(color="rgb(255,128,0)", size=10),
                                    hovertemplate="Non-Essential Spending:%{y: .2f}")
                fig.add_trace(trace3)
                fig.add_trace(trace2)
                fig.add_trace(trace4)

    fig.update_layout(title="Average Percentage Spending of Non-Essential Goods Per User", xaxis_title="Month",
                      yaxis_title="Percentage")
    return fig


# reset date_picker
@app.callback(
    [Output(component_id="tab4_date_picker", component_property="start_date"),
     Output(component_id="tab4_date_picker", component_property="end_date")],
    Input(component_id="tab4_button", component_property="n_clicks")
)
def reset_date(reset):
    return trans_clus["Fixed_Date"].min(), trans_clus["Fixed_Date"].max()


# generate the first pie chart
@app.callback(
    Output(component_id="tab4_pop_Cate", component_property="figure"),
    [Input(component_id="tab4_date_picker", component_property="start_date"),
     Input(component_id="tab4_date_picker", component_property="end_date")]
)
def first_pie(start_date, end_date):
    dates_filtered = trans_clus[trans_clus["Fixed_Date"].between(start_date, end_date)]
    cate_summary = (dates_filtered.groupby("Grupo_Estabelecimento")["Value"].sum() / dates_filtered["Value"].sum()) \
        .reset_index().sort_values("Value", ascending=False).reset_index()
    cate_summary.loc[5:, "Grupo_Estabelecimento"] = "Others"
    fig = px.pie(cate_summary, names="Grupo_Estabelecimento", values="Value")
    fig.update_traces(textposition='inside', textinfo='percent+label', showlegend=False,
                      title_text="Category Breakdown for All Users", title_font_size=60, hovertemplate=None,
                      hoverinfo='skip')
    return fig


# generate the second pie chart
@app.callback(
    Output(component_id="tab4_group_Cate", component_property="figure"),
    [Input(component_id="tab4_date_picker", component_property="start_date"),
     Input(component_id="tab4_date_picker", component_property="end_date"),
     Input(component_id="tab4_profile", component_property="value")]
)
def second_pie(start_date, end_date, profile):
    if profile is None:
        dates_filtered = trans_clus[trans_clus["Fixed_Date"].between(start_date, end_date)]
    else:
        group_filtered = trans_clus[trans_clus["Cluster"] == profile]
        dates_filtered = group_filtered[group_filtered["Fixed_Date"].between(start_date, end_date)]
    cate_summary = (dates_filtered.groupby("Grupo_Estabelecimento")["Value"].sum() / dates_filtered["Value"].sum()) \
        .reset_index().sort_values("Value", ascending=False).reset_index()
    cate_summary.loc[5:, "Grupo_Estabelecimento"] = "Others"
    fig = px.pie(cate_summary, names="Grupo_Estabelecimento", values="Value")
    fig.update_traces(textposition='inside', textinfo='percent+label', showlegend=False,
                      title_text=f"Category Breakdown for all users in {profile}", title_font_size=60,
                      hovertemplate=None, hoverinfo='skip'
                      )
    return fig


# generate the third pie chart
@app.callback(
    Output(component_id="tab4_health_Cate", component_property="figure"),
    [Input(component_id="tab4_date_picker", component_property="start_date"),
     Input(component_id="tab4_date_picker", component_property="end_date"),
     Input(component_id="tab4_profile", component_property="value"),
     Input(component_id="tab4_financial_health", component_property="value")]
)
def third_pie(start_date, end_date, profile, financial_health):
    if profile is None:
        dates_filtered = trans_clus[trans_clus["Fixed_Date"].between(start_date, end_date)]
    else:
        if financial_health == "All" or financial_health is None:
            group_filtered = trans_clus[trans_clus["Cluster"] == profile]
            dates_filtered = group_filtered[group_filtered["Fixed_Date"].between(start_date, end_date)]
        else:
            group_filtered = trans_clus[trans_clus["Cluster"] == profile]
            health_filtered = group_filtered[group_filtered["overall_health"] == financial_health]
            dates_filtered = health_filtered[health_filtered["Fixed_Date"].between(start_date, end_date)]
    cate_summary = (dates_filtered.groupby("Grupo_Estabelecimento")["Value"].sum() / dates_filtered["Value"].sum()) \
        .reset_index().sort_values("Value", ascending=False).reset_index()
    cate_summary.loc[5:, "Grupo_Estabelecimento"] = "Others"
    fig = px.pie(cate_summary, names="Grupo_Estabelecimento", values="Value")
    fig.update_traces(textposition='inside', textinfo='percent+label', showlegend=False,
                      title_text=f"Category Breakdown for {financial_health} financial health users in {profile}",
                      title_font_size=60, hovertemplate=None, hoverinfo='skip')
    return fig


# tab 5 callbacks
# Callback to generate the second dropdown based on the first dropdown
@app.callback(
    Output(component_id="tab5_financial_health", component_property="options"),
    Input(component_id="tab5_profile", component_property="value")
)
def return_selection(user_selected):
    filtered = user_clus[user_clus["Cluster"] == user_selected]
    unique_keys = filtered["overall_health"].unique()
    if len(unique_keys) == 1:
        options = [{"label": "All Users", "value": "All"}]
    else:
        options = [{"label": health_dic[unique_key], "value": unique_key} for unique_key in unique_keys]
        options.append({"label": "All Users", "value": "All"})
    return options


# Reset the second dropdown whether the user changes the first
@app.callback(
    Output(component_id="tab5_financial_health", component_property="value"),
    Input(component_id="tab5_profile", component_property="value")
)
def reset(user_selected):
    return "All"


# show how many users are selected
@app.callback(
    Output(component_id="tab5_num_users", component_property="children"),
    [Input(component_id="tab5_profile", component_property="value"),
     Input(component_id="tab5_financial_health", component_property="value")]
)
def print_num_users(profile, financial_health):
    if profile is None:
        num = user_clus.shape[0]
    else:
        if financial_health is None or financial_health == "All":
            filtered1 = user_clus[user_clus["Cluster"] == profile]
            num = filtered1.shape[0]
        else:
            filtered1 = user_clus[user_clus["Cluster"] == profile]
            filtered2 = filtered1[filtered1["overall_health"] == financial_health]
            num = filtered2.shape[0]
    return f"Number of users selected: {num}"


# pie chart for gender
@app.callback(
    Output(component_id="gender_pie", component_property="figure"),
    [Input(component_id="tab5_profile", component_property="value"),
     Input(component_id="tab5_financial_health", component_property="value")]
)
def gender_pie(profile, health):
    if profile is None:
        filtered = user_clus
    else:
        if health is None or health == "All":
            filtered = user_clus[user_clus["Cluster"] == profile]
        else:
            filtered1 = user_clus[user_clus["Cluster"] == profile]
            filtered = filtered1[filtered1["overall_health"] == health]
    filtered_pie = filtered.groupby("Sexo")["Internal_ID"].count().reset_index()
    fig = px.pie(filtered_pie, names="Sexo", values="Internal_ID")
    fig.update_traces(textposition='inside', textinfo='percent+label', showlegend=False,
                      title_text="Gender Breakdown",
                      title_font_size=18, hovertemplate="Number of Users: %{value}")
    return fig


# pie chart for location
@app.callback(
    Output(component_id="geo_pie", component_property="figure"),
    [Input(component_id="tab5_profile", component_property="value"),
     Input(component_id="tab5_financial_health", component_property="value")]
)
def geo_pie(profile, health):
    user_clus["location"] = np.where(user_clus["Cidade"] == "SAO PAULO", "In SAO PAULO", "Outside SAO PAULO")
    if profile is None:
        filtered = user_clus
    else:
        if health is None or health == "All":
            filtered = user_clus[user_clus["Cluster"] == profile]
        else:
            filtered1 = user_clus[user_clus["Cluster"] == profile]
            filtered = filtered1[filtered1["overall_health"] == health]
    filtered_pie = filtered.groupby("location")["Internal_ID"].count().reset_index()
    fig = px.pie(filtered_pie, names="location", values="Internal_ID")
    fig.update_traces(textposition='inside', textinfo='percent+label', showlegend=False,
                      title_text="Location Breakdown",
                      title_font_size=18, hovertemplate="Number of Users: %{value}")
    return fig


# age scatter plot
@app.callback(
    Output(component_id="age_scatter", component_property="figure"),
    [Input(component_id="tab5_profile", component_property="value"),
     Input(component_id="tab5_financial_health", component_property="value")]
)
def age_scatter(profile, health):
    user_clus["location"] = np.where(user_clus["Cidade"] == "SAO PAULO", "In SAO PAULO", "Outside SAO PAULO")
    if profile is None:
        filtered = user_clus
    else:
        if health is None or health == "All":
            filtered = user_clus[user_clus["Cluster"] == profile]
        else:
            filtered1 = user_clus[user_clus["Cluster"] == profile]
            filtered = filtered1[filtered1["overall_health"] == health]
    fig = px.scatter(filtered, x="Idade", y="Monthly_Spending", color="Sexo", title="Age Analysis")
    fig.update_traces(marker=dict(size=15))
    fig.update_xaxes(range=[18, 48])
    return fig


app.run_server(debug=True)
