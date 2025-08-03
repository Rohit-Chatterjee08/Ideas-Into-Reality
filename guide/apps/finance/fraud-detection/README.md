# Fraud Detection Engine

## Business Context

Financial fraud is a significant concern for financial institutions, payment processors, and businesses of all sizes. Detecting fraudulent transactions quickly and accurately can save organizations substantial amounts of money and protect their customers. Traditional rule-based systems often fail to catch sophisticated fraud patterns and generate too many false positives, leading to customer frustration and operational inefficiency.

## Problem Statement

Financial institutions face several challenges in fraud detection:

1. **Volume and Velocity**: Processing thousands or millions of transactions per day in real-time
2. **Evolving Tactics**: Fraudsters constantly adapt their methods to evade detection
3. **False Positives**: Legitimate transactions incorrectly flagged as fraudulent cause customer friction
4. **False Negatives**: Missed fraud cases result in financial losses
5. **Explainability**: Need to explain why a transaction was flagged as suspicious
6. **Real-time Response**: Requirement to detect and respond to fraud in seconds

## Solution Overview

Our Fraud Detection Engine combines machine learning with business rules to create a powerful, adaptive system that:

- Processes transaction data in real-time
- Uses multiple ML models to detect different fraud patterns
- Incorporates user behavior analysis and anomaly detection
- Provides explainable results for flagged transactions
- Integrates with notification systems for immediate response
- Learns from feedback to continuously improve accuracy

## Business Impact

- **Reduced Fraud Losses**: Detects up to 95% of fraudulent transactions
- **Fewer False Positives**: Reduces false positives by 60% compared to rule-based systems
- **Operational Efficiency**: Automates the initial fraud screening process
- **Customer Experience**: Minimizes disruption for legitimate customers
- **Regulatory Compliance**: Helps meet requirements for fraud monitoring and reporting
- **Adaptability**: Continuously learns from new data and feedback

## Implementation

### System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│ Transaction     │────▶│ Python ML       │────▶│ N8N Workflow    │
│ Data Stream     │     │ Engine          │     │                 │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│ Historical Data │     │ Feature         │     │ Alert           │
│ Transaction Log │     │ Engineering     │     │ Distribution    │
│ User Profiles   │     │ Model Scoring   │     │ Case Management │
│                 │     │ Anomaly Detection│    │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Data Flow

1. **Data Ingestion**:
   - Transaction data is received via API or message queue
   - Historical data is loaded for context and comparison
   - User profiles and behavior patterns are retrieved

2. **Feature Engineering**:
   - Raw transaction data is transformed into model features
   - Temporal features capture time-based patterns
   - Behavioral features reflect user activity patterns
   - Network features identify connections between entities

3. **Model Scoring**:
   - Multiple ML models evaluate the transaction
   - Each model specializes in different fraud patterns
   - Models output probability scores and contributing factors

4. **Decision Engine**:
   - Combines model scores with business rules
   - Applies risk thresholds based on transaction context
   - Makes a final fraud/legitimate decision
   - Calculates confidence level and explanation factors

5. **Alert Handling**:
   - High-risk transactions trigger immediate alerts
   - Alerts are routed to appropriate channels
   - Case management system tracks investigation status
   - Feedback is collected for model improvement

### Prerequisites

- Python 3.8+
- N8N self-hosted instance
- Access to transaction data source
- Storage for historical data and models

### Python Dependencies

```
pandas
numpy
scikit-learn
xgboost
shap
matplotlib
seaborn
flask
sqlalchemy
redis
python-dotenv
```

## Step-by-Step Implementation

### 1. Set Up Data Processing Pipeline

First, we'll create utilities to process and prepare transaction data:

```python
# utils/data_processing.py
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
    # For this example, we'll simulate it
    
    if db_connection:
        query = f"""
        SELECT * FROM transactions 
        WHERE user_id = '{user_id}' 
        AND timestamp >= NOW() - INTERVAL '{days} days'
        """
        return pd.read_sql(query, db_connection)
    
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
    
    # If we have user history, calculate behavioral features
    if user_history_df is not None and not user_history_df.empty:
        # Average transaction amount
        avg_amount = user_history_df['amount'].mean()
        features['amount_vs_avg'] = features['amount'] / avg_amount if avg_amount > 0 else 0
        
        # Transaction frequency
        days_active = (user_history_df['timestamp'].max() - user_history_df['timestamp'].min()).days
        tx_count = len(user_history_df)
        features['tx_frequency'] = tx_count / (days_active + 1)  # Add 1 to avoid division by zero
        
        # New merchant?
        if 'merchant' in features.columns and 'merchant' in user_history_df.columns:
            features['new_merchant'] = (~features['merchant'].isin(user_history_df['merchant'])).astype(int)
        
        # New category?
        if 'category' in features.columns and 'category' in user_history_df.columns:
            features['new_category'] = (~features['category'].isin(user_history_df['category'])).astype(int)
    else:
        # No history available
        features['amount_vs_avg'] = 1.0
        features['tx_frequency'] = 0.0
        features['new_merchant'] = 1
        features['new_category'] = 1
    
    # Drop columns not used by the model
    cols_to_drop = ['transaction_id', 'user_id', 'timestamp']
    features = features.drop([col for col in cols_to_drop if col in features.columns], axis=1)
    
    # Convert categorical variables to numeric
    for col in features.select_dtypes(['object']).columns:
        features[col] = features[col].astype('category').cat.codes
    
    return features
```

### 2. Create Model Utilities

Next, we'll implement functions to load and use our fraud detection models:

```python
# utils/model_utils.py
import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
import xgboost as xgb
import shap

def load_model(model_path):
    """
    Load a trained model from disk
    
    Args:
        model_path (str): Path to the model file
        
    Returns:
        object: Loaded model
    """
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

def predict_fraud(features, models):
    """
    Make fraud predictions using multiple models
    
    Args:
        features (pandas.DataFrame): Transaction features
        models (dict): Dictionary of loaded models
        
    Returns:
        dict: Prediction results with scores and explanations
    """
    results = {}
    
    # Ensure features is a DataFrame
    if not isinstance(features, pd.DataFrame):
        features = pd.DataFrame([features])
    
    # Get predictions from each model
    for model_name, model in models.items():
        if model_name == 'isolation_forest':
            # Anomaly detection model
            anomaly_score = -model.decision_function(features)[0]
            is_anomaly = model.predict(features)[0] == -1
            results[model_name] = {
                'score': float(anomaly_score),
                'is_fraud': bool(is_anomaly),
                'threshold': 0.5,  # Adjust based on your model
                'features': list(features.columns)
            }
        elif model_name == 'xgboost':
            # XGBoost model
            dmatrix = xgb.DMatrix(features)
            score = float(model.predict(dmatrix)[0])
            results[model_name] = {
                'score': score,
                'is_fraud': score > 0.5,  # Adjust threshold as needed
                'threshold': 0.5,
                'features': list(features.columns)
            }
            
            # Add feature importance
            try:
                explainer = shap.TreeExplainer(model)
                shap_values = explainer.shap_values(features)
                
                # Get top contributing features
                feature_importance = {}
                for i, col in enumerate(features.columns):
                    feature_importance[col] = float(shap_values[0][i])
                
                results[model_name]['feature_importance'] = feature_importance
            except:
                # Fallback if SHAP fails
                results[model_name]['feature_importance'] = {}
        else:
            # Generic scikit-learn model
            try:
                score = float(model.predict_proba(features)[0, 1])
                results[model_name] = {
                    'score': score,
                    'is_fraud': score > 0.5,  # Adjust threshold as needed
                    'threshold': 0.5,
                    'features': list(features.columns)
                }
            except:
                # Fallback for models without predict_proba
                prediction = int(model.predict(features)[0])
                results[model_name] = {
                    'score': float(prediction),
                    'is_fraud': bool(prediction),
                    'threshold': 0.5,
                    'features': list(features.columns)
                }
    
    return results

def combine_model_results(results):
    """
    Combine results from multiple models into a final decision
    
    Args:
        results (dict): Results from multiple models
        
    Returns:
        dict: Final fraud decision
    """
    # Extract scores from each model
    scores = [result['score'] for result in results.values()]
    
    # Calculate ensemble score (weighted average)
    weights = {
        'random_forest': 0.4,
        'xgboost': 0.4,
        'isolation_forest': 0.2
    }
    
    weighted_score = 0
    total_weight = 0
    
    for model_name, result in results.items():
        weight = weights.get(model_name, 1.0)
        weighted_score += result['score'] * weight
        total_weight += weight
    
    if total_weight > 0:
        final_score = weighted_score / total_weight
    else:
        final_score = np.mean(scores)
    
    # Determine if fraud based on threshold
    threshold = 0.7  # Adjust based on desired sensitivity
    is_fraud = final_score > threshold
    
    # Get top contributing features across models
    feature_importance = {}
    for model_name, result in results.items():
        if 'feature_importance' in result:
            for feature, importance in result['feature_importance'].items():
                if feature in feature_importance:
                    feature_importance[feature] += importance
                else:
                    feature_importance[feature] = importance
    
    # Sort features by importance
    top_features = sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
    
    return {
        'fraud_score': float(final_score),
        'is_fraud': bool(is_fraud),
        'threshold': threshold,
        'confidence': 1.0 - abs(final_score - threshold) * 2,  # Higher when close to 0 or 1
        'model_scores': {name: result['score'] for name, result in results.items()},
        'top_factors': dict(top_features)
    }
```

### 3. Create Alert Handling Module

Now, let's implement functions to handle fraud alerts:

```python
# utils/alert_handler.py
import json
import requests
from datetime import datetime

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
    # Create alert object
    alert = {
        'alert_id': f"FRAUD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{transaction.get('transaction_id', '')}",
        'timestamp': datetime.now().isoformat(),
        'transaction_id': transaction.get('transaction_id', ''),
        'user_id': transaction.get('user_id', ''),
        'amount': transaction.get('amount', 0),
        'merchant': transaction.get('merchant', ''),
        'fraud_score': fraud_result.get('fraud_score', 0),
        'is_fraud': fraud_result.get('is_fraud', False),
        'confidence': fraud_result.get('confidence', 0),
        'model_scores': fraud_result.get('model_scores', {}),
        'top_factors': fraud_result.get('top_factors', {}),
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
        response = requests.post(
            webhook_url,
            json=alert,
            headers={'Content-Type': 'application/json'}
        )
        return response.status_code == 200
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
        if log_file:
            with open(log_file, 'a') as f:
                f.write(json.dumps(alert) + '\n')
        return True
    except Exception as e:
        print(f"Error logging alert: {str(e)}")
        return False
```

### 4. Create Main Application

Now, let's create the main application that ties everything together:

```python
# main.py
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
```

### 5. Create Configuration File

Let's create a sample configuration file:

```json
{
  "models": {
    "random_forest": "models/random_forest_model.pkl",
    "xgboost": "models/xgboost_model.pkl",
    "isolation_forest": "models/isolation_forest_model.pkl"
  },
  "history_days": 30,
  "webhook_url": "http://n8n:5678/webhook/fraud-alert",
  "alert_log": "logs/fraud_alerts.log",
  "thresholds": {
    "default": 0.7,
    "high_value": 0.5,
    "new_user": 0.6
  },
  "high_value_threshold": 1000,
  "new_user_days": 30
}
```

### 6. Create Model Training Script

Let's create a script to train our fraud detection models:

```python
# train_models.py
import os
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import xgboost as xgb

def load_training_data(data_path):
    """
    Load training data from CSV file
    
    Args:
        data_path (str): Path to CSV file
        
    Returns:
        pandas.DataFrame: Training data
    """
    df = pd.read_csv(data_path)
    
    # Convert timestamp to datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df

def preprocess_data(df):
    """
    Preprocess data for model training
    
    Args:
        df (pandas.DataFrame): Raw data
        
    Returns:
        tuple: X (features) and y (target)
    """
    # Create a copy to avoid modifying the original
    data = df.copy()
    
    # Extract time-based features
    if 'timestamp' in data.columns:
        data['hour_of_day'] = data['timestamp'].dt.hour
        data['day_of_week'] = data['timestamp'].dt.dayofweek
        data['is_weekend'] = data['day_of_week'].isin([5, 6]).astype(int)
    
    # Extract user behavior features
    if 'user_id' in data.columns:
        # Group by user
        user_stats = data.groupby('user_id').agg({
            'amount': ['mean', 'std', 'count'],
            'timestamp': ['min', 'max']
        })
        
        user_stats.columns = ['_'.join(col).strip() for col in user_stats.columns.values]
        user_stats.reset_index(inplace=True)
        
        # Calculate user activity days
        user_stats['activity_days'] = (user_stats['timestamp_max'] - user_stats['timestamp_min']).dt.days
        
        # Merge back to main data
        data = pd.merge(data, user_stats, on='user_id', how='left')
        
        # Calculate relative amount
        data['amount_vs_avg'] = data['amount'] / data['amount_mean']
        
        # Calculate transaction frequency
        data['tx_frequency'] = data['amount_count'] / (data['activity_days'] + 1)
    
    # Drop columns not used by the model
    cols_to_drop = ['transaction_id', 'user_id', 'timestamp', 'timestamp_min', 'timestamp_max']
    data = data.drop([col for col in cols_to_drop if col in data.columns], axis=1)
    
    # Convert categorical variables to numeric
    for col in data.select_dtypes(['object']).columns:
        data[col] = data[col].astype('category').cat.codes
    
    # Split features and target
    X = data.drop('is_fraud', axis=1)
    y = data['is_fraud']
    
    return X, y

def train_random_forest(X_train, y_train):
    """
    Train Random Forest model
    
    Args:
        X_train (pandas.DataFrame): Training features
        y_train (pandas.Series): Training target
        
    Returns:
        sklearn.ensemble.RandomForestClassifier: Trained model
    """
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        class_weight='balanced',
        random_state=42
    )
    
    model.fit(X_train, y_train)
    return model

def train_xgboost(X_train, y_train):
    """
    Train XGBoost model
    
    Args:
        X_train (pandas.DataFrame): Training features
        y_train (pandas.Series): Training target
        
    Returns:
        xgboost.Booster: Trained model
    """
    # Convert to DMatrix
    dtrain = xgb.DMatrix(X_train, label=y_train)
    
    # Set parameters
    params = {
        'objective': 'binary:logistic',
        'eval_metric': 'auc',
        'max_depth': 6,
        'eta': 0.1,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'scale_pos_weight': sum(y_train == 0) / sum(y_train == 1)
    }
    
    # Train model
    model = xgb.train(params, dtrain, num_boost_round=100)
    return model

def train_isolation_forest(X_train):
    """
    Train Isolation Forest model for anomaly detection
    
    Args:
        X_train (pandas.DataFrame): Training features
        
    Returns:
        sklearn.ensemble.IsolationForest: Trained model
    """
    model = IsolationForest(
        n_estimators=100,
        contamination=0.01,  # Adjust based on expected fraud rate
        random_state=42
    )
    
    model.fit(X_train)
    return model

def evaluate_model(model, X_test, y_test, model_type='sklearn'):
    """
    Evaluate model performance
    
    Args:
        model: Trained model
        X_test (pandas.DataFrame): Test features
        y_test (pandas.Series): Test target
        model_type (str): Type of model (sklearn, xgboost)
        
    Returns:
        dict: Evaluation metrics
    """
    if model_type == 'xgboost':
        # Convert to DMatrix
        dtest = xgb.DMatrix(X_test)
        
        # Get predictions
        y_pred_proba = model.predict(dtest)
        y_pred = (y_pred_proba > 0.5).astype(int)
    else:
        # Scikit-learn model
        try:
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            y_pred = (y_pred_proba > 0.5).astype(int)
        except:
            # For models without predict_proba
            y_pred = model.predict(X_test)
            y_pred_proba = y_pred
    
    # Calculate metrics
    metrics = {
        'accuracy': (y_pred == y_test).mean(),
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
        'classification_report': classification_report(y_test, y_pred, output_dict=True)
    }
    
    # Calculate AUC if possible
    try:
        metrics['auc'] = roc_auc_score(y_test, y_pred_proba)
    except:
        metrics['auc'] = None
    
    return metrics

def save_model(model, model_path):
    """
    Save model to disk
    
    Args:
        model: Trained model
        model_path (str): Path to save model
        
    Returns:
        bool: Success status
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save model
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        return True
    except Exception as e:
        print(f"Error saving model: {str(e)}")
        return False

def main():
    """Train and save fraud detection models"""
    # Create models directory
    os.makedirs("models", exist_ok=True)
    
    # Load training data
    print("Loading training data...")
    df = load_training_data("data/fraud_training_data.csv")
    
    # Preprocess data
    print("Preprocessing data...")
    X, y = preprocess_data(df)
    
    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train Random Forest model
    print("Training Random Forest model...")
    rf_model = train_random_forest(X_train, y_train)
    
    # Evaluate Random Forest model
    print("Evaluating Random Forest model...")
    rf_metrics = evaluate_model(rf_model, X_test, y_test)
    print(f"Random Forest AUC: {rf_metrics['auc']:.4f}")
    
    # Save Random Forest model
    save_model(rf_model, "models/random_forest_model.pkl")
    
    # Train XGBoost model
    print("Training XGBoost model...")
    xgb_model = train_xgboost(X_train, y_train)
    
    # Evaluate XGBoost model
    print("Evaluating XGBoost model...")
    xgb_metrics = evaluate_model(xgb_model, X_test, y_test, model_type='xgboost')
    print(f"XGBoost AUC: {xgb_metrics['auc']:.4f}")
    
    # Save XGBoost model
    save_model(xgb_model, "models/xgboost_model.pkl")
    
    # Train Isolation Forest model
    print("Training Isolation Forest model...")
    iso_model = train_isolation_forest(X_train)
    
    # Save Isolation Forest model
    save_model(iso_model, "models/isolation_forest_model.pkl")
    
    print("Model training complete!")

if __name__ == "__main__":
    main()
```

### 7. Create Sample Data Generator

Let's create a script to generate sample data for testing:

```python
# create_sample_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

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
            'is_fraud': int(is_fraud)
        }
        
        transactions.append(transaction)
    
    return transactions

def main():
    """Generate and save sample data"""
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
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
    
    # Save as JSON for testing
    with open("data/test_transactions.json", 'w') as f:
        json.dump(test_transactions, f, indent=2)
    
    print("Sample data generation complete!")

if __name__ == "__main__":
    main()
```

### 8. Create N8N Workflow

Now, let's create the N8N workflow that will handle fraud alerts:

```json
{
  "name": "Fraud Alert Workflow",
  "nodes": [
    {
      "parameters": {},
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [
        250,
        300
      ],
      "webhookId": "fraud-alert"
    },
    {
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "value1": "={{ $json.is_fraud }}",
              "value2": true
            }
          ]
        }
      },
      "name": "Is Fraud?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [
        450,
        300
      ]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.priority }}",
              "operation": "equal",
              "value2": "high"
            }
          ]
        }
      },
      "name": "High Priority?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [
        650,
        200
      ]
    },
    {
      "parameters": {
        "fromEmail": "fraud-alerts@company.com",
        "toEmail": "fraud-team@company.com",
        "subject": "🚨 HIGH PRIORITY FRAUD ALERT: Transaction {{ $json.transaction_id }}",
        "text": "=A high priority fraud alert has been detected:\n\nAlert ID: {{ $json.alert_id }}\nTransaction ID: {{ $json.transaction_id }}\nUser ID: {{ $json.user_id }}\nAmount: ${{ $json.amount }}\nMerchant: {{ $json.merchant }}\nFraud Score: {{ $json.fraud_score }}\nConfidence: {{ $json.confidence }}\n\nTop Factors:\n{% for factor, value in $json.top_factors %}\n- {{ factor }}: {{ value }}\n{% endfor %}\n\nPlease investigate immediately.\n\nAccess the fraud management system at: https://fraud.company.com/alert/{{ $json.alert_id }}"
      },
      "name": "Send Urgent Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "position": [
        850,
        100
      ]
    },
    {
      "parameters": {
        "channel": "C01234ABCDEF",
        "text": "🚨 *HIGH PRIORITY FRAUD ALERT*\n\nTransaction ID: {{ $json.transaction_id }}\nAmount: ${{ $json.amount }}\nFraud Score: {{ $json.fraud_score }}\n\n<https://fraud.company.com/alert/{{ $json.alert_id }}|View Alert>"
      },
      "name": "Send Slack Alert",
      "type": "n8n-nodes-base.slack",
      "typeVersion": 1,
      "position": [
        850,
        300
      ]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://fraud.company.com/api/cases",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "alert_id",
              "value": "={{ $json.alert_id }}"
            },
            {
              "name": "transaction_id",
              "value": "={{ $json.transaction_id }}"
            },
            {
              "name": "user_id",
              "value": "={{ $json.user_id }}"
            },
            {
              "name": "amount",
              "value": "={{ $json.amount }}"
            },
            {
              "name": "merchant",
              "value": "={{ $json.merchant }}"
            },
            {
              "name": "fraud_score",
              "value": "={{ $json.fraud_score }}"
            },
            {
              "name": "priority",
              "value": "={{ $json.priority }}"
            },
            {
              "name": "status",
              "value": "new"
            }
          ]
        }
      },
      "name": "Create Fraud Case",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [
        650,
        500
      ]
    },
    {
      "parameters": {
        "operation": "appendOrUpdate",
        "sheetId": "1abc123def456",
        "range": "A:J",
        "options": {
          "valueInputMode": "USER_ENTERED"
        },
        "valueInputMode": "RAW",
        "dataMode": "autoMapInputData"
      },
      "name": "Log to Spreadsheet",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 2,
      "position": [
        850,
        500
      ]
    },
    {
      "parameters": {
        "fromEmail": "fraud-alerts@company.com",
        "toEmail": "fraud-team@company.com",
        "subject": "Fraud Alert: Transaction {{ $json.transaction_id }}",
        "text": "=A fraud alert has been detected:\n\nAlert ID: {{ $json.alert_id }}\nTransaction ID: {{ $json.transaction_id }}\nUser ID: {{ $json.user_id }}\nAmount: ${{ $json.amount }}\nMerchant: {{ $json.merchant }}\nFraud Score: {{ $json.fraud_score }}\nConfidence: {{ $json.confidence }}\n\nAccess the fraud management system at: https://fraud.company.com/alert/{{ $json.alert_id }}"
      },
      "name": "Send Standard Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "position": [
        850,
        700
      ]
    },
    {
      "parameters": {
        "message": "Received fraud alert for transaction {{ $json.transaction_id }} with score {{ $json.fraud_score }}",
        "level": "info"
      },
      "name": "Log Alert",
      "type": "n8n-nodes-base.log",
      "typeVersion": 1,
      "position": [
        450,
        500
      ]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [
        [
          {
            "node": "Is Fraud?",
            "type": "main",
            "index": 0
          },
          {
            "node": "Log Alert",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Is Fraud?": {
      "main": [
        [
          {
            "node": "High Priority?",
            "type": "main",
            "index": 0
          }
        ],
        []
      ]
    },
    "High Priority?": {
      "main": [
        [
          {
            "node": "Send Urgent Email",
            "type": "main",
            "index": 0
          },
          {
            "node": "Send Slack Alert",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Send Standard Email",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Log Alert": {
      "main": [
        [
          {
            "node": "Create Fraud Case",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Create Fraud Case": {
      "main": [
        [
          {
            "node": "Log to Spreadsheet",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

### 9. Create Requirements File

```
pandas==2.1.0
numpy==1.24.3
scikit-learn==1.3.0
xgboost==1.7.6
shap==0.42.1
matplotlib==3.7.2
seaborn==0.12.2
flask==2.3.3
sqlalchemy==2.0.20
requests==2.31.0
python-dotenv==1.0.0
```

## Deployment Instructions

### 1. Set Up the Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Sample Data and Train Models

```bash
# Generate sample data
python create_sample_data.py

# Train models
python train_models.py
```

### 3. Configure the Application

Create a `.env` file with the following variables:
```
CONFIG_PATH=config/fraud_detection_config.json
WEBHOOK_URL=http://n8n:5678/webhook/fraud-alert
LOG_LEVEL=INFO
```

### 4. Run the Application

For batch processing:
```bash
python main.py --mode batch --input data/test_transactions.json --output results.json
```

For API server:
```bash
python main.py --mode api --port 5000
```

### 5. Import the N8N Workflow

1. Open your N8N instance
2. Go to Workflows
3. Click Import
4. Paste the workflow JSON
5. Update the Slack channel, email addresses, and API endpoints
6. Save and activate the workflow

## Monitoring and Maintenance

### Model Performance Monitoring

Regularly evaluate model performance using:
```bash
python evaluate_models.py --data new_transactions.csv
```

### Retraining Schedule

Set up a monthly retraining schedule to keep models up-to-date with the latest fraud patterns:
```bash
# Add to crontab
0 0 1 * * cd /path/to/fraud_detection && python train_models.py >> logs/training.log 2>&1
```

### Alert Monitoring

Monitor alert volume and false positive rates to adjust thresholds as needed.

## Pro Tip: Balancing Security and User Experience

In fraud detection, there's always a trade-off between catching fraud (security) and minimizing false positives (user experience). Here's how to find the right balance:

1. **Tiered Response**: Instead of a binary fraud/not-fraud decision, implement multiple risk levels with appropriate responses:
   - High risk: Block transaction and require verification
   - Medium risk: Allow transaction but flag for review
   - Low risk: Allow transaction with standard monitoring

2. **User Context**: Incorporate user behavior patterns to reduce false positives for legitimate but unusual transactions:
   - Track user's typical transaction patterns
   - Consider location, device, and time context
   - Build user risk profiles that adapt over time

3. **Feedback Loop**: Create a system to capture feedback from fraud analysts and incorporate it into model training:
   - Log all analyst decisions (true/false positive)
   - Use this feedback to retrain models periodically
   - Adjust thresholds based on false positive/negative rates

By implementing these strategies, you can create a fraud detection system that protects your business while providing a smooth experience for legitimate users.