from inventory.exception.exceptions import ItemNotFoundError
from inventory.service.inventory_service import Inventory


def main():
    inv = Inventory()

    # 1. Upsert a few items
    inv.upsert_item("apple", price=1.25, qty=100, metadata={"category": "fruit"})
    inv.upsert_item("banana", price=0.75, qty=150)
    inv.upsert_item("carrot", price=0.50, qty=200)

    # 2. Show all items
    print("Current inventory:")
    for item_id, item in inv:
        print(f" - {item_id}: price=${item.price}, qty={item.qty}")

    # 3. Range queries
    low, high = 0.6, 1.5
    print(f"\nTotal qty in price range ${low}–${high}:",
          inv.range_query_quantity(low, high))
    print(f"Total value in range ${low}–${high}:",
          inv.range_query_value(low, high))

    # 4. Top‑k
    print("\nTop 2 by price:")
    for item_id, item in inv.top_k_by_price(2):
        print(f"  {item_id} (${item.price})")

    print("\nTop 2 by quantity:")
    for item_id, item in inv.top_k_by_quantity(2):
        print(f"  {item_id} (qty={item.qty})")

    # 5. Error handling demo
    try:
        inv.remove_item("nonexistent")
    except ItemNotFoundError as e:
        print(f"\nExpected error: {e}")

if __name__ == "__main__":
    main()
