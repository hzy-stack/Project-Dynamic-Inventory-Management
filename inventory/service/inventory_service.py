from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple, Iterator
import heapq

from inventory.exception.exceptions import InvalidItemError, ItemNotFoundError


@dataclass
class Item:
    price: float
    qty: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class Inventory:
    """
    Dynamic inventory supporting:
      - upsert (insert/update)
      - deletion
      - retrieval (get)
      - range queries (quantity and value)
      - top-k queries (by price and quantity)
      - traversal
    """

    def __init__(self) -> None:
        # Internal storage: item_id -> Item
        self._items: Dict[str, Item] = {}

    def upsert_item(
        self,
        item_id: str,
        price: float,
        qty: int,
        metadata: Dict[str, Any] = None,
    ) -> None:
        """
        Add a new item or update an existing one.

        Args:
            item_id: Unique identifier for the item.
            price: Non-negative price of the item.
            qty: Non-negative quantity of the item.
            metadata: Optional dictionary of extra attributes.

        Raises:
            InvalidItemError: If price or qty is negative.
        """
        if price < 0 or qty < 0:
            raise InvalidItemError("Price and quantity must be non-negative.")
        if metadata is None:
            metadata = {}
        self._items[item_id] = Item(price=price, qty=qty, metadata=metadata)

    def remove_item(self, item_id: str) -> None:
        """
        Remove an item from the inventory.

        Args:
            item_id: Identifier of the item to remove.

        Raises:
            ItemNotFoundError: If the item does not exist.
        """
        try:
            del self._items[item_id]
        except KeyError:
            raise ItemNotFoundError(f"Item '{item_id}' not found.")

    def get_item(self, item_id: str) -> Item:
        """
        Retrieve a single item.

        Args:
            item_id: Identifier of the item.

        Returns:
            The Item object associated with item_id.

        Raises:
            ItemNotFoundError: If the item does not exist.
        """
        try:
            return self._items[item_id]
        except KeyError:
            raise ItemNotFoundError(f"Item '{item_id}' not found.")

    def range_query_quantity(self, low: float, high: float) -> int:
        """
        Sum of quantities for items with price in [low, high].

        Args:
            low: Lower bound of price range.
            high: Upper bound of price range.

        Returns:
            Total quantity of matching items.
        """
        return sum(item.qty for item in self._items.values() if low <= item.price <= high)

    def range_query_value(self, low: float, high: float) -> float:
        """
        Sum of (price * quantity) for items with price in [low, high].

        Args:
            low: Lower bound of price range.
            high: Upper bound of price range.

        Returns:
            Total inventory value of matching items.
        """
        return sum(item.price * item.qty for item in self._items.values() if low <= item.price <= high)

    def top_k_by_price(self, k: int) -> List[Tuple[str, Item]]:
        """
        Retrieve the top-k items sorted by price (descending).

        Args:
            k: Number of items to retrieve.

        Returns:
            List of (item_id, Item) tuples.
        """
        return heapq.nlargest(k, self._items.items(), key=lambda kv: kv[1].price)

    def top_k_by_quantity(self, k: int) -> List[Tuple[str, Item]]:
        """
        Retrieve the top-k items sorted by quantity (descending).

        Args:
            k: Number of items to retrieve.

        Returns:
            List of (item_id, Item) tuples.
        """
        return heapq.nlargest(k, self._items.items(), key=lambda kv: kv[1].qty)

    def __len__(self) -> int:
        """Return the number of distinct items in the inventory."""
        return len(self._items)

    def __iter__(self) -> Iterator[Tuple[str, Item]]:
        """Iterate over (item_id, Item) pairs in the inventory."""
        return iter(self._items.items())
