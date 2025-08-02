from typing import Dict, Any


class Item:
    __slots__ = ("price", "qty", "metadata")

    def __init__(self, price: float, qty: int, metadata: Dict[str, Any] = None):
        self.price = price
        self.qty = qty
        self.metadata = metadata or {}
