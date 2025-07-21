{{
  config(
    materialized='table',
    tags=['marts', 'core', 'user_engagement'],
    description='User engagement metrics with comprehensive definitions for satisfaction scores, engagement levels, and activity metrics'
  )
}}

/*
METRIC DEFINITIONS:

1. SATISFACTION SCORES:
   - Source: feedback_score from events table (1-5 scale)
   - High Satisfaction: feedback_score >= 4 (80%+ satisfaction rate)
   - Low Satisfaction: feedback_score <= 2 (40% or lower satisfaction rate)
   - avg_feedback_score: Average of all valid feedback scores per user per month
   - satisfaction_rate: Percentage of queries with high satisfaction scores

2. ENGAGEMENT LEVELS:
   - Power User: 50+ queries AND 15+ active days per month
   - Active User: 20+ queries AND 8+ active days per month  
   - Regular User: 5+ queries AND 3+ active days per month
   - Occasional User: 1+ queries (any activity)
   - Inactive: No queries in the month

3. ACTIVITY METRICS:
   - query_count: Total number of events/queries in the month
   - active_days: Number of unique days with activity
   - queries_per_active_day: Average queries per active day
   - last_activity_at: Most recent event timestamp
   - first_activity_at: First event timestamp in the month

4. DOCUMENT PROCESSING:
   - total_documents_processed: Sum of num_docs across all events
   - avg_documents_per_query: Average documents processed per event
   - max_documents_in_query: Highest document count in a single event

5. EVENT TYPE BREAKDOWN:
   - assistant_queries: Count of ASSISTANT event types
   - vault_queries: Count of VAULT event types
   - workflow_queries: Count of WORKFLOW event types
*/

with user_events as (
    select * from {{ ref('int_user_events') }}
),

user_monthly_metrics as (
    select
        user_id,
        firm_id,
        user_title,
        event_month as month,
        
        -- Usage metrics
        count(*) as query_count,
        count(distinct event_date) as active_days,
        sum(adjusted_num_docs) as total_documents_processed,
        
        -- Event type breakdown
        count(case when normalized_event_type = 'ASSISTANT' then 1 end) as assistant_queries,
        count(case when normalized_event_type = 'VAULT' then 1 end) as vault_queries,
        count(case when normalized_event_type = 'WORKFLOW' then 1 end) as workflow_queries,
        
        -- Quality metrics
        avg(valid_feedback_score) as avg_feedback_score,
        count(case when valid_feedback_score >= 4 then 1 end) as high_satisfaction_queries,
        count(case when valid_feedback_score <= 2 then 1 end) as low_satisfaction_queries,
        
        -- Activity metrics
        max(event_created_at) as last_activity_at,
        min(event_created_at) as first_activity_at,
        avg(days_since_signup) as avg_days_since_signup,
        
        -- Document processing efficiency
        avg(adjusted_num_docs) as avg_documents_per_query,
        max(adjusted_num_docs) as max_documents_in_query
        
    from user_events
    group by 1, 2, 3, 4
),

engagement_calculation as (
    select
        *,
        
        -- Engagement level classification
        case 
            when query_count >= 50 and active_days >= 15 then 'Power User'
            when query_count >= 20 and active_days >= 8 then 'Active User'
            when query_count >= 5 and active_days >= 3 then 'Regular User'
            when query_count >= 1 then 'Occasional User'
            else 'Inactive'
        end as engagement_level,
        
        -- Satisfaction rate
        case 
            when query_count > 0 then 
                round(100.0 * high_satisfaction_queries / query_count, 2)
            else 0
        end as satisfaction_rate,
        
        -- Activity frequency
        case 
            when active_days > 0 then 
                round(query_count::float / active_days, 2)
            else 0
        end as queries_per_active_day,
        
        -- Document processing rate
        case 
            when query_count > 0 then 
                round(total_documents_processed::float / query_count, 2)
            else 0
        end as avg_documents_per_query_calc
        
    from user_monthly_metrics
),

final as (
    select
        user_id,
        firm_id,
        user_title,
        month,
        
        -- Core metrics
        query_count,
        active_days,
        total_documents_processed,
        
        -- Event type metrics
        assistant_queries,
        vault_queries,
        workflow_queries,
        
        -- Quality metrics
        avg_feedback_score,
        high_satisfaction_queries,
        low_satisfaction_queries,
        satisfaction_rate,
        
        -- Activity metrics
        last_activity_at,
        first_activity_at,
        queries_per_active_day,
        avg_documents_per_query_calc,
        
        -- Classification
        engagement_level,
        
        -- Metadata
        current_timestamp as _loaded_at
        
    from engagement_calculation
)

select * from final 