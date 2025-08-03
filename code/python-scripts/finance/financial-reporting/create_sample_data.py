#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sample Data Generator for Financial Reporting System

This script generates realistic sample data for testing the
Automated Financial Reporting System.

Author: NinjaTech AI
Date: August 2025
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_transactions(num_records=1000):
    """
    Generate sample transaction data
    
    Args:
        num_records (int): Number of records to generate
        
    Returns:
        pandas.DataFrame: Generated transaction data
    """
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate dates for the past year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days)]
    
    # Generate random transaction data
    transactions = []
    categories = ['Sales', 'Services', 'Subscriptions', 'Licensing', 'Consulting']
    
    for i in range(num_records):
        date = np.random.choice(dates)
        category = np.random.choice(categories)
        
        # Base amount by category
        if category == 'Sales':
            base_amount = 500
        elif category == 'Services':
            base_amount = 1000
        elif category == 'Subscriptions':
            base_amount = 50
        elif category == 'Licensing':
            base_amount = 2000
        else:  # Consulting
            base_amount = 1500
        
        # Add some randomness
        amount = base_amount * (0.5 + np.random.random())
        
        # Add some seasonality
        month = date.month
        if month in [11, 12]:  # Holiday season
            amount *= 1.3
        elif month in [1, 2]:  # Post-holiday slump
            amount *= 0.8
        
        # Add some anomalies (1% chance)
        if np.random.random() < 0.01:
            amount *= 10
        
        transactions.append({
            'transaction_id': f"TRX-{i:06d}",
            'transaction_date': date.strftime('%Y-%m-%d'),
            'category': category,
            'amount': round(amount, 2),
            'customer_id': f"CUST-{np.random.randint(1, 101):03d}",
            'payment_method': np.random.choice(['Credit Card', 'Bank Transfer', 'PayPal', 'Check']),
            'region': np.random.choice(['North', 'South', 'East', 'West', 'Central'])
        })
    
    return pd.DataFrame(transactions)

def generate_expenses(num_records=500):
    """
    Generate sample expense data
    
    Args:
        num_records (int): Number of records to generate
        
    Returns:
        pandas.DataFrame: Generated expense data
    """
    # Set random seed for reproducibility
    np.random.seed(43)
    
    # Generate dates for the past year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days)]
    
    # Generate random expense data
    expenses = []
    categories = ['Rent', 'Salaries', 'Marketing', 'Equipment', 'Utilities', 
                 'Travel', 'Software', 'Office Supplies', 'Insurance', 'Taxes']
    
    for i in range(num_records):
        date = np.random.choice(dates)
        category = np.random.choice(categories)
        
        # Base amount by category
        if category == 'Rent':
            base_amount = 5000
        elif category == 'Salaries':
            base_amount = 4000
        elif category == 'Marketing':
            base_amount = 2000
        elif category == 'Equipment':
            base_amount = 1500
        elif category == 'Utilities':
            base_amount = 800
        elif category == 'Travel':
            base_amount = 1200
        elif category == 'Software':
            base_amount = 500
        elif category == 'Office Supplies':
            base_amount = 300
        elif category == 'Insurance':
            base_amount = 1000
        else:  # Taxes
            base_amount = 3000
        
        # Add some randomness
        amount = base_amount * (0.8 + 0.4 * np.random.random())
        
        # Add some seasonality for certain categories
        month = date.month
        if category == 'Marketing' and month in [11, 12]:  # Holiday marketing
            amount *= 1.5
        elif category == 'Travel' and month in [6, 7, 8]:  # Summer travel
            amount *= 1.3
        elif category == 'Utilities' and month in [12, 1, 2]:  # Winter utilities
            amount *= 1.2
        
        # Add some anomalies (1% chance)
        if np.random.random() < 0.01:
            amount *= 5
        
        expenses.append({
            'expense_id': f"EXP-{i:06d}",
            'expense_date': date.strftime('%Y-%m-%d'),
            'category': category,
            'amount': round(amount, 2),
            'department': np.random.choice(['Sales', 'Marketing', 'Engineering', 'HR', 'Finance', 'Operations']),
            'payment_method': np.random.choice(['Credit Card', 'Bank Transfer', 'Cash', 'Check']),
            'approved_by': f"EMP-{np.random.randint(1, 21):03d}"
        })
    
    return pd.DataFrame(expenses)

def generate_budget(categories, start_date, end_date):
    """
    Generate sample budget data
    
    Args:
        categories (list): List of expense categories
        start_date (datetime): Budget start date
        end_date (datetime): Budget end date
        
    Returns:
        pandas.DataFrame: Generated budget data
    """
    # Set random seed for reproducibility
    np.random.seed(44)
    
    # Generate monthly budget data
    budget = []
    current_date = start_date
    
    while current_date <= end_date:
        for category in categories:
            # Base budget by category
            if category == 'Rent':
                base_amount = 5500
            elif category == 'Salaries':
                base_amount = 45000
            elif category == 'Marketing':
                base_amount = 25000
            elif category == 'Equipment':
                base_amount = 10000
            elif category == 'Utilities':
                base_amount = 1000
            elif category == 'Travel':
                base_amount = 8000
            elif category == 'Software':
                base_amount = 3000
            elif category == 'Office Supplies':
                base_amount = 1500
            elif category == 'Insurance':
                base_amount = 2000
            else:  # Taxes
                base_amount = 15000
            
            # Add some randomness (smaller variance for budget)
            amount = base_amount * (0.95 + 0.1 * np.random.random())
            
            budget.append({
                'budget_id': f"BUD-{len(budget):06d}",
                'month': current_date.strftime('%Y-%m'),
                'category': category,
                'amount': round(amount, 2)
            })
        
        # Move to next month
        year = current_date.year + ((current_date.month + 1) // 13)
        month = (current_date.month % 12) + 1
        current_date = datetime(year, month, 1)
    
    return pd.DataFrame(budget)

def main():
    """Generate and save sample data"""
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    # Generate transaction data
    transactions_df = generate_transactions(1000)
    transactions_df.to_csv("data/transactions.csv", index=False)
    print(f"Generated {len(transactions_df)} transactions")
    
    # Generate expense data
    expenses_df = generate_expenses(500)
    expenses_df.to_csv("data/expenses.csv", index=False)
    print(f"Generated {len(expenses_df)} expenses")
    
    # Generate budget data
    categories = ['Rent', 'Salaries', 'Marketing', 'Equipment', 'Utilities', 
                 'Travel', 'Software', 'Office Supplies', 'Insurance', 'Taxes']
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    budget_df = generate_budget(categories, start_date, end_date)
    budget_df.to_csv("data/budget.csv", index=False)
    print(f"Generated {len(budget_df)} budget entries")
    
    print("Sample data generation complete. Files saved to data/ directory.")

if __name__ == "__main__":
    main()