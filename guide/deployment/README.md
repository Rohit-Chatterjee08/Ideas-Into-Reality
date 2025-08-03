# Deployment Infrastructure

This section provides comprehensive instructions for setting up the infrastructure needed to run our enterprise applications. We'll focus on free, open-source tools and platforms that can be used in production environments.

## N8N Self-Hosted Deployment Options

N8N is a powerful workflow automation tool that can be self-hosted in various ways. Below are three options for deploying N8N without any cost.

### Option 1: Railway.app Deployment

Railway.app offers a free tier that's perfect for hosting N8N instances.

#### Prerequisites
- GitHub account
- Railway.app account (sign up at [railway.app](https://railway.app))

#### Deployment Steps

1. **Fork the N8N Railway Template**

```bash
# Clone the repository
git clone https://github.com/railwayapp-templates/n8n.git
cd n8n
```

2. **Deploy to Railway**

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy the project
railway up
```

3. **Configure Environment Variables**

Set the following environment variables in the Railway dashboard:

```
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=your_username
N8N_BASIC_AUTH_PASSWORD=your_secure_password
N8N_HOST=your_railway_domain
N8N_PROTOCOL=https
N8N_PORT=3000
N8N_ENCRYPTION_KEY=your_encryption_key
```

4. **Access Your N8N Instance**

Once deployed, Railway will provide a URL to access your N8N instance.

### Option 2: Render Deployment

Render offers a free tier suitable for N8N deployment.

#### Prerequisites
- GitHub account
- Render account (sign up at [render.com](https://render.com))

#### Deployment Steps

1. **Create a new Web Service in Render**

- Connect your GitHub account
- Select "New Web Service"
- Choose the repository containing your N8N configuration
- Use the following settings:
  - Environment: Docker
  - Build Command: `docker build -t n8n .`
  - Start Command: `docker run -p $PORT:5678 n8n`

2. **Configure Environment Variables**

Set the same environment variables as in the Railway deployment.

3. **Deploy and Access**

Render will build and deploy your N8N instance, providing a URL for access.

### Option 3: Local Docker Setup

For development or internal use, a local Docker setup is ideal.

#### Prerequisites
- Docker installed on your system
- Docker Compose installed on your system

#### Deployment Steps

1. **Create a Docker Compose File**

Create a file named `docker-compose.yml` with the following content:

```yaml
version: '3'

services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=your_username
      - N8N_BASIC_AUTH_PASSWORD=your_secure_password
      - N8N_ENCRYPTION_KEY=your_encryption_key
      - N8N_PROTOCOL=http
      - N8N_HOST=localhost
      - N8N_PORT=5678
    volumes:
      - ./n8n_data:/home/node/.n8n
```

2. **Start N8N**

```bash
docker-compose up -d
```

3. **Access N8N**

Open your browser and navigate to `http://localhost:5678`

## Python Execution Environments

Our applications use Python for data processing and machine learning. Here are the recommended environments for running Python code.

### Google Colab Setup

Google Colab provides a free, cloud-based Python environment with GPU support.

#### Setup Steps

1. **Access Google Colab**

Visit [colab.research.google.com](https://colab.research.google.com) and sign in with your Google account.

2. **Create a New Notebook**

Click on "New Notebook" to create a new Python environment.

3. **Install Required Libraries**

```python
!pip install pandas numpy scikit-learn matplotlib seaborn plotly dash streamlit flask xgboost lightgbm catboost nltk spacy transformers opencv-python
```

4. **Mount Google Drive (Optional)**

For persistent storage:

```python
from google.colab import drive
drive.mount('/content/drive')
```

5. **Clone Repository (Optional)**

To access your project code:

```python
!git clone https://github.com/yourusername/your-repo.git
```

6. **Set Up N8N Connection**

```python
# Install requests library if not already installed
!pip install requests

# Example function to connect to N8N webhook
def send_to_n8n(data, webhook_url):
    import requests
    import json
    
    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, headers=headers, data=json.dumps(data))
    
    return response.status_code, response.text
```

### Local Python Environment Setup

For local development and production deployment.

#### Prerequisites
- Python 3.8+ installed
- pip package manager
- Virtual environment tool (venv, conda, or pipenv)

#### Setup Steps

1. **Create a Virtual Environment**

Using venv:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Using conda:
```bash
conda create -n enterprise-apps python=3.9
conda activate enterprise-apps
```

2. **Install Required Libraries**

```bash
pip install pandas numpy scikit-learn matplotlib seaborn plotly dash streamlit flask xgboost lightgbm catboost nltk spacy transformers opencv-python
```

3. **Create a Requirements File**

```bash
pip freeze > requirements.txt
```

4. **Set Up Environment Variables**

Create a `.env` file:
```
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/your-endpoint
API_KEY=your_api_key
DATABASE_URL=your_database_connection_string
```

5. **Load Environment Variables in Python**

```python
from dotenv import load_dotenv
import os

load_dotenv()
n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")
```

## Public URL Access

To make your applications and N8N workflows accessible via public URLs, you can use the following methods.

### Option 1: ngrok for Local Development

ngrok provides temporary public URLs for local development.

#### Setup Steps

1. **Install ngrok**

Download from [ngrok.com](https://ngrok.com/download) or install via package manager:

```bash
# Using npm
npm install ngrok -g

# Using Homebrew on macOS
brew install ngrok
```

2. **Expose Local N8N Instance**

```bash
ngrok http 5678
```

3. **Expose Python Web Applications**

```bash
# For a Flask app running on port 5000
ngrok http 5000
```

4. **Update N8N Webhook URLs**

In your N8N workflows, update webhook URLs to use the ngrok URL.

### Option 2: Railway.app Public URLs

Railway automatically provides public URLs for deployed services.

1. **Access the URL**

In the Railway dashboard, find the URL for your deployed service.

2. **Configure CORS (if needed)**

For web applications, configure CORS to allow requests from your domain:

```python
# For Flask applications
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
```

### Option 3: Render Public URLs

Render also provides public URLs for all deployed services.

1. **Access the URL**

In the Render dashboard, find the URL for your deployed service.

2. **Configure Custom Domains (Optional)**

In the Render dashboard, you can configure custom domains for your services.

## Environment Configuration

Proper environment configuration is crucial for secure and maintainable applications.

### Managing Secrets

1. **Use Environment Variables**

Never hardcode sensitive information in your code.

```python
import os

api_key = os.environ.get("API_KEY")
database_url = os.environ.get("DATABASE_URL")
```

2. **Use .env Files for Local Development**

```python
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file
```

3. **Use Platform Secret Management**

Both Railway and Render provide secure ways to manage environment variables.

### Configuration Files

For non-sensitive configuration:

```python
import yaml

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)
    
database_name = config["database"]["name"]
```

### Cross-Environment Configuration

Create environment-specific configuration files:

```
config/
  ├── development.yaml
  ├── testing.yaml
  └── production.yaml
```

Load the appropriate configuration:

```python
import os
import yaml

env = os.environ.get("ENVIRONMENT", "development")
config_path = f"config/{env}.yaml"

with open(config_path, "r") as file:
    config = yaml.safe_load(file)
```

## Pro Tip: Secure Deployment Practices

When deploying enterprise applications, security should be a top priority:

1. **Rotate Secrets Regularly**: Set up a process to rotate API keys, passwords, and encryption keys on a regular schedule

2. **Use Least Privilege Principle**: Give each component only the permissions it absolutely needs

3. **Implement Rate Limiting**: Protect your APIs and webhooks from abuse with rate limiting

4. **Set Up Monitoring**: Configure alerts for unusual activity or resource usage

5. **Backup Workflows and Data**: Regularly export N8N workflows and back up application data

6. **Document Recovery Procedures**: Create step-by-step instructions for recovering from failures

7. **Use Version Control**: Keep all configuration files and code in version control

8. **Implement CI/CD**: Automate testing and deployment to reduce human error

Remember: A secure deployment is not just about initial setup but ongoing maintenance and monitoring. Schedule regular security reviews of your infrastructure.