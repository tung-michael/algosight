select asset_id, count(asset_id) as times_used, sum(amount) as total_traded_volume
from asset_usage
group by asset_id
order by times_used desc limit %s