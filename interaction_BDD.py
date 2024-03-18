import sqlite3


conn = sqlite3.connect('inv_pichon.db')
cur = conn.cursor()
cur.execute("INSERT INTO Admins(username,password) VALUES ('tset','test')")
conn.commit()
conn.close()
