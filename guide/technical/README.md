# Technical Implementation

This section covers the technical aspects of implementing enterprise-grade business applications using Python and N8N. It provides detailed guidance on authentication, error handling, logging, background jobs, webhooks, database integration, and file management.

## Table of Contents

1. [Authentication Methods](#authentication-methods)
2. [Error Handling & Logging](#error-handling--logging)
3. [Background Jobs & Scheduling](#background-jobs--scheduling)
4. [Webhooks & APIs](#webhooks--apis)
5. [Database Integration](#database-integration)
6. [File Management](#file-management)

## Authentication Methods

Secure authentication is critical for enterprise applications. This section covers the most common authentication methods and how to implement them in Python and N8N.

### OAuth 2.0

OAuth 2.0 is the industry standard for API authentication, allowing secure delegated access to resources.

#### Implementation in Python

```python
import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

def get_oauth2_token(client_id, client_secret, token_url):
    """
    Get OAuth 2.0 token using client credentials flow
    
    Args:
        client_id (str): OAuth client ID
        client_secret (str): OAuth client secret
        token_url (str): Token endpoint URL
        
    Returns:
        dict: OAuth token response
    """
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret
    )
    return token

def make_authenticated_request(url, token, method='GET', data=None):
    """
    Make authenticated request using OAuth token
    
    Args:
        url (str): API endpoint URL
        token (dict): OAuth token
        method (str): HTTP method
        data (dict): Request data
        
    Returns:
        requests.Response: API response
    """
    headers = {
        'Authorization': f"Bearer {token['access_token']}",
        'Content-Type': 'application/json'
    }
    
    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        json=data
    )
    
    return response
```

#### Implementation in N8N

N8N provides built-in OAuth 2.0 support for many services. For custom OAuth 2.0 implementation:

1. Create a new credential of type "OAuth2 API"
2. Configure the following settings:
   - Authentication URL
   - Access Token URL
   - Client ID
   - Client Secret
   - Scope (if required)
3. Use the credential in HTTP Request nodes

### API Keys

API keys are simple but effective for many use cases.

#### Implementation in Python

```python
import requests

def make_api_key_request(url, api_key, method='GET', data=None):
    """
    Make request using API key authentication
    
    Args:
        url (str): API endpoint URL
        api_key (str): API key
        method (str): HTTP method
        data (dict): Request data
        
    Returns:
        requests.Response: API response
    """
    # API key in header
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    # Alternative: API key in query parameter
    params = {
        'api_key': api_key
    }
    
    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        # params=params,  # Uncomment for query parameter approach
        json=data
    )
    
    return response
```

#### Implementation in N8N

1. Create a new credential of type "API Key"
2. Configure:
   - API Key field name (e.g., "X-API-Key")
   - API Key value
   - Add to: "Header" or "Query Parameter"
3. Use the credential in HTTP Request nodes

### JWT (JSON Web Tokens)

JWTs provide a secure way to transmit information between parties as a JSON object.

#### Implementation in Python

```python
import jwt
import requests
from datetime import datetime, timedelta

def generate_jwt(secret_key, user_id, expiry_minutes=60):
    """
    Generate JWT token
    
    Args:
        secret_key (str): Secret key for signing
        user_id (str): User identifier
        expiry_minutes (int): Token expiry in minutes
        
    Returns:
        str: JWT token
    """
    payload = {
        'sub': user_id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=expiry_minutes)
    }
    
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token

def make_jwt_request(url, jwt_token, method='GET', data=None):
    """
    Make request using JWT authentication
    
    Args:
        url (str): API endpoint URL
        jwt_token (str): JWT token
        method (str): HTTP method
        data (dict): Request data
        
    Returns:
        requests.Response: API response
    """
    headers = {
        'Authorization': f"Bearer {jwt_token}",
        'Content-Type': 'application/json'
    }
    
    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        json=data
    )
    
    return response
```

#### Implementation in N8N

1. Create a Function node to generate the JWT:

```javascript
const jwt = require('jsonwebtoken');

// Create payload
const payload = {
  sub: 'user123',
  iat: Math.floor(Date.now() / 1000),
  exp: Math.floor(Date.now() / 1000) + (60 * 60) // 1 hour
};

// Sign token
const token = jwt.sign(payload, 'your_secret_key', { algorithm: 'HS256' });

return {json: {token}};
```

2. Use the token in an HTTP Request node:

```
Authorization: Bearer {{$node["JWT_Function"].json.token}}
```

### Basic Authentication

Basic authentication is simple but should only be used over HTTPS.

#### Implementation in Python

```python
import requests
import base64

def make_basic_auth_request(url, username, password, method='GET', data=None):
    """
    Make request using Basic authentication
    
    Args:
        url (str): API endpoint URL
        username (str): Username
        password (str): Password
        method (str): HTTP method
        data (dict): Request data
        
    Returns:
        requests.Response: API response
    """
    # Method 1: Using auth parameter
    response = requests.request(
        method=method,
        url=url,
        auth=(username, password),
        json=data
    )
    
    # Method 2: Manual header creation
    # credentials = f"{username}:{password}"
    # encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    # headers = {
    #     'Authorization': f"Basic {encoded_credentials}",
    #     'Content-Type': 'application/json'
    # }
    # response = requests.request(method=method, url=url, headers=headers, json=data)
    
    return response
```

#### Implementation in N8N

1. Create a new credential of type "Basic Auth"
2. Enter the username and password
3. Use the credential in HTTP Request nodes

### Authentication Best Practices

1. **Secure Storage**: Never hardcode credentials in your code
   ```python
   # Bad
   API_KEY = "1234567890abcdef"
   
   # Good
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   API_KEY = os.getenv("API_KEY")
   ```

2. **Token Refresh**: Implement automatic token refresh for OAuth 2.0
   ```python
   def refresh_token_if_needed(token, client_id, client_secret, token_url):
       """Refresh token if it's expired or about to expire"""
       if token.get('expires_at') and token['expires_at'] < time.time() + 300:  # 5 minutes buffer
           client = BackendApplicationClient(client_id=client_id)
           oauth = OAuth2Session(client=client)
           token = oauth.refresh_token(
               token_url=token_url,
               client_id=client_id,
               client_secret=client_secret,
               refresh_token=token['refresh_token']
           )
       return token
   ```

3. **Credential Rotation**: Implement regular credential rotation
   ```python
   def rotate_api_key(rotation_api_url, current_api_key):
       """Rotate API key"""
       response = requests.post(
           rotation_api_url,
           headers={'Authorization': f"Bearer {current_api_key}"}
       )
       new_api_key = response.json()['new_api_key']
       # Save new API key securely
       return new_api_key
   ```

4. **Scoped Access**: Use the principle of least privilege
   ```python
   # OAuth with specific scopes
   oauth = OAuth2Session(client_id, scope=['read:data', 'write:data'])
   ```

## Error Handling & Logging

Robust error handling and logging are essential for enterprise applications.

### Structured Error Handling

#### Python Exception Hierarchy

```python
class AppError(Exception):
    """Base exception for application errors"""
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(AppError):
    """Validation error"""
    def __init__(self, message):
        super().__init__(message, status_code=400)

class AuthenticationError(AppError):
    """Authentication error"""
    def __init__(self, message):
        super().__init__(message, status_code=401)

class AuthorizationError(AppError):
    """Authorization error"""
    def __init__(self, message):
        super().__init__(message, status_code=403)

class ResourceNotFoundError(AppError):
    """Resource not found error"""
    def __init__(self, message):
        super().__init__(message, status_code=404)

class ExternalServiceError(AppError):
    """External service error"""
    def __init__(self, message, service_name):
        self.service_name = service_name
        super().__init__(f"{service_name} error: {message}", status_code=502)
```

#### Try-Except Pattern

```python
def process_data(data):
    try:
        # Validate input
        if not data:
            raise ValidationError("Data cannot be empty")
        
        # Process data
        result = perform_calculation(data)
        
        # Return result
        return result
    
    except ValidationError as e:
        logger.warning(f"Validation error: {e.message}")
        raise
    
    except ExternalServiceError as e:
        logger.error(f"External service error: {e.message}", extra={
            'service_name': e.service_name
        })
        # Retry logic or fallback
        return fallback_calculation(data)
    
    except Exception as e:
        logger.exception(f"Unexpected error processing data: {str(e)}")
        raise AppError(f"Failed to process data: {str(e)}")
```

### Retry Strategies

#### Exponential Backoff

```python
import time
import random

def retry_with_backoff(func, max_retries=3, base_delay=1, max_delay=60):
    """
    Retry a function with exponential backoff
    
    Args:
        func: Function to retry
        max_retries (int): Maximum number of retries
        base_delay (int): Base delay in seconds
        max_delay (int): Maximum delay in seconds
        
    Returns:
        Result of the function call
    """
    retries = 0
    while True:
        try:
            return func()
        except Exception as e:
            retries += 1
            if retries > max_retries:
                raise
            
            # Calculate delay with jitter
            delay = min(base_delay * (2 ** (retries - 1)) + random.uniform(0, 1), max_delay)
            
            logger.warning(f"Retry {retries}/{max_retries} after {delay:.2f}s due to: {str(e)}")
            time.sleep(delay)
```

#### Using tenacity Library

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    retry=retry_if_exception_type(ExternalServiceError),
    before_sleep=lambda retry_state: logger.info(f"Retrying after {retry_state.next_action.sleep} seconds")
)
def call_external_service(service_url, payload):
    """Call external service with retry logic"""
    response = requests.post(service_url, json=payload)
    
    if response.status_code >= 500:
        raise ExternalServiceError(f"Service returned {response.status_code}", "ExternalAPI")
    
    return response.json()
```

### Comprehensive Logging

#### Logging Configuration

```python
import logging
import logging.config
import json
import os
from datetime import datetime

def setup_logging(log_level=logging.INFO, log_file=None):
    """
    Set up logging configuration
    
    Args:
        log_level: Logging level
        log_file: Log file path
    """
    handlers = {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': log_level
        }
    }
    
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': log_file,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'json',
            'level': log_level
        }
    
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'json': {
                'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)s'
            }
        },
        'handlers': handlers,
        'loggers': {
            '': {
                'handlers': list(handlers.keys()),
                'level': log_level,
                'propagate': True
            }
        }
    })
```

#### Structured Logging

```python
import logging
from uuid import uuid4

# Create logger
logger = logging.getLogger(__name__)

def process_transaction(transaction_data):
    """Process a financial transaction"""
    # Generate request ID for tracing
    request_id = str(uuid4())
    
    # Log with context
    logger.info("Processing transaction", extra={
        'request_id': request_id,
        'transaction_id': transaction_data.get('id'),
        'amount': transaction_data.get('amount'),
        'user_id': transaction_data.get('user_id')
    })
    
    try:
        # Process transaction
        result = perform_transaction(transaction_data)
        
        # Log success
        logger.info("Transaction processed successfully", extra={
            'request_id': request_id,
            'transaction_id': transaction_data.get('id'),
            'result_code': result.get('code')
        })
        
        return result
    
    except Exception as e:
        # Log error with full context
        logger.error("Transaction processing failed", extra={
            'request_id': request_id,
            'transaction_id': transaction_data.get('id'),
            'error': str(e),
            'error_type': e.__class__.__name__
        })
        raise
```

### Error Handling in N8N

N8N provides several ways to handle errors:

#### Error Workflow

1. Create a dedicated error handling workflow
2. In your main workflow, use the "Error Trigger" node to catch errors
3. Configure error notification and recovery actions

#### Error Handling in Workflows

1. Use "IF" nodes to check for error conditions
2. Add error handling paths in your workflow
3. Use the "Error" node to explicitly trigger errors

Example:
```javascript
// Function node to check for errors
if (!$input.json.data) {
  return {
    json: {
      error: true,
      message: "Missing data in response"
    }
  };
}
return $input;
```

#### N8N Error Handling Best Practices

1. **Always check API responses** for error codes and messages
2. **Set up notification channels** for workflow failures (email, Slack)
3. **Use error workflows** for centralized error handling
4. **Implement retry logic** for transient errors
5. **Log detailed error information** for troubleshooting

## Background Jobs & Scheduling

Enterprise applications often need to run tasks in the background and on schedules.

### Python Background Jobs

#### Using Celery

```python
# tasks.py
from celery import Celery

# Initialize Celery
app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def process_data(data_id):
    """Process data in background"""
    try:
        # Get data
        data = get_data_by_id(data_id)
        
        # Process data
        result = perform_processing(data)
        
        # Update status
        update_processing_status(data_id, 'completed', result)
        
    except Exception as e:
        # Log error
        logger.exception(f"Error processing data {data_id}: {str(e)}")
        
        # Update status
        update_processing_status(data_id, 'failed', str(e))

# In your application code
def start_processing(data_id):
    """Start background processing"""
    # Queue task
    process_data.delay(data_id)
    
    # Return immediately
    return {'status': 'processing', 'data_id': data_id}
```

#### Using APScheduler

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

# Configure scheduler
jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}

executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}

job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

scheduler = BackgroundScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults
)

# Define job
def generate_report(report_id, email):
    """Generate report and send email"""
    try:
        # Generate report
        report_data = generate_report_data(report_id)
        report_file = create_report_file(report_data)
        
        # Send email
        send_report_email(email, report_file)
        
        # Update status
        update_report_status(report_id, 'completed')
        
    except Exception as e:
        logger.exception(f"Error generating report {report_id}: {str(e)}")
        update_report_status(report_id, 'failed')

# Schedule job
def schedule_report(report_id, email, run_date):
    """Schedule report generation"""
    job = scheduler.add_job(
        generate_report,
        'date',
        run_date=run_date,
        args=[report_id, email],
        id=f"report_{report_id}",
        replace_existing=True
    )
    
    return job.id

# Start scheduler
scheduler.start()
```

### N8N Scheduling

N8N provides powerful scheduling capabilities:

#### Schedule Trigger

1. Use the "Schedule Trigger" node to start workflows on a schedule
2. Configure using cron expressions or simple intervals
3. Set timezone for accurate scheduling

Example cron expressions:
- Every day at 8 AM: `0 8 * * *`
- Every Monday at 9 AM: `0 9 * * 1`
- Every hour: `0 * * * *`
- Every 15 minutes: `*/15 * * * *`

#### Workflow Chaining

1. Use the "N8N" node to trigger other workflows
2. Pass data between workflows
3. Create modular workflow systems

#### Error Handling in Scheduled Jobs

1. Configure retry settings in the "Schedule Trigger" node
2. Set up error notification workflows
3. Implement idempotent operations for safe retries

## Webhooks & APIs

Webhooks and APIs are essential for integrating applications.

### Creating Webhooks in Python

#### Using Flask

```python
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)

@app.route('/webhook/payment', methods=['POST'])
def payment_webhook():
    """Handle payment webhook"""
    # Get request data
    data = request.json
    
    # Verify webhook signature
    signature = request.headers.get('X-Signature')
    if not verify_signature(data, signature, 'your_webhook_secret'):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Process webhook
    try:
        payment_id = data.get('payment_id')
        status = data.get('status')
        
        # Update payment status
        update_payment_status(payment_id, status)
        
        # Return success
        return jsonify({'success': True}), 200
    
    except Exception as e:
        logger.exception(f"Error processing payment webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

def verify_signature(data, signature, secret):
    """Verify webhook signature"""
    if not signature:
        return False
    
    # Create expected signature
    expected = hmac.new(
        secret.encode('utf-8'),
        request.data,
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures
    return hmac.compare_digest(expected, signature)
```

#### Using FastAPI

```python
from fastapi import FastAPI, Request, Header, HTTPException, Depends
from pydantic import BaseModel
import hmac
import hashlib
from typing import Optional

app = FastAPI()

class PaymentWebhook(BaseModel):
    """Payment webhook data model"""
    payment_id: str
    status: str
    amount: float
    currency: str

async def verify_signature(
    request: Request,
    x_signature: Optional[str] = Header(None)
):
    """Verify webhook signature"""
    if not x_signature:
        raise HTTPException(status_code=401, detail="Missing signature")
    
    # Get request body
    body = await request.body()
    
    # Create expected signature
    secret = "your_webhook_secret"
    expected = hmac.new(
        secret.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures
    if not hmac.compare_digest(expected, x_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    return True

@app.post('/webhook/payment')
async def payment_webhook(
    webhook: PaymentWebhook,
    verified: bool = Depends(verify_signature)
):
    """Handle payment webhook"""
    try:
        # Update payment status
        update_payment_status(webhook.payment_id, webhook.status)
        
        # Return success
        return {'success': True}
    
    except Exception as e:
        logger.exception(f"Error processing payment webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Consuming Webhooks in Python

```python
import requests
import json
import hmac
import hashlib
import time

def send_webhook(url, data, secret=None):
    """
    Send webhook with optional signature
    
    Args:
        url (str): Webhook URL
        data (dict): Webhook data
        secret (str): Secret for signature
        
    Returns:
        requests.Response: Webhook response
    """
    # Convert data to JSON
    payload = json.dumps(data)
    
    # Set headers
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Add signature if secret provided
    if secret:
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        headers['X-Signature'] = signature
    
    # Send webhook
    response = requests.post(url, data=payload, headers=headers)
    
    # Return response
    return response

def send_webhook_with_retry(url, data, secret=None, max_retries=3):
    """Send webhook with retry logic"""
    retries = 0
    while retries < max_retries:
        try:
            response = send_webhook(url, data, secret)
            
            # Check if successful
            if response.status_code < 400:
                return response
            
            # If rate limited, wait and retry
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                logger.warning(f"Rate limited, retrying after {retry_after} seconds")
                time.sleep(retry_after)
                retries += 1
                continue
            
            # If server error, retry
            if response.status_code >= 500:
                retries += 1
                backoff = 2 ** retries
                logger.warning(f"Server error, retrying after {backoff} seconds")
                time.sleep(backoff)
                continue
            
            # Other error, don't retry
            logger.error(f"Webhook failed with status {response.status_code}: {response.text}")
            return response
            
        except requests.RequestException as e:
            retries += 1
            backoff = 2 ** retries
            logger.warning(f"Webhook request failed, retrying after {backoff} seconds: {str(e)}")
            time.sleep(backoff)
    
    logger.error(f"Webhook failed after {max_retries} retries")
    raise Exception(f"Webhook failed after {max_retries} retries")
```

### Webhooks in N8N

N8N provides powerful webhook capabilities:

#### Creating Webhooks

1. Use the "Webhook" node to create endpoints
2. Configure authentication and security settings
3. Process incoming webhook data

#### Webhook Security

1. Use webhook secrets for verification
2. Implement IP filtering
3. Use authentication (API key, OAuth, etc.)

Example webhook verification in N8N:
```javascript
// Function node to verify webhook signature
const crypto = require('crypto');
const secret = 'your_webhook_secret';

// Get request data and signature
const data = $input.json;
const signature = $input.headers['x-signature'];

// Calculate expected signature
const expectedSignature = crypto
  .createHmac('sha256', secret)
  .update(JSON.stringify(data))
  .digest('hex');

// Verify signature
if (signature !== expectedSignature) {
  return {
    json: {
      error: 'Invalid signature'
    }
  };
}

return $input;
```

## Database Integration

Enterprise applications typically require database integration for data persistence.

### SQLAlchemy ORM

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Create base class
Base = declarative_base()

# Define models
class User(Base):
    """User model"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    transactions = relationship('Transaction', back_populates='user')
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Transaction(Base):
    """Transaction model"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='transactions')
    
    def __repr__(self):
        return f"<Transaction(amount={self.amount}, description='{self.description}')>"

# Create engine and session
engine = create_engine('sqlite:///app.db')
Session = sessionmaker(bind=engine)

# Create tables
Base.metadata.create_all(engine)

# Database operations
def create_user(username, email, password_hash):
    """Create a new user"""
    session = Session()
    try:
        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        session.add(user)
        session.commit()
        return user.id
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

def get_user_transactions(user_id):
    """Get user transactions"""
    session = Session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return None
        
        transactions = session.query(Transaction).filter_by(user_id=user_id).all()
        return transactions
    finally:
        session.close()

def create_transaction(user_id, amount, description):
    """Create a new transaction"""
    session = Session()
    try:
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            description=description
        )
        session.add(transaction)
        session.commit()
        return transaction.id
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()
```

### Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# Create engine with connection pooling
engine = create_engine(
    'postgresql://username:password@localhost/dbname',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800
)

# Create session factory
Session = sessionmaker(bind=engine)

# Context manager for session handling
from contextlib import contextmanager

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

# Usage
def get_user(user_id):
    """Get user by ID"""
    with session_scope() as session:
        user = session.query(User).filter_by(id=user_id).first()
        return user
```

### Database Migrations

Using Alembic with SQLAlchemy:

```python
# Initial setup
# alembic init migrations

# alembic.ini
# sqlalchemy.url = postgresql://username:password@localhost/dbname

# migrations/env.py
# from myapp.models import Base
# target_metadata = Base.metadata

# Create migration
# alembic revision --autogenerate -m "Create users and transactions tables"

# Apply migration
# alembic upgrade head

# Rollback migration
# alembic downgrade -1
```

### Database Integration in N8N

N8N provides nodes for various databases:

1. **PostgreSQL**: Connect to PostgreSQL databases
2. **MySQL**: Connect to MySQL databases
3. **Microsoft SQL**: Connect to MS SQL databases
4. **MongoDB**: Connect to MongoDB databases
5. **SQLite**: Connect to SQLite databases

Example workflow:
1. Use "Schedule Trigger" to run daily
2. Use "PostgreSQL" node to execute a query
3. Process the results
4. Send a notification with the results

## File Management

Enterprise applications often need to handle files efficiently.

### File Operations in Python

```python
import os
import shutil
import tempfile
from pathlib import Path

def safe_file_operations(file_path, operation, content=None):
    """
    Perform safe file operations with error handling
    
    Args:
        file_path (str): Path to file
        operation (str): Operation to perform (read, write, append, delete)
        content (str): Content to write (for write and append)
        
    Returns:
        str or bool: File content or success status
    """
    try:
        # Ensure directory exists
        if operation in ('write', 'append'):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Perform operation
        if operation == 'read':
            with open(file_path, 'r') as f:
                return f.read()
        
        elif operation == 'write':
            # Write to temporary file first
            fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(file_path))
            try:
                with os.fdopen(fd, 'w') as f:
                    f.write(content)
                
                # Rename to target file (atomic operation)
                os.replace(temp_path, file_path)
                return True
            except:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise
        
        elif operation == 'append':
            with open(file_path, 'a') as f:
                f.write(content)
            return True
        
        elif operation == 'delete':
            if os.path.exists(file_path):
                os.unlink(file_path)
            return True
        
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    except Exception as e:
        logger.error(f"File operation error ({operation}): {str(e)}")
        raise

def process_csv_file(file_path, output_path):
    """Process CSV file"""
    import csv
    
    try:
        # Read input file
        with open(file_path, 'r', newline='') as f_in:
            reader = csv.DictReader(f_in)
            data = list(reader)
        
        # Process data
        processed_data = []
        for row in data:
            processed_row = {
                'id': row['id'],
                'name': row['name'].upper(),
                'value': float(row['value']) * 1.1  # Add 10%
            }
            processed_data.append(processed_row)
        
        # Write output file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=['id', 'name', 'value'])
            writer.writeheader()
            writer.writerows(processed_data)
        
        return len(processed_data)
    
    except Exception as e:
        logger.error(f"CSV processing error: {str(e)}")
        raise
```

### Cloud Storage Integration

#### AWS S3

```python
import boto3
from botocore.exceptions import ClientError

def s3_operations(bucket_name, operation, key=None, file_path=None, content=None):
    """
    Perform S3 operations
    
    Args:
        bucket_name (str): S3 bucket name
        operation (str): Operation to perform (upload, download, delete, list)
        key (str): S3 object key
        file_path (str): Local file path
        content (str): Content to upload
        
    Returns:
        dict or list or bool: Operation result
    """
    # Create S3 client
    s3 = boto3.client('s3')
    
    try:
        # Perform operation
        if operation == 'upload':
            if file_path:
                s3.upload_file(file_path, bucket_name, key)
            elif content:
                s3.put_object(Body=content, Bucket=bucket_name, Key=key)
            else:
                raise ValueError("Either file_path or content must be provided")
            
            return True
        
        elif operation == 'download':
            if file_path:
                s3.download_file(bucket_name, key, file_path)
                return True
            else:
                response = s3.get_object(Bucket=bucket_name, Key=key)
                return response['Body'].read().decode('utf-8')
        
        elif operation == 'delete':
            s3.delete_object(Bucket=bucket_name, Key=key)
            return True
        
        elif operation == 'list':
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=key or '')
            if 'Contents' in response:
                return [item['Key'] for item in response['Contents']]
            return []
        
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    except ClientError as e:
        logger.error(f"S3 operation error ({operation}): {str(e)}")
        raise
```

#### Google Cloud Storage

```python
from google.cloud import storage

def gcs_operations(bucket_name, operation, blob_name=None, file_path=None, content=None):
    """
    Perform Google Cloud Storage operations
    
    Args:
        bucket_name (str): GCS bucket name
        operation (str): Operation to perform (upload, download, delete, list)
        blob_name (str): GCS blob name
        file_path (str): Local file path
        content (str): Content to upload
        
    Returns:
        dict or list or bool: Operation result
    """
    # Create GCS client
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    try:
        # Perform operation
        if operation == 'upload':
            blob = bucket.blob(blob_name)
            
            if file_path:
                blob.upload_from_filename(file_path)
            elif content:
                blob.upload_from_string(content)
            else:
                raise ValueError("Either file_path or content must be provided")
            
            return True
        
        elif operation == 'download':
            blob = bucket.blob(blob_name)
            
            if file_path:
                blob.download_to_filename(file_path)
                return True
            else:
                return blob.download_as_text()
        
        elif operation == 'delete':
            blob = bucket.blob(blob_name)
            blob.delete()
            return True
        
        elif operation == 'list':
            blobs = client.list_blobs(bucket_name, prefix=blob_name or '')
            return [blob.name for blob in blobs]
        
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    except Exception as e:
        logger.error(f"GCS operation error ({operation}): {str(e)}")
        raise
```

### File Management in N8N

N8N provides several nodes for file operations:

1. **Read Binary File**: Read file content
2. **Write Binary File**: Write content to a file
3. **Move Binary File**: Move files
4. **Copy Binary File**: Copy files
5. **Delete File**: Delete files

Example workflow:
1. Use "Schedule Trigger" to run daily
2. Use "HTTP Request" to download a file
3. Use "Write Binary File" to save the file
4. Process the file
5. Use "S3" node to upload the processed file

## Pro Tip: Building Resilient Systems

When building enterprise-grade applications, resilience is key. Here are some strategies to make your systems more robust:

1. **Circuit Breakers**: Implement circuit breakers to prevent cascading failures when external services are down.

```python
from pybreaker import CircuitBreaker

# Create circuit breaker
db_breaker = CircuitBreaker(
    fail_max=5,
    reset_timeout=60,
    exclude=[ValueError, TypeError]
)

@db_breaker
def query_database(query):
    """Query database with circuit breaker"""
    # If database is down, circuit breaker will open after 5 failures
    # and prevent further calls for 60 seconds
    return db_connection.execute(query)
```

2. **Bulkhead Pattern**: Isolate components to contain failures.

```python
from concurrent.futures import ThreadPoolExecutor

# Create separate thread pools for different services
db_pool = ThreadPoolExecutor(max_workers=10)
api_pool = ThreadPoolExecutor(max_workers=5)
email_pool = ThreadPoolExecutor(max_workers=3)

# Use appropriate pool for each service
def process_user(user_id):
    # Database operations use db_pool
    user_future = db_pool.submit(get_user, user_id)
    
    # API calls use api_pool
    api_future = api_pool.submit(get_user_data_from_api, user_id)
    
    # Email operations use email_pool
    email_future = email_pool.submit(send_welcome_email, user_id)
    
    # Wait for results
    user = user_future.result()
    api_data = api_future.result()
    email_sent = email_future.result()
    
    return {
        'user': user,
        'api_data': api_data,
        'email_sent': email_sent
    }
```

3. **Health Checks**: Implement comprehensive health checks for all components.

```python
def health_check():
    """Perform health check of all components"""
    status = {
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'components': {}
    }
    
    # Check database
    try:
        db_result = db_connection.execute("SELECT 1")
        status['components']['database'] = {
            'status': 'ok',
            'latency_ms': measure_latency(db_connection.execute, "SELECT 1")
        }
    except Exception as e:
        status['components']['database'] = {
            'status': 'error',
            'error': str(e)
        }
        status['status'] = 'degraded'
    
    # Check external API
    try:
        api_response = requests.get(API_URL + '/health', timeout=5)
        if api_response.status_code == 200:
            status['components']['api'] = {
                'status': 'ok',
                'latency_ms': api_response.elapsed.total_seconds() * 1000
            }
        else:
            status['components']['api'] = {
                'status': 'error',
                'error': f"HTTP {api_response.status_code}"
            }
            status['status'] = 'degraded'
    except Exception as e:
        status['components']['api'] = {
            'status': 'error',
            'error': str(e)
        }
        status['status'] = 'degraded'
    
    # Check cache
    try:
        cache_result = cache.ping()
        status['components']['cache'] = {
            'status': 'ok',
            'latency_ms': measure_latency(cache.ping)
        }
    except Exception as e:
        status['components']['cache'] = {
            'status': 'error',
            'error': str(e)
        }
        status['status'] = 'degraded'
    
    return status
```

4. **Graceful Degradation**: Design systems to function with reduced capabilities when components fail.

```python
def get_product_recommendations(user_id):
    """Get product recommendations with graceful degradation"""
    try:
        # Try personalized recommendations first
        recommendations = recommendation_service.get_personalized(user_id)
        return recommendations
    except Exception as e:
        logger.warning(f"Personalized recommendations failed: {str(e)}")
        
        try:
            # Fall back to category-based recommendations
            user = get_user(user_id)
            category = user.get('preferred_category')
            if category:
                recommendations = recommendation_service.get_by_category(category)
                return recommendations
        except Exception as e:
            logger.warning(f"Category recommendations failed: {str(e)}")
        
        # Final fallback to popular products
        try:
            return recommendation_service.get_popular()
        except Exception as e:
            logger.error(f"All recommendation methods failed: {str(e)}")
            return []  # Empty list as last resort
```

5. **Feature Flags**: Use feature flags to control feature availability and rollout.

```python
import os
from functools import wraps

# Simple feature flag system
def feature_enabled(feature_name):
    """Check if feature is enabled"""
    return os.getenv(f"FEATURE_{feature_name.upper()}", "false").lower() == "true"

def feature_flag(feature_name, fallback=None):
    """Feature flag decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if feature_enabled(feature_name):
                return func(*args, **kwargs)
            elif fallback:
                return fallback(*args, **kwargs)
            return None
        return wrapper
    return decorator

# Usage
@feature_flag('new_recommendation_algorithm', fallback=old_recommendation_algorithm)
def new_recommendation_algorithm(user_id):
    """New recommendation algorithm"""
    # Implementation
    pass
```

By implementing these resilience patterns, you'll build systems that can withstand failures and continue to provide value to users even when components fail.