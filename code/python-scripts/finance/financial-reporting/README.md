# Automated Financial Reporting System

A comprehensive system for generating financial reports from multiple data sources with visualizations and automated distribution.

## Overview

The Automated Financial Reporting System extracts financial data from various sources, performs analysis, creates visualizations, and generates PDF and Excel reports. It can be integrated with N8N for scheduling and distribution.

## Features

- **Data Source Integration**: Connect to databases, APIs, Excel files, and CSV files
- **Data Processing**: Clean, transform, and analyze financial data
- **Visualization**: Generate charts and graphs using matplotlib, seaborn, and plotly
- **Report Generation**: Create PDF and Excel reports with tables and visualizations
- **Anomaly Detection**: Identify unusual financial transactions
- **Interactive Dashboards**: Generate web-based interactive dashboards
- **Automation**: Schedule report generation and distribution with N8N

## Directory Structure

```
financial-reporting/
├── main.py                 # Main application script
├── create_sample_data.py   # Script to generate sample data
├── requirements.txt        # Python dependencies
├── utils/                  # Utility modules
│   ├── data_sources.py     # Data source connections
│   ├── data_processing.py  # Data cleaning and analysis
│   ├── visualizations.py   # Chart and graph generation
│   └── report_generator.py # PDF and Excel report creation
├── config/                 # Configuration files
│   ├── report_config.json  # Report configuration
│   ├── recipients.json     # Email recipients
│   └── .env.example        # Environment variables template
├── data/                   # Sample and input data
│   ├── transactions.csv    # Sample transaction data
│   ├── expenses.csv        # Sample expense data
│   └── budget.csv          # Sample budget data
└── reports/                # Generated reports (created at runtime)
    ├── figures/            # Generated visualizations
    └── interactive/        # Interactive dashboards
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-organization/financial-reporting.git
cd financial-reporting
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
cp config/.env.example config/.env
# Edit config/.env with your settings
```

## Usage

### Generate Sample Data

```bash
python create_sample_data.py
```

This will create sample transaction and expense data in the `data/` directory.

### Run the Reporting System

```bash
python main.py
```

By default, this will use the configuration in `config/report_config.json` and save reports to the `reports/` directory.

### Command Line Options

```bash
python main.py --config path/to/config.json --output path/to/output/dir
```

- `--config`: Path to the configuration file (default: value from .env or `config/report_config.json`)
- `--output`: Directory to save reports (default: `reports/`)

## Configuration

### Report Configuration

Edit `config/report_config.json` to configure data sources, analyses, and report options:

```json
{
  "report_title": "Monthly Financial Performance Report",
  "data_sources": [
    {
      "type": "csv",
      "name": "transactions",
      "file_path": "data/transactions.csv"
    }
  ],
  "analyses": [
    {
      "name": "Revenue",
      "type": "time_series",
      "data_source": "transactions",
      "date_column": "transaction_date",
      "value_column": "amount"
    }
  ],
  "create_dashboard": true
}
```

### Email Recipients

Edit `config/recipients.json` to configure email recipients:

```json
{
  "recipients": [
    "finance@company.com",
    "ceo@company.com"
  ],
  "distribution_groups": {
    "executive": [
      "ceo@company.com",
      "cfo@company.com"
    ]
  }
}
```

## Integration with N8N

To automate report generation and distribution with N8N:

1. Import the workflow from `n8n-workflows/finance/financial-reporting/automated_financial_reporting.json`
2. Update the paths in the workflow to match your environment
3. Configure the email settings in N8N
4. Activate the workflow

The workflow will:
1. Run on a schedule (default: daily)
2. Execute the Python script to generate reports
3. Read the report summary
4. Send emails with the reports attached
5. Send notifications on completion or failure

## Customization

### Adding New Data Sources

Extend `utils/data_sources.py` to add new data source types.

### Adding New Analysis Types

Extend `utils/data_processing.py` to add new analysis functions.

### Adding New Visualization Types

Extend `utils/visualizations.py` to add new chart types.

### Customizing Report Templates

Modify `utils/report_generator.py` to customize report layouts and styles.

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Check your database credentials in `.env`
   - Ensure the database server is running
   - Verify network connectivity

2. **Missing Dependencies**:
   - Run `pip install -r requirements.txt`
   - For database connectors, install the specific package (e.g., `pip install pymysql`)

3. **Report Generation Errors**:
   - Check the logs for specific error messages
   - Verify that input data files exist and have the expected format
   - Ensure the output directory is writable

4. **Email Sending Failures**:
   - Verify SMTP settings in `.env`
   - Check network connectivity to the SMTP server
   - Ensure email recipients are properly formatted

## License

This project is licensed under the MIT License - see the LICENSE file for details.