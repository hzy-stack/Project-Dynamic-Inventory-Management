import bisect
from threading import RLock
from functools import lru_cache
from inventory.exception.exceptions import InvalidItemError, ItemNotFoundError
from inventory.models.inventory_items import Item


class ThreadSafeInventoryService:
    """Thread-safe, in-memory inventory with bisect-based indexes."""
    __slots__ = ('_lock', '_items', '_price_index', '_quantity_index')

    def __init__(self):
        self._lock = RLock()
        self._items: dict[str, Item] = {}
        # Sorted lists of (price, item_id) and (qty, item_id)
        self._price_index: list[tuple[float, str]] = []
        self._quantity_index: list[tuple[int, str]] = []

    def upsert_item(
        self,
        item_id: str,
        price: float,
        qty: int,
        metadata: dict = None
    ):
        """
        Insert or update an item. Maintains sorted indices in O(log n).
        """
        if price < 0 or qty < 0:
            raise InvalidItemError("Price and quantity must be non-negative.")

        with self._lock:
            old = self._items.get(item_id)
            if old:
                # remove old price index
                key = (old.price, item_id)
                idx = bisect.bisect_left(self._price_index, key)
                if idx < len(self._price_index) and self._price_index[idx] == key:
                    self._price_index.pop(idx)
                # remove old quantity index
                key_q = (old.qty, item_id)
                idx_q = bisect.bisect_left(self._quantity_index, key_q)
                if idx_q < len(self._quantity_index) and self._quantity_index[idx_q] == key_q:
                    self._quantity_index.pop(idx_q)

            # update storage
            self._items[item_id] = Item(price, qty, metadata or {})
            # insert into price index
            bisect.insort(self._price_index, (price, item_id))
            # insert into quantity index
            bisect.insort(self._quantity_index, (qty, item_id))

            # clear caches after mutation
            self._clear_caches()

    def remove_item(self, item_id: str):  # -> None
        """
        Remove an item and update indices.
        """
        with self._lock:
            item = self._items.pop(item_id, None)
            if item is None:
                raise ItemNotFoundError(f"Item '{item_id}' not found.")
            # remove from price index
            key = (item.price, item_id)
            idx = bisect.bisect_left(self._price_index, key)
            if idx < len(self._price_index) and self._price_index[idx] == key:
                self._price_index.pop(idx)
            # remove from quantity index
            key_q = (item.qty, item_id)
            idx_q = bisect.bisect_left(self._quantity_index, key_q)
            if idx_q < len(self._quantity_index) and self._quantity_index[idx_q] == key_q:
                self._quantity_index.pop(idx_q)

            self._clear_caches()

    def get_item(self, item_id: str) -> Item:
        """
        Retrieve an item by id.
        """
        with self._lock:
            try:
                return self._items[item_id]
            except KeyError:
                raise ItemNotFoundError(f"Item '{item_id}' not found.")

    @lru_cache(maxsize=128)
    def range_query_quantity(self, low: float, high: float) -> int:
        """
        Sum quantities for items with price in [low, high] in O(log n + k).
        """
        with self._lock:
            left = bisect.bisect_left(self._price_index, (low, ""))
            right = bisect.bisect_right(self._price_index, (high, chr(0x10ffff)))
            total = 0
            for _, item_id in self._price_index[left:right]:
                total += self._items[item_id].qty
            return total

    @lru_cache(maxsize=128)
    def range_query_value(self, low: float, high: float) -> float:
        """
        Sum price*qty for items with price in [low, high] in O(log n + k).
        """
        with self._lock:
            left = bisect.bisect_left(self._price_index, (low, ""))
            right = bisect.bisect_right(self._price_index, (high, chr(0x10ffff)))
            total = 0.0
            for _, item_id in self._price_index[left:right]:
                itm = self._items[item_id]
                total += itm.price * itm.qty
            return total

    @lru_cache(maxsize=64)
    def top_k_by_price(self, k: int) -> list[tuple[str, Item]]:
        """
        Retrieve top-K items by price in O(k).
        """
        with self._lock:
            # last k entries are highest prices
            slice_k = self._price_index[-k:]
            return [(item_id, self._items[item_id]) for _, item_id in reversed(slice_k)]

    @lru_cache(maxsize=64)
    def top_k_by_quantity(self, k: int) -> list[tuple[str, Item]]:
        """
        Retrieve top-K items by quantity in O(k).
        """
        with self._lock:
            slice_k = self._quantity_index[-k:]
            return [(item_id, self._items[item_id]) for _, item_id in reversed(slice_k)]

    def __len__(self) -> int:
        with self._lock:
            return len(self._items)

    def __iter__(self):
        with self._lock:
            # snapshot to avoid race conditions
            return iter(list(self._items.items()))

    def _clear_caches(self):
        self.range_query_quantity.cache_clear()
        self.range_query_value.cache_clear()
        self.top_k_by_price.cache_clear()
        self.top_k_by_quantity.cache_clear()
