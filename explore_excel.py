import pandas as pd
import json
import os

def explore():
    file_path = 'Tabela-cBenef-SP.xlsx'
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    # Read the excel file
    # Usually the first few rows are headers or info
    df = pd.read_excel(file_path, sheet_name=0, skiprows=0)
    
    print("Columns found:")
    print(df.columns.tolist())
    
    print("\nFirst 5 rows:")
    print(df.head(5).to_string())
    
    # Save a sample to json for inspection
    df.head(20).to_json('sample_data.json', orient='records', indent=4, force_ascii=False)
    print("\nSaved sample_data.json for inspection.")

if __name__ == "__main__":
    explore()
