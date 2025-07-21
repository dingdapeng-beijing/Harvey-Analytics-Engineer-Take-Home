-- Analysis: Data Quality Issues and Anomalies
-- This analysis identifies potential data quality concerns in the Harvey dataset

with users as (
    select * from {{ ref('stg_users') }}
),

firms as (
    select * from {{ ref('stg_firms') }}
),

events as (
    select * from {{ ref('stg_events') }}
),

-- Data completeness analysis
completeness_issues as (
    select
        'Data Completeness Issues' as issue_category,
        'Missing user titles' as issue_description,
        count(*) as issue_count,
        round(100.0 * count(*) / (select count(*) from users), 2) as percentage_affected
    from users
    where user_title is null or user_title = ''
    
    union all
    
    select
        'Data Completeness Issues' as issue_category,
        'Missing firm creation dates' as issue_description,
        count(*) as issue_count,
        round(100.0 * count(*) / (select count(*) from firms), 2) as percentage_affected
    from firms
    where firm_created_date is null
    
    union all
    
    select
        'Data Completeness Issues' as issue_category,
        'Missing feedback scores' as issue_description,
        count(*) as issue_count,
        round(100.0 * count(*) / (select count(*) from events), 2) as percentage_affected
    from events
    where valid_feedback_score is null
),

-- Data consistency analysis
consistency_issues as (
    select
        'Data Consistency Issues' as issue_category,
        'Events before user creation' as issue_description,
        count(*) as issue_count,
        round(100.0 * count(*) / (select count(*) from events), 2) as percentage_affected
    from events e
    join users u on e.user_id = u.user_id
    where e.event_created_at < u.user_created_date
    
    union all
    
    select
        'Data Consistency Issues' as issue_category,
        'Invalid feedback scores (outside 1-5 range)' as issue_description,
        count(*) as issue_count,
        round(100.0 * count(*) / (select count(*) from events), 2) as percentage_affected
    from events
    where feedback_score not between 1 and 5
    
    union all
    
    select
        'Data Consistency Issues' as issue_category,
        'Zero or negative document counts' as issue_description,
        count(*) as issue_count,
        round(100.0 * count(*) / (select count(*) from events), 2) as percentage_affected
    from events
    where num_docs <= 0
),

-- Data anomaly analysis
anomaly_issues as (
    select
        'Data Anomalies' as issue_category,
        'Extremely high document counts (>100)' as issue_description,
        count(*) as issue_count,
        round(100.0 * count(*) / (select count(*) from events), 2) as percentage_affected
    from events
    where num_docs > 100
    
    union all
    
    select
        'Data Anomalies' as issue_category,
        'Users with no events' as issue_description,
        count(*) as issue_count,
        round(100.0 * count(*) / (select count(*) from users), 2) as percentage_affected
    from users u
    left join events e on u.user_id = e.user_id
    where e.user_id is null
    
    union all
    
    select
        'Data Anomalies' as issue_category,
        'Firms with no users' as issue_description,
        count(*) as issue_count,
        round(100.0 * count(*) / (select count(*) from firms), 2) as percentage_affected
    from firms f
    left join events e on f.firm_id = e.firm_id
    where e.firm_id is null
),

-- Business logic issues
business_logic_issues as (
    select
        'Business Logic Issues' as issue_category,
        'Firms with zero ARR' as issue_description,
        count(*) as issue_count,
        round(100.0 * count(*) / (select count(*) from firms), 2) as percentage_affected
    from firms
    where arr_in_thousands = 0
    
    union all
    
    select
        'Business Logic Issues' as issue_category,
        'Firms with zero employees' as issue_description,
        count(*) as issue_count,
        round(100.0 * count(*) / (select count(*) from firms), 2) as percentage_affected
    from firms
    where firm_size = 0
    
    union all
    
    select
        'Business Logic Issues' as issue_category,
        'Users created in future dates' as issue_description,
        count(*) as issue_count,
        round(100.0 * count(*) / (select count(*) from users), 2) as percentage_affected
    from users
    where user_created_date > current_date
)

-- Combine all issues
select * from completeness_issues
union all
select * from consistency_issues
union all
select * from anomaly_issues
union all
select * from business_logic_issues
order by issue_category, issue_description 