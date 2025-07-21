{{
  config(
    materialized='table',
    description='Base user acquisition data model for individual user acquisition analysis'
  )
}}

WITH user_acquisition_base AS (
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
    SUM(e.num_docs) AS total_documents_processed,
    -- Activation flags
    CASE WHEN MIN(e.event_created_at) IS NOT NULL THEN 1 ELSE 0 END AS is_activated,
    CASE 
      WHEN DATE_DIFF('day', u.user_created_date, MIN(e.event_created_at)) <= 7 THEN 1 
      ELSE 0 
    END AS is_quick_start,
    CASE 
      WHEN DATE_DIFF('day', u.user_created_date, MIN(e.event_created_at)) <= 30 THEN 1 
      ELSE 0 
    END AS is_monthly_activated,
    -- Firm size categories
    CASE 
      WHEN f.firm_size >= 500 THEN 'Enterprise'
      WHEN f.firm_size >= 200 THEN 'Large'
      WHEN f.firm_size >= 100 THEN 'Medium'
      ELSE 'Small'
    END AS firm_size_category,
    -- ARR categories
    CASE 
      WHEN f.arr_in_thousands >= 500 THEN 'High Value'
      WHEN f.arr_in_thousands >= 200 THEN 'Medium Value'
      WHEN f.arr_in_thousands >= 100 THEN 'Low Value'
      ELSE 'Minimal Value'
    END AS arr_category
  FROM {{ ref('stg_users') }} u
  LEFT JOIN {{ ref('stg_firms') }} f ON u.firm_id = f.firm_id
  LEFT JOIN {{ ref('stg_events') }} e ON u.user_id = e.user_id
  GROUP BY 1, 2, 3, 4, 5, 6
)

SELECT
  user_id,
  user_title,
  user_created_date,
  firm_id,
  firm_size,
  arr_in_thousands,
  acquisition_month,
  first_activity_date,
  days_to_first_activity,
  total_events,
  active_days,
  avg_satisfaction_score,
  total_documents_processed,
  is_activated,
  is_quick_start,
  is_monthly_activated,
  firm_size_category,
  arr_category,
  -- Performance indicators
  CASE 
    WHEN is_activated = 1 AND days_to_first_activity <= 1 THEN 'Immediate Activation'
    WHEN is_activated = 1 AND days_to_first_activity <= 7 THEN 'Quick Activation'
    WHEN is_activated = 1 AND days_to_first_activity <= 30 THEN 'Standard Activation'
    WHEN is_activated = 1 THEN 'Delayed Activation'
    ELSE 'Not Activated'
  END AS activation_category,
  CASE 
    WHEN avg_satisfaction_score >= 4.5 THEN 'High Satisfaction'
    WHEN avg_satisfaction_score >= 4.0 THEN 'Good Satisfaction'
    WHEN avg_satisfaction_score >= 3.5 THEN 'Fair Satisfaction'
    WHEN avg_satisfaction_score IS NOT NULL THEN 'Low Satisfaction'
    ELSE 'No Feedback'
  END AS satisfaction_category
FROM user_acquisition_base
ORDER BY user_created_date DESC, user_id 