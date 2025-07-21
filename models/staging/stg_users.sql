{{
  config(
    materialized='view',
    tags=['staging', 'users']
  )
}}

with source as (
    select * from {{ ref('analytics_engineer_harvey_mock_data___users_csv') }}
),

cleaned as (
    select
        -- Primary key
        id as user_id,
        
        -- Timestamps
        case 
            when created is not null then cast(created as date)
            else null
        end as user_created_date,
        
        -- User attributes
        title as user_title,
        
        -- Metadata
        'staging' as _source,
        current_timestamp as _loaded_at
        
    from source
    where id is not null  -- Remove records without user_id
)

select * from cleaned 