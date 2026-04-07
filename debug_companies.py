import psycopg2

def debug_dbs():
    com_url = "postgresql://DB_USER:DB_PASS@DB_HOST:DB_PORT/comfitasdb?sslmode=require"
    mul_url = "postgresql://DB_USER:DB_PASS@DB_HOST:DB_PORT/multinstdb?sslmode=require"
    
    query = """
        SELECT t.cdcfo, t.cdst, t.cdtip, n.cdmodelo, count(t.cnitnfiscal)
        FROM itnfiscais t
        JOIN nfiscais n ON t.cnnota = n.cnnota
        WHERE n.dtref >= '2026-01-01' 
          AND n.status = '131'
        GROUP BY t.cdcfo, t.cdst, t.cdtip, n.cdmodelo
        ORDER BY count DESC;
    """
    
    try:
        print("------- RESULTADOS COMFITASDB 2026 -------")
        conn = psycopg2.connect(com_url)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        print("TOTAL ITENS (STATUS 131):", sum(r[4] for r in rows))
        for r in rows:
            print(f"CFOP: {r[0]} | CST: {r[1]} | NCM: {r[2]} | MOD: {r[3]} | QTD: {r[4]}")
        conn.close()
    except Exception as e:
        print("Erro Comfitas:", e)

    try:
        print("\n------- RESULTADOS MULTINSTDB 2026 -------")
        conn = psycopg2.connect(mul_url)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        print("TOTAL ITENS (STATUS 131):", sum(r[4] for r in rows))
        for r in rows:
            print(f"CFOP: {r[0]} | CST: {r[1]} | NCM: {r[2]} | MOD: {r[3]} | QTD: {r[4]}")
        conn.close()
    except Exception as e:
        print("Erro Multiinst:", e)

if __name__ == "__main__":
    debug_dbs()
