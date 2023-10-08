# BTIs (clogs)
# Arbitrages

from utilities import display_table
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.subheader('Arbitrage Activities on Algorand from 09.2021 to 07.2023')
arbitrages_tokens_profits = {
  'token_name': ['ALGO', 'GARD', 'STBL', 'USDC', 'USDT'],
  'profits_in_usd': [235825.85958885177, 0.20898541950551966, 2899.516709122528, 11755.431827941433, 1169.1385135338169],
  'arbitrage_tx_counts': [1107629, 66, 3337, 18560, 2523]
  }
arb_tokens_df = pd.DataFrame(arbitrages_tokens_profits)

# Create lists for labels, parents, and values
total_profits = arb_tokens_df['profits_in_usd'].sum()
labels = ['Total'] + list(arb_tokens_df['token_name'])
parents = [''] + ['Total'] * len(arb_tokens_df)
values = [total_profits] + list(arb_tokens_df['profits_in_usd'])


# Abitrage Tokens Profits in treemap
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


# Arbitrage Transaction Counts per Token
bar_chart = go.Figure(
  data=[go.Bar(
  x=arbitrages_tokens_profits['token_name'],
  y=arbitrages_tokens_profits['arbitrage_tx_counts'])],
  layout={
    'title' : 'Arbitrage Transaction Counts per Token'
  }
  )
st.write(bar_chart)

# Arbers Profits charts
st.subheader("Arbitrageur's profits on Algorand from 09.2021 to 07.2023")

arber_profits = pd.read_csv('/Users/michael/Desktop/Algorand_DeFi_app/DeFi_app/postgres/arber_profits_in_usd.csv')
arber_profits = pd.DataFrame(arber_profits.groupby(['arber'])['profits_in_usd'].sum())
arber_profits = arber_profits.round(decimals=2)
arber_profits = arber_profits.sort_values(by='profits_in_usd', ascending=False).reset_index()
arber_profits.index +=1
display_table(arber_profits.head(20))

# Arbitrage Transaction Counts per Days
st.subheader("Arbitrage Transaction Counts per Days on Algorand from 09.2021 to 07.2023")

arbs_tx_counts = pd.read_csv('./postgres/arbs_tx_counts.csv')
chart_arbs_tx_counts = px.line(
  arbs_tx_counts,
  x='date',
  y='daily_arbitrage_counts',
  title='Arbitrage Transaction Counts per Days'
  )
st.write(chart_arbs_tx_counts)