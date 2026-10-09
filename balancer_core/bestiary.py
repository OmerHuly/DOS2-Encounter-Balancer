"""
DOS2 Encounter Balancer - GM Mode Bestiary Database
Curated catalog directly cross-referenced and verified against official
Divinity: Original Sin 2 Definitive Edition game files:
- GameMaster.pak (Public/GameMaster/Stats/Generated/Data/Character.txt)
- RootTemplates (_merged.lsf in GameMaster.pak & Shared.pak)
- English.pak (Localization/English/english.xml)

Features full multi-racial NPC representations across Humans, Elves, Dwarves,
Lizards, and Undead for Bandits, Black Ring, Magisters, and all factions.
"""

from dataclasses import dataclass
from typing import List, Optional
from .models import Faction, Archetype, Race


@dataclass
class BestiaryTemplate:
    name: str
    gm_template_id: str  # Exact in-engine template ID in GM mode files
    faction: Faction
    race: Race
    archetype: Archetype
    equipment: str
    ai_tactics: str
    gm_notes: str
    can_be_boss: bool = False
    can_be_minion: bool = False
    signature_skills: Optional[List[str]] = None


BESTIARY: List[BestiaryTemplate] = [
    # =========================================================================
    # FACTION: BANDITS & OUTLAWS / BRUTES (MULTI-RACIAL GANGS)
    # Verified in english.xml: Bandit Dwarf, Bandit Elf, Bandit Lizard, Bandit Human, Undead Bandit
    # =========================================================================
    # --- Human Bandits ---
    BestiaryTemplate(
        name="Bandit Human Thug",
        gm_template_id="GM_Brute_Melee",
        faction=Faction.BANDITS,
        race=Race.HUMAN,
        archetype=Archetype.FIGHTER,
        equipment="Spiked Mace + Round Wooden Shield",
        ai_tactics="Brawls in close quarters, uses Bouncing Shield and Battering Ram on closest player. Uses Encourage.",
        gm_notes="Engine template: GM_Brute_Melee. Tough human mercenary brawler.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Bandit Human Cutthroat",
        gm_template_id="GM_BruteAssassin",
        faction=Faction.BANDITS,
        race=Race.HUMAN,
        archetype=Archetype.ROGUE,
        equipment="Pair of Serrated Daggers",
        ai_tactics="Uses Cloak and Dagger from stealth, backstabs player spellcaster, applies Rupture Tendons and Adrenaline.",
        gm_notes="Engine template: GM_BruteAssassin. High initiative backstab specialist.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Bandit Human Poacher",
        gm_template_id="GM_Brute_Ranger",
        faction=Faction.BANDITS,
        race=Race.HUMAN,
        archetype=Archetype.RANGER,
        equipment="Hunting Crossbow + Throwing Knives",
        ai_tactics="Fires Pin Down to stop player melee from approaching, then uses Sky Shot from high ground.",
        gm_notes="Engine template: GM_Brute_Ranger. Equips oil and knockdown arrows.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Bandit Human Hedge Witch",
        gm_template_id="GM_Brute_Caster_Pyro",
        faction=Faction.BANDITS,
        race=Race.HUMAN,
        archetype=Archetype.MAGE,
        equipment="Warped Willow Wand + Poison Vial",
        ai_tactics="Casts Chloroform on physical damage dealers, casts Fossil Strike to slow and ignite the battlefield.",
        gm_notes="Engine template: GM_Brute_Caster_Pyro. Chaotic spellcaster.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Bandit Kingpin",
        gm_template_id="GM_Brute_Tank",
        faction=Faction.BANDITS,
        race=Race.HUMAN,
        archetype=Archetype.BOSS,
        equipment="Two-Handed Greataxe + Spiked Shoulders",
        ai_tactics="Drinks stat potions, enrages himself for guaranteed critical hits, and cleaves through multiple party members.",
        gm_notes="Engine template: GM_Brute_Tank. Outlaw leader with Executioner talent.",
        can_be_boss=True
    ),

    # --- Dwarf Bandits ---
    BestiaryTemplate(
        name="Bandit Dwarf Defender",
        gm_template_id="Dwarves_Male_Clothing_Bandit_A",
        faction=Faction.BANDITS,
        race=Race.DWARF,
        archetype=Archetype.TANK,
        equipment="Dwarven Heavy Bulwark Shield + Stone Hammer",
        ai_tactics="High vitality and physical armor. Casts Petrifying Touch in melee and uses Shields Up when battered.",
        gm_notes="Engine template: Dwarves_Male_Clothing_Bandit_A. Dwarf racial (+10% Vitality, Petrifying Touch).",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Bandit Dwarf Brawler",
        gm_template_id="Dwarves_Male_Clothing_Bandit_A",
        faction=Faction.BANDITS,
        race=Race.DWARF,
        archetype=Archetype.FIGHTER,
        equipment="Dual Waraxes",
        ai_tactics="Charges in with Bull Horns, performs Whirlwind, and leverages high innate dodging.",
        gm_notes="Engine template: Dwarves_Male_Clothing_Bandit_A (Brawler variant). Sturdy frontline dwarf.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Bandit Dwarf Archer",
        gm_template_id="Dwarves_Male_Clothing_Bandit_A",
        faction=Faction.BANDITS,
        race=Race.DWARF,
        archetype=Archetype.RANGER,
        equipment="Recurve Shortbow + Earth Arrows",
        ai_tactics="Takes high ground, fires Pin Down and Ricochet. Tougher to kill than human archers.",
        gm_notes="Engine template: Dwarves_Male_Clothing_Bandit_A (Archer). Listed directly in english.xml.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Bandit Dwarf Elementalist",
        gm_template_id="Dwarves_Female_Mage",
        faction=Faction.BANDITS,
        race=Race.DWARF,
        archetype=Archetype.MAGE,
        equipment="Earth Runestone Staff",
        ai_tactics="Geomancy specialist: coats players in oil with Fossil Strike and petrifies with Petrifying Touch.",
        gm_notes="Engine template: Dwarves_Female_Mage / Dwarves_Male_Clothing_Bandit_A. Earth/Geo caster.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Bandit Dwarf Cutthroat",
        gm_template_id="Dwarves_Male_Clothing_Bandit_A",
        faction=Faction.BANDITS,
        race=Race.DWARF,
        archetype=Archetype.ROGUE,
        equipment="Dual Serrated Dwarven Daggers",
        ai_tactics="Flanks with The Pawn, applies Petrifying Touch to vulnerable targets, and backstabs backline casters.",
        gm_notes="Engine template: Dwarves_Male_Clothing_Bandit_A (Rogue/Assassin variant).",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Bandit Dwarven Warlord",
        gm_template_id="Dwarves_Male_Clothing_Bandit_A",
        faction=Faction.BANDITS,
        race=Race.DWARF,
        archetype=Archetype.BOSS,
        equipment="Two-Handed Dwarven Battleaxe + Spiked Armor",
        ai_tactics="Charges with Bull Horns, uses Petrifying Touch and Whirlwind. High vitality.",
        gm_notes="Engine template: Dwarves_Male_Clothing_Bandit_A (Boss).",
        can_be_boss=True
    ),

    # --- Elf Bandits ---
    BestiaryTemplate(
        name="Bandit Elf Warrior",
        gm_template_id="Elves_Female_Armor_Leather_A",
        faction=Faction.BANDITS,
        race=Race.ELF,
        archetype=Archetype.FIGHTER,
        equipment="Elven Two-Handed Curved Greatsword",
        ai_tactics="Activates Flesh Sacrifice (+1 AP, +10% dmg) on Turn 1, then charges with Battering Ram and Whirlwind.",
        gm_notes="Engine template: Elves_Female_Armor_Leather_A. High burst melee elf.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Bandit Elf Rogue",
        gm_template_id="Elves_Female_Armor_Leather_A",
        faction=Faction.BANDITS,
        race=Race.ELF,
        archetype=Archetype.ROGUE,
        equipment="Dual Needle Daggers",
        ai_tactics="Uses Flesh Sacrifice for extra AP, teleports behind casters with Backlash, applies Rupture Tendons.",
        gm_notes="Engine template: Elves_Female_Armor_Leather_A (Rogue). Lethal elven assassin.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Bandit Elf Ranger",
        gm_template_id="Elves_Female_Armor_Leather_A",
        faction=Faction.BANDITS,
        race=Race.ELF,
        archetype=Archetype.RANGER,
        equipment="Long Elven Yew Bow",
        ai_tactics="Flesh Sacrifice into Tactical Retreat to reach high ground. Rains Ballistic Shot and Marksman's Fang.",
        gm_notes="Engine template: Elves_Female_Armor_Leather_A (Ranger). Sniper with AP boost.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Bandit Elf Elementalist",
        gm_template_id="Elves_Female_Armor_Mage",
        faction=Faction.BANDITS,
        race=Race.ELF,
        archetype=Archetype.MAGE,
        equipment="Hydro Wand + Shield",
        ai_tactics="Uses Flesh Sacrifice to create blood puddle, then casts Elemental Affinity spells at reduced AP cost.",
        gm_notes="Engine template: Elves_Female_Armor_Mage. Leverages blood surface synergy.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Bandit Elven Captain",
        gm_template_id="Elves_Female_Armor_Leather_A",
        faction=Faction.BANDITS,
        race=Race.ELF,
        archetype=Archetype.BOSS,
        equipment="Masterwork Elven Longbow + Poison Quiver",
        ai_tactics="Flesh Sacrifice into Tactical Retreat, rains Arrow Storm and Ballistic Shot.",
        gm_notes="Engine template: Elves_Female_Armor_Leather_A (Boss).",
        can_be_boss=True
    ),

    # --- Lizard Bandits ---
    BestiaryTemplate(
        name="Bandit Lizard Warrior",
        gm_template_id="Lizards_Female_Armor_Leather_A",
        faction=Faction.BANDITS,
        race=Race.LIZARD,
        archetype=Archetype.FIGHTER,
        equipment="Curved Scimitar + Heavy Shield",
        ai_tactics="High Fire resistance. Breathes Dragon's Blaze on players to strip magic armor, then knocks down.",
        gm_notes="Engine template: Lizards_Female_Armor_Leather_A. Dragon's Blaze fire cone.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Bandit Lizard Rogue",
        gm_template_id="Lizards_Female_Armor_Leather_A",
        faction=Faction.BANDITS,
        race=Race.LIZARD,
        archetype=Archetype.ROGUE,
        equipment="Twin Ceremonial Daggers",
        ai_tactics="High movement speed. Ignites surroundings with Dragon's Blaze, then backstabs retreating heroes.",
        gm_notes="Engine template: Lizards_Female_Armor_Leather_A (Rogue). Fast and agile skirmisher.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Bandit Lizard Ranger",
        gm_template_id="Lizards_Female_Armor_Leather_A",
        faction=Faction.BANDITS,
        race=Race.LIZARD,
        archetype=Archetype.RANGER,
        equipment="Empire Composite Bow",
        ai_tactics="Shoots fire arrows, sets fire surfaces, breathes fire on anyone who tries to engage in melee.",
        gm_notes="Engine template: Lizards_Female_Armor_Leather_A (Ranger). Fire archer.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Bandit Lizard Elementalist",
        gm_template_id="Lizards_Female_Armor_Mage",
        faction=Faction.BANDITS,
        race=Race.LIZARD,
        archetype=Archetype.MAGE,
        equipment="Incinerator Wand + Pyromancy Orb",
        ai_tactics="Pyrokinetic expert: casts Fireball, Searing Daggers, and Dragon's Blaze. High elemental resistance.",
        gm_notes="Engine template: Lizards_Female_Armor_Mage. Lizard fire mage.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Bandit Lizard Firelord",
        gm_template_id="Lizards_Female_Armor_Leather_A",
        faction=Faction.BANDITS,
        race=Race.LIZARD,
        archetype=Archetype.BOSS,
        equipment="Blazing Scimitar + Greatshield",
        ai_tactics="Ignites the battlefield with Dragon's Blaze and Fireball, then executes with Warfare.",
        gm_notes="Engine template: Lizards_Female_Armor_Leather_A (Boss).",
        can_be_boss=True
    ),

    # --- Undead Bandits ---
    BestiaryTemplate(
        name="Undead Bandit Thug",
        gm_template_id="Undead_Skeleton_Axe_1H",
        faction=Faction.BANDITS,
        race=Race.UNDEAD,
        archetype=Archetype.FIGHTER,
        equipment="Rusty Cleaver + Splintered Buckler",
        ai_tactics="Healed by poison. Feigns death with Play Dead when low on HP. Uses Crippling Blow.",
        gm_notes="Engine template: Undead_Skeleton_Axe_1H. Skeletal outlaw recruit.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Undead Bandit Cutthroat",
        gm_template_id="Undead_Skeleton_Dagger_1H",
        faction=Faction.BANDITS,
        race=Race.UNDEAD,
        archetype=Archetype.ROGUE,
        equipment="Dual Bone Shivs",
        ai_tactics="Stealth assassin. Applies poison coating to blades, drops aggro with Play Dead if targeted.",
        gm_notes="Engine template: Undead_Skeleton_Dagger_1H. Undead rogue.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Undead Bandit Poacher",
        gm_template_id="Undead_Skeleton_Bow",
        faction=Faction.BANDITS,
        race=Race.UNDEAD,
        archetype=Archetype.RANGER,
        equipment="Rotting Longbow + Venom Quiver",
        ai_tactics="Fires poison arrows to heal friendly undead while damaging player vitality.",
        gm_notes="Engine template: Undead_Skeleton_Bow. Poison archer.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Undead Bandit Hexer",
        gm_template_id="Undead_Skeleton_Caster_Fire",
        faction=Faction.BANDITS,
        race=Race.UNDEAD,
        archetype=Archetype.MAGE,
        equipment="Skull-Topped Staff",
        ai_tactics="Casts Contamination and Poison Darts, spreading poison across the battlefield.",
        gm_notes="Engine template: Undead_Skeleton_Caster_Fire / Earth. Toxic caster.",
        can_be_minion=False
    ),

    # =========================================================================
    # FACTION: UNDEAD & BLACK RING (MULTI-RACIAL LEGIONS)
    # Verified in english.xml: Undead Elf, Undead Dwarf, Undead Lizard, Undead Human
    # =========================================================================
    # --- Undead Humans & Skeletons ---
    BestiaryTemplate(
        name="Undead Human Warrior",
        gm_template_id="Undead_Skeleton_Axe_1H",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_HUMAN,
        archetype=Archetype.FIGHTER,
        equipment="Ancient Iron Sword + Rotted Shield",
        ai_tactics="Healed by poison surfaces; casts Play Dead if critically damaged to drop aggro. Knocks down enemies.",
        gm_notes="Engine template: Undead_Skeleton_Axe_1H / Undead_FireSkeleton_2HAxe. Undead human swordsman.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Undead Human Marksman",
        gm_template_id="Undead_Skeleton_Bow",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_HUMAN,
        archetype=Archetype.RANGER,
        equipment="Bone Bow + Poison Arrows",
        ai_tactics="Shoots poison arrows at enemies or down at friendly undead feet to heal them while poisoning players.",
        gm_notes="Engine template: Undead_Skeleton_Bow / Undead_FireSkeleton_Ranger. Poison sniper.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Undead Decaying Mage",
        gm_template_id="Undead_Skeleton_Caster_Air",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_HUMAN,
        archetype=Archetype.MAGE,
        equipment="Bone Wand + Hexing Skull",
        ai_tactics="Spits Poison Darts, casts Contamination, and casts Mosquito Swarm. Heals himself with poison.",
        gm_notes="Engine template: Undead_Skeleton_Caster_Air / Undead_FireSkeleton_Mage. High magic armor.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Undead Bone Reaver",
        gm_template_id="Undead_Skeleton_Axe_2H",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_HUMAN,
        archetype=Archetype.TANK,
        equipment="Heavy Two-Handed Scythe + Spiked Ribcage",
        ai_tactics="Taunts heroes, applies Retribution damage reflection, and uses Battle Stomp when armor is low.",
        gm_notes="Engine template: Undead_Skeleton_Axe_2H. Heavy skeletal frontline.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Undead Skeletal Overlord",
        gm_template_id="Undead_Skeleton_Axe_2H",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_HUMAN,
        archetype=Archetype.BOSS,
        equipment="Two-Handed Ancient Cleaver + Spiked Ribs",
        ai_tactics="Commands undead thralls, leaps with Phoenix Dive, casts Play Dead and Whirlwind.",
        gm_notes="Engine template: Undead_Skeleton_Axe_2H (Boss).",
        can_be_boss=True
    ),

    # --- Undead Elves ---
    BestiaryTemplate(
        name="Undead Elf Warrior",
        gm_template_id="Elves_Female_Skeleton_A",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_ELF,
        archetype=Archetype.FIGHTER,
        equipment="Ancient Elven Glaive",
        ai_tactics="Uses Flesh Sacrifice for extra AP, charges into party with Battering Ram and Whirlwind.",
        gm_notes="Engine template: Elves_Female_Skeleton_A. Skeletal elf warrior with Flesh Sacrifice.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Undead Elf Rogue",
        gm_template_id="Elves_Hero_Female_Undead",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_ELF,
        archetype=Archetype.ROGUE,
        equipment="Cursed Obsidian Daggers",
        ai_tactics="Lethal assassin. Casts Flesh Sacrifice to get extra AP, teleports behind targets with Backlash.",
        gm_notes="Engine template: Elves_Hero_Female_Undead. Undead elf assassin.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Undead Elf Ranger",
        gm_template_id="Elves_Female_Skeleton_A",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_ELF,
        archetype=Archetype.RANGER,
        equipment="Elven Skeletal Bow",
        ai_tactics="Combines Flesh Sacrifice with Tactical Retreat to seize elevated terrain. Rains poison arrows.",
        gm_notes="Engine template: Elves_Female_Skeleton_A (Ranger). Undead elf archer.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Undead Elf Elementalist",
        gm_template_id="Elves_Female_Skeleton_Mage_A",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_ELF,
        archetype=Archetype.MAGE,
        equipment="Staff of the Dead Ancestors",
        ai_tactics="Creates blood surfaces with Flesh Sacrifice, casts Grasp of the Starved and Decaying Touch.",
        gm_notes="Engine template: Elves_Female_Skeleton_Mage_A. Blood and decay caster.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Ancient Undead Elven Scion",
        gm_template_id="Elves_Female_Skeleton_Mage_A",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_ELF,
        archetype=Archetype.BOSS,
        equipment="Staff of Ancient Roots + Bone Circlet",
        ai_tactics="Flesh Sacrifice into Grasp of the Starved, casts Play Dead when threatened.",
        gm_notes="Engine template: Elves_Female_Skeleton_Mage_A (Boss).",
        can_be_boss=True
    ),

    # --- Undead Dwarves ---
    BestiaryTemplate(
        name="Undead Dwarf Warrior",
        gm_template_id="Dwarves_Female_Skeleton_A",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_DWARF,
        archetype=Archetype.FIGHTER,
        equipment="Skeletal Dwarven Greathammer",
        ai_tactics="Crushing blows, high vitality, casts Petrifying Touch to freeze targets stripped of magic armor.",
        gm_notes="Engine template: Dwarves_Female_Skeleton_A. Sturdy undead dwarf brawler.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Undead Dwarf Defender",
        gm_template_id="Dwarves_Female_Skeleton_A",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_DWARF,
        archetype=Archetype.TANK,
        equipment="Ancient Dwarven Tomb Shield + Mace",
        ai_tactics="Massive armor pool. Uses Shields Up and Fortify to create an impenetrable defensive vanguard.",
        gm_notes="Engine template: Dwarves_Female_Skeleton_A (Tank). Tough skeletal defender.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Undead Dwarf Rogue",
        gm_template_id="Dwarves_Female_Skeleton_A",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_DWARF,
        archetype=Archetype.ROGUE,
        equipment="Twin Tomb Daggers",
        ai_tactics="Sneaks through combat, applies Petrifying Touch and backstabs vulnerable backline characters.",
        gm_notes="Engine template: Dwarves_Female_Skeleton_A (Rogue). Undead dwarf assassin.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Undead Dwarf Elementalist",
        gm_template_id="Dwarves_Female_Skeleton_A",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_DWARF,
        archetype=Archetype.MAGE,
        equipment="Skeletal Earth Wand",
        ai_tactics="Geomancy spells: shoots poison darts and oil boulders, turns the arena into a hazardous zone.",
        gm_notes="Engine template: Dwarves_Female_Skeleton_A (Mage). Earth elementalist.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Ancient Undead Dwarven Thane",
        gm_template_id="Dwarves_Female_Skeleton_A",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_DWARF,
        archetype=Archetype.BOSS,
        equipment="Skeletal Dwarven Greathammer + Crypt Shield",
        ai_tactics="Immense durability, uses Petrifying Touch and Battle Stomp to lock down party.",
        gm_notes="Engine template: Dwarves_Female_Skeleton_A (Boss).",
        can_be_boss=True
    ),

    # --- Undead Lizards ---
    BestiaryTemplate(
        name="Undead Lizard Warrior",
        gm_template_id="Lizards_Female_Skeleton_A",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_LIZARD,
        archetype=Archetype.FIGHTER,
        equipment="Ancient Lizard Blade + Tower Shield",
        ai_tactics="Breathes Dragon's Blaze to ignite oil and players, charges with Battering Ram.",
        gm_notes="Engine template: Lizards_Female_Skeleton_A. Undead lizard with Dragon's Blaze.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Undead Lizard Rogue",
        gm_template_id="Lizards_Hero_Female_Undead",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_LIZARD,
        archetype=Archetype.ROGUE,
        equipment="Twin Cursed Daggers",
        ai_tactics="Fast movement. Teleports with Cloak and Dagger, breathes fire, and inflicts Rupture Tendons.",
        gm_notes="Engine template: Lizards_Hero_Female_Undead. High mobility undead lizard.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Undead Lizard Ranger",
        gm_template_id="Lizards_Female_Skeleton_A",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_LIZARD,
        archetype=Archetype.RANGER,
        equipment="Ancient Reptilian Bow",
        ai_tactics="Long range poison and fire arrows. Uses Dragon's Blaze as close-quarters defense.",
        gm_notes="Engine template: Lizards_Female_Skeleton_A (Ranger). Fire/Poison hybrid archer.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Undead Lizard Elementalist",
        gm_template_id="Lizards_Female_Skeleton_Mage_A",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_LIZARD,
        archetype=Archetype.MAGE,
        equipment="Skeletal Pyro Staff",
        ai_tactics="Combines Pyromancy with Geomancy. Immune to fire and poison surfaces.",
        gm_notes="Engine template: Lizards_Female_Skeleton_Mage_A. High magic armor.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Ancient Undead Lizard Sovereign",
        gm_template_id="Lizards_Female_Skeleton_Mage_A",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_LIZARD,
        archetype=Archetype.BOSS,
        equipment="Flaming Skeletal Glaive + Obsidian Crest",
        ai_tactics="Dragon's Blaze into Fireball, creates massive cursed fire zones.",
        gm_notes="Engine template: Lizards_Female_Skeleton_Mage_A (Boss).",
        can_be_boss=True
    ),

    # --- Black Ring & Undead Bosses ---
    BestiaryTemplate(
        name="Black Ring Pain Reaver",
        gm_template_id="GEN_GM_GenericTank",
        faction=Faction.UNDEAD,
        race=Race.HUMAN,
        archetype=Archetype.TANK,
        equipment="Spiked Morningstar + Tower Shield",
        ai_tactics="Taunts heroes, applies Retribution damage reflection, and uses Battle Stomp when armor is low.",
        gm_notes="Engine template: GEN_GM_GenericTank with Black Ring tag. God King vanguard.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Black Ring Defiler",
        gm_template_id="GM_Brute_Caster_Terra",
        faction=Faction.UNDEAD,
        race=Race.HUMAN,
        archetype=Archetype.BATTLEMAGE,
        equipment="Cursed Obsidian Blade + Shadow Focus",
        ai_tactics="Casts Raining Blood followed by Grasp of the Starved. Uses Living on the Edge when dropping to 1 HP.",
        gm_notes="Engine template: GM_Brute_Caster_Terra with Necromancer spells. Extremely lethal in blood.",
        can_be_boss=True
    ),
    BestiaryTemplate(
        name="Ancient Bone Golem",
        gm_template_id="Undead_Bonepile_Troll_A",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD,
        archetype=Archetype.BOSS,
        equipment="Colossal Fused Bone Fists",
        ai_tactics="Absorbs nearby corpses with Bone Cage for massive physical armor spikes, then slams ground for AoE knockdown.",
        gm_notes="Engine template: Undead_Bonepile_Troll_A / Undead_Bonepile_Spider_A. Fused bone monstrosity.",
        can_be_boss=True
    ),

    # =========================================================================
    # FACTION: MAGISTERS & DIVINE ORDER / PALADINS
    # =========================================================================
    BestiaryTemplate(
        name="Magister Swordsman",
        gm_template_id="GM_Magister_Melee",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.FIGHTER,
        equipment="One-handed Longsword + Divine Steel Shield",
        ai_tactics="Engages frontliners, uses Battering Ram to knock down targets stripped of physical armor. Uses Shields Up.",
        gm_notes="Engine template: GM_Magister_Melee. Standard Divine Order soldier.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Magister Ranger",
        gm_template_id="GM_Magister_Ranger",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.RANGER,
        equipment="Refined Composite Bow + Quiver of Knockdown/Poison Arrows",
        ai_tactics="Prioritizes high-ground platforms immediately with Tactical Retreat. Snipes squishy mages with Ballistic Shot.",
        gm_notes="Engine template: GM_Magister_Ranger. High Ground sniper.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Magister Cryomancer",
        gm_template_id="GM_Magister_Caster_Cryo",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.MAGE,
        equipment="Glacial Water Staff + Cloth Robes",
        ai_tactics="Casts Rain to make party Wet, then freezes with Hail Strike or Winter Blast. Clears CC with Armor of Frost.",
        gm_notes="Engine template: GM_Magister_Caster_Cryo. Specialized water/ice control caster.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Magister Pyromancer",
        gm_template_id="GM_Magister_Caster_Pyro",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.MAGE,
        equipment="Scorching Fire Wand + Shield",
        ai_tactics="Ignites oil surfaces and players with Fireball and Searing Daggers. Uses Peace of Mind to buff allies.",
        gm_notes="Engine template: GM_Magister_Caster_Pyro. Fiery area denial.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Magister Inquisitor",
        gm_template_id="GM_Magister_Melee_Strong",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.BATTLEMAGE,
        equipment="Two-Handed Greatsword + Plate Armor",
        ai_tactics="Blends Warfare cleaves with Necromancy. Casts Mosquito Swarm from range, then charges in with Decaying Touch.",
        gm_notes="Engine template: GM_Magister_Melee_Strong. Decaying Touch turns player healing into lethal damage.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Silent Monk Initiate",
        gm_template_id="Creatures_Purged_A",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.ROGUE,
        equipment="Dual Purged Daggers",
        ai_tactics="Fast footwork, immune to Silenced. Flanks party backline, applies Rupture Tendons and Backlash.",
        gm_notes="Engine template: Creatures_Purged_A / GM_Magister_Rogue. Soulless purged fighter.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Elven Silent Monk",
        gm_template_id="Elves_Female_Silentmonk_A",
        faction=Faction.MAGISTERS,
        race=Race.ELF,
        archetype=Archetype.ROGUE,
        equipment="Twin Purged Blades",
        ai_tactics="Extremely rapid movement. Uses Flesh Sacrifice and Backlash to stunlock squishy mages.",
        gm_notes="Engine template: Elves_Female_Silentmonk_A. Elven variant of the Silent Monk.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Lizard Silent Monk",
        gm_template_id="Lizards_Female_Silentmonk_A",
        faction=Faction.MAGISTERS,
        race=Race.LIZARD,
        archetype=Archetype.FIGHTER,
        equipment="Purged Scimitar + Shield",
        ai_tactics="Breathes Dragon's Blaze to trigger fire traps, charges into player frontlines.",
        gm_notes="Engine template: Lizards_Female_Silentmonk_A. Lizard variant of the Silent Monk.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Gheist Monstrosity",
        gm_template_id="Creatures_Gheist_A",
        faction=Faction.MAGISTERS,
        race=Race.CREATURE,
        archetype=Archetype.ROGUE,
        equipment="Monstrous Claw Blades",
        ai_tactics="Lethal assassin with extreme AP efficiency. Teleports behind lowest physical armor hero, backstabs relentlessly.",
        gm_notes="Engine template: Creatures_Gheist_A. Terrifying mutated bioweapon.",
        can_be_boss=False
    ),
    BestiaryTemplate(
        name="Paladin Defender",
        gm_template_id="GM_Paladin_Melee_Strong",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.TANK,
        equipment="Lucian Holy Greatshield + Blessed Mace",
        ai_tactics="Shields allies, Taunts enemy martial characters, and casts Fortify to purge debuffs.",
        gm_notes="Engine template: GM_Paladin_Melee_Strong. Order of the Divine paladin; heavy physical vanguard.",
        can_be_boss=False
    ),
    BestiaryTemplate(
        name="Paladin Ranger",
        gm_template_id="GM_Paladin_Ranger",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.RANGER,
        equipment="Divine Order Longbow",
        ai_tactics="Snipes from fortified positions, fires holy-enchanted arrows and pins down threats.",
        gm_notes="Engine template: GM_Paladin_Ranger. High precision ranged support.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Magister High Commander",
        gm_template_id="GM_Magister_Caster_Strong",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.BOSS,
        equipment="Enchanted Divine Greatblade + Ornate Gold Plate",
        ai_tactics="Leads from the front with Overpower, Leadership aura, and Phoenix Dive. Coordinates target focus.",
        gm_notes="Engine template: GM_Magister_Caster_Strong / GM_Paladin_Caster_Strong. Boss with 6 AP per turn.",
        can_be_boss=True
    ),

    # =========================================================================
    # FACTION: VOIDWOKEN & VOID ENTITIES
    # =========================================================================
    BestiaryTemplate(
        name="Viscous Voidling",
        gm_template_id="Animals_Voidling",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.MINION,
        equipment="Venomous Mandibles",
        ai_tactics="Swarm tactic: rushes closest target in numbers. Explodes on death in cursed necrofire or acid puddle.",
        gm_notes="Engine template: Animals_Voidling / Animals_Voidwoken_VolatileVoidling. Fragile swarm minion.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Voidwoken Frog Spitter",
        gm_template_id="Animals_Voidwoken_Frog_A",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.RANGER,
        equipment="Corrosive Acid Spittle",
        ai_tactics="Leaps across platforms, spits caustic poison pools that corrode physical armor.",
        gm_notes="Engine template: Animals_Voidwoken_Frog_A. Native GM void creature with ranged acid attacks.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Void-Touched Stalker",
        gm_template_id="Animals_Deer_A_Void_A",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.FIGHTER,
        equipment="Corrupted Claws & Spikes",
        ai_tactics="Leaps over frontline tanks straight onto vulnerable mages. Applies Crippled and Bleeding with claw strikes.",
        gm_notes="Engine template: Animals_Deer_A_Void_A / Animals_Wolf_A_Voidwoken. Fast leaping corrupted beast.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Voidwoken Deep-Dweller",
        gm_template_id="Animals_Voidwoken_Merman_A",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.BOSS,
        equipment="Ancient Void Staff & Cursed Tendrils",
        ai_tactics="Opens with Shackles of Pain on highest DPS player, then casts Grasp of the Starved and Decaying Touch.",
        gm_notes="Engine template: Animals_Voidwoken_Merman_A / Voidwoken_Alan_A_Boss. Dangerous caster boss.",
        can_be_boss=True
    ),
    BestiaryTemplate(
        name="Voidwoken Goliath / Drillworm",
        gm_template_id="Animals_Voidwoken_Drillworm_Hatchling",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.TANK,
        equipment="Armored Carapace & Chitinous Fists",
        ai_tactics="Heavy brawler. Charges through frontline with Battering Ram and casts Earthquake to disrupt entire party.",
        gm_notes="Engine template: Animals_Voidwoken_Drillworm_Hatchling. Immense Physical Armor and burrowing power.",
        can_be_boss=True
    ),

    # =========================================================================
    # FACTION: WILD BEASTS & ELEMENTALS
    # =========================================================================
    BestiaryTemplate(
        name="Pack Wolf",
        gm_template_id="Animals_Wolf_A_Black",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.MINION,
        equipment="Razor Fangs",
        ai_tactics="Coordinates with pack members, flanks isolated heroes, inflicts Crippled and Bleeding.",
        gm_notes="Engine template: Animals_Wolf_A_Black / Animals_Wolf_A_White. Deploy in packs of 3 to 6.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Giant Brood Spider",
        gm_template_id="GM_Spider_Easy",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.ROGUE,
        equipment="Venomous Fangs & Spinnerets",
        ai_tactics="Spins Spider Web on players to entrap them, then spits corrosive poison darts.",
        gm_notes="Engine template: GM_Spider_Easy / Animals_Spider_Poison. Entangles players ignoring physical armor.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Alpha Dire Bear",
        gm_template_id="GM_Bear_Easy",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.TANK,
        equipment="Gargantuan Claws & Thick Fur",
        ai_tactics="Massive vitality pool. Roars to terrify players, swipes with heavy physical cleaves.",
        gm_notes="Engine template: GM_Bear_Easy / Animals_Bear_A. High vitality beast guardian.",
        can_be_boss=True
    ),
    BestiaryTemplate(
        name="Fire Slug Matriarch",
        gm_template_id="GM_FireSlug_Boss",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.BOSS,
        equipment="Molten Magma Carapace",
        ai_tactics="Oozes continuous fire trails, casts Supernova, and heals when submerged in fire.",
        gm_notes="Engine template: GM_FireSlug_Boss (Grunts: GM_FireSlug_Grunt). Native GM boss creature.",
        can_be_boss=True
    ),
    BestiaryTemplate(
        name="Greater Fire Elemental",
        gm_template_id="Creatures_Elemental_A_Fire",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.MAGE,
        equipment="Blazing Core",
        ai_tactics="Immune to and healed by Fire. Casts Fireball, Supernova, and ignites all surrounding surfaces.",
        gm_notes="Engine template: Creatures_Elemental_A_Fire. Living embodiment of flame.",
        can_be_boss=False
    ),

    # =========================================================================
    # FACTION: DEMONS & CULTISTS
    # =========================================================================
    BestiaryTemplate(
        name="Crimson Fire Demon",
        gm_template_id="GM_Fire_Demon",
        faction=Faction.DEMONS,
        race=Race.DEMON,
        archetype=Archetype.FIGHTER,
        equipment="Burning Hell-Blades",
        ai_tactics="Sprouts wings to fly into player rear lines, slashes with fire-infused melee strikes.",
        gm_notes="Engine template: GM_Fire_Demon. Hostile Netherworld fiend; fire immune.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Blood Demon Harvester",
        gm_template_id="GM_Blood_Demon",
        faction=Faction.DEMONS,
        race=Race.DEMON,
        archetype=Archetype.MAGE,
        equipment="Cursed Blood Talons",
        ai_tactics="Drains vitality with Mosquito Swarm, casts Raining Blood, and inflicts Decaying Touch.",
        gm_notes="Engine template: GM_Blood_Demon. Specialized necromantic demon in GM mode.",
        can_be_boss=False
    ),
    BestiaryTemplate(
        name="Electric Storm Demon",
        gm_template_id="GM_Electric_Demon",
        faction=Faction.DEMONS,
        race=Race.DEMON,
        archetype=Archetype.MAGE,
        equipment="Crackling Arcane Wand",
        ai_tactics="Casts Chain Lightning and Electric Discharge. Stuns wet or shocked players.",
        gm_notes="Engine template: GM_Electric_Demon. High air magic and shock damage.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Blood Cultist Zealot",
        gm_template_id="GM_Poison_Demon",
        faction=Faction.DEMONS,
        race=Race.HUMAN,
        archetype=Archetype.MINION,
        equipment="Sacrificial Kris Dagger",
        ai_tactics="Rushes heroes and casts Blood Sacrifice. Explodes on death in toxic cursed fluid.",
        gm_notes="Engine template: GM_Poison_Demon / GM_Oil_Demon. Suicide rush fanatic.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Arch-Demon of Chaos",
        gm_template_id="Creatures_Demon_Grunt_A",
        faction=Faction.DEMONS,
        race=Race.DEMON,
        archetype=Archetype.BOSS,
        equipment="Obsidian Greatsword + Demonic Wings",
        ai_tactics="Radiates Demonic Aura. Casts Chain Lightning, Epidemic of Fire, and strikes with devastating cleaves.",
        gm_notes="Engine template: Creatures_Demon_Grunt_A with boss scaling. 6 AP turns.",
        can_be_boss=True
    ),

    # =========================================================================
    # FACTION: ANCIENT AUTOMATONS
    # =========================================================================
    BestiaryTemplate(
        name="Raanaar Clockwork Sentinel",
        gm_template_id="Creatures_Raanaar_Automaton_A",
        faction=Faction.AUTOMATONS,
        race=Race.AUTOMATON,
        archetype=Archetype.TANK,
        equipment="Heavy Brass Tower Shield + Shock Baton",
        ai_tactics="Immune to Bleeding and Poison. Uses Deflective Barrier and Shield Bash to protect allies.",
        gm_notes="Engine template: Creatures_Raanaar_Automaton_A. Authentic ancient automaton in GM RootTemplates.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Raanaar Arcane Ballista",
        gm_template_id="Creatures_Raanaar_Automaton_B",
        faction=Faction.AUTOMATONS,
        race=Race.AUTOMATON,
        archetype=Archetype.RANGER,
        equipment="Mounted Triple-Repeater Ballista",
        ai_tactics="Stationary or slow-moving artillery. Fires heavy piercing bolts with long range and high ground simulation.",
        gm_notes="Engine template: Creatures_Raanaar_Automaton_B. Heavy physical ranged pressure.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Ancient Relic Titan",
        gm_template_id="Creatures_Raanaar_Automaton_A",
        faction=Faction.AUTOMATONS,
        race=Race.AUTOMATON,
        archetype=Archetype.BOSS,
        equipment="Colossal Steam Pistons & Kinetic Core",
        ai_tactics="Crushes players with Ground Slam, emits EMP shockwaves that silence and shock nearby heroes.",
        gm_notes="Engine template: Creatures_Raanaar_Automaton_A (Boss variant). Massive mechanical dungeon guardian.",
        can_be_boss=True
    ),
]


def get_templates_by_faction(faction: Optional[Faction] = None, race: Optional[Race] = None) -> List[BestiaryTemplate]:
    """
    Retrieve bestiary templates, filterable by faction and/or race.
    If faction is None or Faction.ANY, considers templates across all factions.
    If race is Race.UNDEAD, matches all undead variants (UNDEAD, UNDEAD_HUMAN, UNDEAD_ELF, UNDEAD_DWARF, UNDEAD_LIZARD).
    If a specific race is given (e.g. Race.UNDEAD_DWARF, Race.DWARF, Race.HUMAN), matches strictly that race.
    """
    templates = BESTIARY if (faction is None or faction == Faction.ANY) else [t for t in BESTIARY if t.faction == faction]
    if race is not None:
        if race == Race.UNDEAD:
            templates = [t for t in templates if t.race in (
                Race.UNDEAD,
                Race.UNDEAD_HUMAN,
                Race.UNDEAD_ELF,
                Race.UNDEAD_DWARF,
                Race.UNDEAD_LIZARD,
            )]
        else:
            templates = [t for t in templates if t.race == race]
    return templates
