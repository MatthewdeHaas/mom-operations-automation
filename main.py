import sys
import requests
import pandas as pd 
import sqlite3
from jinja2 import Template
import html
from datetime import datetime
import os




# Establish a database conneciton
conn = sqlite3.connect("instance/prod.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()


# Get data from the google sheet
if len(sys.argv) > 1 and sys.argv[1].lower() == "--get":
    sheet_id = "1y0dLkj7M99k3MNYZ2NQj5Z_epRBSycrk"
    gid = "891988535"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    response = requests.get(url)


    with open("data/production.csv", "wb") as f:
        f.write(response.content)

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
    df.to_sql("production", conn, if_exists="replace")



# TODO: Create Packing Slips 
# - For a given customer, create a new packing slip for every unqiue entry on the 'Shipment date' column
# - Packing slip columns - all from the respective customer's order in the prod sheet (starred entires aren't in every sheet):
#   - Customer
#   - Serving
#   - Item
#   - Meal
#   - Order
#   - Quantity
#   - Client
#   - *Hot
#   - *Chilled
#   - *Frozen
#   - # of Bags/pans
# - Either:
#   - Create a dataframe that mirroring the packing slip table
#   - Could also export directly to a packing slip PDF 


# Get all rows in the Customer column
customers_raw = cur.execute('SELECT Customer FROM production').fetchall()

# Get unique customers
customers = list(set([col[0] for col in customers_raw]))

for customer in customers:

    # Get a list of unique dates
    order_dates = list()

    orders = cur.execute('''
    SELECT 
    "Customer", "Serving Date", "Item", "Meal", "Day", "Order Amount", "Quantity", Client, "Quantity to Produce/Ship", "Shipment Date" 
    FROM production 
    WHERE Customer = ?''', (customer, )).fetchall()


    for order in orders:
        if str(order["Shipment Date"]) not in order_dates:
            order_dates.append(order["Shipment Date"])

    # Could fail if the single digit days are entered as one digit
    order_dates = sorted(order_dates, key=lambda d: datetime.strptime(d, "%d/%b/%y"))


    # Create as many packing slips as there are unique dates
    for date in order_dates:
        

        # Jinja2 HTML template for packing slip
        template = Template("""

            <h1>Packing Slip</h1>

            <p>
                <strong>Client:</strong> {{ client }}
            </p>

            <p>
                <strong>Shipment Date:</strong> {{ date }}
            </p>

            <table border="1" cellpadding="5">

                <tr>
                    <th>Serving Date</th>

                    <th>Item</th>

                    <th>Meal</th>

                    <th>Day</th>

                    <th>Order Amount</th>

                    <th>Client</th>

                    <th>Quantity Shipped</th>
                </tr>
                    {% for order in orders %}
                        <tr>    
                            <td>{{ order['Serving Date'] or '' }}</td>

                            <td>{{ order['Item'] or '' }}</td>

                            <td>{{ order['Meal'] or '' }}

                            <td>{{ order['Day'] or '' }}

                            <td>{{ order['Order Amount'] or '' }}
                            
                            <td>{{ order['Client'] or '' }}

                            <td>{{ order['Quantity to Produce/Ship'] or '' }}
                            </td>
                        </tr>
                    {% endfor %}
            </table>

        """)

        # Convert template to html
        html = template.render(
            client=customer,
            date=date,
            orders=orders
        )

            
        os.makedirs(f"data/{customer}", exist_ok=True)
        os.makedirs(f"data/{customer}/packing_slips", exist_ok=True)

        with open(f"data/{customer}/packing_slips/{customer}_{str(date.replace('/', '_'))}.html", "w") as f:
            f.write(html)






# TODO: Create Invoices






# TODO: Create shopping list



# Export to readable data format
