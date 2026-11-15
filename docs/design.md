# Design

| Route | Input | Output | CLI command |
|---|---|---|---|
| GET /inventory | none | list of all items | list |
| GET /inventory/<id> | id in URL | one item, or 404 | view |
| POST /inventory | JSON: product_name, price, stock | new item (201) | add |
| PATCH /inventory/<id> | JSON: fields to change | updated item | update |
| DELETE /inventory/<id> | id in URL | confirmation message | delete |
| GET /lookup | ?barcode= or ?name= | product from OpenFoodFacts | find |

## Example item in the mock database

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