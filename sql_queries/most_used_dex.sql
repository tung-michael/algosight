with top_used_app as (
	select app_id, count(app_id) as times_used
	from appl_usage
	where round_time between '2023-06-01 02:00:00'and '2023-06-02 01:59:58'
	group by app_id
	order by times_used desc
)
select pair, platform, times_used
from dexes join top_used_app on dexes.app_id = top_used_app.app_id
order by times_used desc