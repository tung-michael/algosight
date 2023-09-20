from analytical_scripts import user_date_input, \
    get_data_with_date_input, session_state_init, DEX_LIST
import streamlit as st
from sql_templates import QUERY_DEX_USAGE, QUERY_DEX_TRADING_VOLUME
import plotly.express as px



# Initialize session states for relevant variables.
# Default value is None

session_state_init(session_variable='dex_usage_df')
session_state_init(session_variable='date_input_dex_usage')
session_state_init(
  session_variable='user_options_dex_usage',
  init_value=DEX_LIST
  )


st.title("Put something creative here")

# Compare Dexs Usage Block
st.subheader('DEXs Usage')
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
  session_date = st.session_state['date_input_dex_usage']
  session_dex_usage = st.session_state['dex_usage_df']
  session_options_dex_usage = st.session_state['user_options_dex_usage']

  st.write(f'Usages of DEXs between {session_date[0]} and {session_date[1]}')

  chosen_dex_usage = session_dex_usage[session_dex_usage["platform"].isin(session_options_dex_usage)]
  result_dex_usage = chosen_dex_usage.groupby(["platform","tx_date"])["trading_frequency"].sum().reset_index()
  fig_dex_usage = px.line(result_dex_usage, x='tx_date', y='trading_frequency', color='platform', title='Trading Frequency (number of transactions)')
  st.write(fig_dex_usage)



# Dexs Trading Volume or Dexs Usage for each tokens ?

