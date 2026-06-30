import sys
from Backend.config import Config
import mysql.connector

print('HOST:', Config.DB_HOST)
print('USER:', Config.DB_USER)
print('DB:', Config.DB_NAME)

try:
    conn = mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        ssl_disabled=False,
        connection_timeout=15
    )
    print('KONEKSI: SUCCESS')
    cur = conn.cursor()
    cur.execute('SHOW TABLES')
    tables = [row[0] for row in cur.fetchall()]
    print('TABLES:', tables)
    for table in tables:
        cur.execute(f'DESCRIBE `{table}`')
        cols = cur.fetchall()
        print(f'-- {table} --')
        for col in cols:
            print(col)
        print()
    cur.close()
    conn.close()
except Exception as e:
    print('KONEKSI: FAILED')
    print(type(e).__name__, e)
    sys.exit(1)
