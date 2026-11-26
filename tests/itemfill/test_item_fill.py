import random
import unittest
from collections import Counter

from jprando.jpmap import jpmap
from jprando.jpmap.entrancetypes import (
    Battery,
    IDCard,
    Item,
)
from jprando.jpmap.itemfill import AssumedItemFill


class AssumedItemFillTests(unittest.TestCase):

    def setUp(self):
        self.rng = random.Random(12345)
        self.map_data = jpmap.get_default_map()
        self.fill = AssumedItemFill()

    def test_successful_fill_populates_all_locations(self):
        success = self.fill.place_items(
            self.rng,
            self.map_data
        )

        self.assertTrue(success)

        self.assertTrue(
            all(
                reward is not None
                for reward in self.map_data.treasure_map.values()
            )
        )

    def test_all_progression_items_are_preserved(self):
        expected = Counter()
        expected.update(Battery)
        expected.update(IDCard)
        expected.update([Item.EGG] * 18)

        self.fill.place_items(
            self.rng,
            self.map_data
        )

        actual = Counter(
            self.map_data.treasure_map.values()
        )

        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
