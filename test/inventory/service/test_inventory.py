import pytest
from inventory.exception.exceptions import InvalidItemError, ItemNotFoundError
from inventory.service.inventory_service import Inventory, Item


@pytest.fixture
def sample_inventory():
    inv = Inventory()
    # seed with some items
    inv.upsert_item("A", price=10.0, qty=5)
    inv.upsert_item("B", price=20.0, qty=2)
    inv.upsert_item("C", price=15.0, qty=0)
    return inv


def test_upsert_and_get_item():
    inv = Inventory()
    inv.upsert_item("X", price=3.5, qty=10, metadata={"color": "red"})
    item = inv.get_item("X")
    assert isinstance(item, Item)
    assert item.price == pytest.approx(3.5)
    assert item.qty == 10
    assert item.metadata["color"] == "red"


def test_upsert_invalid():
    inv = Inventory()
    with pytest.raises(InvalidItemError):
        inv.upsert_item("bad", price=-1, qty=5)
    with pytest.raises(InvalidItemError):
        inv.upsert_item("bad", price=1, qty=-5)


def test_remove_item(sample_inventory):
    sample_inventory.remove_item("B")
    with pytest.raises(ItemNotFoundError):
        sample_inventory.get_item("B")


def test_remove_nonexistent():
    inv = Inventory()
    with pytest.raises(ItemNotFoundError):
        inv.remove_item("nope")


def test_range_query_quantity(sample_inventory):
    # prices: A=10(qty5), B=20(qty2), C=15(qty0)
    assert sample_inventory.range_query_quantity(10, 15) == 5  # A only
    assert sample_inventory.range_query_quantity(0, 100) == 7  # all qty


def test_range_query_value(sample_inventory):
    # A:10*5=50, B:20*2=40, C:15*0=0
    assert sample_inventory.range_query_value(10, 20) == pytest.approx(90)
    assert sample_inventory.range_query_value(12, 19) == pytest.approx(0)


def test_top_k_by_price(sample_inventory):
    top2 = sample_inventory.top_k_by_price(2)
    assert [item_id for item_id, _ in top2] == ["B", "C"]


def test_top_k_by_quantity(sample_inventory):
    top2 = sample_inventory.top_k_by_quantity(2)
    assert [item_id for item_id, _ in top2] == ["A", "B"]


def test_len_and_iter(sample_inventory):
    assert len(sample_inventory) == 3
    ids = {item_id for item_id, _ in sample_inventory}
    assert ids == {"A", "B", "C"}
