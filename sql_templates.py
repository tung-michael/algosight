
################### Overview page ########################
# Top Used Dexs
QUERY_TOP_DEXS = """
SELECT
    APP_ID,
    PLATFORM,
    COUNT(APP_ID) AS TRADING_FREQUENCY
  FROM TXNS_ON_DEXS
  WHERE TX_DATE BETWEEN '{start_date}' AND '{end_date}'
	GROUP BY APP_ID, PLATFORM
ORDER BY TRADING_FREQUENCY DESC LIMIT 10
"""

# Top Traded Tokens
QUERY_TOP_TOKENS = """
SELECT
    ASSET_ID,
    TOKEN_NAME,
    COUNT(ASSET_ID) AS TRADING_FREQUENCY
  FROM TXNS_OF_HOT_TOKENS
  WHERE TX_DATE BETWEEN '{start_date}' AND '{end_date}'
	GROUP BY ASSET_ID, TOKEN_NAME
ORDER BY TRADING_FREQUENCY DESC LIMIT 10
"""

################### Hot DEXs page ########################

# Compare Dexs Usage
QUERY_DEX_USAGE = """
SELECT
    APP_ID,
    PLATFORM,
    TX_DATE,
    COUNT(APP_ID) AS TRADING_FREQUENCY
  FROM TXNS_ON_DEXS
  WHERE
    TX_DATE BETWEEN '{start_date}' AND '{end_date}'
	GROUP BY APP_ID, PLATFORM, TX_DATE
ORDER BY TX_DATE ASC
"""

# Hot DEX Platforms by Trading Volume
QUERY_DEX_TRADING_VOLUME = """

"""


################### Hot Tokens page ########################

# Compare Token(s) Usage during a Time Period
QUERY_TOKEN_USAGE = """
SELECT
    ASSET_ID,
    TOKEN_NAME,
    TX_DATE,
    COUNT(ASSET_ID) AS TRADING_FREQUENCY
  FROM TXNS_OF_HOT_TOKENS
  WHERE
    TX_DATE BETWEEN '{start_date}' AND '{end_date}'
	GROUP BY ASSET_ID, TOKEN_NAME, TX_DATE
ORDER BY TX_DATE ASC
"""

# Hot Tokens by Trading Volume during a Time Period
QUERY_TOKEN_TRADING_VOLUME = """

"""


# Might be used for both trading volume plot?
QUERY_TRADING_VOLUME = """
with dexs_tokens_trading as (
	select
	platform, txns_on_dexs.tx_date,
	token_name, sum(amount) as total_trading, decimals
	from txns_of_hot_tokens join  txns_on_dexs
		on txns_of_hot_tokens.related_tx = txns_on_dexs.related_tx
--	where tx_date between '2023-06-01' and '2023-06-08'
	group by platform, token_name,txns_on_dexs.tx_date, decimals
	order by tx_date ASC, platform, token_name
)
select platform, tx_date,
	token_name,
	case
		when decimals =0 then total_trading
		else total_trading / decimals
	end as trading_volume
	from dexs_tokens_trading
"""
