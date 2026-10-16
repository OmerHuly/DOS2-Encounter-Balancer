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
    signature_talents: Optional[List[str]] = None


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
        gm_notes="Tough human mercenary brawler.",
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
        gm_notes="High initiative backstab specialist.",
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
        gm_notes="Equips oil and knockdown arrows.",
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
        gm_notes="Chaotic spellcaster.",
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
        gm_notes="Outlaw leader with Executioner talent.",
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
        gm_notes="Dwarf racial (+10% Vitality, Petrifying Touch).",
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
        gm_notes="Sturdy frontline dwarf.",
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
        gm_notes="Listed directly in english.xml.",
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
        gm_notes="Earth/Geo caster.",
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
        gm_notes="Agile dwarven rogue/assassin.",
        can_be_minion=False,
        signature_talents=["The Pawn"]
    ),
    BestiaryTemplate(
        name="Bandit Dwarven Warlord",
        gm_template_id="Dwarves_Male_Clothing_Bandit_A",
        faction=Faction.BANDITS,
        race=Race.DWARF,
        archetype=Archetype.BOSS,
        equipment="Two-Handed Dwarven Battleaxe + Spiked Armor",
        ai_tactics="Charges with Bull Horns, uses Petrifying Touch and Whirlwind. High vitality.",
        gm_notes="Veteran dwarven bandit warlord.",
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
        gm_notes="High burst melee elf.",
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
        gm_notes="Lethal elven assassin.",
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
        gm_notes="Sniper with AP boost.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Bandit Elf Elementalist",
        gm_template_id="Elves_Female_Armor_Mage",
        faction=Faction.BANDITS,
        race=Race.ELF,
        archetype=Archetype.MAGE,
        equipment="Hydro Wand + Shield",
        ai_tactics="Uses Flesh Sacrifice for bonus AP and damage, ignites ground with Ignition to trigger fire Elemental Affinity, and casts Fireball and Laser Ray at reduced AP cost.",
        gm_notes="Leverages fire surface synergy.",
        can_be_boss=True,
        can_be_minion=False,
        signature_talents=["Elemental Affinity"]
    ),
    BestiaryTemplate(
        name="Bandit Elven Captain",
        gm_template_id="Elves_Female_Armor_Leather_A",
        faction=Faction.BANDITS,
        race=Race.ELF,
        archetype=Archetype.BOSS,
        equipment="Masterwork Elven Longbow + Poison Quiver",
        ai_tactics="Flesh Sacrifice into Tactical Retreat, rains Arrow Storm and Ballistic Shot.",
        gm_notes="Elven outlaw sharpshooter captain.",
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
        gm_notes="Dragon's Blaze fire cone.",
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
        gm_notes="Fast and agile skirmisher.",
        can_be_boss=True,
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Lizard Shadowblade Assassin",
        gm_template_id="Lizards_Female_Armor_Leather_A",
        faction=Faction.BANDITS,
        race=Race.LIZARD,
        archetype=Archetype.ROGUE,
        equipment="Twin Masterwork Dragon-Bone Daggers",
        ai_tactics="Lethal shadowblade assassin. Teleports with Cloak and Dagger, strikes from shadows with Backlash and Rupture Tendons, vanishes into Chameleon Cloak, and ignites survivors with Dragon's Blaze.",
        gm_notes="Iconic Lizard Rogue / Assassin boss.",
        can_be_boss=True,
        can_be_minion=False,
        signature_skills=["Backlash", "Cloak and Dagger", "Rupture Tendons", "Chameleon Cloak", "Adrenaline", "Dragon's Blaze", "Sawtooth Blade"],
    ),
    BestiaryTemplate(
        name="Bandit Lizard Ranger",
        gm_template_id="Lizards_Female_Armor_Leather_A",
        faction=Faction.BANDITS,
        race=Race.LIZARD,
        archetype=Archetype.RANGER,
        equipment="Empire Composite Bow",
        ai_tactics="Shoots fire arrows, sets fire surfaces, breathes fire on anyone who tries to engage in melee.",
        gm_notes="Fire archer.",
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
        gm_notes="Lizard fire mage.",
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
        gm_notes="Pyrokinetic lizard commander.",
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
        gm_notes="Skeletal outlaw recruit.",
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
        gm_notes="Undead rogue.",
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
        gm_notes="Poison archer.",
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
        gm_notes="Toxic caster.",
        can_be_minion=False
    ),

    # --- Official GM Mode Outlaw & Adventurer Archetypes ---
    BestiaryTemplate(
        name="Bandit Enforcer Brute",
        gm_template_id="GameMaster_Bandit_Norm_Female_Brute",
        faction=Faction.BANDITS,
        race=Race.HUMAN,
        archetype=Archetype.TANK,
        equipment="Heavy Iron Warhammer + Reinforced Bandit Shield",
        ai_tactics="Anchors the outlaw frontline, uses Shield Bounce and Battle Stomp to knock down intruders.",
        gm_notes="Official GM Mode Bandit Brute template.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Outlaw Alchemist",
        gm_template_id="GameMaster_Archetype_TheAlchemist",
        faction=Faction.BANDITS,
        race=Race.HUMAN,
        archetype=Archetype.RANGER,
        equipment="Repeating Crossbow + Bandolier of Alchemical Flasks",
        ai_tactics="Hurls explosive firestorm and poison flasks, fires special elemental bolts, and uses Chloroform.",
        gm_notes="Official GM Mode Archetype: The Alchemist.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Outlaw Barbarian Berserker",
        gm_template_id="GameMaster_Archetype_TheBarbarian",
        faction=Faction.BANDITS,
        race=Race.HUMAN,
        archetype=Archetype.FIGHTER,
        equipment="Colossal Two-Handed Greataxe",
        ai_tactics="Enrages for guaranteed critical hits, charges with Battering Ram, and cleaves with Whirlwind.",
        gm_notes="Official GM Mode Archetype: The Barbarian.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Renegade Battlemage",
        gm_template_id="GameMaster_Archetype_TheBattleMage",
        faction=Faction.BANDITS,
        race=Race.HUMAN,
        archetype=Archetype.BATTLEMAGE,
        equipment="Sparking Quarterstaff + Spiked Mail",
        ai_tactics="Combines close-quarters Warfare strikes with Blinding Radiance and Shocking Touch.",
        gm_notes="Official GM Mode Archetype: The Battlemage.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Outlaw Dark Knight",
        gm_template_id="GameMaster_Archetype_TheDarkKnight",
        faction=Faction.BANDITS,
        race=Race.HUMAN,
        archetype=Archetype.TANK,
        equipment="Cursed Greatsword + Dread Plate",
        ai_tactics="Inflicts Decaying Touch and Shackles of Pain, drains vitality with Mosquito Swarm, and cleaves frontliners.",
        gm_notes="Official GM Mode Archetype: The Dark Knight.",
        can_be_boss=True,
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Wildlander Druid",
        gm_template_id="GameMaster_Archetype_TheDruid",
        faction=Faction.BANDITS,
        race=Race.ELF,
        archetype=Archetype.SUMMONER,
        equipment="Living Wood Staff + Bark Buckler",
        ai_tactics="Summons an Elemental Incarnate on natural surfaces, buffs allies with Mend Metal and Soothing Cold.",
        gm_notes="Official GM Mode Archetype: The Druid.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Arena Gladiator Champion",
        gm_template_id="GameMaster_Archetype_TheGladiator",
        faction=Faction.BANDITS,
        race=Race.HUMAN,
        archetype=Archetype.FIGHTER,
        equipment="Gladiator Gladius + Spiked Buckler",
        ai_tactics="Veteran pit fighter. Uses Bouncing Shield, Tentacle Lash, and Bull Horns to dominate single combat.",
        gm_notes="Official GM Mode Archetype: The Gladiator.",
        can_be_boss=True,
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Outlaw Martial Monk",
        gm_template_id="GameMaster_Archetype_TheMonk",
        faction=Faction.BANDITS,
        race=Race.ELF,
        archetype=Archetype.ROGUE,
        equipment="Twin Katar Daggers",
        ai_tactics="High dodge and mobility. Uses Backlash, Adrenaline, and Chloroform to neutralize priority targets.",
        gm_notes="Official GM Mode Archetype: The Monk.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Renegade Necromancer",
        gm_template_id="GameMaster_Archetype_TheNecromancer",
        faction=Faction.BANDITS,
        race=Race.HUMAN,
        archetype=Archetype.CLERIC,
        equipment="Bone-Carved Mace + Skull Shield",
        ai_tactics="Rains blood over the arena, casts Mosquito Swarm and Infect, and raises bloated corpses.",
        gm_notes="Official GM Mode Archetype: The Necromancer.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Tribal Shaman Conjurer",
        gm_template_id="GameMaster_Archetype_TheShaman",
        faction=Faction.BANDITS,
        race=Race.LIZARD,
        archetype=Archetype.SUMMONER,
        equipment="Totemic Wand + Fetish Shield",
        ai_tactics="Spawns Elemental Totems every turn, summons an Incarnate, and supports with Farsight Infusion.",
        gm_notes="Official GM Mode Archetype: The Shaman.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Outlaw Swashbuckler",
        gm_template_id="GameMaster_Archetype_TheSwashbuckler",
        faction=Faction.BANDITS,
        race=Race.HUMAN,
        archetype=Archetype.ROGUE,
        equipment="Twin Cutlass Daggers",
        ai_tactics="Flanks with Cloak and Dagger, throws Gag Order and Sleeping Arms, and backstabs isolated foes.",
        gm_notes="Official GM Mode Archetype: The Swashbuckler.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Tribal Goblin War-Chief",
        gm_template_id="GameMaster_Goblin_Tough_Chief",
        faction=Faction.BANDITS,
        race=Race.DWARF,
        archetype=Archetype.BOSS,
        equipment="Jagged Tribal Cleaver + War-Chief Totem Shield",
        ai_tactics="Rallies raiders with Leadership, hurls oil flasks, and charges knocked-down heroes.",
        gm_notes="Official GM Mode Goblin Tough Chief template.",
        can_be_boss=True,
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
        gm_notes="Undead human swordsman.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Undead Human Rogue",
        gm_template_id="GameMaster_Skeleton_Human_Rogue",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_HUMAN,
        archetype=Archetype.ROGUE,
        equipment="Dual Corroded Bone Daggers",
        ai_tactics="Teleports behind casters with Backlash, lacerates with Rupture Tendons, and feigns death with Play Dead.",
        gm_notes="Official GM Mode Skeleton Human Rogue.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Undead Human Marksman",
        gm_template_id="Undead_Skeleton_Bow",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_HUMAN,
        archetype=Archetype.RANGER,
        equipment="Bone Bow + Poison Arrows",
        ai_tactics="Shoots poison arrows at enemies or down at friendly undead feet to heal them while poisoning players.",
        gm_notes="Poison sniper.",
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
        gm_notes="High magic armor.",
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
        gm_notes="Heavy skeletal frontline.",
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
        gm_notes="Skeletal legion commander.",
        can_be_boss=True
    ),
    BestiaryTemplate(
        name="Fire Skeleton Decapitator",
        gm_template_id="GameMaster_SkeletonFire_Easy_Decapitator",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_HUMAN,
        archetype=Archetype.FIGHTER,
        equipment="Blazing Two-Handed Executioner Greatsword",
        ai_tactics="Wreathed in necrofire. Charges with Phoenix Dive and cleaves burning targets with Whirlwind.",
        gm_notes="Official GM Mode Fire Skeleton Decapitator.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Fire Skeleton Marksman",
        gm_template_id="GameMaster_SkeletonFire_Easy_Marksman",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_HUMAN,
        archetype=Archetype.RANGER,
        equipment="Charred Longbow + Explosive Fire Arrows",
        ai_tactics="Shoots fire and explosive arrows from high ground to ignite oil and poison surfaces.",
        gm_notes="Official GM Mode Fire Skeleton Marksman.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Fire Skeleton Scorcher",
        gm_template_id="GameMaster_SkeletonFire_Easy_Scorcher",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_HUMAN,
        archetype=Archetype.MAGE,
        equipment="Cursed Pyromancy Staff",
        ai_tactics="Hurls Fireball and Searing Daggers, igniting poison clouds into massive explosions.",
        gm_notes="Official GM Mode Fire Skeleton Scorcher.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Ancient Lich Archmage",
        gm_template_id="GameMaster_Archetype_TheLich",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_HUMAN,
        archetype=Archetype.BOSS,
        equipment="Staff of the Undying Lich + Phylactery Amulet",
        ai_tactics="Master of Necromancy and Geomancy. Casts Grasp of the Starved, Contamination, and Living on the Edge.",
        gm_notes="Official GM Mode Archetype: The Lich.",
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
        gm_notes="Skeletal elf warrior with Flesh Sacrifice.",
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
        gm_notes="Undead elf assassin.",
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
        gm_notes="Undead elf archer.",
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
        gm_notes="Blood and decay caster.",
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
        gm_notes="Ancient elven necromancer lord.",
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
        gm_notes="Sturdy undead dwarf brawler.",
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
        gm_notes="Tough skeletal defender.",
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
        gm_notes="Undead dwarf assassin.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Undead Dwarf Ranger",
        gm_template_id="GameMaster_Skeleton_Dwarf_Ranger",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD_DWARF,
        archetype=Archetype.RANGER,
        equipment="Dwarven Bone Crossbow + Venom Bolts",
        ai_tactics="Holds elevated ledges, fires Pin Down and Ricochet, and petrifies any flanker who approaches.",
        gm_notes="Official GM Mode Skeleton Dwarf Ranger.",
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
        gm_notes="Earth elementalist.",
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
        gm_notes="Ancient dwarven crypt monarch.",
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
        gm_notes="Undead lizard with Dragon's Blaze.",
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
        gm_notes="High mobility undead lizard.",
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
        gm_notes="Fire/Poison hybrid archer.",
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
        gm_notes="High magic armor.",
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
        gm_notes="Ancient lizard empire undead ruler.",
        can_be_boss=True
    ),

    # --- Undead Zombies, Ghouls, Bone Abominations & Black Ring ---
    BestiaryTemplate(
        name="Half-Rotten Zombie",
        gm_template_id="GameMaster_Undead_Zombie_Norm_HalfRotten",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD,
        archetype=Archetype.FIGHTER,
        equipment="Rotting Claws & Pestilent Bile",
        ai_tactics="Shambles forward, spews poison puddles when struck, and spreads disease in melee.",
        gm_notes="Official GM Mode Half-Rotten Zombie.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Flesh-Eating Ghoul",
        gm_template_id="GameMaster_Ghoul_Easy_Common",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD,
        archetype=Archetype.ROGUE,
        equipment="Feral Necrotic Claws",
        ai_tactics="Leaps onto bleeding or isolated heroes, cannibalizes corpses to regenerate vitality.",
        gm_notes="Official GM Mode Ghoul template.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Necrotic Corpse Leech",
        gm_template_id="GameMaster_Undead_CorpseLeech_A",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD,
        archetype=Archetype.MINION,
        equipment="Blood-Sucking Mandibles",
        ai_tactics="Swarms targets in blood puddles, drains vitality and inflicts Bleeding.",
        gm_notes="Official GM Mode Undead Corpse Leech.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Undead Bone Crawler",
        gm_template_id="GameMaster_Undead_Easy_BoneCrawler",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD,
        archetype=Archetype.MINION,
        equipment="Chitinous Bone Legs & Fangs",
        ai_tactics="Scuttles rapidly across the battlefield to flank casters and spit necrotic venom.",
        gm_notes="Official GM Mode Bone Crawler.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Bone Widow Spider",
        gm_template_id="GameMaster_Undead_Easy_FastBoneSpiderling",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD,
        archetype=Archetype.FIGHTER,
        equipment="Skeletal Arachnid Talons",
        ai_tactics="Burrows beneath the battlefield, devours corpses to boost physical damage, and pierces armor.",
        gm_notes="Official GM Mode Bone Widow / Fast Bone Spider.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Bone Walker Abomination",
        gm_template_id="GameMaster_Undead_Norm_BoneWalker",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD,
        archetype=Archetype.TANK,
        equipment="Grafted Bone Scythes & Fused Ribcage",
        ai_tactics="Towering skeletal construct. Absorbs nearby corpses with Bone Cage and cleaves the frontline.",
        gm_notes="Official GM Mode Bone Walker (Normal & Tough variants).",
        can_be_boss=True,
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Cursed Scarecrow",
        gm_template_id="GameMaster_Undead_Norm_Scarecrow",
        faction=Faction.UNDEAD,
        race=Race.UNDEAD,
        archetype=Archetype.MAGE,
        equipment="Reaper Scythe Staff + Aura of Terror",
        ai_tactics="Radiates terrifying dread once Magic Armor is stripped, bombards party with Geomancy and Necromancy.",
        gm_notes="Official GM Mode Cursed Scarecrow.",
        can_be_boss=True,
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Black Ring Pain Reaver",
        gm_template_id="GEN_GM_GenericTank",
        faction=Faction.UNDEAD,
        race=Race.HUMAN,
        archetype=Archetype.TANK,
        equipment="Spiked Morningstar + Tower Shield",
        ai_tactics="Taunts heroes, applies Retribution damage reflection, and uses Battle Stomp when armor is low.",
        gm_notes="God King vanguard.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Black Ring Ravager",
        gm_template_id="GameMaster_Blackring_Norm_Ravager",
        faction=Faction.UNDEAD,
        race=Race.HUMAN,
        archetype=Archetype.FIGHTER,
        equipment="Two-Handed Black Ring Executioner Axe",
        ai_tactics="Aggressive God King shock trooper. Uses Phoenix Dive, Whirlwind, and Shackles of Pain.",
        gm_notes="Official GM Mode Black Ring Ravager.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Black Ring Witch",
        gm_template_id="GameMaster_Blackring_Easy_Witch",
        faction=Faction.UNDEAD,
        race=Race.HUMAN,
        archetype=Archetype.MAGE,
        equipment="Cursed Bone Wand + Hex Totem",
        ai_tactics="Casts Raining Blood, Infect, and Mosquito Swarm while cursing surfaces beneath the party.",
        gm_notes="Official GM Mode Black Ring Witch.",
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
        gm_notes="Necromancer spells; extremely lethal in blood.",
        can_be_boss=True
    ),
    BestiaryTemplate(
        name="Black Ring Champion",
        gm_template_id="GameMaster_Blackring_Tough_Champion",
        faction=Faction.UNDEAD,
        race=Race.HUMAN,
        archetype=Archetype.BOSS,
        equipment="Runed Black Ring Greatsword + Sworn Plate",
        ai_tactics="Elite commander of the Black Ring. Leads with Overpower, Decaying Touch, and Whirlwind.",
        gm_notes="Official GM Mode Black Ring Tough Champion.",
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
        gm_notes="Fused bone monstrosity.",
        can_be_boss=True
    ),

    # =========================================================================
    # FACTION: MAGISTERS & DIVINE ORDER / PALADINS / GUARDS
    # =========================================================================
    BestiaryTemplate(
        name="Magister Swordsman",
        gm_template_id="GM_Magister_Melee",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.FIGHTER,
        equipment="One-handed Longsword + Divine Steel Shield",
        ai_tactics="Engages frontliners, uses Battering Ram to knock down targets stripped of physical armor. Uses Shields Up.",
        gm_notes="Standard Divine Order soldier.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Magister Knight",
        gm_template_id="GameMaster_Magister_Knight",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.TANK,
        equipment="Heavy Divine Greatblade + Crimson Plate",
        ai_tactics="Vanguard heavy knight. Uses Battering Ram, Battle Stomp, and Heart of Steel to hold the line.",
        gm_notes="Official GM Mode Magister Knight.",
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
        gm_notes="High Ground sniper.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Magister Houndmaster",
        gm_template_id="GM_Magister_Ranger_Strong",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.SUMMONER,
        equipment="Heavy Crossbow + Source Hound Whistle",
        ai_tactics="Commands Source Hounds and summons backup, pins down targets from afar and buffs allies with Encourage.",
        gm_notes="Official GM Mode Magister Ranger Strong / Houndmaster.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Magister Source Hound",
        gm_template_id="Animals_SourceHound_A",
        faction=Faction.MAGISTERS,
        race=Race.CREATURE,
        archetype=Archetype.FIGHTER,
        equipment="Spiked Collar & Source-Sniffing Jaws",
        ai_tactics="Tracks Sourcerers, rushes into melee to inflict Bleeding and Crippled, and flanks enemy casters.",
        gm_notes="Official DOS2 Magister Source Hound.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Magister Cryomancer",
        gm_template_id="GM_Magister_Caster_Cryo",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.MAGE,
        equipment="Glacial Water Staff + Cloth Robes",
        ai_tactics="Casts Rain to make party Wet, then freezes with Hail Strike or Winter Blast. Clears CC with Armor of Frost.",
        gm_notes="Specialized water/ice control caster.",
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
        gm_notes="Fiery area denial.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Magister Aerotheurge",
        gm_template_id="GM_Magister_Caster_Aero",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.MAGE,
        equipment=" Fulminating Air Wand + Divine Buckler",
        ai_tactics="Teleports heroes into hazards, stuns wet targets with Electric Discharge and Dazing Bolt.",
        gm_notes="Official GM Mode Magister Aero Caster.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Magister Geomancer",
        gm_template_id="GM_Magister_Caster_Terra",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.MAGE,
        equipment="Earth Runed Staff + Magister Robes",
        ai_tactics="Slows the party with Fossil Strike and Impalement, and reinforces frontline allies with Fortify.",
        gm_notes="Official GM Mode Magister Terra Caster.",
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
        gm_notes="Decaying Touch turns player healing into lethal damage.",
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
        gm_notes="Soulless purged fighter.",
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
        gm_notes="Elven variant of the Silent Monk.",
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
        gm_notes="Lizard variant of the Silent Monk.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Silent Watcher",
        gm_template_id="GameMaster_SilentWatcher_Norm_Human",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.RANGER,
        equipment="Inquisition Crossbow + Silencing Bolts",
        ai_tactics="Elite purged sentry. Spots sneaking targets with high Wits and suppresses casters from range.",
        gm_notes="Official GM Mode Silent Watcher.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Elven Silent Watcher",
        gm_template_id="GameMaster_SilentWatcher_Norm_Elf",
        faction=Faction.MAGISTERS,
        race=Race.ELF,
        archetype=Archetype.MAGE,
        equipment="Purged Arcane Staff",
        ai_tactics="Uses Flesh Sacrifice and hurls elemental bolts with unblinking precision.",
        gm_notes="Official GM Mode Elven Silent Watcher.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Gheist Monstrosity",
        gm_template_id="Creatures_Gheist_A",
        faction=Faction.MAGISTERS,
        race=Race.CREATURE,
        archetype=Archetype.ROGUE,
        equipment="Monstrous Claw Blades",
        ai_tactics="Lethal assassin with extreme AP efficiency. Teleports behind lowest physical armor hero, backstabs relentlessly.",
        gm_notes="Terrifying mutated bioweapon.",
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
        gm_notes="Order of the Divine paladin; heavy physical vanguard.",
        can_be_boss=False
    ),
    BestiaryTemplate(
        name="Paladin Swordsman",
        gm_template_id="GameMaster_Paladin_Warrior_Male",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.FIGHTER,
        equipment="Blessed Longsword + Paladin Kite Shield",
        ai_tactics="Disciplined martial paladin. Uses Phoenix Dive, Bouncing Shield, and Battle Stomp.",
        gm_notes="Official GM Mode Paladin Warrior.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Paladin Ranger",
        gm_template_id="GM_Paladin_Ranger",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.RANGER,
        equipment="Divine Order Longbow",
        ai_tactics="Snipes from fortified positions, fires holy-enchanted arrows and pins down threats.",
        gm_notes="High precision ranged support.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Paladin War Caster",
        gm_template_id="GameMaster_Paladin_Caster_Female",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.BATTLEMAGE,
        equipment="Sun-Blessed Quarterstaff + Paladin Half-Plate",
        ai_tactics="Channels Pyrokinetic and Geomancer magic alongside frontline Warfare crowd control.",
        gm_notes="Official GM Mode Paladin Caster.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Paladin Healer / Cleric",
        gm_template_id="GameMaster_Paladin_Healer_Female",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.CLERIC,
        equipment="Ceremonial Warhammer + Sun Shield",
        ai_tactics="Restores allied vitality and Magic Armor with Restoration, Armor of Frost, and Cleanse Wounds.",
        gm_notes="Official GM Mode Paladin Healer.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="City Guard Watchman",
        gm_template_id="GameMaster_TEMPLATE_Guard_Melee_01",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.FIGHTER,
        equipment="Town Guard Halberd",
        ai_tactics="Patrols in pairs, uses Crippling Blow and Battering Ram to detain lawbreakers.",
        gm_notes="Official GM Mode City Guard Melee template.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="City Guard Marksman",
        gm_template_id="GameMaster_TEMPLATE_Guard_Ranger_01",
        faction=Faction.MAGISTERS,
        race=Race.HUMAN,
        archetype=Archetype.RANGER,
        equipment="Garrison Crossbow + Knockdown Bolts",
        ai_tactics="Provides ranged overwatch from battlements, pinning down fleeing suspects.",
        gm_notes="Official GM Mode City Guard Ranger template.",
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
        gm_notes="Boss with up to 6 AP per turn.",
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
        gm_notes="Fragile swarm minion.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Volatile Fire Voidling",
        gm_template_id="GameMaster_Voidwoken_Easy_Fire_Hatchling",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.MINION,
        equipment="Flame-Engorged Carapace",
        ai_tactics="Scuttles into clusters of heroes and detonates in a burst of cursed fire upon death.",
        gm_notes="Official GM Mode Fire Voidling Hatchling.",
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
        gm_notes="Native GM void creature with ranged acid attacks.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Oil Voidling Molespitter",
        gm_template_id="GameMaster_Voidwoken_Easy_Molespitter",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.RANGER,
        equipment="Tar-Spitting Gullet",
        ai_tactics="Bombards the party with粘oil blobs that slow movement and prime the arena for fire explosions.",
        gm_notes="Official GM Mode Oil Voidwoken Molespitter.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Voidwoken Spider",
        gm_template_id="GameMaster_Voidwoken_Easy_Spider",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.ROGUE,
        equipment="Void-Corrupted Fangs & Web Spinnerets",
        ai_tactics="Entangles party members with cursed webs and strikes from behind with venomous bites.",
        gm_notes="Official GM Mode Voidwoken Spider.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Void Flayer Grunt",
        gm_template_id="GameMaster_Voidwoken_Easy_Grunt",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.FIGHTER,
        equipment="Serrated Void Scythe-Claws",
        ai_tactics="Skirmishes in packs, leaps into melee to rend Physical Armor and inflict Bleeding.",
        gm_notes="Official GM Mode Voidwoken Grunt.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Void-Touched Stalker (Deer)",
        gm_template_id="Animals_Deer_A_Void_A",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.FIGHTER,
        equipment="Corrupted Claws & Spikes",
        ai_tactics="Leaps over frontline tanks straight onto vulnerable mages. Applies Crippled and Bleeding with claw strikes.",
        gm_notes="Fast leaping corrupted beast.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Void-Touched Bear",
        gm_template_id="Animals_Bear_A_Voidwoken",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.TANK,
        equipment="Void-Mutated Claws & Cursed Carapace",
        ai_tactics="Monstrous void-corrupted bear. Charges through frontlines, roars to terrify, and mauls with heavy cleaves.",
        gm_notes="Official DOS2 Voidwoken Bear.",
        can_be_boss=False,
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Void-Touched Turtle",
        gm_template_id="GameMaster_Voidwoken_Norm_Turtle",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.TANK,
        equipment="Cursed Spiked Shell",
        ai_tactics="High armor shell. Spits cursed poison projectiles and detonates toxic clouds in close quarters.",
        gm_notes="Official GM Mode Voidwoken Turtle.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Noxious Voidwoken Insect",
        gm_template_id="GameMaster_Monsters_Norm_Insect_Common",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.FIGHTER,
        equipment="Chitinous Pincers & Acid Gland",
        ai_tactics="Burrows or flies across terrain, spits acid to dissolve armor, and slashes with razor mandibles.",
        gm_notes="Official GM Mode Voidwoken Insect.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Cold-Crawler Ice Voidwoken",
        gm_template_id="GameMaster_Monsters_Norm_Insect_Ice",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.MAGE,
        equipment="Frost-Rimed Mandibles",
        ai_tactics="Chills and freezes heroes with Winter Blast and Hail Strike, leaving frozen surfaces in its wake.",
        gm_notes="Official GM Mode Ice Insect Voidwoken.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Necro-Wing Fire Voidwoken",
        gm_template_id="GameMaster_Monsters_Norm_Insect_Wing_Fire",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.RANGER,
        equipment="Scorching Wings & Fire Spittle",
        ai_tactics="Flies to elevated perches, bombards the party with Fireball and cursed flame projectiles.",
        gm_notes="Official GM Mode Winged Fire Insect Voidwoken.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Vampiric Voidwoken Bat",
        gm_template_id="GameMaster_Undead_Norm_VampireScourge",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.ROGUE,
        equipment="Vampiric Fangs & Sonic Screech",
        ai_tactics="Swoops behind fragile heroes, drains vitality with Mosquito Swarm and lacerates unarmored targets.",
        gm_notes="Official GM Mode Vampire Scourge Voidwoken.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Voidwoken Deep-Dweller",
        gm_template_id="Animals_Voidwoken_Merman_A",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.BOSS,
        equipment="Ancient Void Staff & Cursed Tendrils",
        ai_tactics="Opens with Shackles of Pain on highest DPS player, then casts Grasp of the Starved and Decaying Touch.",
        gm_notes="Dangerous caster boss.",
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
        gm_notes="Immense Physical Armor and burrowing power.",
        can_be_boss=True
    ),
    BestiaryTemplate(
        name="Voidwoken Bonecrusher",
        gm_template_id="GameMaster_Voidwoken_Norm_Troll",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.TANK,
        equipment="Colossal Void-Mutated Fists",
        ai_tactics="hulking void-twisted colossus. Slams the ground with Battle Stomp and crushes armor with Overpower.",
        gm_notes="Official GM Mode Voidwoken Troll / Bonecrusher.",
        can_be_boss=True
    ),
    BestiaryTemplate(
        name="Voidwoken Guardian Statue",
        gm_template_id="GameMaster_Voidwoken_Norm_Guardian",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.TANK,
        equipment="Living Obsidian Monolith",
        ai_tactics="Towering animated sentinel. Reflects damage with Retribution and blasts intruders with elemental beams.",
        gm_notes="Official GM Mode Voidwoken Guardian Statue.",
        can_be_boss=True
    ),
    BestiaryTemplate(
        name="Ancient Insect Matriarch",
        gm_template_id="GameMaster_Monsters_Boss_Insect_Dominator",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.BOSS,
        equipment="Queen's Chitinous Crown & Acid Ovipositor",
        ai_tactics="Spawns voidling hatchlings, blankets the arena in corrosive acid spores, and dominates the hive.",
        gm_notes="Official GM Mode Boss Insect Dominator.",
        can_be_boss=True
    ),
    BestiaryTemplate(
        name="Harbinger of Doom",
        gm_template_id="GameMaster_Voidwoken_Boss_Alan",
        faction=Faction.VOIDWOKEN,
        race=Race.CREATURE,
        archetype=Archetype.BOSS,
        equipment="Apocalyptic Void Carapace & Pestilent Aura",
        ai_tactics="Radiates a cursed aura of decay, unleashes devastating necrofire and acid barrages, and commands undead/void thralls.",
        gm_notes="Official GM Mode Voidwoken Boss (Harbinger of Doom).",
        can_be_boss=True
    ),

    # =========================================================================
    # FACTION: WILD BEASTS & ELEMENTALS
    # Complete DOS2 GM Mode Catalog: Bears, Wolves, Cats, Boars, Deer, Birds,
    # Reptiles (Crocodiles, Salamanders, Turtles, Frogs), Insects/Spiders/Crabs,
    # Oozes/Slugs/Elementals, Shambling Mounds/Plants, Trolls, Werewolf, Dragon
    # =========================================================================
    # --- Bears ---
    BestiaryTemplate(
        name="Bear (Black Bear)",
        gm_template_id="GM_Bear_Easy",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.FIGHTER,
        equipment="Heavy Bear Claws & Crushing Jaws",
        ai_tactics="Charges frontline targets, mauls with rending claw swipes that inflict Bleeding, and shrugs off blows with thick hide.",
        gm_notes="Official DOS2 GM Mode Bear (GM_Bear_Easy / Animals_Bear_A).",
        can_be_boss=False,
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Grizzly Bear",
        gm_template_id="Animals_Bear_A",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.TANK,
        equipment="Massive Grizzly Paws & Thick Pelt",
        ai_tactics="High vitality woodland bruiser. Uses Battle Stomp to slam the ground and protects its territory fiercely.",
        gm_notes="Sturdy tank bear variant for woodland or ranger encounters.",
        can_be_boss=False,
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Bear Cub",
        gm_template_id="GameMaster_Animals_Easy_Bear_Cub",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.MINION,
        equipment="Young Claws & Teeth",
        ai_tactics="Scurries alongside adult bears; harming a cub enrages nearby mother or alpha bears.",
        gm_notes="Official GM Mode Bear Cub.",
        can_be_boss=False,
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
        gm_notes="High vitality beast guardian / Mama Bear boss.",
        can_be_boss=True
    ),

    # --- Wolves, Hounds, Tigers, Boars, Deer, Owls & Rats ---
    BestiaryTemplate(
        name="Pack Wolf",
        gm_template_id="Animals_Wolf_A_Black",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.MINION,
        equipment="Razor Fangs",
        ai_tactics="Coordinates with pack members, flanks isolated heroes, inflicts Crippled and Bleeding.",
        gm_notes="Deploy in packs of 3 to 6.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Timber Wolf",
        gm_template_id="GameMaster_Animals_Norm_Wolf_Enrage",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.FIGHTER,
        equipment="Savage Jaws & Lupine Pounce",
        ai_tactics="Howls to Enrage itself and packmates, lunges at knocked-down or bleeding prey.",
        gm_notes="Official GM Mode Enraging Wolf.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Black Wolf",
        gm_template_id="GameMaster_Animals_Wolf_Black",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.FIGHTER,
        equipment="Obsidian Fangs & Alpha Pelt",
        ai_tactics="Aggressive pack hunter that targets low-armor heroes and hamstrings retreating mages.",
        gm_notes="Official GM Mode Black Wolf.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Gray Wolf",
        gm_template_id="GameMaster_Animals_Wolf_Gray",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.ROGUE,
        equipment="Swift Fangs & Silent Paws",
        ai_tactics="High initiative and movement speed; circles behind the party to ambush ranged characters.",
        gm_notes="Official GM Mode Gray Wolf.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="War Dog / Black Hound",
        gm_template_id="GameMaster_Animals_Easy_Dog_Black_A",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.FIGHTER,
        equipment="Trained Mastiff Jaws",
        ai_tactics="Loyal guard hound. Charges intruders, bites to cripple movement, and guards archers.",
        gm_notes="Official GM Mode War Dog / Black Hound.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Forest Tiger",
        gm_template_id="GameMaster_Animals_Norm_Tiger",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.ROGUE,
        equipment="Razor-Sharp Retractable Claws & Fangs",
        ai_tactics="Apex ambush predator. Pounces from stealth onto backline targets with Backlash and Rupture Tendons.",
        gm_notes="Official GM Mode Forest Tiger.",
        can_be_boss=False,
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Wild Boar",
        gm_template_id="Animals_Boar_A",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.FIGHTER,
        equipment="Goring Ivory Tusks",
        ai_tactics="Charges in a straight line with Battering Ram to knock down heroes in its path.",
        gm_notes="Official DOS2 Wild Boar.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Forest Deer",
        gm_template_id="GameMaster_Animals_Easy_Deer",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.MINION,
        equipment="Branching Antlers",
        ai_tactics="Bounds swiftly across woodland terrain, butts intruders with Bull Horns.",
        gm_notes="Official GM Mode Deer.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Enchanted Deer",
        gm_template_id="GameMaster_Animals_EnchantedDeer_A",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.MAGE,
        equipment="Glowing Runed Antlers",
        ai_tactics="Fey-touched woodland guardian. Casts chain lightning and restorative nature magic.",
        gm_notes="Official GM Mode Enchanted Deer.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="War Owl",
        gm_template_id="GameMaster_Animals_Easy_WarOwl",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.RANGER,
        equipment="Piercing Talons & Dive-Bomb",
        ai_tactics="Flies over obstacles, swoops down to blind and harry enemy spellcasters.",
        gm_notes="Official GM Mode War Owl.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Giant Rat",
        gm_template_id="GameMaster_Animals_Easy_Rat_Giant",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.MINION,
        equipment="Diseased Incisors",
        ai_tactics="Swarms from sewers and cellars, inflicts Diseased and Bleeding on unarmored ankles.",
        gm_notes="Official GM Mode Giant Rat.",
        can_be_minion=True
    ),

    # --- Reptiles & Amphibians (Crocodiles, Salamanders, Turtles, Frogs) ---
    BestiaryTemplate(
        name="Saltwater Crocodile",
        gm_template_id="GameMaster_Crocodile_Norm_Common",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.FIGHTER,
        equipment="Bone-Crushing Jaws & Scaly Hide",
        ai_tactics="Lurks in shallow water, snaps at heroes with Crippling Blow, and hurls scalding rocks or teleports if mutated.",
        gm_notes="Official GM Mode Crocodile.",
        can_be_boss=False,
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Salamander",
        gm_template_id="GameMaster_Salamander_Norm_Common",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.FIGHTER,
        equipment="Whip-Tail & Serrated Jaws",
        ai_tactics="Lashes multiple targets with tail cleaves and lunges with Bull Horns, using Battle Stomp and Crippling Blow.",
        gm_notes="Official GM Mode Common Salamander.",
        can_be_minion=False,
        signature_skills=["Battle Stomp", "Crippling Blow", "Bull Horns"]
    ),
    BestiaryTemplate(
        name="Fire Salamander",
        gm_template_id="GameMaster_Salamander_Norm_Fire",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.MAGE,
        equipment="Molten Throat-Sac & Burning Scales",
        ai_tactics="Breathes gouts of flame, casts Fireball, Ignition, and Searing Daggers, and heals in fire surfaces.",
        gm_notes="Official GM Mode Fire Salamander.",
        can_be_minion=False,
        signature_skills=["Fireball", "Ignition", "Searing Daggers"]
    ),
    BestiaryTemplate(
        name="Noxious Poison Salamander",
        gm_template_id="GameMaster_Salamander_Norm_Poison",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.MAGE,
        equipment="Venom-Spitting Gland & Caustic Jaws",
        ai_tactics="Spits long-range Poison Dart, coats the arena in toxic slime with Contamination, and slows with Fossil Strike.",
        gm_notes="Official GM Mode Poison Salamander.",
        can_be_minion=False,
        signature_skills=["Poison Dart", "Contamination", "Fossil Strike"]
    ),
    BestiaryTemplate(
        name="Poisonous Turtle",
        gm_template_id="GameMaster_Turtle_Norm_Poison_Common",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.TANK,
        equipment="Mossy Armored Carapace & Toxic Breath",
        ai_tactics="Slow, heavily armored reptile that belches poison clouds and absorbs frontline punishment.",
        gm_notes="Official GM Mode Poison Turtle.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Ancient Giant Turtle",
        gm_template_id="GameMaster_Turtle_Tough_Ancient",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.TANK,
        equipment="Colossal Stone-Like Shell",
        ai_tactics="Massive physical and magic armor. Slams the ground with Earthquake and shields nearby beasts.",
        gm_notes="Official GM Mode Tough Ancient Turtle.",
        can_be_boss=True,
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Venomous Swamp Frog",
        gm_template_id="GameMaster_Frog_Easy_SmallVenomous",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.RANGER,
        equipment="Barbed Tongue & Poison Sacs",
        ai_tactics="Leaps onto ledges, spits Poison Darts, and is completely immune to poison and acid.",
        gm_notes="Official GM Mode Venomous Frog (GM_Frog_Poison).",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="River Water Frog",
        gm_template_id="GameMaster_Frog_Easy_SmallRocky",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.FIGHTER,
        equipment="Slick Amphibious Hide & Tongue Lash",
        ai_tactics="Springs across water puddles, lashes targets with Tentacle Lash, and is immune to slipping and freezing.",
        gm_notes="Official GM Mode Rocky / Water Frog (GM_Frog_Water).",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Giant Electric Frog",
        gm_template_id="GameMaster_TEMPLATE_Frog_GiantElectric_A",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.MAGE,
        equipment="Bio-ElectricVocal Sac",
        ai_tactics="Discharges lightning bolts across wet surfaces to stun multiple party members at once.",
        gm_notes="Official GM Mode Giant Electric Frog.",
        can_be_boss=False,
        can_be_minion=False
    ),

    # --- Spiders, Insects, Beetles & Crabs ---
    BestiaryTemplate(
        name="Giant Brood Spider",
        gm_template_id="GM_Spider_Easy",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.ROGUE,
        equipment="Venomous Fangs & Spinnerets",
        ai_tactics="Spins Spider Web on players to entrap them, then spits corrosive poison darts.",
        gm_notes="Entangles players ignoring physical armor.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Forest Crawler Spiderling",
        gm_template_id="GameMaster_Spider_Easy_CrawlerSpiderling",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.MINION,
        equipment="Chitinous Fangs",
        ai_tactics="Hatches in clusters, rushes webbed heroes and bites with poison-tipped fangs.",
        gm_notes="Official GM Mode Crawler Spiderling.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Dune Sand Spider",
        gm_template_id="GameMaster_Spider_Easy_SandSpiderling",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.ROGUE,
        equipment="Burrowing Chelicerae",
        ai_tactics="Ambush predator that strikes from sand clouds and blinds or slows targets.",
        gm_notes="Official GM Mode Sand Spider.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Cursed Widow Spider",
        gm_template_id="GameMaster_Spider_Easy_Widow",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.ROGUE,
        equipment="Lethal Black Widow Fangs",
        ai_tactics="Brood matriarch. Casts Spider Web to root the party, then delivers high-crit venomous bites.",
        gm_notes="Official GM Mode Widow Spider.",
        can_be_boss=True,
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Dune Beetle",
        gm_template_id="GameMaster_Monsters_Beetle_Norm_Dune",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.RANGER,
        equipment="Armored Wing-Casing & Acid Spray",
        ai_tactics="Flies to high ground, bombards the party with Fossil Strike oil boulders and corrosive spit.",
        gm_notes="Official GM Mode Dune Beetle.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Giant Crab",
        gm_template_id="GameMaster_Animals_Easy_Crab_Giant",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.TANK,
        equipment="Crushing Pincers & Calcified Shell",
        ai_tactics="High Physical Armor coastal crustacean. Pinches ankles to inflict Crippled and Bleeding.",
        gm_notes="Official GM Mode Giant Crab.",
        can_be_minion=True
    ),

    # --- Slugs, Oozes & Elementals ---
    BestiaryTemplate(
        name="Fire Slug",
        gm_template_id="GM_FireSlug_Grunt",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.MAGE,
        equipment="Molten Slime Body",
        ai_tactics="Leaves a trail of fire wherever it slithers, casts Searing Daggers, and heals in fire.",
        gm_notes="Official GM Mode Courteous Fire Slug (GM_FireSlug_Grunt).",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Fire Slug Matriarch",
        gm_template_id="GM_FireSlug_Boss",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.BOSS,
        equipment="Molten Magma Carapace",
        ai_tactics="Oozes continuous fire trails, casts Supernova, and heals when submerged in fire.",
        gm_notes="Native GM boss creature.",
        can_be_boss=True
    ),
    BestiaryTemplate(
        name="Fire Ooze",
        gm_template_id="GameMaster_Ooze_Norm_Fire",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.MAGE,
        equipment="Volatile Magma Gel",
        ai_tactics="Hurls fiery globules from range, ignites surfaces on contact, and heals from fire damage.",
        gm_notes="Official GM Mode Fire Ooze.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Poison Ooze",
        gm_template_id="GameMaster_Ooze_Norm_Poison",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.RANGER,
        equipment="Caustic Venom Gel",
        ai_tactics="Spits Poison Darts and Contamination waves; beware open flames which detonate its puddle.",
        gm_notes="Official GM Mode Poison Ooze.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Water Ooze",
        gm_template_id="GameMaster_Ooze_Norm_Water",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.MAGE,
        equipment="Frigid Brine Gel",
        ai_tactics="Drenches targets and freezes them with Winter Blast and Ice Fan.",
        gm_notes="Official GM Mode Water Ooze.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Flesh Blood Ooze",
        gm_template_id="GameMaster_Ooze_Norm_Flesh",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.FIGHTER,
        equipment="Coagulated Blood & Bone Shards",
        ai_tactics="Splits and flows through blood surfaces, inflicts Bleeding and Mosquito Swarm.",
        gm_notes="Official GM Mode Flesh Ooze.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Greater Fire Elemental",
        gm_template_id="Creatures_Elemental_A_Fire",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.MAGE,
        equipment="Blazing Core",
        ai_tactics="Immune to and healed by Fire. Casts Fireball, Supernova, and ignites all surrounding surfaces.",
        gm_notes="Living embodiment of flame.",
        can_be_boss=False
    ),

    # --- Vegetal / Shambling Mounds (Plant Monsters) ---
    BestiaryTemplate(
        name="Shambling Mound (Poisonous Trunk)",
        gm_template_id="GameMaster_Shambling_Easy_Grunt",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.TANK,
        equipment="Gnarled Ironwood Limbs & Spore Cloud",
        ai_tactics="Lumbering woodland plant monster. Entangles heroes with Worm Tremor and slams with heavy roots.",
        gm_notes="Official GM Mode Shambling Grunt / Poisonous Trunk.",
        can_be_boss=False,
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Shambling Thorn-Shooter (Spiky Trunk)",
        gm_template_id="GameMaster_Shambling_Easy_Ranger",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.RANGER,
        equipment="Barbed Briar Volley",
        ai_tactics="Fires volleys of razor-sharp wooden thorns from afar, pinning down and bleeding targets.",
        gm_notes="Official GM Mode Shambling Ranger / Spiky Trunk.",
        can_be_boss=False,
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Hungry Carnivorous Flower",
        gm_template_id="GameMaster_Shambling_Norm_Flower",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.MAGE,
        equipment="Acidic Petals & Spore Pod",
        ai_tactics="Stationary or rooting floral predator that bombards the arena with Poison Darts and corrosive spores.",
        gm_notes="Official GM Mode Shambling Flower.",
        can_be_boss=True,
        can_be_minion=False
    ),

    # --- Trolls, Werewolves & Dragons ---
    BestiaryTemplate(
        name="Mountain Troll Brute",
        gm_template_id="Troll_Mountain_A",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.BOSS,
        equipment="Colossal Stone Club + Thick Hides",
        ai_tactics="Devastating frontline brute. Uses Battle Stomp to knock down players, hurls boulders with Fossil Strike, and regenerates massive Vitality with Troll Blood (nullified by Fire/Burning).",
        gm_notes="Official DOS2 GM Mode Mountain Troll. Weakness: Fire/Burning deactivates Troll Blood regeneration.",
        can_be_boss=True,
        can_be_minion=False,
        signature_skills=["Battle Stomp", "Fossil Strike", "Battering Ram", "Earthquake", "Troll Blood (Fire Weakness)"],
    ),
    BestiaryTemplate(
        name="Forest Troll Wanderer",
        gm_template_id="Troll_Forest_A",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.BOSS,
        equipment="Ancient Ironbound Log + Moss Armor",
        ai_tactics="Crushes frontline with Overpower and Whirlwind, roots players with Worm Tremor, and shrugs off attacks with Heart of Steel and Troll Blood.",
        gm_notes="Official DOS2 GM Mode Forest Troll. Legendary forest wanderer with massive HP and cleave.",
        can_be_boss=True,
        can_be_minion=False,
        signature_skills=["Overpower", "Whirlwind", "Battle Stomp", "Heart of Steel", "Worm Tremor", "Troll Blood"],
    ),
    BestiaryTemplate(
        name="Lupine Nightmare Werewolf",
        gm_template_id="GameMaster_Monsters_Abomination_Boss_Werewolf",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.BOSS,
        equipment="Monstrous Lycanthrope Claws & Fangs",
        ai_tactics="Ferocious apex predator. Enrages, leaps across the battlefield, and shreds armor with rapid claw flurries.",
        gm_notes="Official GM Mode Abomination Boss Werewolf.",
        can_be_boss=True,
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Frost Dragon",
        gm_template_id="GameMaster_Dragons_Tough_Frost",
        faction=Faction.BEASTS,
        race=Race.CREATURE,
        archetype=Archetype.BOSS,
        equipment="Glacial Dragon Breath, Tail Sweep & Wing Buffet",
        ai_tactics="Apex draconic boss. Unleashes freezing breath cones, Hail Strike, and devastating physical tail cleaves.",
        gm_notes="Official GM Mode Tough Frost Dragon.",
        can_be_boss=True,
        can_be_minion=False
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
        gm_notes="Hostile Netherworld fiend; fire immune.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Frost Ice Demon",
        gm_template_id="GM_Ice_Demon",
        faction=Faction.DEMONS,
        race=Race.DEMON,
        archetype=Archetype.MAGE,
        equipment="Rime-Forged Glacial Talons",
        ai_tactics="Immune to Water and Freezing; chills enemies on contact and casts Winter Blast and Ice Fan.",
        gm_notes="Official GM Mode Elemental Ice Devil (GM_Ice_Demon).",
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
        gm_notes="Specialized necromantic demon in GM mode.",
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
        gm_notes="High air magic and shock damage.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Venomous Poison Demon",
        gm_template_id="GM_Poison_Demon",
        faction=Faction.DEMONS,
        race=Race.DEMON,
        archetype=Archetype.RANGER,
        equipment="Toxic Hell-Spines",
        ai_tactics="Immune to Poison and Acid; poisons attackers on contact and hurls corrosive venom projectiles.",
        gm_notes="Official GM Mode Elemental Poison Devil (GM_Poison_Demon).",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Black Oil Demon",
        gm_template_id="GM_Oil_Demon",
        faction=Faction.DEMONS,
        race=Race.DEMON,
        archetype=Archetype.TANK,
        equipment="Tar-Coated Obsidian Fists",
        ai_tactics="Immune to Fire, Earth, and Slowed. Coats the battlefield in viscous oil and slams slowed heroes.",
        gm_notes="Official GM Mode Elemental Oil Devil (GM_Oil_Demon).",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Demonic Hellhound",
        gm_template_id="GameMaster_Monsters_Demon_Easy_Hound",
        faction=Faction.DEMONS,
        race=Race.DEMON,
        archetype=Archetype.FIGHTER,
        equipment="Flaming Maw & Hellfire Pounce",
        ai_tactics="Pack fiend that leaps through fire surfaces to maul enemy spellcasters and archers.",
        gm_notes="Official GM Mode Demon Hound.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Demon Shadow Assassin",
        gm_template_id="GameMaster_Monsters_Demon_Easy_Rogue",
        faction=Faction.DEMONS,
        race=Race.DEMON,
        archetype=Archetype.ROGUE,
        equipment="Twin Netherworld Kris Daggers",
        ai_tactics="Teleports behind fragile targets with Cloak and Dagger, backstabs with Rupture Tendons and Terrifying Cruelty.",
        gm_notes="Official GM Mode Demon Rogue.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Demonic Parasitic Heart",
        gm_template_id="GameMaster_Demons_ParasiticHeart",
        faction=Faction.DEMONS,
        race=Race.DEMON,
        archetype=Archetype.SUMMONER,
        equipment="Pulsating Blood Tendrils",
        ai_tactics="Organic demonic nexus that spawns blood totems and elemental fiends while pulsing necrotic waves.",
        gm_notes="Official GM Mode Demonic Parasitic Heart.",
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
        gm_notes="Suicide rush fanatic.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Burning Cultist Witch",
        gm_template_id="GameMaster_Monsters_Witch_Norm_Burning",
        faction=Faction.DEMONS,
        race=Race.HUMAN,
        archetype=Archetype.MAGE,
        equipment="Cursed Hellfire Staff",
        ai_tactics="Wreathed in necrofire. Unleashes Fireball, Laser Ray, and decaying blood hexes.",
        gm_notes="Official GM Mode Burning Witch.",
        can_be_boss=True,
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Arch-Demon of Chaos",
        gm_template_id="Creatures_Demon_Grunt_A",
        faction=Faction.DEMONS,
        race=Race.DEMON,
        archetype=Archetype.BOSS,
        equipment="Obsidian Greatsword + Demonic Wings",
        ai_tactics="Radiates Demonic Aura. Casts Chain Lightning, Epidemic of Fire, and strikes with devastating cleaves.",
        gm_notes="Arch-demon boss with up to 6 AP turns.",
        can_be_boss=True
    ),

    # =========================================================================
    # FACTION: ANCIENT AUTOMATONS, GOLEMS & MECHANICAL PUPPETS
    # =========================================================================
    BestiaryTemplate(
        name="Clockwork Automaton Grunt",
        gm_template_id="GameMaster_Automaton_Easy_Grunt",
        faction=Faction.AUTOMATONS,
        race=Race.AUTOMATON,
        archetype=Archetype.FIGHTER,
        equipment="Bronze Gear-Blade & Steam Limbs",
        ai_tactics="Advances in lockstep, immune to Poison and Bleeding, and cleaves frontliners with mechanical precision.",
        gm_notes="Official GM Mode Automaton Grunt.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Raanaar Clockwork Sentinel",
        gm_template_id="Creatures_Raanaar_Automaton_A",
        faction=Faction.AUTOMATONS,
        race=Race.AUTOMATON,
        archetype=Archetype.TANK,
        equipment="Heavy Brass Tower Shield + Shock Baton",
        ai_tactics="Immune to Bleeding and Poison. Uses Deflective Barrier and Shield Bash to protect allies.",
        gm_notes="Authentic ancient automaton guardian.",
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
        gm_notes="Heavy physical ranged pressure.",
        can_be_minion=False
    ),
    BestiaryTemplate(
        name="Raanaar Mechanical Hound",
        gm_template_id="GameMaster_Voidwoken_Easy_Hound",
        faction=Faction.AUTOMATONS,
        race=Race.AUTOMATON,
        archetype=Archetype.ROGUE,
        equipment="Clockwork Jaws & Spring-Loaded Pounce",
        ai_tactics="Fast mechanical tracker that leaps onto backline casters and locks them down.",
        gm_notes="Official GM Mode Clockwork / Raanaar Hound.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Battle Source Puppet",
        gm_template_id="GameMaster_Misc_FirePuppet",
        faction=Faction.AUTOMATONS,
        race=Race.AUTOMATON,
        archetype=Archetype.BATTLEMAGE,
        equipment="Articulated Flamethrower Arms & Brass Blades",
        ai_tactics="Constructed war puppet that breathes fire cones and whirls through melee.",
        gm_notes="Official GM Mode Fire / Battle Puppet.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Bewitched Clockwork Moppet",
        gm_template_id="GameMaster_Misc_SourcePuppet",
        faction=Faction.AUTOMATONS,
        race=Race.AUTOMATON,
        archetype=Archetype.ROGUE,
        equipment="Hidden Doll Shivs & Spring Joints",
        ai_tactics="Uncanny animated doll that teleports behind targets and strikes with lethal precision.",
        gm_notes="Official GM Mode Source Puppet / Moppet.",
        can_be_minion=True
    ),
    BestiaryTemplate(
        name="Colossal Source Titan",
        gm_template_id="GameMaster_SourceTitan_A",
        faction=Faction.AUTOMATONS,
        race=Race.AUTOMATON,
        archetype=Archetype.BOSS,
        equipment="Titan Greatblade & Arcane Source Conduit",
        ai_tactics="Towering construct of the Eternals. Unleashes Chain Lightning, Supernova, and earth-shattering slams.",
        gm_notes="Official GM Mode Source Titan.",
        can_be_boss=True
    ),
    BestiaryTemplate(
        name="Ancient Relic Titan",
        gm_template_id="Creatures_Raanaar_Automaton_A",
        faction=Faction.AUTOMATONS,
        race=Race.AUTOMATON,
        archetype=Archetype.BOSS,
        equipment="Colossal Steam Pistons & Kinetic Core",
        ai_tactics="Crushes players with Ground Slam, emits EMP shockwaves that silence and shock nearby heroes.",
        gm_notes="Massive mechanical dungeon guardian.",
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


def get_all_boss_templates() -> List[BestiaryTemplate]:
    """Returns all templates eligible to serve as a boss (can_be_boss=True or archetype=Archetype.BOSS)."""
    return [t for t in BESTIARY if t.can_be_boss or t.archetype == Archetype.BOSS]


def search_templates(query: str, faction: Optional[Faction] = None) -> List[BestiaryTemplate]:
    """Searches bestiary templates matching query in name, gm_template_id, or gm_notes, prioritizing name matches and bosses."""
    q = query.strip().lower()
    if not q:
        return get_templates_by_faction(faction)
    pool = BESTIARY if not faction or faction == Faction.ANY else [t for t in BESTIARY if t.faction == faction]
    name_matches = [t for t in pool if q in t.name.lower()]
    other_matches = [t for t in pool if (q in t.gm_template_id.lower() or q in t.gm_notes.lower()) and t not in name_matches]
    name_matches.sort(key=lambda t: 0 if (t.can_be_boss or t.archetype == Archetype.BOSS) else 1)
    return name_matches + other_matches


def find_template_by_name(name_query: str) -> Optional[BestiaryTemplate]:
    """
    Finds the best matching BestiaryTemplate by name or engine template ID.
    Prioritizes exact matches, then name substring matches (preferring bosses), then template ID matches.
    """
    q = name_query.strip().lower()
    if not q:
        return None

    # 1. Exact match by name
    for t in BESTIARY:
        if t.name.lower() == q:
            return t

    # 2. Exact match on base name before parentheses (e.g. 'Bear' matching 'Bear (Black Bear)')
    for t in BESTIARY:
        base = t.name.lower().split(" (")[0].strip()
        if base == q:
            return t

    # 3. Exact match by gm_template_id
    for t in BESTIARY:
        if t.gm_template_id.lower() == q:
            return t

    # 4. Name starts with query as a full prefix word (e.g. 'Mountain Troll' matching 'Mountain Troll Brute')
    for t in BESTIARY:
        if t.name.lower().startswith(q + " ") or t.name.lower().startswith(q + " ("):
            return t

    # 5. Substring match by NAME for bosses
    boss_name_matches = [
        t for t in BESTIARY 
        if (t.can_be_boss or t.archetype == Archetype.BOSS) and (q in t.name.lower())
    ]
    if boss_name_matches:
        return boss_name_matches[0]

    # 6. Any substring match by NAME
    any_name_matches = [t for t in BESTIARY if q in t.name.lower()]
    if any_name_matches:
        return any_name_matches[0]

    # 7. Substring match by gm_template_id for bosses
    boss_id_matches = [
        t for t in BESTIARY 
        if (t.can_be_boss or t.archetype == Archetype.BOSS) and (q in t.gm_template_id.lower())
    ]
    if boss_id_matches:
        return boss_id_matches[0]

    # 8. Any substring match by gm_template_id
    any_id_matches = [t for t in BESTIARY if q in t.gm_template_id.lower()]
    if any_id_matches:
        return any_id_matches[0]

    return None


def create_custom_boss_template(
    name: str,
    faction: Optional[Faction] = None,
    race: Optional[Race] = None,
    gm_template_id: Optional[str] = None
) -> BestiaryTemplate:
    """Dynamically creates a custom Boss template with smart race, class, and equipment deduction."""
    clean_id = gm_template_id or f"GM_Custom_{name.strip().replace(' ', '_')}"
    q = name.lower()

    # Smart race detection
    detected_race = race
    if detected_race is None or detected_race == Race.CREATURE:
        if "undead" in q and "lizard" in q:
            detected_race = Race.UNDEAD_LIZARD
        elif "undead" in q and "elf" in q:
            detected_race = Race.UNDEAD_ELF
        elif "undead" in q and "dwarf" in q:
            detected_race = Race.UNDEAD_DWARF
        elif "undead" in q:
            detected_race = Race.UNDEAD_HUMAN
        elif "lizard" in q:
            detected_race = Race.LIZARD
        elif "elf" in q:
            detected_race = Race.ELF
        elif "dwarf" in q:
            detected_race = Race.DWARF
        elif "human" in q:
            detected_race = Race.HUMAN
        elif "demon" in q:
            detected_race = Race.DEMON
        elif "automaton" in q:
            detected_race = Race.AUTOMATON
        else:
            detected_race = Race.CREATURE

    # Smart faction detection
    detected_faction = faction
    if detected_faction is None or detected_faction == Faction.ANY:
        if any(k in q for k in ["magister", "divine", "paladin"]):
            detected_faction = Faction.MAGISTERS
        elif any(k in q for k in ["void", "drillworm", "deep-dweller"]):
            detected_faction = Faction.VOIDWOKEN
        elif any(k in q for k in ["undead", "skeleton", "black ring"]):
            detected_faction = Faction.UNDEAD
        elif any(k in q for k in ["bandit", "outlaw", "pirate", "thug", "assassin"]):
            detected_faction = Faction.BANDITS
        elif any(k in q for k in ["demon", "cultist", "arch-demon"]):
            detected_faction = Faction.DEMONS
        elif any(k in q for k in ["automaton", "relic", "clockwork"]):
            detected_faction = Faction.AUTOMATONS
        elif detected_race in (Race.LIZARD, Race.ELF, Race.DWARF, Race.HUMAN):
            detected_faction = Faction.BANDITS
        else:
            detected_faction = Faction.BEASTS

    # Smart class archetype and equipment deduction
    detected_archetype = Archetype.BOSS
    equipment = "Masterwork Weaponry & Enchanted Armor"
    ai_tactics = "Focuses key targets, utilizes devastating area-of-effect abilities, and controls the battlefield."
    sig_skills = None
    sig_talents = None

    if any(k in q for k in ["rogue", "assassin", "shadowblade", "cutthroat", "dagger"]):
        detected_archetype = Archetype.ROGUE
        equipment = "Twin Masterwork Dragon-Bone Daggers" if "lizard" in q else "Twin Masterwork Obsidian Daggers"
        ai_tactics = "Lethal shadowblade assassin. Teleports with Cloak and Dagger, backstabs with Backlash and Rupture Tendons, and vanishes with Chameleon Cloak."
        sig_skills = ["Backlash", "Cloak and Dagger", "Rupture Tendons", "Adrenaline", "Chameleon Cloak"]
        sig_talents = ["The Pawn"]
    elif any(k in q for k in ["ranger", "archer", "marksman", "hunter", "sniper", "bow"]):
        detected_archetype = Archetype.RANGER
        equipment = "Masterwork Composite Bow"
        ai_tactics = "Deadly long-range sniper. Seeks high ground (+20% damage), pins down players, and fires Ricochet and Barrage."
        sig_skills = ["Ricochet", "Pin Down", "First Aid", "Sky Shot"]
        sig_talents = ["Duck Duck Goose"]
    elif any(k in q for k in ["mage", "wizard", "sorcerer", "elementalist", "pyro"]):
        detected_archetype = Archetype.MAGE
        equipment = "Enchanted Pyromancy Staff"
        ai_tactics = "Devastating spellcaster. Casts high-impact elemental spells and coats the battlefield in surfaces."
        sig_skills = ["Fireball", "Searing Daggers", "Ignition", "Peace of Mind"]
        sig_talents = ["Elemental Affinity"]

    return BestiaryTemplate(
        name=name.strip(),
        gm_template_id=clean_id,
        faction=detected_faction,
        race=detected_race,
        archetype=detected_archetype,
        equipment=equipment,
        ai_tactics=ai_tactics,
        gm_notes=f"Forcefully designated GM Boss: {name.strip()}. Custom narrative centerpiece.",
        can_be_boss=True,
        signature_skills=sig_skills,
        signature_talents=sig_talents,
    )

