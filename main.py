import sys
import requests
import pandas as pd 
import sqlite3


# Get data from the google sheet
if len(sys.argv) > 1 and sys.argv[1].lower() == "get_data":
    sheet_id = "1y0dLkj7M99k3MNYZ2NQj5Z_epRBSycrk"
    gid = "891988535"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    response = requests.get(url)


    with open("data/produciton.csv", "wb") as f:
        f.write(response.content)


    # Esablish a database conneciton
    conn = sqlite3.connect("instance/prod.db")


    # Convert .csv format to .sql
    df = pd.read_csv("data/produciton.csv")
    df.to_sql("produciton", conn, if_exists="replace")





# Create Packing Slips





# Create Invoices




# Export to readable data format
