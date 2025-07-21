-- Test to ensure critical fields are not null in user_engagement
select *
from {{ ref('user_engagement') }}
where user_id is null
   or firm_id is null
   or month is null
   or query_count is null 