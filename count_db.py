import psycopg2

def check_status_dist():
    conn_url = "postgresql://DB_USER:DB_PASS@DB_HOST:DB_PORT/solutionsp?sslmode=require"
    try:
        conn = psycopg2.connect(conn_url)
        cur = conn.cursor()
        
        cur.execute("SELECT status, count(*) FROM nfiscais WHERE innotapropria = 'S' GROUP BY status ORDER BY count(*) DESC")
        results = cur.fetchall()
        print(f"DISTRIBUICAO DE STATUS (PROPRIA='S'): {results}")
        
        conn.close()
    except Exception as e:
        print(f"COUNT ERROR: {e}")

if __name__ == "__main__":
    check_status_dist()
