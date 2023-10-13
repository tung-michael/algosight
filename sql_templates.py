
################### Overview page ########################
# Top Used Dexs
QUERY_TOP_DEXS = """
SELECT
    APP_ID,
    PLATFORM,
    COUNT(APP_ID) AS TOTAL_TX_COUNTS
  FROM TXNS_ON_DEXS
  WHERE TX_DATE BETWEEN '{start_date}' AND '{end_date}'
	GROUP BY APP_ID, PLATFORM
ORDER BY TOTAL_TX_COUNTS DESC LIMIT 10
"""

# Top Traded Tokens
QUERY_TOP_TOKENS = """
SELECT
    ASSET_ID,
    TOKEN_NAME,
    COUNT(ASSET_ID) AS TOTAL_TX_COUNTS
  FROM TXNS_OF_HOT_TOKENS
  WHERE TX_DATE BETWEEN '{start_date}' AND '{end_date}'
	GROUP BY ASSET_ID, TOKEN_NAME
ORDER BY TOTAL_TX_COUNTS DESC LIMIT 10
"""

################### Hot DEXs page ########################

# Compare Dexs Usage
QUERY_DEX_USAGE = """
SELECT
    APP_ID,
    PLATFORM,
    TX_DATE,
    COUNT(APP_ID) AS DAILY_TX_COUNTS
  FROM TXNS_ON_DEXS
  WHERE
    TX_DATE BETWEEN '{start_date}' AND '{end_date}'
	GROUP BY APP_ID, PLATFORM, TX_DATE
ORDER BY TX_DATE ASC
"""

# Hot DEX Platforms by Trading Volume
QUERY_DEX_TRADING_VOLUME = """

"""


################### Tokens page ########################

# Compare Token(s) Usage during a Time Period
QUERY_TOKEN_USAGE = """
SELECT
    ASSET_ID,
    TOKEN_NAME,
    TX_DATE,
    COUNT(ASSET_ID) AS DAILY_TX_COUNTS
  FROM TXNS_OF_HOT_TOKENS
  WHERE
    TX_DATE BETWEEN '{start_date}' AND '{end_date}'
	GROUP BY ASSET_ID, TOKEN_NAME, TX_DATE
ORDER BY TX_DATE ASC
"""

# Hot Tokens by Trading Volume during a Time Period
QUERY_TOKEN_TRADING_VOLUME = """

"""


# Might be used for both trading volume treemap?
QUERY_TRADING_VOLUME = """
WITH TXNS_TOKENS_DEXS AS
	(SELECT PLATFORM,
			TXNS_ON_DEXS.TX_DATE,
			TOKEN_NAME,
			SUM(AMOUNT) AS TX_AMOUNT,
			DECIMALS
		FROM TXNS_OF_HOT_TOKENS
		JOIN TXNS_ON_DEXS ON TXNS_OF_HOT_TOKENS.RELATED_TX = TXNS_ON_DEXS.RELATED_TX

	 	WHERE TXNS_ON_DEXS.TX_DATE BETWEEN '{start_date}' AND '{end_date}'

	 	GROUP BY PLATFORM,
			TOKEN_NAME,
			TXNS_ON_DEXS.TX_DATE,
			DECIMALS
		ORDER BY TX_DATE ASC, PLATFORM,
			TOKEN_NAME),
	TRANSACTION_VOLUME AS
	(SELECT PLATFORM,
			TX_DATE,
			TOKEN_NAME,
			TX_AMOUNT / POWER(10,DECIMALS) AS TRADING_AMOUNT
		FROM TXNS_TOKENS_DEXS)
SELECT PLATFORM,
	TX_DATE,
	TOKEN_PRICES.TOKEN_NAME,
	TRADING_AMOUNT,
	RATES_TO_USD,
	TRADING_AMOUNT * RATES_TO_USD AS TRADING_VOLUME_USD
FROM TRANSACTION_VOLUME
JOIN TOKEN_PRICES ON TRANSACTION_VOLUME.TX_DATE = TOKEN_PRICES.AS_OF_DATE
AND TRANSACTION_VOLUME.TOKEN_NAME = TOKEN_PRICES.TOKEN_NAME
"""

# This query can be used for both "tokens per dex" and "dexs per token" computation
QUERY_DETAILED_TX_COUNTS = """
SELECT
    TOKEN_NAME,
	  PLATFORM,
    TXNS_OF_HOT_TOKENS.TX_DATE,
    COUNT(*) AS DAILY_TX_COUNTS
  FROM TXNS_OF_HOT_TOKENS JOIN TXNS_ON_DEXS
  	ON TXNS_OF_HOT_TOKENS.RELATED_TX = TXNS_ON_DEXS.RELATED_TX
  WHERE
    TXNS_OF_HOT_TOKENS.TX_DATE BETWEEN '{start_date}' AND '{end_date}'
GROUP BY TOKEN_NAME,PLATFORM, TXNS_OF_HOT_TOKENS.TX_DATE
ORDER BY TX_DATE ASC, TOKEN_NAME, PLATFORM
"""


# previous version QUERY_TRADING_VOLUME
"""
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