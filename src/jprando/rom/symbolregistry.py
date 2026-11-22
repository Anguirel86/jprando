from dataclasses import dataclass
from enum import Enum, auto


class SymbolException(Exception):
    pass

class SymbolType(Enum):
    DATA = auto()
    PATCH = auto()
    ROUTINE = auto()
    TABLE = auto()
    TILESET = auto()
    TILEMAP = auto()

@dataclass
class SymbolMetadata:
    """
    Dataclass to hold metadata for a patch.
    """
    name: str
    addr: int  # ROM address of the patch (not CPU address)
    size: int
    type: SymbolType

class SymbolRegistry:
    """
    Allows the ROM manager to register symbol metadata by name for easy
    management and lookup. This could include newly created patch data
    as well as existing ROM routines we may want to reuse.
    """

    def __init__(self):
        self.symbols: dict[str, SymbolMetadata] = {}

    def register_symbol(self, name: str, addr: int, size: int):
        """
        Register a new symbol.

        Assumes addr and size are validated by the caller.

        NOTE: All symbols are registered PATCH type currently.
        """
        assert addr >= 0
        assert size > 0

        if name in self.symbols:
            raise SymbolException(f"Symbol {name} already exists")

        self.symbols[name] = SymbolMetadata(name, addr, size, SymbolType.PATCH)

    def get_symbol_data(self, name: str) -> SymbolMetadata | None:
        """
        Get the metadata for a symbol
        """
        return self.symbols.get(name, None)

    def has_symbol(self, name: str) -> bool:
        """
        Check if a symbol has been registered with the given name.
        """
        return name in self.symbols
