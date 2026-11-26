
import unittest

from jprando.jpmap import jpmap
from jprando.jpmap.entrancetypes import (
    Event,
    JPRegion,
)


class SweepMapTests(unittest.TestCase):

    def setUp(self):
        self.start = jpmap.MapNode(
            JPRegion.OW_SOUTH_REGION, None, None
        )

        self.locked = jpmap.MapNode(
            JPRegion.OW_CENTRAL_REGION, None, None
        )

        connector = jpmap.Connector(
            "Locked Door",
            jpmap.ConnectorType.STATIC,
            self.start,
            self.locked,
            False,
            [[Event.REBOOT_PARK_SYSTEMS]]
        )

        self.start.exits.append(connector)

        self.map_data = jpmap.MapData(
            start=self.start,
            nodes={
                self.start.name: self.start,
                self.locked.name: self.locked,
            },
            connectors=[connector],
            treasure_map={}
        )

    def test_start_node_is_reachable(self):
        results = jpmap.sweep_map(self.map_data, [])

        self.assertIn(
            self.start,
            results.reachable_nodes
        )

    def test_locked_connector_requires_event(self):
        results = jpmap.sweep_map(self.map_data, [])

        self.assertNotIn(
            self.locked,
            results.reachable_nodes
        )

        self.assertIn(
            self.locked,
            results.unreachable_nodes
        )

    def test_event_unlocks_connector(self):
        results = jpmap.sweep_map(
            self.map_data,
            [Event.REBOOT_PARK_SYSTEMS]
        )

        self.assertIn(
            self.locked,
            results.reachable_nodes
        )

        self.assertEqual(
            len(results.unreachable_nodes),
            0
        )


if __name__ == "__main__":
    unittest.main()
