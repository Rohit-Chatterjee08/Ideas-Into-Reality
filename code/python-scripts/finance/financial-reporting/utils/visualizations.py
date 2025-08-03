#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualizations Module for Financial Reporting System

This module provides functions to create various visualizations
for financial reports using matplotlib, seaborn, and plotly.

Author: NinjaTech AI
Date: August 2025
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

def set_styling():
    """
    Set consistent styling for matplotlib plots
    """
    sns.set(style="whitegrid")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    
    # Use a professional color palette
    sns.set_palette("muted")

def save_plot(plt, filename, directory="reports/figures"):
    """
    Save matplotlib plot to file
    
    Args:
        plt: Matplotlib pyplot object
        filename (str): Output filename
        directory (str): Output directory
        
    Returns:
        str: Path to saved file
    """
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    file_path = os.path.join(directory, filename)
    plt.savefig(file_path, bbox_inches='tight', dpi=300)
    plt.close()
    return file_path

def plot_time_series(df, date_column, value_column, title, filename):
    """
    Create time series plot
    
    Args:
        df (pandas.DataFrame): Data to plot
        date_column (str): Name of date column
        value_column (str): Name of value column
        title (str): Plot title
        filename (str): Output filename
        
    Returns:
        str: Path to saved plot
    """
    set_styling()
    plt.figure()
    
    sns.lineplot(data=df, x=date_column, y=value_column, marker='o', linewidth=2)
    
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return save_plot(plt, filename)

def plot_category_breakdown(df, category_column, value_column, title, filename):
    """
    Create pie chart for category breakdown
    
    Args:
        df (pandas.DataFrame): Data to plot
        category_column (str): Name of category column
        value_column (str): Name of value column
        title (str): Plot title
        filename (str): Output filename
        
    Returns:
        str: Path to saved plot
    """
    set_styling()
    plt.figure()
    
    # Get top categories (limit to 8 for readability)
    top_categories = df.nlargest(8, value_column)
    
    # If there are more categories, group the rest as "Other"
    if len(df) > 8:
        other_sum = df.nsmallest(len(df) - 8, value_column)[value_column].sum()
        other_row = pd.DataFrame({category_column: ['Other'], value_column: [other_sum]})
        top_categories = pd.concat([top_categories, other_row])
    
    # Create pie chart
    plt.pie(top_categories[value_column], 
            labels=top_categories[category_column], 
            autopct='%1.1f%%', 
            startangle=90,
            shadow=False,
            explode=[0.05 if i == 0 else 0 for i in range(len(top_categories))],
            wedgeprops={'linewidth': 1, 'edgecolor': 'white'})
    
    plt.axis('equal')
    plt.title(title)
    
    return save_plot(plt, filename)

def plot_monthly_trend(df, title, filename):
    """
    Create monthly trend chart with actual vs moving average
    
    Args:
        df (pandas.DataFrame): Monthly data with 'sum' and '3m_avg' columns
        title (str): Plot title
        filename (str): Output filename
        
    Returns:
        str: Path to saved plot
    """
    set_styling()
    fig, ax = plt.subplots()
    
    # Convert index to string for better display
    x_values = df.index.astype(str)
    
    # Plot monthly total
    ax.plot(x_values, df['sum'], marker='o', linewidth=2, label='Monthly Total')
    
    # Plot 3-month moving average
    ax.plot(x_values, df['3m_avg'], linestyle='--', linewidth=2, label='3-Month Average')
    
    # Add 12-month moving average if available
    if '12m_avg' in df.columns:
        ax.plot(x_values, df['12m_avg'], linestyle=':', linewidth=2, label='12-Month Average')
    
    # Add month-over-month percentage change as text
    for i, (idx, row) in enumerate(df.iterrows()):
        if i > 0 and 'mom_change' in df.columns and not np.isnan(row['mom_change']):
            change_text = f"{row['mom_change']:.1f}%" if abs(row['mom_change']) < 100 else f"{row['mom_change']:.0f}%"
            color = 'green' if row['mom_change'] > 0 else 'red'
            ax.annotate(change_text, 
                       (i, row['sum']), 
                       textcoords="offset points", 
                       xytext=(0,10), 
                       ha='center',
                       color=color,
                       fontweight='bold' if abs(row['mom_change']) > 10 else 'normal')
    
    plt.title(title)
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    return save_plot(plt, filename)

def plot_pareto_chart(df, category_column, value_column, title, filename):
    """
    Create a Pareto chart (bar chart with cumulative line)
    
    Args:
        df (pandas.DataFrame): Data to plot
        category_column (str): Name of category column
        value_column (str): Name of value column
        title (str): Plot title
        filename (str): Output filename
        
    Returns:
        str: Path to saved plot
    """
    set_styling()
    fig, ax1 = plt.subplots()
    
    # Sort data by value
    df_sorted = df.sort_values(value_column, ascending=False).reset_index()
    
    # Calculate cumulative percentage
    df_sorted['cumulative_pct'] = df_sorted[value_column].cumsum() / df_sorted[value_column].sum() * 100
    
    # Create bar chart
    ax1.bar(df_sorted[category_column], df_sorted[value_column], color='steelblue')
    ax1.set_xlabel('Category')
    ax1.set_ylabel('Value', color='steelblue')
    ax1.tick_params(axis='y', labelcolor='steelblue')
    
    # Create cumulative percentage line
    ax2 = ax1.twinx()
    ax2.plot(df_sorted[category_column], df_sorted['cumulative_pct'], 'ro-', linewidth=2)
    ax2.set_ylabel('Cumulative Percentage', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.set_ylim([0, 105])
    
    # Add 80% line
    ax2.axhline(y=80, color='gray', linestyle='--', alpha=0.7)
    
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    return save_plot(plt, filename)

def plot_comparison_chart(current, previous, title, filename):
    """
    Create a comparison bar chart between two periods
    
    Args:
        current (pandas.Series): Current period data
        previous (pandas.Series): Previous period data
        title (str): Plot title
        filename (str): Output filename
        
    Returns:
        str: Path to saved plot
    """
    set_styling()
    fig, ax = plt.subplots()
    
    # Set up bar positions
    categories = current.index
    x = np.arange(len(categories))
    width = 0.35
    
    # Create bars
    ax.bar(x - width/2, current, width, label='Current Period')
    ax.bar(x + width/2, previous, width, label='Previous Period')
    
    # Add percentage change
    for i, (curr, prev) in enumerate(zip(current, previous)):
        if prev != 0:
            pct_change = ((curr - prev) / prev) * 100
            color = 'green' if pct_change > 0 else 'red'
            ax.annotate(f"{pct_change:.1f}%", 
                       (i, max(curr, prev)), 
                       textcoords="offset points", 
                       xytext=(0,10), 
                       ha='center',
                       color=color)
    
    # Customize chart
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.legend()
    
    plt.title(title)
    plt.tight_layout()
    
    return save_plot(plt, filename)

def create_interactive_dashboard(df, date_column, amount_column, category_column):
    """
    Create interactive Plotly dashboard
    
    Args:
        df (pandas.DataFrame): Data to visualize
        date_column (str): Name of date column
        amount_column (str): Name of amount column
        category_column (str): Name of category column
        
    Returns:
        str: Path to saved HTML dashboard
    """
    # Ensure date column is datetime
    df[date_column] = pd.to_datetime(df[date_column])
    
    # Create output directory
    os.makedirs("reports/interactive", exist_ok=True)
    
    # Time series chart
    fig1 = px.line(df, x=date_column, y=amount_column, 
                  title='Time Series Analysis',
                  labels={date_column: 'Date', amount_column: 'Amount'},
                  template='plotly_white')
    
    fig1.update_layout(
        xaxis_title='Date',
        yaxis_title='Amount',
        legend_title='Legend',
        hovermode='x unified'
    )
    
    # Category breakdown
    category_data = df.groupby(category_column)[amount_column].sum().reset_index()
    fig2 = px.pie(category_data, values=amount_column, names=category_column, 
                 title='Category Distribution',
                 template='plotly_white',
                 hole=0.4)
    
    fig2.update_traces(textposition='inside', textinfo='percent+label')
    
    # Monthly trend
    monthly_data = df.groupby(pd.Grouper(key=date_column, freq='M'))[amount_column].sum().reset_index()
    monthly_data['Month'] = monthly_data[date_column].dt.strftime('%b %Y')
    
    fig3 = px.bar(monthly_data, x='Month', y=amount_column, 
                 title='Monthly Trend',
                 template='plotly_white')
    
    fig3.update_layout(
        xaxis_title='Month',
        yaxis_title='Amount',
        hovermode='x unified'
    )
    
    # Save individual charts
    fig1.write_html("reports/interactive/time_series.html")
    fig2.write_html("reports/interactive/category_breakdown.html")
    fig3.write_html("reports/interactive/monthly_trend.html")
    
    # Create a combined dashboard
    dashboard = go.Figure()
    
    # Create a subplot layout
    from plotly.subplots import make_subplots
    dashboard = make_subplots(
        rows=2, cols=2,
        specs=[[{"colspan": 2}, None],
               [{}, {}]],
        subplot_titles=("Time Series Analysis", "Category Distribution", "Monthly Trend")
    )
    
    # Add time series trace
    for trace in fig1.data:
        dashboard.add_trace(trace, row=1, col=1)
    
    # Add pie chart trace
    for trace in fig2.data:
        dashboard.add_trace(trace, row=2, col=1)
    
    # Add bar chart trace
    for trace in fig3.data:
        dashboard.add_trace(trace, row=2, col=2)
    
    # Update layout
    dashboard.update_layout(
        title_text="Financial Dashboard",
        height=900,
        template='plotly_white'
    )
    
    # Save dashboard
    dashboard_path = "reports/interactive/dashboard.html"
    dashboard.write_html(dashboard_path)
    
    return dashboard_path