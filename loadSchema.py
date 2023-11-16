import sqlite3

# Reading in the schema to create the database
# Run once
try:
    # Connect to database
    con = sqlite3.connect("timetable.db")
    cur = con.cursor()
    #print("Successfully Connected to SQLite")

    # Read in the sql file and convert it to a readable sqlite file 
    with open('schema.sql', 'r') as sqlite_file:
        sql_script = sqlite_file.read()

    # Execute the script
    con.executescript(sql_script)
    #print("SQLite script executed successfully")
    # Close the cursor
    cur.close()

# Print error message if any occur while executing scipt
except sqlite3.Error as error:
    print("Error while executing sqlite script", error)

# Once time has been created in database close the connection
finally:
    if con:
        con.close()
        #print("SQlite connection is closed")
