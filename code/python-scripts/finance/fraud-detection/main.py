#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fraud Detection Engine - Main Application

This script processes financial transactions to detect potential fraud
using machine learning models and business rules.

Author: NinjaTech AI
Date: August 2025
"""

import os
import json
import argparse
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# Import utility modules
from utils.data_processing import (
    load_transaction_data, load_user_history, extract_features
)
from utils.model_utils import (
    load_model, predict_fraud, combine_model_results
)
from utils.alert_handler import (
    create_alert, send_alert_webhook, log_alert
)

# Load environment variables
load_dotenv()

def load_config(config_path=None):
    """
    Load configuration from file
    
    Args:
        config_path (str): Path to configuration file
        
    Returns:
        dict: Configuration settings
    """
    if config_path is None:
        config_path = os.getenv("CONFIG_PATH", "config/fraud_detection_config.json")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    return config

def load_models(config):
    """
    Load all models specified in configuration
    
    Args:
        config (dict): Configuration with model paths
        
    Returns:
        dict: Loaded models
    """
    models = {}
    
    for model_name, model_path in config.get('models', {}).items():
        try:
            models[model_name] = load_model(model_path)
            print(f"Loaded model: {model_name}")
        except Exception as e:
            print(f"Error loading model {model_name}: {str(e)}")
    
    return models

def process_transaction(transaction, config, models):
    """
    Process a single transaction for fraud detection
    
    Args:
        transaction (dict): Transaction data
        config (dict): Configuration settings
        models (dict): Loaded models
        
    Returns:
        dict: Fraud detection results
    """
    print(f"Processing transaction: {transaction.get('transaction_id', 'unknown')}")
    
    # Convert transaction to DataFrame
    transaction_df = load_transaction_data(transaction)
    
    # Load user history
    user_id = transaction.get('user_id')
    user_history = None
    if user_id:
        user_history = load_user_history(
            user_id, 
            days=config.get('history_days', 30),
            db_connection=None  # Add DB connection in production
        )
    
    # Extract features
    features = extract_features(transaction_df, user_history)
    
    # Make predictions with each model
    model_results = predict_fraud(features, models)
    
    # Combine results for final decision
    final_result = combine_model_results(model_results)
    
    # Add transaction info to result
    final_result['transaction_id'] = transaction.get('transaction_id')
    final_result['user_id'] = transaction.get('user_id')
    final_result['timestamp'] = transaction.get('timestamp')
    
    return final_result

def handle_fraud_detection(result, transaction, config):
    """
    Handle fraud detection result
    
    Args:
        result (dict): Fraud detection result
        transaction (dict): Original transaction data
        config (dict): Configuration settings
        
    Returns:
        dict: Alert data if fraud detected, None otherwise
    """
    # Check if fraud was detected
    if result.get('is_fraud', False):
        print(f"Fraud detected for transaction {transaction.get('transaction_id', 'unknown')}")
        
        # Create alert
        alert = create_alert(transaction, result, config)
        
        # Send alert to webhook if configured
        webhook_url = config.get('webhook_url')
        if webhook_url:
            send_alert_webhook(alert, webhook_url)
        
        # Log alert
        log_file = config.get('alert_log')
        if log_file:
            log_alert(alert, log_file)
        
        return alert
    
    print(f"No fraud detected for transaction {transaction.get('transaction_id', 'unknown')}")
    return None

def process_batch(transactions_file, config_path=None, output_file=None):
    """
    Process a batch of transactions from a file
    
    Args:
        transactions_file (str): Path to transactions JSON file
        config_path (str): Path to configuration file
        output_file (str): Path to output results file
        
    Returns:
        list: Processing results
    """
    # Load configuration
    config = load_config(config_path)
    
    # Load models
    models = load_models(config)
    
    # Load transactions
    with open(transactions_file, 'r') as f:
        transactions = json.load(f)
    
    results = []
    alerts = []
    
    # Process each transaction
    for transaction in transactions:
        # Detect fraud
        result = process_transaction(transaction, config, models)
        results.append(result)
        
        # Handle result
        alert = handle_fraud_detection(result, transaction, config)
        if alert:
            alerts.append(alert)
    
    # Save results if output file specified
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    print(f"Processed {len(transactions)} transactions, detected {len(alerts)} potential fraud cases")
    return results

def start_api_server(host='0.0.0.0', port=5000, config_path=None):
    """
    Start API server for real-time fraud detection
    
    Args:
        host (str): Host to bind
        port (int): Port to bind
        config_path (str): Path to configuration file
    """
    from flask import Flask, request, jsonify
    
    # Load configuration
    config = load_config(config_path)
    
    # Load models
    models = load_models(config)
    
    # Create Flask app
    app = Flask(__name__)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})
    
    @app.route('/detect', methods=['POST'])
    def detect_fraud():
        # Get transaction data from request
        transaction = request.json
        
        if not transaction:
            return jsonify({'error': 'No transaction data provided'}), 400
        
        # Process transaction
        result = process_transaction(transaction, config, models)
        
        # Handle result
        alert = handle_fraud_detection(result, transaction, config)
        
        # Return result
        return jsonify({
            'transaction_id': transaction.get('transaction_id'),
            'fraud_detected': result.get('is_fraud', False),
            'fraud_score': result.get('fraud_score', 0),
            'confidence': result.get('confidence', 0),
            'alert_id': alert.get('alert_id') if alert else None
        })
    
    # Start server
    print(f"Starting fraud detection API server on {host}:{port}")
    app.run(host=host, port=port)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fraud Detection Engine")
    parser.add_argument("--mode", choices=['batch', 'api'], default='batch',
                      help="Operation mode: batch or api")
    parser.add_argument("--input", help="Input transactions file (for batch mode)")
    parser.add_argument("--output", help="Output results file (for batch mode)")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--host", default="0.0.0.0", help="API server host (for api mode)")
    parser.add_argument("--port", type=int, default=5000, help="API server port (for api mode)")
    
    args = parser.parse_args()
    
    if args.mode == 'batch':
        if not args.input:
            parser.error("Batch mode requires --input")
        process_batch(args.input, args.config, args.output)
    else:  # api mode
        start_api_server(args.host, args.port, args.config)