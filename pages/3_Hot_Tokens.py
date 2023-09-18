from analytical_scripts import user_date_input, execute_button
import streamlit as st


# Compare Token(s) Usage during a Time Period
QUERY_TOKEN_USAGE = """
SELECT
	ASSET_ID,
	TX_DATE,
	COUNT(ASSET_ID) AS TRADING_FREQUENCY
  FROM TXNS_OF_HOT_TOKENS
  WHERE
    TX_DATE BETWEEN {start_date} AND {end_date}
  	AND ASSET_ID IN (SELECT ASSET_ID FROM HOT_TOKENS)
	GROUP BY ASSET_ID, TX_DATE
ORDER BY TX_DATE ASC
"""


st.title("Put something creative here")

# Hot Tokens by Trading Volume during a Time Period

