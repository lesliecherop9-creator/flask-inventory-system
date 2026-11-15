from flask import Flask, jsonify

app = Flask(__name__)

inventory = [
    {
        "id": 1,
        "barcode": "0025293002060",
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "ingredients_text": "Filtered water, almonds, cane sugar",
        "price": 3.49,
        "stock": 25,
    },
    {
        "id": 2,
        "barcode": "3017620422003",
        "product_name": "Nutella",
        "brands": "Ferrero",
        "ingredients_text": "Sugar, palm oil, hazelnuts, cocoa",
        "price": 4.99,
        "stock": 40,
    },
]


@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    for item in inventory:
        if item["id"] == item_id:
            return jsonify(item), 200
    return jsonify({"error": "Item not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)