"""
DOS2 Encounter Balancer - Skills & Spells Database
Curated repository of official DOS2 Definitive Edition skills organized by
school, level tier, AP cost, damage type, and status effects.
Includes DOS2 Racial Skills (Encourage, Flesh Sacrifice, Petrifying Touch, Dragon's Blaze, Play Dead).
"""

import re
from typing import List, Dict, Optional
from .models import Skill, Archetype, Race


SKILL_ENCOURAGE = Skill("Encourage", "Special", "Racial", 1, "Buff", "Inspires allies in 15m radius, granting +1 STR, +1 FIN, +1 INT, +2 CON.", "Encouraged")
SKILL_FLESH_SACRIFICE = Skill("Flesh Sacrifice", "Special", "Racial", 0, "Buff", "Gain +1 AP immediately and +10% damage bonus for 2 turns; creates blood surface.", "Flesh Sacrifice")
SKILL_PETRIFYING_TOUCH = Skill("Petrifying Touch", "Special", "Racial", 1, "Earth", "Touch target dealing earth damage and petrifying if magic armor is 0.", "Petrified")
SKILL_DRAGONS_BLAZE = Skill("Dragon's Blaze", "Special", "Racial", 1, "Fire", "Breathe a fiery cone dealing fire damage, setting Burning and igniting surfaces.", "Burning")
SKILL_PLAY_DEAD = Skill("Play Dead", "Special", "Racial", 0, "Utility", "Feign death, causing enemies to completely ignore you until you act.", "Playing Dead")


RACIAL_SKILLS: Dict[Race, Skill] = {
    Race.HUMAN: SKILL_ENCOURAGE,
    Race.ELF: SKILL_FLESH_SACRIFICE,
    Race.DWARF: SKILL_PETRIFYING_TOUCH,
    Race.LIZARD: SKILL_DRAGONS_BLAZE,
    Race.UNDEAD: SKILL_PLAY_DEAD,
    Race.UNDEAD_HUMAN: SKILL_PLAY_DEAD,
    Race.UNDEAD_ELF: SKILL_PLAY_DEAD,
    Race.UNDEAD_DWARF: SKILL_PLAY_DEAD,
    Race.UNDEAD_LIZARD: SKILL_PLAY_DEAD,
}


def get_racial_skills_for_race(race: Race) -> List[Skill]:
    """
    Returns authentic DOS2 Definitive Edition racial skills.
    In DOS2:
    - ALL Undead (Undead Human, Elf, Dwarf, Lizard, Generic) have 'Play Dead'.
    - In addition, Undead retain their biological race's signature racial skill:
      * Undead Elf: Play Dead + Flesh Sacrifice
      * Undead Dwarf: Play Dead + Petrifying Touch
      * Undead Lizard: Play Dead + Dragon's Blaze
      * Undead Human: Play Dead + Encourage
    - Living races have their signature racial skill:
      * Human: Encourage
      * Elf: Flesh Sacrifice
      * Dwarf: Petrifying Touch
      * Lizard: Dragon's Blaze
    """
    skills: List[Skill] = []
    is_undead = race in (
        Race.UNDEAD,
        Race.UNDEAD_HUMAN,
        Race.UNDEAD_ELF,
        Race.UNDEAD_DWARF,
        Race.UNDEAD_LIZARD,
    )
    
    # 1. Undead signature: Play Dead applies to all undead
    if is_undead:
        skills.append(SKILL_PLAY_DEAD)

    # 2. Biological heritage skills
    if race in (Race.HUMAN, Race.UNDEAD_HUMAN):
        skills.append(SKILL_ENCOURAGE)
    elif race in (Race.ELF, Race.UNDEAD_ELF):
        skills.append(SKILL_FLESH_SACRIFICE)
    elif race in (Race.DWARF, Race.UNDEAD_DWARF):
        skills.append(SKILL_PETRIFYING_TOUCH)
    elif race in (Race.LIZARD, Race.UNDEAD_LIZARD):
        skills.append(SKILL_DRAGONS_BLAZE)

    return skills


SKILLS_DATABASE: List[Skill] = [
    # === RACIAL SKILLS ===
    SKILL_ENCOURAGE,
    SKILL_FLESH_SACRIFICE,
    SKILL_PETRIFYING_TOUCH,
    SKILL_DRAGONS_BLAZE,
    SKILL_PLAY_DEAD,

    # === WARFARE ===
    Skill("Battering Ram", "Warfare", "Novice", 2, "Physical", "Rush forward in a line, dealing physical damage and knocking down enemies with no physical armor.", "Knocked Down"),
    Skill("Battle Stomp", "Warfare", "Novice", 2, "Physical", "Smash ground in a cone, clears surfaces and knocks down targets without physical armor.", "Knocked Down"),
    Skill("Crippling Blow", "Warfare", "Novice", 2, "Physical", "Strike target and adjacent enemies, crippling movement.", "Crippled"),
    Skill("Shields Up", "Warfare", "Novice", 2, "Utility", "Restores both physical and magic armor based on equipped shield.", "Armor Restored"),
    Skill("Bouncing Shield", "Warfare", "Novice", 2, "Physical", "Hurls shield at target, bouncing to another nearby enemy for heavy physical damage.", None),
    Skill("Whirlwind", "Warfare", "Adept", 2, "Physical", "Perform a 360-degree sweep dealing full weapon damage to all nearby foes.", None),
    Skill("Blitz Attack", "Warfare", "Adept", 2, "Physical", "Teleport-slash between two separate enemies.", None),
    Skill("Phoenix Dive", "Warfare", "Adept", 1, "Utility", "Leap to target destination creating a circle of fire at landing spot.", "Flaming Surface"),
    Skill("Deflective Barrier", "Warfare", "Adept", 2, "Utility", "Restores physical armor and deflects ranged projectiles back at attackers.", "Deflecting"),
    Skill("Overpower", "Warfare", "Expert", 2, "Physical", "Heavy hit; if attacker has more physical armor than target, completely destroys target's physical armor and knocks down.", "Knocked Down"),

    # === HUNTSMAN ===
    Skill("Ricochet", "Huntsman", "Novice", 2, "Physical", "Fire an arrow that hits a target and bounces to up to two nearby foes.", None),
    Skill("First Aid", "Huntsman", "Novice", 1, "Healing", "Heals target, removes Crippled, Blind, Silenced, Knocked Down, and Bleeding.", "Rested"),
    Skill("Pin Down", "Huntsman", "Novice", 2, "Physical", "Pin enemy in place with arrow, dealing damage and crippling them.", "Crippled"),
    Skill("Sky Shot", "Huntsman", "Adept", 2, "Physical", "Leap into the air to fire with simulated high-ground bonus even from low ground.", None),
    Skill("Tactical Retreat", "Huntsman", "Adept", 1, "Utility", "Teleport away to high ground and gain Haste for 1 turn.", "Hasted"),
    Skill("Ballistic Shot", "Huntsman", "Adept", 2, "Physical", "Fires long-range shot dealing +5% damage per meter of distance.", None),
    Skill("Marksman's Fang", "Huntsman", "Adept", 2, "Physical", "Straight-line shot that completely pierces and bypasses physical armor directly into Vitality.", "Piercing"),
    Skill("Arrow Spray", "Huntsman", "Expert", 3, "Physical", "Fire a cone of 16 arrows point-blank for devastating burst.", None),
    Skill("Arrow Storm", "Huntsman", "Master", 4, "Physical", "Call down a barrage of arrows over a huge area, obliterating groups.", None),

    # === SCOUNDREL ===
    Skill("Adrenaline", "Scoundrel", "Novice", 0, "Utility", "Gain +2 AP immediately this turn; lose -2 AP next turn.", "Adrenaline"),
    Skill("Backlash", "Scoundrel", "Novice", 1, "Physical", "Teleport behind target and backstab them with daggers.", "Backstab"),
    Skill("Throwing Knife", "Scoundrel", "Novice", 2, "Physical", "Hurl dagger at target at range, can backstab.", None),
    Skill("Chloroform", "Scoundrel", "Novice", 1, "Magic", "Destroys magic armor and puts target to sleep if stripped.", "Sleeping"),
    Skill("Cloak and Dagger", "Scoundrel", "Adept", 1, "Utility", "Teleport silently without breaking stealth or invisibility.", None),
    Skill("Rupture Tendons", "Scoundrel", "Adept", 2, "Physical", "Target takes heavy piercing bleed damage for every meter moved.", "Ruptured"),
    Skill("Corrupted Blade", "Scoundrel", "Adept", 3, "Physical", "Attack dealing damage, setting Decaying and Diseased.", "Decaying"),
    Skill("Fan of Knives", "Scoundrel", "Expert", 3, "Physical", "Hurl daggers at every enemy in radius, devastating against packed targets.", None),
    Skill("Mortal Blow", "Scoundrel", "Master", 4, "Physical", "Instantly kills target with <20% vitality, deals double damage from stealth.", None),

    # === PYROKINETIC ===
    Skill("Ignition", "Pyrokinetic", "Novice", 1, "Fire", "Ignite all enemies around caster, burning away magic armor.", "Burning"),
    Skill("Searing Daggers", "Pyrokinetic", "Novice", 2, "Fire", "Hurl 3 fiery daggers at multiple targets or surfaces.", "Burning"),
    Skill("Peace of Mind", "Pyrokinetic", "Novice", 1, "Buff", "Cures Blinded, Terrified, Charmed, Taunted, Sleeping, Enraged, Madness; grants stats & Wits.", "Clear-Minded"),
    Skill("Haste", "Pyrokinetic", "Novice", 1, "Buff", "Grants +1 AP per turn and +2m movement speed.", "Hasted"),
    Skill("Spontaneous Combustion", "Pyrokinetic", "Adept", 2, "Fire", "Consumes Burning and Necrofire on target for massive instant burst.", None),
    Skill("Fireball", "Pyrokinetic", "Adept", 2, "Fire", "Launch an explosive fireball dealing AoE fire damage and leaving fire surfaces.", "Burning"),
    Skill("Laser Ray", "Pyrokinetic", "Expert", 3, "Fire", "Draw a line of intense heat, dealing huge fire damage and blinding foes.", "Blind"),
    Skill("Supernova", "Pyrokinetic", "Expert", 3, "Fire", "Explode with extreme heat around caster dealing massive fire damage.", "Burning"),
    Skill("Epidemic of Fire", "Pyrokinetic", "Master", 3, "Fire", "Curse target with necrofire that branches and infects up to 5 enemies.", "Necrofire"),

    # === HYDROSOPHIST ===
    Skill("Restoration", "Hydrosophist", "Novice", 1, "Healing", "Heals target over 2 turns, cures Poisoned and Bleeding (damages Undead/Decaying).", "Regeneration"),
    Skill("Armor of Frost", "Hydrosophist", "Novice", 1, "Utility", "Restores Magic Armor and cures Frozen, Stunned, Petrified, Shocked, Chilled.", "Magic Shell"),
    Skill("Rain", "Hydrosophist", "Novice", 1, "Water", "Douses fires and makes all combatants Wet, creating water surfaces.", "Wet"),
    Skill("Hail Strike", "Hydrosophist", "Novice", 3, "Water", "Drop 3 ice shards dealing water damage and freezing surfaces.", "Chilled"),
    Skill("Winter Blast", "Hydrosophist", "Adept", 2, "Water", "Cone of freezing frost, chilling and freezing targets without magic armor.", "Frozen"),
    Skill("Soothing Cold", "Hydrosophist", "Adept", 2, "Utility", "Generates aura restoring magic armor to all nearby allies each turn.", "Soothing Cold"),
    Skill("Ice Fan", "Hydrosophist", "Expert", 3, "Water", "Fire 3 ice shards at targets, freezing wet enemies.", "Frozen"),
    Skill("Global Cooling", "Hydrosophist", "Expert", 1, "Water", "Instantly turn all water surfaces into slippery ice and chill enemies.", "Chilled"),
    Skill("Hail Storm", "Hydrosophist", "Master", 4, "Water", "Rain 20 gigantic hail strikes over a massive battlefield radius.", "Frozen"),

    # === AEROTHEURGE ===
    Skill("Electric Discharge", "Aerotheurge", "Novice", 2, "Air", "Zap target with electricity, shocking them.", "Shocked"),
    Skill("Shocking Touch", "Aerotheurge", "Novice", 1, "Air", "Melee electric shock, stuns shocked enemies without magic armor.", "Stunned"),
    Skill("Teleportation", "Aerotheurge", "Adept", 2, "Utility", "Teleport target enemy or ally up to 13m; target takes heavy physical fall damage.", None),
    Skill("Nether Swap", "Aerotheurge", "Adept", 1, "Utility", "Swap positions of two combatants.", None),
    Skill("Blinding Radiance", "Aerotheurge", "Adept", 1, "Air", "Aura of dazzling light dealing air damage and blinding nearby enemies.", "Blind"),
    Skill("Dazing Bolt", "Aerotheurge", "Adept", 3, "Air", "Thunderbolt striking an area, shocks and suffocates targets.", "Shocked"),
    Skill("Chain Lightning", "Aerotheurge", "Expert", 3, "Air", "Forking lightning striking up to 8 enemies in sequence, stunning wet foes.", "Stunned"),
    Skill("Thunderstorm", "Aerotheurge", "Master", 4, "Air", "Massive tempest striking random enemies with lightning bolts for 3 turns.", "Stunned"),

    # === GEOMANCER ===
    Skill("Fortify", "Geomancer", "Novice", 1, "Utility", "Restores Physical Armor, cures Poisoned, Bleeding, Burning, Acid, Decaying; grants immunity to teleportation.", "Fortified"),
    Skill("Fossil Strike", "Geomancer", "Novice", 2, "Earth", "Hurls rock creating sticky oil puddle and slowing enemies.", "Slowed"),
    Skill("Poison Dart", "Geomancer", "Novice", 2, "Poison", "Spit virulent poison dealing magic damage and poisoning target.", "Poisoned"),
    Skill("Contamination", "Geomancer", "Novice", 1, "Poison", "Turn blood and water surfaces around caster into deadly poison puddles.", "Poisoned"),
    Skill("Impalement", "Geomancer", "Adept", 2, "Earth", "Spikes erupt from ground dealing earth damage, slowing, and crippling foes without armor.", "Crippled"),
    Skill("Worm Tremor", "Geomancer", "Adept", 3, "Earth", "Summon earth worms entangling all targets, preventing movement and teleportation.", "Entangled"),
    Skill("Earthquake", "Geomancer", "Expert", 3, "Earth", "Shake battlefield violently, knocks down all enemies without physical armor.", "Knocked Down"),
    Skill("Pyroclastic Eruption", "Geomancer", "Master", 3, "Earth", "Launch oil boulders at all nearby enemies that explode for cataclysmic earth damage.", None),

    # === NECROMANCER ===
    Skill("Blood Sacrifice", "Necromancer", "Novice", 0, "Utility", "Lose a small amount of vitality to gain +1 AP and +10% damage bonus.", "Flesh Sacrifice"),
    Skill("Mosquito Swarm", "Necromancer", "Novice", 2, "Physical", "Summon blood-sucking insects that deal physical damage and heal caster.", "Bleeding"),
    Skill("Decaying Touch", "Necromancer", "Novice", 2, "Physical", "Touch that sets Decaying: all healing spells now deal direct piercing damage.", "Decaying"),
    Skill("Raining Blood", "Necromancer", "Adept", 2, "Physical", "Rain blood across battlefield, setting Bleeding and leaving blood surfaces.", "Bleeding"),
    Skill("Bone Cage", "Necromancer", "Adept", 1, "Utility", "Draw bone armor from corpses nearby to massively boost Physical Armor.", "Bone Armor"),
    Skill("Shackles of Pain", "Necromancer", "Adept", 3, "Utility", "Bind target: all damage received by caster is mirrored to the bound target.", "Shackled"),
    Skill("Living on the Edge", "Necromancer", "Expert", 3, "Utility", "Target cannot die or drop below 1 HP for 2 turns.", "Death Ward"),
    Skill("Grasp of the Starved", "Necromancer", "Expert", 2, "Physical", "Hands erupt from blood surfaces dealing huge physical damage and crippling foes.", "Crippled"),

    # === POLYMORPH ===
    Skill("Bull Horns", "Polymorph", "Novice", 1, "Physical", "Grow horns allowing Bull Rush charge attack each turn for 1 AP.", None),
    Skill("Tentacle Lash", "Polymorph", "Novice", 2, "Physical", "Lash enemy from range with tentacle, dealing physical damage and setting Atrophy (cannot attack).", "Atrophy"),
    Skill("Chameleon Cloak", "Polymorph", "Novice", 1, "Utility", "Turn completely invisible for 2 turns.", "Invisible"),
    Skill("Chicken Claw", "Polymorph", "Novice", 2, "Physical", "Turn target with no physical armor into a squawking chicken for 2 turns.", "Chicken Form"),
    Skill("Heart of Steel", "Polymorph", "Adept", 2, "Utility", "Gradually regenerates physical armor each turn.", "Steel Heart"),
    Skill("Spider Legs", "Polymorph", "Adept", 1, "Utility", "Spin webs trapping enemies, granting immunity to web slowing.", "Webbed"),
    Skill("Medusa Head", "Polymorph", "Adept", 2, "Earth", "Aura petrifying all enemies within range who have no magic armor.", "Petrified"),

    # === SUMMONING ===
    Skill("Conjure Incarnate", "Summoning", "Novice", 2, "Utility", "Summon a minion matching the surface element it was summoned upon.", None),
    Skill("Elemental Totem", "Summoning", "Novice", 2, "Utility", "Sprout a totem each turn that shoots elemental bolts matching ground surface.", None),
    Skill("Power Infusion", "Summoning", "Novice", 1, "Buff", "Grants Incarnate physical armor, Whirlwind, and Battering Ram.", "Infused"),
    Skill("Farsight Infusion", "Summoning", "Novice", 1, "Buff", "Grants Incarnate magic armor and ranged magic attack.", "Infused"),
    Skill("Shadow Infusion", "Summoning", "Adept", 1, "Buff", "Grants Incarnate invisibility and Corrupted Blade.", "Infused"),
    Skill("Warp Infusion", "Summoning", "Expert", 1, "Buff", "Grants Incarnate Tactical Retreat and Nether Swap.", "Infused"),
    # === TROLL RACIAL & SPECIAL ABILITIES ===
    Skill("Troll Blood", "Special", "Racial", 0, "Healing", "Innate Troll blood: rapidly regenerates massive vitality each round unless suppressed by elemental weakness.", "Troll Blood", memory_cost=0),
    Skill("Troll Blood (Fire Weakness)", "Special", "Racial", 0, "Healing", "Innate Mountain Troll blood: massive vitality regeneration each round; completely negated while Burning or in Necrofire.", "Troll Blood", memory_cost=0),
    Skill("Troll Blood (Poison Weakness)", "Special", "Racial", 0, "Healing", "Innate River/Cave Troll blood: massive vitality regeneration each round; completely negated while Poisoned or in Acid.", "Troll Blood", memory_cost=0),
    Skill("Boulder Toss", "Geomancer", "Novice", 2, "Earth", "Hurl a colossal boulder at the target area, dealing heavy earth damage and setting Crippled.", "Crippled"),
]


def is_skill_compatible_with_equipment(skill: Skill, equipment: Optional[str]) -> bool:
    """Verifies that the character's equipped gear fulfills the requirements of the skill."""
    if not equipment:
        return True
    eq_lower = equipment.lower()

    # Shield requirement: Shields Up, Bouncing Shield, Deflective Barrier
    shield_skills = {"Shields Up", "Bouncing Shield", "Deflective Barrier"}
    if skill.name in shield_skills:
        has_shield = any(w in eq_lower for w in ["shield", "buckler", "greatshield"])
        if not has_shield:
            return False

    # Dagger requirement
    dagger_skills = {"Backlash", "Throwing Knife", "Corrupted Blade", "Fan of Knives", "Mortal Blow"}
    if skill.name in dagger_skills:
        has_dagger = any(w in eq_lower for w in ["dagger", "daggers", "shiv", "shivs", "blade", "blades", "kris"])
        if not has_dagger:
            return False

    # Ranged weapon requirement (Bow / Crossbow)
    ranged_skills = {
        "Ricochet", "Pin Down", "Sky Shot", "Ballistic Shot", 
        "Marksman's Fang", "Arrow Spray", "Arrow Storm"
    }
    if skill.name in ranged_skills:
        has_ranged = any(w in eq_lower for w in ["bow", "crossbow", "ballista", "quiver"])
        if not has_ranged:
            return False

    # Melee weapon requirement
    melee_skills = {
        "Battering Ram", "Battle Stomp", "Crippling Blow", 
        "Whirlwind", "Blitz Attack", "Overpower"
    }
    if skill.name in melee_skills:
        is_pure_ranged = any(w in eq_lower for w in ["bow", "crossbow", "ballista"]) and not any(
            w in eq_lower for w in [
                "sword", "axe", "mace", "dagger", "knife", "blade", "spear", "glaive", 
                "fist", "claw", "waraxe", "battleaxe", "hammer", "scythe", "cleaver",
                "club", "trunk", "log", "boulder", "rock"
            ]
        )
        if is_pure_ranged:
            return False

    return True


def extract_skills_from_tactics(ai_tactics: Optional[str]) -> List[Skill]:
    """Extracts skills explicitly mentioned in the NPC's AI tactics description in order of occurrence."""
    if not ai_tactics:
        return []
    skill_map = {s.name.lower(): s for s in SKILLS_DATABASE}
    sorted_names = sorted(skill_map.keys(), key=lambda x: len(x), reverse=True)
    
    matches = []
    for name in sorted_names:
        pattern = r'\b' + re.escape(name) + r'\b'
        match = re.search(pattern, ai_tactics, re.IGNORECASE)
        if match:
            matches.append((match.start(), skill_map[name]))
            
    matches.sort(key=lambda x: x[0])
    result: List[Skill] = []
    for _, skill in matches:
        if skill not in result:
            result.append(skill)
    return result


def get_skills_for_archetype(
    archetype: Archetype,
    level: int,
    max_slots: int = 5,
    race: Optional[Race] = None,
    ai_tactics: Optional[str] = None,
    equipment: Optional[str] = None,
    signature_skills: Optional[List[str]] = None,
    class_archetype: Optional[Archetype] = None
) -> List[Skill]:
    """
    Selects an appropriate, thematic set of spells for a given archetype, level, and race.
    Prioritizes skills named in AI tactics and explicit signature skills,
    respects equipment requirements (e.g. Shields Up only with shields),
    and honors archetype school order (including Boss combat specializations).
    """
    allowed_tiers = ["Novice", "Racial"]
    if level >= 4:
        allowed_tiers.append("Adept")
    if level >= 9:
        allowed_tiers.append("Expert")
    if level >= 16:
        allowed_tiers.append("Master")

    school_preferences: Dict[Archetype, List[str]] = {
        Archetype.TANK: ["Warfare", "Geomancer", "Polymorph"],
        Archetype.FIGHTER: ["Warfare", "Polymorph", "Scoundrel"],
        Archetype.RANGER: ["Huntsman", "Pyrokinetic", "Scoundrel"],
        Archetype.ROGUE: ["Scoundrel", "Polymorph", "Warfare"],
        Archetype.MAGE: ["Pyrokinetic", "Geomancer", "Aerotheurge", "Hydrosophist"],
        Archetype.BATTLEMAGE: ["Warfare", "Aerotheurge", "Pyrokinetic"],
        Archetype.CLERIC: ["Hydrosophist", "Necromancer", "Warfare"],
        Archetype.SUMMONER: ["Summoning", "Pyrokinetic", "Hydrosophist"],
        Archetype.BOSS: ["Warfare", "Necromancer", "Aerotheurge", "Pyrokinetic"],
        Archetype.MINION: ["Warfare", "Geomancer"],
    }

    if archetype == Archetype.BOSS and class_archetype:
        prefs = school_preferences.get(class_archetype, school_preferences[Archetype.BOSS])
    else:
        prefs = school_preferences.get(archetype, ["Warfare"])
    
    # Candidate skills ordered by school preferences, filtered by equipment and tier
    candidate_skills: List[Skill] = []
    for school in prefs:
        for s in SKILLS_DATABASE:
            if s.school == school and s.tier != "Racial" and s.tier in allowed_tiers:
                if is_skill_compatible_with_equipment(s, equipment) and s not in candidate_skills:
                    candidate_skills.append(s)

    innate_selected: List[Skill] = []
    # 1. Racial / Innate abilities (DO NOT consume memorized skill slots)
    if race:
        for r_skill in get_racial_skills_for_race(race):
            if r_skill not in innate_selected:
                innate_selected.append(r_skill)

    # 2. Signature & AI Tactics skills
    tactics_candidates: List[Skill] = []
    if signature_skills:
        for s_name in signature_skills:
            matching = [s for s in SKILLS_DATABASE if s.name.lower() == s_name.lower()]
            if matching and matching[0] not in tactics_candidates:
                tactics_candidates.append(matching[0])

    if ai_tactics:
        for t_skill in extract_skills_from_tactics(ai_tactics):
            if t_skill not in tactics_candidates:
                tactics_candidates.append(t_skill)

    memorized_selected: List[Skill] = []
    for s in tactics_candidates:
        # If innate (e.g. Troll Blood or racial skill), add to innate_selected without consuming memory slots
        if s.is_innate:
            if s not in innate_selected:
                innate_selected.append(s)
            continue
        if len(memorized_selected) >= max_slots:
            break
        # Tier check: allow if tier is unlocked or for bosses (level 3+)
        tier_ok = (s.tier in allowed_tiers) or (archetype == Archetype.BOSS and level >= 3)
        if tier_ok and is_skill_compatible_with_equipment(s, equipment):
            if s not in memorized_selected:
                memorized_selected.append(s)

    # 3. Fill remaining slots: ensure utility then fill with attacks / candidates
    all_current = innate_selected + memorized_selected
    has_utility = any(s.damage_type in ("Utility", "Buff", "Healing") for s in all_current)
    utility_skills = [
        s for s in candidate_skills 
        if s.damage_type in ("Utility", "Buff", "Healing") and s not in memorized_selected and s not in innate_selected
    ]
    attack_skills = [
        s for s in candidate_skills 
        if s.damage_type not in ("Utility", "Buff", "Healing") and s not in memorized_selected and s not in innate_selected
    ]

    if not has_utility and utility_skills and len(memorized_selected) < max_slots:
        memorized_selected.append(utility_skills[0])
    
    for skill in attack_skills:
        if len(memorized_selected) >= max_slots:
            break
        if skill not in memorized_selected and skill not in innate_selected:
            memorized_selected.append(skill)
            
    for skill in candidate_skills:
        if len(memorized_selected) >= max_slots:
            break
        if skill not in memorized_selected and skill not in innate_selected:
            memorized_selected.append(skill)

    return innate_selected + memorized_selected[:max_slots]

