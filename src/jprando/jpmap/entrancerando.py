from jprando.jpmap.entrancetypes import (
    COORD_IDX_TABLE,
    ENTRANCE_DATA,
    JPRegion,
    OWEntrance,
)
from jprando.jpmap.jpmap import Connectors, ConnectorType, MapData
from jprando.rom.jprom import JPRom


def apply_entrance_rando(rom: JPRom, map_data: MapData):
    """
    Apply entrance rando for building entrances.
    """
    outdoor_regions: list[JPRegion] = [
        JPRegion.OW_SOUTH_REGION,
        JPRegion.OW_CENTRAL_REGION,
        JPRegion.OW_NORTHWEST_REGION,
        JPRegion.OW_RAPTOR_NEST_REGION,
        JPRegion.OW_VISITOR_CENTER_ROOF
    ]

    map_id_table_start: int = 0x8907
    map_coord_table_start: int = 0x8947

    # Build up a list of all outdoor exits
    outdoor_exits: Connectors = []
    for region in outdoor_regions:
        for exit in map_data.nodes[region].exits:
            if exit.type == ConnectorType.BUILDING:
                outdoor_exits.append(exit)

    for conn in outdoor_exits:
        entr_data = ENTRANCE_DATA[OWEntrance(conn.name)]
        if conn.to_node.map_id is not None:
            # Write the new map id to the ROM table to redirect this entrance
            # Table entries are 4 bytes. The last 2 bytes are the little endian map id
            map_id_addr = map_id_table_start + (4 * entr_data.building_table_idx) + 2
            new_map_id = conn.to_node.map_id.to_bytes(2, byteorder="little")
            rom.write(map_id_addr, new_map_id)

            # Update the coord table. Determines where players end up on the
            # world map when leaving a building
            coord_idx = COORD_IDX_TABLE[conn.to_node.map_id]
            coord_id_addr = map_coord_table_start + (8 * coord_idx)
            rom.write(coord_id_addr, entr_data.coords.x.to_bytes(2, byteorder="little"),)
            rom.write(coord_id_addr + 2, entr_data.coords.y.to_bytes(2, byteorder="little"))
            rom.write(coord_id_addr + 4, entr_data.coords.z.to_bytes(2, byteorder="little"))
