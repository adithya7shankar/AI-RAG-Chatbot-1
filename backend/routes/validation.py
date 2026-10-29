from flask import request


def required_text(field):
    """Return a nonempty text field, or None for an invalid request body."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None
    value = data.get(field)
    return value.strip() if isinstance(value, str) and value.strip() else None
