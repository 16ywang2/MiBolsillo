import pandas as pd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# read in the data
trans_clus = pd.read_csv("trans_clustered.csv")
payments_clus = pd.read_csv("payments_clustered.csv")
user_clus = pd.read_csv("pivot_user_info_clustered.csv")
monthly_data = pd.read_csv("monthly_data.csv")


print(user_clus.columns)
