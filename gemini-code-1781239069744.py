import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def run_automated_pipeline():
    print(f"[{datetime.now()}] Starting automated cleaning pipeline...")
    
    # 1. EXTRACT: Automatically grab the latest CSV file from an intake directory
    input_files = glob.glob("data_intake/*.csv")
    if not input_files:
        print("No new files found in data_intake/ folder.")
        return
    
    latest_file = max(input_files, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    initial_rows = len(df)
    
    # 2. TRANSFORM: Automated Cleaning Steps
    # Step A: Drop absolute duplicate records
    df.drop_duplicates(inplace=True)
    
    # Step B: Standardize messy text column formatting
    if 'Region' in df.columns:
        df['Region'] = df['Region'].str.strip().str.upper()
    
    # Step C: Handle missing numeric values dynamically using median imputation
    if 'Revenue' in df.columns:
        # Fill NaN values with the median of that specific column
        median_rev = df['Revenue'].median()
        df['Revenue'].fillna(median_rev, inplace=True)
        
    # Step D: Enforce correct data types (Dates often import as plain text strings)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True) # Drop records with unfixable corrupted dates
        
    cleaned_rows = len(df)
    print(f"Cleaned {initial_rows - cleaned_rows} problematic rows from {os.path.basename(latest_file)}.")

    # 3. LOAD: Generate automated aggregates and visual reporting
    # Calculate summary metrics
    summary = df.groupby('Region')['Revenue'].sum().reset_index()
    
    # Automate the generation and saving of an analytical summary chart
    plt.figure(figsize=(8, 5))
    plt.bar(summary['Region'], summary['Revenue'], color='#1f77b4')
    plt.title(f"Automated Revenue Summary - Generated {datetime.date(datetime.now())}")
    plt.ylabel("Total Revenue ($)")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Create output directory if it doesn't exist
    os.makedirs("automated_reports", exist_ok=True)
    
    # Save report artifacts
    chart_path = "automated_reports/revenue_summary_chart.png"
    csv_path = "automated_reports/cleaned_data_summary.csv"
    
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()
    summary.to_csv(csv_path, index=False)
    
    print(f"Pipeline complete! Report outputs saved to 'automated_reports/' directory.\n")

if __name__ == "__main__":
    run_automated_pipeline()