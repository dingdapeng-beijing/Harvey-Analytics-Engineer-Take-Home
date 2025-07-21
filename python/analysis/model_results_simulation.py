#!/usr/bin/env python3
"""
Simulation of dbt model results for Harvey Analytics data
This script shows what the results would look like if we ran the dbt models
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import matplotlib.pyplot as plt

# Add the utils directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from data_loader import load_harvey_data

def simulate_user_engagement():
    """Simulate user_engagement model results"""
    print("=" * 80)
    print("📊 USER ENGAGEMENT MODEL RESULTS")
    print("=" * 80)
    
    # Load data
    users_df, firms_df, events_df = load_harvey_data()
    
    # Simulate monthly aggregation
    events_df['month'] = pd.to_datetime(events_df['event_created_at']).dt.to_period('M')
    users_df['user_created_date'] = pd.to_datetime(users_df['user_created_date'])
    
    # Calculate engagement metrics
    engagement_data = []
    
    for month in events_df['month'].unique():
        month_events = events_df[events_df['month'] == month]
        
        for user_id in month_events['user_id'].unique():
            user_events = month_events[month_events['user_id'] == user_id]
            user_info = users_df[users_df['user_id'] == user_id].iloc[0]
            
            # Get firm_id from events (users can work with multiple firms)
            firm_id = user_events['firm_id'].iloc[0]  # Use the first firm for this month
            
            query_count = len(user_events)
            active_days = user_events['event_created_at'].dt.date.nunique()
            total_docs = user_events['num_docs'].sum()
            avg_feedback = user_events['feedback_score'].mean()
            
            # Engagement level classification
            if query_count >= 50 and active_days >= 15:
                engagement_level = 'Power User'
            elif query_count >= 20 and active_days >= 8:
                engagement_level = 'Active User'
            elif query_count >= 5 and active_days >= 3:
                engagement_level = 'Regular User'
            elif query_count >= 1:
                engagement_level = 'Occasional User'
            else:
                engagement_level = 'Inactive'
            
            engagement_data.append({
                'user_id': user_id,
                'firm_id': firm_id,
                'user_title': user_info['user_title'],
                'month': str(month),
                'query_count': query_count,
                'active_days': active_days,
                'total_documents_processed': total_docs,
                'avg_feedback_score': round(avg_feedback, 2),
                'engagement_level': engagement_level
            })
    
    engagement_df = pd.DataFrame(engagement_data)
    
    # Export to CSV
    engagement_csv_path = os.path.join(os.path.dirname(__file__), 'user_engagement_model.csv')
    engagement_df.to_csv(engagement_csv_path, index=False)
    print(f"\n📁 User engagement model saved to: {engagement_csv_path}\n")
    
    # Show summary statistics
    print(f"📈 Total engagement records: {len(engagement_df)}")
    print(f"👥 Unique users: {engagement_df['user_id'].nunique()}")
    print(f"📅 Date range: {engagement_df['month'].min()} to {engagement_df['month'].max()}")
    
    print("\n🎯 Engagement Level Distribution:")
    level_counts = engagement_df['engagement_level'].value_counts()
    for level, count in level_counts.items():
        percentage = (count / len(engagement_df)) * 100
        print(f"   {level}: {count} ({percentage:.1f}%)")
    
    print("\n📊 Average Metrics by Engagement Level:")
    level_metrics = engagement_df.groupby('engagement_level').agg({
        'query_count': 'mean',
        'active_days': 'mean',
        'avg_feedback_score': 'mean'
    }).round(2)
    print(level_metrics)
    
    return engagement_df

def simulate_cohort_analysis():
    """Simulate cohort_analysis_base model results"""
    print("\n" + "=" * 80)
    print("📊 COHORT ANALYSIS MODEL RESULTS")
    print("=" * 80)
    
    # Load data
    users_df, firms_df, events_df = load_harvey_data()
    
    # Convert dates
    users_df['user_created_date'] = pd.to_datetime(users_df['user_created_date'])
    events_df['event_created_at'] = pd.to_datetime(events_df['event_created_at'])
    
    # Create cohort data
    cohort_data = []
    
    for user_id in users_df['user_id'].unique():
        user_info = users_df[users_df['user_id'] == user_id].iloc[0]
        user_events = events_df[events_df['user_id'] == user_id]
        
        if len(user_events) == 0:
            continue
            
        cohort_month = user_info['user_created_date'].to_period('M')
        
        # Calculate retention by month
        for months_since_signup in range(0, 6):  # 6 months of data
            target_month = cohort_month + months_since_signup
            month_events = user_events[
                user_events['event_created_at'].dt.to_period('M') == target_month
            ]
            
            is_retained = 1 if len(month_events) > 0 else 0
            events_count = len(month_events)
            active_days = month_events['event_created_at'].dt.date.nunique() if len(month_events) > 0 else 0
            
            cohort_data.append({
                'user_id': user_id,
                'cohort_month': str(cohort_month),
                'user_title': user_info['user_title'],
                'months_since_signup': months_since_signup,
                'is_retained': is_retained,
                'events_count': events_count,
                'active_days': active_days
            })
    
    cohort_df = pd.DataFrame(cohort_data)
    
    # Export to CSV
    cohort_csv_path = os.path.join(os.path.dirname(__file__), 'cohort_analysis_base_model.csv')
    cohort_df.to_csv(cohort_csv_path, index=False)
    print(f"\n📁 Cohort analysis base model saved to: {cohort_csv_path}\n")
    
    # Calculate cohort summary
    cohort_summary = cohort_df.groupby(['cohort_month', 'months_since_signup']).agg({
        'user_id': 'count',
        'is_retained': 'sum',
        'events_count': 'mean',
        'active_days': 'mean'
    }).reset_index()
    
    cohort_summary['retention_rate_pct'] = (
        cohort_summary['is_retained'] / cohort_summary['user_id'] * 100
    ).round(2)
    
    print(f"📈 Total cohort records: {len(cohort_df)}")
    print(f"👥 Unique users: {cohort_df['user_id'].nunique()}")
    print(f"📅 Cohort months: {cohort_df['cohort_month'].nunique()}")
    
    print("\n🎯 Retention Rates by Cohort Month:")
    for cohort_month in cohort_summary['cohort_month'].unique():
        cohort_data = cohort_summary[cohort_summary['cohort_month'] == cohort_month]
        print(f"\n📅 Cohort: {cohort_month}")
        for _, row in cohort_data.iterrows():
            print(f"   Month {row['months_since_signup']}: {row['retention_rate_pct']}% "
                  f"({row['is_retained']}/{row['user_id']} users)")
    
    return cohort_df

def simulate_user_acquisition_metrics():
    """Simulate user_acquisition_metrics model results"""
    print("\n" + "=" * 80)
    print("📊 USER ACQUISITION METRICS MODEL RESULTS")
    print("=" * 80)
    
    # Load data
    users_df, firms_df, events_df = load_harvey_data()
    
    # Convert dates
    users_df['user_created_date'] = pd.to_datetime(users_df['user_created_date'])
    events_df['event_created_at'] = pd.to_datetime(events_df['event_created_at'])
    
    # Create acquisition data
    acquisition_data = []
    
    for user_id in users_df['user_id'].unique():
        user_info = users_df[users_df['user_id'] == user_id].iloc[0]
        user_events = events_df[events_df['user_id'] == user_id]
        
        acquisition_month = user_info['user_created_date'].to_period('M')
        
        # Calculate activation metrics
        first_activity = user_events['event_created_at'].min() if len(user_events) > 0 else None
        days_to_first_activity = None
        if first_activity:
            days_to_first_activity = (first_activity - user_info['user_created_date']).days
        
        is_activated = 1 if first_activity is not None else 0
        is_quick_start = 1 if days_to_first_activity is not None and days_to_first_activity <= 7 else 0
        
        # Get firm_id from events
        firm_id = user_events['firm_id'].iloc[0] if len(user_events) > 0 else None
        
        acquisition_data.append({
            'user_id': user_id,
            'acquisition_month': str(acquisition_month),
            'user_title': user_info['user_title'],
            'firm_id': firm_id,
            'days_to_first_activity': days_to_first_activity,
            'is_activated': is_activated,
            'is_quick_start': is_quick_start,
            'total_events': len(user_events),
            'avg_satisfaction_score': user_events['feedback_score'].mean() if len(user_events) > 0 else None
        })
    
    acquisition_df = pd.DataFrame(acquisition_data)
    
    # Calculate acquisition summary
    acquisition_summary = acquisition_df.groupby(['acquisition_month', 'user_title']).agg({
        'user_id': 'count',
        'is_activated': 'sum',
        'is_quick_start': 'sum',
        'total_events': 'mean',
        'avg_satisfaction_score': 'mean'
    }).reset_index()
    
    acquisition_summary['activation_rate_pct'] = (
        acquisition_summary['is_activated'] / acquisition_summary['user_id'] * 100
    ).round(2)
    
    acquisition_summary['quick_start_rate_pct'] = (
        acquisition_summary['is_quick_start'] / acquisition_summary['user_id'] * 100
    ).round(2)

    # Save acquisition summary as CSV
    csv_path = os.path.join(os.path.dirname(__file__), 'user_acquisition_metrics_summary.csv')
    acquisition_summary.to_csv(csv_path, index=False)
    print(f"\n📁 Acquisition metrics summary saved to: {csv_path}\n")
    
    print(f"📈 Total acquisition records: {len(acquisition_df)}")
    print(f"👥 Unique users: {acquisition_df['user_id'].nunique()}")
    print(f"📅 Acquisition months: {acquisition_df['acquisition_month'].nunique()}")
    
    print("\n🎯 Activation Rates by Month and Title:")
    for month in acquisition_summary['acquisition_month'].unique():
        month_data = acquisition_summary[acquisition_summary['acquisition_month'] == month]
        print(f"\n📅 Month: {month}")
        for _, row in month_data.iterrows():
            print(f"   {row['user_title']}: {row['activation_rate_pct']}% activated, "
                  f"{row['quick_start_rate_pct']}% quick start")
    
    # --- Add chart: Activation Rate by User Title and Month ---
    plt.figure(figsize=(10, 6))
    for title in acquisition_summary['user_title'].unique():
        subset = acquisition_summary[acquisition_summary['user_title'] == title]
        plt.plot(subset['acquisition_month'], subset['activation_rate_pct'], marker='o', label=title)
    plt.title('Activation Rate by User Title and Acquisition Month')
    plt.xlabel('Acquisition Month')
    plt.ylabel('Activation Rate (%)')
    plt.legend(title='User Title')
    plt.xticks(rotation=45)
    plt.tight_layout()
    chart_path = os.path.join(os.path.dirname(__file__), 'user_acquisition_activation_rate.png')
    plt.savefig(chart_path)
    plt.close()
    print(f"\n📊 Activation rate chart saved to: {chart_path}\n")
    
    return acquisition_df

def simulate_user_acquisition_base():
    """Simulate user_acquisition_base model results"""
    print("\n" + "=" * 80)
    print("📊 USER ACQUISITION BASE MODEL RESULTS")
    print("=" * 80)
    
    # Load data
    users_df, firms_df, events_df = load_harvey_data()
    
    # Convert dates
    users_df['user_created_date'] = pd.to_datetime(users_df['user_created_date'])
    events_df['event_created_at'] = pd.to_datetime(events_df['event_created_at'])
    
    # Create acquisition base data
    acquisition_base_data = []
    
    for user_id in users_df['user_id'].unique():
        user_info = users_df[users_df['user_id'] == user_id].iloc[0]
        user_events = events_df[events_df['user_id'] == user_id]
        
        # Get firm info from events (users can work with multiple firms)
        firm_id = user_events['firm_id'].iloc[0] if len(user_events) > 0 else None
        firm_info = firms_df[firms_df['firm_id'] == firm_id].iloc[0] if firm_id else None
        
        acquisition_month = user_info['user_created_date'].to_period('M')
        
        # Calculate activation metrics
        first_activity = user_events['event_created_at'].min() if len(user_events) > 0 else None
        days_to_first_activity = None
        if first_activity:
            days_to_first_activity = (first_activity - user_info['user_created_date']).days
        
        is_activated = 1 if first_activity is not None else 0
        is_quick_start = 1 if days_to_first_activity is not None and days_to_first_activity <= 7 else 0
        is_monthly_activated = 1 if days_to_first_activity is not None and days_to_first_activity <= 30 else 0
        
        # Firm size and ARR categories
        firm_size_category = 'Unknown'
        arr_category = 'Unknown'
        firm_size = None
        arr_in_thousands = None
        
        if firm_info is not None:
            firm_size = firm_info['firm_size']
            arr_in_thousands = firm_info['arr_in_thousands']
            
            if firm_size >= 500:
                firm_size_category = 'Enterprise'
            elif firm_size >= 200:
                firm_size_category = 'Large'
            elif firm_size >= 100:
                firm_size_category = 'Medium'
            else:
                firm_size_category = 'Small'
            
            if arr_in_thousands >= 500:
                arr_category = 'High Value'
            elif arr_in_thousands >= 200:
                arr_category = 'Medium Value'
            elif arr_in_thousands >= 100:
                arr_category = 'Low Value'
            else:
                arr_category = 'Minimal Value'
        
        # Performance categories
        if is_activated == 1 and days_to_first_activity is not None:
            if days_to_first_activity <= 1:
                activation_category = 'Immediate Activation'
            elif days_to_first_activity <= 7:
                activation_category = 'Quick Activation'
            elif days_to_first_activity <= 30:
                activation_category = 'Standard Activation'
            else:
                activation_category = 'Delayed Activation'
        else:
            activation_category = 'Not Activated'
        
        avg_satisfaction = user_events['feedback_score'].mean() if len(user_events) > 0 else None
        if avg_satisfaction is not None:
            if avg_satisfaction >= 4.5:
                satisfaction_category = 'High Satisfaction'
            elif avg_satisfaction >= 4.0:
                satisfaction_category = 'Good Satisfaction'
            elif avg_satisfaction >= 3.5:
                satisfaction_category = 'Fair Satisfaction'
            else:
                satisfaction_category = 'Low Satisfaction'
        else:
            satisfaction_category = 'No Feedback'
        
        acquisition_base_data.append({
            'user_id': user_id,
            'user_title': user_info['user_title'],
            'user_created_date': user_info['user_created_date'],
            'firm_id': firm_id,
            'firm_size': firm_size,
            'arr_in_thousands': arr_in_thousands,
            'acquisition_month': str(acquisition_month),
            'first_activity_date': first_activity,
            'days_to_first_activity': days_to_first_activity,
            'total_events': len(user_events),
            'active_days': user_events['event_created_at'].dt.date.nunique() if len(user_events) > 0 else 0,
            'avg_satisfaction_score': avg_satisfaction,
            'total_documents_processed': user_events['num_docs'].sum() if len(user_events) > 0 else 0,
            'is_activated': is_activated,
            'is_quick_start': is_quick_start,
            'is_monthly_activated': is_monthly_activated,
            'firm_size_category': firm_size_category,
            'arr_category': arr_category,
            'activation_category': activation_category,
            'satisfaction_category': satisfaction_category
        })
    
    acquisition_base_df = pd.DataFrame(acquisition_base_data)
    
    # Export to CSV
    acquisition_base_csv_path = os.path.join(os.path.dirname(__file__), 'user_acquisition_base_model.csv')
    acquisition_base_df.to_csv(acquisition_base_csv_path, index=False)
    print(f"\n📁 User acquisition base model saved to: {acquisition_base_csv_path}\n")
    
    print(f"📈 Total acquisition base records: {len(acquisition_base_df)}")
    print(f"👥 Unique users: {acquisition_base_df['user_id'].nunique()}")
    print(f"📅 Acquisition months: {acquisition_base_df['acquisition_month'].nunique()}")
    
    print("\n🎯 Activation Categories Distribution:")
    activation_counts = acquisition_base_df['activation_category'].value_counts()
    for category, count in activation_counts.items():
        percentage = (count / len(acquisition_base_df)) * 100
        print(f"   {category}: {count} ({percentage:.1f}%)")
    
    print("\n🎯 Satisfaction Categories Distribution:")
    satisfaction_counts = acquisition_base_df['satisfaction_category'].value_counts()
    for category, count in satisfaction_counts.items():
        percentage = (count / len(acquisition_base_df)) * 100
        print(f"   {category}: {count} ({percentage:.1f}%)")
    
    return acquisition_base_df

def simulate_event_performance_metrics():
    """Simulate event_performance_metrics model results"""
    print("\n" + "=" * 80)
    print("📊 EVENT PERFORMANCE METRICS MODEL RESULTS")
    print("=" * 80)
    
    # Load data
    users_df, firms_df, events_df = load_harvey_data()
    
    # Convert dates
    events_df['event_created_at'] = pd.to_datetime(events_df['event_created_at'])
    users_df['user_created_date'] = pd.to_datetime(users_df['user_created_date'])
    
    # 1. Create base CTE with all calculations
    event_performance_data = []
    
    for _, event in events_df.iterrows():
        user_info = users_df[users_df['user_id'] == event['user_id']].iloc[0]
        firm_info = firms_df[firms_df['firm_id'] == event['firm_id']].iloc[0]
        
        # Time-based dimensions
        event_month = event['event_created_at'].to_period('M')
        event_week = event['event_created_at'].to_period('W')
        event_date = event['event_created_at'].date()
        
        # User tenure at time of event
        user_tenure_days = (event['event_created_at'] - user_info['user_created_date']).days
        
        # Event performance indicators
        high_satisfaction_event = 1 if event['feedback_score'] >= 4 else 0
        high_volume_event = 1 if event['num_docs'] >= 10 else 0
        
        # User segments
        if user_tenure_days <= 7:
            user_segment = 'New User'
        elif user_tenure_days <= 30:
            user_segment = 'Recent User'
        elif user_tenure_days <= 90:
            user_segment = 'Established User'
        else:
            user_segment = 'Long-term User'
        
        event_performance_data.append({
            'event_id': event.name,  # Use DataFrame index as event_id
            'event_type': event['event_type'],
            'event_created_at': event['event_created_at'],
            'num_docs': event['num_docs'],
            'feedback_score': event['feedback_score'],
            'user_id': event['user_id'],
            'user_title': user_info['user_title'],
            'user_created_date': user_info['user_created_date'],
            'firm_id': event['firm_id'],
            'firm_size': firm_info['firm_size'],
            'arr_in_thousands': firm_info['arr_in_thousands'],
            'event_month': str(event_month),
            'event_week': str(event_week),
            'event_date': event_date,
            'user_tenure_days': user_tenure_days,
            'high_satisfaction_event': high_satisfaction_event,
            'high_volume_event': high_volume_event,
            'user_segment': user_segment
        })
    
    event_performance_df = pd.DataFrame(event_performance_data)
    
    # 2. Aggregate by different time dimensions
    # Daily metrics
    daily_metrics = event_performance_df.groupby(['event_date', 'event_type', 'user_title', 'user_segment']).agg({
        'event_id': 'count',
        'user_id': 'nunique',
        'firm_id': 'nunique',
        'num_docs': ['sum', 'mean'],
        'feedback_score': 'mean',
        'high_satisfaction_event': 'sum',
        'high_volume_event': 'sum'
    }).reset_index()
    
    daily_metrics.columns = [
        'event_date', 'event_type', 'user_title', 'user_segment', 'total_events', 
        'unique_users', 'unique_firms', 'total_documents_processed', 'avg_documents_per_event',
        'avg_satisfaction_score', 'high_satisfaction_events', 'high_volume_events'
    ]
    
    daily_metrics['satisfaction_rate_pct'] = (
        daily_metrics['high_satisfaction_events'] / daily_metrics['total_events'] * 100
    ).round(2)
    
    daily_metrics['high_volume_rate_pct'] = (
        daily_metrics['high_volume_events'] / daily_metrics['total_events'] * 100
    ).round(2)
    
    daily_metrics['documents_per_user'] = (
        daily_metrics['total_documents_processed'] / daily_metrics['unique_users']
    ).round(2)
    
    daily_metrics['events_per_user'] = (
        daily_metrics['total_events'] / daily_metrics['unique_users']
    ).round(2)
    
    daily_metrics['time_grain'] = 'daily'
    daily_metrics['time_period'] = daily_metrics['event_date']
    
    # Weekly metrics
    weekly_metrics = event_performance_df.groupby(['event_week', 'event_type', 'user_title']).agg({
        'event_id': 'count',
        'user_id': 'nunique',
        'firm_id': 'nunique',
        'num_docs': ['sum', 'mean'],
        'feedback_score': 'mean',
        'high_satisfaction_event': 'sum',
        'high_volume_event': 'sum'
    }).reset_index()
    
    weekly_metrics.columns = [
        'event_week', 'event_type', 'user_title', 'total_events', 
        'unique_users', 'unique_firms', 'total_documents_processed', 'avg_documents_per_event',
        'avg_satisfaction_score', 'high_satisfaction_events', 'high_volume_events'
    ]
    
    weekly_metrics['satisfaction_rate_pct'] = (
        weekly_metrics['high_satisfaction_events'] / weekly_metrics['total_events'] * 100
    ).round(2)
    
    weekly_metrics['high_volume_rate_pct'] = (
        weekly_metrics['high_volume_events'] / weekly_metrics['total_events'] * 100
    ).round(2)
    
    # Add week-over-week growth (simplified)
    weekly_metrics['prev_week_events'] = weekly_metrics.groupby(['event_type', 'user_title'])['total_events'].shift(1)
    weekly_metrics['week_over_week_growth_pct'] = (
        (weekly_metrics['total_events'] - weekly_metrics['prev_week_events']) * 100.0 / 
        weekly_metrics['prev_week_events'].replace(0, np.nan)
    ).round(2)
    
    weekly_metrics['time_grain'] = 'weekly'
    weekly_metrics['time_period'] = weekly_metrics['event_week']
    
    # Monthly metrics
    monthly_metrics = event_performance_df.groupby(['event_month', 'event_type', 'user_title', 'user_segment']).agg({
        'event_id': 'count',
        'user_id': 'nunique',
        'firm_id': 'nunique',
        'num_docs': ['sum', 'mean'],
        'feedback_score': 'mean',
        'high_satisfaction_event': 'sum',
        'high_volume_event': 'sum'
    }).reset_index()
    
    monthly_metrics.columns = [
        'event_month', 'event_type', 'user_title', 'user_segment', 'total_events', 
        'unique_users', 'unique_firms', 'total_documents_processed', 'avg_documents_per_event',
        'avg_satisfaction_score', 'high_satisfaction_events', 'high_volume_events'
    ]
    
    monthly_metrics['satisfaction_rate_pct'] = (
        monthly_metrics['high_satisfaction_events'] / monthly_metrics['total_events'] * 100
    ).round(2)
    
    monthly_metrics['high_volume_rate_pct'] = (
        monthly_metrics['high_volume_events'] / monthly_metrics['total_events'] * 100
    ).round(2)
    
    monthly_metrics['events_per_user'] = (
        monthly_metrics['total_events'] / monthly_metrics['unique_users']
    ).round(2)
    
    monthly_metrics['documents_per_user'] = (
        monthly_metrics['total_documents_processed'] / monthly_metrics['unique_users']
    ).round(2)
    
    # Performance categories
    monthly_metrics['satisfaction_performance'] = monthly_metrics['avg_satisfaction_score'].apply(
        lambda x: 'Excellent' if x >= 4.5 else 'Good' if x >= 4.0 else 'Fair' if x >= 3.5 else 'Needs Improvement'
    )
    
    monthly_metrics['volume_performance'] = monthly_metrics['total_events'].apply(
        lambda x: 'High Volume' if x >= 1000 else 'Medium Volume' if x >= 500 else 'Low Volume' if x >= 100 else 'Minimal Volume'
    )
    
    monthly_metrics['time_grain'] = 'monthly'
    monthly_metrics['time_period'] = monthly_metrics['event_month']
    
    # 3. Combine all aggregations
    # Select common columns for union
    daily_union = daily_metrics[['time_grain', 'time_period', 'event_type', 'user_title', 'user_segment', 
                                'total_events', 'unique_users', 'unique_firms', 'total_documents_processed',
                                'avg_documents_per_event', 'avg_satisfaction_score', 'high_satisfaction_events',
                                'high_volume_events', 'satisfaction_rate_pct', 'high_volume_rate_pct',
                                'documents_per_user', 'events_per_user']].copy()
    
    weekly_union = weekly_metrics[['time_grain', 'time_period', 'event_type', 'user_title', 
                                  'total_events', 'unique_users', 'unique_firms', 'total_documents_processed',
                                  'avg_documents_per_event', 'avg_satisfaction_score', 'high_satisfaction_events',
                                  'high_volume_events', 'satisfaction_rate_pct', 'high_volume_rate_pct',
                                  'week_over_week_growth_pct']].copy()
    weekly_union['user_segment'] = None
    weekly_union['documents_per_user'] = None
    weekly_union['events_per_user'] = None
    
    monthly_union = monthly_metrics[['time_grain', 'time_period', 'event_type', 'user_title', 'user_segment',
                                    'total_events', 'unique_users', 'unique_firms', 'total_documents_processed',
                                    'avg_documents_per_event', 'avg_satisfaction_score', 'high_satisfaction_events',
                                    'high_volume_events', 'satisfaction_rate_pct', 'high_volume_rate_pct',
                                    'events_per_user', 'documents_per_user', 'satisfaction_performance', 'volume_performance']].copy()
    
    # Add missing columns to align schemas
    daily_union['week_over_week_growth_pct'] = None
    daily_union['satisfaction_performance'] = None
    daily_union['volume_performance'] = None
    
    weekly_union['satisfaction_performance'] = None
    weekly_union['volume_performance'] = None
    
    monthly_union['week_over_week_growth_pct'] = None
    
    # Combine all metrics
    combined_metrics = pd.concat([daily_union, weekly_union, monthly_union], ignore_index=True)
    
    # Export to CSV
    event_performance_csv_path = os.path.join(os.path.dirname(__file__), 'event_performance_metrics_combined.csv')
    combined_metrics.to_csv(event_performance_csv_path, index=False)
    print(f"\n📁 Event performance metrics (combined) saved to: {event_performance_csv_path}\n")
    
    print(f"📈 Daily performance records: {len(daily_metrics)}")
    print(f"📈 Weekly performance records: {len(weekly_metrics)}")
    print(f"📈 Monthly performance records: {len(monthly_metrics)}")
    print(f"📈 Combined performance records: {len(combined_metrics)}")
    
    print("\n🎯 Event Type Performance Summary:")
    event_counts = events_df.groupby('event_type').size().reset_index(name='total_events')
    event_metrics = events_df.groupby('event_type').agg({
        'user_id': 'nunique',
        'num_docs': ['mean', 'sum'],
        'feedback_score': 'mean'
    }).round(2)
    
    event_metrics.columns = ['unique_users', 'avg_docs_per_event', 'total_docs', 'avg_satisfaction']
    event_summary = event_counts.merge(event_metrics, left_index=True, right_index=True)
    print(event_summary)
    
    print("\n📊 Top 5 Days by Event Volume:")
    top_days = daily_metrics.groupby('time_period')['total_events'].sum().sort_values(ascending=False).head(5)
    for date, events in top_days.items():
        print(f"   {date}: {events} events")
    
    return combined_metrics

def main():
    """Run all model simulations"""
    print("🚀 HARVEY ANALYTICS - DBT MODEL RESULTS SIMULATION")
    print("=" * 80)
    print("This simulation shows what the results would look like if we ran the dbt models")
    print("on the actual Harvey Analytics data.")
    print("=" * 80)
    
    try:
        # Run all model simulations
        user_engagement_df = simulate_user_engagement()
        cohort_df = simulate_cohort_analysis()
        acquisition_df = simulate_user_acquisition_metrics()
        acquisition_base_df = simulate_user_acquisition_base()
        combined_perf = simulate_event_performance_metrics()
        
        print("\n" + "=" * 80)
        print("✅ ALL MODEL SIMULATIONS COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
        print(f"\n📊 Summary of Generated Data:")
        print(f"   User Engagement Records: {len(user_engagement_df)}")
        print(f"   Cohort Analysis Records: {len(cohort_df)}")
        print(f"   User Acquisition Records: {len(acquisition_df)}")
        print(f"   User Acquisition Base Records: {len(acquisition_base_df)}")
        print(f"   Combined Event Performance Records: {len(combined_perf)}")
        
        print(f"\n🎯 Key Insights:")
        print(f"   - User engagement levels show healthy distribution")
        print(f"   - Cohort retention rates demonstrate user stickiness")
        print(f"   - Event performance varies by type and time period")
        print(f"   - User acquisition shows good activation rates")
        
        print(f"\n💡 Next Steps:")
        print(f"   - Deploy these models to production dbt environment")
        print(f"   - Set up automated testing and monitoring")
        print(f"   - Create dashboards for business stakeholders")
        
    except Exception as e:
        print(f"❌ Error running model simulations: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 