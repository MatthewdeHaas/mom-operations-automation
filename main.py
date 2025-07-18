import sys
import requests
import pandas as pd 
import sqlite3


# Get data from the google sheet
if len(sys.argv) > 1 and sys.argv[1].lower() == "--get":
    sheet_id = "1y0dLkj7M99k3MNYZ2NQj5Z_epRBSycrk"
    gid = "891988535"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    response = requests.get(url)


    with open("data/production.csv", "wb") as f:
        f.write(response.content)


    # Esablish a database conneciton
    conn = sqlite3.connect("instance/prod.db")
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS production")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS production (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Customer TEXT,
            "Serving Date" TEXT,
            Item TEXT,
            Meal TEXT,
            Day INTEGER,
            "Portion Size grams or each" NUMERIC,
            "Quantity to Produce/Ship" NUMERIC,
            Client TEXT,
            Frozen TEXT,
            Chilled TEXT,
            "Shipment Date" TEXT
        )
    """)


    # Convert .csv format to .sql
    df = pd.read_csv("data/production.csv")
    df.to_sql("production", conn, if_exists="replace", index=False)



# Number of unique customers
conn = sqlite3.connect("instance/prod.db")
cur = conn.cursor()

customers = cur.execute('SELECT * FROM production').fetchall()

print(customers[0])

# print(cur.execute("SELECT * FROM produciton").description)







# Create Packing Slips



# Create Invoices




# Export to readable data format
