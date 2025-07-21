{{
  config(
    materialized='table',
    description='User acquisition metrics by firm and user title for marketing analysis'
  )
}}

WITH user_acquisition AS (
  SELECT
    u.user_id,
    u.user_title,
    u.user_created_date,
    f.firm_id,
    f.firm_size,
    f.arr_in_thousands,
    -- Acquisition month for cohort analysis
    DATE_TRUNC('month', u.user_created_date) AS acquisition_month,
    -- User's first activity
    MIN(e.event_created_at) AS first_activity_date,
    -- Time to first activity (in days)
    DATE_DIFF('day', u.user_created_date, MIN(e.event_created_at)) AS days_to_first_activity,
    -- Initial engagement metrics
    COUNT(DISTINCT e.event_id) AS total_events,
    COUNT(DISTINCT DATE(e.event_created_at)) AS active_days,
    AVG(e.feedback_score) AS avg_satisfaction_score,
    SUM(e.num_docs) AS total_documents_processed
  FROM {{ ref('stg_users') }} u
  LEFT JOIN {{ ref('stg_firms') }} f ON u.firm_id = f.firm_id
  LEFT JOIN {{ ref('stg_events') }} e ON u.user_id = e.user_id
  GROUP BY 1, 2, 3, 4, 5, 6, 7
),

acquisition_summary AS (
  SELECT
    acquisition_month,
    user_title,
    firm_size,
    arr_in_thousands,
    COUNT(DISTINCT user_id) AS new_users_acquired,
    COUNT(DISTINCT firm_id) AS new_firms_acquired,
    -- Conversion metrics
    COUNT(DISTINCT CASE WHEN first_activity_date IS NOT NULL THEN user_id END) AS activated_users,
    COUNT(DISTINCT CASE WHEN days_to_first_activity <= 7 THEN user_id END) AS quick_start_users,
    COUNT(DISTINCT CASE WHEN days_to_first_activity <= 30 THEN user_id END) AS monthly_activated_users,
    -- Engagement metrics
    AVG(total_events) AS avg_events_per_user,
    AVG(active_days) AS avg_active_days_per_user,
    AVG(avg_satisfaction_score) AS avg_satisfaction_score,
    AVG(total_documents_processed) AS avg_documents_per_user,
    -- Conversion rates
    ROUND(
      COUNT(DISTINCT CASE WHEN first_activity_date IS NOT NULL THEN user_id END) * 100.0 / 
      COUNT(DISTINCT user_id), 2
    ) AS activation_rate_pct,
    ROUND(
      COUNT(DISTINCT CASE WHEN days_to_first_activity <= 7 THEN user_id END) * 100.0 / 
      COUNT(DISTINCT user_id), 2
    ) AS quick_start_rate_pct,
    -- Firm size categories for analysis
    CASE 
      WHEN firm_size >= 500 THEN 'Enterprise'
      WHEN firm_size >= 200 THEN 'Large'
      WHEN firm_size >= 100 THEN 'Medium'
      ELSE 'Small'
    END AS firm_size_category,
    -- ARR categories
    CASE 
      WHEN arr_in_thousands >= 500 THEN 'High Value'
      WHEN arr_in_thousands >= 200 THEN 'Medium Value'
      WHEN arr_in_thousands >= 100 THEN 'Low Value'
      ELSE 'Minimal Value'
    END AS arr_category
  FROM user_acquisition
  GROUP BY 1, 2, 3, 4
)

SELECT
  acquisition_month,
  user_title,
  firm_size,
  arr_in_thousands,
  firm_size_category,
  arr_category,
  new_users_acquired,
  new_firms_acquired,
  activated_users,
  quick_start_users,
  monthly_activated_users,
  avg_events_per_user,
  avg_active_days_per_user,
  avg_satisfaction_score,
  avg_documents_per_user,
  activation_rate_pct,
  quick_start_rate_pct,
  -- Performance indicators
  CASE 
    WHEN activation_rate_pct >= 80 THEN 'Excellent'
    WHEN activation_rate_pct >= 60 THEN 'Good'
    WHEN activation_rate_pct >= 40 THEN 'Fair'
    ELSE 'Needs Improvement'
  END AS activation_performance,
  CASE 
    WHEN avg_satisfaction_score >= 4.5 THEN 'High Satisfaction'
    WHEN avg_satisfaction_score >= 4.0 THEN 'Good Satisfaction'
    WHEN avg_satisfaction_score >= 3.5 THEN 'Fair Satisfaction'
    ELSE 'Low Satisfaction'
  END AS satisfaction_performance
FROM acquisition_summary
ORDER BY acquisition_month DESC, new_users_acquired DESC 