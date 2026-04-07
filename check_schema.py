import psycopg2

def check_nfiscais():
    conn_url = "postgresql://DB_USER:DB_PASS@DB_HOST:DB_PORT/solutionsp?sslmode=require"
    try:
        conn = psycopg2.connect(conn_url)
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM nfiscais LIMIT 0")
        cols = [desc[0] for desc in cur.description]
        print("MODELO COLS:", [c for c in cols if 'mod' in c])
        
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_nfiscais()
