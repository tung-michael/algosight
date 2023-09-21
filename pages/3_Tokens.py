from analytical_scripts import user_date_input, session_state_init,\
    get_data_with_date_input,TOKEN_LIST
from sql_templates import QUERY_TOKEN_USAGE, QUERY_DETAILED_TX_COUNTS
import streamlit as st
import plotly.express as px



session_state_init(session_variable='token_usage_df')
session_state_init(session_variable='date_input_token_usage')
session_state_init(
  session_variable='user_options_tokens_usage',
  init_value=TOKEN_LIST
)

session_state_init(session_variable='detailed_tx_counts')
session_state_init(session_variable='date_input_dexs_per_token')
session_state_init(
  session_variable='selected_token',
  init_value=TOKEN_LIST[0]
  )


st.title("Put something creative here")

# Compare Token(s) Usage during a Time Period
st.subheader('Tokens Usage')
date_input_token_usage = user_date_input(key="Tokens Usage")
st.session_state['user_options_tokens_usage'] = st.multiselect(
  '**Select your desired Tokens:**',
  options=TOKEN_LIST,
  default=st.session_state['user_options_tokens_usage']
)

if st.button('Show graph', key='Tokens Usage'):
  st.session_state['token_usage_df'] = get_data_with_date_input(
    query=QUERY_TOKEN_USAGE,
    date_input=date_input_token_usage
    )
  st.session_state['date_input_token_usage'] = date_input_token_usage

# Display the graph and
# remain its present through its session state variables
if st.session_state['token_usage_df'] is not None:

  # Assign session varibles to other variables with "simpler" name
  session_date = st.session_state['date_input_token_usage']
  session_token_usage = st.session_state['token_usage_df']
  session_options_token_usage = st.session_state['user_options_tokens_usage']

  st.write(f'Usages of Tokens between {session_date[0]} and {session_date[1]}')

  chosen_token_usage = session_token_usage[session_token_usage["token_name"].isin(session_options_token_usage)]
  result_token_usage = chosen_token_usage.groupby(["token_name","tx_date"])["daily_tx_counts"].sum().reset_index()
  fig_token_usage = px.line(result_token_usage, x='tx_date', y='daily_tx_counts', color='token_name', title='Trading Frequency (number of transactions)')
  st.write(fig_token_usage)


# Token Usage on each Dex by trading frequency
st.subheader('Token traded on DEXs')
st.write(f'Look up which DEXs each Token is traded on')
date_input_dexs_per_token = user_date_input(key='DEXs per Token')
st.session_state['selected_token'] = st.selectbox(
  'Select a Token',
  options=TOKEN_LIST,
  index=TOKEN_LIST.index(st.session_state['selected_token'])
)

if st.button('Show graph', key='DEXs per Token'):

  # QUERY_DETAILED_TX_COUNTS doesn't filter for the selected Token. The filter step is done later with pandas.
  # This would help save some time if querying data for other Tokens, but in the same time period.
  st.session_state['detailed_tx_counts'] = get_data_with_date_input(
    query=QUERY_DETAILED_TX_COUNTS,
    date_input=date_input_dexs_per_token
  )
  st.session_state['date_input_dexs_per_token'] = date_input_dexs_per_token

if st.session_state['detailed_tx_counts'] is not None:

  # Assign session varibles to other variables with "simpler" name
  session_date_tx = st.session_state['date_input_dexs_per_token']
  session_tx_counts = st.session_state['detailed_tx_counts']
  session_selected_token = st.session_state['selected_token']

  st.write(f'DEXs where {session_selected_token} was traded on between {session_date_tx[0]} and {session_date_tx[1]}')

  # Filter for the selected dex
  filtered_tx_counts = session_tx_counts.loc[session_tx_counts['token_name'] == session_selected_token]

  sum_up_tx_counts = filtered_tx_counts.groupby(["platform","tx_date"])["daily_tx_counts"].sum().reset_index()
  fig_token_tx_counts = px.line(
    sum_up_tx_counts,
    x='tx_date',
    y='daily_tx_counts',
    color='platform',
    title=f'{session_selected_token} Daily Transaction Counts on DEXs'
    )
  st.write(fig_token_tx_counts)


# Token Usage on each Dex by trading volume
