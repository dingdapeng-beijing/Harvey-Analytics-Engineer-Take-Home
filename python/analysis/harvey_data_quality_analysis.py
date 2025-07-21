#!/usr/bin/env python3
"""
Harvey Analytics - Data Quality Analysis Script

This script provides a comprehensive analysis of data quality issues in the Harvey Analytics platform.
It analyzes actual data to identify real issues, not imagined ones.

Usage:
    python harvey_data_quality_analysis.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from datetime import datetime
from pathlib import Path
import sys

# Add utils to path
sys.path.append('..')
from utils.data_loader import load_harvey_data, get_data_summary, print_data_summary

warnings.filterwarnings('ignore')

# Set plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


def analyze_completeness(users_df, firms_df, events_df):
    """Analyze data completeness issues."""
    print("\n🔍 Data Completeness Analysis")
    print("=" * 50)
    
    # Users missing values
    users_missing = users_df.isnull().sum()
    users_missing_pct = (users_missing / len(users_df)) * 100
    
    print(f"\n👥 Users Missing Values:")
    for col, missing_count in users_missing.items():
        if missing_count > 0:
            pct = (missing_count / len(users_df)) * 100
            print(f"   {col}: {missing_count} records ({pct:.1f}%)")
        else:
            print(f"   {col}: No missing values")
    
    # Firms missing values
    firms_missing = firms_df.isnull().sum()
    firms_missing_pct = (firms_missing / len(firms_df)) * 100
    
    print(f"\n🏢 Firms Missing Values:")
    for col, missing_count in firms_missing.items():
        if missing_count > 0:
            pct = (missing_count / len(firms_df)) * 100
            print(f"   {col}: {missing_count} records ({pct:.1f}%)")
        else:
            print(f"   {col}: No missing values")
    
    # Events missing values
    events_missing = events_df.isnull().sum()
    events_missing_pct = (events_missing / len(events_df)) * 100
    
    print(f"\n📈 Events Missing Values:")
    for col, missing_count in events_missing.items():
        if missing_count > 0:
            pct = (missing_count / len(events_df)) * 100
            print(f"   {col}: {missing_count} records ({pct:.1f}%)")
        else:
            print(f"   {col}: No missing values")
    
    return {
        'users_missing': users_missing,
        'firms_missing': firms_missing,
        'events_missing': events_missing
    }


def analyze_event_types(events_df):
    """Analyze event type distribution."""
    print("\n📊 Event Type Distribution Analysis")
    print("=" * 50)
    
    event_type_counts = events_df['event_type'].value_counts()
    event_type_pct = (event_type_counts / len(events_df)) * 100
    
    print(f"\nEvent Type Distribution:")
    for event_type, count in event_type_counts.items():
        pct = event_type_pct[event_type]
        print(f"   {event_type}: {count} events ({pct:.1f}%)")
    
    print(f"\nTotal Events: {len(events_df)}")
    print(f"Unique Event Types: {events_df['event_type'].nunique()}")
    
    return event_type_counts


def analyze_consistency(users_df, firms_df, events_df):
    """Analyze data consistency issues."""
    print("\n🔍 Data Consistency Analysis")
    print("=" * 50)
    
    # Timeline consistency
    events_users = events_df.merge(users_df[['user_id', 'user_created_date']], on='user_id', how='left')
    timeline_issues = events_users[events_users['event_created_at'] < events_users['user_created_date']]
    timeline_issue_pct = (len(timeline_issues) / len(events_df)) * 100
    
    print(f"\n⏰ Timeline Consistency:")
    print(f"   Events before user creation: {len(timeline_issues)} ({timeline_issue_pct:.1f}%)")
    
    # Feedback scores
    invalid_feedback = events_df[~events_df['feedback_score'].between(1, 5)]
    invalid_feedback_pct = (len(invalid_feedback) / len(events_df)) * 100
    
    print(f"\n⭐ Feedback Score Analysis:")
    print(f"   Valid range: 1-5")
    print(f"   Actual range: {events_df['feedback_score'].min()}-{events_df['feedback_score'].max()}")
    print(f"   Mean: {events_df['feedback_score'].mean():.2f}")
    print(f"   Missing feedback: {events_df['feedback_score'].isnull().sum()} ({events_df['feedback_score'].isnull().sum()/len(events_df)*100:.1f}%)")
    print(f"   Invalid scores (outside 1-5): {len(invalid_feedback)} ({invalid_feedback_pct:.1f}%)")
    
    # Document counts
    invalid_docs = events_df[events_df['num_docs'] <= 0]
    invalid_docs_pct = (len(invalid_docs) / len(events_df)) * 100
    
    print(f"\n📄 Document Count Analysis:")
    print(f"   Range: {events_df['num_docs'].min()}-{events_df['num_docs'].max()}")
    print(f"   Mean: {events_df['num_docs'].mean():.2f}")
    print(f"   Zero documents: {len(events_df[events_df['num_docs'] == 0])} ({len(events_df[events_df['num_docs'] == 0])/len(events_df)*100:.1f}%)")
    print(f"   Negative documents: {len(events_df[events_df['num_docs'] < 0])} ({len(events_df[events_df['num_docs'] < 0])/len(events_df)*100:.1f}%)")
    print(f"   Zero or negative documents: {len(invalid_docs)} ({invalid_docs_pct:.1f}%)")
    
    return {
        'timeline_issues': timeline_issues,
        'invalid_feedback': invalid_feedback,
        'invalid_docs': invalid_docs
    }


def analyze_business_logic(users_df, firms_df, events_df):
    """Analyze business logic issues."""
    print("\n🏢 Business Logic Analysis")
    print("=" * 50)
    
    # Firms with zero ARR
    zero_arr_firms = firms_df[firms_df['arr_in_thousands'] == 0]
    zero_arr_pct = (len(zero_arr_firms) / len(firms_df)) * 100
    
    print(f"\n💰 ARR Analysis:")
    print(f"   Firms with zero ARR: {len(zero_arr_firms)} ({zero_arr_pct:.1f}%)")
    print(f"   ARR range: ${firms_df['arr_in_thousands'].min():.0f}k - ${firms_df['arr_in_thousands'].max():.0f}k")
    print(f"   Mean ARR: ${firms_df['arr_in_thousands'].mean():.0f}k")
    
    # Firms with zero employees
    zero_size_firms = firms_df[firms_df['firm_size'] == 0]
    zero_size_pct = (len(zero_size_firms) / len(firms_df)) * 100
    
    print(f"\n👥 Firm Size Analysis:")
    print(f"   Firms with zero employees: {len(zero_size_firms)} ({zero_size_pct:.1f}%)")
    print(f"   Firm size range: {firms_df['firm_size'].min()} - {firms_df['firm_size'].max()} employees")
    print(f"   Mean firm size: {firms_df['firm_size'].mean():.0f} employees")
    
    # Future dates
    current_date = datetime.now()
    future_user_dates = users_df[users_df['user_created_date'] > current_date]
    future_firm_dates = firms_df[firms_df['firm_created_date'] > current_date]
    future_event_dates = events_df[events_df['event_created_at'] > current_date]
    
    print(f"\n⏰ Future Date Analysis:")
    print(f"   Users created in future: {len(future_user_dates)} ({len(future_user_dates)/len(users_df)*100:.1f}%)")
    print(f"   Firms created in future: {len(future_firm_dates)} ({len(future_firm_dates)/len(firms_df)*100:.1f}%)")
    print(f"   Events created in future: {len(future_event_dates)} ({len(future_event_dates)/len(events_df)*100:.1f}%)")
    
    return {
        'zero_arr_firms': zero_arr_firms,
        'zero_size_firms': zero_size_firms,
        'future_user_dates': future_user_dates,
        'future_firm_dates': future_firm_dates,
        'future_event_dates': future_event_dates
    }


def analyze_anomalies(users_df, firms_df, events_df):
    """Analyze data anomalies."""
    print("\n🔍 Data Anomalies Analysis")
    print("=" * 50)
    
    # Orphaned users
    users_with_events = events_df['user_id'].unique()
    orphaned_users = users_df[~users_df['user_id'].isin(users_with_events)]
    orphaned_pct = (len(orphaned_users) / len(users_df)) * 100
    
    print(f"\n👤 Orphaned Users:")
    print(f"   Users with no events: {len(orphaned_users)} ({orphaned_pct:.1f}%)")
    
    # Feedback score outliers
    feedback_scores = events_df['feedback_score'].dropna()
    outliers = pd.Series()
    
    if len(feedback_scores) > 0:
        Q1 = feedback_scores.quantile(0.25)
        Q3 = feedback_scores.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = feedback_scores[(feedback_scores < lower_bound) | (feedback_scores > upper_bound)]
        outliers_pct = (len(outliers) / len(feedback_scores)) * 100
        
        print(f"\n📊 Feedback Score Outliers:")
        print(f"   Q1: {Q1:.2f}, Q3: {Q3:.2f}, IQR: {IQR:.2f}")
        print(f"   Lower bound: {lower_bound:.2f}, Upper bound: {upper_bound:.2f}")
        print(f"   Statistical outliers: {len(outliers)} ({outliers_pct:.1f}%)")
    
    # Extreme document counts
    doc_counts = events_df['num_docs']
    Q1_docs = doc_counts.quantile(0.25)
    Q3_docs = doc_counts.quantile(0.75)
    IQR_docs = Q3_docs - Q1_docs
    upper_bound_docs = Q3_docs + 1.5 * IQR_docs
    
    extreme_docs = events_df[events_df['num_docs'] > upper_bound_docs]
    extreme_docs_pct = (len(extreme_docs) / len(events_df)) * 100
    
    print(f"\n📄 Extreme Document Counts:")
    print(f"   Q1: {Q1_docs:.2f}, Q3: {Q3_docs:.2f}, IQR: {IQR_docs:.2f}")
    print(f"   Upper bound: {upper_bound_docs:.2f}")
    print(f"   Extreme document counts (> {upper_bound_docs:.0f}): {len(extreme_docs)} ({extreme_docs_pct:.1f}%)")
    
    return {
        'orphaned_users': orphaned_users,
        'outliers': outliers,
        'extreme_docs': extreme_docs
    }


def create_visualizations(users_df, firms_df, events_df, analysis_results):
    """Create comprehensive visualizations."""
    print("\n📊 Creating Visualizations...")
    
    # Create reports directory
    reports_dir = Path("../reports")
    reports_dir.mkdir(exist_ok=True)
    
    # 1. Event Type Distribution
    event_type_counts = analysis_results['event_type_counts']
    fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    event_type_counts.plot(kind='bar', ax=ax1, color='skyblue')
    ax1.set_title('Event Type Distribution')
    ax1.set_xlabel('Event Type')
    ax1.set_ylabel('Count')
    ax1.tick_params(axis='x', rotation=45)
    
    ax2.pie(event_type_counts.values, labels=event_type_counts.index, autopct='%1.1f%%', startangle=90)
    ax2.set_title('Event Type Distribution (%)')
    
    plt.tight_layout()
    plt.savefig(reports_dir / 'event_type_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 2. Missing Values Analysis
    missing_data = analysis_results['completeness']
    fig2, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Users missing values
    users_missing_data = missing_data['users_missing'][missing_data['users_missing'] > 0]
    if len(users_missing_data) > 0:
        axes[0].bar(users_missing_data.index, users_missing_data.values)
    axes[0].set_title('Users - Missing Values')
    axes[0].set_ylabel('Count')
    axes[0].tick_params(axis='x', rotation=45)
    
    # Firms missing values
    firms_missing_data = missing_data['firms_missing'][missing_data['firms_missing'] > 0]
    if len(firms_missing_data) > 0:
        axes[1].bar(firms_missing_data.index, firms_missing_data.values)
    axes[1].set_title('Firms - Missing Values')
    axes[1].set_ylabel('Count')
    axes[1].tick_params(axis='x', rotation=45)
    
    # Events missing values
    events_missing_data = missing_data['events_missing'][missing_data['events_missing'] > 0]
    if len(events_missing_data) > 0:
        axes[2].bar(events_missing_data.index, events_missing_data.values)
    axes[2].set_title('Events - Missing Values')
    axes[2].set_ylabel('Count')
    axes[2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(reports_dir / 'missing_values_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 3. Business Logic Issues
    business_logic = analysis_results['business_logic']
    fig3, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # ARR distribution
    axes[0,0].hist(firms_df['arr_in_thousands'], bins=30, alpha=0.7, color='lightblue', edgecolor='black')
    axes[0,0].set_title('ARR Distribution (in thousands)')
    axes[0,0].set_xlabel('ARR ($k)')
    axes[0,0].set_ylabel('Count')
    
    # Firm size distribution
    axes[0,1].hist(firms_df['firm_size'], bins=30, alpha=0.7, color='lightgreen', edgecolor='black')
    axes[0,1].set_title('Firm Size Distribution')
    axes[0,1].set_xlabel('Number of Employees')
    axes[0,1].set_ylabel('Count')
    
    # ARR vs Firm Size
    axes[1,0].scatter(firms_df['firm_size'], firms_df['arr_in_thousands'], alpha=0.6, color='purple')
    axes[1,0].set_title('ARR vs Firm Size')
    axes[1,0].set_xlabel('Number of Employees')
    axes[1,0].set_ylabel('ARR ($k)')
    
    # Business logic issues summary
    business_logic_issues = {
        'Zero ARR': len(business_logic['zero_arr_firms']),
        'Zero Employees': len(business_logic['zero_size_firms']),
        'Future User Dates': len(business_logic['future_user_dates']),
        'Future Firm Dates': len(business_logic['future_firm_dates'])
    }
    axes[1,1].bar(business_logic_issues.keys(), business_logic_issues.values(), color=['red', 'orange', 'yellow', 'pink'])
    axes[1,1].set_title('Business Logic Issues Summary')
    axes[1,1].set_ylabel('Count')
    axes[1,1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(reports_dir / 'business_logic_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 4. Consistency Issues
    consistency = analysis_results['consistency']
    fig4, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Feedback score distribution
    feedback_scores = events_df['feedback_score'].dropna()
    axes[0,0].hist(feedback_scores, bins=range(1, 7), alpha=0.7, color='skyblue', edgecolor='black')
    axes[0,0].set_title('Feedback Score Distribution')
    axes[0,0].set_xlabel('Feedback Score')
    axes[0,0].set_ylabel('Count')
    axes[0,0].set_xticks(range(1, 6))
    
    # Document count distribution
    axes[0,1].hist(events_df['num_docs'], bins=50, alpha=0.7, color='lightgreen', edgecolor='black')
    axes[0,1].set_title('Document Count Distribution')
    axes[0,1].set_xlabel('Number of Documents')
    axes[0,1].set_ylabel('Count')
    
    # Timeline issues
    if len(consistency['timeline_issues']) > 0:
        timeline_issues = consistency['timeline_issues']
        timeline_issues['days_diff'] = (timeline_issues['event_created_at'] - timeline_issues['user_created_date']).dt.days
        axes[1,0].hist(timeline_issues['days_diff'], bins=20, alpha=0.7, color='salmon', edgecolor='black')
        axes[1,0].set_title('Timeline Issues: Days Before User Creation')
        axes[1,0].set_xlabel('Days Before User Creation')
        axes[1,0].set_ylabel('Count')
    else:
        axes[1,0].text(0.5, 0.5, 'No Timeline Issues', ha='center', va='center', transform=axes[1,0].transAxes)
        axes[1,0].set_title('Timeline Issues')
    
    # Consistency issues summary
    consistency_summary = {
        'Invalid Feedback': len(consistency['invalid_feedback']),
        'Zero/Negative Docs': len(consistency['invalid_docs']),
        'Timeline Issues': len(consistency['timeline_issues'])
    }
    axes[1,1].bar(consistency_summary.keys(), consistency_summary.values(), color=['red', 'orange', 'yellow'])
    axes[1,1].set_title('Consistency Issues Summary')
    axes[1,1].set_ylabel('Count')
    axes[1,1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(reports_dir / 'consistency_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"✅ Visualizations saved to {reports_dir}")


def generate_summary_report(users_df, firms_df, events_df, analysis_results):
    """Generate comprehensive summary report."""
    print("\n📋 Data Quality Analysis Summary")
    print("=" * 50)
    
    # Calculate overall data quality score
    total_records = len(users_df) + len(firms_df) + len(events_df)
    
    print(f"\n📊 Overall Statistics:")
    print(f"   Total Users: {len(users_df)}")
    print(f"   Total Firms: {len(firms_df)}")
    print(f"   Total Events: {len(events_df)}")
    print(f"   Total Records: {total_records}")
    
    # Calculate issues
    completeness_issues = sum(analysis_results['completeness']['users_missing']) + \
                         sum(analysis_results['completeness']['firms_missing']) + \
                         sum(analysis_results['completeness']['events_missing'])
    
    consistency_issues = len(analysis_results['consistency']['invalid_feedback']) + \
                        len(analysis_results['consistency']['invalid_docs']) + \
                        len(analysis_results['consistency']['timeline_issues'])
    
    business_logic_issues = len(analysis_results['business_logic']['zero_arr_firms']) + \
                           len(analysis_results['business_logic']['zero_size_firms']) + \
                           len(analysis_results['business_logic']['future_user_dates']) + \
                           len(analysis_results['business_logic']['future_firm_dates'])
    
    anomaly_issues = len(analysis_results['anomalies']['orphaned_users']) + \
                    len(analysis_results['anomalies']['outliers']) + \
                    len(analysis_results['anomalies']['extreme_docs'])
    
    total_issues = completeness_issues + consistency_issues + business_logic_issues + anomaly_issues
    overall_quality_score = ((total_records - total_issues) / total_records) * 100
    
    print(f"\n🚨 Data Quality Issues Found:")
    print(f"   Completeness Issues: {completeness_issues} missing values ({(completeness_issues/total_records)*100:.1f}%)")
    print(f"   Consistency Issues: {consistency_issues} records ({(consistency_issues/total_records)*100:.1f}%)")
    print(f"   Business Logic Issues: {business_logic_issues} records ({(business_logic_issues/total_records)*100:.1f}%)")
    print(f"   Anomaly Issues: {anomaly_issues} records ({(anomaly_issues/total_records)*100:.1f}%)")
    
    print(f"\n🎯 Overall Data Quality Score: {overall_quality_score:.1f}%")
    
    print(f"\n💡 Key Findings:")
    if completeness_issues > 0:
        print(f"   - Missing data affects {(completeness_issues/total_records)*100:.1f}% of records")
    if consistency_issues > 0:
        print(f"   - Data consistency issues affect {(consistency_issues/total_records)*100:.1f}% of records")
    if business_logic_issues > 0:
        print(f"   - Business logic violations affect {(business_logic_issues/total_records)*100:.1f}% of records")
    if anomaly_issues > 0:
        print(f"   - Data anomalies affect {(anomaly_issues/total_records)*100:.1f}% of records")
    
    print(f"\n🔧 Recommendations:")
    if completeness_issues > 0:
        print(f"   - Implement data validation at source systems")
    if consistency_issues > 0:
        print(f"   - Fix data consistency rules and validation")
    if business_logic_issues > 0:
        print(f"   - Review and fix business logic violations")
    if anomaly_issues > 0:
        print(f"   - Investigate and resolve data anomalies")
    print(f"   - Establish ongoing data quality monitoring")
    print(f"   - Create automated data quality alerts")
    
    return overall_quality_score


def main():
    """Main function to run the data quality analysis."""
    print("🚀 Harvey Analytics - Data Quality Analysis")
    print("=" * 60)
    
    try:
        # Load data
        users_df, firms_df, events_df = load_harvey_data()
        
        # Get data summary
        summary = get_data_summary(users_df, firms_df, events_df)
        print_data_summary(summary)
        
        # Run analyses
        completeness_results = analyze_completeness(users_df, firms_df, events_df)
        event_type_results = analyze_event_types(events_df)
        consistency_results = analyze_consistency(users_df, firms_df, events_df)
        business_logic_results = analyze_business_logic(users_df, firms_df, events_df)
        anomalies_results = analyze_anomalies(users_df, firms_df, events_df)
        
        # Combine results
        analysis_results = {
            'completeness': completeness_results,
            'event_type_counts': event_type_results,
            'consistency': consistency_results,
            'business_logic': business_logic_results,
            'anomalies': anomalies_results
        }
        
        # Create visualizations
        create_visualizations(users_df, firms_df, events_df, analysis_results)
        
        # Generate summary report
        overall_score = generate_summary_report(users_df, firms_df, events_df, analysis_results)
        
        print(f"\n✅ Analysis completed successfully!")
        print(f"📁 Reports saved to ../reports/")
        print(f"🎯 Overall Data Quality Score: {overall_score:.1f}%")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 