-- Test to ensure critical fields are not null in firm_usage_summary
select *
from {{ ref('firm_usage_summary') }}
where firm_id is null
   or month is null
   or active_users_count is null 