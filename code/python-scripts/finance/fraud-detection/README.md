# Fraud Detection Engine

A machine learning-based system for detecting fraudulent financial transactions in real-time.

## Overview

The Fraud Detection Engine uses multiple machine learning models to identify potentially fraudulent transactions. It can process transactions in batch mode or provide real-time detection through an API.

## Features

- **Multi-Model Approach**: Combines Random Forest, XGBoost, and Isolation Forest models
- **Real-time Detection**: API endpoint for immediate fraud detection
- **Batch Processing**: Process multiple transactions at once
- **Explainable Results**: Provides reasons for fraud flags
- **Alert Management**: Creates and distributes fraud alerts
- **Business Rules**: Applies configurable business rules to detection results
- **Model Training**: Scripts for training and evaluating models

## Directory Structure

```
fraud-detection/
├── main.py                 # Main application script
├── train_models.py         # Model training script
├── create_sample_data.py   # Sample data generator
├── requirements.txt        # Python dependencies
├── utils/                  # Utility modules
│   ├── data_processing.py  # Data preparation and feature engineering
│   ├── model_utils.py      # Model loading and prediction
│   └── alert_handler.py    # Alert creation and distribution
├── config/                 # Configuration files
│   └── fraud_detection_config.json  # Main configuration
├── data/                   # Data files
│   ├── fraud_training_data.csv      # Training data
│   └── test_transactions.json       # Test data
├── models/                 # Trained models and metrics
│   ├── random_forest_model.pkl      # Random Forest model
│   ├── xgboost_model.pkl            # XGBoost model
│   └── isolation_forest_model.pkl   # Isolation Forest model
└── logs/                   # Log files
    └── fraud_alerts.log    # Fraud alert log
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-organization/fraud-detection.git
cd fraud-detection
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Usage

### Generate Sample Data

```bash
python create_sample_data.py
```

This will create sample data files in the `data/` directory:
- `users.json`: Sample user data
- `fraud_training_data.csv`: Training data for models
- `test_transactions.json`: Test transactions
- `realtime_transactions.json`: Transactions for real-time simulation

### Train Models

```bash
python train_models.py
```

This will train and evaluate the models, saving them to the `models/` directory.

### Run in Batch Mode

```bash
python main.py --mode batch --input data/test_transactions.json --output results.json
```

### Run as API Server

```bash
python main.py --mode api --port 5000
```

The API will be available at `http://localhost:5000/detect`.

### API Endpoints

#### Health Check

```
GET /health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2025-08-03T14:02:50.123456"
}
```

#### Detect Fraud

```
POST /detect
```

Request body:
```json
{
  "transaction_id": "TRX-123456",
  "user_id": "USER-123456",
  "timestamp": "2025-08-03T14:02:50.123456",
  "amount": 1500.00,
  "merchant": "Online Electronics Store",
  "category": "Retail",
  "payment_method": "Credit Card"
}
```

Response:
```json
{
  "transaction_id": "TRX-123456",
  "fraud_detected": true,
  "fraud_score": 0.85,
  "confidence": 0.75,
  "alert_id": "FRAUD-20250803140250-abcd1234"
}
```

## Configuration

The main configuration file is `config/fraud_detection_config.json`:

```json
{
  "models": {
    "random_forest": "models/random_forest_model.pkl",
    "xgboost": "models/xgboost_model.pkl",
    "isolation_forest": "models/isolation_forest_model.pkl"
  },
  "history_days": 30,
  "webhook_url": "http://localhost:5678/webhook/fraud-alert",
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

## Integration with N8N

The Fraud Detection Engine can be integrated with N8N for alert handling and workflow automation:

1. Import the workflow from `n8n-workflows/finance/fraud-detection/fraud_alert_workflow.json`
2. Configure the webhook URL in `config/fraud_detection_config.json`
3. Update email addresses and Slack channels in the N8N workflow

## Model Performance

The models are evaluated using the following metrics:

- **AUC (Area Under ROC Curve)**: Measures the model's ability to distinguish between fraud and legitimate transactions
- **Precision**: Proportion of fraud predictions that are correct
- **Recall**: Proportion of actual fraud cases that are detected
- **F1 Score**: Harmonic mean of precision and recall

Typical performance metrics:
- Random Forest: AUC 0.95-0.98
- XGBoost: AUC 0.96-0.99
- Isolation Forest: AUC 0.85-0.90

## Troubleshooting

### Common Issues

1. **Model Loading Errors**:
   - Ensure models are trained and saved in the `models/` directory
   - Check file permissions

2. **API Connection Issues**:
   - Verify the API server is running
   - Check network connectivity and firewall settings

3. **Alert Webhook Failures**:
   - Ensure N8N is running and the webhook is active
   - Verify the webhook URL in the configuration

## License

This project is licensed under the MIT License - see the LICENSE file for details.