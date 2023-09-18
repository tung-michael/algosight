# BTIs (clogs)
# Arbitrages


import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Step 1: Create a dataframe with your transactions
data = {
  'Transaction_ID': [f'Tx_{i}' for i in range(1, 11)],
  'Volume': [i for i in range(1, 100,10)]
}
df = pd.DataFrame(data)

# Step 2: Create lists for labels, parents, and values
total_volume = df['Volume'].sum()
labels = ['Total'] + list(df['Transaction_ID'])
parents = [''] + ['Total'] * len(df)
values = [total_volume] + list(df['Volume'])

# Step 3: Create the treemap
fig = go.Figure(
  go.Treemap(
    labels=labels,
    parents=parents,
    values=values,
    branchvalues='total',
    hovertemplate='<b>%{label}</b><br>Volume: %{value}'
  ),
  layout={
    'title' : 'Transactions Volume'
  }
)

# Step 4: Show the treemap on the Streamlit app
st.write(fig)
