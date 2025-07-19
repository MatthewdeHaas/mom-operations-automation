# mom-operations-automation
Script for creating packing slips and invoices for Meals On the Move.


## Running

Clone the repo and create a virtual environment

```
python3 -m venv venv
source venv/bin/activate
```


Install dependencies:

```
pip install -r requirements.txt
```


Create the folders that are not on version control

```
mkdir data
mkdir instance
```


Run the script. Include --get in *args in stdout if you would like to read from the google sheet and populate the database, otherwise it will assume the database is already there:

```
python3 main.py
```

