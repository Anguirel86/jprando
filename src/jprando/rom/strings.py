# Font definition for the Mr. DNA text box tileset
MR_DNA_FONT: dict[str, int] = {
    ' ': 0x105,
    'M': 0x188,
    'a': 0x189,
    'm': 0x18A,
    'l': 0x18B,
    's': 0x18C,
    ',': 0x18D,
    'u': 0x18E,
    'c': 0x18F,
    'h': 0x190,
    'o': 0x191,
    'r': 0x192,
    'g': 0x193,
    'n': 0x194,
    'd': 0x195,
    'i': 0x196,
    'v': 0x197,
    'e': 0x198,
    't': 0x199,
    'f': 0x19A,
    'b': 0x19B,
    'y': 0x19C,
    'x': 0x19D,
    '1': 0x19E,
    '4': 0x19F,
    '0': 0x1A0,
    '!': 0x1A1,
    'B': 0x1A2,
    '3': 0x1A3,
    '5': 0x1A4,
    '7': 0x1A5,
    'p': 0x1A6,
    'w': 0x1A7,
    'P': 0x1A8,
    '.': 0x1A9,
    'F': 0x1AA,
    'A': 0x1AB,
    'k': 0x1AC,
    'T': 0x1AD,
    'S': 0x1AE,
    'N': 0x1AF,
    'C': 0x1B0,
    '2': 0x1B1,
    'I': 0x1B2,
    'D': 0x1B3,
    '8': 0x1B4,
    'J': 0x1B5,
    '6': 0x1B6,
    'z': 0x1B7,
    'E': 0x1B8,
    'Q': 0x1B9,
    'W': 0x1BA,
    'R': 0x1BB,
    '9': 0x1BC,
    'j': 0x1BD,
    'H': 0x1BE,
}

def make_tilemap_entry(tile_index: int) -> int:
    """
    Combine a font tile index with its tile properties.
    Textbox font tiles use palette index 1 and high priority mode.
    """
    return tile_index | 0x2400

def encode_text(text: str, font: dict[str, int]) -> list[int]:
    """
    Encode a string using the specified font.
    """
    entries = []

    for char in text:
        if char not in font:
            char = char.lower()

        if char not in font:
            raise ValueError(
                f"Unsupported character: {char!r}"
            )

        entries.append(
            make_tilemap_entry(font[char])
        )

    return entries

def encode_tilemap_bytes(text: str, font: dict[str, int]) -> bytes:
    """
    Create the tilemap for the given string using the specified font.
    """
    entries = encode_text(text, font)

    # SNES tilemap entries are little-endian.
    return b''.join(
        entry.to_bytes(2, 'little')
        for entry in entries
    )
