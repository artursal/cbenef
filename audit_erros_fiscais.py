import psycopg2
import csv
from cbenef_engine import CbenefEngine

def run_error_radar(db_name):
    conn_url = f"postgresql://DB_USER:DB_PASS@DB_HOST:DB_PORT/{db_name}?sslmode=require"
    engine = CbenefEngine()
    
    try:
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
                n.cdmodelo as modelo,
                n.inentrada as entrada_saida
            FROM itnfiscais t
            JOIN nfiscais n ON t.cnnota = n.cnnota
            WHERE n.innotapropria = 'S' 
              AND n.status = '131'
              AND n.dtref >= '2026-01-01'
              AND n.cdmodelo IN ('55', '65')
            ORDER BY 
              CASE WHEN t.cdcfo LIKE '3%' THEN 0 ELSE 1 END,
              n.dtref DESC
        """
        cur.execute(query)
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        
        file_name = f'Radar_Erros_Fiscais_{db_name.upper()}_2026_V2.csv'
        with open(file_name, mode='w', newline='', encoding='utf-8-sig') as file:
            file.write("sep=;\n")
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Nota', 'Data', 'Tipo', 'CFOP', 'CST Utilizado', 'cBenef Atual', 'cBenef IA', 'Erro Encontrado e Sugestao', 'NCM', 'Cliente'])
            
            suspensoes_obrigatorias = ('5901', '6901', '5902', '6902', '5903', '6903', '5924', '6924')
            vendas = ('5101', '5102', '6101', '6102', '5405', '5401', '6401', '6403')
            
            for row in rows:
                data = dict(zip(colnames, row))
                cst = str(data.get('cst') or "").strip()
                cfop = str(data.get('cfop') or "").strip()
                tipo_nota = "ENTRADA" if data.get('entrada_saida') == 'S' else "SAIDA"
                val_atual = str(data.get('cbenef_atual') or "VAZIO").strip()
                
                raw_ncm = str(data.get('ncm') or "").replace('.', '').strip()
                ncm = "".join([c for c in raw_ncm if c.isdigit()])
                
                suggestion = engine.suggest(cst, "", ncm=ncm, cfop=cfop)
                val_sug = str(suggestion.get('code') or "SEM CBENEF")
                
                erro = None
                
                # REGRA 3: Prioridade Adubeira em Importações
                if cfop.startswith('3'):
                    if val_atual != "VAZIO" and val_atual != val_sug:
                        erro = "IMPORTAÇÃO DE ALERTA: Divergência na tag cBenef. Revisar alíquotas de base."
                    elif val_atual == "VAZIO" and val_sug != "SEM CBENEF":
                        erro = "IMPORTAÇÃO DE ALERTA: Nota Fiscal VAZIA, mas Tabela da SEFAZ acusa que existe cBenef para esta isenção/tributação e NCM."
                    else:
                        erro = "IMPORTAÇÃO (Revisão Padrão): CFOP 3 em conformidade técnica com Inteligência (Ambos apontam ausência ou coerência de cBenef). Revisão Aduaneira."

                # REGRA 1: Remessa/Retorno SEM CST 50
                elif cfop in suspensoes_obrigatorias and cst != '50':
                    erro = "Faturado com tributação incorreta. CFOP de Industrialização exige Suspensão (CST 50)."
                
                # REGRA 2: Venda COM CST 50 (Impossivel)
                elif cfop in vendas and cst == '50':
                    erro = "Venda Comercial efetuada com Suspensão Tributária (CST 50). Verifique a Isenção."
                
                if erro:
                    writer.writerow([
                        str(data.get('cnnota')),
                        str(data.get('data_nota')),
                        tipo_nota,
                        cfop,
                        cst,
                        val_atual,
                        val_sug,
                        erro,
                        str(data.get('ncm')),
                        str(data.get('cliente') or "").replace(";", ",")
                    ])
                    
        print(f"Radar finalizado ({db_name}): {file_name}")
        conn.close()
    except Exception as e:
        print(f"ERROR na {db_name}: {e}")

if __name__ == "__main__":
    bancos = ['ecotechdb', 'juncaodb', 'eletrocampdb', 'sulcompdb', 'tavaresdb']
    for b in bancos:
        print(f"\\n---> LANÇANDO RADAR PARA O BANCO: {b.upper()}")
        run_error_radar(b)
