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
from .generator import generate_encounter, DEFENSE_PROFILES
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
            "can_be_boss": t.can_be_boss or t.archetype.name == "BOSS",
        }
        for t in BESTIARY
    ]

    return {
        "factions": factions,
        "faction_races": faction_races,
        "encounter_types": encounter_types,
        "damage_profiles": damage_profiles,
        "difficulties": difficulties,
        "defense_profiles": defense_profiles,
        "boss_templates": boss_templates,
        "all_templates": all_templates,
    }


def serialize_npc(npc: NPC, index: int) -> Dict[str, Any]:
    """Serializes an NPC dataclass to a JSON-ready dictionary."""
    return {
        "index": index,
        "name": npc.name,
        "title": npc.title,
        "faction": npc.faction.value,
        "faction_key": npc.faction.name,
        "race": npc.race.value,
        "race_key": npc.race.name,
        "archetype": npc.archetype.value,
        "archetype_key": npc.archetype.name,
        "level": npc.level,
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
        "enemies": [serialize_npc(npc, idx) for idx, npc in enumerate(encounter.enemies, 1)],
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

  .skill-ap {
    font-family: var(--font-mono);
    font-size: 0.74rem;
    color: var(--ap-green);
    white-space: nowrap;
    font-weight: 600;
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
    <div class="panel-section-title">1. Player Party Profile</div>
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
  let debounceTimer = null;
  let activeRequestId = 0;

  function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2600);
  }

  function scheduleGenerate(delayMs = 150) {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      generateEncounter();
    }, delayMs);
  }

  async function initApp() {
    const res = await fetch('/api/meta');
    META = await res.json();

    populateSelect('damageProfile', META.damage_profiles);
    populateSelect('difficulty', META.difficulties);
    populateSelect('encounterType', META.encounter_types, 'STANDARD');
    populateSelect('factionSelect', META.factions, 'ANY');
    populateSelect('defenseProfile', META.defense_profiles, 'auto');

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
      if ((defaultVal && item.value === defaultVal) || (!defaultVal && idx === 0)) {
        opt.selected = true;
      }
      el.appendChild(opt);
    });
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
  }

  function bindEvents() {
    document.getElementById('partySize').addEventListener('change', () => {
      const ps = parseInt(document.getElementById('partySize').value, 10);
      const lw = document.getElementById('isLoneWolf').checked && (ps <= 2);
      if (lw) {
        document.getElementById('minionCount').value = '2';
      }
      syncDynamicControls();
      generateEncounter();
    });

    document.getElementById('partyLevel').addEventListener('change', () => {
      let val = parseInt(document.getElementById('partyLevel').value, 10);
      if (isNaN(val) || val < 1) val = 1;
      if (val > 25) val = 25;
      document.getElementById('partyLevel').value = val;
      generateEncounter();
    });

    document.getElementById('partyLevel').addEventListener('input', () => {
      const val = parseInt(document.getElementById('partyLevel').value, 10);
      if (!isNaN(val) && val >= 1 && val <= 25) {
        scheduleGenerate(120);
      }
    });

    document.getElementById('isLoneWolf').addEventListener('change', (e) => {
      document.getElementById('minionCount').value = e.target.checked ? '2' : '3';
      syncDynamicControls();
      generateEncounter();
    });

    document.getElementById('damageProfile').addEventListener('change', () => generateEncounter());
    document.getElementById('difficulty').addEventListener('change', () => generateEncounter());

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
      scheduleGenerate(220);
    });

    document.getElementById('defenseProfile').addEventListener('change', () => generateEncounter());

    document.getElementById('factionSelect').addEventListener('change', () => {
      syncDynamicControls();
      generateEncounter();
    });

    document.getElementById('raceSelect').addEventListener('change', () => generateEncounter());

    document.getElementById('btnGenerate').addEventListener('click', () => generateEncounter(true));

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
      const res = await fetch('/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(getFormPayload())
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

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function renderEncounter(enc) {
    const container = document.getElementById('resultsArea');
    const p = enc.party_config;
    const a = enc.analysis;

    // Calculate max stat across all enemies for proportional visual bars
    let maxBarVal = 100;
    enc.enemies.forEach(e => {
      maxBarVal = Math.max(maxBarVal, e.stats.vitality, e.stats.physical_armor, e.stats.magic_armor);
    });

    const raceBadge = enc.selected_race
      ? `<span class="tag tag-gold">Race Filter: ${escapeHtml(enc.selected_race)} Only</span>`
      : '';
    const lwBadge = p.is_lone_wolf
      ? `<span class="tag tag-crimson">Lone Wolf Active</span>`
      : '';

    const enemyCardsHtml = enc.enemies.map(e => {
      const isBoss = e.archetype_key === 'BOSS';
      const physPct = Math.min(100, Math.round((e.stats.physical_armor / maxBarVal) * 100));
      const magPct  = Math.min(100, Math.round((e.stats.magic_armor / maxBarVal) * 100));
      const vitPct  = Math.min(100, Math.round((e.stats.vitality / maxBarVal) * 100));

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
        return `
          <div class="skill-item" title="${escapeHtml(s.description)}">
            <div class="skill-left">
              <span class="skill-name">${escapeHtml(s.name)}</span>
              <span class="skill-school">(${escapeHtml(s.school)} &bull; ${escapeHtml(s.damage_type)})</span>
              ${innateTag}
              ${statusTag}
            </div>
            <span class="skill-ap">${s.ap_cost} AP</span>
          </div>
        `;
      }).join('');

      const showRoleTag = e.title && e.title !== 'Combatant' && !e.archetype.toLowerCase().includes(e.title.toLowerCase());
      const roleTagStr = showRoleTag ? ` (${escapeHtml(e.title)})` : '';

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
          </div>
        </div>
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
        elif parsed.path == "/api/export":
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
