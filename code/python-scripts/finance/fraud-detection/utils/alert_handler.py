#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alert Handler Module for Fraud Detection Engine

This module provides functions to create and handle fraud alerts.

Author: NinjaTech AI
Date: August 2025
"""

import os
import json
import requests
from datetime import datetime
import uuid

def create_alert(transaction, fraud_result, config):
    """
    Create a fraud alert from detection results
    
    Args:
        transaction (dict): Original transaction data
        fraud_result (dict): Results from fraud detection
        config (dict): Alert configuration
        
    Returns:
        dict: Alert data
    """
    # Generate a unique alert ID
    alert_id = f"FRAUD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
    
    # Create alert object
    alert = {
        'alert_id': alert_id,
        'timestamp': datetime.now().isoformat(),
        'transaction_id': transaction.get('transaction_id', ''),
        'user_id': transaction.get('user_id', ''),
        'amount': transaction.get('amount', 0),
        'merchant': transaction.get('merchant', ''),
        'category': transaction.get('category', ''),
        'transaction_timestamp': transaction.get('timestamp', ''),
        'fraud_score': fraud_result.get('fraud_score', 0),
        'is_fraud': fraud_result.get('is_fraud', False),
        'confidence': fraud_result.get('confidence', 0),
        'model_scores': fraud_result.get('model_scores', {}),
        'top_factors': fraud_result.get('top_factors', {}),
        'rules_applied': fraud_result.get('rules_applied', []),
        'status': 'new',
        'priority': calculate_priority(transaction, fraud_result)
    }
    
    return alert

def calculate_priority(transaction, fraud_result):
    """
    Calculate alert priority based on transaction and fraud result
    
    Args:
        transaction (dict): Transaction data
        fraud_result (dict): Fraud detection results
        
    Returns:
        str: Priority level (high, medium, low)
    """
    # Default to medium
    priority = 'medium'
    
    # High priority if high confidence and high amount
    if (fraud_result.get('confidence', 0) > 0.8 and 
        transaction.get('amount', 0) > 1000):
        priority = 'high'
    # Also high priority if very high fraud score
    elif fraud_result.get('fraud_score', 0) > 0.9:
        priority = 'high'
    # Low priority if low confidence or small amount
    elif (fraud_result.get('confidence', 0) < 0.6 or 
          transaction.get('amount', 0) < 100):
        priority = 'low'
    
    return priority

def send_alert_webhook(alert, webhook_url):
    """
    Send alert to webhook (e.g., N8N)
    
    Args:
        alert (dict): Alert data
        webhook_url (str): Webhook URL
        
    Returns:
        bool: Success status
    """
    try:
        # If webhook URL is not specified, use environment variable
        if not webhook_url:
            webhook_url = os.getenv("WEBHOOK_URL")
        
        # If still no webhook URL, return False
        if not webhook_url:
            print("No webhook URL specified")
            return False
        
        # Send alert to webhook
        response = requests.post(
            webhook_url,
            json=alert,
            headers={'Content-Type': 'application/json'}
        )
        
        # Check response
        if response.status_code == 200:
            print(f"Alert {alert['alert_id']} sent to webhook successfully")
            return True
        else:
            print(f"Error sending alert to webhook: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error sending alert to webhook: {str(e)}")
        return False

def log_alert(alert, log_file=None):
    """
    Log alert to file
    
    Args:
        alert (dict): Alert data
        log_file (str): Path to log file
        
    Returns:
        bool: Success status
    """
    try:
        # If log file is not specified, use environment variable or default
        if not log_file:
            log_file = os.getenv("ALERT_LOG", "logs/fraud_alerts.log")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Append alert to log file
        with open(log_file, 'a') as f:
            f.write(json.dumps(alert) + '\n')
        
        print(f"Alert {alert['alert_id']} logged to {log_file}")
        return True
    except Exception as e:
        print(f"Error logging alert: {str(e)}")
        return False

def send_email_alert(alert, config):
    """
    Send email alert for high-priority fraud
    
    Args:
        alert (dict): Alert data
        config (dict): Email configuration
        
    Returns:
        bool: Success status
    """
    # Only implemented if email configuration is provided
    # This would typically use an email library like smtplib
    # For this example, we'll just print the alert
    
    if alert['priority'] == 'high':
        print(f"HIGH PRIORITY FRAUD ALERT: {alert['alert_id']}")
        print(f"Transaction: {alert['transaction_id']}")
        print(f"Amount: ${alert['amount']}")
        print(f"User: {alert['user_id']}")
        print(f"Fraud Score: {alert['fraud_score']}")
        print(f"Top Factors: {alert['top_factors']}")
    
    return True

def update_alert_status(alert_id, status, notes=None, db_connection=None):
    """
    Update the status of an alert
    
    Args:
        alert_id (str): Alert ID
        status (str): New status (e.g., 'investigating', 'confirmed', 'false_positive')
        notes (str): Optional notes about the status change
        db_connection: Database connection
        
    Returns:
        bool: Success status
    """
    # In a real system, this would update a database
    # For this example, we'll just print the update
    
    print(f"Updating alert {alert_id} status to {status}")
    if notes:
        print(f"Notes: {notes}")
    
    # If we have a database connection, update the alert
    if db_connection:
        try:
            # This is a placeholder for actual database code
            # query = "UPDATE alerts SET status = %s, notes = %s WHERE alert_id = %s"
            # db_connection.execute(query, (status, notes, alert_id))
            return True
        except Exception as e:
            print(f"Error updating alert status: {str(e)}")
            return False
    
    return True

def get_alert_history(user_id, days=90, db_connection=None):
    """
    Get history of alerts for a user
    
    Args:
        user_id (str): User ID
        days (int): Number of days of history
        db_connection: Database connection
        
    Returns:
        list: Alert history
    """
    # In a real system, this would query a database
    # For this example, we'll return an empty list
    
    print(f"Getting alert history for user {user_id} for the past {days} days")
    
    # If we have a database connection, query the alerts
    if db_connection:
        try:
            # This is a placeholder for actual database code
            # query = """
            #     SELECT * FROM alerts 
            #     WHERE user_id = %s 
            #     AND timestamp >= NOW() - INTERVAL %s DAY
            # """
            # result = db_connection.execute(query, (user_id, days))
            # return result.fetchall()
            pass
        except Exception as e:
            print(f"Error getting alert history: {str(e)}")
    
    return []