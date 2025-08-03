# Automated Financial Reporting System

## Business Context

Financial institutions and departments need to generate regular reports for compliance, decision-making, and stakeholder communication. This process is often manual, time-consuming, and prone to errors. The Automated Financial Reporting System addresses these challenges by automating the entire reporting workflow from data extraction to report generation and distribution.

## Problem Statement

Financial reporting typically involves:
1. Collecting data from multiple sources (databases, APIs, spreadsheets)
2. Cleaning and transforming the data
3. Performing calculations and analysis
4. Generating visualizations
5. Compiling everything into formatted reports
6. Distributing reports to stakeholders

This manual process can take days, introduces human error, and diverts valuable resources from analysis to report production.

## Solution Overview

Our Automated Financial Reporting System:
- Connects to multiple data sources via APIs and database connections
- Processes and transforms financial data using pandas
- Generates insightful visualizations with matplotlib, seaborn, and plotly
- Creates formatted PDF and Excel reports
- Automatically distributes reports via email or secure file sharing
- Schedules the entire process to run at defined intervals
- Maintains an audit trail of all reports generated

## Business Impact

- **Time Savings**: Reduces report generation time from days to minutes
- **Error Reduction**: Eliminates manual data entry and calculation errors
- **Consistency**: Ensures reports follow the same format and methodology every time
- **Resource Optimization**: Frees up financial analysts to focus on insights rather than report production
- **Compliance**: Ensures timely delivery of required regulatory reports
- **Decision Support**: Provides faster access to financial insights for decision-makers

## Implementation

### System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Data Sources   │────▶│  Python Engine  │────▶│  N8N Workflow   │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│ CSV/Excel Files │     │ Data Processing │     │ Report Trigger  │
│ Databases       │     │ Visualization   │     │ Distribution    │
│ APIs            │     │ Report Creation │     │ Notifications   │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Data Flow

1. **Data Collection**:
   - N8N workflow triggers at scheduled time
   - Python scripts connect to data sources and extract data
   - Data is saved to intermediate CSV files

2. **Data Processing**:
   - Python loads data from intermediate files
   - Performs cleaning, transformation, and calculations
   - Generates analysis and insights

3. **Report Generation**:
   - Python creates visualizations using matplotlib and plotly
   - Compiles data and visualizations into reports using ReportLab or Jinja2 templates
   - Saves reports in PDF and Excel formats

4. **Distribution**:
   - N8N workflow picks up generated reports
   - Sends reports via email or uploads to cloud storage
   - Notifies stakeholders
   - Logs completion for audit trail

### Prerequisites

- Python 3.8+
- N8N self-hosted instance
- Access to data sources (databases, APIs)
- SMTP server for email distribution (optional)

### Python Dependencies

```
pandas
numpy
matplotlib
seaborn
plotly
openpyxl
reportlab
jinja2
sqlalchemy
requests
python-dotenv
```

## Step-by-Step Implementation

### 1. Set Up Data Source Connections

First, we'll create utilities to connect to various data sources:

```python
# utils/data_sources.py
import pandas as pd
import sqlalchemy
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def connect_to_database(connection_string=None):
    """Connect to a database using SQLAlchemy"""
    if connection_string is None:
        connection_string = os.getenv("DATABASE_URL")
    
    engine = sqlalchemy.create_engine(connection_string)
    return engine

def query_database(query, engine=None):
    """Execute a SQL query and return results as DataFrame"""
    if engine is None:
        engine = connect_to_database()
    
    return pd.read_sql(query, engine)

def fetch_from_api(endpoint, params=None, headers=None):
    """Fetch data from an API endpoint"""
    if headers is None:
        headers = {
            'Authorization': f'Bearer {os.getenv("API_KEY")}'
        }
    
    response = requests.get(endpoint, params=params, headers=headers)
    response.raise_for_status()
    
    return response.json()

def load_excel_data(file_path):
    """Load data from Excel file"""
    return pd.read_excel(file_path)

def load_csv_data(file_path):
    """Load data from CSV file"""
    return pd.read_csv(file_path)

def save_to_csv(df, file_path):
    """Save DataFrame to CSV"""
    df.to_csv(file_path, index=False)
    return file_path
```

### 2. Create Data Processing Functions

Next, we'll implement functions to process and analyze financial data:

```python
# utils/data_processing.py
import pandas as pd
import numpy as np

def clean_financial_data(df):
    """Clean and prepare financial data"""
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Handle missing values
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].fillna(0)
    
    # Convert date columns
    date_columns = [col for col in df.columns if 'date' in col.lower()]
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df

def calculate_financial_metrics(df, date_column, amount_column):
    """Calculate key financial metrics"""
    # Group by date (month)
    df['month'] = df[date_column].dt.to_period('M')
    monthly = df.groupby('month')[amount_column].agg(['sum', 'mean', 'count'])
    
    # Calculate cumulative sum
    monthly['cumulative'] = monthly['sum'].cumsum()
    
    # Calculate month-over-month change
    monthly['mom_change'] = monthly['sum'].pct_change() * 100
    
    # Calculate rolling metrics
    monthly['3m_avg'] = monthly['sum'].rolling(3).mean()
    
    return monthly

def segment_by_category(df, category_column, amount_column):
    """Segment data by category"""
    category_totals = df.groupby(category_column)[amount_column].agg(['sum', 'count'])
    category_totals['percentage'] = (category_totals['sum'] / category_totals['sum'].sum()) * 100
    
    return category_totals.sort_values('sum', ascending=False)

def detect_anomalies(df, column, threshold=3):
    """Detect anomalies using Z-score"""
    mean = df[column].mean()
    std = df[column].std()
    
    df['z_score'] = (df[column] - mean) / std
    anomalies = df[df['z_score'].abs() > threshold].copy()
    
    return anomalies
```

### 3. Implement Visualization Functions

Now, let's create functions to generate visualizations:

```python
# utils/visualizations.py
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

def set_styling():
    """Set consistent styling for matplotlib plots"""
    sns.set(style="whitegrid")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 12

def save_plot(plt, filename, directory="reports/figures"):
    """Save matplotlib plot to file"""
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)
    plt.savefig(file_path, bbox_inches='tight', dpi=300)
    plt.close()
    return file_path

def plot_time_series(df, date_column, value_column, title, filename):
    """Create time series plot"""
    set_styling()
    plt.figure()
    
    sns.lineplot(data=df, x=date_column, y=value_column, marker='o')
    
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return save_plot(plt, filename)

def plot_category_breakdown(df, category_column, value_column, title, filename):
    """Create pie chart for category breakdown"""
    set_styling()
    plt.figure()
    
    # Get top categories (limit to 10 for readability)
    top_categories = df.nlargest(10, value_column)
    
    # Create pie chart
    plt.pie(top_categories[value_column], labels=top_categories[category_column], 
            autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title(title)
    
    return save_plot(plt, filename)

def plot_monthly_trend(df, title, filename):
    """Create monthly trend chart with actual vs moving average"""
    set_styling()
    plt.figure()
    
    plt.plot(df.index.astype(str), df['sum'], marker='o', label='Monthly Total')
    plt.plot(df.index.astype(str), df['3m_avg'], linestyle='--', label='3-Month Average')
    
    plt.title(title)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    
    return save_plot(plt, filename)

def create_interactive_dashboard(df, date_column, amount_column, category_column):
    """Create interactive Plotly dashboard"""
    # Time series chart
    fig1 = px.line(df, x=date_column, y=amount_column, title='Time Series Analysis')
    
    # Category breakdown
    category_data = df.groupby(category_column)[amount_column].sum().reset_index()
    fig2 = px.pie(category_data, values=amount_column, names=category_column, 
                 title='Category Distribution')
    
    # Monthly trend
    monthly_data = df.groupby(pd.Grouper(key=date_column, freq='M'))[amount_column].sum().reset_index()
    fig3 = px.bar(monthly_data, x=date_column, y=amount_column, title='Monthly Trend')
    
    # Save as HTML
    os.makedirs("reports/interactive", exist_ok=True)
    fig1.write_html("reports/interactive/time_series.html")
    fig2.write_html("reports/interactive/category_breakdown.html")
    fig3.write_html("reports/interactive/monthly_trend.html")
    
    # Create a combined dashboard
    dashboard = go.Figure()
    
    # Add traces from individual figures
    for trace in fig1.data:
        dashboard.add_trace(trace)
    
    # Update layout
    dashboard.update_layout(title="Financial Dashboard")
    dashboard.write_html("reports/interactive/dashboard.html")
    
    return "reports/interactive/dashboard.html"
```

### 4. Create Report Generation Module

Let's implement the report generation functionality:

```python
# utils/report_generator.py
import os
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_pdf_report(title, data_tables, image_paths, output_path="reports"):
    """Generate a PDF report with data tables and images"""
    os.makedirs(output_path, exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{title.replace(' ', '_')}_{timestamp}.pdf"
    file_path = os.path.join(output_path, filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=1,  # Center alignment
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10
    )
    
    # Build content
    content = []
    
    # Add title
    content.append(Paragraph(title, title_style))
    content.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    content.append(Spacer(1, 20))
    
    # Add data tables
    for table_title, df in data_tables.items():
        content.append(Paragraph(table_title, subtitle_style))
        content.append(Spacer(1, 10))
        
        # Convert DataFrame to list of lists for ReportLab
        data = [df.columns.tolist()] + df.values.tolist()
        
        # Create table
        table = Table(data)
        
        # Add table style
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(table)
        content.append(Spacer(1, 20))
    
    # Add images
    for img_title, img_path in image_paths.items():
        content.append(Paragraph(img_title, subtitle_style))
        content.append(Spacer(1, 10))
        
        # Add image
        img = Image(img_path, width=450, height=300)
        content.append(img)
        content.append(Spacer(1, 20))
    
    # Build PDF
    doc.build(content)
    
    return file_path

def create_excel_report(data_tables, output_path="reports"):
    """Generate an Excel report with multiple sheets"""
    os.makedirs(output_path, exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Financial_Report_{timestamp}.xlsx"
    file_path = os.path.join(output_path, filename)
    
    # Create Excel writer
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        # Write each DataFrame to a different sheet
        for sheet_name, df in data_tables.items():
            df.to_excel(writer, sheet_name=sheet_name, index=True)
            
            # Auto-adjust columns' width
            worksheet = writer.sheets[sheet_name]
            for i, col in enumerate(df.columns):
                column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.column_dimensions[chr(65 + i)].width = column_width
    
    return file_path
```

### 5. Create Main Application Script

Now, let's create the main application script that ties everything together:

```python
# main.py
import os
import argparse
from datetime import datetime
import pandas as pd
import json
from dotenv import load_dotenv

# Import utility modules
from utils.data_sources import (
    connect_to_database, query_database, fetch_from_api,
    load_excel_data, load_csv_data, save_to_csv
)
from utils.data_processing import (
    clean_financial_data, calculate_financial_metrics,
    segment_by_category, detect_anomalies
)
from utils.visualizations import (
    plot_time_series, plot_category_breakdown,
    plot_monthly_trend, create_interactive_dashboard
)
from utils.report_generator import (
    create_pdf_report, create_excel_report
)

# Load environment variables
load_dotenv()

def generate_financial_report(config_path=None, output_dir="reports"):
    """Generate financial reports based on configuration"""
    print(f"Starting financial report generation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load configuration
    if config_path is None:
        config_path = os.getenv("CONFIG_PATH", "config/report_config.json")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract data based on configuration
    print("Extracting data from sources...")
    data_frames = {}
    
    for source in config["data_sources"]:
        source_type = source["type"]
        source_name = source["name"]
        
        try:
            if source_type == "database":
                df = query_database(source["query"])
            elif source_type == "api":
                data = fetch_from_api(source["endpoint"], source.get("params"))
                df = pd.DataFrame(data)
            elif source_type == "excel":
                df = load_excel_data(source["file_path"])
            elif source_type == "csv":
                df = load_csv_data(source["file_path"])
            else:
                print(f"Unknown source type: {source_type}")
                continue
                
            data_frames[source_name] = df
            print(f"Successfully loaded data from {source_name}")
            
        except Exception as e:
            print(f"Error loading data from {source_name}: {str(e)}")
    
    # Process data
    print("Processing data...")
    processed_data = {}
    visualizations = {}
    
    for analysis in config["analyses"]:
        analysis_name = analysis["name"]
        df_name = analysis["data_source"]
        
        if df_name not in data_frames:
            print(f"Data source {df_name} not found for analysis {analysis_name}")
            continue
            
        df = data_frames[df_name].copy()
        
        # Clean data
        df = clean_financial_data(df)
        
        # Perform analysis based on type
        analysis_type = analysis["type"]
        
        try:
            if analysis_type == "time_series":
                date_col = analysis["date_column"]
                value_col = analysis["value_column"]
                
                # Calculate metrics
                metrics = calculate_financial_metrics(df, date_col, value_col)
                processed_data[f"{analysis_name}_metrics"] = metrics
                
                # Create visualization
                title = f"Time Series Analysis: {analysis_name}"
                viz_path = plot_monthly_trend(metrics, title, f"{analysis_name}_trend.png")
                visualizations[f"{analysis_name} Trend"] = viz_path
                
            elif analysis_type == "category_analysis":
                category_col = analysis["category_column"]
                value_col = analysis["value_column"]
                
                # Calculate metrics
                segments = segment_by_category(df, category_col, value_col)
                processed_data[f"{analysis_name}_segments"] = segments
                
                # Create visualization
                title = f"Category Analysis: {analysis_name}"
                viz_path = plot_category_breakdown(segments.reset_index(), 
                                                  category_col, 'sum', 
                                                  title, 
                                                  f"{analysis_name}_categories.png")
                visualizations[f"{analysis_name} Categories"] = viz_path
                
            elif analysis_type == "anomaly_detection":
                value_col = analysis["value_column"]
                threshold = analysis.get("threshold", 3)
                
                # Detect anomalies
                anomalies = detect_anomalies(df, value_col, threshold)
                processed_data[f"{analysis_name}_anomalies"] = anomalies
                
                # No specific visualization for anomalies in this example
                
            else:
                print(f"Unknown analysis type: {analysis_type}")
                
            print(f"Successfully completed analysis: {analysis_name}")
            
        except Exception as e:
            print(f"Error in analysis {analysis_name}: {str(e)}")
    
    # Generate reports
    print("Generating reports...")
    report_files = []
    
    try:
        # Generate PDF report
        pdf_path = create_pdf_report(
            config["report_title"],
            processed_data,
            visualizations,
            output_dir
        )
        report_files.append(pdf_path)
        print(f"PDF report generated: {pdf_path}")
        
        # Generate Excel report
        excel_path = create_excel_report(
            processed_data,
            output_dir
        )
        report_files.append(excel_path)
        print(f"Excel report generated: {excel_path}")
        
        # Generate interactive dashboard if configured
        if config.get("create_dashboard", False):
            main_df_name = config.get("main_data_source")
            if main_df_name in data_frames:
                main_df = data_frames[main_df_name]
                dashboard_path = create_interactive_dashboard(
                    main_df,
                    config.get("dashboard_date_column"),
                    config.get("dashboard_value_column"),
                    config.get("dashboard_category_column")
                )
                report_files.append(dashboard_path)
                print(f"Interactive dashboard generated: {dashboard_path}")
    
    except Exception as e:
        print(f"Error generating reports: {str(e)}")
    
    # Create output summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "report_title": config["report_title"],
        "data_sources": list(data_frames.keys()),
        "analyses_performed": list(processed_data.keys()),
        "report_files": report_files
    }
    
    # Save summary
    summary_path = os.path.join(output_dir, "report_summary.json")
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Report generation completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate financial reports")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--output", help="Output directory for reports")
    
    args = parser.parse_args()
    
    config_path = args.config
    output_dir = args.output or "reports"
    
    generate_financial_report(config_path, output_dir)
```

### 6. Create Configuration File

Let's create a sample configuration file:

```json
{
  "report_title": "Monthly Financial Performance Report",
  "data_sources": [
    {
      "type": "csv",
      "name": "transactions",
      "file_path": "data/transactions.csv"
    },
    {
      "type": "csv",
      "name": "expenses",
      "file_path": "data/expenses.csv"
    }
  ],
  "analyses": [
    {
      "name": "Revenue",
      "type": "time_series",
      "data_source": "transactions",
      "date_column": "transaction_date",
      "value_column": "amount"
    },
    {
      "name": "Expenses",
      "type": "category_analysis",
      "data_source": "expenses",
      "category_column": "category",
      "value_column": "amount"
    },
    {
      "name": "Unusual Transactions",
      "type": "anomaly_detection",
      "data_source": "transactions",
      "value_column": "amount",
      "threshold": 2.5
    }
  ],
  "create_dashboard": true,
  "main_data_source": "transactions",
  "dashboard_date_column": "transaction_date",
  "dashboard_value_column": "amount",
  "dashboard_category_column": "category"
}
```

### 7. Create N8N Workflow

Now, let's create the N8N workflow that will orchestrate this process:

```json
{
  "name": "Automated Financial Reporting",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "days",
              "minutesInterval": 0,
              "hoursInterval": 0
            }
          ]
        }
      },
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1,
      "position": [
        250,
        300
      ]
    },
    {
      "parameters": {
        "command": "cd /path/to/project && python main.py"
      },
      "name": "Generate Reports",
      "type": "n8n-nodes-base.executeCommand",
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
              "value1": "={{ $json.exitCode }}",
              "operation": "equal",
              "value2": "0"
            }
          ]
        }
      },
      "name": "Check Success",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [
        650,
        300
      ]
    },
    {
      "parameters": {
        "filePath": "/path/to/project/reports/report_summary.json"
      },
      "name": "Read Summary",
      "type": "n8n-nodes-base.readBinaryFile",
      "typeVersion": 1,
      "position": [
        850,
        200
      ]
    },
    {
      "parameters": {
        "dataType": "string",
        "value": "={{ $binary.data.toString('utf8') }}"
      },
      "name": "Parse Summary",
      "type": "n8n-nodes-base.set",
      "typeVersion": 1,
      "position": [
        1050,
        200
      ]
    },
    {
      "parameters": {
        "operation": "parseJson",
        "propertyName": "reportData",
        "value": "={{ $json.value }}"
      },
      "name": "JSON Parse",
      "type": "n8n-nodes-base.jsonConvert",
      "typeVersion": 1,
      "position": [
        1250,
        200
      ]
    },
    {
      "parameters": {
        "fromEmail": "reports@company.com",
        "toEmail": "={{ $node[&quot;Read Recipients&quot;].json.recipients }}",
        "subject": "={{ $node[&quot;JSON Parse&quot;].json.reportData.report_title }} - {{ $formatDate(new Date(), &quot;YYYY-MM-DD&quot;) }}",
        "text": "Please find attached the latest financial reports.",
        "attachments": "={{ $node[&quot;Get Report Files&quot;].json.files }}"
      },
      "name": "Send Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "position": [
        1650,
        200
      ]
    },
    {
      "parameters": {
        "filePath": "/path/to/project/config/recipients.json"
      },
      "name": "Read Recipients",
      "type": "n8n-nodes-base.readBinaryFile",
      "typeVersion": 1,
      "position": [
        1250,
        50
      ]
    },
    {
      "parameters": {
        "functionCode": "// Get report files from summary\nconst reportFiles = items[0].json.reportData.report_files;\nconst files = [];\n\n// Add each file to the array\nfor (const file of reportFiles) {\n  files.push(file);\n}\n\nreturn [{json: {files}}];"
      },
      "name": "Get Report Files",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [
        1450,
        200
      ]
    },
    {
      "parameters": {
        "message": "Error generating financial reports",
        "level": "error"
      },
      "name": "Log Error",
      "type": "n8n-nodes-base.log",
      "typeVersion": 1,
      "position": [
        850,
        400
      ]
    },
    {
      "parameters": {
        "toEmail": "admin@company.com",
        "subject": "Financial Report Generation Failed",
        "text": "The automated financial report generation process failed. Please check the logs."
      },
      "name": "Send Error Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "position": [
        1050,
        400
      ]
    }
  ],
  "connections": {
    "Schedule Trigger": {
      "main": [
        [
          {
            "node": "Generate Reports",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Generate Reports": {
      "main": [
        [
          {
            "node": "Check Success",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Check Success": {
      "main": [
        [
          {
            "node": "Read Summary",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Log Error",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Read Summary": {
      "main": [
        [
          {
            "node": "Parse Summary",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Parse Summary": {
      "main": [
        [
          {
            "node": "JSON Parse",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "JSON Parse": {
      "main": [
        [
          {
            "node": "Get Report Files",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Read Recipients": {
      "main": [
        [
          {
            "node": "Send Email",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Get Report Files": {
      "main": [
        [
          {
            "node": "Send Email",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Log Error": {
      "main": [
        [
          {
            "node": "Send Error Email",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

### 8. Create Sample Data Files

Let's create sample data files for testing:

```python
# create_sample_data.py
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Create data directory
os.makedirs("data", exist_ok=True)

# Generate transaction data
def generate_transactions(num_records=1000):
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate dates for the past year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days)]
    
    # Generate random transaction data
    transactions = []
    categories = ['Sales', 'Services', 'Subscriptions', 'Licensing', 'Consulting']
    
    for _ in range(num_records):
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
        
        # Add some anomalies (1% chance)
        if np.random.random() < 0.01:
            amount *= 10
        
        transactions.append({
            'transaction_id': f"TRX-{_:06d}",
            'transaction_date': date.strftime('%Y-%m-%d'),
            'category': category,
            'amount': round(amount, 2),
            'customer_id': f"CUST-{np.random.randint(1, 101):03d}"
        })
    
    return pd.DataFrame(transactions)

# Generate expense data
def generate_expenses(num_records=500):
    # Set random seed for reproducibility
    np.random.seed(43)
    
    # Generate dates for the past year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days)]
    
    # Generate random expense data
    expenses = []
    categories = ['Rent', 'Salaries', 'Marketing', 'Equipment', 'Utilities', 'Travel', 'Software', 'Office Supplies']
    
    for _ in range(num_records):
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
        else:  # Office Supplies
            base_amount = 300
        
        # Add some randomness
        amount = base_amount * (0.8 + 0.4 * np.random.random())
        
        # Add some anomalies (1% chance)
        if np.random.random() < 0.01:
            amount *= 5
        
        expenses.append({
            'expense_id': f"EXP-{_:06d}",
            'expense_date': date.strftime('%Y-%m-%d'),
            'category': category,
            'amount': round(amount, 2),
            'department': np.random.choice(['Sales', 'Marketing', 'Engineering', 'HR', 'Finance'])
        })
    
    return pd.DataFrame(expenses)

# Generate the data
transactions_df = generate_transactions()
expenses_df = generate_expenses()

# Save to CSV
transactions_df.to_csv("data/transactions.csv", index=False)
expenses_df.to_csv("data/expenses.csv", index=False)

print(f"Generated {len(transactions_df)} transactions and {len(expenses_df)} expenses")
print("Files saved to data/transactions.csv and data/expenses.csv")
```

### 9. Create Recipients Configuration

```json
{
  "recipients": [
    "finance@company.com",
    "ceo@company.com",
    "cfo@company.com"
  ]
}
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

### 2. Configure the Application

1. Create a `.env` file with the following variables:
```
DATABASE_URL=sqlite:///data/finance.db
API_KEY=your_api_key
CONFIG_PATH=config/report_config.json
```

2. Update the N8N workflow with the correct paths to your Python script and configuration files.

### 3. Generate Sample Data

```bash
python create_sample_data.py
```

### 4. Run the Application Manually

```bash
python main.py
```

### 5. Import the N8N Workflow

1. Open your N8N instance
2. Go to Workflows
3. Click Import
4. Paste the workflow JSON
5. Update the paths and email settings as needed
6. Save and activate the workflow

## Monitoring and Maintenance

### Logging

The application logs all activities to the console. For production use, consider adding a proper logging configuration:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/financial_reporting.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("financial_reporting")
```

### Error Handling

The application includes basic error handling. For production use, consider adding more robust error handling and retry mechanisms.

### Backup

Regularly back up your configuration files and N8N workflows. Consider using version control for your Python code.

## Pro Tip: Report Customization

Financial reports often need to be tailored to different audiences. Consider extending this system with audience-specific report templates:

1. **Executive Summary**: High-level metrics and visualizations for C-suite executives
2. **Operational Reports**: Detailed breakdowns for department managers
3. **Compliance Reports**: Structured data formatted according to regulatory requirements
4. **Analytical Reports**: In-depth analysis with advanced visualizations for financial analysts

Store these templates separately and select the appropriate one based on the recipient or report type. This approach ensures that each stakeholder receives information in the most useful format for their needs.