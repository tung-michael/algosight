from analytical_scripts import user_date_input, session_state_init,\
    get_data_with_date_input,TOKEN_LIST
from sql_templates import QUERY_TOKEN_USAGE
import streamlit as st
import plotly.express as px




session_state_init(session_variable='token_usage_df')
session_state_init(session_variable='date_input_token_usage')
session_state_init(
  session_variable='user_options_tokens_usage',
  init_value=TOKEN_LIST
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
  result_token_usage = chosen_token_usage.groupby(["token_name","tx_date"])["trading_frequency"].sum().reset_index()
  fig_token_usage = px.line(result_token_usage, x='tx_date', y='trading_frequency', color='token_name', title='Trading Frequency (number of transactions)')
  st.write(fig_token_usage)
# Token Usage on each Dex by trading frequency



# Token Usage on each Dex by trading volume
