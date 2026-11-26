import random
import unittest

from jprando.jpmap import jpmap
from jprando.jpmap.itemfill import AssumedItemFill


class ItemFillIntegrationTests(unittest.TestCase):

    def test_randomized_maps_are_completable(self):
        for seed in range(100):
            with self.subTest(seed=seed):
                rng = random.Random(seed)

                map_data = jpmap.get_default_map()

                jpmap.shuffle_map(map_data, rng)

                fill = AssumedItemFill()

                success = fill.place_items(
                    rng,
                    map_data
                )

                self.assertTrue(
                    success,
                    f"Item fill failed with seed {seed}"
                )

                self.assertTrue(
                    all(
                        reward is not None
                        for reward in map_data.treasure_map.values()
                    ),
                    f"Unfilled locations with seed {seed}"
                )

                self.assertTrue(
                    jpmap.validate_map(map_data),
                    f"Invalid map with seed {seed}"
                )


if __name__ == "__main__":
    unittest.main()
