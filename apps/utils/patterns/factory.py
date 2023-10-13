from __future__ import annotations

# Standard Library
from typing import Any, Optional


class ConfigurationFactory:
    _registry: dict

    def __init_subclass__(cls, configuration: Optional[Any] = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if configuration:
            cls._registry[configuration] = cls
        else:
            cls._registry = {}

    def __new__(cls, configuration: Optional[Any] = None, **kwargs):
        if configuration:
            subclass = cls._registry[configuration]
        else:
            subclass = cls
        return super().__new__(subclass)
