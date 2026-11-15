from flask import Flask, jsonify, request

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

def get_next_id():
    highest = 0
    for item in inventory:
        if item["id"] > highest:
            highest = item["id"]
    return highest + 1



@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    for item in inventory:
        if item["id"] == item_id:
            return jsonify(item), 200
    return jsonify({"error": "Item not found"}), 404



@app.route("/inventory", methods=["POST"])
def add_item():
    data = request.get_json()

    # Check that the client sent a product name
    if not data or "product_name" not in data:
        return jsonify({"error": "product_name is required"}), 400

    price = data.get("price", 0)
    stock = data.get("stock", 0)

    # Check that price and stock are numbers
    if not isinstance(price, (int, float)) or not isinstance(stock, int):
        return jsonify({"error": "price must be a number and stock a whole number"}), 400

    new_item = {
        "id": get_next_id(),
        "barcode": data.get("barcode", ""),
        "product_name": data["product_name"],
        "brands": data.get("brands", ""),
        "ingredients_text": data.get("ingredients_text", ""),
        "price": price,
        "stock": stock,
    }

    inventory.append(new_item)
    return jsonify(new_item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    # Find the item
    found_item = None
    for item in inventory:
        if item["id"] == item_id:
            found_item = item

    if found_item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data given"}), 400

    if "price" in data and not isinstance(data["price"], (int, float)):
        return jsonify({"error": "price must be a number"}), 400
    if "stock" in data and not isinstance(data["stock"], int):
        return jsonify({"error": "stock must be a whole number"}), 400

    for field in ["product_name", "brands", "ingredients_text", "barcode", "price", "stock"]:
        if field in data:
            found_item[field] = data[field]

    return jsonify(found_item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    for item in inventory:
        if item["id"] == item_id:
            inventory.remove(item)
            return jsonify({"message": "Item deleted"}), 200
    return jsonify({"error": "Item not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)