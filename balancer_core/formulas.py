"""
DOS2 Encounter Balancer - Mathematical Formulas & Scaling Engine
Faithful to Divinity: Original Sin 2 Definitive Edition mechanics.
Includes base vitality tables, exponential gear/armor progression,
archetype weighting, difficulty modifiers, and action economy calculations.
"""

import math
from typing import Dict, Tuple
from .models import Archetype, Difficulty, EnemyStats, PartyConfig, DamageProfile, Race


# Official DOS2 Definitive Edition Base Vitality by Level (1 to 25)
BASE_VITALITY_TABLE: Dict[int, int] = {
    1: 30,
    2: 45,
    3: 65,
    4: 85,
    5: 110,
    6: 135,
    7: 165,
    8: 200,
    9: 235,   # Leap 1
    10: 285,
    11: 345,
    12: 415,
    13: 560,  # Leap 2
    14: 685,
    15: 840,
    16: 1015, # Leap 3
    17: 1255,
    18: 1790, # Leap 4
    19: 2240,
    20: 2815,
    21: 3545,
    22: 4480,
    23: 5670,
    24: 7190,
    25: 9130,
}

# Baseline Total Armor (Physical + Magic combined) for normal gear at each level
BASE_TOTAL_ARMOR_TABLE: Dict[int, int] = {
    1: 30,
    2: 50,
    3: 85,
    4: 140,
    5: 210,
    6: 300,
    7: 420,
    8: 580,
    9: 780,
    10: 1050,
    11: 1400,
    12: 1900,
    13: 2700,
    14: 3600,
    15: 4900,
    16: 6600,
    17: 9000,
    18: 12500,
    19: 17000,
    20: 23000,
    21: 31000,
    22: 42000,
    23: 56000,
    24: 75000,
    25: 100000,
}

# Archetype Stat Multipliers: (PhysArmorRatio, MagicArmorRatio, VitalityRatio)
# Phys + Magic ratios are split from baseline total armor
ARCHETYPE_MULTIPLIERS: Dict[Archetype, Tuple[float, float, float]] = {
    Archetype.TANK:       (0.70, 0.30, 1.35),   # Heavy Physical Armor, low-mid Magic Armor, high HP
    Archetype.FIGHTER:    (0.58, 0.42, 1.15),   # Balanced frontline, slight physical lean
    Archetype.RANGER:     (0.50, 0.50, 0.90),   # 50/50 balanced armor, squishier HP
    Archetype.ROGUE:      (0.48, 0.44, 0.85),   # Lower armor, high initiative & evasion
    Archetype.MAGE:       (0.25, 0.75, 0.85),   # Very high Magic Armor, weak Physical Armor
    Archetype.BATTLEMAGE: (0.45, 0.55, 1.10),   # Hybrids with dual shields or close spells
    Archetype.CLERIC:     (0.45, 0.60, 1.15),   # High resilience, buff spells
    Archetype.SUMMONER:   (0.45, 0.45, 0.95),   # Moderate armor, relies on summons
    Archetype.BOSS:       (0.85, 0.85, 2.75),   # Huge dual armor pools, massive HP pool
    Archetype.MINION:     (0.18, 0.15, 0.38),   # Fragile cannon-fodder
}

# Difficulty Multipliers on HP & Armor
DIFFICULTY_MULTIPLIERS: Dict[Difficulty, float] = {
    Difficulty.STORY:     0.70,
    Difficulty.BALANCED:  1.00,
    Difficulty.TACTICIAN: 1.35,
    Difficulty.DEADLY:    1.65,
}


def get_base_vitality(level: int) -> int:
    """Retrieve or project the official base vitality for a given character level."""
    if level in BASE_VITALITY_TABLE:
        return BASE_VITALITY_TABLE[level]
    if level < 1:
        return BASE_VITALITY_TABLE[1]
    # Exponential projection beyond lvl 25 (growth factor ~1.28)
    highest_lvl = max(BASE_VITALITY_TABLE.keys())
    return int(BASE_VITALITY_TABLE[highest_lvl] * (1.28 ** (level - highest_lvl)))


def get_base_armor(level: int) -> int:
    """Retrieve or project the baseline total armor pool for a given level."""
    if level in BASE_TOTAL_ARMOR_TABLE:
        return BASE_TOTAL_ARMOR_TABLE[level]
    if level < 1:
        return BASE_TOTAL_ARMOR_TABLE[1]
    highest_lvl = max(BASE_TOTAL_ARMOR_TABLE.keys())
    return int(BASE_TOTAL_ARMOR_TABLE[highest_lvl] * (1.33 ** (level - highest_lvl)))


def calculate_attributes_for_level(
    level: int,
    archetype: Archetype,
    polymorph_points: int = 0,
    class_archetype: Optional[Archetype] = None
) -> Tuple[int, int, int, int, int, int]:
    """
    Distributes attribute points (STR, FIN, INT, CON, MEM, WIT) based on level, archetype, and Polymorph.
    Base is 10 for all attributes. Characters start with 3 attribute points at level 1,
    gain 2 attribute points per level gained (level >= 2), plus 1 free attribute point per
    point invested in Polymorph.
    """
    level_points = 3 + max(0, (level - 1) * 2) if level >= 1 else 0
    total_points = level_points + max(0, int(polymorph_points))
    
    str_pts, fin_pts, int_pts, con_pts, mem_pts, wit_pts = 0, 0, 0, 0, 0, 0
    
    # Reserve memory to allow adequate skill memorization
    if level >= 16:
        mem_pts = min(12, total_points // 4)
    elif level >= 9:
        mem_pts = min(6, total_points // 4)
    elif level >= 4:
        mem_pts = min(3, total_points // 5)
    
    remaining = total_points - mem_pts
    
    if archetype in (Archetype.TANK, Archetype.FIGHTER):
        str_pts = int(remaining * 0.65)
        con_pts = int(remaining * 0.25)
        wit_pts = remaining - (str_pts + con_pts)
    elif archetype in (Archetype.RANGER, Archetype.ROGUE):
        fin_pts = int(remaining * 0.65)
        wit_pts = int(remaining * 0.25)  # High initiative for rogues/archers
        con_pts = remaining - (fin_pts + wit_pts)
    elif archetype in (Archetype.MAGE, Archetype.SUMMONER):
        int_pts = int(remaining * 0.70)
        wit_pts = int(remaining * 0.15)
        con_pts = remaining - (int_pts + wit_pts)
    elif archetype in (Archetype.BATTLEMAGE, Archetype.CLERIC):
        int_pts = int(remaining * 0.45)
        str_pts = int(remaining * 0.30)
        con_pts = remaining - (int_pts + str_pts)
    elif archetype == Archetype.BOSS:
        # Bosses have inflated stats tailored to their combat specialization
        if class_archetype in (Archetype.ROGUE, Archetype.RANGER):
            fin_pts = int(remaining * 0.55)
            wit_pts = int(remaining * 0.20)
            con_pts = remaining - (fin_pts + wit_pts)
        elif class_archetype in (Archetype.MAGE, Archetype.SUMMONER):
            int_pts = int(remaining * 0.55)
            wit_pts = int(remaining * 0.20)
            con_pts = remaining - (int_pts + wit_pts)
        elif class_archetype in (Archetype.TANK, Archetype.FIGHTER):
            str_pts = int(remaining * 0.55)
            con_pts = int(remaining * 0.25)
            wit_pts = remaining - (str_pts + con_pts)
        else:
            primary = int(remaining * 0.50)
            str_pts = primary // 2
            int_pts = primary // 2
            con_pts = int(remaining * 0.30)
            wit_pts = remaining - (str_pts + int_pts + con_pts)
    elif archetype == Archetype.MINION:
        # Minions have very low attribute investment
        str_pts = int(remaining * 0.4)
        fin_pts = int(remaining * 0.4)
        con_pts = remaining - (str_pts + fin_pts)

    str_val = 10 + str_pts
    fin_val = 10 + fin_pts
    int_val = 10 + int_pts
    con_val = 10 + con_pts
    mem_val = 10 + mem_pts
    wit_val = 10 + wit_pts

    # Bosses receive an innate stat boost
    if archetype == Archetype.BOSS:
        str_val += 4
        fin_val += 4
        int_val += 4
        con_val += 6
        wit_val += 6
        mem_val += 4  # Ensures 6+ memory slots for boss spell arsenal

    return str_val, fin_val, int_val, con_val, mem_val, wit_val


def calculate_combat_abilities(
    level: int,
    archetype: Archetype,
    class_archetype: Optional[Archetype] = None
) -> Dict[str, int]:
    """Calculates combat ability points according to level, archetype, and class specialization."""
    points = max(2, level + 1)
    abilities: Dict[str, int] = {}
    
    if archetype == Archetype.TANK:
        abilities["Warfare"] = min(10, points // 2 + 1)
        abilities["Geomancer"] = max(1, points // 4)
        abilities["Retribution"] = max(1, points // 4)
    elif archetype == Archetype.FIGHTER:
        abilities["Warfare"] = min(10, int(points * 0.7))
        abilities["Polymorph"] = max(1, int(points * 0.3))
    elif archetype == Archetype.RANGER:
        abilities["Huntsman"] = min(10, points // 2 + 1)
        abilities["Ranged"] = max(1, points // 3)
    elif archetype == Archetype.ROGUE:
        abilities["Scoundrel"] = min(10, points // 2 + 1)
        abilities["Dual Wielding"] = max(1, points // 3)
    elif archetype == Archetype.MAGE:
        abilities["Pyrokinetic"] = min(10, points // 2)
        abilities["Geomancer"] = max(1, points // 3)
    elif archetype == Archetype.BATTLEMAGE:
        abilities["Warfare"] = max(1, points // 3)
        abilities["Aerotheurge"] = max(1, points // 3)
        abilities["Pyrokinetic"] = max(1, points // 4)
    elif archetype == Archetype.CLERIC:
        abilities["Hydrosophist"] = min(10, points // 2)
        abilities["Necromancer"] = max(1, points // 3)
    elif archetype == Archetype.SUMMONER:
        abilities["Summoning"] = min(10, points)
    elif archetype == Archetype.BOSS:
        if class_archetype == Archetype.ROGUE:
            abilities["Scoundrel"] = min(10, points // 2 + 2)
            abilities["Dual Wielding"] = max(2, points // 3)
            abilities["Polymorph"] = max(1, points // 4)
        elif class_archetype == Archetype.RANGER:
            abilities["Huntsman"] = min(10, points // 2 + 2)
            abilities["Ranged"] = max(2, points // 3)
        elif class_archetype in (Archetype.MAGE, Archetype.SUMMONER):
            abilities["Pyrokinetic"] = min(10, points // 2 + 1)
            abilities["Geomancer"] = max(2, points // 3)
            abilities["Aerotheurge"] = max(1, points // 4)
        else:
            abilities["Warfare"] = min(10, points // 2 + 2)
            abilities["Necromancer"] = max(2, points // 3)
    elif archetype == Archetype.MINION:
        abilities["Single-Handed"] = 1
        abilities["Warfare"] = 1
        
    return abilities


TALENT_LEVEL_MILESTONES = (1, 3, 8, 13, 18, 23, 28, 33)


def get_talent_points_for_level(level: int) -> int:
    """
    Returns the number of talent points awarded according to DOS2 Definitive Edition rules.
    1 talent point is awarded at levels 1, 3, 8, 13, 18, 23, 28, 33.
    """
    if level < 1:
        return 0
    return sum(1 for milestone in TALENT_LEVEL_MILESTONES if level >= milestone)


# Authentic DOS2 talent priority queues per archetype (ordered from earliest to latest acquisition)
ARCHETYPE_TALENTS: Dict[Archetype, List[str]] = {
    Archetype.TANK: [
        "Opportunist",       # Lvl 1
        "Picture of Health", # Lvl 3
        "Living Armor",      # Lvl 8
        "Comeback Kid",      # Lvl 13
        "The Pawn",          # Lvl 18
        "Executioner",       # Lvl 23
        "What a Rush",       # Lvl 28
        "Mnemonic",          # Lvl 33
    ],
    Archetype.FIGHTER: [
        "Opportunist",       # Lvl 1
        "Picture of Health", # Lvl 3
        "Executioner",       # Lvl 8
        "The Pawn",          # Lvl 13
        "Living Armor",      # Lvl 18
        "Hothead",           # Lvl 23
        "Comeback Kid",      # Lvl 28
        "What a Rush",       # Lvl 33
    ],
    Archetype.RANGER: [
        "Duck Duck Goose",   # Lvl 1
        "Hothead",           # Lvl 3
        "Executioner",       # Lvl 8
        "Elemental Ranger",  # Lvl 13
        "The Pawn",          # Lvl 18
        "Far Out Man",       # Lvl 23
        "What a Rush",       # Lvl 28
        "Mnemonic",          # Lvl 33
    ],
    Archetype.ROGUE: [
        "The Pawn",          # Lvl 1
        "Back-to-the-Wall",   # Lvl 3
        "Torturer",          # Lvl 8
        "Opportunist",       # Lvl 13
        "Executioner",       # Lvl 18
        "Hothead",           # Lvl 23
        "What a Rush",       # Lvl 28
        "Parry Master",      # Lvl 33
    ],
    Archetype.MAGE: [
        "Elemental Affinity",# Lvl 1
        "Torturer",          # Lvl 3
        "Savage Sortilege",  # Lvl 8
        "Far Out Man",       # Lvl 13
        "Hothead",           # Lvl 18
        "Living Armor",      # Lvl 23
        "The Pawn",          # Lvl 28
        "Mnemonic",          # Lvl 33
    ],
    Archetype.BATTLEMAGE: [
        "Elemental Affinity",# Lvl 1
        "Opportunist",       # Lvl 3
        "Torturer",          # Lvl 8
        "Savage Sortilege",  # Lvl 13
        "Picture of Health", # Lvl 18
        "Living Armor",      # Lvl 23
        "Executioner",       # Lvl 28
        "Hothead",           # Lvl 33
    ],
    Archetype.CLERIC: [
        "Elemental Affinity",# Lvl 1
        "Living Armor",      # Lvl 3
        "Torturer",          # Lvl 8
        "Picture of Health", # Lvl 13
        "Opportunist",       # Lvl 18
        "Far Out Man",       # Lvl 23
        "Hothead",           # Lvl 28
        "Comeback Kid",      # Lvl 33
    ],
    Archetype.SUMMONER: [
        "Elemental Affinity",# Lvl 1
        "Far Out Man",       # Lvl 3
        "The Pawn",          # Lvl 8
        "Hothead",           # Lvl 13
        "Torturer",          # Lvl 18
        "Living Armor",      # Lvl 23
        "Mnemonic",          # Lvl 28
        "Comeback Kid",      # Lvl 33
    ],
    Archetype.BOSS: [
        "Opportunist",       # Lvl 1
        "Walk It Off",       # Lvl 3 - Authentic DOS2 campaign boss talent: reduces status durations by 1 turn
        "Executioner",       # Lvl 8
        "Torturer",          # Lvl 13
        "Living Armor",      # Lvl 18
        "Picture of Health", # Lvl 23
        "Savage Sortilege",  # Lvl 28
        "Comeback Kid",      # Lvl 33
    ],
    Archetype.MINION: [
        "Opportunist",       # Lvl 1
        "The Pawn",          # Lvl 3
        "What a Rush",       # Lvl 8
        "Duck Duck Goose",   # Lvl 13
        "Hothead",           # Lvl 18
        "Comeback Kid",      # Lvl 23
        "Torturer",          # Lvl 28
        "Executioner",       # Lvl 33
    ],
}


def calculate_talents(
    archetype: Archetype,
    level: int,
    race: Optional[Race] = None
) -> List[str]:
    """
    Assigns appropriate DOS2 talents based on archetype, level, and race.
    1 talent point is awarded at levels 1, 3, 8, 13, 18, 23, 28, 33.
    Characters also receive their innate racial talent (such as 'Undead' for all Undead).
    """
    pts = get_talent_points_for_level(level)

    priority_list = ARCHETYPE_TALENTS.get(archetype, ARCHETYPE_TALENTS[Archetype.FIGHTER])
    if archetype == Archetype.BOSS:
        count = min(len(priority_list), max(3, pts + 1))
    elif archetype == Archetype.MINION:
        count = min(len(priority_list), max(0, pts - 1))
    else:
        count = min(len(priority_list), pts)

    talents = list(priority_list[:count])

    if race is not None:
        is_undead = race in (
            Race.UNDEAD,
            Race.UNDEAD_HUMAN,
            Race.UNDEAD_ELF,
            Race.UNDEAD_DWARF,
            Race.UNDEAD_LIZARD,
        )
        if is_undead and "Undead" not in talents:
            talents.append("Undead")

        if race in (Race.DWARF, Race.UNDEAD_DWARF) and "Sturdy (+10% HP)" not in talents:
            talents.append("Sturdy (+10% HP)")
        elif race in (Race.HUMAN, Race.UNDEAD_HUMAN) and "Ingenious (+Crit/+Init)" not in talents:
            talents.append("Ingenious (+Crit/+Init)")
        elif race in (Race.LIZARD, Race.UNDEAD_LIZARD) and "Sophisticated (+Resist)" not in talents:
            talents.append("Sophisticated (+Resist)")
        elif race in (Race.ELF, Race.UNDEAD_ELF) and "Corpse Eater" not in talents:
            talents.append("Corpse Eater")

    return talents


def calculate_enemy_stats(
    level: int,
    archetype: Archetype,
    difficulty: Difficulty = Difficulty.BALANCED,
    damage_profile: DamageProfile = DamageProfile.BALANCED,
    race: Race = Race.HUMAN,
    combat_abilities: Optional[Dict[str, int]] = None,
    class_archetype: Optional[Archetype] = None
) -> EnemyStats:
    """
    Computes exact, balanced HP, Physical Armor, and Magic Armor for an NPC,
    taking into account DOS2 Definitive Edition mechanics, archetype, race, party damage profile,
    and class specialization (e.g. Rogue Boss, Ranger Boss).
    """
    base_vit = get_base_vitality(level)
    base_arm = get_base_armor(level)
    
    phys_ratio, magic_ratio, vit_ratio = ARCHETYPE_MULTIPLIERS.get(
        archetype, (0.50, 0.50, 1.00)
    )
    diff_mult = DIFFICULTY_MULTIPLIERS.get(difficulty, 1.00)
    
    if combat_abilities is None:
        abilities = calculate_combat_abilities(level, archetype, class_archetype=class_archetype)
    else:
        abilities = dict(combat_abilities)

    polymorph_pts = abilities.get("Polymorph", 0)

    # Attribute calculations (including 1 free attribute point per point in Polymorph)
    str_val, fin_val, int_val, con_val, mem_val, wit_val = calculate_attributes_for_level(
        level, archetype, polymorph_points=polymorph_pts, class_archetype=class_archetype
    )
    
    # In DOS2, CON gives +7% Vitality per point above 10
    con_vitality_bonus = 1.0 + ((con_val - 10) * 0.07)
    
    calculated_vitality = int(base_vit * vit_ratio * con_vitality_bonus * diff_mult)
    
    # Racial stat bonuses
    if race in (Race.DWARF, Race.UNDEAD_DWARF):
        calculated_vitality = int(calculated_vitality * 1.10)  # Dwarf Sturdy passive (+10% Vitality)
    elif race in (Race.HUMAN, Race.UNDEAD_HUMAN):
        wit_val += 2  # Human Ingenious passive (+Wits)
        
    calculated_phys_armor = int(base_arm * phys_ratio * diff_mult)
    calculated_magic_armor = int(base_arm * magic_ratio * diff_mult)

    # Tactical tuning based on party damage profile:
    if damage_profile == DamageProfile.PURE_PHYSICAL:
        calculated_phys_armor = int(calculated_phys_armor * 1.15)
        calculated_magic_armor = int(calculated_magic_armor * 0.70)
    elif damage_profile == DamageProfile.PURE_MAGICAL:
        calculated_magic_armor = int(calculated_magic_armor * 1.15)
        calculated_phys_armor = int(calculated_phys_armor * 0.70)

    # Initiative = Wits + level bonus
    initiative = wit_val + (level // 2)
    if difficulty in (Difficulty.TACTICIAN, Difficulty.DEADLY):
        initiative += 2

    # AP Economy
    ap_start = 4
    ap_max = 6
    ap_recovery = 4
    if archetype == Archetype.BOSS:
        ap_start = 6
        ap_max = 6
        ap_recovery = 4  # GM mode limitation: cannot set more than 6 start AP and 4 AP recovery
        if "Perseverance" not in abilities:
            abilities["Perseverance"] = 3  # Anti-chain-CC buffer (restores 15% armor on CC recovery)
    elif archetype == Archetype.MINION:
        ap_start = 3
        ap_max = 4
        ap_recovery = 3

    talents = calculate_talents(archetype, level, race=race)

    return EnemyStats(
        vitality=max(15, calculated_vitality),
        physical_armor=max(0, calculated_phys_armor),
        magic_armor=max(0, calculated_magic_armor),
        initiative=initiative,
        ap_start=ap_start,
        ap_max=ap_max,
        ap_recovery=ap_recovery,
        strength=str_val,
        finesse=fin_val,
        intelligence=int_val,
        constitution=con_val,
        memory=mem_val,
        wits=wit_val,
        combat_abilities=abilities,
        talents=talents
    )


def sync_stats_with_combat_abilities(
    stats: EnemyStats,
    level: int,
    archetype: Archetype,
    race: Race = Race.HUMAN,
    difficulty: Difficulty = Difficulty.BALANCED,
    class_archetype: Optional[Archetype] = None
) -> None:
    """
    Synchronizes an EnemyStats object's attributes, vitality, and initiative with its
    current combat abilities (acknowledging free attribute points from Polymorph).
    """
    poly_pts = stats.combat_abilities.get("Polymorph", 0)
    str_val, fin_val, int_val, con_val, mem_val, wit_val = calculate_attributes_for_level(
        level, archetype, polymorph_points=poly_pts, class_archetype=class_archetype
    )
    if race in (Race.HUMAN, Race.UNDEAD_HUMAN):
        wit_val += 2
        
    stats.strength = str_val
    stats.finesse = fin_val
    stats.intelligence = int_val
    stats.constitution = con_val
    stats.memory = mem_val
    stats.wits = wit_val

    # Recalculate vitality if constitution changed
    base_vit = get_base_vitality(level)
    _, _, vit_ratio = ARCHETYPE_MULTIPLIERS.get(archetype, (0.50, 0.50, 1.00))
    diff_mult = DIFFICULTY_MULTIPLIERS.get(difficulty, 1.00)
    con_vitality_bonus = 1.0 + ((con_val - 10) * 0.07)
    calculated_vitality = int(base_vit * vit_ratio * con_vitality_bonus * diff_mult)
    if race in (Race.DWARF, Race.UNDEAD_DWARF):
        calculated_vitality = int(calculated_vitality * 1.10)
    stats.vitality = max(15, calculated_vitality)

    # Recalculate initiative
    initiative = wit_val + (level // 2)
    if difficulty in (Difficulty.TACTICIAN, Difficulty.DEADLY):
        initiative += 2
    stats.initiative = initiative


def estimate_party_ehp(party_config: PartyConfig) -> int:
    """Estimates the total effective health pool of the player party at their level."""
    base_vit = get_base_vitality(party_config.level)
    base_arm = get_base_armor(party_config.level)
    
    # A typical player character at level N has ~base_vit * 1.2 (some CON) + base_arm total
    single_player_ehp = int(base_vit * 1.25) + base_arm
    if party_config.is_lone_wolf:
        # Lone Wolf grants +100% Vitality, +60% Physical Armor, +60% Magic Armor
        single_player_ehp = int(single_player_ehp * 2.1)
        
    return single_player_ehp * party_config.party_size
