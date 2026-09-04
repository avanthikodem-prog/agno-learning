import sqlite3

connection = sqlite3.connect("sessions.db")

print("Sessions:")
rows = connection.execute(
    "SELECT * FROM agno_sessions"
).fetchall()

for row in rows:
    print(row)

connection.close()