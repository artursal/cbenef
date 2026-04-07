import psycopg2

def check_link():
    conn_url = "postgresql://DB_USER:DB_PASS@DB_HOST:DB_PORT/solutionsp?sslmode=require"
    try:
        conn = psycopg2.connect(conn_url)
        cur = conn.cursor()
        
        # Pega itens recentes e checa o pai (nota)
        cur.execute("""
            SELECT t.cnnota as it_cnnota, n.cnnota as nf_cnnota, n.status, n.innotapropria, n.dtref 
            FROM itnfiscais t 
            LEFT JOIN nfiscais n ON t.cnnota = n.cnnota 
            ORDER BY t.cnitnfiscal DESC 
            LIMIT 50
        """)
        rows = cur.fetchall()
        print("ITENS RECENTES E SUAS NOTAS (TOP 50):")
        for r in rows:
            print(f"Item CNNota: {r[0]} | Nota CNNota: {r[1]} | Status: {r[2]} | Propria: {r[3]} | Data: {r[4]}")
            
        conn.close()
    except Exception as e:
        print(f"LINK CHECK ERROR: {e}")

if __name__ == "__main__":
    check_link()
