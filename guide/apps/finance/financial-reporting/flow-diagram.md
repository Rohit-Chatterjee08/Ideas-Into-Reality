# Automated Financial Reporting System - Flow Diagram

```mermaid
flowchart TD
    %% Main components
    N8N[N8N Workflow]
    PY[Python Engine]
    DB[(Databases)]
    API[APIs]
    FILES[CSV/Excel Files]
    REPORTS[Generated Reports]
    EMAIL[Email Distribution]
    STORAGE[Cloud Storage]
    SLACK[Slack Notification]
    
    %% Python components
    PY_MAIN[main.py]
    PY_DATA[data_sources.py]
    PY_PROC[data_processing.py]
    PY_VIZ[visualizations.py]
    PY_REP[report_generator.py]
    
    %% N8N nodes
    N8N_TRIGGER[Schedule Trigger]
    N8N_EXEC[Execute Command]
    N8N_CHECK[Check Success]
    N8N_READ[Read Summary]
    N8N_PARSE[Parse JSON]
    N8N_EMAIL[Send Email]
    N8N_NOTIFY[Send Notifications]
    N8N_ERROR[Handle Errors]
    
    %% Data flow
    N8N_TRIGGER --> N8N_EXEC
    N8N_EXEC --> PY
    N8N_EXEC --> N8N_CHECK
    
    N8N_CHECK -->|Success| N8N_READ
    N8N_CHECK -->|Failure| N8N_ERROR
    
    N8N_READ --> N8N_PARSE
    N8N_PARSE --> N8N_EMAIL
    N8N_EMAIL --> N8N_NOTIFY
    
    N8N_ERROR --> EMAIL
    
    %% Python internal flow
    PY --> PY_MAIN
    PY_MAIN --> PY_DATA
    PY_MAIN --> PY_PROC
    PY_MAIN --> PY_VIZ
    PY_MAIN --> PY_REP
    
    %% Data sources
    PY_DATA --> DB
    PY_DATA --> API
    PY_DATA --> FILES
    
    %% Output flow
    PY_REP --> REPORTS
    N8N_EMAIL --> EMAIL
    N8N_NOTIFY --> SLACK
    N8N_EMAIL --> STORAGE
    
    %% Styling
    classDef n8n fill:#2980b9,stroke:#2980b9,color:white
    classDef python fill:#27ae60,stroke:#27ae60,color:white
    classDef data fill:#f39c12,stroke:#f39c12,color:white
    classDef output fill:#8e44ad,stroke:#8e44ad,color:white
    classDef error fill:#c0392b,stroke:#c0392b,color:white
    
    class N8N,N8N_TRIGGER,N8N_EXEC,N8N_CHECK,N8N_READ,N8N_PARSE,N8N_EMAIL,N8N_NOTIFY n8n
    class PY,PY_MAIN,PY_DATA,PY_PROC,PY_VIZ,PY_REP python
    class DB,API,FILES data
    class REPORTS,EMAIL,STORAGE,SLACK output
    class N8N_ERROR error
```

## Data Flow Description

1. **Scheduling & Triggering**:
   - N8N Schedule Trigger initiates the workflow at configured intervals
   - Execute Command node runs the Python script

2. **Data Collection**:
   - Python connects to configured data sources (databases, APIs, files)
   - Raw data is extracted and temporarily stored

3. **Data Processing**:
   - Financial data is cleaned and transformed
   - Analysis is performed based on configuration
   - Metrics are calculated and anomalies detected

4. **Visualization & Report Generation**:
   - Charts and graphs are created based on analysis results
   - PDF reports are generated with data tables and visualizations
   - Excel reports are created with detailed data
   - Interactive dashboards are generated (optional)

5. **Distribution**:
   - N8N reads the report summary JSON
   - Reports are attached to emails and sent to recipients
   - Reports are uploaded to cloud storage (optional)
   - Notifications are sent to Slack or other channels

6. **Error Handling**:
   - Errors are caught and logged
   - Error notifications are sent to administrators
   - The workflow continues with the next scheduled run

## Component Interaction

### Python Components

- **main.py**: Orchestrates the entire reporting process
- **data_sources.py**: Connects to and extracts data from various sources
- **data_processing.py**: Cleans, transforms, and analyzes financial data
- **visualizations.py**: Creates charts, graphs, and interactive visualizations
- **report_generator.py**: Compiles data and visualizations into formatted reports

### N8N Components

- **Schedule Trigger**: Initiates the workflow at specified intervals
- **Execute Command**: Runs the Python script with appropriate parameters
- **Check Success**: Verifies successful execution of the Python script
- **Read Summary**: Reads the report summary JSON file
- **Parse JSON**: Extracts information from the summary
- **Send Email**: Distributes reports to configured recipients
- **Send Notifications**: Alerts stakeholders about report availability
- **Handle Errors**: Manages failures and sends error notifications

This integrated system combines the data processing power of Python with the workflow automation capabilities of N8N to create a robust, enterprise-grade financial reporting solution.