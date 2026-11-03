import hashlib
import io
from dataclasses import dataclass


@dataclass
class FSBlock:
    """
    Represents a block of free space in the JP ROM
    """
    start: int
    end: int

class FreeSpaceException(Exception):
    pass

class JPRomException(Exception):
    pass

class FreeSpaceManager:
    """
    Manage free space in the JP ROM.
    """

    def __init__(self):
        # NOTE: This list could be replaced with some type of sorted/balanced tree
        #       to speed up free space operations, but that is probably overkill
        #       for this project currently.
        self.free_blocks: list[FSBlock] = []

    def mark_free(self, start: int, end: int):
        """
        Mark the specified bytes as free space starting at the given address
        """
        # TODO: Check if this is part of an existing block and
        #       try to combine them (respecting bank boundaries)
        self.free_blocks.append(FSBlock(start, end))

    def reserve(self, size: int) -> int:
        """
        Reserve the requested number of bytes anywhere in the ROM and
        return the address.
        """
        found_block = None
        for block in self.free_blocks:
            if (block.end - block.start) >= size:
                # Found a free block for this reserve request
                found_block = block
                break

        if found_block is None:
            raise FreeSpaceException(f"No free space blocks available for requested size ({size})")

        addr = found_block.start

        # Reduce the size of the block and remove it if it's used up
        found_block.start += size
        if found_block.start == found_block.end:
            self.free_blocks.remove(found_block)

        return addr

class JPRom:
    """
    Class to manage the Jurassic Park ROM data.
    """

    JPUSA_MD5_HASH = "bb9c2f667ced16a2e605b385c041c744"

    # Expanded ROM size (3MB)
    _ROM_SIZE = 0x30_0000

    def __init__(self, rom: bytes | str):
        if isinstance(rom, str):
            with open(rom, "rb") as file:
                self._rom_buf = io.BytesIO(file.read())
        elif isinstance(rom, bytes):
            self._rom_buf = io.BytesIO(rom)
        else:
            raise JPRomException("Invalid ROM source")

        rommd5 = hashlib.md5()
        rommd5.update(self._rom_buf.getbuffer())

        if rommd5.hexdigest() != self.JPUSA_MD5_HASH:
            raise JPRomException("Invalid hash. Please use a Jurassic Park USA ROM")

        self.free_space_manager = FreeSpaceManager()
        self._expand_rom()

    def _expand_rom(self):
        """
        Expand the Jurassic Park ROM data to 3MB
        and update the SNES headers appropriately.
        """

        # Update ROM max size from 2MB to 4MB
        self._rom_buf.seek(0x7FD7)
        self._rom_buf.write(bytes([0x0C]))

        # Update with a temp checksum
        self._rom_buf.seek(0x7FDC)
        self._rom_buf.write(bytes([0x00, 0x00, 0xFF, 0xFF]))

        # Expand the ROM to 3MB
        # Could go to 4MB, but 1MB should be mnore than enough space
        self._rom_buf.seek(0, io.SEEK_END)
        self._rom_buf.write(bytes([0] * 0x10_0000))

        # Mark the newly created space as free space
        self._init_free_space()

    def _init_free_space(self):
        """
        Set the initial free space for the expanded ROM.
        """
        # The ROM was expanded from 2MB to 3MB, this leave 20 banks of 32k bytes
        # as newly minted free space.
        start = 0x20_0000
        bank_size = 0x8000
        for addr in range(start, self._ROM_SIZE, bank_size):
            self.free_space_manager.mark_free(addr, addr + bank_size - 1)

    @staticmethod
    def to_cpu_addr(rom_addr: int) -> int:
        """
        Convert a ROM address to a CPU address for branches/jumps

        Jurassic Park is a LoROM game, meaning it only uses 32k of each bank,
        specifically, the upper half (0x8000-0xFFFF)
        Program memory is mapped starting at 0x80_0000
        """
        # Divide by 32k to get the bank offset
        bank = 0x80 + (rom_addr >> 15)

        # shift remaining addr into upper half of the bank
        addr = 0x8000 + (rom_addr & 0x7FFF)

        # Combine the bank and address
        return (bank << 16) | addr

    def write(self, addr: int, data: bytes):
        """
        Write the given data starting at the given address.
        """
        end = addr + len(data) - 1
        if end >= self._ROM_SIZE:
            raise JPRomException(f"Attempt to write beyond the ROM bounds: {end}")

        self._rom_buf.seek(addr)
        self._rom_buf.write(data)

    def write_patch_with_padding(self, addr: int, end_addr: int, data: bytes):
        """
        Write to the ROM and pad out any extra bytes with NOP instructions.
        """
        total_bytes = end_addr - addr
        if total_bytes < len(data):
            raise JPRomException("Data overlaps end address")

        self.write(addr, data)
        pad_bytes = total_bytes - len(data)
        # TODO: This could be smarter for big gaps with a jump or branch
        #       instead of a long string of NOPs.
        nops = bytes([0xEA] * pad_bytes)
        self._rom_buf.seek(addr + len(data))
        self._rom_buf.write(nops)

    def reserve(self, requested_size: int) -> int:
        """
        Get the next free address to store data to the ROM.
        This is a ROM (file) address, not a CPU address.
        Requested_size is the size of the requested free space in bytes.
        The requested space will be reserved.
        """
        return self.free_space_manager.reserve(requested_size)

    def get_buffer(self) -> memoryview:
        """
        Return the raw bytes buffer of this ROM.
        """
        return self._rom_buf.getbuffer()

    def write_to_file(self, file_name: str):
        """
        Update the SNES header checksum and write the ROM to file
        """
        # Calculate the ROM checksum and complement and write them
        # to the SNES header.
        checksum = sum(self._rom_buf.getbuffer()) & 0xFFFF
        complement = checksum ^ 0xFFFF

        self.write(0x7FDE, checksum.to_bytes(
            2, byteorder="little", signed=False))
        self.write(0x7FDC, complement.to_bytes(
            2, byteorder="little", signed=False))

        # Write file
        with open(file_name, 'wb') as f:
            f.write(self._rom_buf.getbuffer())
