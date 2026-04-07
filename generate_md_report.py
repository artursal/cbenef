import psycopg2
import json
from cbenef_engine import CbenefEngine

def run_audit_md():
    conn_url = "postgresql://DB_USER:DB_PASS@DB_HOST:DB_PORT/solutionsp?sslmode=require"
    engine = CbenefEngine()
    
    try:
        conn = psycopg2.connect(conn_url)
        cur = conn.cursor()
        
        # Filtro de Modelo 55 e 65 já incluso no WHERE
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
        
        with open('Relatorio_cBenef_2026.md', 'w', encoding='utf-8') as f:
            f.write("# 📊 Relatório de Auditoria Fiscal cBenef - Ano 2026 (Filtrado)\n\n")
            f.write("> **Filtros Aplicados:** Apenas Notas Modelos 55 e 65. Omitidos registros sem benefício fiscal (CST 00 e SEM CBENEF).\n\n")
            f.write("| Nota | Data | Mod | Cliente | NCM | CST | CFOP | Banco | Motor IA | Motivo |\n")
            f.write("|------|------|-----|---------|-----|-----|------|-------|----------|--------|\n")
            
            count_total = len(rows)
            count_exibidos = 0
            
            for row in rows:
                data = dict(zip(colnames, row))
                
                raw_ncm = str(data.get('ncm') or "").replace('.', '').strip()
                ncm = "".join([c for c in raw_ncm if c.isdigit()])
                
                cst = str(data.get('cst') or "").strip()
                cfop = str(data.get('cfop') or "").strip()
                
                # Inteligencia do motor
                suggestion = engine.suggest(cst, "", ncm=ncm, cfop=cfop)
                val_sug = str(suggestion.get('code') or "SEM CBENEF")
                
                # OMITIR REGISTROS CST 00 OU SEM CBENEF
                if cst == '00' or val_sug == "SEM CBENEF":
                    continue
                    
                count_exibidos += 1
                
                val_nota = str(data.get('cnnota') or "N/A")
                val_data = str(data.get('data_nota') or "S/D")
                val_mod = str(data.get('modelo') or "N/A").strip()
                val_cli = str(data.get('cliente') or "NÃO INFORMADO")[:20] # Limitando a 20 caracteres para a tabela
                val_atual = str(data.get('cbenef_atual') or "VAZIO")
                val_mot = str(suggestion.get('message') or "Sem justificativa")
                
                alerta = ""
                if val_atual != "VAZIO" and val_atual != val_sug:
                    alerta = " ⚠️"
                
                f.write(f"| {val_nota} | {val_data} | {val_mod} | {val_cli} | {ncm} | {cst} | {cfop} | {val_atual} | **{val_sug}**{alerta} | {val_mot} |\n")

            f.write(f"\n✅ **Resumo:** De {count_total} itens analisados (Mod 55/65), **{count_exibidos}** exigem benefício fiscal e foram exibidos acima.\n")
            
        print("Novo relatorio limpo e com clientes gerado com sucesso!")
        conn.close()
    except Exception as e:
        print(f"AUDIT ERROR: {e}")

if __name__ == "__main__":
    run_audit_md()
