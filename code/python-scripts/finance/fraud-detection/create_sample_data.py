#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sample Data Generator for Fraud Detection Engine

This script generates realistic sample data for testing and training
the Fraud Detection Engine.

Author: NinjaTech AI
Date: August 2025
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid

def generate_users(num_users=100):
    """
    Generate sample user data
    
    Args:
        num_users (int): Number of users to generate
        
    Returns:
        list: User data
    """
    users = []
    
    for i in range(num_users):
        user_id = f"USER-{i:06d}"
        
        # Assign user to a risk segment
        risk_segment = np.random.choice(['low', 'medium', 'high'], p=[0.7, 0.25, 0.05])
        
        users.append({
            'user_id': user_id,
            'risk_segment': risk_segment,
            'account_age_days': np.random.randint(1, 1000),
            'typical_amount': np.random.uniform(50, 500)
        })
    
    return users

def generate_transactions(users, num_transactions=1000, fraud_rate=0.01):
    """
    Generate sample transaction data
    
    Args:
        users (list): User data
        num_transactions (int): Number of transactions to generate
        fraud_rate (float): Proportion of fraudulent transactions
        
    Returns:
        list: Transaction data
    """
    transactions = []
    
    # Generate dates for the past month
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Define merchant categories
    categories = [
        'Retail', 'Dining', 'Travel', 'Entertainment', 
        'Groceries', 'Utilities', 'Services', 'Healthcare'
    ]
    
    # Generate transactions
    for i in range(num_transactions):
        # Select a user
        user = np.random.choice(users)
        user_id = user['user_id']
        
        # Generate transaction details
        timestamp = start_date + timedelta(
            seconds=np.random.randint(0, int((end_date - start_date).total_seconds()))
        )
        
        category = np.random.choice(categories)
        
        # Base amount on user's typical amount
        typical_amount = user['typical_amount']
        amount = np.random.normal(typical_amount, typical_amount * 0.2)
        amount = max(1, amount)  # Ensure positive amount
        
        # Determine if this transaction is fraudulent
        is_fraud = np.random.random() < fraud_rate
        
        # If fraudulent, modify the transaction to look suspicious
        if is_fraud:
            # Increase amount significantly
            amount *= np.random.uniform(5, 20)
            
            # More likely to be in certain categories
            if np.random.random() < 0.7:
                category = np.random.choice(['Travel', 'Entertainment', 'Services'])
        
        # Generate merchant name based on category
        merchants = {
            'Retail': ['Amazon', 'Walmart', 'Target', 'Best Buy', 'Apple Store'],
            'Dining': ['McDonalds', 'Starbucks', 'Chipotle', 'Olive Garden', 'Local Restaurant'],
            'Travel': ['Expedia', 'Airbnb', 'Delta Airlines', 'Uber', 'Marriott'],
            'Entertainment': ['Netflix', 'AMC Theaters', 'Spotify', 'Steam', 'Disney+'],
            'Groceries': ['Kroger', 'Whole Foods', 'Safeway', 'Trader Joes', 'Aldi'],
            'Utilities': ['Electric Company', 'Water Service', 'Gas Company', 'Internet Provider', 'Phone Company'],
            'Services': ['Cleaning Service', 'Lawn Care', 'Plumber', 'Electrician', 'Consultant'],
            'Healthcare': ['Pharmacy', 'Doctor Office', 'Hospital', 'Dental Clinic', 'Vision Center']
        }
        
        merchant = np.random.choice(merchants.get(category, ['Unknown']))
        
        # Create transaction
        transaction = {
            'transaction_id': f"TRX-{i:06d}",
            'user_id': user_id,
            'timestamp': timestamp.isoformat(),
            'amount': round(amount, 2),
            'merchant': merchant,
            'category': category,
            'payment_method': np.random.choice(['Credit Card', 'Debit Card', 'PayPal', 'Bank Transfer']),
            'is_fraud': int(is_fraud)
        }
        
        transactions.append(transaction)
    
    return transactions

def generate_fraud_patterns(users, num_transactions=50):
    """
    Generate specific fraud patterns for testing
    
    Args:
        users (list): User data
        num_transactions (int): Number of transactions to generate
        
    Returns:
        list: Transaction data with fraud patterns
    """
    transactions = []
    
    # Current date and time
    now = datetime.now()
    
    # Pattern 1: Multiple high-value transactions in short time
    user = np.random.choice(users)
    user_id = user['user_id']
    
    for i in range(5):
        timestamp = now - timedelta(minutes=i*15)
        
        transaction = {
            'transaction_id': f"FRAUD-P1-{i}",
            'user_id': user_id,
            'timestamp': timestamp.isoformat(),
            'amount': round(np.random.uniform(1000, 5000), 2),
            'merchant': np.random.choice(['Best Buy', 'Apple Store', 'Jewelry Store']),
            'category': 'Retail',
            'payment_method': 'Credit Card',
            'is_fraud': 1
        }
        
        transactions.append(transaction)
    
    # Pattern 2: Unusual location/time transactions
    user = np.random.choice(users)
    user_id = user['user_id']
    
    for i in range(3):
        timestamp = now - timedelta(hours=i) - timedelta(minutes=np.random.randint(0, 60))
        timestamp = timestamp.replace(hour=3)  # 3 AM transactions
        
        transaction = {
            'transaction_id': f"FRAUD-P2-{i}",
            'user_id': user_id,
            'timestamp': timestamp.isoformat(),
            'amount': round(np.random.uniform(100, 500), 2),
            'merchant': np.random.choice(['Gas Station', 'ATM', 'Convenience Store']),
            'category': np.random.choice(['Retail', 'Services']),
            'payment_method': 'Credit Card',
            'is_fraud': 1
        }
        
        transactions.append(transaction)
    
    # Pattern 3: Unusual merchant category
    user = np.random.choice(users)
    user_id = user['user_id']
    
    for i in range(3):
        timestamp = now - timedelta(hours=i*2)
        
        transaction = {
            'transaction_id': f"FRAUD-P3-{i}",
            'user_id': user_id,
            'timestamp': timestamp.isoformat(),
            'amount': round(np.random.uniform(500, 2000), 2),
            'merchant': f"Unknown Merchant {uuid.uuid4().hex[:8]}",
            'category': 'Services',
            'payment_method': 'Credit Card',
            'is_fraud': 1
        }
        
        transactions.append(transaction)
    
    # Pattern 4: Amount just below threshold
    user = np.random.choice(users)
    user_id = user['user_id']
    
    for i in range(5):
        timestamp = now - timedelta(days=i)
        
        transaction = {
            'transaction_id': f"FRAUD-P4-{i}",
            'user_id': user_id,
            'timestamp': timestamp.isoformat(),
            'amount': 999.99,  # Just below 1000
            'merchant': np.random.choice(['Online Store', 'Electronics Shop', 'Department Store']),
            'category': 'Retail',
            'payment_method': 'Credit Card',
            'is_fraud': 1
        }
        
        transactions.append(transaction)
    
    # Fill remaining transactions with random fraud
    remaining = num_transactions - len(transactions)
    if remaining > 0:
        random_fraud = generate_transactions(users, remaining, fraud_rate=1.0)
        transactions.extend(random_fraud)
    
    return transactions

def main():
    """Generate and save sample data"""
    # Create directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Generate users
    print("Generating users...")
    users = generate_users(100)
    
    # Save users
    with open("data/users.json", 'w') as f:
        json.dump(users, f, indent=2)
    
    # Generate training transactions
    print("Generating training transactions...")
    training_transactions = generate_transactions(users, 5000, fraud_rate=0.05)
    
    # Save as CSV for training
    pd.DataFrame(training_transactions).to_csv("data/fraud_training_data.csv", index=False)
    
    # Generate test transactions
    print("Generating test transactions...")
    test_transactions = generate_transactions(users, 100, fraud_rate=0.1)
    
    # Generate specific fraud patterns
    print("Generating fraud patterns...")
    fraud_patterns = generate_fraud_patterns(users, 50)
    
    # Combine with test transactions
    test_transactions.extend(fraud_patterns)
    
    # Save as JSON for testing
    with open("data/test_transactions.json", 'w') as f:
        json.dump(test_transactions, f, indent=2)
    
    # Generate real-time simulation data
    print("Generating real-time simulation data...")
    realtime_transactions = generate_transactions(users, 200, fraud_rate=0.05)
    
    # Save as JSON for real-time simulation
    with open("data/realtime_transactions.json", 'w') as f:
        json.dump(realtime_transactions, f, indent=2)
    
    print("Sample data generation complete!")
    print(f"Generated {len(users)} users")
    print(f"Generated {len(training_transactions)} training transactions")
    print(f"Generated {len(test_transactions)} test transactions")
    print(f"Generated {len(realtime_transactions)} real-time simulation transactions")

if __name__ == "__main__":
    main()