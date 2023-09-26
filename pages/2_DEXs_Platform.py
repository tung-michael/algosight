from utilities import user_date_input, \
    get_data_with_date_input, session_state_init, DEX_LIST
import streamlit as st
from sql_templates import QUERY_DEX_USAGE, QUERY_DEX_TRADING_VOLUME, QUERY_DETAILED_TX_COUNTS
import plotly.express as px



# Initialize session states for relevant variables.
# Default value is None

session_state_init(session_variable='dex_usage_df')
session_state_init(session_variable='date_input_dex_usage')
session_state_init(
  session_variable='user_options_dex_usage',
  init_value=DEX_LIST
  )

session_state_init(session_variable='detailed_tx_counts')
session_state_init(session_variable='date_input_tokens_on_dex')
session_state_init(
  session_variable='selected_dex',
  init_value=DEX_LIST[0]
  )


st.title("Put something creative here")

# Compare Dexs Usage Block
st.subheader('DEXs Usage')
st.write(f'Compare the usages of DEXs within a time period ')
date_input_dex_usage = user_date_input('DEXs Usage')
st.session_state['user_options_dex_usage'] = st.multiselect(
  '**Select your desired DEXs:**',
  options=DEX_LIST,
  default=st.session_state['user_options_dex_usage']
)

if st.button('Show graph', key='DEXs Usage'):
  st.session_state['dex_usage_df'] = get_data_with_date_input(
    query=QUERY_DEX_USAGE,
    date_input=date_input_dex_usage
    )
  st.session_state['date_input_dex_usage'] = date_input_dex_usage

# Display the graph and
# remain its present through its session state variables
if st.session_state['dex_usage_df'] is not None:

  # Assign session varibles to other variables with "simpler" name
  session_date_usage = st.session_state['date_input_dex_usage']
  session_dex_usage = st.session_state['dex_usage_df']
  session_options_dex_usage = st.session_state['user_options_dex_usage']

  st.write(f'Usages of DEXs between {session_date_usage[0]} and {session_date_usage[1]}')

  chosen_dex_usage = session_dex_usage[session_dex_usage["platform"].isin(session_options_dex_usage)]
  result_dex_usage = chosen_dex_usage.groupby(["platform","tx_date"])["daily_tx_counts"].sum().reset_index()
  fig_dex_usage = px.line(result_dex_usage, x='tx_date', y='daily_tx_counts', color='platform', title='Trading Frequency (number of transactions)')
  st.write(fig_dex_usage)


# DEX's Transaction Counts per Tokens

st.subheader("DEX's Transaction Counts per Tokens")
st.write(f'Look up how frequently tokens are traded on each DEX')
date_input_tokens_on_dex = user_date_input(key='Tokens per DEX')
st.session_state['selected_dex'] = st.selectbox(
  'Select a DEX platform',
  options=DEX_LIST,
  index=DEX_LIST.index(st.session_state['selected_dex'])
)

if st.button('Show graph', key='Tokens per DEX'):

  # QUERY_DETAILED_TX_COUNTS doesn't filter for the selected DEX. The filter step is done later with pandas.
  # This would help save some time if querying data for other DEXs, but in the same time period.
  st.session_state['detailed_tx_counts'] = get_data_with_date_input(
    query=QUERY_DETAILED_TX_COUNTS,
    date_input=date_input_tokens_on_dex
  )
  st.session_state['date_input_tokens_on_dex'] = date_input_tokens_on_dex

if st.session_state['detailed_tx_counts'] is not None:

  # Assign session varibles to other variables with "simpler" name
  session_date_tx = st.session_state['date_input_tokens_on_dex']
  session_tx_counts = st.session_state['detailed_tx_counts']
  session_selected_dex = st.session_state['selected_dex']

  st.write(f'Tokens traded on {session_selected_dex} between {session_date_tx[0]} and {session_date_tx[1]}')

  # Filter for the selected dex
  filtered_tx_counts = session_tx_counts.loc[session_tx_counts['platform'] == session_selected_dex]

  sum_up_tx_counts = filtered_tx_counts.groupby(["token_name","tx_date"])["daily_tx_counts"].sum().reset_index()
  fig_dex_tx_counts = px.line(
    sum_up_tx_counts,
    x='tx_date',
    y='daily_tx_counts',
    color='token_name',
    title=f'{session_selected_dex} Daily Transaction Counts per Token'
    )
  st.write(fig_dex_tx_counts)


# DEXs Trading Volume per Token