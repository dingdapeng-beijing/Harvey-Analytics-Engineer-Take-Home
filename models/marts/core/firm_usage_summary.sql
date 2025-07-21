{{
  config(
    materialized='table',
    tags=['marts', 'core', 'firm_usage_summary']
  )
}}

with firms as (
    select * from {{ ref('stg_firms') }}
),

user_engagement as (
    select * from {{ ref('user_engagement') }}
),

firm_monthly_metrics as (
    select
        f.firm_id,
        f.firm_created_date,
        f.firm_size,
        f.firm_size_category,
        f.arr_in_thousands,
        f.arr_category,
        ue.month,
        
        -- User metrics
        count(distinct ue.user_id) as active_users_count,
        count(distinct case when ue.engagement_level = 'Power User' then ue.user_id end) as power_users_count,
        count(distinct case when ue.engagement_level = 'Active User' then ue.user_id end) as active_users_count_engaged,
        count(distinct case when ue.engagement_level in ('Power User', 'Active User') then ue.user_id end) as engaged_users_count,
        
        -- Usage metrics
        sum(ue.query_count) as total_queries,
        sum(ue.total_documents_processed) as total_documents_processed,
        avg(ue.query_count) as avg_queries_per_user,
        avg(ue.total_documents_processed) as avg_documents_per_user,
        
        -- Event type breakdown
        sum(ue.assistant_queries) as total_assistant_queries,
        sum(ue.vault_queries) as total_vault_queries,
        sum(ue.workflow_queries) as total_workflow_queries,
        
        -- Quality metrics
        avg(ue.avg_feedback_score) as avg_feedback_score,
        sum(ue.high_satisfaction_queries) as total_high_satisfaction_queries,
        sum(ue.low_satisfaction_queries) as total_low_satisfaction_queries,
        
        -- Activity metrics
        max(ue.last_activity_at) as last_firm_activity,
        min(ue.first_activity_at) as first_firm_activity,
        avg(ue.queries_per_active_day) as avg_queries_per_active_day,
        avg(ue.avg_documents_per_query_calc) as avg_documents_per_query
        
    from firms f
    left join user_engagement ue 
        on f.firm_id = ue.firm_id
    group by 1, 2, 3, 4, 5, 6, 7
),

firm_calculations as (
    select
        *,
        
        -- Engagement rates
        case 
            when active_users_count > 0 then 
                round(100.0 * engaged_users_count / active_users_count, 2)
            else 0
        end as user_engagement_rate,
        
        case 
            when active_users_count > 0 then 
                round(100.0 * power_users_count / active_users_count, 2)
            else 0
        end as power_user_rate,
        
        -- Satisfaction rate
        case 
            when total_queries > 0 then 
                round(100.0 * total_high_satisfaction_queries / total_queries, 2)
            else 0
        end as satisfaction_rate,
        
        -- Usage intensity
        case 
            when active_users_count > 0 then 
                round(total_queries::float / active_users_count, 2)
            else 0
        end as queries_per_active_user,
        
        case 
            when active_users_count > 0 then 
                round(total_documents_processed::float / active_users_count, 2)
            else 0
        end as documents_per_active_user,
        
        -- ARR per user
        case 
            when active_users_count > 0 then 
                round(arr_in_thousands::float / active_users_count, 2)
            else 0
        end as arr_per_active_user,
        
        -- Firm health score (composite metric)
        case 
            when active_users_count > 0 and total_queries > 0 then
                round(
                    (user_engagement_rate * 0.3) +
                    (satisfaction_rate * 0.3) +
                    (power_user_rate * 0.2) +
                    (case when queries_per_active_user >= 10 then 20 else queries_per_active_user * 2 end) +
                    (case when arr_per_active_user >= 5 then 20 else arr_per_active_user * 4 end),
                    2
                )
            else 0
        end as firm_health_score
        
    from firm_monthly_metrics
),

final as (
    select
        firm_id,
        firm_created_date,
        firm_size,
        firm_size_category,
        arr_in_thousands,
        arr_category,
        month,
        
        -- User metrics
        active_users_count,
        power_users_count,
        engaged_users_count,
        user_engagement_rate,
        power_user_rate,
        
        -- Usage metrics
        total_queries,
        total_documents_processed,
        queries_per_active_user,
        documents_per_active_user,
        avg_queries_per_active_day,
        avg_documents_per_query,
        
        -- Event type metrics
        total_assistant_queries,
        total_vault_queries,
        total_workflow_queries,
        
        -- Quality metrics
        avg_feedback_score,
        satisfaction_rate,
        
        -- Financial metrics
        arr_per_active_user,
        
        -- Health metrics
        firm_health_score,
        
        -- Activity metrics
        last_firm_activity,
        first_firm_activity,
        
        -- Metadata
        current_timestamp as _loaded_at
        
    from firm_calculations
)

select * from final 