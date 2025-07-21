{{
  config(
    materialized='table',
    description='Event performance metrics by type, user segment, and time for marketing analysis'
  )
}}

-- 1. Create base CTE with all calculations
WITH event_performance AS (
  SELECT
    e.event_id,
    e.event_type,
    e.event_created_at,
    e.num_docs,
    e.feedback_score,
    u.user_id,
    u.user_title,
    u.user_created_date,
    f.firm_id,
    f.firm_size,
    f.arr_in_thousands,
    -- Time-based dimensions
    DATE_TRUNC('month', e.event_created_at) AS event_month,
    DATE_TRUNC('week', e.event_created_at) AS event_week,
    DATE(e.event_created_at) AS event_date,
    -- User tenure at time of event
    DATE_DIFF('day', u.user_created_date, e.event_created_at) AS user_tenure_days,
    -- Event performance indicators
    CASE 
      WHEN e.feedback_score >= 4 THEN 1 
      ELSE 0 
    END AS high_satisfaction_event,
    CASE 
      WHEN e.num_docs >= 10 THEN 1 
      ELSE 0 
    END AS high_volume_event,
    -- User segments
    CASE 
      WHEN DATE_DIFF('day', u.user_created_date, e.event_created_at) <= 7 THEN 'New User'
      WHEN DATE_DIFF('day', u.user_created_date, e.event_created_at) <= 30 THEN 'Recent User'
      WHEN DATE_DIFF('day', u.user_created_date, e.event_created_at) <= 90 THEN 'Established User'
      ELSE 'Long-term User'
    END AS user_segment
  FROM {{ ref('stg_events') }} e
  LEFT JOIN {{ ref('stg_users') }} u ON e.user_id = u.user_id
  LEFT JOIN {{ ref('stg_firms') }} f ON e.firm_id = f.firm_id
),

-- 2. Aggregate by different time dimensions
daily_metrics AS (
  SELECT 'daily' AS time_grain, event_date AS time_period, event_type, user_title, user_segment, COUNT(DISTINCT event_id) AS total_events, COUNT(DISTINCT user_id) AS unique_users, COUNT(DISTINCT firm_id) AS unique_firms, SUM(num_docs) AS total_documents_processed, AVG(num_docs) AS avg_documents_per_event, AVG(feedback_score) AS avg_satisfaction_score, SUM(high_satisfaction_event) AS high_satisfaction_events, SUM(high_volume_event) AS high_volume_events, ROUND(SUM(high_satisfaction_event) * 100.0 / COUNT(*), 2) AS satisfaction_rate_pct, ROUND(SUM(high_volume_event) * 100.0 / COUNT(*), 2) AS high_volume_rate_pct, ROUND(SUM(num_docs) * 1.0 / COUNT(DISTINCT user_id), 2) AS documents_per_user, ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT user_id), 2) AS events_per_user FROM event_performance GROUP BY event_date, event_type, user_title, user_segment
),

weekly_metrics AS (
  SELECT 'weekly' AS time_grain, event_week AS time_period, event_type, user_title, COUNT(DISTINCT event_id) AS total_events, COUNT(DISTINCT user_id) AS unique_users, COUNT(DISTINCT firm_id) AS unique_firms, SUM(num_docs) AS total_documents_processed, AVG(num_docs) AS avg_documents_per_event, AVG(feedback_score) AS avg_satisfaction_score, SUM(high_satisfaction_event) AS high_satisfaction_events, SUM(high_volume_event) AS high_volume_events, ROUND(SUM(high_satisfaction_event) * 100.0 / COUNT(*), 2) AS satisfaction_rate_pct, ROUND(SUM(high_volume_event) * 100.0 / COUNT(*), 2) AS high_volume_rate_pct, LAG(COUNT(*)) OVER (PARTITION BY event_type, user_title ORDER BY event_week) AS prev_week_events, ROUND((COUNT(*) - LAG(COUNT(*)) OVER (PARTITION BY event_type, user_title ORDER BY event_week)) * 100.0 / NULLIF(LAG(COUNT(*)) OVER (PARTITION BY event_type, user_title ORDER BY event_week), 0), 2) AS week_over_week_growth_pct FROM event_performance GROUP BY event_week, event_type, user_title
),

monthly_metrics AS (
  SELECT 'monthly' AS time_grain, event_month AS time_period, event_type, user_title, user_segment, COUNT(DISTINCT event_id) AS total_events, COUNT(DISTINCT user_id) AS unique_users, COUNT(DISTINCT firm_id) AS unique_firms, SUM(num_docs) AS total_documents_processed, AVG(num_docs) AS avg_documents_per_event, AVG(feedback_score) AS avg_satisfaction_score, SUM(high_satisfaction_event) AS high_satisfaction_events, SUM(high_volume_event) AS high_volume_events, ROUND(SUM(high_satisfaction_event) * 100.0 / COUNT(*), 2) AS satisfaction_rate_pct, ROUND(SUM(high_volume_event) * 100.0 / COUNT(*), 2) AS high_volume_rate_pct, ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT user_id), 2) AS events_per_user, ROUND(SUM(num_docs) * 1.0 / COUNT(DISTINCT user_id), 2) AS documents_per_user, CASE WHEN AVG(feedback_score) >= 4.5 THEN 'Excellent' WHEN AVG(feedback_score) >= 4.0 THEN 'Good' WHEN AVG(feedback_score) >= 3.5 THEN 'Fair' ELSE 'Needs Improvement' END AS satisfaction_performance, CASE WHEN COUNT(*) >= 1000 THEN 'High Volume' WHEN COUNT(*) >= 500 THEN 'Medium Volume' WHEN COUNT(*) >= 100 THEN 'Low Volume' ELSE 'Minimal Volume' END AS volume_performance FROM event_performance GROUP BY event_month, event_type, user_title, user_segment
)

-- 3. Combine all aggregations
SELECT * FROM daily_metrics
UNION ALL
SELECT * FROM weekly_metrics
UNION ALL
SELECT * FROM monthly_metrics

ORDER BY time_grain, time_period DESC, total_events DESC 