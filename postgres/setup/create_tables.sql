CREATE TABLE IF NOT EXISTS app_calls (
  app_id BIGINT,
  round_time TIMESTAMP,
  related_tx VARCHAR(100),
  inner_tx_level INTEGER
);

CREATE TABLE IF NOT EXISTS asset_transfer_txns (
  asset_id BIGINT,
  amount NUMERIC,
  round_time TIMESTAMP,
  related_tx VARCHAR(100),
  inner_tx_level INTEGER
);

CREATE TABLE IF NOT EXISTS dexes (
  pair VARCHAR(100),
  app_id BIGINT,
  platform VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS algo_prices (
  as_of_date TIMESTAMP,
  rates_to_usd NUMERIC,
);

CREATE TABLE IF NOT EXISTS hot_tokens (
  asset_id BIGINT,
  decimals INTEGER,
  token_name VARCHAR(100)
);