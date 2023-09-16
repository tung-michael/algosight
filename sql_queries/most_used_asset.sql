select asset_id, count(asset_id) as times_used, sum(amount) as total_traded_volume
from asset_usage
  join asset_prices on asset_usage.asset_id = asset_prices.asset_id
group by asset_id
order by times_used desc limit %s