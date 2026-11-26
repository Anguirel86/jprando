import unittest
from collections import Counter

from jprando.jpmap import jpmap
from jprando.jpmap.entrancetypes import Battery, Event, IDCard


class AccessRuleTests(unittest.TestCase):

    def test_access_rules(self):
        rules = [
            [Battery.SHIP, Event.DESTROY_RAPTOR_NEST],
            [IDCard.JOHN_HAMMOND],
        ]

        test_cases = [
            ([], False),
            ([Battery.SHIP], False),
            ([Battery.SHIP, Event.DESTROY_RAPTOR_NEST], True),
            ([IDCard.JOHN_HAMMOND], True),
        ]

        for inventory, expected in test_cases:
            with self.subTest(inventory=inventory):
                self.assertEqual(
                    jpmap._can_access(rules, Counter(inventory)),
                    expected
                )

    def test_empty_rules_allow_access(self):
        self.assertTrue(jpmap._can_access(None, Counter()))
        self.assertTrue(jpmap._can_access([], Counter()))


if __name__ == "__main__":
    unittest.main()
