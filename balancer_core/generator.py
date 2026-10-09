"""
DOS2 Encounter Balancer - Generation & Balance Analysis Engine
Generates tactically sound, faction-coherent encounters matching DOS2 GM mode mechanics
and evaluates balance metrics (Action Economy, EHP ratio, Damage Profile compatibility).
"""

import random
from typing import List, Optional
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
)
from .skills_db import get_skills_for_archetype
from .bestiary import get_templates_by_faction, BestiaryTemplate, BESTIARY


def analyze_encounter_balance(
    party_config: PartyConfig,
    enemies: List[NPC],
    encounter_type: EncounterType
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
    if encounter_type == EncounterType.BOSS:
        tactical_recs.append("Boss Mechanics: Do NOT let players surround the Boss alone; use Minions to bodyblock and soak hits.")
    elif encounter_type == EncounterType.SWARM:
        tactical_recs.append("Swarm Mechanics: Spread minions across different angles so a single AoE spell doesn't wipe them on Turn 1.")

    # Tuning Dials for GM on the fly
    tuning_dials = {
        "To make it EASIER on the fly": "Reduce enemy Magic/Physical Armor by 20% or have an enemy spend 2 AP buffing rather than attacking.",
        "To make it HARDER on the fly": "Spawn 1-2 delayed reinforcements from the shadows, or give the leader an extra source spell.",
        "If a Player goes down early": "Have the enemy prioritize self-buffing (Fortify/Armor of Frost) or taunting instead of executing the downed hero."
    }

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
    difficulty: Optional[Difficulty] = None
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
    missing_schools = [s for s in unique_schools if stats.combat_abilities.get(s, 0) == 0]
    if missing_schools:
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
            difficulty=difficulty or Difficulty.BALANCED
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
) -> NPC:
    actual_archetype = archetype or template.archetype
    stats = calculate_enemy_stats(
        level, 
        actual_archetype, 
        party_config.difficulty, 
        party_config.damage_profile, 
        race=template.race
    )
    if armor_multiplier != 1.0:
        stats.physical_armor = int(stats.physical_armor * armor_multiplier)
        stats.magic_armor = int(stats.magic_armor * armor_multiplier)
        
    calc_max_skills = 3 + max(0, stats.memory - 10)
    slots = min(max_slots, calc_max_skills) if max_slots is not None else calc_max_skills
    
    skills = get_skills_for_archetype(
        actual_archetype,
        level,
        max_slots=slots,
        race=template.race,
        ai_tactics=template.ai_tactics,
        equipment=template.equipment,
        signature_skills=getattr(template, "signature_skills", None)
    )
    
    align_combat_abilities_with_skills(
        stats,
        skills,
        actual_archetype,
        level=level,
        race=template.race,
        difficulty=party_config.difficulty
    )
    
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
        gm_notes=template.gm_notes,
        gm_template_id=template.gm_template_id
    )


def generate_encounter(
    party_config: PartyConfig,
    encounter_type: Optional[EncounterType] = None,
    faction: Optional[Faction] = None,
    race: Optional[Race] = None,
    seed: Optional[int] = None
) -> Encounter:
    """
    Generates a complete, balanced DOS2 GM mode encounter with exact stats,
    skills, gear, terrain, and balance analytics.
    Optionally filters enemies to a single specific race (e.g. Race.HUMAN, Race.UNDEAD_DWARF).
    """
    if seed is not None:
        random.seed(seed)

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
        # If the faction + race combo has no templates, pull across all factions to honor the race
        if not templates:
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
            
            # Prioritize distinct races for factions with multi-racial rosters (Bandits, Undead, Magisters)
            used_races = [e.race for e in enemies]
            unrepresented = [t for t in matching if t.race not in used_races]
            candidates = unrepresented if unrepresented else matching
            template = random.choice(candidates) if candidates else random.choice(templates)
            
            enemies.append(_create_npc(template, party_lvl, party_config, title=f"Unit #{i+1}"))

    elif encounter_type == EncounterType.BOSS:
        boss_templates = [t for t in templates if t.can_be_boss or t.archetype == Archetype.BOSS]
        if not boss_templates:
            boss_templates = templates
        boss_tpl = random.choice(boss_templates)
        
        boss_level = party_lvl + (1 if party_config.difficulty != Difficulty.STORY else 0)
        enemies.append(_create_npc(
            boss_tpl, 
            boss_level, 
            party_config, 
            title="Boss / Commander", 
            archetype=Archetype.BOSS, 
            max_slots=6
        ))
        
        minion_count = 2 if party_config.is_lone_wolf else 3
        regular_templates = [t for t in templates if not t.can_be_boss] or templates
        for i in range(minion_count):
            used_races = [e.race for e in enemies]
            unrepresented = [t for t in regular_templates if t.race not in used_races]
            candidates = unrepresented if unrepresented else regular_templates
            tpl = random.choice(candidates)

            minion_level = max(1, party_lvl - 1)
            enemies.append(_create_npc(tpl, minion_level, party_config, title=f"Minion #{i+1}", max_slots=3))

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
                title=f"Swarmer #{i+1}", 
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
                title=f"Champion #{i+1}", 
                name_prefix="Elite ", 
                max_slots=5, 
                armor_multiplier=1.25
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
    analysis = analyze_encounter_balance(party_config, enemies, encounter_type)

    if race is not None:
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
        selected_race=race
    )
