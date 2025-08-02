import pytest
import threading
from inventory.service.thread_safe_inventory_service import ThreadSafeInventoryService
from inventory.exception.exceptions import InvalidItemError, ItemNotFoundError
from inventory.models.inventory_items import Item


def test_upsert_and_get_item():
    inv = ThreadSafeInventoryService()
    inv.upsert_item("A", price=10.0, qty=5)
    item = inv.get_item("A")
    assert isinstance(item, Item)
    assert item.price == pytest.approx(10.0)
    assert item.qty == 5


def test_upsert_invalid():
    inv = ThreadSafeInventoryService()
    with pytest.raises(InvalidItemError):
        inv.upsert_item("X", price=-1.0, qty=1)
    with pytest.raises(InvalidItemError):
        inv.upsert_item("X", price=1.0, qty=-1)


def test_remove_item_and_get():
    inv = ThreadSafeInventoryService()
    inv.upsert_item("B", price=2.5, qty=3)
    inv.remove_item("B")
    with pytest.raises(ItemNotFoundError):
        inv.get_item("B")


def test_remove_nonexistent():
    inv = ThreadSafeInventoryService()
    with pytest.raises(ItemNotFoundError):
        inv.remove_item("Y")


def test_range_queries():
    inv = ThreadSafeInventoryService()
    inv.upsert_item("A", price=10.0, qty=5)
    inv.upsert_item("B", price=20.0, qty=2)
    inv.upsert_item("C", price=15.0, qty=3)
    # Quantity in [10,15] = 5 + 3 = 8
    assert inv.range_query_quantity(10, 15) == 8
    # Value in [10,20] = 10*5 + 15*3 + 20*2 = 50 + 45 + 40 = 135
    assert inv.range_query_value(10, 20) == pytest.approx(135)


def test_top_k_queries():
    inv = ThreadSafeInventoryService()
    inv.upsert_item("A", price=10.0, qty=5)
    inv.upsert_item("B", price=20.0, qty=2)
    inv.upsert_item("C", price=15.0, qty=3)
    top_price = inv.top_k_by_price(2)
    assert [item_id for item_id, _ in top_price] == ["B", "C"]
    top_qty = inv.top_k_by_quantity(2)
    assert [item_id for item_id, _ in top_qty] == ["A", "C"]


def test_len_and_iter():
    inv = ThreadSafeInventoryService()
    inv.upsert_item("A", price=1.0, qty=1)
    inv.upsert_item("B", price=2.0, qty=2)
    assert len(inv) == 2
    ids = {item_id for item_id, _ in inv}
    assert ids == {"A", "B"}


def test_thread_safety_concurrent_upserts_and_removals():
    inv = ThreadSafeInventoryService()
    def inserter(start, count):
        for i in range(start, start + count):
            inv.upsert_item(f"item{i}", price=float(i), qty=i)

    def remover(start, count):
        for i in range(start, start + count):
            try:
                inv.remove_item(f"item{i}")
            except ItemNotFoundError:
                pass

    threads = []
    # Launch inserters
    for offset in (0, 1000):
        t = threading.Thread(target=inserter, args=(offset, 1000))
        threads.append(t)
        t.start()
    # Launch removers
    for offset in (500, 1500):
        t = threading.Thread(target=remover, args=(offset, 1000))
        threads.append(t)
        t.start()
    # Wait for all
    for t in threads:
        t.join()

    # Validate consistency: no deadlock and inventory size within expected bounds
    size = len(inv)
    assert 0 <= size <= 2000
    # Check that every item in inventory matches its price index
    for item_id, item in inv:
        # get_item should not raise
        got = inv.get_item(item_id)
        assert got.price == item.price
        assert got.qty == item.qty
