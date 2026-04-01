# --- Domain-level errors (so routers can translate to HTTP codes later) ---

class DuplicateNameError(Exception):
    """Raised when attempting to create/update a card with a duplicate name (unique violation)."""


class NotFoundError(Exception):
    """Raised when a card is not found for a given identifier."""