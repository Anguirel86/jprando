from dataclasses import dataclass


@dataclass
class FSBlock:
    """
    Represents a block of free space in the JP ROM
    """
    start: int
    end: int

    def contains_addr(self, addr: int) -> bool:
        return self.start <= addr <= self.end

    def contains(self, start: int, end: int) -> bool:
        return start <= end and self.contains_addr(start) and self.contains_addr(end)

    def get_size(self) -> int:
        return self.end - self.start + 1

    def __lt__(self, other) -> bool:
        return self.start < other.start

class FreeSpaceException(Exception):
    pass

class FreeSpaceManager:
    """
    Manage free space in the JP ROM.
    """

    # Max block size is equal to a full 32kb bank
    MAX_BLOCK_SIZE = 0x8000

    def __init__(self):
        # NOTE: This list could be replaced with some type of sorted/balanced tree
        #       to speed up free space operations, but that is probably overkill
        #       for this project currently.
        self.free_blocks: list[FSBlock] = []

    def mark_free(self, start: int, end: int):
        """
        Mark the specified bytes as free space starting at the given address (end inclusive)
        """
        # Make sure the start/end values make sense
        if start < 0 or end < 0:
            raise FreeSpaceException(f"Start ({hex(start)}) and end ({hex(end)}) cannot be negative")

        if end < start:
            raise FreeSpaceException(f"End ({hex(end)}) cannot be before start ({hex(start)})")

        # Verify the new space does not exceed the max block size
        if (end - start + 1) > self.MAX_BLOCK_SIZE:
            raise FreeSpaceException(f"Invalid block size. start={hex(start)}. Max={hex(self.MAX_BLOCK_SIZE)}")

        # Ensure this range doesn't overlap any existing block
        for block in self.free_blocks:
            if block.contains_addr(start) or block.contains_addr(end) or (block.start > start and block.end < end):
                raise FreeSpaceException(
                    f"Marked range [{hex(start)}, {hex(end)})"
                    f" overlaps existing free space at [{hex(block.start)}, {hex(block.end)})")

        self.free_blocks.append(FSBlock(start, end))
        self.free_blocks.sort()

    def is_free(self, addr: int, size: int) -> bool:
        """
        Check if the the requested block is free.
        """
        if size <= 0:
            raise FreeSpaceException(f"Invalid size: {size}")

        if addr < 0:
            raise FreeSpaceException(f"Invalid address: {addr}")

        for block in self.free_blocks:
            if block.contains(addr, (addr + size - 1)):
                return True

        return False

    def reserve(self, size: int, addr: int | None = None) -> int:
        """
        Reserve the requested number of bytes anywhere in the ROM and
        return the address.

        Optional address can be supplied to force a specific reserved address.
        """
        if size <= 0:
            temp = hex(addr) if addr is not None else None
            raise FreeSpaceException(f"Invalid reserve request size ({hex(size)}) at address {temp}")

        if addr is not None and addr < 0:
            raise FreeSpaceException(f"Invalid address {hex(addr)}")

        for block in self.free_blocks:
            if addr is not None and not block.contains_addr(addr):
                continue

            start = block.start if addr is None else addr
            if block.get_size() >= size and block.contains(start, start + size - 1):
                # Found a free block for this reserve request
                self._resize_block(block, start, size)
                return start

        # If we got here, no free blocks wre found for this request
        raise FreeSpaceException(f"No free space blocks available for requested size ({hex(size)})")

    def _resize_block(self, block: FSBlock, addr: int, size: int):
        """
        Handle resizing a block after space has been reserved

        Assumes block is valid and both addr and size args are positive and part of the block
        """
        end = addr + size - 1

        assert size > 0
        assert block.contains(addr, end)

        if size == block.get_size():
            self.free_blocks.remove(block)
        elif addr == block.start:
            block.start += size
        elif end == block.end:
            block.end -= size
        else:
            # The block is being split in 2
            block1 = FSBlock(block.start, addr -1)
            block2 = FSBlock(end + 1, block.end)
            self.free_blocks.extend([block1, block2])
            self.free_blocks.remove(block)
            self.free_blocks.sort()
