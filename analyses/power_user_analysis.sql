-- Analysis: Power User Definition and Characteristics
-- This analysis explores what defines a power user and their key characteristics

with user_engagement as (
    select * from {{ ref('user_engagement') }}
),

power_user_metrics as (
    select
        engagement_level,
        count(distinct user_id) as user_count,
        avg(query_count) as avg_queries,
        avg(active_days) as avg_active_days,
        avg(satisfaction_rate) as avg_satisfaction,
        avg(avg_feedback_score) as avg_feedback,
        avg(queries_per_active_day) as avg_queries_per_day,
        avg(avg_documents_per_query_calc) as avg_docs_per_query,
        
        -- Power user specific metrics
        count(case when engagement_level = 'Power User' then user_id end) as power_users,
        count(case when engagement_level = 'Active User' then user_id end) as active_users,
        count(case when engagement_level = 'Regular User' then user_id end) as regular_users,
        count(case when engagement_level = 'Occasional User' then user_id end) as occasional_users
        
    from user_engagement
    group by 1
),

power_user_characteristics as (
    select
        'Power User Characteristics' as analysis_type,
        'Based on current classification: 50+ queries AND 15+ active days per month' as definition,
        power_users as total_power_users,
        round(100.0 * power_users / (power_users + active_users + regular_users + occasional_users), 2) as power_user_percentage,
        avg_queries as avg_queries_for_power_users,
        avg_active_days as avg_active_days_for_power_users,
        avg_satisfaction as avg_satisfaction_for_power_users,
        avg_feedback as avg_feedback_for_power_users,
        avg_queries_per_day as avg_queries_per_day_for_power_users,
        avg_docs_per_query as avg_docs_per_query_for_power_users
        
    from power_user_metrics
    where engagement_level = 'Power User'
),

alternative_definitions as (
    select
        'Alternative Power User Definitions' as analysis_type,
        'High Volume: 30+ queries per month' as definition_1,
        'High Frequency: 20+ active days per month' as definition_2,
        'High Satisfaction: 90%+ satisfaction rate' as definition_3,
        'High Efficiency: 15+ documents per query' as definition_4,
        'Composite: 25+ queries AND 10+ active days AND 80%+ satisfaction' as definition_5
)

select * from power_user_characteristics
union all
select * from alternative_definitions 