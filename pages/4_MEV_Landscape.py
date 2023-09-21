# BTIs (clogs)
# Arbitrages


import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.subheader('Arbitrage Activities on Algorand from 09.2021 to 07.2023')
arbitrages_profit_data = {
  'token_name': ['ALGO', 'GARD', 'STBL', 'USDC', 'USDT'],
  'profits_in_usd': [235825.85958885177, 0.20898541950551966, 2899.516709122528, 11755.431827941433, 1169.1385135338169],
  'arbitrage_tx_counts': [1107629, 66, 3337, 18560, 2523]
  }
df = pd.DataFrame(arbitrages_profit_data)

# Create lists for labels, parents, and values
total_profits = df['profits_in_usd'].sum()
labels = ['Total'] + list(df['token_name'])
parents = [''] + ['Total'] * len(df)
values = [total_profits] + list(df['profits_in_usd'])

# Create the treemap
treemap_fig = go.Figure(
  go.Treemap(
    labels=labels,
    parents=parents,
    values=values,
    branchvalues='total',
    hovertemplate='<b>%{label}</b><br>Volume: %{value}'
  ),
  layout={
    'title' : 'Arbitrage Profits in USD'
  }
)

st.write(treemap_fig)

bar_chart = go.Figure(
  data=[go.Bar(
  x=arbitrages_profit_data['token_name'],
  y=arbitrages_profit_data['arbitrage_tx_counts'])],
  layout={
    'title' : 'Arbitrage Transaction Counts per Token'
  }
  )
st.write(bar_chart)

