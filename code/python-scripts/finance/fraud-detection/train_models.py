#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Training Script for Fraud Detection Engine

This script trains machine learning models for fraud detection
using historical transaction data.

Author: NinjaTech AI
Date: August 2025
"""

import os
import pickle
import json
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, precision_recall_curve, average_precision_score
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns

from utils.data_processing import preprocess_batch

def load_training_data(data_path):
    """
    Load training data from CSV file
    
    Args:
        data_path (str): Path to CSV file
        
    Returns:
        pandas.DataFrame: Training data
    """
    print(f"Loading training data from {data_path}")
    df = pd.read_csv(data_path)
    
    # Convert timestamp to datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    print(f"Loaded {len(df)} records")
    
    # Print class distribution
    if 'is_fraud' in df.columns:
        fraud_count = df['is_fraud'].sum()
        print(f"Fraud transactions: {fraud_count} ({fraud_count/len(df)*100:.2f}%)")
        print(f"Legitimate transactions: {len(df) - fraud_count} ({(len(df) - fraud_count)/len(df)*100:.2f}%)")
    
    return df

def train_random_forest(X_train, y_train):
    """
    Train Random Forest model
    
    Args:
        X_train (pandas.DataFrame): Training features
        y_train (pandas.Series): Training target
        
    Returns:
        sklearn.ensemble.RandomForestClassifier: Trained model
    """
    print("Training Random Forest model...")
    
    # Create and train model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1  # Use all available cores
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
    print("Training XGBoost model...")
    
    # Calculate class weight
    pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    
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
        'scale_pos_weight': pos_weight
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
    print("Training Isolation Forest model...")
    
    # Create and train model
    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,  # Adjust based on expected fraud rate
        random_state=42,
        n_jobs=-1  # Use all available cores
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
        model_type (str): Type of model (sklearn, xgboost, isolation_forest)
        
    Returns:
        dict: Evaluation metrics
    """
    print(f"Evaluating {model_type} model...")
    
    if model_type == 'xgboost':
        # Convert to DMatrix
        dtest = xgb.DMatrix(X_test)
        
        # Get predictions
        y_pred_proba = model.predict(dtest)
        y_pred = (y_pred_proba > 0.5).astype(int)
    elif model_type == 'isolation_forest':
        # For Isolation Forest, -1 is anomaly (fraud), 1 is normal
        y_pred = model.predict(X_test)
        y_pred = (y_pred == -1).astype(int)  # Convert to 1 for fraud, 0 for normal
        
        # Get anomaly scores
        y_pred_proba = -model.decision_function(X_test)
        
        # Normalize scores to [0, 1]
        y_pred_proba = (y_pred_proba - y_pred_proba.min()) / (y_pred_proba.max() - y_pred_proba.min())
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
        'accuracy': float((y_pred == y_test).mean()),
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
        'classification_report': classification_report(y_test, y_pred, output_dict=True)
    }
    
    # Calculate AUC if possible
    try:
        metrics['auc'] = float(roc_auc_score(y_test, y_pred_proba))
    except:
        metrics['auc'] = None
    
    # Calculate average precision (AP)
    try:
        metrics['average_precision'] = float(average_precision_score(y_test, y_pred_proba))
    except:
        metrics['average_precision'] = None
    
    # Print key metrics
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    if metrics['auc'] is not None:
        print(f"AUC: {metrics['auc']:.4f}")
    if metrics['average_precision'] is not None:
        print(f"Average Precision: {metrics['average_precision']:.4f}")
    
    # Print classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    return metrics

def plot_roc_curve(y_test, y_pred_proba, model_name, output_dir="models"):
    """
    Plot ROC curve
    
    Args:
        y_test (pandas.Series): Test target
        y_pred_proba (numpy.ndarray): Predicted probabilities
        model_name (str): Model name
        output_dir (str): Output directory
    """
    from sklearn.metrics import roc_curve
    
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Calculate ROC curve
    fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
    auc = roc_auc_score(y_test, y_pred_proba)
    
    # Plot ROC curve
    plt.figure(figsize=(10, 8))
    plt.plot(fpr, tpr, label=f'{model_name} (AUC = {auc:.4f})')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'ROC Curve - {model_name}')
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    
    # Save plot
    plt.savefig(f"{output_dir}/{model_name}_roc_curve.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_precision_recall_curve(y_test, y_pred_proba, model_name, output_dir="models"):
    """
    Plot Precision-Recall curve
    
    Args:
        y_test (pandas.Series): Test target
        y_pred_proba (numpy.ndarray): Predicted probabilities
        model_name (str): Model name
        output_dir (str): Output directory
    """
    from sklearn.metrics import precision_recall_curve
    
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Calculate Precision-Recall curve
    precision, recall, thresholds = precision_recall_curve(y_test, y_pred_proba)
    ap = average_precision_score(y_test, y_pred_proba)
    
    # Plot Precision-Recall curve
    plt.figure(figsize=(10, 8))
    plt.plot(recall, precision, label=f'{model_name} (AP = {ap:.4f})')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title(f'Precision-Recall Curve - {model_name}')
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    
    # Save plot
    plt.savefig(f"{output_dir}/{model_name}_pr_curve.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_feature_importance(model, feature_names, model_name, output_dir="models"):
    """
    Plot feature importance
    
    Args:
        model: Trained model
        feature_names (list): Feature names
        model_name (str): Model name
        output_dir (str): Output directory
    """
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get feature importance
    if model_name == 'xgboost':
        importance = model.get_score(importance_type='weight')
        importance = {k: v for k, v in importance.items()}
    elif hasattr(model, 'feature_importances_'):
        importance = {feature: imp for feature, imp in zip(feature_names, model.feature_importances_)}
    else:
        return
    
    # Convert to DataFrame
    importance_df = pd.DataFrame({
        'Feature': list(importance.keys()),
        'Importance': list(importance.values())
    })
    
    # Sort by importance
    importance_df = importance_df.sort_values('Importance', ascending=False)
    
    # Plot feature importance
    plt.figure(figsize=(12, 10))
    sns.barplot(x='Importance', y='Feature', data=importance_df.head(20))
    plt.title(f'Feature Importance - {model_name}')
    plt.tight_layout()
    
    # Save plot
    plt.savefig(f"{output_dir}/{model_name}_feature_importance.png", dpi=300, bbox_inches='tight')
    plt.close()

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
        
        print(f"Model saved to {model_path}")
        return True
    except Exception as e:
        print(f"Error saving model: {str(e)}")
        return False

def save_metrics(metrics, metrics_path):
    """
    Save metrics to disk
    
    Args:
        metrics (dict): Evaluation metrics
        metrics_path (str): Path to save metrics
        
    Returns:
        bool: Success status
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
        
        # Save metrics
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        print(f"Metrics saved to {metrics_path}")
        return True
    except Exception as e:
        print(f"Error saving metrics: {str(e)}")
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
    df_processed = preprocess_batch(df)
    
    # Split features and target
    X = df_processed.drop('is_fraud', axis=1)
    y = df_processed['is_fraud']
    
    # Print feature information
    print(f"\nFeatures ({len(X.columns)}):")
    for col in X.columns:
        print(f"- {col}")
    
    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # Train Random Forest model
    rf_model = train_random_forest(X_train, y_train)
    
    # Evaluate Random Forest model
    rf_pred_proba = rf_model.predict_proba(X_test)[:, 1]
    rf_metrics = evaluate_model(rf_model, X_test, y_test)
    
    # Plot Random Forest evaluation
    plot_roc_curve(y_test, rf_pred_proba, "Random Forest")
    plot_precision_recall_curve(y_test, rf_pred_proba, "Random Forest")
    plot_feature_importance(rf_model, X.columns, "Random Forest")
    
    # Save Random Forest model and metrics
    save_model(rf_model, "models/random_forest_model.pkl")
    save_metrics(rf_metrics, "models/random_forest_metrics.json")
    
    # Train XGBoost model
    xgb_model = train_xgboost(X_train, y_train)
    
    # Evaluate XGBoost model
    dtest = xgb.DMatrix(X_test)
    xgb_pred_proba = xgb_model.predict(dtest)
    xgb_metrics = evaluate_model(xgb_model, X_test, y_test, model_type='xgboost')
    
    # Plot XGBoost evaluation
    plot_roc_curve(y_test, xgb_pred_proba, "XGBoost")
    plot_precision_recall_curve(y_test, xgb_pred_proba, "XGBoost")
    plot_feature_importance(xgb_model, X.columns, "XGBoost")
    
    # Save XGBoost model and metrics
    save_model(xgb_model, "models/xgboost_model.pkl")
    save_metrics(xgb_metrics, "models/xgboost_metrics.json")
    
    # Train Isolation Forest model
    iso_model = train_isolation_forest(X_train)
    
    # Evaluate Isolation Forest model
    iso_pred_score = -iso_model.decision_function(X_test)
    iso_pred_score = (iso_pred_score - iso_pred_score.min()) / (iso_pred_score.max() - iso_pred_score.min())
    iso_metrics = evaluate_model(iso_model, X_test, y_test, model_type='isolation_forest')
    
    # Plot Isolation Forest evaluation
    plot_roc_curve(y_test, iso_pred_score, "Isolation Forest")
    plot_precision_recall_curve(y_test, iso_pred_score, "Isolation Forest")
    
    # Save Isolation Forest model and metrics
    save_model(iso_model, "models/isolation_forest_model.pkl")
    save_metrics(iso_metrics, "models/isolation_forest_metrics.json")
    
    # Save combined metrics
    combined_metrics = {
        'random_forest': rf_metrics,
        'xgboost': xgb_metrics,
        'isolation_forest': iso_metrics,
        'timestamp': datetime.now().isoformat(),
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'features': list(X.columns)
    }
    
    save_metrics(combined_metrics, "models/combined_metrics.json")
    
    print("\nModel training complete!")

if __name__ == "__main__":
    main()