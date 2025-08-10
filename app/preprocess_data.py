import sys
import requests
import pandas as pd 
import sqlite3
from jinja2 import Template
import html
from datetime import datetime
import os
# from weasyprint import HTML
from app.db import get_db


# Create a new table for the repsonse named after the given week
def add_week(url, week):

    # Establish a database conneciton
    db = get_db()
    cur = db.cursor()

    # Get data from the google sheet
    response = requests.get(parse_url(url))

    # Store .csv response locally
    os.makedirs("data", exist_ok=True)
    with open(f"data/week_{week}.csv", "wb") as f:
        f.write(response.content)


    # Drop the table if it exists already
    cur.execute(f"DROP TABLE IF EXISTS week_{week}")

    # Create new table
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS week_{week} (
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
    df = pd.read_csv(f"data/week_{week}.csv")
    df.to_sql(f"week_{week}", db, if_exists="replace", index=False)
   
    db.commit()


# Returns the relavent infomation for exporting data from a google sheet from the url
def parse_url(url):

    sheet_id = url[url.index("/d/") + len("/d/"):url.index("/edit?")]

    gid = url[url.index("#gid=") + len("#gid="):]
    
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"



def generate_packing_slips(week):

    # Establish a database conneciton
    db = get_db()
    cur = db.cursor()

    # Get all rows in the Customer column
    data = cur.execute(f'SELECT Customer FROM week_{week}').fetchall()

    # Get unique customers
    customers = list(set([d["Customer"] for d in data]))

    # Create packing slips for each customer
    for customer in customers:

        # Get a list of unique dates
        order_dates = list()

        orders = cur.execute(f'''
        SELECT 
        "Customer", "Serving Date", "Item", "Meal", "Day", "Order Amount", "Quantity", Client, "Quantity to Produce/Ship", "Shipment Date" 
        FROM week_{week}
        WHERE Customer = ?''', (customer, )).fetchall()

        # Populate the list with unqiue date entires
        for order in orders:
            if str(order["Shipment Date"]) not in order_dates:
                order_dates.append(order["Shipment Date"])

        # Order the dates from least to most recent (could fail if the single digit days are entered as one digit)
        order_dates = sorted(order_dates, key=lambda d: datetime.strptime(d, "%d/%b/%y"))


        # Create as many packing slips as there are unique dates
        for date in order_dates:

            # Create the html template for the packing slips
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
                            <p><em>Print Name:</em></p>
                            <p><em>Signature:</em></p>
                        </div>
                    </div>

                </body>
                </html>

            """)

            # Convert the template to html
            html = template.render(
                client=customer,
                date=date,
                orders=list(filter(lambda o: o["Shipment Date"] == date, orders))
            )


            # Write html data to an html file  
            os.makedirs(f"data/{customer}", exist_ok=True)
            os.makedirs(f"data/{customer}/packing_slips", exist_ok=True)


            # HTML(string=html).write_pdf(f"data/{customer}/packing_slips/{customer}_{str(date.replace('/', '_'))}.pdf")


            with open(f"data/{customer}/packing_slips/{customer}_{str(date.replace('/', '_'))}.html", "w") as f:
                f.write(html)

def generate_labels(week):

    # Establish a database conneciton
    db = get_db()
    cur = db.cursor()

    df_original = pd.read_sql_query(f'''SELECT Customer, "Serving Date", Client, Item, Meal, Day, "Portion Size grams or each", "Order Amount", "Quantity to Produce/Ship" FROM week_{week}''', db)

    # These are the list of columns that don't have a trailing column with the column in it (I don't fucking know)
    excluded_cols = ["Customer", "Serving Date", "Client"]

    # Get all rows in the Customer column
    data = cur.execute(f'SELECT Customer FROM week_{week}').fetchall()

    # Get unique customers
    customers = list(set([d["Customer"] for d in data]))


    # Generate a new label file for each unique customer
    for customer in customers:
        df = df_original.query("Customer == @customer")
            
        # Special case for Westover
        if customer == "Westover":
            excluded_cols.remove("Serving Date")
        else:
            df = df.drop("Day", axis="columns")
        
        # Clean up long name
        df = df.rename(columns=({'Portion Size grams or each': 'Portion Size'}))

        # get a list of column names to itereate over
        cols = [col for col in df.columns if col not in excluded_cols]

        # insert labels as columns
        for i, col in enumerate(cols):
            df.insert(loc=df.columns.get_loc(col), column=" " * i, value=[col for _ in range(len(df[col]))])

        # Insert this last fucker
        df.insert(loc=len(list(df.columns)), column=None, value="# ____ of ____")

        # Export to excel
        df.to_excel(f"data/{customer}/{str(customer.replace('/', '_'))}_labels.xlsx", index=False)





# TODO: Create a new .xlsx file that contains a column for ingredients and quantity
def generate_shopping_list(week):

    # Establish a database conneciton
    db = get_db()
    cur = db.cursor()

    # Fetch data
    data = cur.execute(f'SELECT "Item", "Portion Size grams or each", "Order Amount" FROM week_{week}').fetchall()
   
    # Create a unique list of items (foods) that can be looped over
    items = list(set([d["Item"] for d in data]))

    foods = dict() 

    # Calculate the amount of each food
    for item in items:
        foods[item] = sum([e["Portion Size grams or each"] * e["Order Amount"] for e in data if e["Item"] == item])

    
    # Export as .xlsx
    df = pd.DataFrame({'Item': foods.keys(), 'Quantity': foods.values()})
    df.to_excel(f"data/shopping_list.xlsx", index=False)



def get_data(url, week):

    # Create an entry for the given url and week
    add_week(url, week)

    # Create packing slips, labels and shopping list and store them in the 'data' directory
    generate_packing_slips(week)
    generate_labels(week)
    generate_shopping_list(week)






