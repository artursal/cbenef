import psycopg2

def list_all_it_cols():
    conn_url = "postgresql://DB_USER:DB_PASS@DB_HOST:DB_PORT/solutionsp?sslmode=require"
    try:
        conn = psycopg2.connect(conn_url)
        cur = conn.cursor()
        
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'itnfiscais'")
        cols = [r[0] for r in cur.fetchall()]
        print(f"ALL ITNFISCAIS COLS: {cols}")
        
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    list_all_it_cols()
