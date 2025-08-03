#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Utilities Module for Fraud Detection Engine

This module provides functions to load and use machine learning models
for fraud detection.

Author: NinjaTech AI
Date: August 2025
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
import xgboost as xgb

# Try to import SHAP for model explainability
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("SHAP not available. Model explanations will be limited.")

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
            if SHAP_AVAILABLE:
                try:
                    explainer = shap.TreeExplainer(model)
                    shap_values = explainer.shap_values(features)
                    
                    # Get top contributing features
                    feature_importance = {}
                    for i, col in enumerate(features.columns):
                        feature_importance[col] = float(shap_values[0][i])
                    
                    results[model_name]['feature_importance'] = feature_importance
                except Exception as e:
                    print(f"Error calculating SHAP values: {str(e)}")
                    # Fallback to built-in feature importance
                    feature_importance = {}
                    for i, col in enumerate(features.columns):
                        if hasattr(model, 'get_score'):
                            scores = model.get_score(importance_type='weight')
                            feature_importance[col] = float(scores.get(col, 0))
                        else:
                            feature_importance[col] = 0
                    
                    results[model_name]['feature_importance'] = feature_importance
            else:
                # Fallback to built-in feature importance
                feature_importance = {}
                for i, col in enumerate(features.columns):
                    if hasattr(model, 'get_score'):
                        scores = model.get_score(importance_type='weight')
                        feature_importance[col] = float(scores.get(col, 0))
                    else:
                        feature_importance[col] = 0
                
                results[model_name]['feature_importance'] = feature_importance
        else:
            # Generic scikit-learn model
            try:
                # Try to get probability scores
                score = float(model.predict_proba(features)[0, 1])
                results[model_name] = {
                    'score': score,
                    'is_fraud': score > 0.5,  # Adjust threshold as needed
                    'threshold': 0.5,
                    'features': list(features.columns)
                }
                
                # Add feature importance if available
                if hasattr(model, 'feature_importances_'):
                    feature_importance = {}
                    for i, col in enumerate(features.columns):
                        feature_importance[col] = float(model.feature_importances_[i])
                    
                    results[model_name]['feature_importance'] = feature_importance
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

def apply_business_rules(transaction, fraud_result, config):
    """
    Apply business rules to adjust fraud decision
    
    Args:
        transaction (dict): Transaction data
        fraud_result (dict): Fraud detection result
        config (dict): Configuration with business rules
        
    Returns:
        dict: Updated fraud result
    """
    # Create a copy to avoid modifying the original
    result = fraud_result.copy()
    
    # Get thresholds from config
    thresholds = config.get('thresholds', {})
    default_threshold = thresholds.get('default', 0.7)
    high_value_threshold = thresholds.get('high_value', 0.5)
    new_user_threshold = thresholds.get('new_user', 0.6)
    
    # Get transaction details
    amount = transaction.get('amount', 0)
    user_id = transaction.get('user_id', '')
    
    # Apply high value rule
    high_value_amount = config.get('high_value_threshold', 1000)
    if amount > high_value_amount:
        # Lower threshold for high-value transactions
        result['threshold'] = high_value_threshold
        result['is_fraud'] = result['fraud_score'] > high_value_threshold
        result['rules_applied'] = ['high_value']
    
    # Apply new user rule if applicable
    # In a real system, you would check user account age
    # For this example, we'll assume a placeholder check
    is_new_user = False  # Replace with actual check
    if is_new_user:
        # Lower threshold for new users
        result['threshold'] = new_user_threshold
        result['is_fraud'] = result['fraud_score'] > new_user_threshold
        if 'rules_applied' in result:
            result['rules_applied'].append('new_user')
        else:
            result['rules_applied'] = ['new_user']
    
    # Update confidence based on new threshold
    result['confidence'] = 1.0 - abs(result['fraud_score'] - result['threshold']) * 2
    
    return result