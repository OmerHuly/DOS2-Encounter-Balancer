"""
DOS2 Encounter Balancer - Core Data Models
Data structures representing characters, encounters, party configurations, and balancing metrics.
Includes Race support (Human, Elf, Dwarf, Lizard, Undead, Creature, Demon, Automaton).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional


class Faction(str, Enum):
    MAGISTERS = "Magisters & Divine Order"
    VOIDWOKEN = "Voidwoken & Void Entities"
    UNDEAD = "Undead & Black Ring"
    BANDITS = "Bandits & Outlaws"
    BEASTS = "Wild Beasts & Elementals"
    DEMONS = "Demons & Cultists"
    AUTOMATONS = "Ancient Automatons"
    ANY = "Any / Mixed"


class Race(str, Enum):
    HUMAN = "Human"
    ELF = "Elf"
    DWARF = "Dwarf"
    LIZARD = "Lizard"
    UNDEAD = "Undead"
    UNDEAD_HUMAN = "Undead Human"
    UNDEAD_ELF = "Undead Elf"
    UNDEAD_DWARF = "Undead Dwarf"
    UNDEAD_LIZARD = "Undead Lizard"
    CREATURE = "Creature / Beast"
    DEMON = "Demon"
    AUTOMATON = "Automaton"


class EncounterType(str, Enum):
    STANDARD = "Standard Balanced Skirmish"
    BOSS = "Boss Encounter"
    SWARM = "Swarm Battle"
    ELITE = "Elite Strike Team"


class Archetype(str, Enum):
    TANK = "Tank / Juggernaut"
    FIGHTER = "Warrior / Bruiser"
    RANGER = "Ranger / Marksman"
    ROGUE = "Rogue / Assassin"
    MAGE = "Mage / Elementalist"
    BATTLEMAGE = "Battlemage / Inquisitor"
    CLERIC = "Cleric / Support"
    SUMMONER = "Summoner / Conjurer"
    BOSS = "Legendary Boss / Overlord"
    MINION = "Minion / Swarmer"


class DamageProfile(str, Enum):
    BALANCED = "Split (50% Physical / 50% Magical)"
    PURE_PHYSICAL = "Pure Physical (100% Physical)"
    PURE_MAGICAL = "Pure Magical (100% Magical)"
    PHYSICAL_LEAN = "Physical Lean (75% Physical / 25% Magical)"
    MAGICAL_LEAN = "Magical Lean (25% Physical / 75% Magical)"


class Difficulty(str, Enum):
    STORY = "Story (Easy, casual progression)"
    BALANCED = "Classic (Fair tactical challenge, engaging)"
    TACTICIAN = "Tactician (Challenging, punishing mistakes)"
    DEADLY = "Deadly / Boss Rush (Extremely difficult)"


@dataclass
class PartyConfig:
    level: int = 4
    party_size: int = 4
    is_lone_wolf: bool = False
    damage_profile: DamageProfile = DamageProfile.BALANCED
    difficulty: Difficulty = Difficulty.BALANCED
    notes: str = ""

    @property
    def total_ap_per_round(self) -> int:
        if self.is_lone_wolf:
            return self.party_size * 6
        return self.party_size * 4


@dataclass
class Skill:
    name: str
    school: str
    tier: str  # Racial, Novice, Adept, Expert, Master
    ap_cost: int
    damage_type: str  # Physical, Fire, Water, Air, Earth, Poison, Healing, Utility, Buff
    description: str
    status_applied: Optional[str] = None
    memory_cost: int = 1

    def __post_init__(self):
        if self.tier == "Racial":
            self.memory_cost = 0

    @property
    def is_innate(self) -> bool:
        return self.memory_cost == 0 or self.tier == "Racial"


@dataclass
class EnemyStats:
    vitality: int
    physical_armor: int
    magic_armor: int
    initiative: int
    ap_start: int = 4
    ap_max: int = 6
    ap_recovery: int = 4
    
    # Attributes
    strength: int = 10
    finesse: int = 10
    intelligence: int = 10
    constitution: int = 10
    memory: int = 10
    wits: int = 10

    # Combat Abilities
    combat_abilities: Dict[str, int] = field(default_factory=dict)
    talents: List[str] = field(default_factory=list)


@dataclass
class NPC:
    name: str
    title: str
    faction: Faction
    race: Race
    archetype: Archetype
    level: int
    stats: EnemyStats
    skills: List[Skill] = field(default_factory=list)
    equipment: str = "Standard Gear"
    ai_tactics: str = ""
    gm_notes: str = ""
    gm_template_id: str = ""  # Exact in-engine template ID in GM mode

    @property
    def total_ehp(self) -> int:
        """Effective Health Pool = Vitality + Physical Armor + Magic Armor"""
        return self.stats.vitality + self.stats.physical_armor + self.stats.magic_armor

    @property
    def max_memory_slots(self) -> int:
        """Maximum memorized skill slots based on Memory attribute (base 3 slots + 1 per point over 10)."""
        return 3 + max(0, self.stats.memory - 10)

    @property
    def used_memory_slots(self) -> int:
        """Total memory slots consumed by memorized skills (innate skills cost 0)."""
        return sum(s.memory_cost for s in self.skills)

    @property
    def innate_skills(self) -> List[Skill]:
        """Innate skills that do not require memory points (e.g. racial abilities)."""
        return [s for s in self.skills if s.is_innate]

    @property
    def memorized_skills(self) -> List[Skill]:
        """Skills that consume memory slots."""
        return [s for s in self.skills if not s.is_innate]


@dataclass
class EncounterBalanceAnalysis:
    party_total_ap: int
    enemy_total_ap: int
    ap_ratio_explanation: str
    party_expected_ehp: int
    enemy_total_ehp: int
    ehp_ratio_explanation: str
    damage_compatibility_rating: str
    damage_compatibility_notes: str
    overall_difficulty_assessment: str
    tactical_recommendations: List[str] = field(default_factory=list)
    tuning_dials: Dict[str, str] = field(default_factory=dict)


@dataclass
class Encounter:
    name: str
    encounter_type: EncounterType
    faction: Faction
    party_config: PartyConfig
    enemies: List[NPC] = field(default_factory=list)
    environmental_hazards: List[str] = field(default_factory=list)
    tactical_terrain: str = ""
    analysis: Optional[EncounterBalanceAnalysis] = None
    selected_race: Optional[Race] = None
