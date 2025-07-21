{{
  config(
    materialized='view',
    tags=['intermediate', 'user_events']
  )
}}

with users as (
    select * from {{ ref('stg_users') }}
),

events as (
    select * from {{ ref('stg_events') }}
),

user_events_joined as (
    select
        e.firm_id,
        e.user_id,
        u.user_title,
        u.user_created_date,
        e.event_created_at,
        e.event_type,
        e.normalized_event_type,
        e.num_docs,
        e.adjusted_num_docs,
        e.feedback_score,
        e.valid_feedback_score,
        
        -- Time-based fields
        date_trunc('month', e.event_created_at) as event_month,
        date_trunc('day', e.event_created_at) as event_date,
        
        -- User tenure
        date_diff('day', u.user_created_date, e.event_created_at) as days_since_signup,
        
        -- Metadata
        e._source,
        e._loaded_at
        
    from events e
    left join users u 
        on e.user_id = u.user_id
    where e.event_created_at >= u.user_created_date  -- Ensure events are after user creation
)

select * from user_events_joined 