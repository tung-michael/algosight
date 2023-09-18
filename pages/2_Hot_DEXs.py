from analytical_scripts import user_date_input, execute_button
import streamlit as st
from sql_templates import QUERY_DEX_USAGE, QUERY_DEX_TRADING_VOLUME

# Graph: Treemap
# parameters: from_date, to_date
# data input:
#   dexs: pair, app_id, platform
#   app_calss: app_id, related_txn
#   asset_transfer_txns: asset_id, amount, related_txn
#   algo_prices:
#
# Compute Logic
#
#


######################## Streamlit codes ####################################

st.title("Put something creative here")


# Compare Dexs Usage Block

st.subheader('DEXs Usage')
date_input = user_date_input('DEXs Usage')
execute_button(
  key='DEXs Usage',
  query=QUERY_DEX_USAGE.format(
    start_date=date_input[0],
    end_date=date_input[1]
  ),
  output_form='table'
  )



# Dexs Trading Volume

st.subheader('DEXs Trading Volume')
date_input = user_date_input('DEXs Trading Volume')
execute_button(
  key='DEXs Trading Volume',
  query=QUERY_DEX_TRADING_VOLUME.format(
    start_date=date_input[0],
    end_date=date_input[1]
  ),
  output_form='table'
  )

# st.title('Choose Time Period')
# # Select boxes for start and end dates
# dexs_start_date = st.date_input('Start date', datetime.date(2023, 1, 1))
# dexs_end_date = st.date_input('End date', datetime.date(2023, 12, 31))

# if dexs_start_date > dexs_end_date:
#     st.warning('End date must fall after start date.')

# # Execute the SQL query and display the result
# if st.button("Execute"):
#   if dexs_start_date and dexs_end_date:
#     # Fetching and plotting the data
#     query = QUERY_DEX_USAGE.format(dexs_start_date, dexs_end_date)
#     top_dexs_df = execute_sql_query(query=query)
#     display_interactive_table(data=top_dexs_df)
#   else:
#     st.warning('Please select valid start and end dates.')