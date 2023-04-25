from typing import Optional


def make_error(message: str, code: Optional[str] = "error") -> dict[str, any]:
    data = dict(error=dict(message=message, code=code))
    return data
