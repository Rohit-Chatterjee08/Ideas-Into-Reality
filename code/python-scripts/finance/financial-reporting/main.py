#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Financial Reporting System - Main Application

This script generates financial reports based on configuration settings.
It extracts data from various sources, performs analysis, and creates
visualizations and reports in PDF and Excel formats.

Author: NinjaTech AI
Date: August 2025
"""

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
    """
    Generate financial reports based on configuration
    
    Args:
        config_path (str): Path to the configuration JSON file
        output_dir (str): Directory to save generated reports
        
    Returns:
        dict: Summary of the report generation process
    """
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