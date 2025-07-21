{{
  config(
    materialized='table',
    tags=['marts', 'core', 'daily_event_summary']
  )
}}

with user_events as (
    select * from {{ ref('int_user_events') }}
),

daily_metrics as (
    select
        event_date as date,
        
        -- Volume metrics
        count(*) as total_events,
        count(distinct user_id) as unique_users,
        count(distinct firm_id) as unique_firms,
        sum(adjusted_num_docs) as total_documents_processed,
        
        -- Event type breakdown
        count(case when normalized_event_type = 'ASSISTANT' then 1 end) as assistant_events,
        count(case when normalized_event_type = 'VAULT' then 1 end) as vault_events,
        count(case when normalized_event_type = 'WORKFLOW' then 1 end) as workflow_events,
        
        -- Quality metrics
        avg(valid_feedback_score) as avg_feedback_score,
        count(case when valid_feedback_score >= 4 then 1 end) as high_satisfaction_events,
        count(case when valid_feedback_score <= 2 then 1 end) as low_satisfaction_events,
        
        -- Document processing metrics
        avg(adjusted_num_docs) as avg_documents_per_event,
        max(adjusted_num_docs) as max_documents_in_event,
        sum(case when adjusted_num_docs > 10 then 1 end) as high_volume_events,
        
        -- User activity metrics
        count(distinct case when days_since_signup <= 7 then user_id end) as new_users_active,
        count(distinct case when days_since_signup > 30 then user_id end) as established_users_active
        
    from user_events
    group by 1
),

daily_calculations as (
    select
        *,
        
        -- Event type percentages
        case 
            when total_events > 0 then 
                round(100.0 * assistant_events / total_events, 2)
            else 0
        end as assistant_event_pct,
        
        case 
            when total_events > 0 then 
                round(100.0 * vault_events / total_events, 2)
            else 0
        end as vault_event_pct,
        
        case 
            when total_events > 0 then 
                round(100.0 * workflow_events / total_events, 2)
            else 0
        end as workflow_event_pct,
        
        -- Satisfaction rate
        case 
            when total_events > 0 then 
                round(100.0 * high_satisfaction_events / total_events, 2)
            else 0
        end as satisfaction_rate,
        
        -- User engagement rate
        case 
            when unique_users > 0 then 
                round(total_events::float / unique_users, 2)
            else 0
        end as events_per_user,
        
        -- Document processing efficiency
        case 
            when total_events > 0 then 
                round(total_documents_processed::float / total_events, 2)
            else 0
        end as documents_per_event,
        
        -- High volume event rate
        case 
            when total_events > 0 then 
                round(100.0 * high_volume_events / total_events, 2)
            else 0
        end as high_volume_event_rate,
        
        -- User mix
        case 
            when unique_users > 0 then 
                round(100.0 * new_users_active / unique_users, 2)
            else 0
        end as new_user_pct,
        
        case 
            when unique_users > 0 then 
                round(100.0 * established_users_active / unique_users, 2)
            else 0
        end as established_user_pct
        
    from daily_metrics
),

final as (
    select
        date,
        
        -- Volume metrics
        total_events,
        unique_users,
        unique_firms,
        total_documents_processed,
        
        -- Event type metrics
        assistant_events,
        vault_events,
        workflow_events,
        assistant_event_pct,
        vault_event_pct,
        workflow_event_pct,
        
        -- Quality metrics
        avg_feedback_score,
        satisfaction_rate,
        high_satisfaction_events,
        low_satisfaction_events,
        
        -- Processing metrics
        avg_documents_per_event,
        documents_per_event,
        max_documents_in_event,
        high_volume_events,
        high_volume_event_rate,
        
        -- User metrics
        events_per_user,
        new_users_active,
        established_users_active,
        new_user_pct,
        established_user_pct,
        
        -- Metadata
        current_timestamp as _loaded_at
        
    from daily_calculations
    order by date
)

select * from final 