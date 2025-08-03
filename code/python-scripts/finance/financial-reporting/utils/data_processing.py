#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Processing Module for Financial Reporting System

This module provides functions to clean, transform, and analyze
financial data for reporting purposes.

Author: NinjaTech AI
Date: August 2025
"""

import pandas as pd
import numpy as np

def clean_financial_data(df):
    """
    Clean and prepare financial data
    
    Args:
        df (pandas.DataFrame): Raw financial data
        
    Returns:
        pandas.DataFrame: Cleaned data
    """
    # Create a copy to avoid modifying the original
    df = df.copy()
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Handle missing values
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].fillna(0)
    
    # Convert date columns
    date_columns = [col for col in df.columns if 'date' in col.lower()]
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Drop rows with missing dates in date columns
    if date_columns:
        df = df.dropna(subset=date_columns)
    
    return df

def calculate_financial_metrics(df, date_column, amount_column):
    """
    Calculate key financial metrics
    
    Args:
        df (pandas.DataFrame): Financial data
        date_column (str): Name of date column
        amount_column (str): Name of amount column
        
    Returns:
        pandas.DataFrame: Calculated metrics
    """
    # Create a copy to avoid modifying the original
    df = df.copy()
    
    # Ensure date column is datetime
    df[date_column] = pd.to_datetime(df[date_column])
    
    # Group by date (month)
    df['month'] = df[date_column].dt.to_period('M')
    monthly = df.groupby('month')[amount_column].agg(['sum', 'mean', 'count'])
    
    # Calculate cumulative sum
    monthly['cumulative'] = monthly['sum'].cumsum()
    
    # Calculate month-over-month change
    monthly['mom_change'] = monthly['sum'].pct_change() * 100
    
    # Calculate rolling metrics
    monthly['3m_avg'] = monthly['sum'].rolling(3).mean()
    monthly['12m_avg'] = monthly['sum'].rolling(12).mean()
    
    # Calculate year-over-year change if enough data
    if len(monthly) >= 13:
        monthly['yoy_change'] = monthly['sum'].pct_change(12) * 100
    
    return monthly

def segment_by_category(df, category_column, amount_column):
    """
    Segment data by category
    
    Args:
        df (pandas.DataFrame): Financial data
        category_column (str): Name of category column
        amount_column (str): Name of amount column
        
    Returns:
        pandas.DataFrame: Category segments with metrics
    """
    # Create a copy to avoid modifying the original
    df = df.copy()
    
    # Group by category
    category_totals = df.groupby(category_column)[amount_column].agg(['sum', 'mean', 'count'])
    
    # Calculate percentage of total
    total_sum = category_totals['sum'].sum()
    category_totals['percentage'] = (category_totals['sum'] / total_sum) * 100
    
    # Calculate cumulative percentage (for Pareto analysis)
    category_totals = category_totals.sort_values('sum', ascending=False)
    category_totals['cumulative_percentage'] = category_totals['percentage'].cumsum()
    
    return category_totals

def detect_anomalies(df, column, threshold=3):
    """
    Detect anomalies using Z-score
    
    Args:
        df (pandas.DataFrame): Financial data
        column (str): Column to analyze for anomalies
        threshold (float): Z-score threshold for anomaly detection
        
    Returns:
        pandas.DataFrame: Anomalies with z-scores
    """
    # Create a copy to avoid modifying the original
    df = df.copy()
    
    # Calculate mean and standard deviation
    mean = df[column].mean()
    std = df[column].std()
    
    # Calculate Z-score
    df['z_score'] = (df[column] - mean) / std
    
    # Identify anomalies
    anomalies = df[df['z_score'].abs() > threshold].copy()
    
    # Add deviation percentage
    anomalies['deviation_pct'] = ((anomalies[column] - mean) / mean) * 100
    
    return anomalies.sort_values('z_score', ascending=False)

def calculate_period_comparison(df, date_column, amount_column, periods=None):
    """
    Calculate period-over-period comparisons
    
    Args:
        df (pandas.DataFrame): Financial data
        date_column (str): Name of date column
        amount_column (str): Name of amount column
        periods (dict): Dictionary of period names and their durations in days
        
    Returns:
        pandas.DataFrame: Period comparisons
    """
    # Create a copy to avoid modifying the original
    df = df.copy()
    
    # Ensure date column is datetime
    df[date_column] = pd.to_datetime(df[date_column])
    
    # Default periods if none provided
    if periods is None:
        periods = {
            'Current Month': 30,
            'Previous Month': 60,
            'Current Quarter': 90,
            'Previous Quarter': 180,
            'Current Year': 365,
            'Previous Year': 730
        }
    
    # Get current date (max date in dataset)
    current_date = df[date_column].max()
    
    # Calculate metrics for each period
    results = {}
    
    for period_name, days in periods.items():
        period_start = current_date - pd.Timedelta(days=days)
        period_end = current_date - pd.Timedelta(days=days/2) if 'Previous' in period_name else current_date
        
        period_data = df[(df[date_column] >= period_start) & (df[date_column] <= period_end)]
        
        results[period_name] = {
            'total': period_data[amount_column].sum(),
            'average': period_data[amount_column].mean(),
            'count': len(period_data),
            'min': period_data[amount_column].min(),
            'max': period_data[amount_column].max()
        }
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results).T
    
    # Calculate period-over-period changes
    for i in range(0, len(results_df), 2):
        if i+1 < len(results_df):
            current = results_df.iloc[i]['total']
            previous = results_df.iloc[i+1]['total']
            
            if previous != 0:
                change_pct = ((current - previous) / previous) * 100
                results_df.loc[results_df.index[i], 'change_pct'] = change_pct
    
    return results_df