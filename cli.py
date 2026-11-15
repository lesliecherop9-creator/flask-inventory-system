import argparse
import requests

BASE_URL = "http://127.0.0.1:5000"


def call_api(method, path, **kwargs):
    try:
        response = requests.request(method, BASE_URL + path, timeout=15, **kwargs)
    except requests.exceptions.RequestException:
        print("Error: could not reach the API. Is the Flask server running?")
        return None

    try:
        data = response.json()
    except ValueError:
        print("Error: the server sent an unexpected answer (status", response.status_code, ")")
        return None

    if response.status_code >= 400:
        print("Error:", data.get("error", "Something went wrong"))
        return None
    return data


def print_item(item):
    print(f"[{item['id']}] {item['product_name']} ({item['brands']})")
    print(f"     Price: {item['price']}  Stock: {item['stock']}")


def list_items(args):
    items = call_api("GET", "/inventory")
    if items is None:
        return
    for item in items:
        print_item(item)


def view_item(args):
    item = call_api("GET", f"/inventory/{args.id}")
    if item is None:
        return
    print_item(item)
    print("     Barcode:", item["barcode"])
    print("     Ingredients:", item["ingredients_text"])


def add_item(args):
    body = {
        "product_name": args.name,
        "brands": args.brand,
        "price": args.price,
        "stock": args.stock,
    }
    item = call_api("POST", "/inventory", json=body)
    if item is not None:
        print("Added:")
        print_item(item)


def update_item(args):
    body = {}
    if args.price is not None:
        body["price"] = args.price
    if args.stock is not None:
        body["stock"] = args.stock
    if not body:
        print("Error: give --price and/or --stock")
        return
    item = call_api("PATCH", f"/inventory/{args.id}", json=body)
    if item is not None:
        print("Updated:")
        print_item(item)


def delete_item(args):
    result = call_api("DELETE", f"/inventory/{args.id}")
    if result is not None:
        print(result["message"])


def find_on_api(args):
    if args.barcode:
        params = {"barcode": args.barcode}
    elif args.name:
        params = {"name": args.name}
    else:
        print("Error: give --barcode or --name")
        return
    product = call_api("GET", "/lookup", params=params)
    if product is not None:
        print(product["product_name"], "-", product["brands"])
        print("Barcode:", product["barcode"])
        print("Ingredients:", product["ingredients_text"])


def import_item(args):
    body = {"barcode": args.barcode, "price": args.price, "stock": args.stock}
    item = call_api("POST", "/inventory/import", json=body)
    if item is not None:
        print("Imported:")
        print_item(item)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Inventory CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list", help="show all items")
    p.set_defaults(func=list_items)

    p = sub.add_parser("view", help="show one item")
    p.add_argument("id", type=int)
    p.set_defaults(func=view_item)

    p = sub.add_parser("add", help="add a new item")
    p.add_argument("name")
    p.add_argument("--brand", default="")
    p.add_argument("--price", type=float, default=0)
    p.add_argument("--stock", type=int, default=0)
    p.set_defaults(func=add_item)

    p = sub.add_parser("update", help="change price or stock")
    p.add_argument("id", type=int)
    p.add_argument("--price", type=float)
    p.add_argument("--stock", type=int)
    p.set_defaults(func=update_item)

    p = sub.add_parser("delete", help="remove an item")
    p.add_argument("id", type=int)
    p.set_defaults(func=delete_item)

    p = sub.add_parser("find", help="search OpenFoodFacts")
    p.add_argument("--barcode")
    p.add_argument("--name")
    p.set_defaults(func=find_on_api)

    p = sub.add_parser("import", help="add a product from OpenFoodFacts by barcode")
    p.add_argument("barcode")
    p.add_argument("--price", type=float, default=0)
    p.add_argument("--stock", type=int, default=0)
    p.set_defaults(func=import_item)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()