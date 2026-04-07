import requests
import os
import subprocess

def sync():
    # Official URL for cBenef SP table (Excel)
    # Note: The version number might change, but this is the current one
    url = "https://portal.fazenda.sp.gov.br/servicos/nfe/Downloads/Tabela-cBenef-SP-v20260313.xlsx"
    target = "Tabela-cBenef-SP.xlsx"
    
    print(f"Checking for updates from {url}...")
    
    # Download the file
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(target, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Download successful.")
            
            # Re-parse the table
            print("Parsing updated table...")
            # Use subprocess to run parse_table.py using the venv python
            subprocess.run(["./venv/bin/python3", "parse_table.py"], check=True)
            print("Sync complete.")
        else:
            print(f"Failed to download: {response.status_code}")
    except Exception as e:
        print(f"Error during sync: {e}")

if __name__ == "__main__":
    sync()
