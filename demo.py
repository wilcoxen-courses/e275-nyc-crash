"""
demo.py
Mar 2026 PJW

Demonstrate SQL query methods and the use of SQLite databases.
"""

import sqlite3
import pandas as pd
import os
import sys

#
#  Check whether the database has been downloaded.
#

eia_file = 'demo.db'

if not os.path.exists(eia_file):
    print('\nNeed to download demo.db to run the remainder of the script')
    sys.exit()

#
#  Connect to it
#

con = sqlite3.connect(eia_file)

#
#  Get its schema from the sqlite_master table.
#

cur = con.execute("SELECT name,sql FROM sqlite_master;")
rows = cur.fetchall()

#
#  The result is a list of tuples with the table name and its
#  definition. Turn it into a dictionary for convenience.
#

schema = { table:sql for table,sql in rows }

#
#  List the tables. The autoindex tables are indexes that are
#  built automatically by SQLite using the primary keys of each
#  table.
#

print(f'Tables in {eia_file}:')
for table in schema.keys():
    print("   ",table)

#%%
#
#  Now print the definitions of the data tables
#

for table in ['Utility','Plant','Generator']:
    print("\nTable:",table,"\n")
    print(schema[table])

#%%
#
#  Get and print the records in the utility table using
#  core sqlite techniques
#

cur = con.execute("SELECT * FROM Utility;")
rows = cur.fetchall()

#
#  Print the first few rows
#

for i,row in enumerate(rows[:3]):
    print(f'\nRow {i}:\n')
    print(row)

#%%
#
#  Column names can be obtained from a cursor description. The
#  description is a tuple of tuples: one for each column. The
#  first element of each tuple is the column name and the remainder
#  are None (extra elements are for compatibility with another
#  standard Python module).
#

cur_info = cur.description

cols = [c[0] for c in cur_info]
print('\nColumn names:')
for c in cols:
    print('   ',c)

#%%
#
#  Selecting the data via Pandas
#

utility = pd.read_sql("SELECT * FROM Utility;", con)
print(utility.head())

#%%
#
#  Using the COUNT() function to count records
#

sql_count = """
    SELECT
        State,
        COUNT(*) AS count
    FROM
        Utility
    GROUP BY
        State;
    """

data = pd.read_sql(sql_count,con)
print(data)

#%%
#
#  Working with column names with spaces
#

sql = """
    SELECT
        County,
        SUM(`Nameplate MW`) AS mw
    FROM
        Generator
    JOIN
        Plant
        ON Plant.PID = Generator.PID
    WHERE
        Plant.State = 'NY'
    GROUP BY
        County
    ORDER BY
        mw DESC
    """

data = pd.read_sql(sql,con)
print(data)

#%%
#
#  Using a WHERE clause with IN
#

sql = """
    SELECT
        p.State AS plant_state,
        u.State AS utility_state,
        COUNT(*) AS count
    FROM
        Plant AS p
    JOIN
        Utility AS u
        USING(UID)
    WHERE
        p.State IN ('VT','NH')
    GROUP BY
        p.State, u.State
    ORDER BY
        p.State, count DESC, u.State
    """

data = pd.read_sql(sql,con)
print(data)

#%%
#
#  Using a subquery with an IN clause
#

sql = """
    SELECT
        Technology,
        `Energy Source`,
        COUNT(*) AS number,
        SUM(`Nameplate MW`) AS total_mw
    FROM
        Generator
    WHERE PID IN
        (
        SELECT PID
        FROM Plant
        WHERE County = 'Oswego'
        )
    GROUP BY
        Technology, `Energy Source`
    ORDER BY
        total_mw DESC, Technology
    """

data = pd.read_sql(sql,con)
print(data)

#%%
#
#  Look up NYS generating capacity by technology
#

sql = """
    SELECT
        Technology,
        SUM(`Nameplate MW`) AS total_mw,
        `Startup Time`
    FROM
        Generator
    WHERE PID IN
        (
        SELECT PID
        FROM Plant
        WHERE State = 'NY'
        )
    GROUP BY
        Technology, `Startup Time`
    ORDER BY
        total_mw DESC
    ;
    """

data = pd.read_sql(sql,con)
print(data)

#%%
#
#  Using CAST to change a data type. This is mostly useful when
#  the data will be further manipulated by pandas since SQL
#  automatically handles many type conversions.
#

sql = """
    SELECT
        `Grid kV`,
        CAST(`Grid kV` AS NUMERIC) AS kV,
        COUNT(*) as count
    FROM
        Plant
    WHERE
        State = 'CA'
    GROUP BY
        `Grid kV`
    ;
"""

data = pd.read_sql(sql,con)
print(data)
data.info()

#%%
#
#  Using LIKE in a WHERE clause
#

sql = """
    SELECT
        Name,
        State
    FROM
        Utility
    WHERE
        Name LIKE '%national grid%'
    ;
"""

data = pd.read_sql(sql,con)
print(data)

con.close()
