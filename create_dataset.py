import json
import random
import os

# Define vanilla Minecraft knowledge base
VANILLA_BLOCKS = [
    {"name": "stone", "tool": "pickaxe", "min_level": "wooden", "drops": "cobblestone"},
    {"name": "coal_ore", "tool": "pickaxe", "min_level": "wooden", "drops": "coal"},
    {"name": "iron_ore", "tool": "pickaxe", "min_level": "stone", "drops": "iron_ore", "needs_smelting": True},
    {"name": "gold_ore", "tool": "pickaxe", "min_level": "iron", "drops": "gold_ore", "needs_smelting": True},
    {"name": "diamond_ore", "tool": "pickaxe", "min_level": "iron", "drops": "diamond"},
    {"name": "redstone_ore", "tool": "pickaxe", "min_level": "iron", "drops": "redstone"},
    {"name": "lapis_ore", "tool": "pickaxe", "min_level": "stone", "drops": "lapis_lazuli"},
    {"name": "emerald_ore", "tool": "pickaxe", "min_level": "iron", "drops": "emerald"},
    {"name": "obsidian", "tool": "pickaxe", "min_level": "diamond", "drops": "obsidian"},
    {"name": "oak_log", "tool": "axe", "min_level": "none", "drops": "oak_log"},
    {"name": "spruce_log", "tool": "axe", "min_level": "none", "drops": "spruce_log"},
    {"name": "birch_log", "tool": "axe", "min_level": "none", "drops": "birch_log"},
    {"name": "jungle_log", "tool": "axe", "min_level": "none", "drops": "jungle_log"},
    {"name": "acacia_log", "tool": "axe", "min_level": "none", "drops": "acacia_log"},
    {"name": "dark_oak_log", "tool": "axe", "min_level": "none", "drops": "dark_oak_log"},
    {"name": "sand", "tool": "shovel", "min_level": "none", "drops": "sand"},
    {"name": "gravel", "tool": "shovel", "min_level": "none", "drops": ["gravel", "flint"]},
    {"name": "clay", "tool": "shovel", "min_level": "none", "drops": "clay_ball"},
    {"name": "dirt", "tool": "shovel", "min_level": "none", "drops": "dirt"},
    {"name": "grass_block", "tool": "shovel", "min_level": "none", "drops": "dirt"},
    {"name": "netherrack", "tool": "pickaxe", "min_level": "wooden", "drops": "netherrack"},
    {"name": "ancient_debris", "tool": "pickaxe", "min_level": "diamond", "drops": "ancient_debris"},
    {"name": "nether_quartz_ore", "tool": "pickaxe", "min_level": "wooden", "drops": "nether_quartz"}
]

# Vanilla Minecraft crafting recipes with actual ingredients
VANILLA_RECIPES = [
    {
        "name": "crafting_table",
        "ingredients": {"oak_planks": 4},
        "pattern": "2x2 square of planks",
        "station": "none"
    },
    {
        "name": "furnace",
        "ingredients": {"cobblestone": 8},
        "pattern": "all slots except center in crafting table",
        "station": "crafting_table"
    },
    {
        "name": "chest",
        "ingredients": {"oak_planks": 8},
        "pattern": "all slots except center in crafting table",
        "station": "crafting_table"
    },
    {
        "name": "wooden_pickaxe",
        "ingredients": {"oak_planks": 3, "stick": 2},
        "pattern": "planks in top row, sticks in middle of middle and bottom rows",
        "station": "crafting_table"
    },
    {
        "name": "stone_pickaxe",
        "ingredients": {"cobblestone": 3, "stick": 2},
        "pattern": "cobblestone in top row, sticks in middle of middle and bottom rows",
        "station": "crafting_table"
    },
    {
        "name": "iron_pickaxe",
        "ingredients": {"iron_ingot": 3, "stick": 2},
        "pattern": "iron ingots in top row, sticks in middle of middle and bottom rows",
        "station": "crafting_table"
    },
    {
        "name": "diamond_pickaxe",
        "ingredients": {"diamond": 3, "stick": 2},
        "pattern": "diamonds in top row, sticks in middle of middle and bottom rows",
        "station": "crafting_table"
    },
    {
        "name": "golden_pickaxe",
        "ingredients": {"gold_ingot": 3, "stick": 2},
        "pattern": "gold ingots in top row, sticks in middle of middle and bottom rows",
        "station": "crafting_table"
    },
    {
        "name": "netherite_pickaxe",
        "ingredients": {"diamond_pickaxe": 1, "netherite_ingot": 1},
        "pattern": "smithing table upgrade",
        "station": "smithing_table"
    },
    {
        "name": "wooden_axe",
        "ingredients": {"oak_planks": 3, "stick": 2},
        "pattern": "planks in top row and top-left, sticks in middle and bottom middle",
        "station": "crafting_table"
    },
    {
        "name": "stone_sword",
        "ingredients": {"cobblestone": 2, "stick": 1},
        "pattern": "cobblestone in top and middle rows, stick in bottom middle",
        "station": "crafting_table"
    },
    {
        "name": "iron_sword",
        "ingredients": {"iron_ingot": 2, "stick": 1},
        "pattern": "iron ingots in top and middle rows, stick in bottom middle",
        "station": "crafting_table"
    },
    {
        "name": "diamond_sword",
        "ingredients": {"diamond": 2, "stick": 1},
        "pattern": "diamonds in top and middle rows, stick in bottom middle",
        "station": "crafting_table"
    },
    {
        "name": "stick",
        "ingredients": {"oak_planks": 2},
        "pattern": "one plank above another",
        "station": "none"
    },
    {
        "name": "oak_planks",
        "ingredients": {"oak_log": 1},
        "pattern": "single log anywhere (creates 4 planks)",
        "station": "none"
    },
    {
        "name": "torch",
        "ingredients": {"coal": 1, "stick": 1},
        "pattern": "coal above stick",
        "station": "none"
    },
    {
        "name": "bed",
        "ingredients": {"wool": 3, "oak_planks": 3},
        "pattern": "3 wool in top row, 3 planks in middle row",
        "station": "crafting_table"
    },
    {
        "name": "shield",
        "ingredients": {"oak_planks": 6, "iron_ingot": 1},
        "pattern": "planks in all but center-left and center-right, iron ingot in center",
        "station": "crafting_table"
    },
    {
        "name": "bow",
        "ingredients": {"stick": 3, "string": 3},
        "pattern": "sticks in left column and middle right, string in right column minus bottom right",
        "station": "crafting_table"
    }
]

# Vanilla Minecraft mob information
VANILLA_MOBS = [
    {"name": "zombie", "hostile": True, "drops": ["rotten_flesh", "rarely: iron_ingot, carrot, potato"]},
    {"name": "skeleton", "hostile": True, "drops": ["bone", "arrow", "rarely: bow"]},
    {"name": "creeper", "hostile": True, "drops": ["gunpowder"]},
    {"name": "spider", "hostile": True, "drops": ["string", "rarely: spider_eye"]},
    {"name": "enderman", "hostile": True, "drops": ["ender_pearl"]},
    {"name": "witch", "hostile": True, "drops": ["glass_bottle", "glowstone_dust", "redstone", "spider_eye", "sugar", "stick"]},
    {"name": "cow", "hostile": False, "drops": ["leather", "beef"]},
    {"name": "sheep", "hostile": False, "drops": ["wool", "mutton"]},
    {"name": "chicken", "hostile": False, "drops": ["feather", "chicken", "egg"]},
    {"name": "pig", "hostile": False, "drops": ["porkchop"]},
    {"name": "wolf", "hostile": False, "tameable": True, "taming_item": "bone"}
]

# Biomes and locations
VANILLA_BIOMES = [
    "plains", "forest", "dark forest", "birch forest", "flower forest", "mountains", "desert", 
    "savanna", "badlands", "taiga", "snowy taiga", "jungle", "swamp", "ocean", "mushroom fields"
]

# Vanilla Minecraft game mechanics
VANILLA_MECHANICS = [
    {"name": "sleeping", "info": "Use a bed at night to skip to morning and reset spawn point"},
    {"name": "hunger", "info": "Food bar depletes over time, affecting health regeneration and ability to sprint"},
    {"name": "torch placement", "info": "Place torches to light areas and prevent hostile mob spawning"},
    {"name": "mob spawning", "info": "Hostile mobs spawn in darkness (light level 0-7) and neutral/passive mobs in light"},
    {"name": "farming", "info": "Till dirt with hoe, plant seeds, wait for growth, harvest crops"},
    {"name": "enchanting", "info": "Use enchanting table with lapis lazuli and experience levels to enhance items"},
    {"name": "brewing", "info": "Use brewing stand with blaze powder and ingredients to create potions"},
    {"name": "redstone", "info": "Create circuits and mechanisms with redstone dust and components"},
    {"name": "smelting", "info": "Use furnace with fuel to smelt items like ores into ingots"},
    {"name": "fishing", "info": "Use fishing rod near water to catch fish and other items"}
]

def generate_mining_examples(count=50):
    """Generate mining examples with specific Minecraft knowledge"""
    examples = []
    
    # Mining-related prompts
    prompts = [
        "mine that {block}",
        "get me some {block}",
        "I need {block}",
        "can you collect {block}",
        "harvest some {block} for me",
        "dig up that {block}"
    ]
    
    for _ in range(count):
        # Select a random block
        block_data = random.choice(VANILLA_BLOCKS)
        block_name = block_data["name"]
        
        # Select a random prompt and format it
        prompt = random.choice(prompts).format(block=block_name)
        
        # Generate thinking based on block properties
        thinking = f"""To mine {block_name}:
1. Need {block_data['tool']} (minimum: {block_data['min_level']})
2. Check if I have the right tool in my inventory
3. If not, I need to craft the appropriate tool first
4. Locate {block_name}"""

        # Add location hints for certain blocks
        if "ore" in block_name:
            if "nether" in block_name or block_name == "ancient_debris":
                thinking += f"\n   - Found in the Nether"
            elif block_name == "diamond_ore":
                thinking += f"\n   - Found at Y-levels 1-16, best at Y-11"
            elif block_name == "iron_ore":
                thinking += f"\n   - Found at Y-levels 1-63"
            elif block_name == "coal_ore":
                thinking += f"\n   - Found at Y-levels 0-127"
            elif block_name == "emerald_ore":
                thinking += f"\n   - Found only in mountain biomes"
        
        thinking += f"\n5. Mine the block with the correct tool"
        
        # Add information about what the block drops
        thinking += f"\n6. Collect {block_data['drops']}"
        
        # Add smelting information if needed
        if block_data.get("needs_smelting", False):
            thinking += f"\n7. Smelt {block_data['drops']} in a furnace to get {block_data['drops'].replace('_ore', '_ingot')}"
        
        # Generate response with specific Minecraft knowledge
        response = f"""<thinking>
{thinking}
</thinking>

I'll mine that {block_name} for you. Let me check if I have the right tool first.
<action>check_inventory("{block_data['min_level']}_{block_data['tool']}")</action>

[If I have the tool]:
I have a {block_data['min_level']} {block_data['tool']} or better. I'll mine the {block_name} now.
<action>mine("{block_name}")</action>"""

        # Add specific post-mining information
        if block_data.get("needs_smelting", False):
            response += f"""
I've mined the {block_name}. Now I need to smelt it in a furnace to get {block_data['drops'].replace('_ore', '_ingot')}.
<action>check_inventory("furnace")</action>
<action>check_inventory("fuel")</action>"""
        else:
            response += f"""
Got it! I've collected the {block_data['drops']}."""

        # Add tool crafting scenario
        response += f"""

[If I don't have the tool]:
I don't have a {block_data['min_level']} {block_data['tool']} or better, which I need to mine {block_name}. I should craft one first.
<action>check_recipe("{block_data['min_level']}_{block_data['tool']}")</action>
Should I gather materials to craft a {block_data['min_level']} {block_data['tool']}?"""

        examples.append({
            "instruction": prompt,
            "output": response
        })
    
    return examples

def generate_crafting_examples(count=50):
    """Generate crafting examples with real recipes"""
    examples = []
    
    # Crafting-related prompts
    prompts = [
        "craft a {item}",
        "make me a {item}",
        "I need a {item}",
        "can you build a {item}",
        "create a {item} for me"
    ]
    
    for _ in range(count):
        # Select a random recipe
        recipe = random.choice(VANILLA_RECIPES)
        item_name = recipe["name"]
        
        # Skip items that might be confused with Minecraft Dungeons
        if "dungeon" in item_name:
            continue
        
        # Select a random prompt and format it
        prompt = random.choice(prompts).format(item=item_name)
        
        # Generate thinking based on recipe
        thinking = f"""To craft {item_name}:

Required materials:"""
        
        # Add ingredients with counts
        for ingredient, count in recipe["ingredients"].items():
            thinking += f"\n- {count}x {ingredient}"
        
        # Add crafting station requirement
        if recipe["station"] != "none":
            thinking += f"\n\nNeeds {recipe['station']} to craft"
        
        # Add crafting pattern
        thinking += f"\n\nPattern: {recipe['pattern']}"
        
        # Add prerequisite crafting if needed
        if "planks" in str(recipe["ingredients"]) and item_name != "oak_planks":
            thinking += "\n\nPrerequisites:\n- Oak logs → Oak planks"
        
        if "stick" in str(recipe["ingredients"]) and item_name != "stick":
            thinking += "\n- Oak planks → Sticks"
        
        # Generate response with specific Minecraft recipe knowledge
        response = f"""<thinking>
{thinking}
</thinking>

I'll craft a {item_name} for you. First, let me check if I have all the materials.
"""
        
        # Add checks for each ingredient
        for ingredient, count in recipe["ingredients"].items():
            response += f"<action>check_inventory(\"{ingredient}\", min_count={count})</action>\n"
        
        # Add crafting station check if needed
        if recipe["station"] != "none":
            response += f"<action>check_inventory(\"{recipe['station']}\")</action>\n"
        
        # Add success scenario
        response += f"""
[If I have all materials]:
Great! I have all the materials needed."""
        
        # Add crafting station interaction if needed
        if recipe["station"] != "none":
            response += f"""
Let me use the {recipe['station']}.
<action>use(\"{recipe['station']}\")</action>"""
        
        response += f"""
Crafting the {item_name} now.
<action>craft(\"{item_name}\")</action>
Done! I've crafted a {item_name} for you.

[If I'm missing materials]:
I don't have all the materials needed to craft a {item_name}. """
        
        # Add specific material gathering suggestions
        if "wood" in item_name or "planks" in str(recipe["ingredients"]):
            response += "I need to chop some trees to get logs and craft planks."
        elif "stone" in item_name or "cobblestone" in str(recipe["ingredients"]):
            response += "I need to mine some stone to get cobblestone."
        elif "iron" in item_name:
            response += "I need to mine and smelt iron ore to get iron ingots."
        elif "diamond" in item_name:
            response += "I need to mine some diamond ore, which is found deep underground at Y-levels 1-16."
        else:
            response += "Should I gather the missing materials first?"

        examples.append({
            "instruction": prompt,
            "output": response
        })
    
    return examples

def generate_navigation_examples(count=50):
    """Generate navigation examples with Minecraft-specific hazards and environments"""
    examples = []
    
    # Basic navigation prompts
    basic_prompts = [
        "come here",
        "follow me",
        "come to me",
        "over here",
        "teleport to me"
    ]
    
    # Location-specific navigation prompts
    location_prompts = [
        "explore that cave",
        "go to the village",
        "check out that desert temple",
        "investigate that ruined portal",
        "explore that mineshaft",
        "climb that mountain",
        "go to the nether fortress",
        "search that shipwreck",
        "explore that jungle temple",
        "check out that woodland mansion",
        "go to the stronghold",
        "dive into that ocean monument"
    ]
    
    # Generate basic navigation examples
    for _ in range(count // 2):
        prompt = random.choice(basic_prompts)
        
        if "teleport" in prompt:
            thinking = """This is a request for immediate teleportation:
1. Need to get player's exact coordinates
2. Use teleport command to instantly move there
3. This requires appropriate server permissions or game mode"""

            response = f"""<thinking>
{thinking}
</thinking>

Teleporting to you now.
<action>teleport_to_player</action>
I've teleported to your location."""
        else:
            thinking = """This is a request to move to the player's location:
1. Need to identify player's current position
2. Find a path to reach the player
3. Avoid hazards along the way (lava, deep drops, hostile mobs)
4. Use pathfinding to navigate complex terrain
5. Maintain a reasonable following distance"""

            response = f"""<thinking>
{thinking}
</thinking>

I'll come to you right away.
<action>locate_player</action>
<action>navigate_to_player</action>
Moving to your location now. I'll watch out for any hazards on the way."""

        examples.append({
            "instruction": prompt,
            "output": response
        })
    
    # Generate location-specific navigation examples
    for _ in range(count - (count // 2)):
        prompt = random.choice(location_prompts)
        
        # Customize thinking and response based on location type
        if "cave" in prompt:
            thinking = """Exploring a cave requires:
1. Proper equipment:
   - Torches for light and to prevent mob spawning
   - Weapons for protection against hostile mobs
   - Pickaxe for mining resources
   - Food for hunger restoration
2. Hazard awareness:
   - Watch for drops into lava or deep pits
   - Listen for mob sounds (zombies, skeletons, creepers)
   - Mark path with torches to avoid getting lost
   - Be cautious of cave-ins from gravel or sand
3. Resource identification:
   - Look for valuable ores (coal, iron, gold, diamond, redstone)
   - Note the location of rare resources
   - Watch for mob spawners, mineshafts, or other structures"""

            response = f"""<thinking>
{thinking}
</thinking>

I'll explore that cave. Let me check my inventory for essentials first.
<action>check_inventory("torch", min_count=12)</action>
<action>check_inventory("weapon")</action>
<action>check_inventory("pickaxe")</action>
<action>check_inventory("food")</action>

[If well-equipped]:
I have the necessary equipment. I'll explore the cave now.
<action>navigate_to("cave")</action>
I'm placing torches as I go to mark our path and prevent mobs from spawning. I'll watch for valuable ores and be careful of hazards like lava pools and hostile mobs.

[If missing equipment]:
I'm not fully prepared to explore the cave. I should get some torches, a weapon, and a pickaxe first. Caves can be dangerous with hostile mobs and hazards like lava."""

        elif "village" in prompt:
            thinking = """Going to a village involves:
1. Finding the village:
   - Villages spawn in plains, desert, savanna, taiga, and snowy tundra biomes
   - Look for structures like houses, farms, and wells
2. Village features:
   - Villagers with different professions (farmer, librarian, etc.)
   - Trading opportunities using emeralds
   - Farms with crops (wheat, carrots, potatoes)
   - Iron golems for protection
3. Considerations:
   - Protect villagers from zombies at night
   - Avoid hitting villagers or iron golems
   - Respect villagers' beds and workstations"""

            response = f"""<thinking>
{thinking}
</thinking>

I'll head to the village.
<action>navigate_to("village")</action>
On my way to the village. When we get there, we can trade with villagers, gather crops from their farms, or use their crafting stations. I'll be careful not to harm any villagers or iron golems."""

        elif "nether" in prompt:
            thinking = """Going to the Nether Fortress requires:
1. First, be in the Nether dimension
2. Nether Fortress identification:
   - Large structures made of nether brick
   - Contains hallways, bridges, and staircases
   - Home to blazes and wither skeletons
3. Hazards:
   - Blaze spawners and their fireballs
   - Wither skeletons with wither effect
   - Ghasts in open areas
   - Lava oceans below
4. Important resources:
   - Blaze rods (needed for brewing stands and End portal)
   - Nether wart (base for most potions)
   - Wither skeleton skulls (for summoning the Wither)"""

            response = f"""<thinking>
{thinking}
</thinking>

I'll head to the Nether Fortress.
<action>check_dimension</action>

[If in Overworld]:
We need to go through a Nether Portal first to reach the Nether. Do you have an active portal nearby?

[If in Nether]:
<action>navigate_to("nether_fortress")</action>
Searching for the Nether Fortress. They're characterized by their dark nether brick structures. We should be careful of blazes and wither skeletons once we find it. I'll look for valuable resources like blaze rods and nether wart."""

        elif "temple" in prompt or "monument" in prompt or "mansion" in prompt or "portal" in prompt or "shipwreck" in prompt:
            structure_type = next((s for s in ["temple", "monument", "mansion", "portal", "shipwreck"] if s in prompt), "structure")
            
            thinking = f"""Exploring a {structure_type} requires:
1. Structure identification:
   - {structure_type.capitalize()}s have distinct appearances and generation patterns
   - They contain unique features and loot
2. Hazards specific to this structure:
   - Potential traps or puzzles
   - Possible hostile mobs
   - Environmental dangers
3. Valuable loot possibilities:
   - Rare items or resources
   - Unique blocks or decorations
   - Treasure chests"""

            response = f"""<thinking>
{thinking}
</thinking>

I'll explore that {structure_type}.
<action>navigate_to("{structure_type}")</action>
I'm on my way to the {structure_type}. I'll be careful of potential traps or hostile mobs, and I'll look for valuable loot inside."""

        examples.append({
            "instruction": prompt,
            "output": response
        })
    
    return examples

def generate_conversation_examples(count=50):
    """Generate conversation examples with accurate Minecraft knowledge"""
    examples = []
    
    # Predefined high-quality conversation examples
    conversations = [
        {
            "instruction": "what's your favorite thing in minecraft?", 
            "output": "I really enjoy exploring caves! There's something thrilling about venturing into the darkness, placing torches as you go, and discovering a rich vein of diamonds or a sprawling mineshaft. I also love building automated farms and redstone contraptions - it's satisfying to create systems that work efficiently. What about you? What do you enjoy most in Minecraft?"
        },
        
        {
            "instruction": "how do you survive the first night?", 
            "output": "To survive your first night in Minecraft:\n\n1. Punch trees to collect wood (at least 12-16 blocks)\n2. Craft a crafting table and wooden tools (especially a pickaxe)\n3. Find stone and mine it to make stone tools\n4. Gather food - kill animals or collect berries/apples\n5. Mine coal for torches if you find it\n6. Before sunset, either:\n   - Dig a small shelter into a hillside\n   - Build a simple hut with a door\n   - Pillar up high and wait out the night\n7. Place torches inside your shelter to prevent mob spawning\n8. Craft a bed if possible (requires 3 wool from sheep and 3 planks)\n\nThe key is to have a secure, well-lit shelter before darkness falls, when hostile mobs like zombies, skeletons, and creepers will start spawning."
        },
        
        {
            "instruction": "what's the best way to find diamonds?", 
            "output": "The most efficient way to find diamonds in Minecraft:\n\n1. Mine at Y-level 11-12 (press F3 to see your coordinates)\n   - Diamonds spawn between Y-levels 1-16\n   - Y-11 keeps you just above lava lake level (Y-10)\n\n2. Use the strip mining technique:\n   - Dig a main tunnel\n   - Branch out with 1-block wide tunnels\n   - Space branches 3 blocks apart for maximum efficiency\n\n3. Bring the right tools:\n   - Iron or diamond pickaxe (required for diamond ore)\n   - Water bucket (for lava encounters)\n   - Torches for lighting\n   - Food and weapons for safety\n\n4. Look for exposed diamonds in ravines and caves at the right depth\n\n5. For maximum yield, use a Fortune III enchanted pickaxe when mining diamonds\n\nCave exploring at the right depth can also be effective, especially with the new larger cave systems in recent updates."
        },
        
        {
            "instruction": "how do I tame a wolf?", 
            "output": "To tame a wolf in Minecraft:\n\n1. Find wolves in forest, taiga, or giant tree taiga biomes\n\n2. Collect bones (dropped by skeletons) - bring at least 5-6 as success isn't guaranteed\n\n3. Approach the wolf slowly and right-click it with a bone in hand\n   - You'll see hearts appear if successful\n   - It might take several bones before taming succeeds\n   - The wolf's tail will rise and collar will appear when tamed\n\n4. Once tamed:\n   - The wolf becomes your loyal dog\n   - Right-click to make it sit/stand\n   - It will follow you when standing\n   - It will attack mobs that attack you\n   - You can heal it with any meat\n   - You can dye its collar different colors\n\nBe careful not to hit wolves, as they'll become hostile and attack in packs!"
        },
        
        {
            "instruction": "what's the best enchantment for a sword?", 
            "output": "The best enchantments for a Minecraft sword depend on your purpose, but here's a comprehensive setup:\n\n1. Essential combat enchantments:\n   - Sharpness V (increases damage against all mobs)\n   - Unbreaking III (increases durability)\n   - Mending (repairs using XP)\n   - Looting III (better mob drops)\n\n2. Defensive enchantments:\n   - Knockback II (pushes enemies back)\n   - Fire Aspect II (sets enemies on fire)\n\n3. Specialized alternatives:\n   - Smite V instead of Sharpness (extra damage against undead mobs)\n   - Bane of Arthropods V instead of Sharpness (extra damage against spiders, silverfish)\n\nNote that Sharpness, Smite, and Bane of Arthropods are mutually exclusive.\n\nFor PVP combat, many players prefer Sharpness, Knockback, and Fire Aspect.\nFor fighting the Wither or in zombie-heavy areas, Smite is actually more powerful than Sharpness."
        },
        
        {
            "instruction": "how do I find a woodland mansion?", 
            "output": "Finding a Woodland Mansion in Minecraft is challenging as they're extremely rare. Here's how to locate one:\n\n1. Easiest method: Purchase a Woodland Explorer Map\n   - Find a cartographer villager (white coat)\n   - Level them up to journeyman level (may require trading paper and compasses)\n   - Trade emeralds for the Woodland Explorer Map\n   - The map will show the location of the nearest mansion\n\n2. Without a map:\n   - They spawn only in Dark Forest biomes\n   - These mansions are extremely rare and can be thousands of blocks away\n   - Extensive exploration is required\n\n3. Using commands (if allowed):\n   - /locate mansion\n   - This will give you coordinates to the nearest mansion\n\n4. Be prepared before going:\n   - Bring good armor and weapons\n   - Pack plenty of food and torches\n   - The mansion contains hostile mobs and Vindicators/Evokers\n\nWoodland Mansions are worth finding for their unique loot and to battle Evokers, which drop Totems of Undying."
        },
        
        {
            "instruction": "what should I do if I get lost in the nether?", 
            "output": "If you're lost in the Nether, here are strategies to find your way back:\n\n1. Check your coordinates (press F3)\n   - Note your X and Z coordinates\n   - In the Overworld, 1 block = 8 blocks in the Nether\n   - Divide Overworld coordinates by 8 to find equivalent Nether position\n\n2. Follow your trail\n   - Look for torches, cobblestone markers, or other blocks you placed\n   - Create bridges or paths when exploring to mark your route\n\n3. Create a new portal\n   - If you have obsidian (10 blocks) and flint and steel, build a new portal\n   - This creates a new exit but might be far from your base\n\n4. Use a lodestone compass\n   - If you have a lodestone set up near your portal, a compass linked to it will point the way\n\n5. Last resort\n   - If you have valuable items, put them in a chest and note coordinates\n   - Use the death respawn as a way back (you'll lose XP though)\n\nFor future Nether exploration:\n- Always bring obsidian and flint and steel\n- Create cobblestone markers or place torches systematically\n- Build a safe path from your portal"
        },
        
        {
            "instruction": "how do I make an automatic farm?", 
            "output": "Here's how to build a basic automatic crop farm in Minecraft:\n\n1. Water-harvesting crop farm:\n   - Create a 9x9 plot of farmland (till dirt with hoe)\n   - Place water in the center block\n   - Plant crops in the remaining 80 blocks\n   - Place a hopper beneath the water block connected to a chest\n   - When crops are grown, break the water source temporarily\n   - The water will flow out, breaking crops and washing items to the hopper\n\n2. Observer-based farm:\n   - Build a row of farmland\n   - Place water source at one end behind a piston\n   - Plant crops\n   - Place observers watching the crops\n   - Connect observers to the piston with redstone\n   - When crops grow fully, observer detects the change and triggers water flow\n\n3. Villager-powered farm:\n   - Create a platform with farmland\n   - Place a farmer villager who can't leave the area\n   - Add a second platform below with hoppers leading to chests\n   - The villager will plant and harvest crops, but can't pick up all items\n   - Items fall through gaps to the collection system\n\nFor animal farms, you can use water streams to push them to a collection point, or use breeding mechanics with trapdoors for baby animals."
        },
        
        {
            "instruction": "do you play on peaceful or hard mode?", 
            "output": "I find survival mode on Normal difficulty to be the most balanced experience. It provides a good challenge with hostile mobs and hunger management, but isn't as punishing as Hard mode where zombies can break doors and hunger depletes faster.\n\nPeaceful has its place too - it's great for focusing on building projects without interruptions. Sometimes I'll switch to Peaceful temporarily when building something complex, then return to Normal for the regular gameplay experience.\n\nWhat difficulty do you usually play on? Do you prefer the challenge of Hard mode or the building focus of Peaceful?"
        },
        
        {
            "instruction": "what's the fastest way to get to the end?", 
            "output": "The fastest way to reach The End in Minecraft:\n\n1. Find a stronghold\n   - Craft Eyes of Ender (Blaze Powder + Ender Pearl)\n   - Throw Eyes of Ender and follow their direction\n   - Dig down when Eyes start dropping to find the stronghold\n\n2. Locate the End Portal room\n   - Search through the stronghold for the portal room\n   - Look for the stone brick room with stairs and a silverfish spawner\n   - The portal frame is made of 12 End Portal Frames with a lava pool underneath\n\n3. Activate the portal\n   - Place Eyes of Ender in any empty portal frames\n   - You need up to 12 Eyes (some frames may already have Eyes)\n   - Portal activates when all frames are filled\n\nFor speedrunners, additional strategies include:\n- Village speedrunning (find a village for food and resources)\n- Nether fortress rushing (to quickly obtain Blaze Rods)\n- Enderman farming in warped forests (for Ender Pearls)\n- Using beds to locate the stronghold (beds explode in the Nether, revealing caves and potentially the stronghold)\n\nMake sure to prepare before entering - The End contains the Ender Dragon and Endermen!"
        }
    ]
    
    # Add the predefined conversations
    examples.extend(conversations)
    
    # Generate additional Minecraft knowledge questions if needed
    if count > len(conversations):
        # Topics for additional questions
        topics = [
            "how to make a nether portal",
            "best enchantments for armor",
            "how to breed villagers",
            "how to find netherite",
            "what to do after beating the ender dragon",
            "how to make an XP farm",
            "best mining techniques",
            "how to find a stronghold",
            "how to defeat the wither",
            "best food sources in minecraft",
            "how to make an iron golem farm",
            "tips for building underwater",
            "how to protect a village from raids",
            "best biomes to build in",
            "how to use redstone effectively"
        ]
        
        # Add remaining examples if needed
        for i in range(len(conversations), count):
            if i < len(topics):
                # Here we would normally generate a response, but for now we'll use placeholder
                # In a real scenario, you'd want to write high-quality responses for these
                examples.append({
                    "instruction": topics[i],
                    "output": f"Here's a comprehensive guide to {topics[i]} in Minecraft: [This would contain detailed, accurate Minecraft information]"
                })
    
    return examples

def create_minecraft_dataset():
    """Create complete Minecraft training dataset"""
    print("Generating training examples...")
    
    # Generate examples for different categories
    mining_examples = generate_mining_examples(count=250)
    crafting_examples = generate_crafting_examples(count=250)
    navigation_examples = generate_navigation_examples(count=250)
    conversation_examples = generate_conversation_examples(count=50)
    
    # Combine all examples
    all_examples = mining_examples + crafting_examples + navigation_examples + conversation_examples
    random.shuffle(all_examples)
    
    # Save as JSONL for fine-tuning
    os.makedirs('training_data', exist_ok=True)
    
    with open('training_data/minecraft_dataset.jsonl', 'w') as f:
        for example in all_examples:
            f.write(json.dumps(example) + '\n')
    
    print(f"Created training dataset with {len(all_examples)} examples:")
    print(f"- Mining: {len(mining_examples)}")
    print(f"- Crafting: {len(crafting_examples)}")
    print(f"- Navigation: {len(navigation_examples)}")
    print(f"- Conversation: {len(conversation_examples)}")
    
    # Return some examples for inspection
    return all_examples[:5]

# Run the dataset generator
sample_examples = create_minecraft_dataset()
print("\nSample examples for inspection:")
for i, example in enumerate(sample_examples):
    print(f"\nExample {i+1}:")
    print(f"Instruction: {example['instruction']}")
    print(f"Output: {example['output'][:100]}...")  # Show just the beginning