from dataclasses import dataclass
from enum import IntEnum, StrEnum, auto


class IDCard(StrEnum):
    JOHN_HAMMOND = auto()
    ELLIE_SATTLER = auto()
    ROBERT_MULDOON = auto()
    ALAN_GRANT = auto()
    DONALD_GENARRO = auto()
    RAY_ARNOLD = auto()
    DENNIS_NEDRY = auto()
    HENRY_WU = auto()
    IAN_MALCOLM = auto()

class Battery(StrEnum):
    NORTH_UTILITY_SHED = auto()
    RAPTOR_PEN = auto()
    VISITOR_CENTER = auto()
    BEACH_UTILITY_SHED = auto()
    NUBLAR_UTILITY_SHED = auto()
    SHIP = auto()

class Item(StrEnum):
    EGG = auto()

class Event(StrEnum):
    """
    Enum type to track in-game story events.
    """
    TURN_ON_GENERATOR = auto()
    REBOOT_PARK_SYSTEMS = auto()
    ACTIVATE_MOTION_SENSORS = auto()
    BLOCK_RAPTOR_PEN_DOOR = auto()
    SECURITY_LEVEL_1 = auto()
    SECURITY_LEVEL_2 = auto()
    CONTACT_SHIP = auto()
    CLEAR_SHIP = auto()
    COLLECT_NERVE_GAS = auto()
    DESTROY_RAPTOR_NEST = auto()
    CONTACT_MAINLAND = auto()

class JPRegion(StrEnum):
    """
    Enum containing all logical regions in Jurassic Park
    """
    ### Overworld regions
    # split up mostly based on the gates
    OW_CENTRAL_REGION = "Overworld Central Region"
    OW_NORTHWEST_REGION = "Overworld Northwest Region" # Gate 1
    OW_RAPTOR_NEST_REGION = "Overworld Raptor Nest Region" # Gate 2
    OW_SOUTH_REGION = "Overworld South Region" # Gate 3 (Start region)
    OW_VISITOR_CENTER_ROOF = "Overworld Visitor Center Roof"

    ### Building regions in the OW south region
    # - Nublar Utility Shed
    NUBLAR_UTILITY_SHED_ENTRY = "Nublar Utility Shed Entry Level"
    NUBLAR_UTILITY_SHED_B1 = "Nublar Utiliy Shed Sublevel"
    NUBLAR_UTILITY_SHED_B1_LOCKED_ROOM = "Nublar Utility Shed Sublevel Locked Room"

    ### Building regions in OW central region
    # - Beach Utility Shed
    BEACH_UTILITY_SHED_ENTRY = "Beach Utility Shed Entry Level"
    BEACH_UTILITY_SHED_B1 = "Beach Utility Shed Sublevel"
    BEACH_UTILITY_SHED_B1_DARK_ROOM = "Beach Utility Shed Sublevel Dark Room"

    # - Visitor Center
    # Need Hammond's card to get to the staff elevator
    VISITOR_CENTER_ENTRY = "Visitor Center Entry Level"
    VISITOR_CENTER_ENTRY_DARK_ROOM = "Visitor Center Entry Level Dark Room"
    VISITOR_CENTER_ENTRY_STAFF_ELEVATOR = "Visitor Center Entry Level Staff Elevator"

    # Need Nedry's card to get to the computer room (reboot park systems)
    # Need Nedry's and Wu's cards to get to the lab (security level 1)
    VISITOR_CENTER_F2 = "Visitor Center Floor 2 Incubator Room"
    VISITOR_CENTER_F2_MAIN_COMPUTER = "Visitor Center Floor 2 Main Computer Room"
    VISITOR_CENTER_F2_LAB = "Visitor Center Floor 2 Laboratory"
    VISITOR_CENTER_F3 = "Visitor Center Roof Level"

    # Need Hammond's card to get here and Sattler's card to use the
    # elevator in the control room (to the raptor pen bottom floor)
    VISITOR_CENTER_B1 = "Visitor Center Sublevel"

    # - Raptor Pen
    RAPTOR_PEN_ENTRY = "Raptor Pen Entry Level" # Actually F3
    RAPTOR_PEN_F2 = "Raptor Pen Floor 2"
    RAPTOR_PEN_F2_DARK_ROOM = "Raptor Pen Floor 2"
    RAPTOR_PEN_F1 = "Raptor Pen Ground Floor"

    # Floor 1 has a few gated areas
    # Communications room (needs security level 1)
    # Elevator room (Dark, needs raptor pen battery) to B1
    RAPTOR_PEN_F1_COMMS_ROOM = "Raptor Pen Floor 1 Communications Room"
    RAPTOR_PEN_F1_DARK_ELEVATOR = "Raptor Pen Floor 1 Dark Elevator"

    RAPTOR_PEN_B1 = "Raptor Pen Sublevel 1"
    RAPTOR_PEN_B2 = "Raptor Pen Sublevel 2"

    # Room with the door that needs to be blocked to stop
    # raptors from entering the visitor center
    # Needs either Grant's ID card to get in via Raptor Pen or
    # Sattler's card to get in from the visitor center control room
    RAPTOR_PEN_B2_RAPTOR_ENTRY = "Raptor Pen Sublevel 2 Raptor Entry"

    # - Secret Area
    # Hidden entrance in the east mountains
    SECRET_AREA = "Secret Area"

    # - Ship
    SHIP_ENTRY = "Ship Entry Level"
    SHIP_B1 = "Ship Sublevel 1"
    SHIP_B1_DARK_ROOM = "Ship Sublevel 1 Dark Room"

    # Main entry part of B2 is always accessible, the back half
    # requires Ray Arnold's ID card.
    # The elevator room also requires the ship battery
    SHIP_B2 = "Ship Sublevel 2"
    SHIP_B2_COMPUTER = "Ship Sublevel 2 Computer"
    SHIP_B2_BACK = "Ship Sublevel 2 Back"
    SHIP_B2_ELEVATOR_ROOM = "Ship Sublevel 2 Elevator Room"

    # Mainland comms station is here.
    # Deploy nerve gas to enable it
    SHIP_B3 = "Ship Sublevel 3 Crew Quarters"
    SHIP_B3_COMMS_ROOM = "Ship Sublevel 3 Communications Room"
    SHIP_B4 = "Ship Sublevel 4 Cargo Hold"
    SHIP_B4_DARK_ROOM = "Ship Sublevel 4 Dark Room"

    ### Building regions in OW northwest region
    NORTH_UTILITY_SHED_ENTRY = "North Utility Shed Entry Level"
    NORTH_UTILITY_SHED_B1 = "North Utility Shed Sublevel"
    # Need Muldoon's ID card to get
    NORTH_UTILITY_SHED_NERVE_GAS = "North Utility Shed Nerve Gas Storage"

    ### Building regions in OW raptor nest region
    RAPTOR_NEST_NORTH = "Raptor Nest North"
    RAPTOR_NEST_SOUTH = "Raptor Nest South"
    # The inner room where nerve gas gets deployed
    # Physically accessible as soon as the nest is available,
    # but you need to have collected the nerve gas and cleared
    # the ship before you can deploy it.
    RAPTOR_NEST_NERVE_GAS = "Raptor Nest Nerve Gas"

class MapId(IntEnum):
    """Jurassic Park Map IDs."""
    OVERWORLD = 0x00
    NORTH_UTILITY_SHED_ENTRY_LEVEL = 0x01
    RAPTOR_PEN_ENTRY_LEVEL = 0x02
    VISITOR_CENTER_ROOF_LEVEL = 0x03
    VISITOR_CENTER_ENTRY_LEVEL = 0x04
    BEACH_UTILITY_SHED_ENTRY_LEVEL = 0x05
    NUBLAR_UTILITY_SHED_ENTRY_LEVEL = 0x06
    SHIP_ENTRY_LEVEL = 0x07
    RAPTOR_NEST_NORTH_ENTRANCE = 0x08
    RAPTOR_NEST_SOUTH_ENTRANCE = 0x09
    SECRET_LEVEL = 0x0A
    RAPTOR_PEN_GROUND_FLOOR = 0x0B
    RAPTOR_PEN_SUB_LEVEL_1 = 0x0C
    RAPTOR_PEN_SUB_LEVEL_2 = 0x0D
    RAPTOR_PEN_UPPER_LEVEL = 0x0E
    VISITOR_CENTER_FLOOR_2 = 0x0F
    VISITOR_CENTER_SUB_LEVEL = 0x10
    NUBLAR_UTILITY_SHED_SUB_LEVEL = 0x11
    BEACH_UTILITY_SHED_SUB_LEVEL = 0x12
    NORTH_UTILITY_SHED_SUB_LEVEL = 0x13
    SHIP_SUB_LEVEL_1 = 0x14
    SHIP_SUB_LEVEL_2 = 0x15
    SHIP_SUB_LEVEL_3 = 0x16
    SHIP_SUB_LEVEL_4 = 0x17

class OWEntrance(StrEnum):
    """Enum defining all of the entrances on the overworld map"""
    VISITOR_CENTER_ENTRANCE = auto()
    VISITOR_CENTER_ROOF_ENTRANCE = auto()
    BEACH_UTILITY_SHED_ENTRANCE = auto()
    RAPTOR_PEN_ENTRANCE = auto()
    SHIP_ENTRANCE = auto()
    SECRET_AREA_ENTRANCE = auto()
    NUBLAR_UTILITY_SHED_ENTRANCE = auto()
    NORTH_UTILITY_SHED_ENTRANCE = auto()
    RAPTOR_NEST_NORTH_ENTRANCE = auto()
    RAPTOR_NEST_SOUTH_ENTRANCE = auto()

    def __repr__(self):
        return repr(self.value).replace("_", " ").title()

@dataclass
class ExitCoords:
    """
    Table entry for the coordinate exit table.
    Holds the X and Y coords used when taking a building exit to the overworld.
    TODO: Figure out what Z is
          It's included here since it's part of the table entry, but I'm not
          actually sure what the value is used for yet.
    """
    x: int
    y: int
    z: int

    def __repr__(self):
        return f"x: 0x{self.x:04x}, 0x{self.y:04x}, 0x{self.z:04x}"

@dataclass
class DoorData:
    """
    Class to hold ROM data for a building entrance
    """
    # Map ID of the building connected to this door
    map_id: MapId
    # index into the building ID and coord tables in the ROM
    building_table_idx: int
    # Exit coords for this door
    coords: ExitCoords

# Table mapping map IDs to their coordinate table index.
COORD_IDX_TABLE: dict[MapId, int] = {
    MapId.NORTH_UTILITY_SHED_ENTRY_LEVEL: 0,
    MapId.RAPTOR_PEN_ENTRY_LEVEL: 1,
    MapId.VISITOR_CENTER_ROOF_LEVEL: 2,
    MapId.VISITOR_CENTER_ENTRY_LEVEL: 3,
    MapId.BEACH_UTILITY_SHED_ENTRY_LEVEL: 4,
    MapId.NUBLAR_UTILITY_SHED_ENTRY_LEVEL: 5,
    MapId.SHIP_ENTRY_LEVEL: 6,
    MapId.RAPTOR_NEST_NORTH_ENTRANCE: 7,
    # MapId.RAPTOR_NEST_NORTH_ENTRANCE: 8, # Alternate data
    MapId.RAPTOR_NEST_SOUTH_ENTRANCE: 9,
    # MapId.RAPTOR_NEST_SOUTH_ENTRANCE: 10, # Alternate data
    MapId.SECRET_LEVEL: 11
}

# Map overworld entrances to their ROM table data.
#
# NOTE: There are two missing entries near the end of this table. These
#       are duplicate table entries for the raptor nest that don't appear
#       to be used by the game.
ENTRANCE_DATA: dict[OWEntrance, DoorData] = {
    OWEntrance.NORTH_UTILITY_SHED_ENTRANCE: DoorData(
        MapId.NORTH_UTILITY_SHED_ENTRY_LEVEL, 0, ExitCoords(0x0520, 0x01F0, 0x0800)),
    OWEntrance.RAPTOR_PEN_ENTRANCE: DoorData(
        MapId.RAPTOR_PEN_ENTRY_LEVEL, 1, ExitCoords(0x0A70, 0x02C0, 0x4000)),
    OWEntrance.VISITOR_CENTER_ROOF_ENTRANCE: DoorData(
        MapId.VISITOR_CENTER_ROOF_LEVEL, 2, ExitCoords(0x0670, 0x0530, 0x4000)),
    OWEntrance.VISITOR_CENTER_ENTRANCE: DoorData(
        MapId.VISITOR_CENTER_ENTRY_LEVEL, 3, ExitCoords(0x0670, 0x05D0, 0x0800)),
    OWEntrance.BEACH_UTILITY_SHED_ENTRANCE: DoorData(
        MapId.BEACH_UTILITY_SHED_ENTRY_LEVEL, 4, ExitCoords(0x0340, 0x0DF0, 0x0800)),
    OWEntrance.NUBLAR_UTILITY_SHED_ENTRANCE: DoorData(
        MapId.NUBLAR_UTILITY_SHED_ENTRY_LEVEL, 5, ExitCoords(0x0820, 0x0DF0, 0x0800)),
    OWEntrance.SHIP_ENTRANCE: DoorData(
        MapId.SHIP_ENTRY_LEVEL, 6, ExitCoords(0x0ED0, 0x0B70, 0x0800)),
    OWEntrance.RAPTOR_NEST_NORTH_ENTRANCE: DoorData(
        MapId.RAPTOR_NEST_NORTH_ENTRANCE, 7, ExitCoords(0x0BB0, 0x0070, 0x0800)),
    OWEntrance.RAPTOR_NEST_SOUTH_ENTRANCE: DoorData(
        MapId.RAPTOR_NEST_SOUTH_ENTRANCE, 9, ExitCoords(0x0F00, 0x05C0, 0x0800)),
    OWEntrance.SECRET_AREA_ENTRANCE: DoorData(
        MapId.SECRET_LEVEL, 11, ExitCoords(0x0B74, 0x0B00, 0x4000)),
}
