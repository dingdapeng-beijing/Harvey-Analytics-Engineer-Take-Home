{{
  config(
    materialized='table',
    description='Cohort analysis base model for user retention analysis by signup month'
  )
}}

WITH user_cohorts AS (
  SELECT
    user_id,
    DATE_TRUNC('month', user_created_date) AS cohort_month,
    user_created_date,
    user_title
  FROM {{ ref('stg_users') }}
),

user_activity AS (
  SELECT
    user_id,
    DATE_TRUNC('month', event_created_at) AS activity_month,
    COUNT(*) AS events_count,
    COUNT(DISTINCT DATE(event_created_at)) AS active_days
  FROM {{ ref('stg_events') }}
  GROUP BY 1, 2
),

cohort_retention AS (
  SELECT
    uc.user_id,
    uc.cohort_month,
    uc.user_title,
    ua.activity_month,
    DATE_DIFF('month', uc.cohort_month, ua.activity_month) AS months_since_signup,
    ua.events_count,
    ua.active_days,
    -- Define retention: user is retained if they have activity in the given month
    CASE WHEN ua.activity_month IS NOT NULL THEN 1 ELSE 0 END AS is_retained,
    -- Define power user retention: user is power user if they meet criteria
    CASE 
      WHEN ua.events_count >= 50 AND ua.active_days >= 15 THEN 1 
      ELSE 0 
    END AS is_power_user_retained
  FROM user_cohorts uc
  LEFT JOIN user_activity ua ON uc.user_id = ua.user_id
),

cohort_summary AS (
  SELECT
    cohort_month,
    user_title,
    months_since_signup,
    COUNT(DISTINCT user_id) AS total_users_in_cohort,
    COUNT(DISTINCT CASE WHEN is_retained = 1 THEN user_id END) AS retained_users,
    COUNT(DISTINCT CASE WHEN is_power_user_retained = 1 THEN user_id END) AS power_users_retained,
    AVG(events_count) AS avg_events_per_user,
    AVG(active_days) AS avg_active_days_per_user,
    -- Retention rate calculation
    ROUND(
      COUNT(DISTINCT CASE WHEN is_retained = 1 THEN user_id END) * 100.0 / 
      COUNT(DISTINCT user_id), 2
    ) AS retention_rate_pct,
    -- Power user retention rate
    ROUND(
      COUNT(DISTINCT CASE WHEN is_power_user_retained = 1 THEN user_id END) * 100.0 / 
      COUNT(DISTINCT user_id), 2
    ) AS power_user_retention_rate_pct
  FROM cohort_retention
  WHERE months_since_signup >= 0  -- Include signup month (month 0)
  GROUP BY 1, 2, 3
)

SELECT
  cohort_month,
  user_title,
  months_since_signup,
  total_users_in_cohort,
  retained_users,
  power_users_retained,
  avg_events_per_user,
  avg_active_days_per_user,
  retention_rate_pct,
  power_user_retention_rate_pct,
  -- Cohort size category for analysis
  CASE 
    WHEN total_users_in_cohort >= 100 THEN 'Large Cohort'
    WHEN total_users_in_cohort >= 50 THEN 'Medium Cohort'
    ELSE 'Small Cohort'
  END AS cohort_size_category,
  -- Retention performance category
  CASE 
    WHEN retention_rate_pct >= 80 THEN 'High Retention'
    WHEN retention_rate_pct >= 60 THEN 'Medium Retention'
    ELSE 'Low Retention'
  END AS retention_performance
FROM cohort_summary
ORDER BY cohort_month DESC, months_since_signup ASC 