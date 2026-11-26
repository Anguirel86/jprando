import unittest

from jprando.jpmap import jpmap
from jprando.jpmap.entrancetypes import Location


class AllLocationsExistTest(unittest.TestCase):

    def test_all_locations_exist(self):

        map_data = jpmap.get_default_map()
        locs = list(map_data.treasure_map.keys())

        for loc in list(Location):
            locs.remove(loc)

        self.assertTrue(
            len(locs) == 0,
            f"Unplaced locations: {locs}"
        )

if __name__ == "__main__":
    unittest.main()
