select app_id, count(app_id) as times_called
from appl_usage
group by app_id
order by times_called desc limit %s