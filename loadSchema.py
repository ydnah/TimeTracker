import sqlite3

try:
    con = sqlite3.connect("timetable.db")
    cur = con.cursor()
    print("Successfully Connected to SQLite")

    with open('schema.sql', 'r') as sqlite_file:
        sql_script = sqlite_file.read()

    con.executescript(sql_script)
    print("SQLite script executed successfully")
    cur.close()

except sqlite3.Error as error:
    print("Error while executing sqlite script", error)

finally:
    if con:
        con.close()
        print("SQlite connection is closed")
