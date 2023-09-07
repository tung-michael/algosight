CREATE TABLE IF NOT EXISTS appl_usage (
  app_id BIGINT,
  round_time TIMESTAMP,
  related_tx VARCHAR(100),
  inner_tx_level INTEGER
);

CREATE TABLE IF NOT EXISTS asset_usage (
  asset_id BIGINT,
-- amount BIGINT,
  round_time TIMESTAMP,
  related_tx VARCHAR(100),
  inner_tx_level INTEGER
);

CREATE TABLE IF NOT EXISTS dexes (
  pair VARCHAR(100),
  app_id BIGINT,
  platform VARCHAR(100)
);