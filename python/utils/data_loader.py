"""
Data loader utility for Harvey Analytics data quality analysis.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Any


def load_harvey_data(data_dir: str = "../../data_source") -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load Harvey Analytics data from CSV files.
    
    Args:
        data_dir: Directory containing the CSV files
        
    Returns:
        Tuple of (users_df, firms_df, events_df)
    """
    data_path = Path(data_dir)
    
    # Load users data
    users_file = data_path / "analytics_engineer_harvey_mock_data - users.csv"
    users_df = pd.read_csv(users_file)
    
    # Load firms data
    firms_file = data_path / "analytics_engineer_harvey_mock_data - firms.csv"
    firms_df = pd.read_csv(firms_file)
    
    # Load events data
    events_file = data_path / "analytics_engineer_harvey_mock_data - events.csv"
    events_df = pd.read_csv(events_file)
    
    # Rename columns to match expected names
    users_df = users_df.rename(columns={
        'ID': 'user_id',
        'CREATED': 'user_created_date',
        'TITLE': 'user_title'
    })
    
    firms_df = firms_df.rename(columns={
        'ID': 'firm_id',
        'CREATED': 'firm_created_date',
        'FIRM_SIZE': 'firm_size',
        'ARR_IN_THOUSANDS': 'arr_in_thousands'
    })
    
    events_df = events_df.rename(columns={
        'CREATED': 'event_created_at',
        'FIRM_ID': 'firm_id',
        'USER_ID': 'user_id',
        'EVENT_TYPE': 'event_type',
        'NUM_DOCS': 'num_docs',
        'FEEDBACK_SCORE': 'feedback_score'
    })
    
    # Convert date columns
    users_df['user_created_date'] = pd.to_datetime(users_df['user_created_date'])
    firms_df['firm_created_date'] = pd.to_datetime(firms_df['firm_created_date'])
    events_df['event_created_at'] = pd.to_datetime(events_df['event_created_at'])
    
    print(f"✅ Loaded data:")
    print(f"   - Users: {len(users_df)} records")
    print(f"   - Firms: {len(firms_df)} records")
    print(f"   - Events: {len(events_df)} records")
    
    return users_df, firms_df, events_df


def get_data_summary(users_df: pd.DataFrame, firms_df: pd.DataFrame, events_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get summary statistics for the data.
    
    Args:
        users_df: Users dataframe
        firms_df: Firms dataframe
        events_df: Events dataframe
        
    Returns:
        Dictionary with summary statistics
    """
    summary = {
        'users': {
            'total_records': len(users_df),
            'columns': list(users_df.columns),
            'missing_values': users_df.isnull().sum().to_dict(),
            'unique_user_titles': users_df['user_title'].nunique(),
            'user_title_distribution': users_df['user_title'].value_counts().to_dict()
        },
        'firms': {
            'total_records': len(firms_df),
            'columns': list(firms_df.columns),
            'missing_values': firms_df.isnull().sum().to_dict(),
            'arr_stats': {
                'min': firms_df['arr_in_thousands'].min(),
                'max': firms_df['arr_in_thousands'].max(),
                'mean': firms_df['arr_in_thousands'].mean(),
                'zero_arr_count': len(firms_df[firms_df['arr_in_thousands'] == 0])
            },
            'firm_size_stats': {
                'min': firms_df['firm_size'].min(),
                'max': firms_df['firm_size'].max(),
                'mean': firms_df['firm_size'].mean(),
                'zero_size_count': len(firms_df[firms_df['firm_size'] == 0])
            }
        },
        'events': {
            'total_records': len(events_df),
            'columns': list(events_df.columns),
            'missing_values': events_df.isnull().sum().to_dict(),
            'event_type_distribution': events_df['event_type'].value_counts().to_dict(),
            'feedback_score_stats': {
                'min': events_df['feedback_score'].min(),
                'max': events_df['feedback_score'].max(),
                'mean': events_df['feedback_score'].mean(),
                'missing_feedback': events_df['feedback_score'].isnull().sum()
            },
            'num_docs_stats': {
                'min': events_df['num_docs'].min(),
                'max': events_df['num_docs'].max(),
                'mean': events_df['num_docs'].mean(),
                'zero_docs_count': len(events_df[events_df['num_docs'] == 0])
            }
        }
    }
    
    return summary


def print_data_summary(summary: Dict[str, Any]):
    """
    Print formatted data summary.
    
    Args:
        summary: Data summary dictionary
    """
    print("\n📊 Data Summary:")
    print("=" * 50)
    
    # Users summary
    print(f"\n👥 Users ({summary['users']['total_records']} records):")
    print(f"   Missing values: {summary['users']['missing_values']}")
    print(f"   Unique user titles: {summary['users']['unique_user_titles']}")
    print(f"   User title distribution: {summary['users']['user_title_distribution']}")
    
    # Firms summary
    print(f"\n🏢 Firms ({summary['firms']['total_records']} records):")
    print(f"   Missing values: {summary['firms']['missing_values']}")
    print(f"   ARR stats: {summary['firms']['arr_stats']}")
    print(f"   Firm size stats: {summary['firms']['firm_size_stats']}")
    
    # Events summary
    print(f"\n📈 Events ({summary['events']['total_records']} records):")
    print(f"   Missing values: {summary['events']['missing_values']}")
    print(f"   Event type distribution: {summary['events']['event_type_distribution']}")
    print(f"   Feedback score stats: {summary['events']['feedback_score_stats']}")
    print(f"   Document count stats: {summary['events']['num_docs_stats']}") 