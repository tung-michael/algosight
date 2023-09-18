from analytical_scripts import user_date_input, execute_button
import streamlit as st
from sql_templates import QUERY_TOP_DEXS, QUERY_TOP_TOKENS
import pandas as pd
from pandas import DataFrame
import datetime


st.title("Put something creative here")
# Top DEXs Block

st.subheader('Top DEXs')
date_input = user_date_input('Top DEXs')
execute_button(
  key='Top DEXs',
  query=QUERY_TOP_DEXS.format(
    start_date=date_input[0],
    end_date=date_input[1]
  ),
  output_form='table'
  )

# Top Tokens Blocks

st.subheader('Top Tokens')
date_input = user_date_input('Top Tokens')
execute_button(
  key='Top Tokens',
  query=QUERY_TOP_TOKENS.format(
    start_date=date_input[0],
    end_date=date_input[1]
  ),
  output_form='table'
  )
