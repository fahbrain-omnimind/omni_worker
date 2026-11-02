"""Clean control file — no planted errors (false-positive control)."""


def clamp(value, low, high):
    return max(low, min(high, value))


def chunked(items, size):
    return [items[i : i + size] for i in range(0, len(items), size)]
