"""
DOS2 Encounter Balancer - Generation & Balance Analysis Engine
Generates tactically sound, faction-coherent encounters matching DOS2 GM mode mechanics
and evaluates balance metrics (Action Economy, EHP ratio, Damage Profile compatibility).
"""

import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from .models import (
    PartyConfig,
    Encounter,
    EncounterType,
    Faction,
    Archetype,
    NPC,
    EnemyStats,
    EncounterBalanceAnalysis,
    DamageProfile,
    Difficulty,
    Race,
    Skill,
)
from .formulas import (
    calculate_enemy_stats,
    estimate_party_ehp,
    get_base_vitality,
    get_base_armor,
    sync_stats_with_combat_abilities,
    calculate_talents,
    validate_and_filter_talents,
)
from .skills_db import get_skills_for_archetype
from .bestiary import (
    get_templates_by_faction,
    BestiaryTemplate,
    BESTIARY,
    find_template_by_name,
    create_custom_boss_template,
)


def analyze_encounter_balance(
    party_config: PartyConfig,
    enemies: List[NPC],
    encounter_type: EncounterType,
    minion_count: Optional[int] = None,
    boss_scaling_notes: Optional[str] = None,
) -> EncounterBalanceAnalysis:
    """
    Evaluates the mathematical and tactical fairness of the encounter.
    Compares AP economy, EHP pools, and damage type alignment.
    """
    party_ap = party_config.total_ap_per_round
    enemy_ap = sum(npc.stats.ap_recovery for npc in enemies)
    
    party_ehp = estimate_party_ehp(party_config)
    enemy_ehp = sum(npc.total_ehp for npc in enemies)
    
    total_enemy_phys_armor = sum(npc.stats.physical_armor for npc in enemies)
    total_enemy_magic_armor = sum(npc.stats.magic_armor for npc in enemies)
    
    # AP Ratio Analysis
    ap_ratio = enemy_ap / max(1, party_ap)
    if ap_ratio > 1.3:
        ap_explanation = (
            f"Enemies hold a significant Action Economy advantage ({enemy_ap} AP vs {party_ap} AP). "
            "Due to round-robin turns, players may face heavy incoming pressure if enemies are not CC'd quickly."
        )
    elif ap_ratio < 0.8:
        ap_explanation = (
            f"Players hold the Action Economy advantage ({party_ap} AP vs {enemy_ap} AP). "
            "Boss/elite enemies must rely on high armor buffer or area denial to avoid being locked down."
        )
    else:
        ap_explanation = (
            f"Balanced Action Economy ({party_ap} Party AP vs {enemy_ap} Enemy AP). "
            "Combat will closely mirror the classic round-robin tactical tempo."
        )

    # EHP Ratio Analysis
    ehp_ratio = enemy_ehp / max(1, party_ehp)
    if ehp_ratio > 1.8:
        ehp_explanation = (
            f"Enemy Total EHP ({enemy_ehp:,}) significantly exceeds Party EHP ({party_ehp:,}) [Ratio: {ehp_ratio:.2f}x]. "
            "Expect a high-endurance battle requiring smart positioning and crowd control."
        )
    elif ehp_ratio < 0.9:
        ehp_explanation = (
            f"Party EHP ({party_ehp:,}) exceeds Enemy EHP ({enemy_ehp:,}) [Ratio: {ehp_ratio:.2f}x]. "
            "Players will defeat enemies relatively swiftly if they execute their rotations."
        )
    else:
        ehp_explanation = (
            f"Well-matched durability: Enemy EHP ({enemy_ehp:,}) vs Party EHP ({party_ehp:,}) [Ratio: {ehp_ratio:.2f}x]. "
            "Ideal for a tense, rewarding back-and-forth engagement."
        )

    # Damage Type Compatibility Check
    compat_rating = "Favorable & Engaging"
    compat_notes = ""
    
    if party_config.damage_profile == DamageProfile.PURE_PHYSICAL:
        if total_enemy_phys_armor > total_enemy_magic_armor * 1.4:
            compat_rating = "Challenging (High Physical Defense)"
            compat_notes = (
                "Your party deals 100% Physical damage, but enemies possess substantial Physical Armor. "
                "Players must rely on high-burst Warfare skills and Knockdowns once armor breaks. "
                "Enemies with high Magic Armor will waste some of their defensive budget against this party."
            )
        else:
            compat_notes = (
                "Pure Physical party matches well against the enemy roster. "
                "Prioritize eliminating low-armor mages/archers first to trigger Executioner."
            )
    elif party_config.damage_profile == DamageProfile.PURE_MAGICAL:
        if total_enemy_magic_armor > total_enemy_phys_armor * 1.4:
            compat_rating = "Challenging (High Magic Defense)"
            compat_notes = (
                "Your party deals 100% Magical damage, but enemies have high Magic Armor pools. "
                "Remind players to capitalize on elemental surfaces (Fire/Water/Air) to strip armor collaboratively."
            )
        else:
            compat_notes = (
                "Pure Magic party has advantageous targets against low-magic-armor brutes and warriors. "
                "Look for surface combos (e.g. Rain + Shock) to chain stun."
            )
    else:
        compat_notes = (
            "Split damage composition creates the quintessential DOS2 tactical puzzle: "
            "Physical damage dealers should target low-physical-armor casters/rogues, "
            "while Mages focus down heavy-armor warriors and tanks."
        )

    # Overall Difficulty Assessment
    if party_config.difficulty == Difficulty.DEADLY or (ehp_ratio > 2.0 and ap_ratio > 1.3):
        overall_assessment = "DEADLY (Lethal threat; high wipe potential without flawless tactics)"
    elif party_config.difficulty == Difficulty.TACTICIAN or ehp_ratio > 1.4:
        overall_assessment = "TACTICIAN (Demanding; punishes misplays and rewards surface mastery)"
    elif party_config.difficulty == Difficulty.STORY or ehp_ratio < 0.8:
        overall_assessment = "STORY (Relaxed; players will triumph comfortably with minimal attrition)"
    else:
        overall_assessment = "REWARDING & BALANCED (Classic sweet spot: engaging, tactical, fair)"

    # Tactical GM Recommendations
    tactical_recs = [
        "Turn 1 Initiative: Use the highest-initiative enemy to reposition or set an elemental surface rather than instant burst.",
        "Round-Robin Flow: Alternate turns cleanly. Avoid dogpiling an isolated player unless they overextended.",
        "Armor Buffer: Once an enemy's armor is cracked, encourage players to apply CC (Knockdown, Freeze, Stun) before finishing off.",
    ]
    if boss_scaling_notes:
        tactical_recs.insert(0, f"Boss Scaling Engine: {boss_scaling_notes}")

    if encounter_type == EncounterType.BOSS:
        effective_minions = minion_count if minion_count is not None else max(0, len(enemies) - 1)
        if effective_minions == 0:
            tactical_recs.append("Solo Boss Combat: With no minion support, the boss relies on massive armor pools and high AP. Players must prioritize breaking one armor type quickly to land hard CC.")
        elif effective_minions == 1:
            tactical_recs.append("Duo Boss Battle: The lieutenant guards the boss's flank. Eliminate or CC the lieutenant first to isolate the commander.")
        elif effective_minions >= 4:
            tactical_recs.append(f"Minion Horde ({effective_minions} minions): High enemy Action Economy. Use wide AoE (Earthquake, Fireball, Ricochet) and surface obstacles (Oil/Webs) to eliminate minions before they flank.")
        else:
            tactical_recs.append("Boss Mechanics: Do NOT let players surround the Boss alone; use Minions to bodyblock and soak hits.")

        boss_npc = next((e for e in enemies if e.archetype == Archetype.BOSS), None)
        if boss_npc:
            pers_val = boss_npc.stats.combat_abilities.get("Perseverance", 0)
            if pers_val > 0:
                tactical_recs.append(f"Anti-CC Perseverance: Boss has Perseverance {pers_val}. When hard CC (Knockdown, Freeze, Stun, Petrify) expires, it instantly recovers {pers_val * 5}% Armor. Players must burst or re-apply CC promptly.")
            lead_val = boss_npc.stats.combat_abilities.get("Leadership", 0)
            if lead_val > 0 and len(enemies) > 1:
                tactical_recs.append(f"Commander Aura: Boss radiates Leadership {lead_val} (+{lead_val * 2}% Dodge and +{lead_val * 3}% All Resistances to minions within 8m). Advise players to isolate or displace minions.")
            if boss_npc.stats.resistances:
                weaknesses = [f"{elem} ({val}%)" for elem, val in boss_npc.stats.resistances.items() if val < 0]
                if weaknesses:
                    tactical_recs.append(f"Elemental Vulnerability: Boss is vulnerable to {', '.join(weaknesses)}. Highlight these weaknesses to reward player elemental synergies.")
    elif encounter_type == EncounterType.SWARM:
        tactical_recs.append("Swarm Mechanics: Spread minions across different angles so a single AoE spell doesn't wipe them on Turn 1.")

    # Tuning Dials for GM on the fly
    tuning_dials = {
        "To make it EASIER on the fly": "Reduce enemy Magic/Physical Armor by 20% or have an enemy spend 2 AP buffing rather than attacking.",
        "To make it HARDER on the fly": "Spawn 1-2 delayed reinforcements from the shadows, or give the leader an extra source spell.",
        "If a Player goes down early": "Have the enemy prioritize self-buffing (Fortify/Armor of Frost) or taunting instead of executing the downed hero."
    }

    if encounter_type == EncounterType.BOSS:
        effective_minions = minion_count if minion_count is not None else max(0, len(enemies) - 1)
        if effective_minions == 0:
            tuning_dials["Solo Boss Tuning"] = "If players lock down the boss too easily on Turn 1, grant an emergency Cleansing/Armor buff reaction."
        elif effective_minions >= 4:
            tuning_dials["High Minion Tuning"] = "If players are struggling against action economy, have 1-2 minions delay actions or spend AP buffing instead of attacking."

    return EncounterBalanceAnalysis(
        party_total_ap=party_ap,
        enemy_total_ap=enemy_ap,
        ap_ratio_explanation=ap_explanation,
        party_expected_ehp=party_ehp,
        enemy_total_ehp=enemy_ehp,
        ehp_ratio_explanation=ehp_explanation,
        damage_compatibility_rating=compat_rating,
        damage_compatibility_notes=compat_notes,
        overall_difficulty_assessment=overall_assessment,
        tactical_recommendations=tactical_recs,
        tuning_dials=tuning_dials
    )


def align_combat_abilities_with_skills(
    stats: EnemyStats,
    skills: List[Skill],
    archetype: Archetype,
    level: Optional[int] = None,
    race: Optional[Race] = None,
    difficulty: Optional[Difficulty] = None,
    class_archetype: Optional[Archetype] = None
) -> None:
    """Ensure combat abilities support the schools of the character's memorized skills."""
    active_schools = [s.school for s in skills if s.school not in ("Special", "Racial")]
    if not active_schools:
        return
    unique_schools = list(dict.fromkeys(active_schools))
    magic_schools = {
        "Warfare", "Huntsman", "Scoundrel", "Pyrokinetic", "Hydrosophist",
        "Aerotheurge", "Geomancer", "Necromancer", "Polymorph", "Summoning"
    }
    total_pts = sum(v for k, v in stats.combat_abilities.items() if k in magic_schools)
    if total_pts <= 0:
        return
    current_assigned = {k: v for k, v in stats.combat_abilities.items() if k in magic_schools and v > 0}
    needs_realign = any(stats.combat_abilities.get(s, 0) == 0 for s in unique_schools) or any(s not in unique_schools for s in current_assigned)
    if needs_realign:
        new_abilities = {k: v for k, v in stats.combat_abilities.items() if k not in magic_schools}
        base_per_school = max(1, total_pts // len(unique_schools))
        remainder = total_pts - (base_per_school * len(unique_schools))
        for i, school in enumerate(unique_schools):
            pts = base_per_school + (remainder if i == 0 else 0)
            new_abilities[school] = min(10, pts)
        stats.combat_abilities = new_abilities

    # If level is provided, sync attributes and dependent stats with any Polymorph changes
    if level is not None:
        sync_stats_with_combat_abilities(
            stats,
            level=level,
            archetype=archetype,
            race=race or Race.HUMAN,
            difficulty=difficulty or Difficulty.BALANCED,
            class_archetype=class_archetype
        )


@dataclass
class BossScalingProfile:
    minion_count: int
    boss_armor_mult: float
    boss_vitality_mult: float
    boss_attribute_bonus: int
    boss_con_bonus: int
    boss_retribution_bonus: int
    boss_initiative_bonus: int
    boss_max_slots: int
    minion_armor_mult: float
    minion_vitality_mult: float
    minion_level_offset: int
    minion_max_slots: int
    scaling_description: str
    boss_perseverance: int = 4
    boss_leadership: int = 0
    boss_ap_recovery: int = 6
    minion_ap_recovery: int = 4


@dataclass
class DefenseProfile:
    name: str
    display_name: str
    phys_armor_mult: float
    magic_armor_mult: float
    resistances: Dict[str, int]
    vulnerability_notes: str


DEFENSE_PROFILES: Dict[str, DefenseProfile] = {
    "balanced": DefenseProfile(
        name="balanced",
        display_name="Balanced Bastion (Symmetrical 50/50 Armor)",
        phys_armor_mult=1.0,
        magic_armor_mult=1.0,
        resistances={},
        vulnerability_notes="Even defense distribution with standard neutral resistances."
    ),
    "ironclad": DefenseProfile(
        name="ironclad",
        display_name="Ironclad Juggernaut (Heavy Physical / Low Magic)",
        phys_armor_mult=1.30,
        magic_armor_mult=0.70,
        resistances={"Physical": 15, "Earth": 20, "Air": -25},
        vulnerability_notes="High Physical Armor; vulnerable to Air and Magic CC once Magic Armor drops."
    ),
    "arcane": DefenseProfile(
        name="arcane",
        display_name="Arcane Aegis (High Magic / Low Physical)",
        phys_armor_mult=0.70,
        magic_armor_mult=1.30,
        resistances={"Fire": 20, "Water": 20, "Air": 20, "Earth": 20, "Physical": -20},
        vulnerability_notes="High Magic Armor; vulnerable to Warfare knockdowns and backstabs once Physical Armor drops."
    ),
    "pyro": DefenseProfile(
        name="pyro",
        display_name="Pyroclastic Vanguard (Fire Immune / Water Weakness)",
        phys_armor_mult=1.05,
        magic_armor_mult=0.95,
        resistances={"Fire": 60, "Earth": 20, "Water": -40},
        vulnerability_notes="High Fire resistance; critically weak to Hydro/Cryo frost spells (-40% resistance)."
    ),
    "cryo": DefenseProfile(
        name="cryo",
        display_name="Glacial Frost-Bound (Water/Air Resistant / Fire Weakness)",
        phys_armor_mult=0.95,
        magic_armor_mult=1.05,
        resistances={"Water": 60, "Air": 25, "Fire": -40},
        vulnerability_notes="High Water and Air resistance; critically weak to Pyrokinetic fire spells (-40% resistance)."
    ),
    "venom": DefenseProfile(
        name="venom",
        display_name="Venomous / Undead (Poison Absorption / Fire Weakness)",
        phys_armor_mult=1.0,
        magic_armor_mult=1.0,
        resistances={"Poison": 100, "Earth": 25, "Fire": -25},
        vulnerability_notes="Healed by Poison, resistant to Earth; vulnerable to Fire/Holy radiant damage (-25% resistance)."
    ),
    "storm": DefenseProfile(
        name="storm",
        display_name="Storm Conduit (Air Immune / Earth Weakness)",
        phys_armor_mult=0.85,
        magic_armor_mult=1.15,
        resistances={"Air": 60, "Water": 20, "Earth": -35},
        vulnerability_notes="Immune to electrical stun surfaces; vulnerable to Geomancer boulders and oil (-35% resistance)."
    ),
    "troll": DefenseProfile(
        name="troll",
        display_name="Troll Hide (Colossal Physical / Fire Weakness)",
        phys_armor_mult=1.20,
        magic_armor_mult=0.80,
        resistances={"Earth": 40, "Physical": 10, "Fire": -30},
        vulnerability_notes="Massive physical resilience; vulnerable to Fire (-30% resistance, suppresses Troll Blood regeneration)."
    ),
}


def auto_detect_defense_profile(template: BestiaryTemplate, archetype: Archetype) -> str:
    """Automatically infers an authentic thematic defensive profile based on template name, race, and faction."""
    t_name = template.name.lower()
    t_id = template.gm_template_id.lower()
    t_tactics = template.ai_tactics.lower()

    if "troll" in t_name or "troll" in t_id:
        return "troll"

    if template.race in (Race.UNDEAD, Race.UNDEAD_HUMAN, Race.UNDEAD_ELF, Race.UNDEAD_DWARF, Race.UNDEAD_LIZARD) or "undead" in t_name or "skeleton" in t_id:
        return "venom"

    if any(k in t_name or k in t_tactics for k in ["fire", "pyro", "flame", "blaze", "magma"]):
        return "pyro"

    if any(k in t_name or k in t_tactics for k in ["frost", "ice", "cryo", "water", "glacial"]):
        return "cryo"

    if any(k in t_name or k in t_tactics for k in ["storm", "electric", "lightning", "aero", "air"]):
        return "storm"

    effective_arch = template.archetype if archetype == Archetype.BOSS else archetype

    if effective_arch in (Archetype.TANK, Archetype.FIGHTER) or any(k in t_id for k in ["strong", "tank"]):
        return "ironclad"

    if effective_arch in (Archetype.MAGE, Archetype.BATTLEMAGE, Archetype.CLERIC, Archetype.SUMMONER) or any(k in t_tactics for k in ["spell", "magic", "caster"]):
        return "arcane"

    return "balanced"


def calculate_boss_scaling(minion_count: int, is_lone_wolf: bool) -> BossScalingProfile:
    """
    Computes precise mathematical durability, attribute, and tactical scaling
    for a boss encounter based on the GM's chosen minion count (0 to 5).
    Strictly adheres to DOS2 GM Mode limits (fixed 4 Start AP, fixed 6 Max AP, and 0-6 Turn AP).
    Balancing is achieved through:
    - AP per turn slider (0-6 recovery AP configured on the boss Character Sheet)
    - Durability buffers (Armor and Vitality multipliers)
    - Primary attribute scaling (STR/FIN/INT +5% base dmg per pt)
    - Constitution (+7% vitality per pt)
    - Retribution combat ability (damage reflection against focused fire)
    - Initiative bonuses (Turn 1 priority)
    - Authentic survival talents (Comeback Kid, What a Rush, Living Armor)
    """
    if minion_count == 0:
        if is_lone_wolf:
            return BossScalingProfile(
                minion_count=0,
                boss_armor_mult=1.45,
                boss_vitality_mult=1.35,
                boss_attribute_bonus=3,
                boss_con_bonus=3,
                boss_retribution_bonus=2,
                boss_initiative_bonus=5,
                boss_max_slots=7,
                minion_armor_mult=1.0,
                minion_vitality_mult=1.0,
                minion_level_offset=0,
                minion_max_slots=3,
                scaling_description="Solo Boss Duel (Lone Wolf): Fixed 4 Start AP / 6 Max AP, tuned with +6 AP/turn slider. Durability (+45% armor, +35% HP), +STR/INT damage, and Perseverance 5 counter 2-player Lone Wolf burst.",
                boss_perseverance=5,
                boss_leadership=0,
                boss_ap_recovery=6,
                minion_ap_recovery=4,
            )
        else:
            return BossScalingProfile(
                minion_count=0,
                boss_armor_mult=1.65,
                boss_vitality_mult=1.50,
                boss_attribute_bonus=4,
                boss_con_bonus=4,
                boss_retribution_bonus=3,
                boss_initiative_bonus=6,
                boss_max_slots=7,
                minion_armor_mult=1.0,
                minion_vitality_mult=1.0,
                minion_level_offset=0,
                minion_max_slots=3,
                scaling_description="Solo Overlord Duel (0 Minions): Fixed 4 Start AP / 6 Max AP, tuned with +6 AP/turn slider. Durability (+65% armor, +50% HP), Retribution 3, and Perseverance 5 (restores 25% armor on CC recovery) balance against 4v1 party turns.",
                boss_perseverance=5,
                boss_leadership=0,
                boss_ap_recovery=6,
                minion_ap_recovery=4,
            )
    elif minion_count == 1:
        if is_lone_wolf:
            return BossScalingProfile(
                minion_count=1,
                boss_armor_mult=1.15,
                boss_vitality_mult=1.10,
                boss_attribute_bonus=1,
                boss_con_bonus=1,
                boss_retribution_bonus=0,
                boss_initiative_bonus=2,
                boss_max_slots=6,
                minion_armor_mult=1.05,
                minion_vitality_mult=1.05,
                minion_level_offset=0,
                minion_max_slots=4,
                scaling_description="Duo Boss Encounter (Lone Wolf): Fixed 4 Start AP / 6 Max AP with +5 AP/turn on boss. Boss and lieutenant tuned for a tight 2v2 tactical duel with Leadership 2 aura.",
                boss_perseverance=4,
                boss_leadership=2,
                boss_ap_recovery=5,
                minion_ap_recovery=4,
            )
        else:
            return BossScalingProfile(
                minion_count=1,
                boss_armor_mult=1.30,
                boss_vitality_mult=1.20,
                boss_attribute_bonus=2,
                boss_con_bonus=2,
                boss_retribution_bonus=1,
                boss_initiative_bonus=3,
                boss_max_slots=6,
                minion_armor_mult=1.15,
                minion_vitality_mult=1.10,
                minion_level_offset=0,
                minion_max_slots=4,
                scaling_description="Boss & Elite Lieutenant Duo (1 Minion): Fixed 4 Start AP / 6 Max AP with +6 AP/turn on boss. Elevated boss armor (+30%), Perseverance 4, and Leadership 2 aura protect the lieutenant.",
                boss_perseverance=4,
                boss_leadership=2,
                boss_ap_recovery=6,
                minion_ap_recovery=4,
            )
    elif minion_count == 2:
        if is_lone_wolf:
            return BossScalingProfile(
                minion_count=2,
                boss_armor_mult=1.00,
                boss_vitality_mult=1.00,
                boss_attribute_bonus=0,
                boss_con_bonus=0,
                boss_retribution_bonus=0,
                boss_initiative_bonus=0,
                boss_max_slots=6,
                minion_armor_mult=1.00,
                minion_vitality_mult=1.00,
                minion_level_offset=-1,
                minion_max_slots=3,
                scaling_description="Standard Lone Wolf Boss Encounter: Calibrated baseline 1 Boss + 2 Minions matching Lone Wolf power (fixed 4 Start AP / 6 Max AP, +4 AP/turn).",
                boss_perseverance=4,
                boss_leadership=3,
                boss_ap_recovery=4,
                minion_ap_recovery=4,
            )
        else:
            return BossScalingProfile(
                minion_count=2,
                boss_armor_mult=1.15,
                boss_vitality_mult=1.10,
                boss_attribute_bonus=1,
                boss_con_bonus=1,
                boss_retribution_bonus=0,
                boss_initiative_bonus=2,
                boss_max_slots=6,
                minion_armor_mult=1.05,
                minion_vitality_mult=1.00,
                minion_level_offset=0,
                minion_max_slots=3,
                scaling_description="Tightly Guarded Boss Trio: 2 minions. Modest durability buffer (+15% boss armor), +5 AP/turn, Perseverance 4, and Leadership 3 aura match 4 player turns.",
                boss_perseverance=4,
                boss_leadership=3,
                boss_ap_recovery=5,
                minion_ap_recovery=4,
            )
    elif minion_count == 3:
        if is_lone_wolf:
            return BossScalingProfile(
                minion_count=3,
                boss_armor_mult=0.90,
                boss_vitality_mult=0.95,
                boss_attribute_bonus=0,
                boss_con_bonus=0,
                boss_retribution_bonus=0,
                boss_initiative_bonus=0,
                boss_max_slots=6,
                minion_armor_mult=0.88,
                minion_vitality_mult=0.90,
                minion_level_offset=-1,
                minion_max_slots=3,
                scaling_description="Pressure Squad (Lone Wolf): 3 minions; durability trimmed (-10% boss armor) to prevent action economy overwhelm against 2 heroes (fixed 4 Start AP / 6 Max AP, +4 AP/turn).",
                boss_perseverance=4,
                boss_leadership=3,
                boss_ap_recovery=4,
                minion_ap_recovery=4,
            )
        else:
            return BossScalingProfile(
                minion_count=3,
                boss_armor_mult=1.00,
                boss_vitality_mult=1.00,
                boss_attribute_bonus=0,
                boss_con_bonus=0,
                boss_retribution_bonus=0,
                boss_initiative_bonus=0,
                boss_max_slots=6,
                minion_armor_mult=1.00,
                minion_vitality_mult=1.00,
                minion_level_offset=-1,
                minion_max_slots=3,
                scaling_description="Classic Boss Squad: Standard 1 Boss + 3 Minions providing authentic round-robin tactical tempo at standard GM caps (fixed 4 Start AP / 6 Max AP, +4 AP/turn, Perseverance 4, Leadership 3).",
                boss_perseverance=4,
                boss_leadership=3,
                boss_ap_recovery=4,
                minion_ap_recovery=4,
            )
    elif minion_count == 4:
        if is_lone_wolf:
            return BossScalingProfile(
                minion_count=4,
                boss_armor_mult=0.80,
                boss_vitality_mult=0.85,
                boss_attribute_bonus=0,
                boss_con_bonus=0,
                boss_retribution_bonus=0,
                boss_initiative_bonus=0,
                boss_max_slots=6,
                minion_armor_mult=0.75,
                minion_vitality_mult=0.80,
                minion_level_offset=-1,
                minion_max_slots=2,
                scaling_description="Heavy Minion Swarm (Lone Wolf): 4 minions; enemy durability heavily reduced to prevent overwhelming Lone Wolf players (fixed 4 Start AP / 6 Max AP, +4 AP/turn).",
                boss_perseverance=3,
                boss_leadership=4,
                boss_ap_recovery=4,
                minion_ap_recovery=4,
            )
        else:
            return BossScalingProfile(
                minion_count=4,
                boss_armor_mult=0.88,
                boss_vitality_mult=0.92,
                boss_attribute_bonus=0,
                boss_con_bonus=0,
                boss_retribution_bonus=0,
                boss_initiative_bonus=0,
                boss_max_slots=6,
                minion_armor_mult=0.80,
                minion_vitality_mult=0.85,
                minion_level_offset=-1,
                minion_max_slots=3,
                scaling_description="Heavy Minion Guard: 4 minions create high action economy (20 enemy AP). Boss (-12% armor) and minions (-20% armor) softened; boss radiates Leadership 4 (fixed 4 Start AP / 6 Max AP, +4 AP/turn).",
                boss_perseverance=3,
                boss_leadership=4,
                boss_ap_recovery=4,
                minion_ap_recovery=4,
            )
    else:  # minion_count == 5
        if is_lone_wolf:
            return BossScalingProfile(
                minion_count=5,
                boss_armor_mult=0.72,
                boss_vitality_mult=0.80,
                boss_attribute_bonus=0,
                boss_con_bonus=0,
                boss_retribution_bonus=0,
                boss_initiative_bonus=0,
                boss_max_slots=6,
                minion_armor_mult=0.65,
                minion_vitality_mult=0.70,
                minion_level_offset=-1,
                minion_max_slots=2,
                scaling_description="Maximum Minion Horde (Lone Wolf): 5 minions. Enemy stats trimmed down (-28% boss armor, -35% minion armor) to maintain tactical viability (fixed 4 Start AP / 6 Max AP, +4 AP/turn).",
                boss_perseverance=3,
                boss_leadership=4,
                boss_ap_recovery=4,
                minion_ap_recovery=4,
            )
        else:
            return BossScalingProfile(
                minion_count=5,
                boss_armor_mult=0.78,
                boss_vitality_mult=0.85,
                boss_attribute_bonus=0,
                boss_con_bonus=0,
                boss_retribution_bonus=0,
                boss_initiative_bonus=0,
                boss_max_slots=6,
                minion_armor_mult=0.70,
                minion_vitality_mult=0.75,
                minion_level_offset=-1,
                minion_max_slots=2,
                scaling_description="Full Minion Swarm Boss Battle: 5 minions (6 enemies, 24 enemy AP). Boss (-22% armor, Leadership 4) and minions (-30% armor, -25% HP) scaled as swarmer cannon-fodder, rewarding wide AoE clearance (Fireball, Earthquake, Ricochet). Fixed 4 Start AP / 6 Max AP, +4 AP/turn.",
                boss_perseverance=3,
                boss_leadership=4,
                boss_ap_recovery=4,
                minion_ap_recovery=4,
            )


def _create_npc(
    template: BestiaryTemplate,
    level: int,
    party_config: PartyConfig,
    title: str,
    archetype: Optional[Archetype] = None,
    max_slots: Optional[int] = None,
    name_prefix: str = "",
    armor_multiplier: float = 1.0,
    vitality_multiplier: float = 1.0,
    attribute_bonus: int = 0,
    con_bonus: int = 0,
    retribution_bonus: int = 0,
    initiative_bonus: int = 0,
    perseverance_bonus: int = 0,
    leadership_bonus: int = 0,
    defense_profile_name: Optional[str] = None,
    ap_recovery: Optional[int] = None,
    explicit_skills: Optional[List[str]] = None,
) -> NPC:
    actual_archetype = archetype or template.archetype
    class_style = template.archetype if template.archetype not in (Archetype.BOSS, Archetype.MINION) else None
    if not class_style:
        eq_lower = template.equipment.lower()
        tac_lower = template.ai_tactics.lower()
        name_lower = template.name.lower()
        if any(k in eq_lower or k in tac_lower or k in name_lower for k in ["dagger", "rogue", "assassin", "shadowblade", "cutthroat"]):
            class_style = Archetype.ROGUE
        elif any(k in eq_lower or k in tac_lower or k in name_lower for k in ["bow", "crossbow", "ranger", "marksman", "hunter"]):
            class_style = Archetype.RANGER
        elif any(k in eq_lower or k in tac_lower or k in name_lower for k in ["wand", "staff", "mage", "wizard", "pyro", "cryo", "elementalist"]):
            class_style = Archetype.MAGE

    stats = calculate_enemy_stats(
        level, 
        actual_archetype, 
        party_config.difficulty, 
        party_config.damage_profile, 
        race=template.race,
        class_archetype=class_style
    )

    calc_max_skills = 3 + max(0, stats.memory - 10)
    slots = min(max_slots, calc_max_skills) if max_slots is not None else calc_max_skills
    
    if explicit_skills is not None:
        from .skills_db import SKILLS_DATABASE, get_racial_skills_for_race, Skill
        skill_map = {s.name.lower(): s for s in SKILLS_DATABASE}
        skills = []
        if template.race:
            for r_s in get_racial_skills_for_race(template.race):
                if r_s not in skills:
                    skills.append(r_s)
        for s_name in explicit_skills:
            clean = str(s_name).strip().lower()
            if not clean:
                continue
            if clean in skill_map:
                sk = skill_map[clean]
                if sk not in skills:
                    skills.append(sk)
            else:
                skills.append(Skill(
                    name=str(s_name).strip(),
                    school="Special",
                    tier="Novice",
                    ap_cost=2,
                    damage_type="Physical",
                    description=f"Custom tactical ability: {str(s_name).strip()}",
                    status_applied=None
                ))
        used_mem = sum(s.memory_cost for s in skills)
        needed_mem = 10 + max(0, used_mem - 3)
        if stats.memory < needed_mem:
            stats.memory = needed_mem
    else:
        skills = get_skills_for_archetype(
            actual_archetype,
            level,
            max_slots=slots,
            race=template.race,
            ai_tactics=template.ai_tactics,
            equipment=template.equipment,
            signature_skills=getattr(template, "signature_skills", None),
            class_archetype=class_style
        )
    
    align_combat_abilities_with_skills(
        stats,
        skills,
        actual_archetype,
        level=level,
        race=template.race,
        difficulty=party_config.difficulty,
        class_archetype=class_style
    )

    if explicit_skills is None:
        calc_max = 3 + max(0, stats.memory - 10)
        final_slots = min(max_slots, calc_max) if max_slots is not None else calc_max
        innates = [s for s in skills if s.is_innate]
        memorized = [s for s in skills if not s.is_innate]
        if len(memorized) > final_slots:
            skills = innates + memorized[:final_slots]

    if ap_recovery is not None:
        stats.ap_recovery = ap_recovery

    # Enforce GM mode hard limits on AP:
    # Starting AP is fixed at 4; Maximum AP is fixed at 6.
    # AP per turn (recovery) can be adjusted from 0 to 6.
    stats.ap_start = 4
    stats.ap_max = 6
    stats.ap_recovery = min(6, max(0, stats.ap_recovery))

    if armor_multiplier != 1.0:
        stats.physical_armor = int(stats.physical_armor * armor_multiplier)
        stats.magic_armor = int(stats.magic_armor * armor_multiplier)
    if vitality_multiplier != 1.0:
        stats.vitality = max(15, int(stats.vitality * vitality_multiplier))
    if attribute_bonus > 0:
        stats.strength += attribute_bonus
        stats.finesse += attribute_bonus
        stats.intelligence += attribute_bonus
    if con_bonus > 0:
        stats.constitution += con_bonus
        stats.vitality = int(stats.vitality * (1.0 + con_bonus * 0.07))
    if retribution_bonus > 0:
        stats.combat_abilities["Retribution"] = stats.combat_abilities.get("Retribution", 0) + retribution_bonus
    if initiative_bonus != 0:
        stats.initiative += initiative_bonus

    # Combat ability adjustments (Perseverance and Leadership)
    if actual_archetype == Archetype.BOSS:
        stats.combat_abilities["Perseverance"] = max(stats.combat_abilities.get("Perseverance", 0), perseverance_bonus if perseverance_bonus > 0 else 3)
    elif "Champion" in title or "Elite" in name_prefix:
        stats.combat_abilities["Perseverance"] = max(stats.combat_abilities.get("Perseverance", 0), 2)

    if leadership_bonus > 0:
        stats.combat_abilities["Leadership"] = max(stats.combat_abilities.get("Leadership", 0), leadership_bonus)

    # Calculate talents tailored to final combat abilities, class style, equipment, and AI tactics
    stats.talents = calculate_talents(
        actual_archetype,
        level,
        race=template.race,
        combat_abilities=stats.combat_abilities,
        class_archetype=class_style,
        equipment=template.equipment,
        ai_tactics=template.ai_tactics,
        preferred_talents=getattr(template, "signature_talents", None)
    )

    # For Bosses, grant Walk It Off (anti-chain-CC) and for Solo Bosses grant Comeback Kid & What a Rush
    if actual_archetype == Archetype.BOSS:
        if "Walk It Off" not in stats.talents:
            stats.talents.append("Walk It Off")
        if "Solo" in title or attribute_bonus >= 3:
            for t in ["Comeback Kid", "What a Rush"]:
                if t not in stats.talents:
                    stats.talents.append(t)

    # Strictly filter and validate against combat ability prerequisites, mutual exclusions, and equipment
    stats.talents = validate_and_filter_talents(
        stats.talents,
        combat_abilities=stats.combat_abilities,
        level=level,
        equipment=template.equipment
    )

    # Asymmetric Armor & Elemental Weakness Profiles (Point 3)
    defense_theme = ""
    gm_notes = template.gm_notes
    if actual_archetype == Archetype.BOSS or "Champion" in title or "Elite" in name_prefix or defense_profile_name is not None:
        prof_key = defense_profile_name if (defense_profile_name and defense_profile_name.lower() != "auto") else auto_detect_defense_profile(template, actual_archetype)
        def_prof = DEFENSE_PROFILES.get(prof_key.lower(), DEFENSE_PROFILES["balanced"])
        if def_prof.phys_armor_mult != 1.0 or def_prof.magic_armor_mult != 1.0:
            total_armor = stats.physical_armor + stats.magic_armor
            raw_phys = stats.physical_armor * def_prof.phys_armor_mult
            raw_mag = stats.magic_armor * def_prof.magic_armor_mult
            sum_raw = raw_phys + raw_mag
            if sum_raw > 0 and total_armor > 0:
                stats.physical_armor = max(0, int(round(total_armor * (raw_phys / sum_raw))))
                stats.magic_armor = max(0, total_armor - stats.physical_armor)
        stats.resistances = dict(def_prof.resistances)
        defense_theme = def_prof.display_name
        if def_prof.vulnerability_notes and def_prof.name != "balanced":
            gm_notes = f"{template.gm_notes} [Defensive Trait: {def_prof.vulnerability_notes}]"
    
    npc_name = f"{name_prefix}{template.name}"
    return NPC(
        name=npc_name,
        title=title,
        faction=template.faction,
        race=template.race,
        archetype=actual_archetype,
        level=level,
        stats=stats,
        skills=skills,
        equipment=template.equipment,
        ai_tactics=template.ai_tactics,
        gm_notes=gm_notes,
        gm_template_id=template.gm_template_id,
        defense_theme=defense_theme
    )


def generate_encounter(
    party_config: PartyConfig,
    encounter_type: Optional[EncounterType] = None,
    faction: Optional[Faction] = None,
    race: Optional[Race] = None,
    boss_template: Optional[Union[BestiaryTemplate, str]] = None,
    minion_count: Optional[int] = None,
    defense_profile: Optional[str] = None,
    seed: Optional[int] = None
) -> Encounter:
    """
    Generates a complete, balanced DOS2 GM mode encounter with exact stats,
    skills, gear, terrain, and balance analytics.
    Allows specifying boss NPC (by template, name, or custom string) and minion count (0 to 5)
    with automatic tactical and durability balancing strictly within GM mode AP limitations (fixed 4 Start AP / 6 Max AP, 0-6 AP/turn).
    """
    if seed is not None:
        random.seed(seed)

    # If a boss template is explicitly provided, encounter type defaults to BOSS
    if boss_template is not None and encounter_type is None:
        encounter_type = EncounterType.BOSS

    if encounter_type is None:
        encounter_type = random.choice([
            EncounterType.STANDARD,
            EncounterType.BOSS,
            EncounterType.SWARM,
            EncounterType.ELITE
        ])

    # 1. Determine templates based on faction and race filter
    if race is not None:
        templates = get_templates_by_faction(faction, race=race)
        if not templates:
            if faction is not None and faction != Faction.ANY:
                # Preserve the explicitly selected faction and ignore the incompatible race filter
                race = None
                templates = get_templates_by_faction(faction)
            else:
                templates = get_templates_by_faction(Faction.ANY, race=race)
        if not templates:
            templates = BESTIARY
        else:
            if faction is None or faction == Faction.ANY:
                faction = templates[0].faction
    else:
        if faction is None:
            faction = random.choice([f for f in Faction if f != Faction.ANY])
        templates = get_templates_by_faction(faction)
        if not templates:
            templates = BESTIARY

    if faction is None:
        faction = templates[0].faction if templates else Faction.ANY

    party_lvl = party_config.level
    enemies: List[NPC] = []
    actual_minions: Optional[int] = None
    boss_scaling_notes: Optional[str] = None
    boss_tpl_resolved: Optional[BestiaryTemplate] = None
    
    # -------------------------------------------------------------
    # 1. ENCOUNTER COMPOSITION LOGIC
    # -------------------------------------------------------------
    if encounter_type == EncounterType.STANDARD:
        enemy_count = party_config.party_size
        if party_config.is_lone_wolf:
            enemy_count = max(3, party_config.party_size + 1)
            
        desired_archetypes = [
            Archetype.FIGHTER,
            Archetype.RANGER,
            Archetype.MAGE,
            Archetype.ROGUE,
            Archetype.TANK
        ]
        
        for i in range(enemy_count):
            target_arch = desired_archetypes[i % len(desired_archetypes)]
            matching = [t for t in templates if t.archetype == target_arch and not t.can_be_boss]
            if not matching:
                matching = [t for t in templates if not t.can_be_boss]
            
            used_races = [e.race for e in enemies]
            unrepresented = [t for t in matching if t.race not in used_races]
            candidates = unrepresented if unrepresented else matching
            template = random.choice(candidates) if candidates else random.choice(templates)
            
            enemies.append(_create_npc(template, party_lvl, party_config, title="Combatant"))

    elif encounter_type == EncounterType.BOSS:
        # Resolve Boss Template (specifically selected or randomized)
        if boss_template is not None:
            if isinstance(boss_template, BestiaryTemplate):
                boss_tpl = boss_template
            else:
                found = find_template_by_name(str(boss_template))
                if found:
                    boss_tpl = found
                else:
                    boss_tpl = create_custom_boss_template(
                        name=str(boss_template),
                        faction=faction if faction != Faction.ANY else Faction.BEASTS,
                        race=race or Race.CREATURE
                    )
        else:
            boss_templates = [t for t in templates if t.can_be_boss or t.archetype == Archetype.BOSS]
            if not boss_templates:
                boss_templates = templates
            boss_tpl = random.choice(boss_templates)

        boss_tpl_resolved = boss_tpl

        # If faction was not specified or ANY, adopt boss faction for consistency
        if (faction is None or faction == Faction.ANY) and boss_tpl.faction != Faction.ANY:
            faction = boss_tpl.faction

        # Resolve Minion Count (0 to 5)
        if minion_count is not None:
            if not (0 <= minion_count <= 5):
                raise ValueError(f"Minion count for Boss encounter must be between 0 and 5, got {minion_count}")
            actual_minions = minion_count
        else:
            actual_minions = 2 if party_config.is_lone_wolf else 3

        scaling = calculate_boss_scaling(actual_minions, party_config.is_lone_wolf)
        boss_scaling_notes = scaling.scaling_description

        boss_level = party_lvl + (1 if party_config.difficulty != Difficulty.STORY else 0)
        boss_title = "Solo Boss / Overlord" if actual_minions == 0 else "Boss / Commander"

        enemies.append(_create_npc(
            boss_tpl, 
            boss_level, 
            party_config, 
            title=boss_title, 
            archetype=Archetype.BOSS, 
            max_slots=scaling.boss_max_slots,
            armor_multiplier=scaling.boss_armor_mult,
            vitality_multiplier=scaling.boss_vitality_mult,
            attribute_bonus=scaling.boss_attribute_bonus,
            con_bonus=scaling.boss_con_bonus,
            retribution_bonus=scaling.boss_retribution_bonus,
            initiative_bonus=scaling.boss_initiative_bonus,
            perseverance_bonus=scaling.boss_perseverance,
            leadership_bonus=scaling.boss_leadership,
            defense_profile_name=defense_profile,
            ap_recovery=scaling.boss_ap_recovery,
        ))
        
        # Minions (0 to 5)
        regular_templates = [t for t in templates if not t.can_be_boss and t != boss_tpl]
        if not regular_templates:
            regular_templates = [t for t in templates if t != boss_tpl] or templates

        for i in range(actual_minions):
            used_races = [e.race for e in enemies]
            unrepresented = [t for t in regular_templates if t.race not in used_races]
            candidates = unrepresented if unrepresented else regular_templates
            tpl = random.choice(candidates)

            minion_level = max(1, party_lvl + scaling.minion_level_offset)
            minion_title = "Elite Lieutenant" if actual_minions == 1 else "Minion"
            enemies.append(_create_npc(
                tpl, 
                minion_level, 
                party_config, 
                title=minion_title, 
                max_slots=scaling.minion_max_slots,
                armor_multiplier=scaling.minion_armor_mult,
                vitality_multiplier=scaling.minion_vitality_mult,
                ap_recovery=scaling.minion_ap_recovery,
            ))

    elif encounter_type == EncounterType.SWARM:
        minion_count = 5 if party_config.is_lone_wolf else 7
        swarm_templates = [t for t in templates if t.can_be_minion or t.archetype == Archetype.MINION]
        if not swarm_templates:
            swarm_templates = [t for t in templates if not t.can_be_boss] or templates
            
        for i in range(minion_count):
            used_races = [e.race for e in enemies]
            unrepresented = [t for t in swarm_templates if t.race not in used_races]
            candidates = unrepresented if unrepresented else swarm_templates
            tpl = random.choice(candidates)

            swarmer_level = max(1, party_lvl - 1)
            enemies.append(_create_npc(
                tpl, 
                swarmer_level, 
                party_config, 
                title="Swarmer", 
                archetype=Archetype.MINION, 
                max_slots=2
            ))

    elif encounter_type == EncounterType.ELITE:
        champion_count = 2 if party_config.party_size <= 2 else 3
        elite_templates = [t for t in templates if not t.can_be_minion] or templates
        
        for i in range(champion_count):
            used_races = [e.race for e in enemies]
            unrepresented = [t for t in elite_templates if t.race not in used_races]
            candidates = unrepresented if unrepresented else elite_templates
            tpl = random.choice(candidates)

            champ_level = party_lvl
            enemies.append(_create_npc(
                tpl, 
                champ_level, 
                party_config, 
                title="Champion", 
                name_prefix="Elite ", 
                max_slots=5, 
                armor_multiplier=1.25,
                perseverance_bonus=2,
                defense_profile_name=defense_profile,
            ))

    # -------------------------------------------------------------
    # 2. ENVIRONMENTAL HAZARDS & TACTICAL TERRAIN
    # -------------------------------------------------------------
    terrain_options = [
        "Elevated wooden scaffolding providing High Ground (+20% damage) on the northern flank.",
        "Chokepoint bridge flanked by deep water and scattered explosive oil barrels.",
        "Enclosed stone courtyard with broken pillars granting full line-of-sight cover.",
        "Narrow cavern corridor with slick poison slime puddles and high stalagmites.",
        "Ruined shrine courtyard with cursed blood pools and ancient statues."
    ]
    tactical_terrain = random.choice(terrain_options)

    hazard_pool = [
        "2x Oil Barrels placed near central choke point (ready for Ignition/Fireball).",
        "Water surface puddle on southern side (susceptible to Electrocution or Freezing).",
        "Poison barrel on high ground (can be detonated or used to heal Undead).",
        "Steam cloud obscuring ranged line-of-sight in center corridor.",
        "Scattered crates blocking direct melee charge paths."
    ]
    environmental_hazards = random.sample(hazard_pool, k=2)

    # -------------------------------------------------------------
    # 3. BALANCE ANALYSIS
    # -------------------------------------------------------------
    analysis = analyze_encounter_balance(
        party_config=party_config,
        enemies=enemies,
        encounter_type=encounter_type,
        minion_count=actual_minions,
        boss_scaling_notes=boss_scaling_notes,
    )

    if encounter_type == EncounterType.BOSS:
        boss_label = boss_tpl_resolved.name if boss_tpl_resolved else "Boss"
        minion_sub = f"{actual_minions} Minion{'s' if actual_minions != 1 else ''}" if actual_minions > 0 else "Solo Boss"
        if race is not None:
            encounter_name = f"{faction.value} [{race.value} Only]: Boss Encounter - {boss_label} ({minion_sub}) (Lvl {party_lvl})"
        else:
            encounter_name = f"{faction.value}: Boss Encounter - {boss_label} ({minion_sub}) (Lvl {party_lvl})"
    elif race is not None:
        encounter_name = f"{faction.value} [{race.value} Only]: {encounter_type.value} (Lvl {party_lvl})"
    else:
        encounter_name = f"{faction.value}: {encounter_type.value} (Lvl {party_lvl})"

    return Encounter(
        name=encounter_name,
        encounter_type=encounter_type,
        faction=faction,
        party_config=party_config,
        enemies=enemies,
        environmental_hazards=environmental_hazards,
        tactical_terrain=tactical_terrain,
        analysis=analysis,
        selected_race=race,
        minion_count=actual_minions if encounter_type == EncounterType.BOSS else None,
        boss_name=boss_tpl_resolved.name if (encounter_type == EncounterType.BOSS and boss_tpl_resolved) else None,
    )


@dataclass
class CustomEnemySpec:
    """Specification for a single custom or bestiary-based enemy in the Interactive Encounter Builder."""
    template_name: Optional[str] = None
    name: Optional[str] = None
    faction: Optional[Union[Faction, str]] = None
    race: Optional[Union[Race, str]] = None
    combat_role: Optional[Union[Archetype, str]] = None
    unit_tier: str = "NORMAL"  # "NORMAL", "MINION", "ELITE", "BOSS"
    defense_profile: str = "auto"
    equipment: Optional[str] = None
    level_offset: int = 0
    skills: Optional[List[str]] = None


ROLE_DEFAULTS: Dict[Archetype, Dict[str, str]] = {
    Archetype.FIGHTER: {
        "equipment": "Two-Handed Greatsword + Heavy Plate",
        "ai_tactics": "Charges into melee with Battering Ram, cleaves grouped enemies with Whirlwind, and knocks down stripped targets with Battle Stomp.",
        "gm_notes": "Frontline martial bruiser focused on physical armor stripping and knockdowns.",
        "gm_template_id": "GM_Fighter_Custom",
    },
    Archetype.TANK: {
        "equipment": "One-Handed Warhammer + Bulwark Tower Shield",
        "ai_tactics": "Anchors the frontline, throws Bouncing Shield, uses Shields Up and Fortify to weather heavy focus fire, and bodyblocks choke points.",
        "gm_notes": "High-durability frontline tank with shield recovery and physical crowd control.",
        "gm_template_id": "GM_Tank_Custom",
    },
    Archetype.RANGER: {
        "equipment": "Masterwork Longbow + Elemental Arrow Quiver",
        "ai_tactics": "Uses Tactical Retreat to reach high ground (+20% damage), pins down melee threats with Pin Down, and fires Ricochet and Ballistic Shot.",
        "gm_notes": "Mobile ranged marksman; prioritize elevated perches.",
        "gm_template_id": "GM_Ranger_Custom",
    },
    Archetype.ROGUE: {
        "equipment": "Dual Serrated Daggers + Assassin Leathers",
        "ai_tactics": "Teleports behind vulnerable backline targets with Backlash or Cloak and Dagger, bursts with Adrenaline and Rupture Tendons.",
        "gm_notes": "High-initiative backstabber targeting low-physical-armor heroes.",
        "gm_template_id": "GM_Rogue_Custom",
    },
    Archetype.MAGE: {
        "equipment": "Elemental Quarterstaff + Archmage Robes",
        "ai_tactics": "Bombards clustered party members with Fireball and Fossil Strike, creates elemental surface combos, and strips Magic Armor from afar.",
        "gm_notes": "Backline elemental spellcaster; keep at range behind frontline blockers.",
        "gm_template_id": "GM_Mage_Custom",
    },
    Archetype.BATTLEMAGE: {
        "equipment": "Runed Battle-Staff + Reinforced Mail",
        "ai_tactics": "Engages at close-to-mid range, weaving elemental AoE blasts with Warfare crowd control and blinding/shocking aura pressure.",
        "gm_notes": "Hybrid melee-magic combatant capable of threatening both Physical and Magic Armor.",
        "gm_template_id": "GM_Battlemage_Custom",
    },
    Archetype.CLERIC: {
        "equipment": "Blessed Ceremonial Mace + Kite Shield",
        "ai_tactics": "Sustains allies with Restoration and Armor of Frost while punishing enemies with Necromancy and Hydro spells.",
        "gm_notes": "Support and sustain specialist; prioritize disrupting or focusing down early.",
        "gm_template_id": "GM_Cleric_Custom",
    },
    Archetype.SUMMONER: {
        "equipment": "Conjurer's Wand + Runed Buckler",
        "ai_tactics": "Summons an Elemental Incarnate on an active surface on Turn 1, empowers it with Power/Farsight Infusions, and spawns Elemental Totems.",
        "gm_notes": "Action-economy multiplier via incarnate and totems.",
        "gm_template_id": "GM_Summoner_Custom",
    },
}


def _parse_enemy_spec(raw: Union[CustomEnemySpec, Dict[str, Any]]) -> CustomEnemySpec:
    if isinstance(raw, CustomEnemySpec):
        return raw
    raw_skills = raw.get("skills")
    parsed_skills: Optional[List[str]] = None
    if isinstance(raw_skills, list):
        parsed_skills = [str(s).strip() for s in raw_skills if str(s).strip()]
    elif isinstance(raw_skills, str) and raw_skills.strip():
        parsed_skills = [s.strip() for s in raw_skills.split(",") if s.strip()]

    return CustomEnemySpec(
        template_name=raw.get("template_name"),
        name=raw.get("name"),
        faction=raw.get("faction"),
        race=raw.get("race"),
        combat_role=raw.get("combat_role") or raw.get("archetype"),
        unit_tier=str(raw.get("unit_tier") or raw.get("tier") or "NORMAL").upper(),
        defense_profile=str(raw.get("defense_profile") or "auto"),
        equipment=raw.get("equipment"),
        level_offset=int(raw.get("level_offset", 0) or 0),
        skills=parsed_skills,
    )


def _resolve_custom_template(spec: CustomEnemySpec) -> BestiaryTemplate:
    base_tpl: Optional[BestiaryTemplate] = None
    if spec.template_name and str(spec.template_name).strip().upper() not in ("", "CUSTOM", "NONE"):
        base_tpl = find_template_by_name(str(spec.template_name).strip())

    # 1. Faction
    faction: Faction = Faction.BANDITS
    if isinstance(spec.faction, Faction) and spec.faction != Faction.ANY:
        faction = spec.faction
    elif isinstance(spec.faction, str) and spec.faction.upper() in Faction.__members__ and spec.faction.upper() != "ANY":
        faction = Faction[spec.faction.upper()]
    elif base_tpl is not None and base_tpl.faction != Faction.ANY:
        faction = base_tpl.faction

    # 2. Race
    race: Race = Race.HUMAN
    if isinstance(spec.race, Race):
        race = spec.race
    elif isinstance(spec.race, str) and spec.race.upper() in Race.__members__:
        race = Race[spec.race.upper()]
    elif base_tpl is not None:
        race = base_tpl.race
    else:
        default_faction_races = {
            Faction.VOIDWOKEN: Race.CREATURE,
            Faction.UNDEAD: Race.UNDEAD_HUMAN,
            Faction.DEMONS: Race.DEMON,
            Faction.AUTOMATONS: Race.AUTOMATON,
            Faction.BEASTS: Race.CREATURE,
        }
        race = default_faction_races.get(faction, Race.HUMAN)

    # 3. Combat Role (Archetype class style)
    combat_role: Archetype = Archetype.FIGHTER
    if isinstance(spec.combat_role, Archetype):
        combat_role = spec.combat_role
    elif isinstance(spec.combat_role, str) and spec.combat_role.upper() in Archetype.__members__:
        combat_role = Archetype[spec.combat_role.upper()]
    elif base_tpl is not None:
        combat_role = base_tpl.archetype

    if combat_role in (Archetype.BOSS, Archetype.MINION):
        if base_tpl is not None:
            eq_l = base_tpl.equipment.lower()
            tac_l = base_tpl.ai_tactics.lower()
            nm_l = base_tpl.name.lower()
            if any(k in eq_l or k in tac_l or k in nm_l for k in ["dagger", "rogue", "assassin", "shadowblade", "cutthroat"]):
                combat_role = Archetype.ROGUE
            elif any(k in eq_l or k in tac_l or k in nm_l for k in ["bow", "crossbow", "ranger", "marksman", "hunter"]):
                combat_role = Archetype.RANGER
            elif any(k in eq_l or k in tac_l or k in nm_l for k in ["wand", "staff", "mage", "wizard", "pyro", "cryo", "elementalist"]):
                combat_role = Archetype.MAGE
            elif any(k in eq_l or k in tac_l or k in nm_l for k in ["shield", "bulwark", "tank", "guardian"]):
                combat_role = Archetype.TANK
            else:
                combat_role = Archetype.FIGHTER
        else:
            combat_role = Archetype.FIGHTER

    role_def = ROLE_DEFAULTS.get(combat_role, ROLE_DEFAULTS[Archetype.FIGHTER])
    role_changed = (
        base_tpl is not None
        and base_tpl.archetype not in (Archetype.BOSS, Archetype.MINION)
        and combat_role != base_tpl.archetype
    )

    # 4. Equipment, AI Tactics, GM Notes, GM Template ID, Name
    if spec.equipment and str(spec.equipment).strip():
        if role_changed and base_tpl is not None and str(spec.equipment).strip() == base_tpl.equipment:
            equipment = role_def["equipment"]
        else:
            equipment = str(spec.equipment).strip()
    elif base_tpl is not None and not role_changed:
        equipment = base_tpl.equipment
    else:
        equipment = role_def["equipment"]

    if base_tpl is not None and not role_changed:
        ai_tactics = base_tpl.ai_tactics
        gm_notes = base_tpl.gm_notes
        sig_skills = base_tpl.signature_skills
        sig_talents = base_tpl.signature_talents
    else:
        ai_tactics = role_def["ai_tactics"]
        gm_notes = role_def["gm_notes"]
        sig_skills = None
        sig_talents = None

    if spec.name and str(spec.name).strip():
        unit_name = str(spec.name).strip()
    elif base_tpl is not None:
        unit_name = base_tpl.name
    else:
        faction_short = {
            Faction.MAGISTERS: "Magister",
            Faction.VOIDWOKEN: "Voidwoken",
            Faction.UNDEAD: "Black Ring",
            Faction.BANDITS: "Outlaw",
            Faction.BEASTS: "Wild",
            Faction.DEMONS: "Demonic",
            Faction.AUTOMATONS: "Clockwork",
        }.get(faction, "Custom")
        role_short = combat_role.value.split("/")[0].strip()
        unit_name = f"{faction_short} {race.value} {role_short}"

    gm_id = base_tpl.gm_template_id if base_tpl is not None else role_def["gm_template_id"]

    return BestiaryTemplate(
        name=unit_name,
        gm_template_id=gm_id,
        faction=faction,
        race=race,
        archetype=combat_role,
        equipment=equipment,
        ai_tactics=ai_tactics,
        gm_notes=gm_notes,
        can_be_boss=(spec.unit_tier.upper() == "BOSS"),
        can_be_minion=(spec.unit_tier.upper() == "MINION"),
        signature_skills=sig_skills,
        signature_talents=sig_talents,
    )


def build_custom_encounter(
    party_config: PartyConfig,
    enemy_specs: List[Union[CustomEnemySpec, Dict[str, Any]]],
    encounter_type: Optional[Union[EncounterType, str]] = None,
    seed: Optional[int] = None,
) -> Encounter:
    """
    Interactive Encounter Builder engine.
    Builds a custom encounter from user-configured enemy specifications and automatically
    balances enemy durability (Physical Armor, Magic Armor, Vitality) and Action Economy
    against the party's size, level, Lone Wolf status, damage composition, and difficulty.

    Core Rule: If there is only 1 enemy in the encounter, the encounter is automatically
    defined and scaled as a Boss Encounter (Solo Boss / Overlord).
    """
    if seed is not None:
        random.seed(seed)

    specs = [_parse_enemy_spec(s) for s in enemy_specs]
    if not specs:
        specs = [CustomEnemySpec(template_name="Bandit Kingpin", unit_tier="BOSS")]

    # Normalize unit tiers
    valid_tiers = {"NORMAL", "MINION", "ELITE", "BOSS"}
    for s in specs:
        s.unit_tier = s.unit_tier.upper() if s.unit_tier and s.unit_tier.upper() in valid_tiers else "NORMAL"
        s.level_offset = max(-3, min(3, int(s.level_offset)))

    # 1. Determine Encounter Type & Enforce Solo Enemy = Boss Encounter Rule
    explicit_type: Optional[EncounterType] = None
    if isinstance(encounter_type, EncounterType):
        explicit_type = encounter_type
    elif isinstance(encounter_type, str) and encounter_type.upper() in EncounterType.__members__:
        explicit_type = EncounterType[encounter_type.upper()]

    solo_auto_promoted = False
    if len(specs) == 1:
        effective_encounter_type = EncounterType.BOSS
        if specs[0].unit_tier != "BOSS":
            solo_auto_promoted = True
            specs[0].unit_tier = "BOSS"
    else:
        tiers = [s.unit_tier for s in specs]
        if explicit_type is not None:
            effective_encounter_type = explicit_type
            if effective_encounter_type == EncounterType.BOSS and "BOSS" not in tiers:
                # Promote the first unit (or first Elite) to Boss Commander
                elite_idx = next((i for i, s in enumerate(specs) if s.unit_tier == "ELITE"), 0)
                specs[elite_idx].unit_tier = "BOSS"
        else:
            # Auto-detect from roster composition
            if "BOSS" in tiers:
                effective_encounter_type = EncounterType.BOSS
            elif all(t == "ELITE" for t in tiers) or (tiers.count("ELITE") >= len(tiers) / 2 and "MINION" not in tiers):
                effective_encounter_type = EncounterType.ELITE
            elif tiers.count("MINION") >= len(tiers) / 2 or len(specs) >= 6:
                effective_encounter_type = EncounterType.SWARM
            else:
                effective_encounter_type = EncounterType.STANDARD

    # 2. Construct NPCs with tier-appropriate base stats & abilities
    party_lvl = party_config.level
    enemies: List[NPC] = []
    resolved_templates: List[BestiaryTemplate] = [_resolve_custom_template(s) for s in specs]

    boss_count = sum(1 for s in specs if s.unit_tier == "BOSS")
    non_boss_count = max(0, len(specs) - boss_count)
    clamped_minions = min(5, max(0, len(specs) - 1))
    boss_scaling = calculate_boss_scaling(clamped_minions, party_config.is_lone_wolf)

    for idx, (spec, tpl) in enumerate(zip(specs, resolved_templates)):
        unit_lvl = max(1, min(25, party_lvl + spec.level_offset))
        tier = spec.unit_tier

        if len(specs) == 1:
            # Solo Boss / Overlord
            solo_scaling = calculate_boss_scaling(0, party_config.is_lone_wolf)
            npc = _create_npc(
                template=tpl,
                level=unit_lvl,
                party_config=party_config,
                title="Solo Boss / Overlord",
                archetype=Archetype.BOSS,
                max_slots=solo_scaling.boss_max_slots,
                armor_multiplier=solo_scaling.boss_armor_mult,
                vitality_multiplier=solo_scaling.boss_vitality_mult,
                attribute_bonus=solo_scaling.boss_attribute_bonus,
                con_bonus=solo_scaling.boss_con_bonus,
                retribution_bonus=solo_scaling.boss_retribution_bonus,
                initiative_bonus=solo_scaling.boss_initiative_bonus,
                perseverance_bonus=solo_scaling.boss_perseverance,
                leadership_bonus=solo_scaling.boss_leadership,
                defense_profile_name=spec.defense_profile,
                ap_recovery=solo_scaling.boss_ap_recovery,
                explicit_skills=spec.skills,
            )
        elif tier == "BOSS":
            npc = _create_npc(
                template=tpl,
                level=unit_lvl,
                party_config=party_config,
                title="Boss / Commander",
                archetype=Archetype.BOSS,
                max_slots=boss_scaling.boss_max_slots,
                armor_multiplier=boss_scaling.boss_armor_mult,
                vitality_multiplier=boss_scaling.boss_vitality_mult,
                attribute_bonus=boss_scaling.boss_attribute_bonus,
                con_bonus=boss_scaling.boss_con_bonus,
                retribution_bonus=boss_scaling.boss_retribution_bonus,
                initiative_bonus=boss_scaling.boss_initiative_bonus,
                perseverance_bonus=boss_scaling.boss_perseverance,
                leadership_bonus=boss_scaling.boss_leadership,
                defense_profile_name=spec.defense_profile,
                ap_recovery=boss_scaling.boss_ap_recovery,
                explicit_skills=spec.skills,
            )
        elif tier == "ELITE":
            prefix = "" if tpl.name.lower().startswith("elite ") else "Elite "
            elite_title = "Elite Lieutenant" if effective_encounter_type == EncounterType.BOSS else "Champion"
            elite_ap = 5 if len(specs) <= 2 and party_config.total_ap_per_round >= 12 else 4
            npc = _create_npc(
                template=tpl,
                level=unit_lvl,
                party_config=party_config,
                title=elite_title,
                archetype=tpl.archetype,
                name_prefix=prefix,
                max_slots=5,
                armor_multiplier=1.25,
                vitality_multiplier=1.15,
                perseverance_bonus=2,
                defense_profile_name=spec.defense_profile,
                ap_recovery=elite_ap,
                explicit_skills=spec.skills,
            )
        elif tier == "MINION":
            minion_title = "Swarmer" if effective_encounter_type == EncounterType.SWARM else "Minion"
            npc = _create_npc(
                template=tpl,
                level=unit_lvl,
                party_config=party_config,
                title=minion_title,
                archetype=Archetype.MINION,
                max_slots=2,
                armor_multiplier=boss_scaling.minion_armor_mult if effective_encounter_type == EncounterType.BOSS else 1.0,
                vitality_multiplier=boss_scaling.minion_vitality_mult if effective_encounter_type == EncounterType.BOSS else 1.0,
                defense_profile_name=spec.defense_profile if spec.defense_profile != "auto" else None,
                ap_recovery=4,
                explicit_skills=spec.skills,
            )
        else:  # NORMAL
            if effective_encounter_type == EncounterType.BOSS:
                norm_title = "Elite Lieutenant" if non_boss_count == 1 else "Minion"
                norm_slots = boss_scaling.minion_max_slots
                norm_arm = boss_scaling.minion_armor_mult
                norm_vit = boss_scaling.minion_vitality_mult
                norm_ap = boss_scaling.minion_ap_recovery
            else:
                norm_title = "Combatant"
                norm_slots = None
                norm_arm = 1.0
                norm_vit = 1.0
                norm_ap = 5 if (len(specs) == 2 and party_config.total_ap_per_round >= 12) else 4

            npc = _create_npc(
                template=tpl,
                level=unit_lvl,
                party_config=party_config,
                title=norm_title,
                archetype=tpl.archetype,
                max_slots=norm_slots,
                armor_multiplier=norm_arm,
                vitality_multiplier=norm_vit,
                defense_profile_name=spec.defense_profile if spec.defense_profile != "auto" else None,
                ap_recovery=norm_ap,
                explicit_skills=spec.skills,
            )

        enemies.append(npc)

    # 3. Dynamic Encounter Budget Calibration
    # Calibrate total enemy EHP to match the party's expected EHP, difficulty tier,
    # action economy ratio, and intentional level offsets.
    party_ehp = estimate_party_ehp(party_config)
    party_ap = party_config.total_ap_per_round
    enemy_ap = sum(e.stats.ap_recovery for e in enemies)

    diff_target_ratios = {
        Difficulty.STORY: 0.75,
        Difficulty.BALANCED: 1.12,
        Difficulty.TACTICIAN: 1.48,
        Difficulty.DEADLY: 1.82,
    }
    base_target_ratio = diff_target_ratios.get(party_config.difficulty, 1.12)

    # Action economy compensation: fewer enemies need slightly more armor/HP buffer against focus fire;
    # huge swarms need slightly less per-unit EHP so high turn counts don't become tedious.
    ap_comp = max(0.75, min(1.30, (party_ap / max(4, enemy_ap)) ** 0.25))

    # Preserve intentional level offset difficulty shifts (+1/+2 makes encounter tougher, -1/-2 makes it lighter)
    avg_offset = sum(s.level_offset for s in specs) / max(1, len(specs))
    offset_factor = max(0.65, min(1.65, 1.22 ** avg_offset))

    target_total_ehp = party_ehp * base_target_ratio * ap_comp * offset_factor
    raw_total_ehp = sum(e.total_ehp for e in enemies)

    scale_factor = 1.0
    if raw_total_ehp > 0:
        scale_factor = max(0.45, min(2.25, target_total_ehp / raw_total_ehp))
        if abs(scale_factor - 1.0) > 0.03:
            for e in enemies:
                e.stats.physical_armor = max(0, int(round(e.stats.physical_armor * scale_factor)))
                e.stats.magic_armor = max(0, int(round(e.stats.magic_armor * scale_factor)))
                e.stats.vitality = max(15, int(round(e.stats.vitality * scale_factor)))

    # Build Balancer Scaling Explanation
    if len(specs) == 1:
        auto_note = "Solo enemy automatically promoted to Solo Boss / Overlord. " if solo_auto_promoted else ""
        balancer_notes = (
            f"{auto_note}Solo Boss Duel scaling applied (+{enemies[0].stats.ap_recovery} AP/turn, "
            f"Perseverance {enemies[0].stats.combat_abilities.get('Perseverance', 5)}, "
            f"Budget Calibration: {scale_factor:.2f}x durability for {party_config.party_size}-player Lvl {party_lvl} party)."
        )
    else:
        balancer_notes = (
            f"Interactive Roster Auto-Balancer ({len(enemies)} combatants, {enemy_ap} Enemy AP vs {party_ap} Party AP): "
            f"Applied {scale_factor:.2f}x durability calibration to align total enemy EHP ({sum(e.total_ehp for e in enemies):,}) "
            f"with {party_config.difficulty.name.title()} target budget."
        )

    # 4. Determine dominant Faction & Race for encounter metadata
    factions_present = {e.faction for e in enemies}
    dominant_faction = next(iter(factions_present)) if len(factions_present) == 1 else Faction.ANY

    races_present = {e.race for e in enemies}
    dominant_race = next(iter(races_present)) if len(races_present) == 1 else None

    # 5. Terrain & Hazards
    terrain_options = [
        "Elevated wooden scaffolding providing High Ground (+20% damage) on the northern flank.",
        "Chokepoint bridge flanked by deep water and scattered explosive oil barrels.",
        "Enclosed stone courtyard with broken pillars granting full line-of-sight cover.",
        "Narrow cavern corridor with slick poison slime puddles and high stalagmites.",
        "Ruined shrine courtyard with cursed blood pools and ancient statues."
    ]
    tactical_terrain = random.choice(terrain_options)

    hazard_pool = [
        "2x Oil Barrels placed near central choke point (ready for Ignition/Fireball).",
        "Water surface puddle on southern side (susceptible to Electrocution or Freezing).",
        "Poison barrel on high ground (can be detonated or used to heal Undead).",
        "Steam cloud obscuring ranged line-of-sight in center corridor.",
        "Scattered crates blocking direct melee charge paths."
    ]
    environmental_hazards = random.sample(hazard_pool, k=2)

    boss_npc = next((e for e in enemies if e.archetype == Archetype.BOSS), None)
    actual_minions = max(0, len(enemies) - 1) if effective_encounter_type == EncounterType.BOSS else None

    analysis = analyze_encounter_balance(
        party_config=party_config,
        enemies=enemies,
        encounter_type=effective_encounter_type,
        minion_count=actual_minions,
        boss_scaling_notes=balancer_notes,
    )

    faction_label = dominant_faction.value if dominant_faction != Faction.ANY else "Custom Mixed Roster"
    if effective_encounter_type == EncounterType.BOSS and boss_npc:
        minion_sub = f"{actual_minions} Minion{'s' if actual_minions != 1 else ''}" if actual_minions and actual_minions > 0 else "Solo Boss"
        encounter_name = f"{faction_label}: Boss Encounter - {boss_npc.name} ({minion_sub}) (Lvl {party_lvl})"
    else:
        encounter_name = f"{faction_label}: {effective_encounter_type.value} ({len(enemies)} Enemies, Lvl {party_lvl})"

    return Encounter(
        name=encounter_name,
        encounter_type=effective_encounter_type,
        faction=dominant_faction,
        party_config=party_config,
        enemies=enemies,
        environmental_hazards=environmental_hazards,
        tactical_terrain=tactical_terrain,
        analysis=analysis,
        selected_race=dominant_race,
        minion_count=actual_minions,
        boss_name=boss_npc.name if boss_npc else None,
    )

