import random
from collections import Counter
from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import TypeAlias

from jprando.jpmap.entrancetypes import (
    Battery,
    Event,
    IDCard,
    Item,
    JPRegion,
    MapId,
    OWEntrance,
)

Reward: TypeAlias = Event | IDCard | Battery | Item
Rules: TypeAlias = list[list[Reward]] | None
Rewards: TypeAlias = list[Reward] | None
Connectors: TypeAlias = list["Connector"]
MapNodes: TypeAlias = dict[JPRegion, "MapNode"]

_NULL_ACCESS_RULE = None
_REVERSIBLE = True
_NON_REVERSIBLE = False

@dataclass
class MapNode:
    """
    Represents a logical region of the JP map.
    """
    name: JPRegion
    rewards: Rewards
    overworld: bool = False
    map_id: MapId | None = None
    exits: Connectors = field(default_factory=list["Connector"])

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if not isinstance(other, MapNode):
            return False
        return self.name == other.name

class ConnectorType(StrEnum):
    """
    Defines the various types of connectors.
    """
    # Used for external building doors that transition between indoor
    # and outdoor areas
    BUILDING = auto()

    # Used for elevator type connectors in buildings
    ELEVATOR = auto()

    # Static region connector that never gets shuffled
    # Could be something like a dark room requiring a battery or
    # a door that requires a keycard or event flag to unlock or a
    # logical overworld region connector.
    STATIC = auto()

@dataclass
class Connector:
    """
    Parent class that represents a connection between map nodes.
    """
    name: str
    type: ConnectorType
    from_node: MapNode
    to_node: MapNode
    reversible: bool
    rules: Rules = field(default_factory=list[list[Reward]]|None)
    linked_exit: "Connector|None" = None

    def __hash__(self):
        return hash(f"{self.name}{self.from_node.name}{self.to_node.name}")

    def __eq__(self, other):
        if not isinstance(other, Connector):
            return False

        return self.name == other.name and \
               self.to_node == other.to_node and \
               self.from_node == other.from_node

@dataclass
class MapData:
    """
    Top level dataclass to hold a representation of the Jurassic Park map.
    """
    start: MapNode
    nodes: MapNodes
    connectors: Connectors

def get_default_map() -> MapData:
    """
    Get a default Jurassic Park MapData object.
    """
    nodes = _get_default_map_nodes()
    connectors = _get_default_connectors(nodes)
    _connect_nodes(connectors)
    return MapData(nodes[JPRegion.OW_SOUTH_REGION], nodes, connectors)

def _get_default_map_nodes() -> MapNodes:
    """
    Create and return a default set of MapNodes representing all of the
    logical regions (indoor and ourdoor) on the JP map.
    """
    nodes: MapNodes = {
        # Overworld regions
        #    - Always available
        #    - South region is behind gate 3, which starts unlocked
        #    - South region is the starting region
        JPRegion.OW_SOUTH_REGION: MapNode(JPRegion.OW_SOUTH_REGION, None, True),
        JPRegion.OW_CENTRAL_REGION: MapNode(JPRegion.OW_CENTRAL_REGION, None, True),
        JPRegion.OW_VISITOR_CENTER_ROOF: MapNode(JPRegion.OW_VISITOR_CENTER_ROOF, None, True),
        #   - Gates start locked, can be opened after rebooting park systems
        JPRegion.OW_NORTHWEST_REGION: MapNode(JPRegion.OW_NORTHWEST_REGION, None, True), # Gate 1
        JPRegion.OW_RAPTOR_NEST_REGION: MapNode(JPRegion.OW_RAPTOR_NEST_REGION, None, True), # Gate 2

        # Nublar Utility Shed
        #   - Entry and B1 are always open
        #   - Locked room in B1 needs Malcolm's ID card (vanilla Gennaro ID card)
        JPRegion.NUBLAR_UTILITY_SHED_ENTRY: MapNode(
            JPRegion.NUBLAR_UTILITY_SHED_ENTRY,
            [Event.TURN_ON_GENERATOR],
            False,
            MapId.NUBLAR_UTILITY_SHED_ENTRY_LEVEL),
        JPRegion.NUBLAR_UTILITY_SHED_B1: MapNode(JPRegion.NUBLAR_UTILITY_SHED_B1, None),
        JPRegion.NUBLAR_UTILITY_SHED_B1_LOCKED_ROOM: MapNode(JPRegion.NUBLAR_UTILITY_SHED_B1_LOCKED_ROOM, None),

        # Beach Utility Shed
        #   - Entry level always available
        JPRegion.BEACH_UTILITY_SHED_ENTRY: MapNode(
            JPRegion.BEACH_UTILITY_SHED_ENTRY, None, False, MapId.BEACH_UTILITY_SHED_ENTRY_LEVEL),
        #   - Elevator locked by Gennaro's ID card
        JPRegion.BEACH_UTILITY_SHED_B1: MapNode(JPRegion.BEACH_UTILITY_SHED_B1, None),
        #   - Dark room needs the battery (vanilla Ray Arnold ID card location)
        JPRegion.BEACH_UTILITY_SHED_B1_DARK_ROOM: MapNode(JPRegion.BEACH_UTILITY_SHED_B1_DARK_ROOM, None),

        # Visitor Center Floor 1
        #   - Main entry level is always open
        #   - Dark room needs the battery (vanilla Grant ID card)
        #   - Staff elevator room needs Hammond's ID card (leads to sub level)
        JPRegion.VISITOR_CENTER_ENTRY: MapNode(
            JPRegion.VISITOR_CENTER_ENTRY, None, False, MapId.VISITOR_CENTER_ENTRY_LEVEL),
        JPRegion.VISITOR_CENTER_ENTRY_DARK_ROOM: MapNode(JPRegion.VISITOR_CENTER_ENTRY_DARK_ROOM, None),
        JPRegion.VISITOR_CENTER_ENTRY_STAFF_ELEVATOR: MapNode(JPRegion.VISITOR_CENTER_ENTRY_STAFF_ELEVATOR, None),

        # Visitor Center floor 2
        #   - Main floor 2 (incubator room) is always open
        #   - Main computer area needs Nedry's ID card
        #   - Lab needs Nedry's card and Dr. Wu's card
        JPRegion.VISITOR_CENTER_F2: MapNode(JPRegion.VISITOR_CENTER_F2, None),
        JPRegion.VISITOR_CENTER_F2_MAIN_COMPUTER: MapNode(
            JPRegion.VISITOR_CENTER_F2_MAIN_COMPUTER, [Event.REBOOT_PARK_SYSTEMS, Event.ACTIVATE_MOTION_SENSORS]),
        JPRegion.VISITOR_CENTER_F2_LAB: MapNode(JPRegion.VISITOR_CENTER_F2_LAB, [Event.SECURITY_LEVEL_1]),

        # Visitor Center Floor 3
        #   - Always available, leads to roof
        JPRegion.VISITOR_CENTER_F3: MapNode(JPRegion.VISITOR_CENTER_F3, None, False, MapId.VISITOR_CENTER_ROOF_LEVEL),

        # Visitor Center Sub Level
        #   - Accessible with hammond's ID card from the VC entry level
        #     or from the raptor pen with the battery and Grant's card
        #
        #   Need Sattler's card to take the elevator to the raptor pen,
        #   but not to go the other way.
        #
        #   Need Grant's card to get into the room with the elevator in the
        #   raptor pen, but not to get out.
        #   TODO: Confirm this
        JPRegion.VISITOR_CENTER_B1: MapNode(JPRegion.VISITOR_CENTER_B1, None),

        # Raptor Pen Entry Level (Floor 3)
        #   - Entry level is always available
        JPRegion.RAPTOR_PEN_ENTRY: MapNode(JPRegion.RAPTOR_PEN_ENTRY, None, False, MapId.RAPTOR_PEN_ENTRY_LEVEL),

        # Raptor Pen Floor 2
        #   - Always available
        JPRegion.RAPTOR_PEN_F2: MapNode(JPRegion.RAPTOR_PEN_F2, None),
        #   - Need the raptor pen battery for the dark room (vanilla Malcolm ID card)
        JPRegion.RAPTOR_PEN_F2_DARK_ROOM: MapNode(JPRegion.RAPTOR_PEN_F2_DARK_ROOM, None),

        # Raptor Pen Floor 1
        #   - Always available
        JPRegion.RAPTOR_PEN_F1: MapNode(JPRegion.RAPTOR_PEN_F1, None),
        #   - Need security level 1 (computer here can contact the ship)
        JPRegion.RAPTOR_PEN_F1_COMMS_ROOM: MapNode(JPRegion.RAPTOR_PEN_F1_COMMS_ROOM, [Event.CONTACT_SHIP]),
        #   - Need raptor pen battery for the elevator in this room
        JPRegion.RAPTOR_PEN_F1_DARK_ELEVATOR: MapNode(JPRegion.RAPTOR_PEN_F1_DARK_ELEVATOR, None),

        # Raptor Pen B1
        #   - Nothing locked on this floor, but you need the battery
        #     if trying to progress upward since the elevator is
        #     in a dark room on F1
        JPRegion.RAPTOR_PEN_B1: MapNode(JPRegion.RAPTOR_PEN_B1, None),

        # Raptor Pen B2
        #   - Main area doesn't have any restrictions
        JPRegion.RAPTOR_PEN_B2: MapNode(JPRegion.RAPTOR_PEN_B2, None),
        #   - Block raptor pen door event
        #   - Need Grant's card to get in  from raptor pen side
        #   - Need Sattler's card to get in from the visitor center
        JPRegion.RAPTOR_PEN_B2_RAPTOR_ENTRY: MapNode(
            JPRegion.RAPTOR_PEN_B2_RAPTOR_ENTRY, [Event.BLOCK_RAPTOR_PEN_DOOR]),

        # Raptor Nest
        #   - Two overworld entrances lead to the raptor nest
        #   - Entrances are in OW_RAPTOR_NEST_REGION
        #   - This is one of the only connector zones
        JPRegion.RAPTOR_NEST_NORTH: MapNode(JPRegion.RAPTOR_NEST_NORTH, None, False, MapId.RAPTOR_NEST_NORTH_ENTRANCE),
        JPRegion.RAPTOR_NEST_SOUTH: MapNode(JPRegion.RAPTOR_NEST_SOUTH, None, False, MapId.RAPTOR_NEST_SOUTH_ENTRANCE),
        #   - Physically accessible as soon as the nest is open
        #     but logically requires nerve gas to be collected and
        #     the ship to be cleared
        JPRegion.RAPTOR_NEST_NERVE_GAS: MapNode(JPRegion.RAPTOR_NEST_NERVE_GAS, [Event.DESTROY_RAPTOR_NEST]),

        # Ship
        #   - Main level is always open
        JPRegion.SHIP_ENTRY: MapNode(JPRegion.SHIP_ENTRY, None, False, MapId.SHIP_ENTRY_LEVEL),

        # Ship Sublevel 1
        #   - Main area is always open
        #   - Dark room requires the ship battery
        JPRegion.SHIP_B1: MapNode(JPRegion.SHIP_B1, None),
        JPRegion.SHIP_B1_DARK_ROOM: MapNode(JPRegion.SHIP_B1_DARK_ROOM, None),

        # Ship Sublevel 2
        #   - Main area is open and includes the Security Level 2 computer
        #   - The computer is its own region since you need Sec Level 1 to use it
        #   - The back half requires Ray Arnold's ID card
        #   - The elevetor dark room also requires the ship battery
        #   - Using the elevator also requires security level 2
        JPRegion.SHIP_B2: MapNode(JPRegion.SHIP_B2, None),
        JPRegion.SHIP_B2_COMPUTER: MapNode(JPRegion.SHIP_B2_COMPUTER, [Event.SECURITY_LEVEL_2]),
        JPRegion.SHIP_B2_BACK: MapNode(JPRegion.SHIP_B2_BACK, None),
        JPRegion.SHIP_B2_ELEVATOR_ROOM: MapNode(JPRegion.SHIP_B2_ELEVATOR_ROOM, None),

        # Ship Sublevel 3
        #   - sublevel 3 is the crew quarters.  Most of this are is open
        #   - Vanilla Sattler's ID card is in this region
        #   - The comms room requires the battery and the computer will not
        #     be available until the raptor nest is destroyed.
        JPRegion.SHIP_B3: MapNode(JPRegion.SHIP_B3, None),
        JPRegion.SHIP_B3_COMMS_ROOM: MapNode(JPRegion.SHIP_B3_COMMS_ROOM, [Event.CONTACT_MAINLAND]),

        # Ship Sublevel 4
        #   - Ship's cargo hold
        #   - There is a dark room in the back that requires the ship battery
        #   - Being able to reach and clear the cargo hold dark room means that
        #     the whole ship is clearable
        #     TODO: This may not hold true if/when elevator shuffle is added
        #           Clearing the ship in that case will need some additional tracking.
        JPRegion.SHIP_B4: MapNode(JPRegion.SHIP_B4, None),
        JPRegion.SHIP_B4_DARK_ROOM: MapNode(JPRegion.SHIP_B4_DARK_ROOM, [Event.CLEAR_SHIP]),

        # North Utility Shed
        #   - The shed in the northwest area behind the locked gate (gate 1)
        #   - The elevator to B1 has no restrictions, but the nerve gas storage
        #     is locked my Muldoon's ID card
        JPRegion.NORTH_UTILITY_SHED_ENTRY: MapNode(
            JPRegion.NORTH_UTILITY_SHED_ENTRY, None, False, MapId.NORTH_UTILITY_SHED_ENTRY_LEVEL),
        JPRegion.NORTH_UTILITY_SHED_B1: MapNode(JPRegion.NORTH_UTILITY_SHED_B1, None),
        JPRegion.NORTH_UTILITY_SHED_NERVE_GAS: MapNode(
            JPRegion.NORTH_UTILITY_SHED_NERVE_GAS, [Event.COLLECT_NERVE_GAS]),

        # Secret Area
        #   - Secret area is a hidden entrance in the east mountains
        JPRegion.SECRET_AREA: MapNode(JPRegion.SECRET_AREA, None, False, MapId.SECRET_LEVEL)
    }
    return nodes

def _get_default_connectors(nodes: MapNodes) -> Connectors:
    """
    Return a list of the default connectors for the Jurassic Park map.
    """
    # TODO: Elevator shuffle will require some rework, where individual elevators are regions
    #       with multiple connectors to handle elevators with multiple floors.
    #       For now they are treated as single connector types.
    connectors: Connectors = [
        # ######################## #
        # # Overworld connectors # #
        # ######################## #
        # OW to OW Connectors
        Connector("OW Gate 3",
            ConnectorType.STATIC,
            nodes[JPRegion.OW_CENTRAL_REGION],
            nodes[JPRegion.OW_SOUTH_REGION],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        Connector("OW Gate 2",
            ConnectorType.STATIC,
            nodes[JPRegion.OW_CENTRAL_REGION],
            nodes[JPRegion.OW_RAPTOR_NEST_REGION],
            _REVERSIBLE,
            [[Event.REBOOT_PARK_SYSTEMS]]),
        Connector("OW Gate 1",
            ConnectorType.STATIC,
            nodes[JPRegion.OW_CENTRAL_REGION],
            nodes[JPRegion.OW_NORTHWEST_REGION],
            _REVERSIBLE,
            [[Event.REBOOT_PARK_SYSTEMS]]),

        # OW central region connectors
        Connector(OWEntrance.VISITOR_CENTER_ENTRANCE,
            ConnectorType.BUILDING,
            nodes[JPRegion.OW_CENTRAL_REGION],
            nodes[JPRegion.VISITOR_CENTER_ENTRY],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        Connector(OWEntrance.BEACH_UTILITY_SHED_ENTRANCE,
            ConnectorType.BUILDING,
            nodes[JPRegion.OW_CENTRAL_REGION],
            nodes[JPRegion.BEACH_UTILITY_SHED_ENTRY],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        Connector(OWEntrance.RAPTOR_PEN_ENTRANCE,
            ConnectorType.BUILDING,
            nodes[JPRegion.OW_CENTRAL_REGION],
            nodes[JPRegion.RAPTOR_PEN_ENTRY],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        Connector(OWEntrance.SHIP_ENTRANCE,
            ConnectorType.BUILDING,
            nodes[JPRegion.OW_CENTRAL_REGION],
            nodes[JPRegion.SHIP_ENTRY],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        Connector(OWEntrance.SECRET_AREA_ENTRANCE,
            ConnectorType.BUILDING,
            nodes[JPRegion.OW_CENTRAL_REGION],
            nodes[JPRegion.SECRET_AREA],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),

        # OW south (Nublar Utility Shed) region connectors
        Connector(OWEntrance.NUBLAR_UTILITY_SHED_ENTRANCE,
            ConnectorType.BUILDING,
            nodes[JPRegion.OW_SOUTH_REGION],
            nodes[JPRegion.NUBLAR_UTILITY_SHED_ENTRY],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),

        # OW northwest (North Utility Shed) region connectors
        Connector(OWEntrance.NORTH_UTILITY_SHED_ENTRANCE,
            ConnectorType.BUILDING,
            nodes[JPRegion.OW_NORTHWEST_REGION],
            nodes[JPRegion.NORTH_UTILITY_SHED_ENTRY],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),

        # OW raptor nest region connectors
        Connector(OWEntrance.RAPTOR_NEST_NORTH_ENTRANCE,
            ConnectorType.BUILDING,
            nodes[JPRegion.OW_RAPTOR_NEST_REGION],
            nodes[JPRegion.RAPTOR_NEST_NORTH],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        Connector(OWEntrance.RAPTOR_NEST_SOUTH_ENTRANCE,
            ConnectorType.BUILDING,
            nodes[JPRegion.OW_RAPTOR_NEST_REGION],
            nodes[JPRegion.RAPTOR_NEST_SOUTH],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),

        # ################################## #
        # # Nublar utility shed connectors # #
        # ################################## #
        Connector("Nublar Utility Shed Elevator",
            ConnectorType.ELEVATOR,
            nodes[JPRegion.NUBLAR_UTILITY_SHED_ENTRY],
            nodes[JPRegion.NUBLAR_UTILITY_SHED_B1],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        Connector("Nublar Utility Shed B1 Locked Door",
            ConnectorType.STATIC,
            nodes[JPRegion.NUBLAR_UTILITY_SHED_B1],
            nodes[JPRegion.NUBLAR_UTILITY_SHED_B1_LOCKED_ROOM],
            _REVERSIBLE,
            [[IDCard.IAN_MALCOLM]]),

        # ################################# #
        # # Beach utility shed connectors # #
        # ################################# #
        Connector("Beach Utility Shed Elevator",
            ConnectorType.ELEVATOR,
            nodes[JPRegion.BEACH_UTILITY_SHED_ENTRY],
            nodes[JPRegion.BEACH_UTILITY_SHED_B1],
            _REVERSIBLE,
            [[IDCard.DONALD_GENARRO]]),
        Connector("Beach Utility Shed B1 Dark Room",
            ConnectorType.STATIC,
            nodes[JPRegion.BEACH_UTILITY_SHED_B1],
            nodes[JPRegion.BEACH_UTILITY_SHED_B1_DARK_ROOM],
            _REVERSIBLE,
            [[Battery.BEACH_UTILITY_SHED]]),

        # ################################# #
        # # North utility shed connectors # #
        # ################################# #
        Connector("North Utility Shed Elevator",
            ConnectorType.ELEVATOR,
            nodes[JPRegion.NORTH_UTILITY_SHED_ENTRY],
            nodes[JPRegion.NORTH_UTILITY_SHED_B1],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        Connector("North Utility Shed Nerve Gas Storage",
            ConnectorType.STATIC,
            nodes[JPRegion.NORTH_UTILITY_SHED_B1],
            nodes[JPRegion.NORTH_UTILITY_SHED_NERVE_GAS],
            _REVERSIBLE,
            [[IDCard.ROBERT_MULDOON]]),

        # ############################# #
        # # Visitor center connectors # #
        # ############################# #
        # Floor 1 connections
        Connector("Visitor Center F1 Main Elevator",
            ConnectorType.ELEVATOR,
            nodes[JPRegion.VISITOR_CENTER_ENTRY],
            nodes[JPRegion.VISITOR_CENTER_F2],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        Connector("Visitor Center F1 Dark Room",
            ConnectorType.STATIC,
            nodes[JPRegion.VISITOR_CENTER_ENTRY],
            nodes[JPRegion.VISITOR_CENTER_ENTRY_DARK_ROOM],
            _REVERSIBLE,
            [[Battery.VISITOR_CENTER]]),
        # NOTE: Hammond's ID card is needed to get in, but not needed to get out
        Connector("Visitor Center F1 Staff Elevator Room",
            ConnectorType.STATIC,
            nodes[JPRegion.VISITOR_CENTER_ENTRY],
            nodes[JPRegion.VISITOR_CENTER_ENTRY_STAFF_ELEVATOR],
            _NON_REVERSIBLE,
            [[IDCard.JOHN_HAMMOND]]),
        Connector("Visitor Center F1 Staff Elevator Room",
            ConnectorType.STATIC,
            nodes[JPRegion.VISITOR_CENTER_ENTRY_STAFF_ELEVATOR],
            nodes[JPRegion.VISITOR_CENTER_ENTRY],
            _NON_REVERSIBLE,
            _NULL_ACCESS_RULE),
        Connector("Visitor Center F1 Staff Elevator Elevator",
            ConnectorType.ELEVATOR,
            nodes[JPRegion.VISITOR_CENTER_ENTRY_STAFF_ELEVATOR],
            nodes[JPRegion.VISITOR_CENTER_B1],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        # Floor 2
        Connector("Visitor Center F2 Elevator",
            ConnectorType.ELEVATOR,
            nodes[JPRegion.VISITOR_CENTER_F2],
            nodes[JPRegion.VISITOR_CENTER_F3],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        Connector("Visitor Center F2 Computer Room",
            ConnectorType.STATIC,
            nodes[JPRegion.VISITOR_CENTER_F2],
            nodes[JPRegion.VISITOR_CENTER_F2_MAIN_COMPUTER],
            _REVERSIBLE,
            [[IDCard.DENNIS_NEDRY]]),
        Connector("Visitor Center F2 Lab",
            ConnectorType.STATIC,
            nodes[JPRegion.VISITOR_CENTER_F2_MAIN_COMPUTER],
            nodes[JPRegion.VISITOR_CENTER_F2_LAB],
            _REVERSIBLE,
            [[IDCard.HENRY_WU]]),
        # Floor 3
        Connector(OWEntrance.VISITOR_CENTER_ROOF_ENTRANCE,
            ConnectorType.BUILDING,
            nodes[JPRegion.VISITOR_CENTER_F3],
            nodes[JPRegion.OW_VISITOR_CENTER_ROOF],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        # Sublevel 1
        # NOTE: The other side of this connector does not require the ID card
        #       This is ok for now, just define a separate one-way elevator
        #       from the raptor pen. These will need to be associated when
        #       elevator shuffle is implemented.
        Connector("Visitor Center Control Room Elevator",
            ConnectorType.ELEVATOR,
            nodes[JPRegion.VISITOR_CENTER_B1],
            nodes[JPRegion.RAPTOR_PEN_B2_RAPTOR_ENTRY],
            _NON_REVERSIBLE,
            [[IDCard.ELLIE_SATTLER]]),

        # ######################### #
        # # Raptor pen connectors # #
        # ######################### #
        # Entry Level (Floor 3)
        Connector("Raptor Pen F3 Elevator",
            ConnectorType.ELEVATOR,
            nodes[JPRegion.RAPTOR_PEN_ENTRY],
            nodes[JPRegion.RAPTOR_PEN_F2],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        # Floor 2
        Connector("Raptor Pen F2 Dark Room",
            ConnectorType.STATIC,
            nodes[JPRegion.RAPTOR_PEN_F2],
            nodes[JPRegion.RAPTOR_PEN_F2_DARK_ROOM],
            _REVERSIBLE,
            [[Battery.RAPTOR_PEN]]),
        Connector("Raptor Pen F2 Elevator",
            ConnectorType.ELEVATOR,
            nodes[JPRegion.RAPTOR_PEN_F2],
            nodes[JPRegion.RAPTOR_PEN_F1],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        # Floor 1
        Connector("Raptor Pen F1 Comms Room",
            ConnectorType.STATIC,
            nodes[JPRegion.RAPTOR_PEN_F1],
            nodes[JPRegion.RAPTOR_PEN_F1_COMMS_ROOM],
            _REVERSIBLE,
            [[Event.SECURITY_LEVEL_1]]),
        Connector("Raptor Pen F1 Dark Elevator Room",
            ConnectorType.STATIC,
            nodes[JPRegion.RAPTOR_PEN_F1],
            nodes[JPRegion.RAPTOR_PEN_F1_DARK_ELEVATOR],
            _REVERSIBLE,
            [[Battery.RAPTOR_PEN]]),
        Connector("Raptor Pen F1 Dark Elevator",
            ConnectorType.ELEVATOR,
            nodes[JPRegion.RAPTOR_PEN_F1_DARK_ELEVATOR],
            nodes[JPRegion.RAPTOR_PEN_B1],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        # Sublevel 1
        Connector("Raptor Pen B1B2 Elevator",
            ConnectorType.ELEVATOR,
            nodes[JPRegion.RAPTOR_PEN_B1],
            nodes[JPRegion.RAPTOR_PEN_B2],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        # Sublevel 2
        # NOTE: Grants card is only needed to get in, not out
        Connector("Raptor Pen Raptor Entry Point",
            ConnectorType.STATIC,
            nodes[JPRegion.RAPTOR_PEN_B2],
            nodes[JPRegion.RAPTOR_PEN_B2_RAPTOR_ENTRY],
            _NON_REVERSIBLE,
            [[IDCard.ALAN_GRANT]]),
        Connector("Raptor Pen Raptor Entry Point",
            ConnectorType.STATIC,
            nodes[JPRegion.RAPTOR_PEN_B2_RAPTOR_ENTRY],
            nodes[JPRegion.RAPTOR_PEN_B2],
            _NON_REVERSIBLE,
            _NULL_ACCESS_RULE),
        # NOTE: Sattler's card is needed for the opposite direction, but this one has no requirements
        Connector("Raptor Pen Elevator to VC Control Room",
            ConnectorType.ELEVATOR,
            nodes[JPRegion.RAPTOR_PEN_B2_RAPTOR_ENTRY],
            nodes[JPRegion.VISITOR_CENTER_B1],
            _NON_REVERSIBLE,
            _NULL_ACCESS_RULE),

        # ########################## #
        # # Ship connectors # #
        # ########################## #
        # Floor 1
        Connector("Ship F1 Elevator",
            ConnectorType.ELEVATOR,
            nodes[JPRegion.SHIP_ENTRY],
            nodes[JPRegion.SHIP_B1],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        # Sublevel 1
        Connector("Ship B1 Elevator",
            ConnectorType.ELEVATOR,
            nodes[JPRegion.SHIP_B1],
            nodes[JPRegion.SHIP_B2],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        Connector("Ship B1 Dark Room",
            ConnectorType.STATIC,
            nodes[JPRegion.SHIP_B1],
            nodes[JPRegion.SHIP_B1_DARK_ROOM],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        # Sublevel 2
        Connector("Ship B2 Computer",
            ConnectorType.STATIC,
            nodes[JPRegion.SHIP_B2],
            nodes[JPRegion.SHIP_B2_COMPUTER],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        Connector("Ship B2 Back",
            ConnectorType.STATIC,
            nodes[JPRegion.SHIP_B2],
            nodes[JPRegion.SHIP_B2_BACK],
            _REVERSIBLE,
            [[IDCard.RAY_ARNOLD]]),
        Connector("Ship B2 Back Elevator Room",
            ConnectorType.STATIC,
            nodes[JPRegion.SHIP_B2_BACK],
            nodes[JPRegion.SHIP_B2_ELEVATOR_ROOM],
            _REVERSIBLE,
            [[Battery.SHIP]]),
        Connector("Ship B2 Back Elevator",
            ConnectorType.ELEVATOR,
            nodes[JPRegion.SHIP_B2_ELEVATOR_ROOM],
            nodes[JPRegion.SHIP_B3],
            _REVERSIBLE,
            [[Event.SECURITY_LEVEL_2]]),
        # Sublevel 3 (Crew quarters)
        Connector("Ship B3 Comms Room",
            ConnectorType.STATIC,
            nodes[JPRegion.SHIP_B3],
            nodes[JPRegion.SHIP_B3_COMMS_ROOM],
            _REVERSIBLE,
            [[Battery.SHIP, Event.DESTROY_RAPTOR_NEST]]),
        Connector("Ship B3 Elevator",
            ConnectorType.ELEVATOR,
            nodes[JPRegion.SHIP_B3],
            nodes[JPRegion.SHIP_B4],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        # Sublevel 4 (Cargo hold)
        Connector("Ship B4 Dark Room",
            ConnectorType.STATIC,
            nodes[JPRegion.SHIP_B4],
            nodes[JPRegion.SHIP_B4_DARK_ROOM],
            _REVERSIBLE,
            [[Battery.SHIP]]),

        # ########################## #
        # # Raptor nest connectors # #
        # ########################## #
        # TODO: Eventually replace the collect nerve gas event with the nerve gas item
        #       For now the item is local, so we have to use the event.
        Connector("Raptor Nest Link",
            ConnectorType.STATIC,
            nodes[JPRegion.RAPTOR_NEST_NORTH],
            nodes[JPRegion.RAPTOR_NEST_SOUTH],
            _REVERSIBLE,
            _NULL_ACCESS_RULE),
        Connector("Raptor Nest Nerve Gas Room",
            ConnectorType.STATIC,
            nodes[JPRegion.RAPTOR_NEST_NORTH],
            nodes[JPRegion.RAPTOR_NEST_NERVE_GAS],
            _REVERSIBLE,
            [[Event.COLLECT_NERVE_GAS, Event.CLEAR_SHIP]]),
    ]

    return connectors

def _connect_nodes(connectors: Connectors):
    """
    Wire up all of the connectors with their respective nodes
    """
    for conn in connectors:
        conn.from_node.exits.append(conn)
        if conn.reversible:
            # Create the opposite version of this connector
            rev = Connector(conn.name, conn.type, conn.to_node, conn.from_node, conn.reversible, conn.rules)
            conn.to_node.exits.append(rev)
            # Link the two exits together
            conn.linked_exit = rev
            rev.linked_exit = conn

def _can_access(rules: Rules, inventory: Counter) -> bool:
    """
    Check if the player can satisfy the current set of access rules based on the
    current state of their inventory
    """
    # Default case - No rules, so always accessible
    if rules is None or not rules:
        return True

    for rule in rules:
        can_access = True
        for key in rule:
            if key not in inventory:
                can_access = False
                break

        if can_access:
            # One of the access rule passed
            return True

    # None of the access rules passed
    return False

def _visit_all(map_data: MapData, start_inven: Rewards) -> bool:
    """
    Visit the entire map to ensure all nodes are reachable in the current configuration.
    """
    visited = dict.fromkeys(map_data.nodes.values(), False)
    queue = [map_data.start]
    inven = Counter(start_inven)
    # List of connectors that are reachable but can't currently be traversed
    con_reachable: Connectors = []

    # TODO: Maybe add a visited property to the node itself to avoid
    #       dealing with these lookups?
    def not_seen(node: MapNode) -> bool:
        return (not visited[node]) and (node not in queue)

    while len(queue) > 0:
        curr = queue.pop()

        # Add rewards for the new node
        if curr.rewards and not visited[curr]:
            inven.update(curr.rewards)

        visited[curr] = True

        # Check the reachable but locked connectors again
        for entrance in con_reachable:
            if _can_access(entrance.rules, inven) and not_seen(entrance.to_node):
                queue.append(entrance.to_node)

        # Add new reachable nodes from the current node
        for entrance in curr.exits:
            if not_seen(entrance.to_node):
                if _can_access(entrance.rules, inven):
                    queue.append(entrance.to_node)
                else:
                    con_reachable.append(entrance)

    # Verify that all nodes are reachable
    all_reachable = True
    for seen in visited.values():
        if not seen:
            all_reachable = False
            break

    return all_reachable

def _print_map(map_data: MapData):
    """
    Debug function to print the current connections
    """
    for node in map_data.nodes.values():
        print(f"{node.name}")
        for conn in node.exits:
            print(f"  {conn.name} - {conn.from_node.name} -> {conn.to_node.name}")

def _shuffle_map(map_data: MapData):
    """
    Shuffle a map.

    Only shuffled the external building entrances.
    """
    outdoor_regions: list[JPRegion] = [
        JPRegion.OW_SOUTH_REGION,
        JPRegion.OW_CENTRAL_REGION,
        JPRegion.OW_NORTHWEST_REGION,
        JPRegion.OW_RAPTOR_NEST_REGION,
        JPRegion.OW_VISITOR_CENTER_ROOF
    ]

    # Build up a list of all outdoor exits
    # Technically connectors exist for both directions on the doors,
    # but we only want the outdoor -> indoor versions.  The opposite
    # directions are linked in the exit, so we just need the one side.
    outdoor_exits: Connectors = []
    for region in outdoor_regions:
        for exit in map_data.nodes[region].exits:
            if exit.type == ConnectorType.BUILDING:
                outdoor_exits.append(exit)

    # Unlink and delete the reverse connectors
    for conn in outdoor_exits:
        if conn.linked_exit:
            conn.to_node.exits.remove(conn.linked_exit)
        conn.linked_exit = None

    # Create and shuffle a list of all endpoints
    endpoints = [x.to_node for x in outdoor_exits]
    random.shuffle(endpoints)

    # Relink outdoor exits to a new endpoint based on the shuffled index
    for conn, node in zip(outdoor_exits, endpoints, strict=True):
        conn.to_node = node
        if conn.reversible:
            rev = Connector(conn.name, conn.type, conn.to_node, conn.from_node, conn.reversible, conn.rules)
            conn.to_node.exits.append(rev)
            conn.linked_exit = rev
            rev.linked_exit = conn

def shuffle_map(map_data: MapData):
    """
    Shuffle the overworld connectors on the given map.
    """
    # Assume access to all items for shuffling
    inventory: Rewards = list(Battery)
    inventory.extend(list(IDCard))
    inventory.extend(list(Item))
    valid = False
    while not valid:
        _shuffle_map(map_data)
        valid = _visit_all(map_data, inventory)

def main():
    map_data = get_default_map()

    # Assume access to all items for this test
    inventory: Rewards = list(Battery)
    inventory.extend(list(IDCard))
    inventory.extend(list(Item))

    valid = False
    count = 0
    while not valid:
        count += 1
        _shuffle_map(map_data)
        valid = _visit_all(map_data, inventory)

    print(f"Found valid map in {count} iterations")
    _print_map(map_data)

if __name__ == "__main__":
    main()
