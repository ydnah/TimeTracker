import sqlite3

try:
    con = sqlite3.connect("timetable.db")
    cur = con.cursor()
    print("Successfully Connected to SQLite")

    # Define the date range
    start_date = '2023-11-14'
    # Add time if end date is wanting to be included in the query
    end_date = '2023-11-16 12:59:59'

    # Construct the SQL query
    sql_query = """
    SELECT "application", ROUND(AVG("duration"), 2) AS avg_duration
    FROM "time"
    WHERE "datetime" BETWEEN ? AND ?
    GROUP BY "application"
    """

    # Execute the query with date parameters
    cur.execute(sql_query, (start_date, end_date))
    
    # Fetch and print the results
    rows = cur.fetchall()
    for row in rows:
        print(f"Application: {row[0]}, Average Duration: {row[1]}")

    cur.close()

except sqlite3.Error as error:
    print("Error while executing SQLite query:", error)

finally:
    if con:
        con.close()
        print("SQLite connection is closed")