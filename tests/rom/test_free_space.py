import unittest

from jprando.rom.freespace import FreeSpaceException, FreeSpaceManager


class FreeSpaceManagerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.manager = FreeSpaceManager()

    def test_initial_state_has_no_free_blocks(self) -> None:
        """
        A newly created manager has no free blocks.
        """
        self.assertEqual(len(self.manager.free_blocks), 0)

    def test_is_free_returns_false_before_any_marks(self) -> None:
        """
        Before marking any space, is_free should always return False.
        """
        self.assertFalse(self.manager.is_free(0x12345, 0x10))

    def test_reserve_raises_when_no_free_space(self) -> None:
        """
        Reserve should raise FreeSpaceException when there are no free blocks.
        """
        with self.assertRaises(FreeSpaceException):
            self.manager.reserve(0x10)

    def test_mark_and_is_free_works(self) -> None:
        """
        Marking a block makes is_free return True for addresses inside it.
        """
        start = 0x20000
        end = 0x27FFF
        self.manager.mark_free(start, end)

        self.assertTrue(self.manager.is_free(0x21000, 0x7000))
        self.assertFalse(self.manager.is_free(0x1FFFF, 0x1000))
        self.assertFalse(self.manager.is_free(0x27FFF, 0x1000))

    def test_mark_raises_when_block_too_large(self) -> None:
        """
        Trying to mark more than a full bank size will raise an exception
        """
        with self.assertRaises(FreeSpaceException):
            self.manager.mark_free(0x20000, 0x28000)

    def test_reserve_shrinks_block_and_returns_address(self) -> None:
        """
        Reserve should return the start address of a free block and shrink it.
        """
        self.manager.mark_free(0x20000, 0x27FFF)

        addr = self.manager.reserve(0x1000)
        self.assertEqual(addr, 0x20000)
        block = self.manager.free_blocks[0]
        self.assertEqual(block.start, 0x21000)
        self.assertEqual(block.end, 0x27FFF)

    def test_reserve_removes_block_when_fully_consumed(self) -> None:
        """
        When a block is fully consumed by a reserve request, it should be removed.
        """
        self.manager.mark_free(0x20000, 0x27FFF)

        addr = self.manager.reserve(0x8000)  # exactly the whole block
        self.assertEqual(addr, 0x20000)
        self.assertEqual(len(self.manager.free_blocks), 0)

    def test_reserve_raises_when_block_too_small(self) -> None:
        """
        Reserve should raise when no free block is large enough.
        """
        self.manager.mark_free(0x20000, 0x27FFF)

        with self.assertRaises(FreeSpaceException):
            self.manager.reserve(0x10000)  # larger than the block

    def test_multiple_blocks_and_reserve_order(self) -> None:
        """
        With multiple free blocks, reserve should pick the first one that fits.
        """
        self.manager.mark_free(0x20000, 0x27FFF)
        self.manager.mark_free(0x40000, 0x47FFF)

        addr1 = self.manager.reserve(0x7000)
        self.assertEqual(addr1, 0x20000)  # first block fits
        block1 = self.manager.free_blocks[0]
        self.assertEqual(block1.start, 0x27000)

        addr2 = self.manager.reserve(0x7000)
        self.assertEqual(addr2, 0x40000)  # second block now used
        block2 = self.manager.free_blocks[1]
        self.assertEqual(block2.start, 0x47000)

    def test_is_free_with_zero_size_at_boundary(self) -> None:
        """
        Reserve with 0 size should fail with a FreeSpaceException
        """
        self.manager.mark_free(0x20000, 0x27FFF)

        # Exact start address with zero size
        with self.assertRaises(FreeSpaceException):
            self.manager.is_free(0x20000, 0)
        # 0 size requests raise a FreeSpaceException
        with self.assertRaises(FreeSpaceException):
            self.manager.is_free(0x1FFFF, 0)
        # Exact end address (which is outside) should not be free
        with self.assertRaises(FreeSpaceException):
            self.manager.is_free(0x27FFF, 0)

    def test_reserve_exactly_remaining_space_succeeds(self) -> None:
        """
        Reserve with a size equal to the remaining space in a block succeeds.
        """
        self.manager.mark_free(0x20000, 0x27FFF)

        addr = self.manager.reserve(0x8000)
        self.assertEqual(addr, 0x20000)
        # All space is reserved, block has been removed
        self.assertEqual(len(self.manager.free_blocks), 0)

    def test_reserve_one_byte_too_large_raises(self) -> None:
        """
        Reserve one byte larger than available should raise.
        """
        self.manager.mark_free(0x20000, 0x27FFF)

        with self.assertRaises(FreeSpaceException):
            self.manager.reserve(0x8001)  # one more than the block size

    def test_marking_overlapping_ranges_raises_exception(self) -> None:
        """
        Marking overlapping ranges should throw an exception
        """
        self.manager.mark_free(0x20000, 0x27FFF)

        with self.assertRaises(FreeSpaceException):
            self.manager.mark_free(0x25000, 0x40000)  # overlaps the first block

    def test_marking_adjacent_ranges_creates_separate_blocks(self) -> None:
        """
        Marking adjacent ranges should not merge them; they remain separate.
        """
        self.manager.mark_free(0x20000, 0x27FFF)
        self.manager.mark_free(0x28000, 0x2FFFF)  # exactly adjacent

        self.assertEqual(len(self.manager.free_blocks), 2)
        self.assertEqual(self.manager.free_blocks[0].start, 0x20000)
        self.assertEqual(self.manager.free_blocks[1].start, 0x28000)


    def test_block_resizing(self) -> None:
        """
        Test block resizing under various reserve conditions
        """
        self.manager.mark_free(0x20000, 0x27FFF)
        block = self.manager.free_blocks[0]

        _ = self.manager.reserve(0x1000, 0x20000)  # addr = block start
        self.assertEqual(block.start, 0x21000)

        _ = self.manager.reserve(0x1000, 0x27000) # reserved end == block end
        self.assertEqual(block.end, 0x26FFF)

        # Reserved block falls in the middle, split the block in 2
        _ = self.manager.reserve(0x1000, 0x24000)
        self.assertEqual(len(self.manager.free_blocks), 2)
        block1 = self.manager.free_blocks[0]
        block2 = self.manager.free_blocks[1]
        self.assertEqual(block1.start, 0x21000)
        self.assertEqual(block1.end, 0x23FFF)
        self.assertEqual(block2.start, 0x25000)
        self.assertEqual(block2.end, 0x26FFF)
