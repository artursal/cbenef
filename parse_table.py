import pandas as pd
import json
import os
import re

def normalize_text(text):
    if not text or pd.isna(text):
        return ""
    return str(text).lower().strip()

def extract_patterns(text):
    if not text or pd.isna(text):
        return {"ncms": [], "cests": [], "exs": []}
    text = str(text)
    # NCM patterns: 8 digits or 4.2.2 format
    ncms = re.findall(r'\b\d{8}\b|\b\d{4}\.\d{2}\.\d{2}\b', text)
    # CEST patterns: 2.3.2 format
    cests = re.findall(r'\b\d{2}\.\d{3}\.\d{2}\b', text)
    # EX patterns: ex 01, ex 02
    exs = re.findall(r'ex\s*\d+', text, re.I)
    
    # Normalize ncms (remove dots)
    ncms = [n.replace('.', '') for n in ncms]
    
    return {"ncms": ncms, "cests": cests, "exs": exs}

def parse_full_table():
    file_path = 'Tabela-cBenef-SP.xlsx'
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    df = pd.read_excel(file_path)
    df.columns = [str(c).strip() for c in df.columns]
    
    database = []
    
    for _, row in df.iterrows():
        code = row.get('Código')
        if pd.isna(code) or str(code).strip() == "" or code == "Código":
            continue
            
        desc = str(row.get('Objeto/descrição') or "")
        obs = str(row.get('Observação') or "")
        disp = str(row.get('Dispositivo') or "")
        
        patterns = extract_patterns(desc + " " + obs + " " + disp)
        
        entry = {
            "code": str(code).strip(),
            "simples_nacional": row.get('Aplica-se ao Simples Nacional') == "SIM",
            "csts": [],
            "dispositivo": disp,
            "descricao": desc,
            "observacao": obs,
            "ncms": patterns['ncms'],
            "cests": patterns['cests'],
            "exs": patterns['exs'],
            "norm_dispositivo": normalize_text(disp),
            "norm_descricao": normalize_text(desc)
        }
        
        for col in df.columns:
            if col.startswith('CST ') and row.get(col) == "SIM":
                entry["csts"].append(col.replace('CST ', ''))
        
        database.append(entry)
        
    with open('cbenef_db.json', 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
    print(f"Production DB indexed with {len(database)} entries and technical patterns.")

if __name__ == "__main__":
    parse_full_table()
