# Dynamic ThreadSafeInventoryService Management

A lightweight, in-memory Python package for real-time inventory management, supporting core operations like insertion, deletion, retrieval, range queries, and top‑K queries by price or quantity.

## Features

* **Upsert** items (insert or update) in O(1)
* **Remove** items with custom error handling
* **Retrieve** individual item records
* **Range Queries**:

  * Total quantity within a price range
  * Total value (price×quantity) within a price range
* **Top‑K Queries**:

  * Highest-priced items
  * Highest-quantity items
* Pythonic interfaces: **iteration** and **len()** support

## Project Structure

```
Project-Dynamic-ThreadSafeInventoryService-Management/
├── inventory/                  # Core package
│   ├── exception/              # Custom exception classes
│   │   └── __init__.py
│   ├── service/                # Service layer and data structures
│   │   ├── __init__.py
│   │   └── inventory.py        # ThreadSafeInventoryService and Item implementations
│   ├── __init__.py
│   └── demo.py                 # CLI/demo script
├── test/                       # Test suite
│   └── inventory/
│       └── service/
│           ├── __init__.py
│           └── test_inventory.py  # pytest tests
├── README.md                   # Project overview and usage
```

> The core library relies only on built-in Python modules (`dict`, `heapq`, etc.) and has no external dependencies by default.

## Usage

### Demo Script

Run the demo to see the inventory operations in action:

```bash
python -m inventory.demo
```

Expected output:

```
Current inventory:
 - apple: price=$1.25, qty=100
 - banana: price=$0.75, qty=150
 - carrot: price=$0.50, qty=200

Total qty in price range $0.6–$1.5: 250
Total value in range $0.6–$1.5: 237.5

Top 2 by price:
  apple ($1.25)
  banana ($0.75)

Top 2 by quantity:
  carrot (qty=200)
  banana (qty=150)

Expected error: Item 'nonexistent' not found.
```


## Testing

### Unit Test
Run the pytest suite to validate functionality and edge cases:

```bash
pytest 

collected 17 items                                                                                                                                                                  

test/inventory/service/test_inventory_service.py .........                                                                                                                    [ 52%]
test/inventory/service/test_thread_safe_inventory_service.py ........                                                                                                         [100%]

================================================================================ 17 passed in 0.04s =================================================================================
```

All tests cover insertion, deletion, range queries, top‑K retrievals, and error scenarios.

### Performance Test

```bash
python -m inventory.performance_test_comparisons

----------------------- Old Inventory Service Performance Benchmark --------------------------
Original ThreadSafeInventoryService Performance Test
Parameters: 100000 items, 1000 range queries, top-50 x 50 repeats

Upsert: 0.1531 seconds for 100000 items
Range Queries: 11.3060 seconds for 1000 queries
Top-K Queries: 0.9022 seconds for top-50 x 50
----------------------- New Inventory Service Performance Benchmark--------------------------
Original ThreadSafeInventoryService Performance Test
Parameters: 100000 items, 1000 range queries, top-50 x 50 repeats

Upsert: 0.1329 seconds for 100000 items
Range Queries: 8.8341 seconds for 1000 queries
Top-K Queries: 0.0000 seconds for top-50 x 50
```
