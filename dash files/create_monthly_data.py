import pandas as pd
import numpy as np

trans_clus = pd.read_csv("trans_clustered.csv")
payments_clus = pd.read_csv("payments_clustered.csv")
user_clus = pd.read_csv("pivot_user_info_clustered.csv")

# spending
monthly_data = trans_clus.pivot_table(values="Value", index=["Internal_ID", "Year-Month"], aggfunc='sum').reset_index()

# transactions
freq = trans_clus.pivot_table(values="Value", index=["Internal_ID", "Year-Month"], aggfunc='count').reset_index()
monthly_data = monthly_data.merge(freq, on=["Internal_ID", "Year-Month"])
monthly_data.rename(columns={"Value_y": "Transactions"}, inplace=True)
monthly_data.rename(columns={"Value_x": "Spending"}, inplace=True)

# nonessential spending
calc_essential = pd.pivot_table(trans_clus, values='ID', index=['Internal_ID', "Year-Month"],
                                columns=['Expense_Importance'], aggfunc='count').reset_index()
calc_essential.fillna(0, inplace=True)
monthly_data = monthly_data.merge(calc_essential, on=["Internal_ID", "Year-Month"])
monthly_data["NonEssential_Percentage"] = monthly_data['Non-Essential'] / monthly_data['Transactions']
monthly_data["Essential_Percentage"] = monthly_data['Essential'] / monthly_data['Transactions']

# spending of total limit
Average_Total_Limit = pd.pivot_table(trans_clus, values="Limite_Total",
                                     index=["Internal_ID", "Year-Month"], aggfunc="mean").reset_index()
monthly_data = monthly_data.merge(Average_Total_Limit, on=["Internal_ID", "Year-Month"])
monthly_data.rename(columns={"Limite_Total": "Average_Total_Limit"}, inplace=True)
monthly_data["Spending to Limit"] = monthly_data["Spending"] / monthly_data["Average_Total_Limit"]

# append health and clusters for grouping
temp = user_clus[["Internal_ID", "Cluster", "overall_health"]]
monthly_data = monthly_data.merge(temp, on="Internal_ID")

# export data
# monthly_data.to_csv("monthly_data.csv")

print(monthly_data["Year-Month"].min())


