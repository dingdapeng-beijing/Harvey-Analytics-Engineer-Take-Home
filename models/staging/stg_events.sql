{{
  config(
    materialized='view',
    tags=['staging', 'events']
  )
}}

with source as (
    select * from {{ ref('analytics_engineer_harvey_mock_data___events_csv') }}
),

cleaned as (
    select
        -- Primary key (composite)
        firm_id,
        user_id,
        
        -- Timestamps
        case 
            when created is not null then cast(created as timestamp)
            else null
        end as event_created_at,
        
        -- Event attributes
        event_type,
        num_docs,
        feedback_score,
        
        -- Derived fields
        case 
            when event_type in ('ASSISTANT', 'VAULT', 'WORKFLOW') then event_type
            else 'OTHER'
        end as normalized_event_type,
        
        case 
            when feedback_score between 1 and 5 then feedback_score
            else null
        end as valid_feedback_score,
        
        case 
            when num_docs > 0 then num_docs
            else 1  -- Default to 1 if no documents specified
        end as adjusted_num_docs,
        
        -- Metadata
        'staging' as _source,
        current_timestamp as _loaded_at
        
    from source
    where firm_id is not null 
      and user_id is not null  -- Remove records without required keys
      and created is not null  -- Remove records without timestamps
)

select * from cleaned 