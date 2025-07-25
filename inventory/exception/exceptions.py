class InventoryError(Exception):
    """Base exception for inventory errors."""


class ItemNotFoundError(InventoryError):
    """Raised when attempting to access or remove a non-existent item."""


class InvalidItemError(InventoryError):
    """Raised when provided item data is invalid (e.g., negative price or quantity)."""
