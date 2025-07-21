{{
  config(
    materialized='view',
    tags=['staging', 'firms']
  )
}}

with source as (
    select * from {{ ref('analytics_engineer_harvey_mock_data___firms_csv') }}
),

cleaned as (
    select
        -- Primary key
        id as firm_id,
        
        -- Timestamps
        case 
            when created is not null then cast(created as date)
            else null
        end as firm_created_date,
        
        -- Firm attributes
        firm_size,
        arr_in_thousands,
        
        -- Derived fields
        case 
            when firm_size < 100 then 'Small'
            when firm_size between 100 and 500 then 'Medium'
            else 'Large'
        end as firm_size_category,
        
        case 
            when arr_in_thousands < 100 then 'Low'
            when arr_in_thousands between 100 and 300 then 'Medium'
            else 'High'
        end as arr_category,
        
        -- Metadata
        'staging' as _source,
        current_timestamp as _loaded_at
        
    from source
    where id is not null  -- Remove records without firm_id
)

select * from cleaned 