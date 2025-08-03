#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Processing Module for Fraud Detection Engine

This module provides functions to process and prepare transaction data
for fraud detection models.

Author: NinjaTech AI
Date: August 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_transaction_data(transaction):
    """
    Convert a transaction JSON to a DataFrame row
    
    Args:
        transaction (dict): Transaction data
        
    Returns:
        pandas.DataFrame: Single row DataFrame with transaction data
    """
    # Convert to DataFrame
    df = pd.DataFrame([transaction])
    
    # Convert timestamp to datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df

def load_user_history(user_id, days=30, db_connection=None):
    """
    Load historical transactions for a user
    
    Args:
        user_id (str): User identifier
        days (int): Number of days of history to load
        db_connection: Database connection
        
    Returns:
        pandas.DataFrame: User's transaction history
    """
    # In a real system, this would query a database
    # For this example, we'll simulate it with a file-based approach
    
    if db_connection:
        query = f"""
        SELECT * FROM transactions 
        WHERE user_id = '{user_id}' 
        AND timestamp >= NOW() - INTERVAL '{days} days'
        """
        return pd.read_sql(query, db_connection)
    
    # Try to load from a local file (for demo purposes)
    try:
        all_transactions = pd.read_csv("data/fraud_training_data.csv")
        
        # Convert timestamp to datetime
        if 'timestamp' in all_transactions.columns:
            all_transactions['timestamp'] = pd.to_datetime(all_transactions['timestamp'])
        
        # Filter for this user and time period
        cutoff_date = datetime.now() - timedelta(days=days)
        user_transactions = all_transactions[
            (all_transactions['user_id'] == user_id) & 
            (all_transactions['timestamp'] >= cutoff_date)
        ]
        
        return user_transactions
    except Exception as e:
        print(f"Error loading user history: {str(e)}")
    
    # Fallback to empty DataFrame with correct structure
    return pd.DataFrame(columns=[
        'transaction_id', 'user_id', 'timestamp', 'amount', 
        'merchant', 'category', 'is_fraud'
    ])

def extract_features(transaction_df, user_history_df=None):
    """
    Extract features from transaction data and user history
    
    Args:
        transaction_df (pandas.DataFrame): Current transaction
        user_history_df (pandas.DataFrame): User's transaction history
        
    Returns:
        pandas.DataFrame: Features for model input
    """
    # Create a copy to avoid modifying the original
    features = transaction_df.copy()
    
    # Extract time-based features
    if 'timestamp' in features.columns:
        features['hour_of_day'] = features['timestamp'].dt.hour
        features['day_of_week'] = features['timestamp'].dt.dayofweek
        features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
        
        # Time of day segments
        hour = features['timestamp'].dt.hour
        features['is_business_hours'] = ((hour >= 9) & (hour <= 17)).astype(int)
        features['is_evening'] = ((hour >= 18) & (hour <= 22)).astype(int)
        features['is_night'] = ((hour >= 23) | (hour <= 5)).astype(int)
    
    # If we have user history, calculate behavioral features
    if user_history_df is not None and not user_history_df.empty:
        # Average transaction amount
        avg_amount = user_history_df['amount'].mean()
        features['amount_vs_avg'] = features['amount'] / avg_amount if avg_amount > 0 else 0
        
        # Standard deviation of amounts
        std_amount = user_history_df['amount'].std()
        if not pd.isna(std_amount) and std_amount > 0:
            features['amount_zscore'] = (features['amount'] - avg_amount) / std_amount
        else:
            features['amount_zscore'] = 0
        
        # Transaction frequency
        days_active = (user_history_df['timestamp'].max() - user_history_df['timestamp'].min()).days
        tx_count = len(user_history_df)
        features['tx_frequency'] = tx_count / (days_active + 1)  # Add 1 to avoid division by zero
        
        # Time since last transaction
        if 'timestamp' in features.columns:
            last_tx_time = user_history_df['timestamp'].max()
            current_tx_time = features['timestamp'].iloc[0]
            time_diff = (current_tx_time - last_tx_time).total_seconds() / 3600  # hours
            features['hours_since_last_tx'] = time_diff
        
        # New merchant?
        if 'merchant' in features.columns and 'merchant' in user_history_df.columns:
            features['new_merchant'] = (~features['merchant'].isin(user_history_df['merchant'])).astype(int)
        
        # New category?
        if 'category' in features.columns and 'category' in user_history_df.columns:
            features['new_category'] = (~features['category'].isin(user_history_df['category'])).astype(int)
        
        # Merchant frequency
        if 'merchant' in features.columns and 'merchant' in user_history_df.columns:
            merchant = features['merchant'].iloc[0]
            merchant_count = user_history_df[user_history_df['merchant'] == merchant].shape[0]
            features['merchant_frequency'] = merchant_count / tx_count if tx_count > 0 else 0
        
        # Category frequency
        if 'category' in features.columns and 'category' in user_history_df.columns:
            category = features['category'].iloc[0]
            category_count = user_history_df[user_history_df['category'] == category].shape[0]
            features['category_frequency'] = category_count / tx_count if tx_count > 0 else 0
    else:
        # No history available
        features['amount_vs_avg'] = 1.0
        features['amount_zscore'] = 0.0
        features['tx_frequency'] = 0.0
        features['hours_since_last_tx'] = 24.0 * 30  # Assume 30 days
        features['new_merchant'] = 1
        features['new_category'] = 1
        features['merchant_frequency'] = 0.0
        features['category_frequency'] = 0.0
    
    # Add high amount flag
    features['high_amount'] = (features['amount'] > 1000).astype(int)
    
    # Drop columns not used by the model
    cols_to_drop = ['transaction_id', 'user_id', 'timestamp', 'is_fraud']
    features = features.drop([col for col in cols_to_drop if col in features.columns], axis=1)
    
    # Convert categorical variables to numeric
    for col in features.select_dtypes(['object']).columns:
        features[col] = features[col].astype('category').cat.codes
    
    return features

def preprocess_batch(transactions_df):
    """
    Preprocess a batch of transactions
    
    Args:
        transactions_df (pandas.DataFrame): Batch of transactions
        
    Returns:
        pandas.DataFrame: Preprocessed features
    """
    # Create a copy to avoid modifying the original
    df = transactions_df.copy()
    
    # Convert timestamp to datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Extract time-based features
    if 'timestamp' in df.columns:
        df['hour_of_day'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Time of day segments
        hour = df['timestamp'].dt.hour
        df['is_business_hours'] = ((hour >= 9) & (hour <= 17)).astype(int)
        df['is_evening'] = ((hour >= 18) & (hour <= 22)).astype(int)
        df['is_night'] = ((hour >= 23) | (hour <= 5)).astype(int)
    
    # Group by user to calculate user-level features
    if 'user_id' in df.columns:
        user_stats = df.groupby('user_id').agg({
            'amount': ['mean', 'std', 'count'],
            'timestamp': ['min', 'max']
        })
        
        user_stats.columns = ['_'.join(col).strip() for col in user_stats.columns.values]
        user_stats.reset_index(inplace=True)
        
        # Calculate user activity days
        user_stats['activity_days'] = (user_stats['timestamp_max'] - user_stats['timestamp_min']).dt.days + 1
        
        # Calculate transaction frequency
        user_stats['tx_frequency'] = user_stats['amount_count'] / user_stats['activity_days']
        
        # Merge back to main data
        df = pd.merge(df, user_stats, on='user_id', how='left')
        
        # Calculate relative amount
        df['amount_vs_avg'] = df['amount'] / df['amount_mean']
        
        # Calculate z-score
        df['amount_zscore'] = (df['amount'] - df['amount_mean']) / df['amount_std']
        df['amount_zscore'].fillna(0, inplace=True)
    
    # Add high amount flag
    df['high_amount'] = (df['amount'] > 1000).astype(int)
    
    # Drop columns not used by the model
    cols_to_drop = ['transaction_id', 'timestamp', 'timestamp_min', 'timestamp_max']
    df = df.drop([col for col in cols_to_drop if col in df.columns], axis=1)
    
    # Convert categorical variables to numeric
    for col in df.select_dtypes(['object']).columns:
        df[col] = df[col].astype('category').cat.codes
    
    # Handle missing values
    df.fillna(0, inplace=True)
    
    return df