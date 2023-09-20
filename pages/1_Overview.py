from analytical_scripts import user_date_input, get_data_with_date_input,\
    load_top_dexs, load_top_tokens, display_table, load_trading_volume, session_state_init
import streamlit as st
from sql_templates import QUERY_TOP_DEXS, QUERY_TOP_TOKENS, QUERY_TRADING_VOLUME
import pandas as pd
from pandas import DataFrame
import datetime

session_state_init(session_variable='top_dexs_df')
session_state_init(session_variable='top_tokens_df')

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
  st.write(f"Most used Tokens between {date_input_top_dexs[0]} and {date_input_top_dexs[1]}")
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
if st.session_state['top_dexs_df'] is not None:
  st.write(f"Most used Tokens between {date_input_top_tokens[0]} and {date_input_top_tokens[1]}")
  display_table(st.session_state['top_tokens_df'])




# Dexs Trading Volume
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
  trading_df = load_trading_volume(date_input_dex_trading)


# Hot Tokens Trading Volume

st.subheader('Tokens Trading Volume')
date_input_tokens_trading = user_date_input('Tokens Trading Volume')

if st.button('Show graph', key='Tokens Trading Volume'):
  trading_df = load_trading_volume(date_input_tokens_trading)
