import psycopg2
import json
from cbenef_engine import CbenefEngine

def run_audit_2026():
    conn_url = "postgresql://DB_USER:DB_PASS@DB_HOST:DB_PORT/solutionsp?sslmode=require"
    engine = CbenefEngine()
    
    try:
        conn = psycopg2.connect(conn_url)
        cur = conn.cursor()
        
        # Filtro: Notas autorizadas de 2026
        query = """
            SELECT 
                t.cdtip as ncm, 
                t.cdst as cst, 
                t.cdcfo as cfop, 
                t.cdcest as cest, 
                t.cdextip as ex, 
                t.cdcbenef as cbenef_atual,
                t.dsproduto,
                t.cnnota,
                n.dtref as data_nota
            FROM itnfiscais t
            JOIN nfiscais n ON t.cnnota = n.cnnota
            WHERE n.innotapropria = 'S' 
              AND n.status = '131'
              AND n.dtref >= '2026-01-01'
            ORDER BY n.dtref DESC, t.cnitnfiscal DESC
        """
        
        cur.execute(query)
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        
        print(f"PROCESSANDO {len(rows)} ITENS DO ANO DE 2026...")
        print("-" * 140)
        print("NOTA | DATA | NCM | CST | CFOP | ATUAL | SUGERIDO | MOTIVO")
        print("-" * 140)
        
        count_suggested = 0
        for i, row in enumerate(rows):
            data = dict(zip(colnames, row))
            
            raw_ncm = str(data.get('ncm') or "").replace('.', '').strip()
            ncm = "".join([c for c in raw_ncm if c.isdigit()])
            
            cst = str(data.get('cst') or "").strip()
            cfop = str(data.get('cfop') or "").strip()
            
            suggestion = engine.suggest(cst, "", ncm=ncm, cfop=cfop)
            
            # Contabiliza quantos foram sugeridos (diferentes de SEM CBENEF)
            if suggestion['code'] != "SEM CBENEF":
                count_suggested += 1
            
            # Mostra apenas os primeiros 50 no terminal para nao poluir, mas processa tudo
            if i < 50:
                val_nota = str(data.get('cnnota') or "N/A")
                val_data = str(data.get('data_nota') or "S/D")
                val_atual = str(data.get('cbenef_atual') or "VAZIO")
                val_sug = str(suggestion.get('code') or "SEM CBENEF")
                val_mot = str(suggestion.get('message') or "Sem justificativa")
                print(f"{val_nota} | {val_data} | {ncm} | {cst} | {cfop} | {val_atual} | {val_sug} | {val_mot}")

        print("-" * 140)
        print(f"AUDITORIA 2026 CONCLUIDA: {len(rows)} itens analisados. {count_suggested} itens com beneficio fiscal sugerido pelo motor.")

        conn.close()
    except Exception as e:
        print(f"AUDIT ERROR: {e}")

if __name__ == "__main__":
    run_audit_2026()
