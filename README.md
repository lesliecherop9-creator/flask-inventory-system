# Inventory Management System

A small Flask REST API with a command-line interface (CLI) for managing a store's inventory.
Product details can be fetched from the [OpenFoodFacts API](https://world.openfoodfacts.org/).
Data is stored in a Python list (a mock database), so it resets when the server restarts.

## Installation and Setup

1. Clone the repository:
   ```
   git clone https://github.com/lesliecherop9-creator/flask-inventory-system.git
   cd flask-inventory-system
   ```
2. Create and activate a virtual environment:
   ```
   py -m venv venv
   venv\Scripts\activate
3. Install the packages:
   ```
   pip install -r requirements.txt
   ```

## Run the API

py app.py```

The server runs at http://127.0.0.1:5000 with Flask debug mode on.

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | /inventory | Fetch all items |
| GET | /inventory/<id> | Fetch a single item |
| POST | /inventory | Add a new item (`product_name` is required) |
| PATCH | /inventory/<id> | Update an item (for example `price` or `stock`) |
| DELETE | /inventory/<id> | Remove an item |
| GET | /lookup?barcode=... or /lookup?name=... | Find a product on OpenFoodFacts |
| POST | /inventory/import | Fetch a product by `barcode` from OpenFoodFacts and add it to the inventory |

Example item:

```json
{
  "id": 1,
  "barcode": "0025293002060",
  "product_name": "Organic Almond Milk",
  "brands": "Silk",
  "ingredients_text": "Filtered water, almonds, cane sugar",
  "price": 3.49,
  "stock": 25
}
```

Errors are returned as JSON, for example `{"error": "Item not found"}` with a 404 status.

## CLI Usage

Start the API first. Then open a second terminal, activate the virtual environment and run:

py cli.py list
py cli.py view 1
py cli.py add "Green Tea" --brand Lipton --price 2.5 --stock 30
py cli.py update 1 --price 4.20 --stock 12
py cli.py delete 2
py cli.py find --barcode 3017620422003
py cli.py find --name "nutella"
py cli.py import 3017620422003 --price 4.99 --stock 20
```

If the server is not running or the API returns an error, the CLI prints a short error message.

## Tests

py -m pytest -v
```

The tests cover the API routes, the OpenFoodFacts functions and the CLI commands.
Calls to the external API are faked with `unittest.mock`, so no internet is needed.

## Debugging

Flask debug mode is on, and the routes can also be checked with Postman,
for example `GET http://127.0.0.1:5000/inventory`.

## Project Structure

```
app.py            Flask API
cli.py            Command-line interface
test_app.py       Tests
requirements.txt  Packages
docs/design.md    Route design
```