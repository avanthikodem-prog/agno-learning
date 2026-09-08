import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("POSTGRES_DB_URL")

conn = psycopg.connect(db_url)
cur = conn.cursor()

print("Connected to database/user:", end=" ")
cur.execute("SELECT current_database(), current_user;")
print(cur.fetchone())

print("\nTables in ai schema:")

cur.execute("""
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_schema = 'ai'
    ORDER BY table_name;
""")

for table in cur.fetchall():
    print(table)

cur.close()
conn.close()