"""Narrow object cells from row dicts."""


def as_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(type(value).__name__)
    return value


def as_float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(type(value).__name__)
    return float(value)


def as_dict(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise TypeError(type(value).__name__)
    return {str(key): item for key, item in value.items()}
