"""
DOS2 Encounter Balancer - Local Web UI Dashboard
Zero-dependency local HTTP server and dark fantasy GM dashboard.
"""

import json
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from .models import (
    PartyConfig,
    Encounter,
    EncounterType,
    Faction,
    Race,
    Archetype,
    DamageProfile,
    Difficulty,
    NPC,
)
from .bestiary import (
    BESTIARY,
    get_templates_by_faction,
    get_all_boss_templates,
    find_template_by_name,
)
from .skills_db import SKILLS_DATABASE
from .generator import (
    generate_encounter,
    build_custom_encounter,
    CustomEnemySpec,
    ROLE_DEFAULTS,
    DEFENSE_PROFILES,
)
from .exporter import (
    format_encounter_terminal,
    format_encounter_markdown,
    export_encounter_to_markdown,
)


ALL_RACE_CANDIDATES = [
    ("Human Only", Race.HUMAN),
    ("Elf Only", Race.ELF),
    ("Dwarf Only", Race.DWARF),
    ("Lizard Only", Race.LIZARD),
    ("Undead (All Undead Variants)", Race.UNDEAD),
    ("Undead Dwarf Only", Race.UNDEAD_DWARF),
    ("Undead Elf Only", Race.UNDEAD_ELF),
    ("Undead Lizard Only", Race.UNDEAD_LIZARD),
    ("Undead Human Only", Race.UNDEAD_HUMAN),
    ("Demon Only", Race.DEMON),
    ("Creature / Beast Only", Race.CREATURE),
    ("Automaton Only", Race.AUTOMATON),
]


def _infer_combat_role_from_template(tpl: Any) -> str:
    if tpl.archetype not in (Archetype.BOSS, Archetype.MINION):
        return tpl.archetype.name
    eq_l = tpl.equipment.lower()
    tac_l = tpl.ai_tactics.lower()
    nm_l = tpl.name.lower()
    if any(k in eq_l or k in tac_l or k in nm_l for k in ["dagger", "rogue", "assassin", "shadowblade", "cutthroat"]):
        return Archetype.ROGUE.name
    if any(k in eq_l or k in tac_l or k in nm_l for k in ["bow", "crossbow", "ranger", "marksman", "hunter"]):
        return Archetype.RANGER.name
    if any(k in eq_l or k in tac_l or k in nm_l for k in ["wand", "staff", "mage", "wizard", "pyro", "cryo", "elementalist"]):
        return Archetype.MAGE.name
    if any(k in eq_l or k in tac_l or k in nm_l for k in ["shield", "bulwark", "tank", "guardian"]):
        return Archetype.TANK.name
    return Archetype.FIGHTER.name


def get_valid_races_for_faction(faction: Faction) -> List[Dict[str, Optional[str]]]:
    """Returns the valid race filter options for a given faction (matching interactive CLI behavior)."""
    if faction == Faction.ANY:
        valid = [
            {"label": label, "value": r.name}
            for label, r in ALL_RACE_CANDIDATES
            if r not in (Race.DEMON, Race.CREATURE, Race.AUTOMATON)
        ]
        return [{"label": "Any / Multi-racial", "value": "ANY"}] + valid

    faction_templates = get_templates_by_faction(faction)
    distinct_races = {t.race for t in faction_templates}
    if len(distinct_races) <= 1:
        return []

    valid = [
        {"label": label, "value": r.name}
        for label, r in ALL_RACE_CANDIDATES
        if len(get_templates_by_faction(faction, race=r)) > 0
    ]
    if not valid:
        return []
    return [{"label": "Any / Multi-racial", "value": "ANY"}] + valid


def get_gui_metadata() -> Dict[str, Any]:
    """Builds metadata payload for initializing the Web UI controls."""
    factions = [
        {"value": "ANY", "label": "Random / Mixed Factions"},
        {"value": Faction.MAGISTERS.name, "label": Faction.MAGISTERS.value},
        {"value": Faction.VOIDWOKEN.name, "label": Faction.VOIDWOKEN.value},
        {"value": Faction.UNDEAD.name, "label": Faction.UNDEAD.value},
        {"value": Faction.BANDITS.name, "label": Faction.BANDITS.value},
        {"value": Faction.BEASTS.name, "label": Faction.BEASTS.value},
        {"value": Faction.DEMONS.name, "label": Faction.DEMONS.value},
        {"value": Faction.AUTOMATONS.name, "label": Faction.AUTOMATONS.value},
    ]

    builder_factions = [f for f in factions if f["value"] != "ANY"]

    builder_races = [
        {"value": r.name, "label": r.value}
        for r in [
            Race.HUMAN,
            Race.ELF,
            Race.DWARF,
            Race.LIZARD,
            Race.UNDEAD_HUMAN,
            Race.UNDEAD_ELF,
            Race.UNDEAD_DWARF,
            Race.UNDEAD_LIZARD,
            Race.UNDEAD,
            Race.CREATURE,
            Race.DEMON,
            Race.AUTOMATON,
        ]
    ]

    combat_roles = [
        {
            "value": arch.name,
            "label": arch.value,
            "default_equipment": ROLE_DEFAULTS[arch]["equipment"],
        }
        for arch in [
            Archetype.FIGHTER,
            Archetype.RANGER,
            Archetype.ROGUE,
            Archetype.MAGE,
            Archetype.TANK,
            Archetype.BATTLEMAGE,
            Archetype.CLERIC,
            Archetype.SUMMONER,
        ]
    ]

    unit_tiers = [
        {"value": "NORMAL", "label": "Normal Unit (Standard Combatant)"},
        {"value": "MINION", "label": "Minion / Swarmer (Low HP Cannon-Fodder)"},
        {"value": "ELITE", "label": "Elite Champion (+Armor & Perseverance)"},
        {"value": "BOSS", "label": "Boss / Commander (High AP & Aura)"},
    ]

    level_offsets = [
        {"value": -2, "label": "-2 Levels (Underleveled)"},
        {"value": -1, "label": "-1 Level (Slightly Weaker)"},
        {"value": 0, "label": "0 (Same as Party Level)"},
        {"value": 1, "label": "+1 Level (Veteran Threat)"},
        {"value": 2, "label": "+2 Levels (Overleveled Threat)"},
    ]

    faction_races = {}
    for f in Faction:
        faction_races[f.name] = get_valid_races_for_faction(f)

    encounter_types = [
        {"value": "RANDOM", "label": "Random"},
        {"value": EncounterType.STANDARD.name, "label": EncounterType.STANDARD.value},
        {"value": EncounterType.BOSS.name, "label": EncounterType.BOSS.value},
        {"value": EncounterType.SWARM.name, "label": EncounterType.SWARM.value},
        {"value": EncounterType.ELITE.name, "label": EncounterType.ELITE.value},
    ]

    builder_encounter_types = [
        {"value": "AUTO", "label": "Auto-Detect (1 Enemy = Boss Encounter)"},
        {"value": EncounterType.STANDARD.name, "label": EncounterType.STANDARD.value},
        {"value": EncounterType.BOSS.name, "label": EncounterType.BOSS.value},
        {"value": EncounterType.SWARM.name, "label": EncounterType.SWARM.value},
        {"value": EncounterType.ELITE.name, "label": EncounterType.ELITE.value},
    ]

    damage_profiles = [
        {"value": dp.name, "label": dp.value}
        for dp in [
            DamageProfile.BALANCED,
            DamageProfile.PURE_PHYSICAL,
            DamageProfile.PURE_MAGICAL,
            DamageProfile.PHYSICAL_LEAN,
            DamageProfile.MAGICAL_LEAN,
        ]
    ]

    difficulties = [
        {"value": diff.name, "label": diff.value}
        for diff in [
            Difficulty.BALANCED,
            Difficulty.TACTICIAN,
            Difficulty.STORY,
            Difficulty.DEADLY,
        ]
    ]

    defense_profiles = [
        {"value": "auto", "label": "Thematic Auto-Detect (Authentic bestiary resistances & weaknesses)"},
        {"value": "balanced", "label": "Balanced (Standard 1:1 Physical & Magic Armor, no vulnerabilities)"},
        {"value": "ironclad", "label": "Ironclad Juggernaut (High Phys Armor / Low Magic Armor / Air Weakness)"},
        {"value": "arcane", "label": "Arcane Ward / Spellweaver (High Magic Armor / Low Phys Armor / Phys Weakness)"},
        {"value": "pyro", "label": "Volcanic / Fire-Forged (Fire Absorption / Water & Cryo Weakness)"},
        {"value": "cryo", "label": "Glacial Frost-Bound (Water & Air Resistant / Fire Weakness)"},
        {"value": "venom", "label": "Venomous / Undead (Poison Absorption / Fire Weakness)"},
        {"value": "storm", "label": "Storm Conduit (Air Immune / Earth Weakness)"},
        {"value": "troll", "label": "Troll Hide (Massive Phys Armor / Earth Res / Fire Weakness suppresses regen)"},
    ]

    boss_templates = [
        {
            "name": b.name,
            "gm_template_id": b.gm_template_id,
            "faction": b.faction.name,
            "faction_label": b.faction.value,
            "race": b.race.name,
            "race_label": b.race.value,
            "archetype": b.archetype.value,
        }
        for b in get_all_boss_templates()
    ]

    all_templates = [
        {
            "name": t.name,
            "gm_template_id": t.gm_template_id,
            "faction": t.faction.name,
            "faction_label": t.faction.value,
            "race": t.race.name,
            "race_label": t.race.value,
            "archetype": t.archetype.value,
            "archetype_key": t.archetype.name,
            "combat_role_key": _infer_combat_role_from_template(t),
            "default_tier": "BOSS" if t.archetype == Archetype.BOSS else ("MINION" if t.archetype == Archetype.MINION else "NORMAL"),
            "equipment": t.equipment,
            "can_be_boss": t.can_be_boss or t.archetype.name == "BOSS",
        }
        for t in BESTIARY
    ]

    all_skills = [
        {
            "name": s.name,
            "school": s.school,
            "tier": s.tier,
            "ap_cost": s.ap_cost,
            "damage_type": s.damage_type,
            "description": s.description,
            "status_applied": s.status_applied,
            "memory_cost": s.memory_cost,
            "is_innate": s.is_innate,
            "required_abilities": s.required_abilities,
            "requirements_display": s.requirements_display,
        }
        for s in SKILLS_DATABASE
    ]

    canonical_schools = [
        "Warfare", "Huntsman", "Scoundrel", "Pyrokinetic", "Hydrosophist",
        "Aerotheurge", "Geomancer", "Necromancer", "Polymorph", "Summoning", "Special"
    ]
    found_schools = {s.school for s in SKILLS_DATABASE}
    skill_schools = [sch for sch in canonical_schools if sch in found_schools] + sorted(list(found_schools - set(canonical_schools)))

    return {
        "factions": factions,
        "builder_factions": builder_factions,
        "builder_races": builder_races,
        "combat_roles": combat_roles,
        "unit_tiers": unit_tiers,
        "level_offsets": level_offsets,
        "faction_races": faction_races,
        "encounter_types": encounter_types,
        "builder_encounter_types": builder_encounter_types,
        "damage_profiles": damage_profiles,
        "difficulties": difficulties,
        "defense_profiles": defense_profiles,
        "boss_templates": boss_templates,
        "all_templates": all_templates,
        "all_skills": all_skills,
        "skill_schools": skill_schools,
    }


def serialize_npc(npc: NPC, index: int, party_level: Optional[int] = None) -> Dict[str, Any]:
    """Serializes an NPC dataclass to a JSON-ready dictionary."""
    if npc.archetype == Archetype.BOSS:
        unit_tier_key = "BOSS"
    elif npc.archetype == Archetype.MINION:
        unit_tier_key = "MINION"
    elif "Champion" in npc.title or npc.name.startswith("Elite "):
        unit_tier_key = "ELITE"
    else:
        unit_tier_key = "NORMAL"

    base_name = npc.name[6:] if (npc.name.startswith("Elite ") and not find_template_by_name(npc.name)) else npc.name
    matched_tpl = find_template_by_name(base_name)

    if npc.archetype not in (Archetype.BOSS, Archetype.MINION):
        combat_role_key = npc.archetype.name
    elif matched_tpl is not None:
        combat_role_key = _infer_combat_role_from_template(matched_tpl)
    elif npc.stats.intelligence > npc.stats.strength and npc.stats.intelligence > npc.stats.finesse:
        combat_role_key = Archetype.MAGE.name
    elif npc.stats.finesse > npc.stats.strength:
        combat_role_key = Archetype.ROGUE.name if "dagger" in npc.equipment.lower() else Archetype.RANGER.name
    else:
        combat_role_key = Archetype.FIGHTER.name

    level_offset = max(-2, min(2, npc.level - party_level)) if party_level is not None else 0

    return {
        "index": index,
        "name": npc.name,
        "base_name": base_name,
        "template_name": matched_tpl.name if matched_tpl else "CUSTOM",
        "title": npc.title,
        "faction": npc.faction.value,
        "faction_key": npc.faction.name,
        "race": npc.race.value,
        "race_key": npc.race.name,
        "archetype": npc.archetype.value,
        "archetype_key": npc.archetype.name,
        "combat_role_key": combat_role_key,
        "unit_tier_key": unit_tier_key,
        "level": npc.level,
        "level_offset": level_offset,
        "gm_template_id": npc.gm_template_id,
        "equipment": npc.equipment,
        "ai_tactics": npc.ai_tactics,
        "gm_notes": npc.gm_notes,
        "defense_theme": npc.defense_theme,
        "format_resistances": npc.format_resistances,
        "total_ehp": npc.total_ehp,
        "max_memory_slots": npc.max_memory_slots,
        "used_memory_slots": npc.used_memory_slots,
        "stats": {
            "vitality": npc.stats.vitality,
            "physical_armor": npc.stats.physical_armor,
            "magic_armor": npc.stats.magic_armor,
            "initiative": npc.stats.initiative,
            "ap_start": npc.stats.ap_start,
            "ap_max": npc.stats.ap_max,
            "ap_recovery": npc.stats.ap_recovery,
            "strength": npc.stats.strength,
            "finesse": npc.stats.finesse,
            "intelligence": npc.stats.intelligence,
            "constitution": npc.stats.constitution,
            "memory": npc.stats.memory,
            "wits": npc.stats.wits,
            "combat_abilities": npc.stats.combat_abilities,
            "talents": npc.stats.talents,
            "resistances": npc.stats.resistances,
        },
        "skills": [
            {
                "name": s.name,
                "school": s.school,
                "tier": s.tier,
                "ap_cost": s.ap_cost,
                "damage_type": s.damage_type,
                "description": s.description,
                "status_applied": s.status_applied,
                "memory_cost": s.memory_cost,
                "is_innate": s.is_innate,
                "required_abilities": s.required_abilities,
                "requirements_display": s.requirements_display,
            }
            for s in npc.skills
        ],
    }


def serialize_encounter(encounter: Encounter) -> Dict[str, Any]:
    """Serializes an Encounter into a complete JSON payload including Markdown and Terminal text."""
    p = encounter.party_config
    a = encounter.analysis

    return {
        "name": encounter.name,
        "encounter_type": encounter.encounter_type.value,
        "encounter_type_key": encounter.encounter_type.name,
        "faction": encounter.faction.value,
        "faction_key": encounter.faction.name,
        "selected_race": encounter.selected_race.value if encounter.selected_race else None,
        "minion_count": encounter.minion_count,
        "boss_name": encounter.boss_name,
        "tactical_terrain": encounter.tactical_terrain,
        "environmental_hazards": encounter.environmental_hazards,
        "party_config": {
            "level": p.level,
            "party_size": p.party_size,
            "is_lone_wolf": p.is_lone_wolf,
            "damage_profile": p.damage_profile.value,
            "difficulty": p.difficulty.value,
            "total_ap_per_round": p.total_ap_per_round,
        },
        "analysis": {
            "party_total_ap": a.party_total_ap,
            "enemy_total_ap": a.enemy_total_ap,
            "ap_ratio_explanation": a.ap_ratio_explanation,
            "party_expected_ehp": a.party_expected_ehp,
            "enemy_total_ehp": a.enemy_total_ehp,
            "ehp_ratio_explanation": a.ehp_ratio_explanation,
            "damage_compatibility_rating": a.damage_compatibility_rating,
            "damage_compatibility_notes": a.damage_compatibility_notes,
            "overall_difficulty_assessment": a.overall_difficulty_assessment,
            "tactical_recommendations": a.tactical_recommendations,
            "tuning_dials": a.tuning_dials,
        } if a else None,
        "enemies": [serialize_npc(npc, idx, party_level=p.level) for idx, npc in enumerate(encounter.enemies, 1)],
        "markdown": format_encounter_markdown(encounter),
        "terminal_text": format_encounter_terminal(encounter),
    }


def build_encounter_from_payload(payload: Dict[str, Any]) -> Encounter:
    """Constructs and generates an Encounter from a Web UI JSON request payload."""
    level = max(1, min(25, int(payload.get("level", 4))))
    party_size = max(1, min(4, int(payload.get("party_size", 4))))
    is_lone_wolf = bool(payload.get("is_lone_wolf", False)) and party_size in (1, 2)

    dp_key = payload.get("damage_profile", "BALANCED")
    damage_profile = DamageProfile[dp_key] if dp_key in DamageProfile.__members__ else DamageProfile.BALANCED

    diff_key = payload.get("difficulty", "BALANCED")
    difficulty = Difficulty[diff_key] if diff_key in Difficulty.__members__ else Difficulty.BALANCED

    enc_type_key = payload.get("encounter_type", "RANDOM")
    encounter_type = (
        EncounterType[enc_type_key]
        if enc_type_key in EncounterType.__members__
        else None
    )

    fac_key = payload.get("faction", "ANY")
    faction = Faction[fac_key] if fac_key in Faction.__members__ else Faction.ANY

    race_key = payload.get("race", "ANY")
    race = Race[race_key] if (race_key and race_key in Race.__members__) else None

    boss_template = payload.get("boss_template")
    if isinstance(boss_template, str):
        boss_template = boss_template.strip() or None

    minion_count = payload.get("minion_count")
    if minion_count is not None and minion_count != "":
        minion_count = max(0, min(5, int(minion_count)))
    else:
        minion_count = None

    defense_profile = payload.get("defense_profile", "auto") or "auto"
    seed = payload.get("seed")
    if seed is not None and seed != "":
        seed = int(seed)
    else:
        seed = None

    # If Solo Boss (0 minions) and explicit boss template chosen, adopt boss's inherent faction & race
    if encounter_type == EncounterType.BOSS and minion_count == 0 and boss_template:
        tpl = find_template_by_name(boss_template)
        if tpl:
            faction = tpl.faction
            race = tpl.race

    party_cfg = PartyConfig(
        level=level,
        party_size=party_size,
        is_lone_wolf=is_lone_wolf,
        damage_profile=damage_profile,
        difficulty=difficulty,
    )

    return generate_encounter(
        party_config=party_cfg,
        encounter_type=encounter_type,
        faction=faction,
        race=race,
        boss_template=boss_template,
        minion_count=minion_count,
        defense_profile=defense_profile,
        seed=seed,
    )


def build_custom_encounter_from_payload(payload: Dict[str, Any]) -> Encounter:
    """Constructs and balances a custom Encounter from an Interactive Encounter Builder JSON payload."""
    level = max(1, min(25, int(payload.get("level", 4))))
    party_size = max(1, min(4, int(payload.get("party_size", 4))))
    is_lone_wolf = bool(payload.get("is_lone_wolf", False)) and party_size in (1, 2)

    dp_key = payload.get("damage_profile", "BALANCED")
    damage_profile = DamageProfile[dp_key] if dp_key in DamageProfile.__members__ else DamageProfile.BALANCED

    diff_key = payload.get("difficulty", "BALANCED")
    difficulty = Difficulty[diff_key] if diff_key in Difficulty.__members__ else Difficulty.BALANCED

    enc_type_raw = payload.get("encounter_type", "AUTO")
    seed = payload.get("seed")
    if seed is not None and seed != "":
        seed = int(seed)
    else:
        seed = None

    party_cfg = PartyConfig(
        level=level,
        party_size=party_size,
        is_lone_wolf=is_lone_wolf,
        damage_profile=damage_profile,
        difficulty=difficulty,
    )

    enemy_specs = payload.get("enemies", [])
    return build_custom_encounter(
        party_config=party_cfg,
        enemy_specs=enemy_specs,
        encounter_type=enc_type_raw,
        seed=seed,
    )



HTML_DASHBOARD = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DOS2: Definitive Edition - GM Encounter Balancer</title>
<style>
  :root {
    --bg-deep: #0d0c0b;
    --bg-panel: #161412;
    --bg-card: #1d1a17;
    --bg-input: #110f0d;
    --border-gold: #6e552b;
    --border-gold-bright: #c89d4c;
    --border-subtle: #2e2822;
    --text-main: #e8dec8;
    --text-muted: #9e9178;
    --text-gold: #e5b95c;
    --accent-crimson: #9e2a2b;
    --accent-crimson-bright: #c93b3b;
    --vit-red: #c93636;
    --vit-bg: #3b1313;
    --phys-gold: #b89c4e;
    --phys-bg: #383018;
    --mag-blue: #3a89c9;
    --mag-bg: #132a3d;
    --ap-green: #52b788;
    --innate-purple: #9d65c9;
    --font-serif: "Cinzel", "Palatino Linotype", "Book Antiqua", Georgia, serif;
    --font-sans: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    --font-mono: "Consolas", "Cascadia Mono", monospace;
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    background-color: var(--bg-deep);
    background-image: radial-gradient(circle at 50% 0%, #241d15 0%, #0d0c0b 75%);
    color: var(--text-main);
    font-family: var(--font-sans);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  /* Header Banner */
  header {
    background: linear-gradient(180deg, #1f1914 0%, #120f0c 100%);
    border-bottom: 2px solid var(--border-gold);
    padding: 14px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.7);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .brand-emblem {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    border: 2px solid var(--border-gold-bright);
    background: radial-gradient(circle, #8a2424 0%, #2b0909 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: var(--font-serif);
    font-weight: bold;
    color: var(--text-gold);
    font-size: 18px;
    box-shadow: 0 0 12px rgba(200, 157, 76, 0.35);
  }

  .brand-titles h1 {
    font-family: var(--font-serif);
    font-size: 1.25rem;
    color: var(--text-gold);
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  .brand-titles p {
    font-size: 0.78rem;
    color: var(--text-muted);
    letter-spacing: 0.4px;
  }

  .header-actions {
    display: flex;
    gap: 10px;
    align-items: center;
  }

  /* Buttons */
  .btn {
    cursor: pointer;
    font-family: var(--font-serif);
    font-weight: 600;
    font-size: 0.85rem;
    letter-spacing: 0.6px;
    padding: 9px 16px;
    border-radius: 4px;
    border: 1px solid var(--border-gold);
    background: linear-gradient(180deg, #2b231b 0%, #1a1510 100%);
    color: var(--text-main);
    transition: all 0.15s ease;
    display: inline-flex;
    align-items: center;
    gap: 7px;
    white-space: nowrap;
  }

  .btn:hover {
    border-color: var(--border-gold-bright);
    color: #fff;
    background: linear-gradient(180deg, #382d22 0%, #241d16 100%);
    box-shadow: 0 0 10px rgba(200, 157, 76, 0.25);
  }

  .btn:active {
    transform: translateY(1px);
  }

  .btn-primary {
    background: linear-gradient(180deg, #a32c2c 0%, #681717 100%);
    border-color: #d46559;
    color: #fff;
    font-size: 0.88rem;
    padding: 11px 14px;
    width: 100%;
    justify-content: center;
    text-transform: uppercase;
    white-space: nowrap;
    box-shadow: 0 4px 12px rgba(158, 42, 43, 0.4);
  }

  .btn-primary:hover {
    background: linear-gradient(180deg, #bf3636 0%, #7d1c1c 100%);
    border-color: #f09c67;
    box-shadow: 0 0 15px rgba(201, 59, 59, 0.6);
  }

  /* Main Layout */
  .workspace {
    display: grid;
    grid-template-columns: 370px minmax(0, 1fr);
    align-items: start;
    gap: 22px;
    padding: 22px 28px;
    max-width: 1720px;
    width: 100%;
    margin: 0 auto;
    flex: 1;
  }

  /* Left Configuration Panel */
  .config-panel {
    width: 370px;
    max-width: 370px;
    min-width: 0;
    background: var(--bg-panel);
    border: 1px solid var(--border-gold);
    border-radius: 6px;
    padding: 20px;
    position: sticky;
    top: 86px;
    max-height: calc(100vh - 106px);
    overflow-y: auto;
    overflow-x: hidden;
    scrollbar-width: thin;
    scrollbar-color: var(--border-gold) var(--bg-input);
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.6);
  }

  @media (max-width: 1100px) {
    .workspace {
      grid-template-columns: 1fr;
    }
    .config-panel {
      width: 100%;
      max-width: 100%;
      position: static;
      max-height: none;
      overflow-y: visible;
    }
  }

  .panel-section-title {
    font-family: var(--font-serif);
    font-size: 0.92rem;
    color: var(--text-gold);
    text-transform: uppercase;
    letter-spacing: 1px;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 6px;
    margin-bottom: 14px;
    margin-top: 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .panel-section-title:first-child {
    margin-top: 0;
  }

  .form-group {
    margin-bottom: 13px;
    min-width: 0;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }

  label {
    display: block;
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-bottom: 5px;
    font-weight: 600;
  }

  select, input[type="number"], input[type="text"] {
    width: 100%;
    max-width: 100%;
    min-width: 0;
    background: var(--bg-input);
    border: 1px solid #3d342b;
    color: var(--text-main);
    padding: 8px 10px;
    border-radius: 4px;
    font-size: 0.86rem;
    font-family: var(--font-sans);
    text-overflow: ellipsis;
    overflow: hidden;
    white-space: nowrap;
    transition: border-color 0.15s;
  }

  select:focus, input:focus {
    outline: none;
    border-color: var(--border-gold-bright);
  }

  .checkbox-row {
    display: flex;
    align-items: center;
    gap: 9px;
    padding: 8px 10px;
    background: rgba(200, 157, 76, 0.07);
    border: 1px dashed var(--border-gold);
    border-radius: 4px;
    margin-bottom: 12px;
  }

  .checkbox-row input[type="checkbox"] {
    width: 16px;
    height: 16px;
    accent-color: var(--border-gold-bright);
    cursor: pointer;
  }

  .checkbox-row label {
    margin: 0;
    color: var(--text-gold);
    cursor: pointer;
    font-size: 0.84rem;
  }

  .sub-panel {
    background: rgba(158, 42, 43, 0.08);
    border: 1px solid rgba(200, 157, 76, 0.4);
    border-radius: 5px;
    padding: 13px;
    margin-bottom: 14px;
  }

  .sub-panel-header {
    font-family: var(--font-serif);
    font-size: 0.82rem;
    color: #f09c67;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 10px;
    font-weight: bold;
  }

  .hint-badge {
    font-size: 0.74rem;
    color: var(--text-muted);
    background: rgba(255, 255, 255, 0.04);
    border-left: 3px solid var(--border-gold);
    padding: 6px 9px;
    margin-top: 6px;
    line-height: 1.35;
  }

  /* Right Content Area */
  .results-area {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  /* Encounter Summary Banner */
  .encounter-banner {
    background: linear-gradient(135deg, #211a14 0%, #15120f 100%);
    border: 1px solid var(--border-gold);
    border-radius: 6px;
    padding: 18px 22px;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5);
  }

  .encounter-title-block h2 {
    font-family: var(--font-serif);
    color: var(--text-gold);
    font-size: 1.35rem;
    margin-bottom: 5px;
  }

  .encounter-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .tag {
    font-size: 0.75rem;
    padding: 3px 9px;
    border-radius: 3px;
    background: #28221c;
    border: 1px solid #453a2e;
    color: var(--text-main);
  }

  .tag-gold {
    background: rgba(200, 157, 76, 0.15);
    border-color: var(--border-gold-bright);
    color: var(--text-gold);
    font-weight: 600;
  }

  .tag-crimson {
    background: rgba(158, 42, 43, 0.25);
    border-color: var(--accent-crimson-bright);
    color: #ff9b9b;
    font-weight: 600;
  }

  /* Analytics & Terrain Grid */
  .overview-grid {
    display: grid;
    grid-template-columns: 1.35fr 1fr;
    gap: 18px;
  }

  @media (max-width: 1350px) {
    .overview-grid {
      grid-template-columns: 1fr;
    }
  }

  .info-box {
    background: var(--bg-panel);
    border: 1px solid var(--border-subtle);
    border-top: 2px solid var(--border-gold);
    border-radius: 6px;
    padding: 16px 18px;
  }

  .info-box h3 {
    font-family: var(--font-serif);
    font-size: 0.92rem;
    color: var(--text-gold);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .metrics-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 12px;
  }

  .metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 4px;
    padding: 10px 12px;
  }

  .metric-label {
    font-size: 0.72rem;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-bottom: 4px;
  }

  .metric-val {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-main);
  }

  .metric-sub {
    font-size: 0.73rem;
    color: var(--text-muted);
    margin-top: 3px;
    line-height: 1.3;
  }

  .verdict-banner {
    background: rgba(200, 157, 76, 0.1);
    border-left: 3px solid var(--border-gold-bright);
    padding: 8px 12px;
    font-size: 0.84rem;
    margin-bottom: 12px;
  }

  .advice-list {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-size: 0.81rem;
    color: var(--text-main);
  }

  .advice-list li {
    position: relative;
    padding-left: 14px;
    line-height: 1.4;
  }

  .advice-list li::before {
    content: "•";
    color: var(--text-gold);
    position: absolute;
    left: 0;
    font-weight: bold;
  }

  /* Enemy Cards Roster */
  .roster-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-gold);
    padding-bottom: 8px;
  }

  .roster-header h3 {
    font-family: var(--font-serif);
    color: var(--text-gold);
    font-size: 1.1rem;
    letter-spacing: 0.8px;
    text-transform: uppercase;
  }

  .enemy-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(470px, 1fr));
    gap: 18px;
  }

  @media (max-width: 600px) {
    .enemy-grid {
      grid-template-columns: 1fr;
    }
  }

  .enemy-card {
    background: var(--bg-card);
    border: 1px solid #3a3128;
    border-radius: 6px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.45);
    transition: border-color 0.15s;
  }

  .enemy-card.is-boss {
    border: 1px solid var(--border-gold-bright);
    box-shadow: 0 0 20px rgba(200, 157, 76, 0.18);
  }

  .card-top {
    background: linear-gradient(90deg, #261f19 0%, #191512 100%);
    padding: 12px 16px;
    border-bottom: 1px solid #362d24;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 10px;
  }

  .enemy-card.is-boss .card-top {
    background: linear-gradient(90deg, #3d1b1b 0%, #211510 100%);
    border-bottom-color: var(--border-gold);
  }

  .npc-name {
    font-family: var(--font-serif);
    font-size: 1.05rem;
    color: var(--text-gold);
    font-weight: 700;
  }

  .npc-sub {
    font-size: 0.76rem;
    color: var(--text-muted);
    margin-top: 2px;
  }

  .asset-pill {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    background: #120f0d;
    border: 1px solid #3b3229;
    color: #c2b49b;
    padding: 4px 8px;
    border-radius: 4px;
    white-space: nowrap;
  }

  .card-body {
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  /* Defense Bars (Phys Armor, Magic Armor, Vitality) */
  .bars-container {
    display: flex;
    flex-direction: column;
    gap: 7px;
  }

  .stat-bar-row {
    display: grid;
    grid-template-columns: 95px 1fr 68px;
    align-items: center;
    gap: 8px;
    font-size: 0.78rem;
  }

  .bar-label {
    color: var(--text-muted);
    font-weight: 600;
  }

  .bar-track {
    height: 12px;
    border-radius: 3px;
    overflow: hidden;
    background: #12100e;
    border: 1px solid rgba(255, 255, 255, 0.08);
  }

  .bar-fill {
    height: 100%;
    border-radius: 2px;
  }

  .bar-phys { background: linear-gradient(90deg, #8c7332, #d4b663); }
  .bar-mag  { background: linear-gradient(90deg, #276396, #52a8f2); }
  .bar-vit  { background: linear-gradient(90deg, #8f2121, #e04343); }

  .bar-number {
    text-align: right;
    font-family: var(--font-mono);
    font-weight: 700;
    font-size: 0.82rem;
  }

  /* AP & Initiative Strip */
  .combat-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: space-between;
    background: #141210;
    border: 1px solid #29231d;
    border-radius: 4px;
    padding: 7px 11px;
    font-size: 0.78rem;
  }

  .strip-item span {
    color: var(--text-muted);
  }

  .strip-item strong {
    color: var(--text-main);
    margin-left: 3px;
  }

  .ap-highlight {
    color: var(--ap-green) !important;
  }

  /* Attributes 6-col Pill Grid */
  .attr-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 5px;
    text-align: center;
  }

  .attr-box {
    background: #141210;
    border: 1px solid #2b241e;
    border-radius: 4px;
    padding: 5px 2px;
  }

  .attr-box .a-name {
    font-size: 0.66rem;
    color: var(--text-muted);
    display: block;
  }

  .attr-box .a-val {
    font-size: 0.86rem;
    font-weight: 700;
    color: var(--text-gold);
    font-family: var(--font-mono);
  }

  /* Abilities, Talents, Resistances */
  .traits-block {
    font-size: 0.78rem;
    display: flex;
    flex-direction: column;
    gap: 5px;
    line-height: 1.35;
  }

  .trait-line strong {
    color: var(--text-muted);
    margin-right: 4px;
  }

  .pill-list {
    display: inline-flex;
    flex-wrap: wrap;
    gap: 4px;
  }

  .mini-pill {
    background: #25201b;
    border: 1px solid #3d342b;
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 0.73rem;
  }

  .mini-pill.talent {
    border-color: #594626;
    color: #ebd094;
  }

  .mini-pill.vuln {
    background: rgba(158, 42, 43, 0.25);
    border-color: #b53838;
    color: #ffa3a3;
  }

  .mini-pill.resist {
    background: rgba(58, 137, 201, 0.2);
    border-color: #3a75a8;
    color: #9cd0ff;
  }

  /* Skills List */
  .skills-section {
    border-top: 1px solid #2b241e;
    padding-top: 9px;
  }

  .skills-header {
    font-size: 0.74rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
  }

  .skills-list {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }

  .skill-item {
    background: #141210;
    border: 1px solid #26201b;
    border-radius: 4px;
    padding: 6px 9px;
    font-size: 0.77rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
  }

  .skill-left {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
  }

  .skill-name {
    font-weight: 700;
    color: var(--text-main);
  }

  .skill-school {
    color: var(--text-muted);
    font-size: 0.72rem;
  }

  .skill-badge {
    font-size: 0.68rem;
    padding: 1px 5px;
    border-radius: 3px;
    background: #26201a;
    color: #ccc;
  }

  .skill-badge.innate {
    background: rgba(157, 101, 201, 0.2);
    border: 1px solid var(--innate-purple);
    color: #d6b4fc;
  }

  .skill-badge.status {
    background: rgba(201, 54, 54, 0.2);
    border: 1px solid #a83232;
    color: #ffadad;
  }

  .skill-badge.req {
    background: rgba(56, 189, 248, 0.15);
    border: 1px solid rgba(56, 189, 248, 0.35);
    color: #7dd3fc;
  }

  .skill-ap {
    font-family: var(--font-mono);
    font-size: 0.74rem;
    color: var(--ap-green);
    white-space: nowrap;
    font-weight: 600;
  }

  .skill-right {
    display: flex;
    align-items: center;
    gap: 8px;
    white-space: nowrap;
  }

  .btn-skill-remove {
    background: transparent;
    border: none;
    color: #887a6d;
    cursor: pointer;
    font-size: 0.82rem;
    line-height: 1;
    padding: 2px 4px;
    border-radius: 3px;
    transition: color 0.15s, background 0.15s;
  }

  .btn-skill-remove:hover {
    color: #ff6b6b;
    background: rgba(220, 53, 69, 0.18);
  }

  .builder-skill-picker-row {
    margin-top: 8px;
    display: flex;
    gap: 6px;
    align-items: center;
  }

  .builder-skill-select {
    flex: 1;
    font-size: 0.76rem;
    padding: 4px 8px;
    background: #110f0d;
    border: 1px solid #3d3227;
    border-radius: 4px;
    color: var(--text-gold);
    outline: none;
  }

  .builder-skill-select:focus {
    border-color: var(--border-gold-bright);
  }

  .builder-skill-select optgroup {
    background: #1a1714;
    color: #e6c875;
    font-weight: 700;
  }

  .builder-skill-select option {
    background: #110f0d;
    color: #e0d8cb;
    font-weight: normal;
  }

  .builder-skill-select option:disabled {
    color: #665b50;
  }

  /* AI Tactics Footer */
  .tactics-box {
    background: rgba(0, 0, 0, 0.25);
    border-top: 1px solid #29231d;
    padding: 10px 16px;
    font-size: 0.76rem;
    color: var(--text-muted);
    line-height: 1.4;
    margin-top: auto;
  }

  .tactics-box strong {
    color: var(--text-gold);
  }

  /* Interactive Builder Mode Tabs & Controls */
  .mode-tabs {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    background: #100e0c;
    padding: 4px;
    border-radius: 5px;
    border: 1px solid var(--border-subtle);
    margin-bottom: 16px;
  }

  .mode-tab {
    cursor: pointer;
    font-family: var(--font-serif);
    font-size: 0.77rem;
    font-weight: 700;
    letter-spacing: 0.4px;
    padding: 8px 6px;
    border-radius: 4px;
    border: 1px solid transparent;
    background: transparent;
    color: var(--text-muted);
    text-align: center;
    white-space: nowrap;
    transition: all 0.15s ease;
  }

  .mode-tab:hover {
    color: var(--text-main);
    background: rgba(200, 157, 76, 0.08);
  }

  .mode-tab.active {
    background: linear-gradient(180deg, #9e2a2b 0%, #5e1516 100%);
    border-color: var(--border-gold-bright);
    color: #fff;
    box-shadow: 0 2px 8px rgba(158, 42, 43, 0.45);
  }

  .builder-solo-badge {
    font-size: 0.75rem;
    color: #ffcf8b;
    background: rgba(158, 42, 43, 0.22);
    border: 1px solid var(--border-gold-bright);
    border-left: 3px solid var(--accent-crimson-bright);
    border-radius: 4px;
    padding: 7px 10px;
    margin-bottom: 12px;
    line-height: 1.35;
  }

  .builder-card-controls {
    background: #13100d;
    border-bottom: 1px solid #332a21;
    padding: 9px 14px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
  }

  .builder-ctrl-item {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 0.72rem;
    color: var(--text-muted);
  }

  .builder-ctrl-item select {
    padding: 3px 6px;
    font-size: 0.74rem;
    height: 26px;
    width: auto;
    max-width: 145px;
    background: #1c1814;
    border-color: #453a2e;
  }

  .builder-card-actions {
    margin-left: auto;
    display: flex;
    gap: 6px;
    align-items: center;
  }

  .btn-mini {
    cursor: pointer;
    font-family: var(--font-sans);
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 3px;
    border: 1px solid #4a3e31;
    background: #241e18;
    color: var(--text-main);
    white-space: nowrap;
    transition: all 0.12s ease;
  }

  .btn-mini:hover:not(:disabled) {
    border-color: var(--border-gold-bright);
    color: var(--text-gold);
    background: #2f271f;
  }

  .btn-mini.danger:hover:not(:disabled) {
    border-color: var(--accent-crimson-bright);
    background: rgba(158, 42, 43, 0.35);
    color: #ffb3b3;
  }

  .btn-mini:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  /* Toast Notification */
  #toast {
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: #1f1914;
    border: 1px solid var(--border-gold-bright);
    color: var(--text-gold);
    padding: 12px 18px;
    border-radius: 5px;
    font-size: 0.85rem;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.8);
    opacity: 0;
    pointer-events: none;
    transform: translateY(10px);
    transition: all 0.2s ease;
    z-index: 999;
  }

  #toast.show {
    opacity: 1;
    transform: translateY(0);
  }
</style>
</head>
<body>

<header>
  <div class="brand">
    <div class="brand-emblem">II</div>
    <div class="brand-titles">
      <h1>Divinity: Original Sin 2 &mdash; GM Encounter Balancer</h1>
      <p>Precision Tactical Math &bull; Authentic GM Mode Bestiary &bull; Action Economy Engine</p>
    </div>
  </div>
  <div class="header-actions">
    <button class="btn" id="btnCopyMd" title="Copy Markdown Battle Sheet to Clipboard">Copy Markdown</button>
    <button class="btn" id="btnCopyAscii" title="Copy 72-col Terminal Cards to Clipboard">Copy ASCII Cards</button>
    <button class="btn" id="btnDownloadMd" title="Download .md file">Download .md</button>
    <button class="btn" id="btnSaveDisk" title="Save .md file directly to project folder">Save to Disk</button>
  </div>
</header>

<div class="workspace">
  <!-- LEFT CONFIGURATION PANEL -->
  <aside class="config-panel">
    <!-- MODE SWITCHER TABS -->
    <div class="mode-tabs" role="tablist">
      <button type="button" class="mode-tab active" id="tabAutoMode" data-mode="auto">&#x2694; Auto-Generator</button>
      <button type="button" class="mode-tab" id="tabBuilderMode" data-mode="builder">&#x2692; Interactive Builder</button>
    </div>

    <div class="panel-section-title" style="margin-top: 0;">1. Player Party Profile</div>
    <div class="form-row">
      <div class="form-group">
        <label for="partySize">Party Size (1-4)</label>
        <select id="partySize">
          <option value="1">1 Player (Solo)</option>
          <option value="2">2 Players (Duo)</option>
          <option value="3">3 Players</option>
          <option value="4" selected>4 Players (Standard)</option>
        </select>
      </div>
      <div class="form-group">
        <label for="partyLevel">Party Level (1-25)</label>
        <input type="number" id="partyLevel" min="1" max="25" value="4">
      </div>
    </div>

    <div class="checkbox-row" id="loneWolfContainer" style="display: none;">
      <input type="checkbox" id="isLoneWolf">
      <label for="isLoneWolf">Lone Wolf Talent Active (+AP &amp; +Armor/Vitality)</label>
    </div>

    <div class="form-group">
      <label for="damageProfile">Party Damage Composition</label>
      <select id="damageProfile"></select>
    </div>

    <div class="form-group">
      <label for="difficulty">Target Difficulty Tier</label>
      <select id="difficulty"></select>
    </div>

    <!-- ================================================================= -->
    <!-- MODE A: AUTO-GENERATOR CONTROLS                                   -->
    <!-- ================================================================= -->
    <div id="autoModePanel">
      <div class="panel-section-title">2. Encounter Structure</div>
      <div class="form-group">
        <label for="encounterType">Encounter Type</label>
        <select id="encounterType"></select>
      </div>

      <!-- BOSS CONFIGURATION SUB-PANEL -->
      <div class="sub-panel" id="bossConfigPanel" style="display: none;">
        <div class="sub-panel-header">Boss Encounter Tuning</div>
        <div class="form-group">
          <label for="minionCount">Accompanying Minions (0 - 5)</label>
          <select id="minionCount">
            <option value="0">0 Minions (Epic Solo Boss Overlord Duel)</option>
            <option value="1">1 Minion (Boss + Elite Lieutenant Duo)</option>
            <option value="2">2 Minions (Tightly Guarded Trio)</option>
            <option value="3" selected>3 Minions (Standard Balanced Boss Squad)</option>
            <option value="4">4 Minions (Heavy Minion Guard)</option>
            <option value="5">5 Minions (Full Minion Swarm)</option>
          </select>
        </div>

        <div class="form-group">
          <label for="bossSelectionMode">Boss Selection Mode</label>
          <select id="bossSelectionMode">
            <option value="random" selected>Random / Thematic Boss for Faction</option>
            <option value="bestiary">Choose Iconic Boss from Bestiary</option>
            <option value="custom">Search or Forcefully Create Custom Boss</option>
          </select>
        </div>

        <div class="form-group" id="bossBestiaryGroup" style="display: none;">
          <label for="bossPresetSelect">Select Bestiary Boss</label>
          <select id="bossPresetSelect"></select>
        </div>

        <div class="form-group" id="bossCustomGroup" style="display: none;">
          <label for="bossCustomInput">Boss Name or Keyword (e.g. "Mountain Troll", "Viper Assassin")</label>
          <input type="text" id="bossCustomInput" placeholder="Enter Boss name or keyword...">
        </div>

        <div class="form-group">
          <label for="defenseProfile">Defensive &amp; Elemental Weakness Profile</label>
          <select id="defenseProfile"></select>
        </div>
      </div>

      <!-- FACTION & RACE SECTION -->
      <div id="factionRaceSection">
        <div class="panel-section-title" id="factionSectionTitle">3. Faction &amp; Race Theme</div>
        <div class="form-group" id="factionGroup">
          <label for="factionSelect" id="factionLabel">Thematic Enemy Faction</label>
          <select id="factionSelect"></select>
        </div>

        <div class="form-group" id="raceGroup">
          <label for="raceSelect" id="raceLabel">Restrict to Single Enemy Race</label>
          <select id="raceSelect"></select>
        </div>
        <div class="hint-badge" id="singleRaceFactionNotice" style="display: none;">
          All units in this faction share the same innate race; single-race restriction is automatically applied.
        </div>
      </div>

      <div class="hint-badge" id="soloBossSkipNotice" style="display: none; margin-bottom: 14px;">
        Solo Boss duel with a designated Boss NPC selected &mdash; Faction &amp; Race are automatically inherited from the Boss.
      </div>

      <button class="btn btn-primary" id="btnGenerate" style="margin-top: 8px;">
        &#x21bb; Re-Roll Encounter Variant
      </button>
    </div>

    <!-- ================================================================= -->
    <!-- MODE B: INTERACTIVE ENCOUNTER BUILDER CONTROLS                    -->
    <!-- ================================================================= -->
    <div id="builderModePanel" style="display: none;">
      <div class="panel-section-title">2. Encounter Type</div>
      <div class="form-group">
        <label for="builderEncounterType">Encounter Type Definition</label>
        <select id="builderEncounterType"></select>
      </div>

      <div class="builder-solo-badge" id="builderSoloRuleBadge">
        <strong>Solo Enemy Rule Active:</strong> Since there is 1 enemy in the encounter, it is automatically balanced as a <strong>Boss Encounter (Solo Boss / Overlord)</strong>.
      </div>

      <div class="panel-section-title">3. Add New Enemy to Roster</div>
      <div class="sub-panel" style="margin-bottom: 10px;">
        <div class="form-group">
          <label for="builderFaction">Enemy Type / Faction</label>
          <select id="builderFaction"></select>
        </div>

        <div class="form-group">
          <label for="builderTemplate">Bestiary Preset or Custom Unit</label>
          <select id="builderTemplate"></select>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="builderRace">Enemy Race</label>
            <select id="builderRace"></select>
          </div>
          <div class="form-group">
            <label for="builderRole">Enemy Role / Class</label>
            <select id="builderRole"></select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="builderTier">Unit Rank / Tier</label>
            <select id="builderTier"></select>
          </div>
          <div class="form-group">
            <label for="builderLevelOffset">Level Offset</label>
            <select id="builderLevelOffset"></select>
          </div>
        </div>

        <div class="form-group">
          <label for="builderDefense">Defensive / Elemental Profile</label>
          <select id="builderDefense"></select>
        </div>

        <div class="form-group">
          <label for="builderName">Unit Name (Optional Override)</label>
          <input type="text" id="builderName" placeholder="Auto-named from template or role...">
        </div>

        <div class="form-group" style="margin-bottom: 12px;">
          <label for="builderEquipment">Weapons &amp; Equipment</label>
          <input type="text" id="builderEquipment" placeholder="Auto-equipped for role...">
        </div>

        <button type="button" class="btn btn-primary" id="btnAddBuilderEnemy">
          + Add Enemy to Encounter
        </button>
      </div>

      <div class="form-row">
        <button type="button" class="btn" id="btnBuilderRerollTerrain" style="justify-content: center; font-size: 0.78rem; padding: 8px 10px;">
          &#x21bb; Re-Roll Terrain
        </button>
        <button type="button" class="btn" id="btnBuilderResetSolo" style="justify-content: center; font-size: 0.78rem; padding: 8px 10px;">
          Reset to 1 Enemy
        </button>
      </div>
    </div>
  </aside>

  <!-- RIGHT RESULTS AREA -->
  <main class="results-area" id="resultsArea">
    <!-- Populated dynamically via JS -->
  </main>
</div>

<div id="toast">Copied to clipboard!</div>

<script>
  let META = null;
  let CURRENT_ENCOUNTER = null;
  let ACTIVE_MODE = 'auto'; // 'auto' | 'builder'
  let BUILDER_ENEMIES = [];
  let debounceTimer = null;
  let activeRequestId = 0;

  function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2600);
  }

  function scheduleRefresh(delayMs = 150) {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      refreshActiveMode();
    }, delayMs);
  }

  function refreshActiveMode(isExplicitReroll = false) {
    if (ACTIVE_MODE === 'builder') {
      return buildCustomEncounter(isExplicitReroll);
    } else {
      return generateEncounter(isExplicitReroll);
    }
  }

  async function initApp() {
    const res = await fetch('/api/meta');
    META = await res.json();

    populateSelect('damageProfile', META.damage_profiles);
    populateSelect('difficulty', META.difficulties);
    populateSelect('encounterType', META.encounter_types, 'STANDARD');
    populateSelect('factionSelect', META.factions, 'ANY');
    populateSelect('defenseProfile', META.defense_profiles, 'auto');

    // Populate Interactive Builder controls
    populateSelect('builderEncounterType', META.builder_encounter_types, 'AUTO');
    populateSelect('builderFaction', META.builder_factions, 'BANDITS');
    populateSelect('builderRace', META.builder_races, 'HUMAN');
    populateSelect('builderRole', META.combat_roles, 'FIGHTER');
    populateSelect('builderTier', META.unit_tiers, 'NORMAL');
    populateSelect('builderLevelOffset', META.level_offsets, 0);
    populateSelect('builderDefense', META.defense_profiles, 'auto');

    updateBuilderTemplateOptions();
    syncBuilderFormFromTemplate();

    // Initialize Builder Roster with 1 default enemy (which triggers Solo Boss rule)
    BUILDER_ENEMIES = [
      {
        template_name: 'Bandit Kingpin',
        name: 'Bandit Kingpin',
        faction: 'BANDITS',
        race: 'HUMAN',
        combat_role: 'FIGHTER',
        unit_tier: 'BOSS',
        defense_profile: 'auto',
        equipment: 'Two-Handed Greataxe + Spiked Shoulders',
        level_offset: 0
      }
    ];

    const bossPreset = document.getElementById('bossPresetSelect');
    bossPreset.innerHTML = '';
    META.boss_templates.forEach(b => {
      const opt = document.createElement('option');
      opt.value = b.name;
      opt.dataset.faction = b.faction;
      opt.textContent = `${b.name} (${b.faction_label} | ${b.race_label})`;
      bossPreset.appendChild(opt);
    });

    bindEvents();
    syncDynamicControls();
    await generateEncounter();
  }

  function populateSelect(id, items, defaultVal = null) {
    const el = document.getElementById(id);
    el.innerHTML = '';
    items.forEach((item, idx) => {
      const opt = document.createElement('option');
      opt.value = item.value;
      opt.textContent = item.label;
      if ((defaultVal !== null && String(item.value) === String(defaultVal)) || (defaultVal === null && idx === 0)) {
        opt.selected = true;
      }
      el.appendChild(opt);
    });
  }

  function updateBuilderTemplateOptions() {
    const facKey = document.getElementById('builderFaction').value;
    const tplSelect = document.getElementById('builderTemplate');
    tplSelect.innerHTML = '';

    const customOpt = document.createElement('option');
    customOpt.value = 'CUSTOM';
    customOpt.textContent = '✦ Custom Enemy (Configure Freely Below)';
    tplSelect.appendChild(customOpt);

    const matching = (META.all_templates || []).filter(t => t.faction === facKey);
    matching.forEach(t => {
      const opt = document.createElement('option');
      opt.value = t.name;
      const rankTag = t.can_be_boss ? ' [Boss]' : (t.default_tier === 'MINION' ? ' [Minion]' : '');
      opt.textContent = `${t.name} (${t.race_label} • ${t.archetype}${rankTag})`;
      tplSelect.appendChild(opt);
    });

    if (matching.length > 0) {
      tplSelect.value = matching[0].name;
    } else {
      tplSelect.value = 'CUSTOM';
    }
  }

  function syncBuilderFormFromTemplate() {
    const tplName = document.getElementById('builderTemplate').value;
    if (tplName === 'CUSTOM') {
      const roleKey = document.getElementById('builderRole').value;
      const roleObj = (META.combat_roles || []).find(r => r.value === roleKey);
      if (roleObj) {
        document.getElementById('builderEquipment').value = roleObj.default_equipment;
      }
      document.getElementById('builderName').value = '';
      return;
    }

    const tpl = (META.all_templates || []).find(t => t.name === tplName);
    if (!tpl) return;

    document.getElementById('builderFaction').value = tpl.faction;
    document.getElementById('builderRace').value = tpl.race;
    document.getElementById('builderRole').value = tpl.combat_role_key || 'FIGHTER';
    document.getElementById('builderTier').value = tpl.default_tier || 'NORMAL';
    document.getElementById('builderName').value = tpl.name;
    document.getElementById('builderEquipment').value = tpl.equipment;
  }

  function updateBuilderSoloBadge() {
    const badge = document.getElementById('builderSoloRuleBadge');
    const encTypeEl = document.getElementById('builderEncounterType');
    if (!badge || !encTypeEl) return;

    if (BUILDER_ENEMIES.length === 1) {
      badge.innerHTML = `<strong>Solo Enemy Rule Active:</strong> With <strong>1 enemy</strong> in the encounter, it is automatically defined and balanced as a <strong>Boss Encounter (Solo Boss / Overlord)</strong>.`;
      badge.style.borderColor = 'var(--border-gold-bright)';
      badge.style.background = 'rgba(158, 42, 43, 0.24)';
    } else {
      badge.innerHTML = `<strong>Dynamic Roster Balancer (${BUILDER_ENEMIES.length} Enemies):</strong> Armor, Vitality, and AP Recovery automatically scale across all units to match your party.`;
      badge.style.borderColor = 'var(--border-gold)';
      badge.style.background = 'rgba(200, 157, 76, 0.10)';
    }
  }

  function switchMode(newMode) {
    ACTIVE_MODE = newMode;
    document.getElementById('tabAutoMode').classList.toggle('active', newMode === 'auto');
    document.getElementById('tabBuilderMode').classList.toggle('active', newMode === 'builder');
    document.getElementById('autoModePanel').style.display = newMode === 'auto' ? 'block' : 'none';
    document.getElementById('builderModePanel').style.display = newMode === 'builder' ? 'block' : 'none';

    if (newMode === 'builder') {
      updateBuilderSoloBadge();
      buildCustomEncounter();
    } else {
      generateEncounter();
    }
  }

  function importCurrentEncounterToBuilder() {
    if (!CURRENT_ENCOUNTER || !CURRENT_ENCOUNTER.enemies) return;
    BUILDER_ENEMIES = CURRENT_ENCOUNTER.enemies.map(e => ({
      template_name: e.template_name || 'CUSTOM',
      name: e.base_name || e.name,
      faction: e.faction_key || 'BANDITS',
      race: e.race_key || 'HUMAN',
      combat_role: e.combat_role_key || 'FIGHTER',
      unit_tier: e.unit_tier_key || 'NORMAL',
      defense_profile: 'auto',
      equipment: e.equipment || '',
      level_offset: typeof e.level_offset === 'number' ? e.level_offset : 0,
      skills: e.skills ? e.skills.map(s => s.name) : undefined,
    }));
    document.getElementById('builderEncounterType').value = 'AUTO';
    switchMode('builder');
    showToast(`Imported ${BUILDER_ENEMIES.length} combatant(s) into Interactive Builder!`);
  }

  function updateRaceOptionsForFaction(factionKey) {
    const raceGroup = document.getElementById('raceGroup');
    const raceSelect = document.getElementById('raceSelect');
    const notice = document.getElementById('singleRaceFactionNotice');

    const validRaces = (META && META.faction_races[factionKey]) || [];
    const prevValue = raceSelect.value;

    if (validRaces.length === 0) {
      raceGroup.style.display = 'none';
      notice.style.display = 'block';
      raceSelect.innerHTML = '<option value="ANY" selected>Any</option>';
    } else {
      raceGroup.style.display = 'block';
      notice.style.display = 'none';
      raceSelect.innerHTML = '';
      let matched = false;
      validRaces.forEach(r => {
        const opt = document.createElement('option');
        opt.value = r.value;
        opt.textContent = r.label;
        if (r.value === prevValue) {
          opt.selected = true;
          matched = true;
        }
        raceSelect.appendChild(opt);
      });
      if (!matched && raceSelect.options.length > 0) {
        raceSelect.options[0].selected = true;
      }
    }
  }

  function syncDynamicControls() {
    const partySize = parseInt(document.getElementById('partySize').value, 10);
    const lwContainer = document.getElementById('loneWolfContainer');
    const lwCheck = document.getElementById('isLoneWolf');

    if (partySize === 1 || partySize === 2) {
      lwContainer.style.display = 'flex';
    } else {
      lwContainer.style.display = 'none';
      lwCheck.checked = false;
    }

    const encType = document.getElementById('encounterType').value;
    const bossPanel = document.getElementById('bossConfigPanel');
    const bossMode = document.getElementById('bossSelectionMode').value;
    const bossBestiaryGroup = document.getElementById('bossBestiaryGroup');
    const bossCustomGroup = document.getElementById('bossCustomGroup');
    const minionCount = parseInt(document.getElementById('minionCount').value, 10);

    if (encType === 'BOSS') {
      bossPanel.style.display = 'block';
      bossBestiaryGroup.style.display = bossMode === 'bestiary' ? 'block' : 'none';
      bossCustomGroup.style.display = bossMode === 'custom' ? 'block' : 'none';
    } else {
      bossPanel.style.display = 'none';
    }

    // Determine if a specific boss NPC is designated
    let hasSpecificBoss = false;
    if (encType === 'BOSS') {
      if (bossMode === 'bestiary') {
        hasSpecificBoss = true;
      } else if (bossMode === 'custom' && document.getElementById('bossCustomInput').value.trim().length > 0) {
        hasSpecificBoss = true;
      }
    }

    const skipFactionRace = (encType === 'BOSS' && minionCount === 0 && hasSpecificBoss);
    const factionRaceSection = document.getElementById('factionRaceSection');
    const soloBossSkipNotice = document.getElementById('soloBossSkipNotice');

    if (skipFactionRace) {
      factionRaceSection.style.display = 'none';
      soloBossSkipNotice.style.display = 'block';
    } else {
      factionRaceSection.style.display = 'block';
      soloBossSkipNotice.style.display = 'none';

      const factionLabel = document.getElementById('factionLabel');
      const raceLabel = document.getElementById('raceLabel');
      if (encType === 'BOSS' && minionCount > 0) {
        factionLabel.textContent = 'Minion Faction / Theme';
        raceLabel.textContent = 'Restrict Minions to Single Race';
      } else {
        factionLabel.textContent = 'Thematic Enemy Faction';
        raceLabel.textContent = 'Restrict to Single Enemy Race';
      }

      const facKey = document.getElementById('factionSelect').value;
      updateRaceOptionsForFaction(facKey);
    }

    updateBuilderSoloBadge();
  }

  function bindEvents() {
    // Mode tabs
    document.getElementById('tabAutoMode').addEventListener('click', () => switchMode('auto'));
    document.getElementById('tabBuilderMode').addEventListener('click', () => switchMode('builder'));

    // Shared Party Profile controls
    document.getElementById('partySize').addEventListener('change', () => {
      const ps = parseInt(document.getElementById('partySize').value, 10);
      const lw = document.getElementById('isLoneWolf').checked && (ps <= 2);
      if (lw) {
        document.getElementById('minionCount').value = '2';
      }
      syncDynamicControls();
      refreshActiveMode();
    });

    document.getElementById('partyLevel').addEventListener('change', () => {
      let val = parseInt(document.getElementById('partyLevel').value, 10);
      if (isNaN(val) || val < 1) val = 1;
      if (val > 25) val = 25;
      document.getElementById('partyLevel').value = val;
      refreshActiveMode();
    });

    document.getElementById('partyLevel').addEventListener('input', () => {
      const val = parseInt(document.getElementById('partyLevel').value, 10);
      if (!isNaN(val) && val >= 1 && val <= 25) {
        scheduleRefresh(120);
      }
    });

    document.getElementById('isLoneWolf').addEventListener('change', (e) => {
      document.getElementById('minionCount').value = e.target.checked ? '2' : '3';
      syncDynamicControls();
      refreshActiveMode();
    });

    document.getElementById('damageProfile').addEventListener('change', () => refreshActiveMode());
    document.getElementById('difficulty').addEventListener('change', () => refreshActiveMode());

    // Auto-Generator mode controls
    document.getElementById('encounterType').addEventListener('change', () => {
      syncDynamicControls();
      generateEncounter();
    });

    document.getElementById('minionCount').addEventListener('change', () => {
      syncDynamicControls();
      generateEncounter();
    });

    document.getElementById('bossSelectionMode').addEventListener('change', () => {
      if (document.getElementById('bossSelectionMode').value === 'bestiary') {
        const selOpt = document.getElementById('bossPresetSelect').selectedOptions[0];
        if (selOpt && selOpt.dataset.faction) {
          document.getElementById('factionSelect').value = selOpt.dataset.faction;
        }
      }
      syncDynamicControls();
      generateEncounter();
    });

    document.getElementById('bossPresetSelect').addEventListener('change', (e) => {
      const selOpt = e.target.selectedOptions[0];
      if (selOpt && selOpt.dataset.faction) {
        document.getElementById('factionSelect').value = selOpt.dataset.faction;
      }
      syncDynamicControls();
      generateEncounter();
    });

    document.getElementById('bossCustomInput').addEventListener('input', () => {
      syncDynamicControls();
      scheduleRefresh(220);
    });

    document.getElementById('defenseProfile').addEventListener('change', () => generateEncounter());

    document.getElementById('factionSelect').addEventListener('change', () => {
      syncDynamicControls();
      generateEncounter();
    });

    document.getElementById('raceSelect').addEventListener('change', () => generateEncounter());

    document.getElementById('btnGenerate').addEventListener('click', () => generateEncounter(true));

    // Interactive Builder mode controls
    document.getElementById('builderEncounterType').addEventListener('change', () => {
      updateBuilderSoloBadge();
      buildCustomEncounter();
    });

    document.getElementById('builderFaction').addEventListener('change', () => {
      updateBuilderTemplateOptions();
      syncBuilderFormFromTemplate();
    });

    document.getElementById('builderTemplate').addEventListener('change', () => {
      syncBuilderFormFromTemplate();
    });

    document.getElementById('builderRole').addEventListener('change', () => {
      const roleKey = document.getElementById('builderRole').value;
      const roleObj = (META.combat_roles || []).find(r => r.value === roleKey);
      if (roleObj) {
        document.getElementById('builderEquipment').value = roleObj.default_equipment;
      }
    });

    document.getElementById('btnAddBuilderEnemy').addEventListener('click', () => {
      const newSpec = {
        template_name: document.getElementById('builderTemplate').value,
        name: document.getElementById('builderName').value.trim() || null,
        faction: document.getElementById('builderFaction').value,
        race: document.getElementById('builderRace').value,
        combat_role: document.getElementById('builderRole').value,
        unit_tier: document.getElementById('builderTier').value,
        defense_profile: document.getElementById('builderDefense').value,
        equipment: document.getElementById('builderEquipment').value.trim() || null,
        level_offset: parseInt(document.getElementById('builderLevelOffset').value, 10) || 0,
      };
      BUILDER_ENEMIES.push(newSpec);
      updateBuilderSoloBadge();
      buildCustomEncounter();
      showToast(`Added enemy (#${BUILDER_ENEMIES.length}) & rebalanced encounter!`);
    });

    document.getElementById('btnBuilderRerollTerrain').addEventListener('click', () => {
      buildCustomEncounter(true);
    });

    document.getElementById('btnBuilderResetSolo').addEventListener('click', () => {
      if (BUILDER_ENEMIES.length > 1) {
        BUILDER_ENEMIES = [BUILDER_ENEMIES[0]];
        BUILDER_ENEMIES[0].unit_tier = 'BOSS';
      }
      document.getElementById('builderEncounterType').value = 'AUTO';
      updateBuilderSoloBadge();
      buildCustomEncounter();
      showToast('Reset roster to 1 Solo Boss!');
    });

    // Header Export Buttons
    document.getElementById('btnCopyMd').addEventListener('click', () => {
      if (!CURRENT_ENCOUNTER) return;
      navigator.clipboard.writeText(CURRENT_ENCOUNTER.markdown);
      showToast('Markdown Battle Sheet copied to clipboard!');
    });

    document.getElementById('btnCopyAscii').addEventListener('click', () => {
      if (!CURRENT_ENCOUNTER) return;
      navigator.clipboard.writeText(CURRENT_ENCOUNTER.terminal_text);
      showToast('72-col ASCII Terminal Cards copied to clipboard!');
    });

    document.getElementById('btnDownloadMd').addEventListener('click', () => {
      if (!CURRENT_ENCOUNTER) return;
      const blob = new Blob([CURRENT_ENCOUNTER.markdown], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const cleanName = CURRENT_ENCOUNTER.name.toLowerCase().replace(/[^a-z0-9]+/g, '_');
      a.download = `${cleanName}.md`;
      a.click();
      URL.revokeObjectURL(url);
      showToast('Downloaded Markdown Battle Sheet!');
    });

    document.getElementById('btnSaveDisk').addEventListener('click', async () => {
      if (!CURRENT_ENCOUNTER) return;
      const exportPayload = ACTIVE_MODE === 'builder' ? getBuilderPayload() : getFormPayload();
      const res = await fetch('/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(exportPayload)
      });
      const data = await res.json();
      if (data.filepath) {
        showToast(`Saved to: ${data.filename}`);
      }
    });
  }

  function getFormPayload() {
    const encType = document.getElementById('encounterType').value;
    const bossMode = document.getElementById('bossSelectionMode').value;
    let bossTemplate = null;
    let minionCount = null;
    let defenseProfile = 'auto';

    if (encType === 'BOSS') {
      minionCount = parseInt(document.getElementById('minionCount').value, 10);
      defenseProfile = document.getElementById('defenseProfile').value;
      if (bossMode === 'bestiary') {
        bossTemplate = document.getElementById('bossPresetSelect').value;
      } else if (bossMode === 'custom') {
        bossTemplate = document.getElementById('bossCustomInput').value.trim() || null;
      }
    }

    return {
      mode: 'auto',
      party_size: parseInt(document.getElementById('partySize').value, 10),
      level: Math.max(1, Math.min(25, parseInt(document.getElementById('partyLevel').value, 10) || 4)),
      is_lone_wolf: document.getElementById('isLoneWolf').checked,
      damage_profile: document.getElementById('damageProfile').value,
      difficulty: document.getElementById('difficulty').value,
      encounter_type: encType,
      faction: document.getElementById('factionSelect').value,
      race: document.getElementById('raceSelect').value,
      boss_template: bossTemplate,
      minion_count: minionCount,
      defense_profile: defenseProfile,
    };
  }

  function getBuilderPayload() {
    return {
      mode: 'builder',
      party_size: parseInt(document.getElementById('partySize').value, 10),
      level: Math.max(1, Math.min(25, parseInt(document.getElementById('partyLevel').value, 10) || 4)),
      is_lone_wolf: document.getElementById('isLoneWolf').checked,
      damage_profile: document.getElementById('damageProfile').value,
      difficulty: document.getElementById('difficulty').value,
      encounter_type: document.getElementById('builderEncounterType').value,
      enemies: BUILDER_ENEMIES,
    };
  }

  async function generateEncounter(isExplicitReroll = false) {
    if (debounceTimer) {
      clearTimeout(debounceTimer);
      debounceTimer = null;
    }
    const reqId = ++activeRequestId;
    const payload = getFormPayload();
    const resultsEl = document.getElementById('resultsArea');
    if (isExplicitReroll && resultsEl) {
      resultsEl.style.opacity = '0.6';
      resultsEl.style.transition = 'opacity 0.1s ease';
    }
    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (reqId !== activeRequestId) return;
      CURRENT_ENCOUNTER = data;
      renderEncounter(CURRENT_ENCOUNTER);
    } finally {
      if (resultsEl) {
        resultsEl.style.opacity = '1';
      }
    }
  }

  async function buildCustomEncounter(isExplicitReroll = false) {
    if (debounceTimer) {
      clearTimeout(debounceTimer);
      debounceTimer = null;
    }
    const reqId = ++activeRequestId;
    const payload = getBuilderPayload();
    const resultsEl = document.getElementById('resultsArea');
    if (isExplicitReroll && resultsEl) {
      resultsEl.style.opacity = '0.6';
      resultsEl.style.transition = 'opacity 0.1s ease';
    }
    try {
      const res = await fetch('/api/build_custom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (reqId !== activeRequestId) return;
      CURRENT_ENCOUNTER = data;
      updateBuilderSoloBadge();
      renderEncounter(CURRENT_ENCOUNTER);
    } finally {
      if (resultsEl) {
        resultsEl.style.opacity = '1';
      }
    }
  }

  function updateBuilderUnitField(idx, field, value) {
    if (!BUILDER_ENEMIES[idx]) return;
    if (field === 'level_offset') {
      BUILDER_ENEMIES[idx][field] = parseInt(value, 10) || 0;
    } else if (field === 'combat_role') {
      BUILDER_ENEMIES[idx][field] = value;
      const roleObj = (META.combat_roles || []).find(r => r.value === value);
      if (roleObj) {
        BUILDER_ENEMIES[idx].equipment = roleObj.default_equipment;
      }
      delete BUILDER_ENEMIES[idx].skills;
    } else {
      BUILDER_ENEMIES[idx][field] = value;
    }
    buildCustomEncounter();
  }

  function duplicateBuilderUnit(idx) {
    if (!BUILDER_ENEMIES[idx]) return;
    const copy = JSON.parse(JSON.stringify(BUILDER_ENEMIES[idx]));
    if (copy.unit_tier === 'BOSS') {
      copy.unit_tier = 'NORMAL';
    }
    BUILDER_ENEMIES.splice(idx + 1, 0, copy);
    updateBuilderSoloBadge();
    buildCustomEncounter();
    showToast('Duplicated combatant & rebalanced encounter!');
  }

  function removeBuilderUnit(idx) {
    if (BUILDER_ENEMIES.length <= 1) return;
    BUILDER_ENEMIES.splice(idx, 1);
    if (BUILDER_ENEMIES.length === 1) {
      BUILDER_ENEMIES[0].unit_tier = 'BOSS';
    }
    updateBuilderSoloBadge();
    buildCustomEncounter();
    showToast('Removed combatant & rebalanced encounter!');
  }

  function escapeJsStr(str) {
    if (!str) return '';
    return String(str).replace(/\\/g, '\\\\').replace(/'/g, "\\'");
  }

  function addBuilderUnitSkill(idx, skillName) {
    if (!BUILDER_ENEMIES[idx]) return;
    if (!BUILDER_ENEMIES[idx].skills) {
      if (CURRENT_ENCOUNTER && CURRENT_ENCOUNTER.enemies && CURRENT_ENCOUNTER.enemies[idx]) {
        BUILDER_ENEMIES[idx].skills = (CURRENT_ENCOUNTER.enemies[idx].skills || []).map(s => s.name);
      } else {
        BUILDER_ENEMIES[idx].skills = [];
      }
    }
    const clean = String(skillName).trim();
    if (!clean) return;
    if (!BUILDER_ENEMIES[idx].skills.some(s => s.toLowerCase() === clean.toLowerCase())) {
      BUILDER_ENEMIES[idx].skills.push(clean);
      buildCustomEncounter();
      showToast(`Added skill "${clean}" & realigned combat abilities!`);
    }
  }

  function removeBuilderUnitSkill(idx, skillName) {
    if (!BUILDER_ENEMIES[idx]) return;
    if (!BUILDER_ENEMIES[idx].skills) {
      if (CURRENT_ENCOUNTER && CURRENT_ENCOUNTER.enemies && CURRENT_ENCOUNTER.enemies[idx]) {
        BUILDER_ENEMIES[idx].skills = (CURRENT_ENCOUNTER.enemies[idx].skills || []).map(s => s.name);
      } else {
        BUILDER_ENEMIES[idx].skills = [];
      }
    }
    BUILDER_ENEMIES[idx].skills = BUILDER_ENEMIES[idx].skills.filter(
      s => s.toLowerCase() !== String(skillName).trim().toLowerCase()
    );
    buildCustomEncounter();
    showToast(`Removed skill "${skillName}" & realigned combat abilities!`);
  }

  function resetBuilderUnitSkills(idx) {
    if (!BUILDER_ENEMIES[idx]) return;
    delete BUILDER_ENEMIES[idx].skills;
    buildCustomEncounter();
    showToast('Reset skills to authentic template defaults!');
  }

  function renderSkillPickerRow(idx, currentSkills) {
    if (ACTIVE_MODE !== 'builder' || !META.all_skills) return '';
    const currentSet = new Set((currentSkills || []).map(s => s.name.toLowerCase()));
    const schools = META.skill_schools || [];

    let optgroups = '';
    schools.forEach(school => {
      const skillsInSchool = (META.all_skills || []).filter(s => s.school === school);
      if (!skillsInSchool.length) return;
      const opts = skillsInSchool.map(s => {
        const has = currentSet.has(s.name.toLowerCase());
        const disabled = has ? 'disabled' : '';
        const reqStr = (s.requirements_display && s.requirements_display !== 'None') ? ` - Req: ${s.requirements_display}` : '';
        const tag = has ? ' (Learned)' : ` (${s.ap_cost} AP${reqStr})`;
        return `<option value="${escapeHtml(s.name)}" ${disabled}>${escapeHtml(s.name)}${tag}</option>`;
      }).join('');
      optgroups += `<optgroup label="${escapeHtml(school)}">${opts}</optgroup>`;
    });

    return `
      <div class="builder-skill-picker-row">
        <select class="builder-skill-select" onchange="if(this.value){ addBuilderUnitSkill(${idx}, this.value); this.value=''; }">
          <option value="" disabled selected>+ Add Skill to Combatant...</option>
          ${optgroups}
        </select>
        <button type="button" class="btn-mini" onclick="resetBuilderUnitSkills(${idx})" title="Reset to authentic template defaults">&#x21BA; Reset</button>
      </div>
    `;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function renderBuilderCardControls(e, idx) {
    if (ACTIVE_MODE !== 'builder') return '';
    const spec = BUILDER_ENEMIES[idx] || {};
    const isSolo = BUILDER_ENEMIES.length === 1;

    const roleOptions = (META.combat_roles || []).map(r => {
      const sel = (spec.combat_role || e.combat_role_key) === r.value ? 'selected' : '';
      return `<option value="${r.value}" ${sel}>${escapeHtml(r.label.split('/')[0].trim())}</option>`;
    }).join('');

    const raceOptions = (META.builder_races || []).map(r => {
      const sel = (spec.race || e.race_key) === r.value ? 'selected' : '';
      return `<option value="${r.value}" ${sel}>${escapeHtml(r.label)}</option>`;
    }).join('');

    const tierOptions = isSolo
      ? `<option value="BOSS" selected>Solo Boss (1-Enemy Rule)</option>`
      : (META.unit_tiers || []).map(t => {
          const sel = (spec.unit_tier || e.unit_tier_key) === t.value ? 'selected' : '';
          return `<option value="${t.value}" ${sel}>${escapeHtml(t.label.split('(')[0].trim())}</option>`;
        }).join('');

    const offsetVal = typeof spec.level_offset === 'number' ? spec.level_offset : (e.level_offset || 0);
    const offsetOptions = [-2, -1, 0, 1, 2].map(off => {
      const sel = offsetVal === off ? 'selected' : '';
      const lbl = off === 0 ? 'Lvl +0' : (off > 0 ? `Lvl +${off}` : `Lvl ${off}`);
      return `<option value="${off}" ${sel}>${lbl}</option>`;
    }).join('');

    const defVal = spec.defense_profile || 'auto';
    const defOptions = (META.defense_profiles || []).map(d => {
      const sel = defVal === d.value ? 'selected' : '';
      const shortLbl = d.value === 'auto' ? 'Auto' : d.label.split('(')[0].trim();
      return `<option value="${d.value}" ${sel}>${escapeHtml(shortLbl)}</option>`;
    }).join('');

    return `
      <div class="builder-card-controls">
        <div class="builder-ctrl-item">
          <span>Rank:</span>
          <select onchange="updateBuilderUnitField(${idx}, 'unit_tier', this.value)" ${isSolo ? 'disabled title="1 Enemy is automatically a Boss Encounter"' : ''}>
            ${tierOptions}
          </select>
        </div>
        <div class="builder-ctrl-item">
          <span>Role:</span>
          <select onchange="updateBuilderUnitField(${idx}, 'combat_role', this.value)">
            ${roleOptions}
          </select>
        </div>
        <div class="builder-ctrl-item">
          <span>Race:</span>
          <select onchange="updateBuilderUnitField(${idx}, 'race', this.value)">
            ${raceOptions}
          </select>
        </div>
        <div class="builder-ctrl-item">
          <span>Lvl:</span>
          <select onchange="updateBuilderUnitField(${idx}, 'level_offset', this.value)">
            ${offsetOptions}
          </select>
        </div>
        <div class="builder-ctrl-item">
          <span>Def:</span>
          <select onchange="updateBuilderUnitField(${idx}, 'defense_profile', this.value)">
            ${defOptions}
          </select>
        </div>
        <div class="builder-card-actions">
          <button type="button" class="btn-mini" onclick="duplicateBuilderUnit(${idx})" title="Duplicate this enemy">+ Copy</button>
          <button type="button" class="btn-mini danger" onclick="removeBuilderUnit(${idx})" ${isSolo ? 'disabled title="Encounter requires at least 1 enemy"' : 'title="Remove this enemy"'}>&#x2715;</button>
        </div>
      </div>
    `;
  }

  function renderEncounter(enc) {
    const container = document.getElementById('resultsArea');
    const p = enc.party_config;
    const a = enc.analysis;

    const raceBadge = enc.selected_race
      ? `<span class="tag tag-gold">Race: ${escapeHtml(enc.selected_race)}</span>`
      : '';
    const lwBadge = p.is_lone_wolf
      ? `<span class="tag tag-crimson">Lone Wolf Active</span>`
      : '';
    const builderBadge = ACTIVE_MODE === 'builder'
      ? `<span class="tag tag-crimson">Interactive Builder (${enc.enemies.length === 1 ? 'Solo Boss Rule' : 'Auto-Balanced'})</span>`
      : '';
    const customizeBtnHtml = ACTIVE_MODE === 'auto'
      ? `<button type="button" class="btn" onclick="importCurrentEncounterToBuilder()">&#x2692; Customize in Builder</button>`
      : '';

    const enemyCardsHtml = enc.enemies.map((e, arrIdx) => {
      const isBoss = e.archetype_key === 'BOSS';
      const cardTotal = (e.stats.physical_armor + e.stats.magic_armor + e.stats.vitality) || 1;
      const physPct = Math.min(100, Math.max(0, Math.round((e.stats.physical_armor / cardTotal) * 100)));
      const magPct  = Math.min(100, Math.max(0, Math.round((e.stats.magic_armor / cardTotal) * 100)));
      const vitPct  = Math.min(100, Math.max(0, Math.round((e.stats.vitality / cardTotal) * 100)));

      const abilitiesPills = Object.entries(e.stats.combat_abilities)
        .map(([k, v]) => `<span class="mini-pill">${escapeHtml(k)} ${v}</span>`)
        .join('') || '<span class="mini-pill">None</span>';

      const talentPills = e.stats.talents
        .map(t => `<span class="mini-pill talent">${escapeHtml(t)}</span>`)
        .join('') || '<span class="mini-pill">None</span>';

      const resistEntries = Object.entries(e.stats.resistances || {});
      const resistHtml = resistEntries.length > 0
        ? `<div class="trait-line"><strong>Resistances:</strong> <div class="pill-list">${
            resistEntries.map(([elem, val]) => {
              const cls = val < 0 ? 'vuln' : 'resist';
              const sign = val > 0 ? '+' : '';
              return `<span class="mini-pill ${cls}">${escapeHtml(elem)} ${sign}${val}%</span>`;
            }).join('')
          }</div></div>`
        : '';

      const defenseThemeHtml = e.defense_theme
        ? `<div class="trait-line"><strong>Defense Profile:</strong> <span>${escapeHtml(e.defense_theme)}</span></div>`
        : '';

      const skillsHtml = e.skills.map(s => {
        const innateTag = s.is_innate ? `<span class="skill-badge innate">Innate</span>` : '';
        const statusTag = s.status_applied ? `<span class="skill-badge status">${escapeHtml(s.status_applied)}</span>` : '';
        const reqTag = (!s.is_innate && s.requirements_display && s.requirements_display !== 'None')
          ? `<span class="skill-badge req" title="Required Combat Abilities: ${escapeHtml(s.requirements_display)}">${escapeHtml(s.requirements_display)}</span>`
          : '';
        const removeBtn = (ACTIVE_MODE === 'builder')
          ? `<button type="button" class="btn-skill-remove" onclick="removeBuilderUnitSkill(${arrIdx}, '${escapeJsStr(s.name)}')" title="Remove skill ${escapeHtml(s.name)}">&#x2715;</button>`
          : '';
        return `
          <div class="skill-item" title="${escapeHtml(s.description)} (Req: ${escapeHtml(s.requirements_display || 'None')})">
            <div class="skill-left">
              <span class="skill-name">${escapeHtml(s.name)}</span>
              <span class="skill-school">(${escapeHtml(s.school)} &bull; ${escapeHtml(s.damage_type)})</span>
              ${reqTag}
              ${innateTag}
              ${statusTag}
            </div>
            <div class="skill-right">
              <span class="skill-ap">${s.ap_cost} AP</span>
              ${removeBtn}
            </div>
          </div>
        `;
      }).join('');

      const showRoleTag = e.title && e.title !== 'Combatant' && !e.archetype.toLowerCase().includes(e.title.toLowerCase());
      const roleTagStr = showRoleTag ? ` (${escapeHtml(e.title)})` : '';
      const builderControlsHtml = renderBuilderCardControls(e, arrIdx);

      return `
        <div class="enemy-card ${isBoss ? 'is-boss' : ''}">
          <div class="card-top">
            <div>
              <div class="npc-name">[${e.index}] ${escapeHtml(e.name)}</div>
              <div class="npc-sub">Lvl ${e.level} &bull; ${escapeHtml(e.race)} &bull; ${escapeHtml(e.archetype)}${roleTagStr}</div>
            </div>
            <div class="asset-pill">
              ID: ${escapeHtml(e.gm_template_id)}
            </div>
          </div>
          ${builderControlsHtml}

          <div class="card-body">
            <div class="bars-container">
              <div class="stat-bar-row">
                <span class="bar-label">Phys Armor</span>
                <div class="bar-track"><div class="bar-fill bar-phys" style="width: ${physPct}%"></div></div>
                <span class="bar-number" style="color: #e6c875;">${e.stats.physical_armor.toLocaleString()}</span>
              </div>
              <div class="stat-bar-row">
                <span class="bar-label">Magic Armor</span>
                <div class="bar-track"><div class="bar-fill bar-mag" style="width: ${magPct}%"></div></div>
                <span class="bar-number" style="color: #7cc0ff;">${e.stats.magic_armor.toLocaleString()}</span>
              </div>
              <div class="stat-bar-row">
                <span class="bar-label">Vitality (HP)</span>
                <div class="bar-track"><div class="bar-fill bar-vit" style="width: ${vitPct}%"></div></div>
                <span class="bar-number" style="color: #ff8585;">${e.stats.vitality.toLocaleString()}</span>
              </div>
            </div>

            <div class="combat-strip">
              <div class="strip-item"><span>AP:</span> <strong class="ap-highlight">${e.stats.ap_start}/${e.stats.ap_max} (+${e.stats.ap_recovery}/turn)</strong></div>
              <div class="strip-item"><span>Initiative:</span> <strong>${e.stats.initiative}</strong></div>
              <div class="strip-item"><span>Equip:</span> <strong>${escapeHtml(e.equipment)}</strong></div>
            </div>

            <div class="attr-grid">
              <div class="attr-box"><span class="a-name">STR</span><span class="a-val">${e.stats.strength}</span></div>
              <div class="attr-box"><span class="a-name">FIN</span><span class="a-val">${e.stats.finesse}</span></div>
              <div class="attr-box"><span class="a-name">INT</span><span class="a-val">${e.stats.intelligence}</span></div>
              <div class="attr-box"><span class="a-name">CON</span><span class="a-val">${e.stats.constitution}</span></div>
              <div class="attr-box"><span class="a-name">MEM</span><span class="a-val">${e.stats.memory}</span></div>
              <div class="attr-box"><span class="a-name">WIT</span><span class="a-val">${e.stats.wits}</span></div>
            </div>

            <div class="traits-block">
              <div class="trait-line"><strong>Abilities:</strong> <div class="pill-list">${abilitiesPills}</div></div>
              <div class="trait-line"><strong>Talents:</strong> <div class="pill-list">${talentPills}</div></div>
              ${resistHtml}
              ${defenseThemeHtml}
            </div>

            <div class="skills-section">
              <div class="skills-header">
                <span>Skills &amp; Spellbook</span>
                <span>Memory Slots: ${e.used_memory_slots} / ${e.max_memory_slots}</span>
              </div>
              <div class="skills-list">
                ${skillsHtml}
              </div>
              ${renderSkillPickerRow(arrIdx, e.skills)}
            </div>
          </div>

          <div class="tactics-box">
            <div><strong>AI Tactics:</strong> ${escapeHtml(e.ai_tactics)}</div>
            <div style="margin-top: 3px;"><strong>GM Note:</strong> ${escapeHtml(e.gm_notes)}</div>
          </div>
        </div>
      `;
    }).join('');

    const recsHtml = a.tactical_recommendations.map(r => `<li>${escapeHtml(r)}</li>`).join('');
    const dialsHtml = Object.entries(a.tuning_dials)
      .map(([k, v]) => `<li><strong>${escapeHtml(k)}:</strong> ${escapeHtml(v)}</li>`)
      .join('');
    const hazardsHtml = enc.environmental_hazards.map(h => `<li>${escapeHtml(h)}</li>`).join('');

    container.innerHTML = `
      <div class="encounter-banner">
        <div class="encounter-title-block">
          <h2>${escapeHtml(enc.name)}</h2>
          <div class="encounter-tags">
            <span class="tag tag-gold">${escapeHtml(enc.faction)}</span>
            <span class="tag">${escapeHtml(enc.encounter_type)}</span>
            <span class="tag">Party Lvl ${p.level} (${p.party_size} Players)</span>
            <span class="tag">${escapeHtml(p.difficulty)}</span>
            ${lwBadge}
            ${raceBadge}
            ${builderBadge}
          </div>
        </div>
        ${customizeBtnHtml}
      </div>

      <div class="roster-header">
        <h3>Enemy Bestiary Roster (${enc.enemies.length} Combatant${enc.enemies.length === 1 ? '' : 's'})</h3>
      </div>

      <div class="enemy-grid">
        ${enemyCardsHtml}
      </div>

      <div class="overview-grid">
        <div class="info-box">
          <h3>Encounter Balance &amp; Action Economy</h3>
          <div class="verdict-banner">
            <strong>Verdict:</strong> ${escapeHtml(a.overall_difficulty_assessment)}
          </div>
          <div class="metrics-row">
            <div class="metric-card">
              <div class="metric-label">Action Economy</div>
              <div class="metric-val">${a.party_total_ap} vs ${a.enemy_total_ap} AP</div>
              <div class="metric-sub">Party AP vs Enemy AP / Round</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">Effective Health (EHP)</div>
              <div class="metric-val">${a.party_expected_ehp.toLocaleString()} vs ${a.enemy_total_ehp.toLocaleString()}</div>
              <div class="metric-sub">Party EHP vs Enemy Total EHP</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">Damage Synergy</div>
              <div class="metric-val" style="font-size: 0.92rem;">${escapeHtml(a.damage_compatibility_rating)}</div>
              <div class="metric-sub">${escapeHtml(p.damage_profile)}</div>
            </div>
          </div>
          <ul class="advice-list">
            <li>${escapeHtml(a.ap_ratio_explanation)}</li>
            <li>${escapeHtml(a.ehp_ratio_explanation)}</li>
            <li>${escapeHtml(a.damage_compatibility_notes)}</li>
          </ul>
        </div>

        <div class="info-box">
          <h3>Battlefield Setup &amp; GM Tuning Dials</h3>
          <div style="font-size: 0.82rem; margin-bottom: 10px;">
            <strong style="color: var(--text-gold);">Terrain:</strong> ${escapeHtml(enc.tactical_terrain)}
          </div>
          <div style="font-size: 0.78rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px; font-weight: 600;">
            Environmental Hazards
          </div>
          <ul class="advice-list" style="margin-bottom: 12px;">
            ${hazardsHtml}
          </ul>
          <div style="font-size: 0.78rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px; font-weight: 600;">
            Live GM Tuning Dials &amp; Tactical Recommendations
          </div>
          <ul class="advice-list">
            ${recsHtml}
            ${dialsHtml}
          </ul>
        </div>
      </div>
    `;
  }

  initApp();
</script>
</body>
</html>
"""


class EncounterGUIHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for the local DOS2 GM Encounter Balancer Web UI."""

    output_dir: str = "."

    def log_message(self, format: str, *args: Any) -> None:
        # Suppress noisy per-request HTTP logs in console
        pass

    def _send_json(self, data: Dict[str, Any], status: int = 200) -> None:
        raw = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _send_html(self, html: str, status: int = 200) -> None:
        raw = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self._send_html(HTML_DASHBOARD)
        elif parsed.path == "/api/meta":
            self._send_json(get_gui_metadata())
        else:
            self._send_json({"error": "Not found"}, status=404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        if parsed.path == "/api/generate":
            enc = build_encounter_from_payload(payload)
            self._send_json(serialize_encounter(enc))
        elif parsed.path == "/api/build_custom":
            enc = build_custom_encounter_from_payload(payload)
            self._send_json(serialize_encounter(enc))
        elif parsed.path == "/api/export":
            if payload.get("mode") == "builder" or "enemies" in payload:
                enc = build_custom_encounter_from_payload(payload)
            else:
                enc = build_encounter_from_payload(payload)
            os.makedirs(self.output_dir, exist_ok=True)
            filepath = export_encounter_to_markdown(enc, output_dir=self.output_dir)
            self._send_json({
                "filepath": os.path.abspath(filepath),
                "filename": os.path.basename(filepath),
            })
        else:
            self._send_json({"error": "Not found"}, status=404)


def launch_web_gui(
    host: str = "127.0.0.1",
    port: int = 8765,
    output_dir: str = ".",
    open_browser: bool = True,
) -> HTTPServer:
    """Starts the local Web UI HTTP server and optionally opens the default browser."""
    EncounterGUIHandler.output_dir = output_dir
    # Try preferred port, or fallback to OS-assigned free port if busy
    try:
        server = HTTPServer((host, port), EncounterGUIHandler)
    except OSError:
        server = HTTPServer((host, 0), EncounterGUIHandler)

    actual_port = server.server_address[1]
    url = f"http://{host}:{actual_port}"

    print("=" * 72)
    print("  DIVINITY: ORIGINAL SIN 2 - GM ENCOUNTER BALANCER (LOCAL WEB UI)")
    print("=" * 72)
    print(f"  [+] Dashboard running at: {url}")
    print("  [+] Press Ctrl+C in this terminal to stop the server.")
    print("=" * 72)

    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    return server
