-- Test to ensure critical fields are not null in daily_event_summary
select *
from {{ ref('daily_event_summary') }}
where date is null
   or total_events is null
   or unique_users is null 