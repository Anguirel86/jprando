import random

from jprando.jpmap import entrancerando, jpmap
from jprando.options.options import JPFlags, QoLFlags
from jprando.patches import basepatch, qolpatches
from jprando.rom import jprom


def patch_rom(flags: JPFlags, rom: jprom.JPRom):
    """
    Apply the requested patches to the provided JP ROM.

    This is the top level function of the randomizer.
    """
    basepatch.apply_ap_base_patch(rom, flags.player_id, flags.eggs_required)
    _apply_qol_patches(flags.qol_flags, rom)

def _apply_qol_patches(qol_flags: QoLFlags, rom: jprom.JPRom):
    """
    Apply the requested quality of life patches.
    """
    if qol_flags.passive_health_regen:
        qolpatches.patch_health_regen(rom)
    if qol_flags.infinite_lives:
        qolpatches.patch_infinite_lives(rom)
    if qol_flags.infinite_cattle_prod:
        qolpatches.patch_infinite_cattle_prod(rom)
    if qol_flags.infinite_ammo:
        qolpatches.patch_infinite_ammo(rom)
    if qol_flags.linked_gates:
        qolpatches.patch_gates_open_together(rom)


def main():
    """
    Test main
    """
    rom = jprom.JPRom("./jprando/jp-usa.sfc")
    flags = JPFlags()
    flags.qol_flags.infinite_ammo = True
    flags.qol_flags.infinite_lives = True
    flags.qol_flags.infinite_cattle_prod = True
    flags.qol_flags.passive_health_regen = True
    flags.qol_flags.linked_gates = True

    map_data: jpmap.MapData = jpmap.get_default_map()
    rng = random.Random()
    jpmap.shuffle_map(map_data, rng)
    entrancerando.apply_entrance_rando(rom, map_data)
    _apply_qol_patches(flags.qol_flags, rom)
    rom.write_to_file("./jprando/jp-mod.sfc")


if __name__ == "__main__":
    main()
