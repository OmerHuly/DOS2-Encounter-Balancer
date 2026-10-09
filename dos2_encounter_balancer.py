#!/usr/bin/env python3
"""
Divinity: Original Sin 2 - Definitive Edition (GM Mode)
Tactical Encounter Balancer & Generator

A specialized assistant for Game Masters to craft perfectly balanced, rewarding,
and tactically engaging encounters based on player party power and GM bestiary assets.

Usage:
    python dos2_encounter_balancer.py                  # Launches interactive mode
    python dos2_encounter_balancer.py --interactive    # Launches interactive mode
    python dos2_encounter_balancer.py --level 4 --party-size 4 --type boss --export
"""

import sys
import os
import argparse
from typing import Optional

# Ensure safe UTF-8 terminal output on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Support importing balancer_core whether run from root or package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from balancer_core import (
    PartyConfig,
    Encounter,
    EncounterType,
    Faction,
    Race,
    DamageProfile,
    Difficulty,
    generate_encounter,
    format_encounter_terminal,
    export_encounter_to_markdown,
    get_all_boss_templates,
    search_templates,
    find_template_by_name,
)


def print_banner():
    banner = r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     DIVINITY: ORIGINAL SIN 2 DEFINITIVE EDITION - GM ENCOUNTER BALANCER      ║
║          Precision Tactical Math • Faction Bestiary • Action Economy         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def prompt_int(prompt_text: str, default: int, min_val: int = 1, max_val: int = 30) -> int:
    while True:
        try:
            raw = input(f"{prompt_text} [{default}]: ").strip()
            if not raw:
                return default
            val = int(raw)
            if min_val <= val <= max_val:
                return val
            print(f"  [!] Please enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("  [!] Please enter a valid integer.")


def prompt_choice(prompt_text: str, options: list, default_index: int = 0):
    print(f"\n{prompt_text}:")
    for idx, opt in enumerate(options, 1):
        marker = " (Default)" if idx - 1 == default_index else ""
        label = opt.value if hasattr(opt, "value") else str(opt)
        print(f"  [{idx}] {label}{marker}")
    while True:
        raw = input(f"Select option [1-{len(options)}] (Enter for default {default_index + 1}): ").strip()
        if not raw:
            return options[default_index]
        try:
            val = int(raw)
            if 1 <= val <= len(options):
                return options[val - 1]
            print(f"  [!] Invalid choice. Enter a number between 1 and {len(options)}.")
        except ValueError:
            print("  [!] Please enter a valid number.")


def prompt_yes_no(prompt_text: str, default: bool = False) -> bool:
    def_str = "Y/n" if default else "y/N"
    while True:
        raw = input(f"{prompt_text} [{def_str}]: ").strip().lower()
        if not raw:
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("  [!] Please enter 'y' or 'n'.")


def interactive_mode():
    print_banner()
    print("Welcome GM! Let's dial in your party's combat profile to generate a tailored encounter.\n")

    # 1. Party setup
    level = prompt_int("► What level is the player party?", default=4, min_val=1, max_val=25)
    party_size = prompt_int("► How many players are in the party?", default=4, min_val=1, max_val=4)
    is_lone_wolf = False
    if party_size in (1, 2):
        is_lone_wolf = prompt_yes_no("► Are the players using the Lone Wolf talent?", default=False)

    # 2. Damage profile
    damage_options = [
        DamageProfile.BALANCED,
        DamageProfile.PURE_PHYSICAL,
        DamageProfile.PURE_MAGICAL,
        DamageProfile.PHYSICAL_LEAN,
        DamageProfile.MAGICAL_LEAN,
    ]
    damage_profile = prompt_choice("► What is the party's damage composition?", damage_options, default_index=0)

    # 3. Target difficulty
    diff_options = [
        Difficulty.BALANCED,
        Difficulty.TACTICIAN,
        Difficulty.STORY,
        Difficulty.DEADLY,
    ]
    difficulty = prompt_choice("► Desired encounter difficulty tier?", diff_options, default_index=0)

    # 4. Encounter type
    enc_options = [
        ("Random / GM Choice", None),
        (EncounterType.STANDARD.value, EncounterType.STANDARD),
        (EncounterType.BOSS.value, EncounterType.BOSS),
        (EncounterType.SWARM.value, EncounterType.SWARM),
        (EncounterType.ELITE.value, EncounterType.ELITE),
    ]
    enc_type_choice = prompt_choice(
        "► Select Encounter Type",
        [opt[0] for opt in enc_options],
        default_index=0
    )
    selected_enc_type = next(item[1] for item in enc_options if item[0] == enc_type_choice)

    # 4b. Boss Encounter Specific Tuning
    selected_minion_count = None
    selected_boss_template = None
    selected_defense_profile = "auto"
    if selected_enc_type == EncounterType.BOSS:
        print("\n" + "─" * 60)
        print("  👑 BOSS ENCOUNTER CONFIGURATION")
        print("─" * 60)
        print("Specify the number of minions accompanying the boss (0 to 5):")
        print("  • 0 Minions: Epic Solo Boss duel (boss receives Solo Overlord HP/armor/AP scaling)")
        print("  • 1-2 Minions: Small squad (Boss + Lieutenant / Guard)")
        print("  • 3 Minions: Standard balanced boss squad")
        print("  • 4-5 Minions: Boss with minion swarm (boss & minions scaled down for AP balance)")
        default_minions = 2 if is_lone_wolf else 3
        selected_minion_count = prompt_int(
            "► How many minions should accompany the boss? [0-5]",
            default=default_minions,
            min_val=0,
            max_val=5
        )

        boss_selection_modes = [
            "Random / Thematic Boss for Selected Faction (Default)",
            "Select from Iconic Bestiary Bosses (Trolls, Titans, Overlords, etc.)",
            "Search Bestiary by keyword (e.g. 'Troll', 'Spider', 'Magister')",
            "Forcefully designate / create a custom Boss (e.g. 'Cave Troll Chieftain')",
        ]
        b_choice = prompt_choice("► Select Boss NPC", boss_selection_modes, default_index=0)
        
        if b_choice == boss_selection_modes[1]:
            boss_list = get_all_boss_templates()
            boss_options = [f"{b.name} ({b.faction.value} | {b.race.value})" for b in boss_list]
            selected_boss_opt = prompt_choice("► Choose Boss from Bestiary", boss_options, default_index=0)
            selected_boss_template = boss_list[boss_options.index(selected_boss_opt)]
        elif b_choice == boss_selection_modes[2]:
            keyword = input("► Enter search term for Boss (e.g. 'troll'): ").strip()
            matches = search_templates(keyword)
            if matches:
                match_options = [f"{m.name} ({m.faction.value} | {m.race.value})" for m in matches]
                chosen_match = prompt_choice(f"► Found {len(matches)} matching NPCs. Select one as Boss", match_options, default_index=0)
                selected_boss_template = matches[match_options.index(chosen_match)]
            else:
                print(f"  [!] No existing templates matched '{keyword}'. Will forcefully create custom Boss '{keyword}'.")
                selected_boss_template = keyword
        elif b_choice == boss_selection_modes[3]:
            custom_name = input("► Enter custom Boss NPC name: ").strip()
            if custom_name:
                selected_boss_template = custom_name

        defense_options = [
            ("Thematic Auto-Detect (Authentic bestiary resistances & weaknesses)", "auto"),
            ("Balanced (Standard 1:1 Physical & Magic Armor, no vulnerabilities)", "balanced"),
            ("Ironclad Juggernaut (High Phys Armor / Low Magic Armor / Air Weakness)", "ironclad"),
            ("Arcane Ward / Spellweaver (High Magic Armor / Low Phys Armor / Phys Weakness)", "arcane"),
            ("Volcanic / Fire-Forged (Fire Absorption / Water & Cryo Weakness)", "pyro"),
            ("Glacial Frost-Bound (Water & Air Resistant / Fire Weakness)", "cryo"),
            ("Venomous / Undead (Poison Absorption / Fire Weakness)", "venom"),
            ("Storm Conduit (Air Immune / Earth Weakness)", "storm"),
            ("Troll Hide (Massive Phys Armor / Earth Res / Fire Weakness suppresses regen)", "troll"),
        ]
        def_choice = prompt_choice("► Defensive & Elemental Weakness Profile", [opt[0] for opt in defense_options], default_index=0)
        selected_defense_profile = next(item[1] for item in defense_options if item[0] == def_choice)

    # Check if Faction and Race selection can be skipped:
    # If the GM selected a Boss Encounter with 0 minions (Solo Boss duel) and specified a Boss NPC,
    # the entire encounter is determined by that Boss NPC alone (Faction and Race are inherent).
    skip_faction_race = (
        selected_enc_type == EncounterType.BOSS
        and selected_minion_count == 0
        and selected_boss_template is not None
    )

    if skip_faction_race:
        boss_tpl = None
        if hasattr(selected_boss_template, "faction"):
            boss_tpl = selected_boss_template
        else:
            boss_tpl = find_template_by_name(str(selected_boss_template))

        if boss_tpl:
            selected_faction = boss_tpl.faction
            selected_race = boss_tpl.race
            boss_name = boss_tpl.name
        else:
            selected_faction = Faction.ANY
            selected_race = None
            boss_name = str(selected_boss_template)

        faction_desc = selected_faction.value if selected_faction != Faction.ANY else "Thematic"
        race_desc = selected_race.value if selected_race else "Default"
        print(f"\n[✓] Solo Boss duel configured for '{boss_name}' ({faction_desc} | {race_desc}).")
        print("    Skipping Faction & Race selection (encounter consists solely of the designated Boss NPC).")
    else:
        # Resolve boss template if one was chosen for minion faction defaulting
        boss_tpl = None
        if selected_boss_template is not None:
            if hasattr(selected_boss_template, "faction"):
                boss_tpl = selected_boss_template
            else:
                boss_tpl = find_template_by_name(str(selected_boss_template))

        # 5. Faction / Theme
        prompt_faction_title = "► Select Thematic Enemy Faction"
        if selected_enc_type == EncounterType.BOSS and selected_minion_count and selected_minion_count > 0:
            prompt_faction_title = "► Select Minion Faction / Theme"

        faction_options = [
            ("Random / Mixed Factions", Faction.ANY),
            (Faction.MAGISTERS.value, Faction.MAGISTERS),
            (Faction.VOIDWOKEN.value, Faction.VOIDWOKEN),
            (Faction.UNDEAD.value, Faction.UNDEAD),
            (Faction.BANDITS.value, Faction.BANDITS),
            (Faction.BEASTS.value, Faction.BEASTS),
            (Faction.DEMONS.value, Faction.DEMONS),
            (Faction.AUTOMATONS.value, Faction.AUTOMATONS),
        ]

        default_fac_idx = 0
        if boss_tpl and boss_tpl.faction != Faction.ANY:
            for idx, opt in enumerate(faction_options):
                if opt[1] == boss_tpl.faction:
                    default_fac_idx = idx
                    break

        faction_choice = prompt_choice(
            prompt_faction_title,
            [opt[0] for opt in faction_options],
            default_index=default_fac_idx
        )
        selected_faction = next(item[1] for item in faction_options if item[0] == faction_choice)

        # 6. Single Race Filter (Optional)
        prompt_race_title = "► Restrict Encounter to a Single Enemy Race?"
        if selected_enc_type == EncounterType.BOSS and selected_minion_count and selected_minion_count > 0:
            prompt_race_title = "► Restrict Minions to a Single Enemy Race?"

        race_options = [
            ("Any / Multi-racial (Default)", None),
            ("Human Only", Race.HUMAN),
            ("Elf Only", Race.ELF),
            ("Dwarf Only", Race.DWARF),
            ("Lizard Only", Race.LIZARD),
            ("Undead (All Undead Variants)", Race.UNDEAD),
            ("Undead Dwarf Only", Race.UNDEAD_DWARF),
            ("Undead Elf Only", Race.UNDEAD_ELF),
            ("Undead Lizard Only", Race.UNDEAD_LIZARD),
            ("Undead Human Only", Race.UNDEAD_HUMAN),
        ]
        race_choice = prompt_choice(
            prompt_race_title,
            [opt[0] for opt in race_options],
            default_index=0
        )
        selected_race = next(item[1] for item in race_options if item[0] == race_choice)

    party_cfg = PartyConfig(
        level=level,
        party_size=party_size,
        is_lone_wolf=is_lone_wolf,
        damage_profile=damage_profile,
        difficulty=difficulty,
    )

    # Main Generation Loop
    while True:
        encounter = generate_encounter(
            party_config=party_cfg,
            encounter_type=selected_enc_type,
            faction=selected_faction,
            race=selected_race,
            boss_template=selected_boss_template,
            minion_count=selected_minion_count,
            defense_profile=selected_defense_profile,
        )

        print("\n" * 2)
        print(format_encounter_terminal(encounter))
        print("\n" + "=" * 72)
        print("  GM ACTIONS:")
        print("  [1] Re-roll / Generate another encounter (same party settings)")
        print("  [2] Export this battle sheet to Markdown (.md)")
        print("  [3] Adjust Party / Difficulty settings")
        print("  [4] Exit")
        print("=" * 72)

        action = input("Select action [1-4] (Default: 1): ").strip()
        if action == "2":
            md_path = export_encounter_to_markdown(encounter)
            print(f"\n[✓] Battle sheet successfully exported to: {os.path.abspath(md_path)}\n")
            input("Press Enter to continue...")
        elif action == "3":
            return interactive_mode()
        elif action == "4":
            print("\nGood luck with your campaign, GM! May your dice roll true.\n")
            break
        else:
            print("\nGenerating fresh encounter variant...\n")


def parse_cli_args():
    parser = argparse.ArgumentParser(
        description="Divinity: Original Sin 2 GM Mode Encounter Balancer & Generator"
    )
    parser.add_argument("-i", "--interactive", action="store_true", help="Launch interactive wizard")
    parser.add_argument("--level", type=int, default=4, help="Party level (1-25)")
    parser.add_argument("--party-size", type=int, default=4, help="Number of party members (1-4)")
    parser.add_argument("--lone-wolf", action="store_true", help="Enable Lone Wolf talent modifiers")
    parser.add_argument(
        "--damage-profile",
        choices=["split", "pure-phys", "pure-mag", "phys-lean", "mag-lean"],
        default="split",
        help="Party damage composition"
    )
    parser.add_argument(
        "--difficulty",
        choices=["story", "classic", "tactician", "deadly"],
        default="classic",
        help="Target challenge level"
    )
    parser.add_argument(
        "--type",
        choices=["standard", "boss", "swarm", "elite", "random"],
        default="random",
        help="Encounter tactical type"
    )
    parser.add_argument(
        "--faction",
        choices=["magisters", "voidwoken", "undead", "bandits", "beasts", "demons", "automatons", "any"],
        default="any",
        help="Thematic NPC faction"
    )
    parser.add_argument(
        "--race",
        choices=[
            "any",
            "human",
            "elf",
            "dwarf",
            "lizard",
            "undead",
            "undead-dwarf",
            "undead-elf",
            "undead-lizard",
            "undead-human",
        ],
        default="any",
        help="Restrict encounter enemies to a single race"
    )
    parser.add_argument(
        "--boss",
        type=str,
        default=None,
        help="Specifically select or forcefully create the Boss NPC (e.g. 'Mountain Troll', 'Troll', 'Bandit Kingpin')"
    )
    parser.add_argument(
        "--minions",
        "--minion-count",
        dest="minions",
        type=int,
        default=None,
        choices=range(0, 6),
        help="Number of minions accompanying the boss (0-5). Automatically balances boss & minion durability."
    )
    parser.add_argument(
        "--defense",
        "--defense-profile",
        dest="defense_profile",
        choices=["auto", "balanced", "ironclad", "arcane", "pyro", "cryo", "venom", "storm", "troll"],
        default="auto",
        help="Defensive resistance profile and armor skew for Boss/Elite units (default: auto)"
    )
    parser.add_argument("--export", action="store_true", help="Export encounter to Markdown file")
    parser.add_argument("--output-dir", type=str, default=".", help="Directory to save exported Markdown")

    return parser.parse_args()


def main():
    # If no flags passed, default directly to interactive wizard
    if len(sys.argv) == 1:
        interactive_mode()
        return

    args = parse_cli_args()

    if args.interactive:
        interactive_mode()
        return

    # Map CLI choices to Enums
    damage_map = {
        "split": DamageProfile.BALANCED,
        "pure-phys": DamageProfile.PURE_PHYSICAL,
        "pure-mag": DamageProfile.PURE_MAGICAL,
        "phys-lean": DamageProfile.PHYSICAL_LEAN,
        "mag-lean": DamageProfile.MAGICAL_LEAN,
    }
    diff_map = {
        "story": Difficulty.STORY,
        "classic": Difficulty.BALANCED,
        "tactician": Difficulty.TACTICIAN,
        "deadly": Difficulty.DEADLY,
    }
    type_map = {
        "standard": EncounterType.STANDARD,
        "boss": EncounterType.BOSS,
        "swarm": EncounterType.SWARM,
        "elite": EncounterType.ELITE,
        "random": None,
    }
    faction_map = {
        "magisters": Faction.MAGISTERS,
        "voidwoken": Faction.VOIDWOKEN,
        "undead": Faction.UNDEAD,
        "bandits": Faction.BANDITS,
        "beasts": Faction.BEASTS,
        "demons": Faction.DEMONS,
        "automatons": Faction.AUTOMATONS,
        "any": Faction.ANY,
    }
    race_map = {
        "any": None,
        "human": Race.HUMAN,
        "elf": Race.ELF,
        "dwarf": Race.DWARF,
        "lizard": Race.LIZARD,
        "undead": Race.UNDEAD,
        "undead-dwarf": Race.UNDEAD_DWARF,
        "undead-elf": Race.UNDEAD_ELF,
        "undead-lizard": Race.UNDEAD_LIZARD,
        "undead-human": Race.UNDEAD_HUMAN,
    }

    party_cfg = PartyConfig(
        level=args.level,
        party_size=args.party_size,
        is_lone_wolf=args.lone_wolf,
        damage_profile=damage_map[args.damage_profile],
        difficulty=diff_map[args.difficulty],
    )

    chosen_type = type_map[args.type]
    if (args.boss is not None or args.minions is not None) and chosen_type is None:
        chosen_type = EncounterType.BOSS

    encounter = generate_encounter(
        party_config=party_cfg,
        encounter_type=chosen_type,
        faction=faction_map[args.faction],
        race=race_map[args.race],
        boss_template=args.boss,
        minion_count=args.minions,
        defense_profile=args.defense_profile,
    )

    print(format_encounter_terminal(encounter))

    if args.export:
        os.makedirs(args.output_dir, exist_ok=True)
        md_path = export_encounter_to_markdown(encounter, output_dir=args.output_dir)
        print(f"\n[✓] Battle sheet exported to: {os.path.abspath(md_path)}\n")


if __name__ == "__main__":
    main()
