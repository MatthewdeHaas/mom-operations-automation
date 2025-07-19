import sys
import requests
import pandas as pd 
import sqlite3
from jinja2 import Template
import html
from datetime import datetime
import os




# Establish a database conneciton
os.makedirs("instance", exist_ok=True)
conn = sqlite3.connect("instance/prod.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()


# Get data from the google sheet
if len(sys.argv) > 1 and sys.argv[1].lower() == "--get":
    sheet_id = "1y0dLkj7M99k3MNYZ2NQj5Z_epRBSycrk"
    gid = "891988535"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    response = requests.get(url)


    os.makedirs("data", exist_ok=True)
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



# TODO: Create Packing Slips - DONE
def generate_packing_slips():

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

        # Populate the list with unqiue date entires
        for order in orders:
            if str(order["Shipment Date"]) not in order_dates:
                order_dates.append(order["Shipment Date"])

        # Order the dates from least to most recent (could fail if the single digit days are entered as one digit)
        order_dates = sorted(order_dates, key=lambda d: datetime.strptime(d, "%d/%b/%y"))


        # Create as many packing slips as there are unique dates
        for date in order_dates:
           

            template = Template("""
               
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Packing Slip</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            margin: 40px;
                        }
                        h1 {
                            text-align: center;
                        }
                        table {
                            border-collapse: collapse;
                            width: 100%;
                            margin-top: 20px;
                        }
                        th, td {
                            border: 1px solid #000;
                            padding: 8px;
                        }
                        .footer {
                            margin-top: 50px;
                        }
                        .signature-box {
                            margin-top: 40px;
                        }
                        .signature-line {
                            width: 300px;
                            border-bottom: 1px solid #000;
                            margin-bottom: 5px;
                        }
                        .note-box {
                            border: 1px solid #aaa;
                            padding: 10px;
                            margin-top: 20px;
                            background-color: #f9f9f9;
                        }
                    </style>
                </head>
                <body>

                    <h1>Packing Slip</h1>

                    <p><strong>Client:</strong> {{ client }}</p>
                    <p><strong>Shipment Date:</strong> {{ date }}</p>


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


                    <div class="footer">
                        <div class="signature-box">
                            <p><strong>Packed By:</strong> ____________________________</p>
                            <p><strong>Checked By:</strong> ____________________________</p>
                            <p><strong>Date:</strong> ____________________________</p>
                            <div class="signature-line"></div>
                            <p><em>Print Name</em></p>
                            <p><em>Signature</em></p>
                        </div>
                    </div>

                </body>
                </html>

            """)






            # Create the html template for the packing slips
            template_1 = Template("""

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

            # Convert the template to html
            html = template.render(
                client=customer,
                date=date,
                orders=orders
            )

            # Write html data to an html file  
            os.makedirs(f"data/{customer}", exist_ok=True)
            os.makedirs(f"data/{customer}/packing_slips", exist_ok=True)
            with open(f"data/{customer}/packing_slips/{customer}_{str(date.replace('/', '_'))}.html", "w") as f:
                f.write(html)






# TODO: Create Invoices
def generate_invoices():
    pass





# TODO: Create shopping list



# Export to readable data format




if __name__ == "__main__":
    generate_packing_slips()
