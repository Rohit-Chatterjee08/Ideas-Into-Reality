#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Sources Module for Financial Reporting System

This module provides functions to connect to various data sources
including databases, APIs, Excel files, and CSV files.

Author: NinjaTech AI
Date: August 2025
"""

import pandas as pd
import sqlalchemy
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def connect_to_database(connection_string=None):
    """
    Connect to a database using SQLAlchemy
    
    Args:
        connection_string (str): Database connection string
        
    Returns:
        sqlalchemy.engine.Engine: Database connection engine
    """
    if connection_string is None:
        connection_string = os.getenv("DATABASE_URL")
    
    engine = sqlalchemy.create_engine(connection_string)
    return engine

def query_database(query, engine=None):
    """
    Execute a SQL query and return results as DataFrame
    
    Args:
        query (str): SQL query to execute
        engine (sqlalchemy.engine.Engine): Database connection engine
        
    Returns:
        pandas.DataFrame: Query results
    """
    if engine is None:
        engine = connect_to_database()
    
    return pd.read_sql(query, engine)

def fetch_from_api(endpoint, params=None, headers=None):
    """
    Fetch data from an API endpoint
    
    Args:
        endpoint (str): API endpoint URL
        params (dict): Query parameters
        headers (dict): HTTP headers
        
    Returns:
        dict: API response data
    """
    if headers is None:
        headers = {
            'Authorization': f'Bearer {os.getenv("API_KEY")}'
        }
    
    response = requests.get(endpoint, params=params, headers=headers)
    response.raise_for_status()
    
    return response.json()

def load_excel_data(file_path):
    """
    Load data from Excel file
    
    Args:
        file_path (str): Path to Excel file
        
    Returns:
        pandas.DataFrame: Excel data
    """
    return pd.read_excel(file_path)

def load_csv_data(file_path):
    """
    Load data from CSV file
    
    Args:
        file_path (str): Path to CSV file
        
    Returns:
        pandas.DataFrame: CSV data
    """
    return pd.read_csv(file_path)

def save_to_csv(df, file_path):
    """
    Save DataFrame to CSV
    
    Args:
        df (pandas.DataFrame): Data to save
        file_path (str): Output file path
        
    Returns:
        str: Path to saved file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    df.to_csv(file_path, index=False)
    return file_path