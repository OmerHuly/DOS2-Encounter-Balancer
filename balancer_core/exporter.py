"""
DOS2 Encounter Balancer - Terminal Presentation & Markdown Exporter
Renders clean, readable battle cards for the terminal and generates
comprehensive Markdown battle notes for GM session tracking.
"""

import os
import textwrap
from datetime import datetime
from typing import Optional
from .models import Encounter, NPC


def format_enemy_terminal_card(npc: NPC, index: int) -> str:
    """Formats an individual NPC stat block for terminal display."""
    lines = []
    lines.append(f"┌{'─' * 70}┐")
    raw_header = f"  [{index}] {npc.name.upper()} - Lvl {npc.level} ({npc.race.value} | {npc.archetype.name.capitalize()})"
    header = raw_header[:68] if len(raw_header) > 68 else raw_header
    lines.append(f"│{header:<70}│")
    if npc.gm_template_id:
        tpl_line = f"  GM Engine Asset: {npc.gm_template_id}"
        lines.append(f"│{tpl_line:<70}│")
    lines.append(f"├{'─' * 70}┤")
    
    # Core Defenses & Turn Economy
    defenses = (
        f"  Vitality: {npc.stats.vitality:,}  │  "
        f"Phys Armor: {npc.stats.physical_armor:,}  │  "
        f"Magic Armor: {npc.stats.magic_armor:,}"
    )
    lines.append(f"│{defenses:<70}│")
    
    ap_init = (
        f"  AP: {npc.stats.ap_start}/{npc.stats.ap_max} (+{npc.stats.ap_recovery}/rnd)  │  "
        f"Initiative: {npc.stats.initiative}  │  "
        f"Equip: {npc.equipment[:25]}"
    )
    lines.append(f"│{ap_init:<70}│")
    
    # Attributes
    attrs = (
        f"  STR: {npc.stats.strength}  FIN: {npc.stats.finesse}  "
        f"INT: {npc.stats.intelligence}  CON: {npc.stats.constitution}  "
        f"MEM: {npc.stats.memory}  WIT: {npc.stats.wits}"
    )
    lines.append(f"│{attrs:<70}│")
    
    # Combat Abilities & Talents
    abilities_str = ", ".join(f"{k} {v}" for k, v in npc.stats.combat_abilities.items()) or "None"
    talents_str = ", ".join(npc.stats.talents) or "None"
    ab_line = f"  Abilities: {abilities_str[:58]}"
    lines.append(f"│{ab_line:<70}│")
    tal_line = f"  Talents:   {talents_str[:58]}"
    lines.append(f"│{tal_line:<70}│")

    # Skills (Innate & Memorized)
    lines.append(f"├{'─' * 70}┤")
    skill_header = f"  SKILLS (Memory Slots: {npc.used_memory_slots}/{npc.max_memory_slots}):"
    lines.append(f"│{skill_header:<70}│")
    for s in npc.skills:
        cc_tag = f" [{s.status_applied}]" if s.status_applied else ""
        innate_tag = " [Innate]" if s.is_innate else ""
        skill_str = f"   • {s.name} ({s.school}, {s.ap_cost} AP, {s.damage_type}){innate_tag}{cc_tag}"
        lines.append(f"│{skill_str:<70}│")

    # AI Tactics & GM Notes
    lines.append(f"├{'─' * 70}┤")
    wrapped_tac = textwrap.wrap(npc.ai_tactics, width=64) if npc.ai_tactics else []
    if wrapped_tac:
        lines.append(f"│  AI: {wrapped_tac[0]:<64}│")
        for extra in wrapped_tac[1:3]:
            lines.append(f"│      {extra:<64}│")
    else:
        lines.append(f"│  AI: {'Standard tactical engagement':<64}│")

    lines.append(f"└{'─' * 70}┘")
    return "\n".join(lines)


def format_encounter_terminal(encounter: Encounter) -> str:
    """Formats full encounter overview, balance metrics, and enemy cards for terminal."""
    output = []
    
    # Banner
    output.append("=" * 72)
    output.append(f"  DIVINITY: ORIGINAL SIN 2 - GM ENCOUNTER BALANCER")
    output.append(f"  {encounter.name}")
    output.append("=" * 72)
    
    # Party Summary
    p = encounter.party_config
    lw_str = " (Lone Wolf Active)" if p.is_lone_wolf else ""
    output.append(f"► PARTY PROFILE:")
    output.append(f"  • Level: {p.level}  |  Party Size: {p.party_size}{lw_str}  |  Difficulty: {p.difficulty.value}")
    output.append(f"  • Damage Focus: {p.damage_profile.value}")
    output.append(f"  • Party AP / Round: {p.total_ap_per_round} AP")
    if encounter.selected_race:
        output.append(f"  • Enemy Race Filter: {encounter.selected_race.value} (Single Race Encounter)")
    output.append("")

    # Tactical Battlefield
    output.append(f"► TACTICAL BATTLEFIELD SETUP:")
    output.append(f"  • Terrain: {encounter.tactical_terrain}")
    output.append(f"  • Environmental Hazards:")
    for h in encounter.environmental_hazards:
        output.append(f"     - {h}")
    output.append("")

    # Balance Analytics
    if encounter.analysis:
        a = encounter.analysis
        output.append("► BALANCE & ENCOUNTER HEALTH CHECK:")
        output.append(f"  • Verdict: {a.overall_difficulty_assessment}")
        output.append(f"  • Action Economy: {a.party_total_ap} Party AP vs {a.enemy_total_ap} Enemy AP")
        output.append(f"    └─ {a.ap_ratio_explanation}")
        output.append(f"  • Durability: {a.party_expected_ehp:,} Party EHP vs {a.enemy_total_ehp:,} Enemy EHP")
        output.append(f"    └─ {a.ehp_ratio_explanation}")
        output.append(f"  • Damage Profile Synergy: {a.damage_compatibility_rating}")
        output.append(f"    └─ {a.damage_compatibility_notes}")
        output.append("")
        output.append(f"► ON-THE-FLY GM TUNING DIALS:")
        for trigger, advice in a.tuning_dials.items():
            output.append(f"  • {trigger}: {advice}")
        output.append("")

    # Enemy Roster
    output.append(f"► ENEMY ROSTER ({len(encounter.enemies)} Combatants):")
    for i, npc in enumerate(encounter.enemies, 1):
        output.append(format_enemy_terminal_card(npc, i))
        output.append("")

    return "\n".join(output)


def export_encounter_to_markdown(encounter: Encounter, output_dir: str = ".") -> str:
    """Exports the complete encounter as a professional Markdown GM Battle Sheet."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_faction = encounter.faction.name.lower()
    clean_type = encounter.encounter_type.name.lower()
    filename = f"encounter_lvl{encounter.party_config.level}_{clean_faction}_{clean_type}_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)

    p = encounter.party_config
    a = encounter.analysis

    content = []
    content.append(f"# ⚔️ DOS2 GM Battle Sheet: {encounter.name}")
    content.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} for Divinity: Original Sin 2 Definitive Edition*")
    content.append("")
    content.append("---")
    content.append("")
    
    # Party Overview Table
    content.append("## 👥 Party Configuration")
    content.append("| Parameter | Value |")
    content.append("| :--- | :--- |")
    content.append(f"| **Party Level** | Level {p.level} |")
    content.append(f"| **Party Size** | {p.party_size} Players {'(Lone Wolf Active)' if p.is_lone_wolf else ''} |")
    content.append(f"| **Party Total AP/Round** | {p.total_ap_per_round} AP |")
    content.append(f"| **Damage Profile** | {p.damage_profile.value} |")
    content.append(f"| **Target Difficulty** | {p.difficulty.value} |")
    if encounter.selected_race:
        content.append(f"| **Enemy Race Filter** | {encounter.selected_race.value} (Single Race Encounter) |")
    content.append("")

    # Battlefield & Terrain
    content.append("## 🗺️ Tactical Battlefield Setup")
    content.append(f"> **Terrain Feature:** {encounter.tactical_terrain}")
    content.append("")
    content.append("### Environmental Surfaces & Props")
    for h in encounter.environmental_hazards:
        content.append(f"- **{h.split('(')[0].strip()}**: {h}")
    content.append("")

    # Balance Analytics Section
    if a:
        content.append("## ⚖️ Encounter Balance Assessment")
        content.append(f"> [!IMPORTANT]\n> **Overall Verdict:** {a.overall_difficulty_assessment}")
        content.append("")
        content.append("| Metric | Party | Enemies | Analysis |")
        content.append("| :--- | :--- | :--- | :--- |")
        content.append(f"| **Action Economy (AP/Rnd)** | {a.party_total_ap} AP | {a.enemy_total_ap} AP | {a.ap_ratio_explanation} |")
        content.append(f"| **Effective Health (EHP)** | {a.party_expected_ehp:,} | {a.enemy_total_ehp:,} | {a.ehp_ratio_explanation} |")
        content.append(f"| **Damage Type Fit** | {p.damage_profile.value} | Physical: {sum(n.stats.physical_armor for n in encounter.enemies):,} / Magic: {sum(n.stats.magic_armor for n in encounter.enemies):,} | {a.damage_compatibility_notes} |")
        content.append("")
        content.append("### 🎯 GM Tactical Tips")
        for tip in a.tactical_recommendations:
            content.append(f"- {tip}")
        content.append("")
        content.append("### 🎛️ On-The-Fly Balance Dials")
        for dial, note in a.tuning_dials.items():
            content.append(f"- **{dial}:** {note}")
        content.append("")

    # Enemy Cards
    content.append("## 👹 Enemy Bestiary & Stat Blocks")
    content.append("")
    for i, npc in enumerate(encounter.enemies, 1):
        content.append(f"### {i}. {npc.name} ({npc.race.value} • {npc.archetype.value}) - Level {npc.level}")
        gm_tag = f" • GM Template: `{npc.gm_template_id}`" if npc.gm_template_id else ""
        content.append(f"*{npc.title} • {npc.faction.value}{gm_tag}*")
        content.append("")
        content.append("| Stat | Value | Stat | Value |")
        content.append("| :--- | :--- | :--- | :--- |")
        content.append(f"| **Vitality (HP)** | **{npc.stats.vitality:,}** | **Initiative** | **{npc.stats.initiative}** |")
        content.append(f"| **Physical Armor** | **{npc.stats.physical_armor:,}** | **Action Points** | **{npc.stats.ap_start}/{npc.stats.ap_max} (+{npc.stats.ap_recovery})** |")
        content.append(f"| **Magic Armor** | **{npc.stats.magic_armor:,}** | **Equipment** | {npc.equipment} |")
        content.append("")
        
        # Attributes Table
        content.append("**Attributes:**")
        content.append(f"- `STR: {npc.stats.strength}` | `FIN: {npc.stats.finesse}` | `INT: {npc.stats.intelligence}` | `CON: {npc.stats.constitution}` | `MEM: {npc.stats.memory}` | `WIT: {npc.stats.wits}`")
        content.append("")
        
        # Combat Abilities & Talents
        content.append(f"- **Combat Abilities:** {', '.join(f'{k} {v}' for k, v in npc.stats.combat_abilities.items()) or 'None'}")
        content.append(f"- **Talents:** {', '.join(npc.stats.talents) or 'None'}")
        content.append("")

        # Skills (Innate & Memorized)
        content.append(f"**Skills (Memory Slots Used: {npc.used_memory_slots}/{npc.max_memory_slots}):**")
        content.append("| Skill | School | AP | Type | Memory | Effect / Description |")
        content.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for s in npc.skills:
            status_text = f"**[{s.status_applied}]** " if s.status_applied else ""
            mem_text = "0 (Innate)" if s.is_innate else f"{s.memory_cost}"
            content.append(f"| `{s.name}` | {s.school} ({s.tier}) | {s.ap_cost} AP | {s.damage_type} | {mem_text} | {status_text}{s.description} |")
        content.append("")

        # GM Tactics
        content.append(f"> **AI Behavior:** {npc.ai_tactics}")
        content.append(f"> **GM Mode Setup Note:** {npc.gm_notes}")
        content.append("")
        content.append("---")
        content.append("")

    # Setup Guide for GM Mode
    content.append("## 🛠️ Step-by-Step Setup in DOS2 GM Mode")
    content.append("1. **Spawn NPCs:** In the GM Mode interface, open the **Creatures** panel and drag the matching base models onto the board.")
    content.append("2. **Set Level & Resync:** Use the Level slider to adjust each creature to the exact level indicated. If armor numbers look desynced, slide the level up by 1 and back down.")
    content.append("3. **Input Armor & Vitality:** Inspect the creature's Character Sheet and enter the exact Vitality, Physical Armor, and Magic Armor numbers.")
    content.append("4. **Assign Skills:** In the Character Sheet skill tab, ensure Memory is sufficient and drag the recommended skills into the creature's action bar.")
    content.append("5. **Place Hazards:** Drop the recommended barrels or create oil/water surfaces before triggering the encounter or de-cloaking ambushes.")
    content.append("")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(content))

    return filepath
