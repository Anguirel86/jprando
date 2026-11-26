from random import Random
from typing import Protocol

from jprando.jpmap import jpmap


class ItemFillException(Exception):
    pass

class ItemFill(Protocol):
    """Protocol interface for item fill algorithms."""
    def place_items(self, rng: Random, map_data: jpmap.MapData) -> bool:
        ...

def _get_key_item_list() -> jpmap.Rewards:
    """
    Helper function to get the list of key items that can block other locations.
    """
    kis: jpmap.Rewards = list(jpmap.Battery)
    kis.extend(list(jpmap.IDCard))
    return kis

def _get_filler_item_list() -> list[jpmap.Reward]:
    """
    Get a list of filler items to complete the treasure map.
    """
    # Currently the only filler item is eggs
    filler = []
    filler.extend([jpmap.Item.EGG] * 18)
    return filler

class AssumedItemFill:
    """
    Implements the Assumed Fill item placement algorithm.

    Assumed Fill essentially works backwards when placing items in the world.  The user
    is assumed to have access to all other progression items except the one being placed.
    This ensures no item can lock itself.

    This process is repeated until all items have been placed.
    """
    _num_attempts: int = 25;  # TODO: Make this configurable?

    def place_items(self, rng: Random, map_data: jpmap.MapData) -> bool:
        """
        Run the Assumed Fill algorithm to place items.

        Top level public function to run the fill and handle retry logic if necessary.
        """
        counter: int = 0
        fill_success: bool = False
        key_item_list: jpmap.Rewards = _get_key_item_list()
        while not fill_success and (counter < self._num_attempts):
            # Clear out the existing treasure map
            for loc in map_data.treasure_map:
                map_data.treasure_map[loc] = None

            fill_success = self._place_items(rng, map_data, key_item_list)
            counter += 1

        if fill_success:
            # Place filler items
            filler = _get_filler_item_list()

            empty_locs = [x for x in map_data.treasure_map if map_data.treasure_map[x] is None]
            rng.shuffle(filler) # It's all eggs, so not strictly necessary yet
                                # but this matters if we add in the unnecessary batteries later
            if len(filler) != len(empty_locs):
                raise ItemFillException("Not enough locations left for filler items")

            for loc, item in zip(empty_locs, filler, strict=True):
                map_data.treasure_map[loc] = item


        return fill_success

    def _place_items(self, rng: Random, map_data: jpmap.MapData, key_item_list: jpmap.Rewards) -> bool:
        """
        Internal fill implementation.  Runs a single round of Assumed Fill.
        """
        # Create a copy of the key item list and shuffle it
        if key_item_list is None:
            raise ItemFillException("No key item list provided")

        local_ki_list = [x for x in key_item_list]
        rng.shuffle(local_ki_list)

        while len(local_ki_list) > 0:
            # Pick the next key item to place
            current_item = local_ki_list.pop()

            # Sweep the map for valid item placement locations
            results = jpmap.sweep_map(map_data, start_inven=local_ki_list)

            # Filter out locations that are already populated
            empty_locs = [x for x in results.reachable_locations if map_data.treasure_map[x] is None]
            if not empty_locs:
                # This layout is invalid - No available locations to place the item
                break

            # Choose a random location from the list and place the item
            loc = rng.choice(empty_locs)
            map_data.treasure_map[loc] = current_item

        # If there are no key items left, we succeeded.
        return len(local_ki_list) == 0
