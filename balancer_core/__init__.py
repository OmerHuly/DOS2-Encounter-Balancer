"""
DOS2 Encounter Balancer - Package Initialization
"""

from .models import (
    PartyConfig,
    Encounter,
    EncounterType,
    Faction,
    Archetype,
    DamageProfile,
    Difficulty,
    Race,
    NPC,
    EnemyStats,
    Skill,
)
from .formulas import (
    calculate_enemy_stats,
    calculate_attributes_for_level,
    sync_stats_with_combat_abilities,
    calculate_talents,
    get_talent_points_for_level,
    estimate_party_ehp,
    get_base_vitality,
    get_base_armor,
)
from .bestiary import (
    BESTIARY,
    get_templates_by_faction,
    get_all_boss_templates,
    search_templates,
    find_template_by_name,
    create_custom_boss_template,
)
from .skills_db import SKILLS_DATABASE, get_skills_for_archetype
from .generator import (
    generate_encounter,
    analyze_encounter_balance,
    calculate_boss_scaling,
    BossScalingProfile,
    DefenseProfile,
    DEFENSE_PROFILES,
    auto_detect_defense_profile,
)
from .exporter import format_encounter_terminal, export_encounter_to_markdown

__all__ = [
    "PartyConfig",
    "Encounter",
    "EncounterType",
    "Faction",
    "Archetype",
    "DamageProfile",
    "Difficulty",
    "Race",
    "NPC",
    "EnemyStats",
    "Skill",
    "calculate_enemy_stats",
    "calculate_attributes_for_level",
    "sync_stats_with_combat_abilities",
    "calculate_talents",
    "get_talent_points_for_level",
    "estimate_party_ehp",
    "get_base_vitality",
    "get_base_armor",
    "BESTIARY",
    "get_templates_by_faction",
    "get_all_boss_templates",
    "search_templates",
    "find_template_by_name",
    "create_custom_boss_template",
    "SKILLS_DATABASE",
    "get_skills_for_archetype",
    "generate_encounter",
    "analyze_encounter_balance",
    "calculate_boss_scaling",
    "BossScalingProfile",
    "DefenseProfile",
    "DEFENSE_PROFILES",
    "auto_detect_defense_profile",
    "format_encounter_terminal",
    "export_encounter_to_markdown",
]

