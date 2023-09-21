from analytical_scripts import user_date_input, get_data_with_date_input,\
  display_table, session_state_init
import streamlit as st
from sql_templates import QUERY_TOP_DEXS, QUERY_TOP_TOKENS, QUERY_TRADING_VOLUME
import pandas as pd
from pandas import DataFrame
import datetime
import plotly.express as px

session_state_init(session_variable='top_dexs_df')
session_state_init(session_variable='top_tokens_df')
session_state_init(session_variable='dex_trading_df')
session_state_init(session_variable='token_trading_df')
session_state_init(session_variable='date_input_dex_trading')
session_state_init(session_variable='date_input_tokens_trading')

st.title("Put something creative here")
# Top DEXs Block

st.subheader('Top DEXs')
# Ask for user input
date_input_top_dexs = user_date_input('Top DEXs')

# Calculate the data and save to the corresponding session state
if st.button('Show graph', key='Top DEXs'):
  # st.session_state['top_dexs_df'] = load_top_dexs(date_input_top_dexs)
  st.session_state['top_dexs_df'] = get_data_with_date_input(
    date_input=date_input_top_dexs,
    query=QUERY_TOP_DEXS
    )

# Visualize data saved in session state.
# Keep the visualization presented
# even when user interacts with other parts of the page or navigate away.
if st.session_state['top_dexs_df'] is not None:
  st.write(f"Most used DEXs between {date_input_top_dexs[0]} and {date_input_top_dexs[1]}")
  display_table(st.session_state['top_dexs_df'])



# Top Tokens Blocks

st.subheader('Top Tokens')
date_input_top_tokens = user_date_input('Top Tokens')
if st.button('Show graph', key='Top Tokens'):
  # st.session_state['top_tokens_df'] = load_top_tokens(date_input_top_tokens)
  st.session_state['top_tokens_df'] = get_data_with_date_input(
    date_input=date_input_top_tokens,
    query=QUERY_TOP_TOKENS
    )
if st.session_state['top_tokens_df'] is not None:
  st.write(f"Most used Tokens between {date_input_top_tokens[0]} and {date_input_top_tokens[1]}")
  display_table(st.session_state['top_tokens_df'])




# Trading Volume DEXs and Tokens
# Graph: Treemap
# parameters: from_date, to_date
# data input:
#   dexs: pair, app_id, platform
#   app_calss: app_id, related_txn
#   asset_transfer_txns: asset_id, amount, related_txn
#   algo_prices:
#
# Compute Logic


st.subheader('DEXs Trading Volume')
date_input_dex_trading = user_date_input('DEXs Trading Volume')

if st.button('Show graph', key='DEXs Trading Volume'):
  st.session_state['dex_trading_df'] = get_data_with_date_input(
    query=QUERY_TRADING_VOLUME,
    date_input=date_input_dex_trading)
  st.session_state['date_input_dex_trading'] = date_input_dex_trading

if st.session_state['dex_trading_df'] is not None:
  session_date_dex_trading = st.session_state['date_input_dex_trading']
  session_dex_trading_df = st.session_state['dex_trading_df']

  filtered_dex_trading_df = session_dex_trading_df.groupby(['platform'])['trading_volume_usd'].sum().reset_index()
  dex_trading_fig = px.treemap(filtered_dex_trading_df, path=['platform'], values='trading_volume_usd')
  st.write(dex_trading_fig)



# Hot Tokens Trading Volume

st.subheader('Tokens Trading Volume')
date_input_tokens_trading = user_date_input('Tokens Trading Volume')

if st.button('Show graph', key='Tokens Trading Volume'):
  st.session_state['token_trading_df'] = get_data_with_date_input(
    query=QUERY_TRADING_VOLUME,
    date_input=date_input_tokens_trading)
  st.session_state['date_input_tokens_trading'] = date_input_tokens_trading

if st.session_state['token_trading_df'] is not None:
  session_date_tokens_trading = st.session_state['date_input_tokens_trading']
  session_token_trading_df = st.session_state['token_trading_df']

  filtered_token_trading_df = session_token_trading_df.groupby(['token_name'])['trading_volume_usd'].sum().reset_index()
  token_trading_fig = px.treemap(filtered_token_trading_df, path=['token_name'], values='trading_volume_usd')
  st.write(token_trading_fig)