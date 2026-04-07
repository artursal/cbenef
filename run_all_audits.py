import psycopg2
import csv
from cbenef_engine import CbenefEngine

def generate_audit(db_name):
    conn_url = f"postgresql://DB_USER:DB_PASS@DB_HOST:DB_PORT/{db_name}?sslmode=require"
    engine = CbenefEngine()
    
    try:
        print(f"\\nIniciando auditoria completa da base: {db_name.upper()}...")
        conn = psycopg2.connect(conn_url)
        cur = conn.cursor()
        
        query = """
            SELECT 
                t.cdtip as ncm, 
                t.cdst as cst, 
                t.cdcfo as cfop, 
                t.cdcbenef as cbenef_atual,
                t.cnnota,
                n.dtref as data_nota,
                n.nmcli as cliente,
                n.cdmodelo as modelo
            FROM itnfiscais t
            JOIN nfiscais n ON t.cnnota = n.cnnota
            WHERE n.innotapropria = 'S' 
              AND n.status = '131'
              AND n.dtref >= '2026-01-01'
              AND n.cdmodelo IN ('55', '65')
            ORDER BY n.dtref DESC, t.cnitnfiscal DESC
        """
        
        cur.execute(query)
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        
        file_name = f'Auditoria_cBenef_{db_name.upper()}_2026.csv'
        with open(file_name, mode='w', newline='', encoding='utf-8-sig') as file:
            file.write("sep=;\n")
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Nota', 'Data', 'Modelo', 'Cliente', 'NCM', 'CST', 'CFOP', 'cBenef_Atual_no_Banco', 'cBenef_Sugerido_IA', 'Divergencia', 'Justificativa_Regra'])
            
            for row in rows:
                data = dict(zip(colnames, row))
                
                raw_ncm = str(data.get('ncm') or "").replace('.', '').strip()
                ncm = "".join([c for c in raw_ncm if c.isdigit()])
                
                cst = str(data.get('cst') or "").strip()
                cfop = str(data.get('cfop') or "").strip()
                
                suggestion = engine.suggest(cst, "", ncm=ncm, cfop=cfop)
                val_sug = str(suggestion.get('code') or "SEM CBENEF")
                
                # Omite lixo (CST 00 e sem cbenef) para o relatorio ser enxuto
                if cst == '00' or val_sug == "SEM CBENEF":
                    continue
                
                val_nota = str(data.get('cnnota') or "")
                val_data = str(data.get('data_nota') or "")
                val_mod = str(data.get('modelo') or "").strip()
                val_cli = str(data.get('cliente') or "").replace(";", ",")
                val_atual = str(data.get('cbenef_atual') or "VAZIO").strip()
                val_mot = str(suggestion.get('message') or "").replace(";", ",")
                
                divergencia = "NÃO"
                if val_atual != "VAZIO" and val_atual != val_sug:
                    divergencia = "SIM (VERIFICAR)"
                elif val_atual == "VAZIO":
                    divergencia = "IA SUGERIU PREENCHIMENTO"
                
                writer.writerow([val_nota, val_data, val_mod, val_cli, ncm, cst, cfop, val_atual, val_sug, divergencia, val_mot])
                
        print(f"Auditoria salva com sucesso: {file_name}")
        conn.close()
    except Exception as e:
        print(f"AUDIT ERROR ({db_name}): {e}")

if __name__ == "__main__":
    bases = [
        'solutionsp', 
        'multinstdb', 
        'comfitasdb', 
        'ecotechdb', 
        'juncaodb', 
        'eletrocampdb', 
        'sulcompdb', 
        'tavaresdb'
    ]
    for b in bases:
        generate_audit(b)
