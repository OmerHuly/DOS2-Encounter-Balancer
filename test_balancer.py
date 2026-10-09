"""
DOS2 Encounter Balancer - Verification & Test Suite
Runs validation tests on generation, balance math, factions, encounter types,
and CLI execution against DOS2 Definitive Edition mechanics.
"""

import os
import sys
import unittest
import subprocess

# Ensure balancer_core is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from balancer_core import (
    PartyConfig,
    EncounterType,
    Faction,
    Race,
    Archetype,
    DamageProfile,
    Difficulty,
    generate_encounter,
    export_encounter_to_markdown,
    BESTIARY,
    calculate_enemy_stats,
    calculate_attributes_for_level,
    sync_stats_with_combat_abilities,
    calculate_talents,
    get_talent_points_for_level,
    get_base_vitality,
    get_base_armor,
    DEFENSE_PROFILES,
    DefenseProfile,
    calculate_boss_scaling,
)
from balancer_core.exporter import format_enemy_terminal_card
from balancer_core.skills_db import (
    get_racial_skills_for_race,
    get_skills_for_archetype,
    is_skill_compatible_with_equipment,
)


class TestDOS2EncounterBalancer(unittest.TestCase):

    def test_vitality_and_armor_growth(self):
        """Verify baseline vitality and armor growth across level leaps (9, 13, 16, 18)."""
        # Base table values
        self.assertEqual(get_base_vitality(1), 30)
        self.assertEqual(get_base_vitality(4), 85)
        self.assertEqual(get_base_vitality(9), 235)
        self.assertEqual(get_base_vitality(13), 560)
        self.assertEqual(get_base_vitality(16), 1015)
        self.assertEqual(get_base_vitality(18), 1790)
        self.assertEqual(get_base_vitality(20), 2815)
        
        # Verify armor scales up with level
        self.assertGreater(get_base_armor(5), get_base_armor(4))
        self.assertGreater(get_base_armor(13), get_base_armor(12))

    def test_standard_skirmish_generation(self):
        """Test standard skirmish encounter generation for a level 4 party."""
        party = PartyConfig(level=4, party_size=4, damage_profile=DamageProfile.BALANCED)
        enc = generate_encounter(party, encounter_type=EncounterType.STANDARD, faction=Faction.MAGISTERS, seed=42)
        
        self.assertEqual(enc.encounter_type, EncounterType.STANDARD)
        self.assertEqual(enc.faction, Faction.MAGISTERS)
        self.assertEqual(len(enc.enemies), 4)
        
        for npc in enc.enemies:
            self.assertEqual(npc.level, 4)
            self.assertGreater(npc.stats.vitality, 0)
            self.assertGreater(npc.stats.physical_armor, 0)
            self.assertGreater(npc.stats.magic_armor, 0)
            # Memory constraint verification: memorized skills and used memory slots must not exceed available memory slots
            max_memory_slots = 3 + max(0, npc.stats.memory - 10)
            self.assertEqual(npc.max_memory_slots, max_memory_slots)
            self.assertLessEqual(npc.used_memory_slots, max_memory_slots)
            self.assertLessEqual(len(npc.memorized_skills), max_memory_slots)
            self.assertTrue(bool(npc.gm_template_id), f"{npc.name} should have a GM template ID")

    def test_boss_encounter_generation(self):
        """Test boss battle generation: 1 boss (+1 lvl) + 3 minions."""
        party = PartyConfig(level=5, party_size=4, difficulty=Difficulty.BALANCED)
        enc = generate_encounter(party, encounter_type=EncounterType.BOSS, faction=Faction.VOIDWOKEN, seed=123)
        
        self.assertEqual(enc.encounter_type, EncounterType.BOSS)
        self.assertGreaterEqual(len(enc.enemies), 3)
        
        boss = enc.enemies[0]
        self.assertEqual(boss.archetype, Archetype.BOSS)
        self.assertEqual(boss.level, 6)  # Level + 1
        self.assertEqual(boss.stats.ap_start, 6)
        self.assertEqual(boss.stats.ap_recovery, 4)
        
        # Verify boss is significantly tankier than regular minions
        minion = enc.enemies[1]
        self.assertGreater(boss.total_ehp, minion.total_ehp * 2)

    def test_swarm_battle_generation(self):
        """Test swarm battle generation: 7 fragile minions with lower HP."""
        party = PartyConfig(level=6, party_size=4)
        enc = generate_encounter(party, encounter_type=EncounterType.SWARM, faction=Faction.BEASTS, seed=77)
        
        self.assertEqual(enc.encounter_type, EncounterType.SWARM)
        self.assertEqual(len(enc.enemies), 7)
        for minion in enc.enemies:
            self.assertEqual(minion.archetype, Archetype.MINION)
            self.assertEqual(minion.level, 5)  # Level - 1
            # Minion HP is fragile
            self.assertLess(minion.stats.vitality, get_base_vitality(5))

    def test_elite_encounter_generation(self):
        """Test elite encounter: 3 champions with elevated armor."""
        party = PartyConfig(level=8, party_size=4)
        enc = generate_encounter(party, encounter_type=EncounterType.ELITE, faction=Faction.UNDEAD, seed=88)
        
        self.assertEqual(enc.encounter_type, EncounterType.ELITE)
        self.assertEqual(len(enc.enemies), 3)
        for champ in enc.enemies:
            self.assertTrue(champ.name.startswith("Elite "))
            self.assertEqual(champ.level, 8)

    def test_all_factions_available_and_valid(self):
        """Ensure all 7 GM Mode factions produce valid encounters with authentic templates."""
        party = PartyConfig(level=5, party_size=4)
        factions = [
            Faction.MAGISTERS,
            Faction.VOIDWOKEN,
            Faction.UNDEAD,
            Faction.BANDITS,
            Faction.BEASTS,
            Faction.DEMONS,
            Faction.AUTOMATONS,
        ]
        for f in factions:
            enc = generate_encounter(party, encounter_type=EncounterType.STANDARD, faction=f, seed=99)
            self.assertEqual(enc.faction, f)
            self.assertGreater(len(enc.enemies), 0)
            for npc in enc.enemies:
                self.assertTrue(len(npc.gm_template_id) > 0)

    def test_lone_wolf_adaptation(self):
        """Verify Lone Wolf party adjustments (2 players, +30% boost + 6 AP/round)."""
        party_lw = PartyConfig(level=5, party_size=2, is_lone_wolf=True)
        party_norm = PartyConfig(level=5, party_size=2, is_lone_wolf=False)
        
        self.assertEqual(party_lw.total_ap_per_round, 12)  # 2 * 6 AP
        self.assertEqual(party_norm.total_ap_per_round, 8)  # 2 * 4 AP
        
        enc_lw = generate_encounter(party_lw, encounter_type=EncounterType.BOSS, seed=1)
        # For Lone Wolf (2 players), boss spawns 2 minions instead of 3
        self.assertEqual(len(enc_lw.enemies), 3)  # 1 boss + 2 minions

    def test_damage_profile_diagnostics(self):
        """Verify that damage profile triggers proper analytical feedback."""
        party_phys = PartyConfig(level=5, party_size=4, damage_profile=DamageProfile.PURE_PHYSICAL)
        enc = generate_encounter(party_phys, encounter_type=EncounterType.STANDARD, seed=10)
        self.assertIsNotNone(enc.analysis)
        self.assertIn("Physical", enc.analysis.damage_compatibility_notes)

    def test_markdown_export(self):
        """Verify Markdown export produces a valid non-empty file on disk."""
        party = PartyConfig(level=3, party_size=4)
        enc = generate_encounter(party, encounter_type=EncounterType.STANDARD, faction=Faction.BANDITS, seed=5)
        out_dir = "test_output"
        os.makedirs(out_dir, exist_ok=True)
        md_file = export_encounter_to_markdown(enc, output_dir=out_dir)
        
        self.assertTrue(os.path.exists(md_file))
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("# ⚔️ DOS2 GM Battle Sheet:", content)
        self.assertIn("Bandits & Outlaws", content)
        
        # Cleanup
        os.remove(md_file)
        os.rmdir(out_dir)

    def test_cli_execution_end_to_end(self):
        """Run dos2_encounter_balancer.py as a subprocess to verify CLI flags."""
        script_path = os.path.abspath("dos2_encounter_balancer.py")
        cmd = [
            sys.executable,
            script_path,
            "--level", "6",
            "--party-size", "4",
            "--type", "boss",
            "--faction", "magisters",
            "--difficulty", "classic"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, f"CLI failed: {result.stderr}")
        self.assertIn("DIVINITY: ORIGINAL SIN 2 - GM ENCOUNTER BALANCER", result.stdout)
        self.assertIn("Magisters & Divine Order: Boss Encounter", result.stdout)
    def test_multiracial_bandits_variety(self):
        """Verify Bandits have rich multi-racial rosters (Human, Elf, Dwarf, Lizard, Undead) and generate varied gangs."""
        bandit_templates = [t for t in BESTIARY if t.faction == Faction.BANDITS]
        bandit_races = {t.race for t in bandit_templates}
        self.assertIn(Race.HUMAN, bandit_races)
        self.assertIn(Race.ELF, bandit_races)
        self.assertIn(Race.DWARF, bandit_races)
        self.assertIn(Race.LIZARD, bandit_races)
        self.assertIn(Race.UNDEAD, bandit_races)

        # Generate a standard 4-man bandit encounter and verify diverse races
        party = PartyConfig(level=4, party_size=4)
        enc = generate_encounter(party, encounter_type=EncounterType.STANDARD, faction=Faction.BANDITS, seed=42)
        generated_races = {npc.race for npc in enc.enemies}
        # A 4-man bandit group should have at least 3 distinct races represented
        self.assertGreaterEqual(len(generated_races), 3)

    def test_multiracial_undead_variety(self):
        """Verify Undead legions feature Undead Humans, Elves, Dwarves, and Lizards."""
        undead_templates = [t for t in BESTIARY if t.faction == Faction.UNDEAD]
        undead_races = {t.race for t in undead_templates}
        self.assertIn(Race.UNDEAD_HUMAN, undead_races)
        self.assertIn(Race.UNDEAD_ELF, undead_races)
        self.assertIn(Race.UNDEAD_DWARF, undead_races)
        self.assertIn(Race.UNDEAD_LIZARD, undead_races)

    def test_play_dead_and_racial_skills_on_all_undead(self):
        """Verify that Play Dead applies to ALL Undead races along with their origin racial skill."""
        all_undead_races = [
            Race.UNDEAD,
            Race.UNDEAD_HUMAN,
            Race.UNDEAD_ELF,
            Race.UNDEAD_DWARF,
            Race.UNDEAD_LIZARD,
        ]
        for r in all_undead_races:
            skills = get_racial_skills_for_race(r)
            skill_names = [s.name for s in skills]
            self.assertIn("Play Dead", skill_names, f"Play Dead must be present for {r}")

        # Undead Elf has Play Dead AND Flesh Sacrifice
        undead_elf_skills = [s.name for s in get_racial_skills_for_race(Race.UNDEAD_ELF)]
        self.assertIn("Play Dead", undead_elf_skills)
        self.assertIn("Flesh Sacrifice", undead_elf_skills)

        # Undead Dwarf has Play Dead AND Petrifying Touch
        undead_dwarf_skills = [s.name for s in get_racial_skills_for_race(Race.UNDEAD_DWARF)]
        self.assertIn("Play Dead", undead_dwarf_skills)
        self.assertIn("Petrifying Touch", undead_dwarf_skills)

        # Undead Lizard has Play Dead AND Dragon's Blaze
        undead_lizard_skills = [s.name for s in get_racial_skills_for_race(Race.UNDEAD_LIZARD)]
        self.assertIn("Play Dead", undead_lizard_skills)
        self.assertIn("Dragon's Blaze", undead_lizard_skills)

    def test_single_race_undead_dwarf_encounter(self):
        """Verify that requesting Race.UNDEAD_DWARF produces 100% Undead Dwarf enemies."""
        party = PartyConfig(level=5, party_size=4)
        enc = generate_encounter(party, encounter_type=EncounterType.STANDARD, race=Race.UNDEAD_DWARF, seed=99)
        self.assertEqual(enc.selected_race, Race.UNDEAD_DWARF)
        self.assertGreater(len(enc.enemies), 0)
        for npc in enc.enemies:
            self.assertEqual(npc.race, Race.UNDEAD_DWARF, f"{npc.name} should be an Undead Dwarf")
            # All undead dwarves should have both Play Dead and Petrifying Touch
            skill_names = [s.name for s in npc.skills]
            self.assertIn("Play Dead", skill_names)
            self.assertIn("Petrifying Touch", skill_names)

    def test_single_race_human_encounter(self):
        """Verify that requesting Race.HUMAN produces 100% Human enemies."""
        party = PartyConfig(level=4, party_size=4)
        enc = generate_encounter(party, encounter_type=EncounterType.STANDARD, race=Race.HUMAN, seed=55)
        self.assertEqual(enc.selected_race, Race.HUMAN)
        for npc in enc.enemies:
            self.assertEqual(npc.race, Race.HUMAN, f"{npc.name} should be Human")

    def test_single_race_boss_encounter_undead_dwarf(self):
        """Verify that requesting a Boss battle with Race.UNDEAD_DWARF produces an Undead Dwarf Boss and Undead Dwarf Minions."""
        party = PartyConfig(level=6, party_size=4)
        enc = generate_encounter(party, encounter_type=EncounterType.BOSS, race=Race.UNDEAD_DWARF, seed=7)
        self.assertEqual(enc.encounter_type, EncounterType.BOSS)
        for npc in enc.enemies:
            self.assertEqual(npc.race, Race.UNDEAD_DWARF)

    def test_cli_single_race_flag(self):
        """Verify CLI execution with --race undead-dwarf flag."""
        script_path = os.path.abspath("dos2_encounter_balancer.py")
        cmd = [
            sys.executable,
            script_path,
            "--level", "5",
            "--party-size", "4",
            "--type", "standard",
            "--race", "undead-dwarf",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, f"CLI failed: {result.stderr}")
        self.assertIn("Undead Dwarf (Single Race Encounter)", result.stdout)
    def test_bandit_dwarf_brawler_skills_match_ai_tactics(self):
        """Verify Bandit Dwarf Brawler memorizes Bull Horns and Whirlwind as described in AI tactics."""
        brawler_tpl = [t for t in BESTIARY if t.name == "Bandit Dwarf Brawler"][0]
        skills = get_skills_for_archetype(
            brawler_tpl.archetype,
            level=4,
            max_slots=4,
            race=brawler_tpl.race,
            ai_tactics=brawler_tpl.ai_tactics,
            equipment=brawler_tpl.equipment
        )
        skill_names = [s.name for s in skills]
        # Bull Horns and Whirlwind must be memorized
        self.assertIn("Bull Horns", skill_names)
        self.assertIn("Whirlwind", skill_names)
        self.assertIn("Petrifying Touch", skill_names)  # Dwarf racial
        # Must NOT have Shields Up because Dual Waraxes has no shield
        self.assertNotIn("Shields Up", skill_names)
        self.assertNotIn("Bouncing Shield", skill_names)

    def test_equipment_compatibility_constraints(self):
        """Verify that shield, dagger, and ranged skills strictly require matching equipment."""
        from balancer_core.skills_db import SKILLS_DATABASE
        skill_map = {s.name: s for s in SKILLS_DATABASE}

        # Shields Up requires a shield
        self.assertFalse(is_skill_compatible_with_equipment(skill_map["Shields Up"], "Dual Waraxes"))
        self.assertTrue(is_skill_compatible_with_equipment(skill_map["Shields Up"], "One-handed Longsword + Divine Steel Shield"))
        self.assertTrue(is_skill_compatible_with_equipment(skill_map["Bouncing Shield"], "Rusty Cleaver + Splintered Buckler"))
        self.assertFalse(is_skill_compatible_with_equipment(skill_map["Bouncing Shield"], "Two-Handed Greataxe"))

        # Backlash requires daggers
        self.assertFalse(is_skill_compatible_with_equipment(skill_map["Backlash"], "Two-Handed Greatsword"))
        self.assertTrue(is_skill_compatible_with_equipment(skill_map["Backlash"], "Pair of Serrated Daggers"))
        self.assertTrue(is_skill_compatible_with_equipment(skill_map["Backlash"], "Dual Bone Shivs"))

        # Pin Down requires a bow / crossbow
        self.assertFalse(is_skill_compatible_with_equipment(skill_map["Pin Down"], "Dual Waraxes"))
        self.assertTrue(is_skill_compatible_with_equipment(skill_map["Pin Down"], "Recurve Shortbow + Earth Arrows"))

    def test_rogue_skills_priority_not_overridden_by_warfare(self):
        """Verify Rogues memorize Scoundrel abilities instead of being flooded with Warfare skills."""
        rogue_skills = get_skills_for_archetype(
            Archetype.ROGUE,
            level=4,
            max_slots=4,
            race=Race.HUMAN,
            equipment="Pair of Serrated Daggers"
        )
        skill_schools = [s.school for s in rogue_skills]
        # Should have Scoundrel abilities, not Warfare
        self.assertIn("Scoundrel", skill_schools)
        self.assertNotIn("Shields Up", [s.name for s in rogue_skills])
        
    def test_innate_skills_do_not_consume_memory_slots(self):
        """Verify all DOS2 racial skills are innate and cost 0 memory points."""
        racial_skills = [
            get_racial_skills_for_race(Race.DWARF),
            get_racial_skills_for_race(Race.HUMAN),
            get_racial_skills_for_race(Race.ELF),
            get_racial_skills_for_race(Race.LIZARD),
            get_racial_skills_for_race(Race.UNDEAD),
        ]
        for skill_list in racial_skills:
            for s in skill_list:
                self.assertTrue(s.is_innate, f"{s.name} must be marked as innate")
                self.assertEqual(s.memory_cost, 0, f"{s.name} must cost 0 memory points")

    def test_dwarf_innate_petrifying_touch_does_not_reduce_memorized_slots(self):
        """Verify Dwarves have innate Petrifying Touch without consuming memorized skill slots."""
        # When requesting 3 memorized slots for a Dwarf, they must receive Petrifying Touch + 3 class skills
        dwarf_skills = get_skills_for_archetype(
            Archetype.FIGHTER,
            level=4,
            max_slots=3,
            race=Race.DWARF,
            equipment="Warhammer + Round Wooden Shield"
        )
        dwarf_skill_names = [s.name for s in dwarf_skills]
        self.assertIn("Petrifying Touch", dwarf_skill_names)
        
        innate = [s for s in dwarf_skills if s.is_innate]
        memorized = [s for s in dwarf_skills if not s.is_innate]
        self.assertEqual(len(innate), 1)
        self.assertEqual(innate[0].name, "Petrifying Touch")
        self.assertEqual(len(memorized), 3, "Dwarf must receive full 3 memorized class skills in addition to innate Petrifying Touch")
        
        # Total memory slots consumed must be exactly 3 (Petrifying Touch costs 0)
        total_mem_used = sum(s.memory_cost for s in dwarf_skills)
        self.assertEqual(total_mem_used, 3)

    def test_undead_dwarf_dual_innate_skills_and_memory(self):
        """Verify Undead Dwarves retain both Play Dead and Petrifying Touch at 0 memory cost."""
        party = PartyConfig(level=4, party_size=4)
        enc = generate_encounter(party, encounter_type=EncounterType.STANDARD, race=Race.UNDEAD_DWARF, seed=12)
        for npc in enc.enemies:
            skill_names = [s.name for s in npc.skills]
            self.assertIn("Play Dead", skill_names)
            self.assertIn("Petrifying Touch", skill_names)
            
            # Innate skills check
            innate_names = [s.name for s in npc.innate_skills]
            self.assertIn("Play Dead", innate_names)
            self.assertIn("Petrifying Touch", innate_names)
            for s in npc.innate_skills:
                self.assertEqual(s.memory_cost, 0)
            
            # Memory accounting check
            self.assertLessEqual(npc.used_memory_slots, npc.max_memory_slots)
            self.assertLessEqual(len(npc.memorized_skills), npc.max_memory_slots)

    def test_level_1_attribute_points_start_at_3(self):
        """Verify that at level 1, characters start with exactly 3 attribute points to allocate (above base 10)."""
        standard_archetypes = [
            Archetype.TANK,
            Archetype.FIGHTER,
            Archetype.RANGER,
            Archetype.ROGUE,
            Archetype.MAGE,
            Archetype.BATTLEMAGE,
            Archetype.CLERIC,
            Archetype.SUMMONER,
            Archetype.MINION,
        ]
        for arch in standard_archetypes:
            stats = calculate_attributes_for_level(level=1, archetype=arch, polymorph_points=0)
            allocated_points = sum(val - 10 for val in stats)
            self.assertEqual(
                allocated_points, 3,
                f"Archetype {arch} at level 1 must have exactly 3 attribute points allocated above base 10, got {allocated_points}"
            )

    def test_attribute_point_scaling_per_level(self):
        """Verify attribute points scale as: 3 points at lvl 1, and +2 per level thereafter."""
        expected_points_by_level = {
            1: 3,
            2: 5,   # 3 + 2
            3: 7,   # 3 + 4
            4: 9,   # 3 + 6
            5: 11,  # 3 + 8
            10: 21, # 3 + 18
            15: 31, # 3 + 28
            20: 41, # 3 + 38
        }
        for lvl, expected_pts in expected_points_by_level.items():
            stats = calculate_attributes_for_level(level=lvl, archetype=Archetype.TANK, polymorph_points=0)
            allocated = sum(val - 10 for val in stats)
            self.assertEqual(
                allocated, expected_pts,
                f"Level {lvl} without Polymorph should have {expected_pts} points allocated, got {allocated}"
            )

    def test_polymorph_provides_one_attribute_point_per_point_invested(self):
        """Verify that points invested in Polymorph provide 1 free attribute point per point invested."""
        # Level 4 baseline: 3 + (4 - 1) * 2 = 9 points
        base_stats = calculate_attributes_for_level(level=4, archetype=Archetype.FIGHTER, polymorph_points=0)
        base_allocated = sum(val - 10 for val in base_stats)
        self.assertEqual(base_allocated, 9)

        for poly_pts in [1, 2, 3, 5, 10]:
            poly_stats = calculate_attributes_for_level(level=4, archetype=Archetype.FIGHTER, polymorph_points=poly_pts)
            poly_allocated = sum(val - 10 for val in poly_stats)
            self.assertEqual(
                poly_allocated, base_allocated + poly_pts,
                f"With {poly_pts} Polymorph points, total allocated points should be {base_allocated + poly_pts}, got {poly_allocated}"
            )

    def test_enemy_stats_calculation_includes_polymorph_attribute_bonus(self):
        """Verify calculate_enemy_stats grants additional attributes when Polymorph is in combat abilities."""
        # Level 4 Fighter: calculate_combat_abilities gives Warfare 3 and Polymorph 1
        fighter_stats = calculate_enemy_stats(level=4, archetype=Archetype.FIGHTER, race=Race.ELF)
        self.assertIn("Polymorph", fighter_stats.combat_abilities)
        fighter_poly = fighter_stats.combat_abilities["Polymorph"]
        self.assertEqual(fighter_poly, 1)

        fighter_total_allocated = (
            (fighter_stats.strength - 10) +
            (fighter_stats.finesse - 10) +
            (fighter_stats.intelligence - 10) +
            (fighter_stats.constitution - 10) +
            (fighter_stats.memory - 10) +
            (fighter_stats.wits - 10)
        )
        # 9 (lvl 4) + 1 (Polymorph) = 10 points
        self.assertEqual(fighter_total_allocated, 10)

        # Level 4 Tank: 0 Polymorph points by default -> 9 points
        tank_stats = calculate_enemy_stats(level=4, archetype=Archetype.TANK, race=Race.ELF)
        tank_total_allocated = (
            (tank_stats.strength - 10) +
            (tank_stats.finesse - 10) +
            (tank_stats.intelligence - 10) +
            (tank_stats.constitution - 10) +
            (tank_stats.memory - 10) +
            (tank_stats.wits - 10)
        )
        self.assertEqual(tank_total_allocated, 9)

        # Now sync Tank with combat abilities that include Polymorph: 2
        tank_stats.combat_abilities["Polymorph"] = 2
        sync_stats_with_combat_abilities(tank_stats, level=4, archetype=Archetype.TANK, race=Race.ELF)
        updated_allocated = (
            (tank_stats.strength - 10) +
            (tank_stats.finesse - 10) +
            (tank_stats.intelligence - 10) +
            (tank_stats.constitution - 10) +
            (tank_stats.memory - 10) +
            (tank_stats.wits - 10)
        )
        # 9 (lvl 4) + 2 (Polymorph) = 11 points
        self.assertEqual(updated_allocated, 11)

    def test_talent_points_progression_by_level(self):
        """Verify 1 talent point is awarded at levels 1, 3, 8, 13, 18, 23, 28, 33."""
        expected_points_by_level = {
            1: 1,
            2: 1,
            3: 2,   # +1 at lvl 3
            4: 2,
            7: 2,
            8: 3,   # +1 at lvl 8
            12: 3,
            13: 4,  # +1 at lvl 13
            17: 4,
            18: 5,  # +1 at lvl 18
            22: 5,
            23: 6,  # +1 at lvl 23
            27: 6,
            28: 7,  # +1 at lvl 28
            32: 7,
            33: 8,  # +1 at lvl 33
            35: 8,
        }
        for lvl, expected_pts in expected_points_by_level.items():
            pts = get_talent_points_for_level(lvl)
            self.assertEqual(
                pts, expected_pts,
                f"Level {lvl} should award {expected_pts} talent points, got {pts}"
            )

    def test_characters_can_have_more_than_one_talent(self):
        """Verify that characters acquire multiple distinct talents as their level increases."""
        archetypes = [
            Archetype.TANK,
            Archetype.FIGHTER,
            Archetype.RANGER,
            Archetype.ROGUE,
            Archetype.MAGE,
            Archetype.BATTLEMAGE,
            Archetype.CLERIC,
            Archetype.SUMMONER,
        ]
        # At level 1: 1 talent
        for arch in archetypes:
            lvl1_talents = calculate_talents(arch, level=1)
            self.assertEqual(len(lvl1_talents), 1)

        # At level 4 (past level 3 milestone): 2 distinct talents
        for arch in archetypes:
            lvl4_talents = calculate_talents(arch, level=4)
            self.assertEqual(
                len(lvl4_talents), 2,
                f"Archetype {arch} at level 4 should have 2 talents, got {lvl4_talents}"
            )
            self.assertEqual(len(set(lvl4_talents)), 2, "Talents must be unique")

        # At level 8: 3 distinct talents
        for arch in archetypes:
            lvl8_talents = calculate_talents(arch, level=8)
            self.assertEqual(
                len(lvl8_talents), 3,
                f"Archetype {arch} at level 8 should have 3 talents, got {lvl8_talents}"
            )
            self.assertEqual(len(set(lvl8_talents)), 3, "Talents must be unique")

        # At level 18: 5 distinct talents
        for arch in archetypes:
            lvl18_talents = calculate_talents(arch, level=18)
            self.assertEqual(
                len(lvl18_talents), 5,
                f"Archetype {arch} at level 18 should have 5 talents, got {lvl18_talents}"
            )
            self.assertEqual(len(set(lvl18_talents)), 5, "Talents must be unique")

    def test_all_undead_races_receive_undead_talent(self):
        """Verify that all Undead races (Generic, Human, Elf, Dwarf, Lizard) receive the Undead talent."""
        all_undead_races = [
            Race.UNDEAD,
            Race.UNDEAD_HUMAN,
            Race.UNDEAD_ELF,
            Race.UNDEAD_DWARF,
            Race.UNDEAD_LIZARD,
        ]
        for r in all_undead_races:
            stats = calculate_enemy_stats(level=4, archetype=Archetype.FIGHTER, race=r)
            self.assertIn(
                "Undead", stats.talents,
                f"Race {r} must have the 'Undead' talent in talents, got {stats.talents}"
            )

        # Undead Dwarf has both Undead AND Sturdy
        undead_dwarf_stats = calculate_enemy_stats(level=4, archetype=Archetype.TANK, race=Race.UNDEAD_DWARF)
        self.assertIn("Undead", undead_dwarf_stats.talents)
        self.assertIn("Sturdy (+10% HP)", undead_dwarf_stats.talents)

        # Undead Human has both Undead AND Ingenious
        undead_human_stats = calculate_enemy_stats(level=4, archetype=Archetype.MAGE, race=Race.UNDEAD_HUMAN)
        self.assertIn("Undead", undead_human_stats.talents)
        self.assertIn("Ingenious (+Crit/+Init)", undead_human_stats.talents)

        # In full encounter generation, Undead enemies have the Undead talent
        party = PartyConfig(level=4, party_size=4)
        enc = generate_encounter(party, encounter_type=EncounterType.STANDARD, faction=Faction.UNDEAD, seed=33)
        for npc in enc.enemies:
            if "undead" in npc.race.value.lower():
                self.assertIn(
                    "Undead", npc.stats.talents,
                    f"{npc.name} ({npc.race}) in Undead encounter must have 'Undead' talent, got {npc.stats.talents}"
                )

    def test_boss_minion_count_scaling_range(self):
        """Verify GM ability to set minion count from 0 to 5, with appropriate enemy count and stat balancing."""
        party = PartyConfig(level=5, party_size=4, difficulty=Difficulty.BALANCED)
        
        boss_ehps = []
        for minion_count in range(6):  # 0 to 5
            enc = generate_encounter(
                party,
                encounter_type=EncounterType.BOSS,
                minion_count=minion_count,
                seed=42
            )
            self.assertEqual(enc.encounter_type, EncounterType.BOSS)
            self.assertEqual(len(enc.enemies), minion_count + 1)
            self.assertEqual(enc.minion_count, minion_count)
            boss = enc.enemies[0]
            self.assertEqual(boss.archetype, Archetype.BOSS)
            boss_ehps.append(boss.total_ehp)

        # 0 minions boss (solo overlord) must have significantly higher EHP than 3 minions boss
        self.assertGreater(boss_ehps[0], boss_ehps[3])
        # 3 minions boss must have higher EHP than 5 minions boss (which scales down for AP swarm balance)
        self.assertGreater(boss_ehps[3], boss_ehps[5])

    def test_solo_boss_overlord_buffs(self):
        """Verify that 0 minions results in a Solo Boss with GM-compliant AP (6/4) and alternative balancing."""
        party = PartyConfig(level=4, party_size=4)
        enc = generate_encounter(party, encounter_type=EncounterType.BOSS, minion_count=0, seed=10)
        
        self.assertEqual(len(enc.enemies), 1)
        boss = enc.enemies[0]
        self.assertEqual(boss.title, "Solo Boss / Overlord")
        # Enforces GM Mode AP caps (6 Start / 4 Recovery AP)
        self.assertEqual(boss.stats.ap_start, 6)
        self.assertEqual(boss.stats.ap_recovery, 4)
        # Alternative balance levers: Talents, Retribution, Attribute scaling
        self.assertIn("Comeback Kid", boss.stats.talents)
        self.assertIn("What a Rush", boss.stats.talents)
        self.assertGreaterEqual(boss.stats.combat_abilities.get("Retribution", 0), 3)
        self.assertTrue(any("Solo Boss Combat" in rec for rec in enc.analysis.tactical_recommendations))
        self.assertIn("Solo Boss Tuning", enc.analysis.tuning_dials)

    def test_troll_boss_selection_and_troll_blood(self):
        """Verify GM can specifically select authentic GM Mode Trolls (Mountain & Forest Trolls) with Troll Blood."""
        from balancer_core.bestiary import find_template_by_name
        
        # Verify River and Cave trolls are not present in GM Mode bestiary
        self.assertIsNone(find_template_by_name("River Troll"))
        self.assertIsNone(find_template_by_name("Cave Troll"))
        self.assertIsNotNone(find_template_by_name("Mountain Troll"))
        self.assertIsNotNone(find_template_by_name("Forest Troll"))

        party = PartyConfig(level=4, party_size=4)
        
        # Test Mountain Troll Brute
        enc_mountain = generate_encounter(
            party,
            encounter_type=EncounterType.BOSS,
            boss_template="Mountain Troll",
            minion_count=2,
            seed=20
        )
        boss_mountain = enc_mountain.enemies[0]
        self.assertEqual(boss_mountain.name, "Mountain Troll Brute")
        self.assertEqual(boss_mountain.gm_template_id, "Troll_Mountain_A")
        self.assertEqual(boss_mountain.archetype, Archetype.BOSS)
        skill_names = [s.name for s in boss_mountain.skills]
        self.assertIn("Troll Blood (Fire Weakness)", skill_names)
        self.assertIn("Battle Stomp", skill_names)

        # Test Forest Troll Wanderer
        enc_forest = generate_encounter(
            party,
            encounter_type=EncounterType.BOSS,
            boss_template="Forest Troll",
            minion_count=0,
            seed=21
        )
        boss_forest = enc_forest.enemies[0]
        self.assertEqual(boss_forest.name, "Forest Troll Wanderer")
        self.assertEqual(boss_forest.gm_template_id, "Troll_Forest_A")
        self.assertEqual(boss_forest.archetype, Archetype.BOSS)
        forest_skills = [s.name for s in boss_forest.skills]
        self.assertIn("Troll Blood", forest_skills)
        self.assertIn("Overpower", forest_skills)

    def test_forcefully_create_custom_boss(self):
        """Verify GM can forcefully create an arbitrary narrative boss not currently in the bestiary."""
        party = PartyConfig(level=6, party_size=4)
        enc = generate_encounter(
            party,
            boss_template="Ancient Corrupted Cave Troll",
            minion_count=3,
            seed=77
        )
        self.assertEqual(enc.encounter_type, EncounterType.BOSS)
        self.assertEqual(len(enc.enemies), 4)
        boss = enc.enemies[0]
        self.assertEqual(boss.name, "Ancient Corrupted Cave Troll")
        self.assertEqual(boss.archetype, Archetype.BOSS)
        self.assertEqual(boss.level, 7)  # Party level + 1

    def test_forcefully_promote_regular_npc_to_boss(self):
        """Verify selecting a non-boss NPC template forcefully elevates it to Archetype.BOSS with boss stats."""
        party = PartyConfig(level=4, party_size=4)
        # Pack Wolf is ordinarily a MINION in the bestiary
        enc = generate_encounter(
            party,
            boss_template="Pack Wolf",
            minion_count=1,
            seed=88
        )
        self.assertEqual(enc.encounter_type, EncounterType.BOSS)
        boss = enc.enemies[0]
        self.assertEqual(boss.name, "Pack Wolf")
        self.assertEqual(boss.archetype, Archetype.BOSS)
        self.assertEqual(boss.title, "Boss / Commander")
        self.assertEqual(boss.stats.ap_start, 6)
        self.assertEqual(boss.stats.ap_recovery, 4)

    def test_minion_count_bounds_validation(self):
        """Verify that minion count outside [0, 5] raises a ValueError."""
        party = PartyConfig(level=4, party_size=4)
        with self.assertRaises(ValueError):
            generate_encounter(party, encounter_type=EncounterType.BOSS, minion_count=-1)
        with self.assertRaises(ValueError):
            generate_encounter(party, encounter_type=EncounterType.BOSS, minion_count=6)

    def test_cli_boss_and_minions_flags(self):
        """Verify CLI execution with --boss and --minions flags."""
        script_path = os.path.abspath("dos2_encounter_balancer.py")
        
        # 1. Solo Troll boss CLI test
        cmd_solo = [
            sys.executable,
            script_path,
            "--level", "4",
            "--boss", "Mountain Troll",
            "--minions", "0",
        ]
        res_solo = subprocess.run(cmd_solo, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(res_solo.returncode, 0, f"CLI solo boss failed: {res_solo.stderr}")
        self.assertIn("Mountain Troll Brute", res_solo.stdout)
        self.assertIn("Solo Boss", res_solo.stdout)
        self.assertIn("ENEMY ROSTER (1 Combatants):", res_solo.stdout)

        # 2. Troll boss with 5 minions CLI test
        cmd_swarm = [
            sys.executable,
            script_path,
            "--level", "5",
            "--boss", "Forest Troll",
            "--minions", "5",
        ]
        res_swarm = subprocess.run(cmd_swarm, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(res_swarm.returncode, 0, f"CLI swarm boss failed: {res_swarm.stderr}")
        self.assertIn("Forest Troll Wanderer", res_swarm.stdout)
        self.assertIn("ENEMY ROSTER (6 Combatants):", res_swarm.stdout)

    def test_boss_perseverance_and_leadership_scaling(self):
        """Verify Boss Combat Abilities (Perseverance 3-5 anti-chain-CC and Leadership 2-4 minion aura)."""
        party = PartyConfig(level=4, party_size=4)
        
        # 1. Solo Boss (0 minions): Perseverance 5, Leadership 0
        enc_solo = generate_encounter(party, encounter_type=EncounterType.BOSS, minion_count=0, seed=42)
        boss_solo = enc_solo.enemies[0]
        self.assertEqual(boss_solo.stats.combat_abilities.get("Perseverance"), 5)
        self.assertEqual(boss_solo.stats.combat_abilities.get("Leadership", 0), 0)
        
        # 2. Boss + 1 Lieutenant: Perseverance 4, Leadership 2
        enc_1m = generate_encounter(party, encounter_type=EncounterType.BOSS, minion_count=1, seed=42)
        boss_1m = enc_1m.enemies[0]
        self.assertEqual(boss_1m.stats.combat_abilities.get("Perseverance"), 4)
        self.assertEqual(boss_1m.stats.combat_abilities.get("Leadership"), 2)

        # 3. Boss + 3 Minions (Standard): Perseverance 4, Leadership 3
        enc_3m = generate_encounter(party, encounter_type=EncounterType.BOSS, minion_count=3, seed=42)
        boss_3m = enc_3m.enemies[0]
        self.assertEqual(boss_3m.stats.combat_abilities.get("Perseverance"), 4)
        self.assertEqual(boss_3m.stats.combat_abilities.get("Leadership"), 3)

        # 4. Boss + 5 Minions (Horde): Perseverance 3, Leadership 4
        enc_5m = generate_encounter(party, encounter_type=EncounterType.BOSS, minion_count=5, seed=42)
        boss_5m = enc_5m.enemies[0]
        self.assertEqual(boss_5m.stats.combat_abilities.get("Perseverance"), 3)
        self.assertEqual(boss_5m.stats.combat_abilities.get("Leadership"), 4)

        # Check tactical recommendations mention perseverance and leadership
        recs = enc_3m.analysis.tactical_recommendations
        self.assertTrue(any("Perseverance" in r for r in recs), "Tactical notes must mention Boss Perseverance")
        self.assertTrue(any("Leadership" in r for r in recs), "Tactical notes must mention Leadership Aura")

    def test_boss_walk_it_off_talent(self):
        """Verify Bosses gain 'Walk It Off' talent to reduce status & CC durations by 1 round."""
        party = PartyConfig(level=4, party_size=4)
        enc = generate_encounter(party, encounter_type=EncounterType.BOSS, minion_count=2, seed=10)
        boss = enc.enemies[0]
        self.assertIn("Walk It Off", boss.stats.talents)

        # Solo boss should also have Comeback Kid and What a Rush
        enc_solo = generate_encounter(party, encounter_type=EncounterType.BOSS, minion_count=0, seed=10)
        boss_solo = enc_solo.enemies[0]
        self.assertIn("Walk It Off", boss_solo.stats.talents)
        self.assertIn("Comeback Kid", boss_solo.stats.talents)
        self.assertIn("What a Rush", boss_solo.stats.talents)

    def test_asymmetric_defense_profiles_and_budget_conservation(self):
        """Verify Asymmetric Armor & Elemental Weakness Profiles with exact armor budget conservation."""
        party = PartyConfig(level=4, party_size=4)

        # 1. Ironclad profile (high phys armor, low magic armor, Air weakness)
        enc_iron = generate_encounter(party, encounter_type=EncounterType.BOSS, minion_count=2, defense_profile="ironclad", seed=99)
        boss_iron = enc_iron.enemies[0]
        self.assertGreater(boss_iron.stats.physical_armor, boss_iron.stats.magic_armor)
        self.assertEqual(boss_iron.stats.resistances.get("Air"), -25)
        self.assertIn("Ironclad", boss_iron.defense_theme)

        # 2. Arcane profile (high magic armor, low phys armor, Physical weakness)
        enc_arc = generate_encounter(party, encounter_type=EncounterType.BOSS, minion_count=2, defense_profile="arcane", seed=99)
        boss_arc = enc_arc.enemies[0]
        self.assertGreater(boss_arc.stats.magic_armor, boss_iron.stats.magic_armor)
        self.assertGreater(boss_arc.stats.magic_armor, boss_arc.stats.physical_armor)
        self.assertEqual(boss_arc.stats.resistances.get("Physical"), -20)
        self.assertIn("Arcane", boss_arc.defense_theme)

        # 3. Exact Armor Budget Conservation:
        # Compare Balanced vs Ironclad vs Arcane on the same seed and boss template
        enc_bal = generate_encounter(party, encounter_type=EncounterType.BOSS, minion_count=2, defense_profile="balanced", seed=99)
        total_bal = enc_bal.enemies[0].stats.physical_armor + enc_bal.enemies[0].stats.magic_armor
        total_iron = boss_iron.stats.physical_armor + boss_iron.stats.magic_armor
        total_arc = boss_arc.stats.physical_armor + boss_arc.stats.magic_armor
        self.assertEqual(total_bal, total_iron, "Ironclad defense must conserve exact total armor budget")
        self.assertEqual(total_bal, total_arc, "Arcane defense must conserve exact total armor budget")

        # 4. Thematic Auto-Detection for Trolls
        enc_troll = generate_encounter(party, encounter_type=EncounterType.BOSS, boss_template="Mountain Troll", minion_count=2, seed=99)
        boss_troll = enc_troll.enemies[0]
        self.assertIn("Troll Hide", boss_troll.defense_theme)
        self.assertEqual(boss_troll.stats.resistances.get("Fire"), -30)
        self.assertEqual(boss_troll.stats.resistances.get("Earth"), 40)

    def test_cli_defense_flag(self):
        """Verify CLI execution with --defense / --defense-profile flag."""
        script_path = os.path.abspath("dos2_encounter_balancer.py")
        cmd = [
            sys.executable,
            script_path,
            "--level", "4",
            "--boss", "Mountain Troll",
            "--minions", "1",
            "--defense", "ironclad",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(res.returncode, 0, f"CLI with --defense ironclad failed: {res.stderr}")
        self.assertIn("Ironclad Juggernaut", res.stdout)
        self.assertIn("Air -25%", res.stdout)
        self.assertIn("Perseverance", res.stdout)
        self.assertIn("Walk It Off", res.stdout)
        self.assertIn("Leadership", res.stdout)

    def test_interactive_mode_skips_faction_and_race_for_solo_boss(self):
        """Verify interactive wizard skips Faction and Race prompts when a Solo Boss (0 minions) with designated Boss NPC is chosen."""
        script_path = os.path.abspath("dos2_encounter_balancer.py")
        # Input sequence:
        # 1. Level [4]: \n
        # 2. Party size [4]: \n
        # 3. Damage comp [1]: \n
        # 4. Difficulty [1]: \n
        # 5. Encounter type: 3 (Boss Encounter)
        # 6. Minions: 0 (Solo Boss duel)
        # 7. Select Boss NPC: 2 (Iconic Bestiary Bosses)
        # 8. Choose Boss from Bestiary: 1 (Mountain Troll Brute)
        # 9. Defensive profile: \n (Auto-detect)
        # 10. GM Action: 4 (Exit)
        inputs = "\n\n\n\n3\n0\n2\n1\n\n4\n"
        res = subprocess.run(
            [sys.executable, script_path, "-i"],
            input=inputs,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        self.assertEqual(res.returncode, 0, f"Interactive mode failed: {res.stderr}")
        self.assertIn("Solo Boss duel configured for 'Bandit Kingpin'", res.stdout)
        self.assertIn("Skipping Faction & Race selection", res.stdout)
        self.assertNotIn("Select Thematic Enemy Faction", res.stdout)
        self.assertNotIn("Restrict Encounter to a Single Enemy Race?", res.stdout)

    def test_terminal_card_no_truncation(self):
        """Verify that terminal cards do not truncate talents (e.g. 'What a Rush') or break 72-char borders."""
        party = PartyConfig(level=4, party_size=4)
        enc = generate_encounter(
            party,
            encounter_type=EncounterType.BOSS,
            boss_template="Mountain Troll",
            minion_count=0,
            defense_profile="ironclad",
            seed=42
        )
        boss = enc.enemies[0]
        card = format_enemy_terminal_card(boss, 1)

        # 1. Full talent names must be present, never cut off
        self.assertIn("What a Rush", card)
        self.assertIn("Comeback Kid", card)
        self.assertIn("Walk It Off", card)

        # 2. Every single line in the card must have exact width of 72 characters
        for idx, line in enumerate(card.splitlines(), 1):
            self.assertEqual(
                len(line),
                72,
                f"Line {idx} does not have width 72 (got {len(line)}): '{line}'"
            )

    def test_lizard_rogue_boss_stats_and_skills(self):
        """Verify that a Lizard Rogue elevated to Boss retains Finesse, Scoundrel skills, and Lizard traits."""
        party = PartyConfig(level=5, party_size=4)
        enc = generate_encounter(
            party,
            encounter_type=EncounterType.BOSS,
            boss_template="Lizard Shadowblade Assassin",
            minion_count=2,
            seed=42
        )
        boss = enc.enemies[0]

        # 1. Identity & Race
        self.assertEqual(boss.race, Race.LIZARD)
        self.assertEqual(boss.archetype, Archetype.BOSS)

        # 2. Primary attribute must be Finesse for daggers (+55% points allocated)
        self.assertGreater(boss.stats.finesse, boss.stats.strength)
        self.assertGreater(boss.stats.finesse, boss.stats.intelligence)

        # 3. Combat abilities must feature Scoundrel and Dual Wielding
        self.assertIn("Scoundrel", boss.stats.combat_abilities)
        self.assertGreaterEqual(boss.stats.combat_abilities["Scoundrel"], 4)
        self.assertIn("Dual Wielding", boss.stats.combat_abilities)

        # 4. Skills must include signature Scoundrel and Lizard racial skills
        skill_names = [s.name for s in boss.skills]
        self.assertIn("Dragon's Blaze", skill_names)
        self.assertIn("Backlash", skill_names)
        self.assertIn("Cloak and Dagger", skill_names)
        self.assertIn("Rupture Tendons", skill_names)

        # 5. Talents must include Lizard racial and Boss survival
        self.assertIn("Sophisticated (+Resist)", boss.stats.talents)
        self.assertIn("Walk It Off", boss.stats.talents)

        # 6. GM AP limits enforced
        self.assertLessEqual(boss.stats.ap_start, 6)
        self.assertLessEqual(boss.stats.ap_recovery, 4)

    def test_custom_lizard_rogue_boss_by_string(self):
        """Verify custom boss creation automatically detects Lizard Rogue from keywords."""
        party = PartyConfig(level=4, party_size=4)
        enc = generate_encounter(
            party,
            encounter_type=EncounterType.BOSS,
            boss_template="Viper King Lizard Assassin",
            minion_count=0,
            seed=42
        )
        boss = enc.enemies[0]

        self.assertEqual(boss.race, Race.LIZARD)
        self.assertGreater(boss.stats.finesse, boss.stats.strength)
        self.assertIn("Scoundrel", boss.stats.combat_abilities)
        skill_names = [s.name for s in boss.skills]
        self.assertIn("Dragon's Blaze", skill_names)
        self.assertTrue(any("Backlash" in s or "Cloak" in s for s in skill_names))
        self.assertIn("Walk It Off", boss.stats.talents)
        self.assertIn("Comeback Kid", boss.stats.talents)  # Solo boss talent


if __name__ == "__main__":
    unittest.main()


