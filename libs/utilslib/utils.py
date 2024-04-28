from typing import TypeVar, Any

VT = TypeVar("VT")


def getDictV(inDict: dict, key: Any, default: VT) -> VT:
    if key is None:
        raise KeyError("Key is None")

    v = inDict.get(key, default)

    if isinstance(v, type(default)):
        return v

    raise TypeError(
        f"Expected type '{type(default)}' for key '{key}', received value '{v}' with type '{type(v)}'"
    )
