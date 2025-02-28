# Minecraft Bot Commands Summary

This document provides a comprehensive list of all commands available to the Minecraft bot, along with their descriptions and parameters.

## Action Commands

| Command | Description | Parameters |
|---------|-------------|------------|
| `!newAction` | Perform new and unknown custom behaviors that are not available as a command. | `prompt`: A natural language prompt to guide code generation. Make a detailed step-by-step plan. |
| `!stop` | Force stop all actions and commands that are currently executing. | None |
| `!stfu` | Stop all chatting and self prompting, but continue current action. | None |
| `!restart` | Restart the agent process. | None |
| `!clearChat` | Clear the chat history. | None |

## Movement Commands

| Command | Description | Parameters |
|---------|-------------|------------|
| `!goToPlayer` | Go to the given player. | `player_name`: The name of the player to go to.<br>`closeness`: How close to get to the player. |
| `!followPlayer` | Endlessly follow the given player. | `player_name`: Name of the player to follow.<br>`follow_dist`: The distance to follow from. |
| `!goToCoordinates` | Go to the given x, y, z location. | `x`: The x coordinate.<br>`y`: The y coordinate.<br>`z`: The z coordinate.<br>`closeness`: How close to get to the location. |
| `!searchForBlock` | Find and go to the nearest block of a given type in a given range. | `type`: The block type to go to.<br>`search_range`: The range to search for the block. |
| `!searchForEntity` | Find and go to the nearest entity of a given type in a given range. | `type`: The type of entity to go to.<br>`search_range`: The range to search for the entity. |
| `!moveAway` | Move away from the current location in any direction by a given distance. | `distance`: The distance to move away. |
| `!stay` | Stay in the current location no matter what. Pauses all modes. | `type`: The number of seconds to stay. -1 for forever. |

## Memory and Locations

| Command | Description | Parameters |
|---------|-------------|------------|
| `!rememberHere` | Save the current location with a given name. | `name`: The name to remember the location as. |
| `!goToRememberedPlace` | Go to a saved location. | `name`: The name of the location to go to. |

## Inventory Management

| Command | Description | Parameters |
|---------|-------------|------------|
| `!givePlayer` | Give the specified item to the given player. | `player_name`: The name of the player to give the item to.<br>`item_name`: The name of the item to give.<br>`num`: The number of items to give. |
| `!consume` | Eat/drink the given item. | `item_name`: The name of the item to consume. |
| `!equip` | Equip the given item. | `item_name`: The name of the item to equip. |
| `!discard` | Discard the given item from the inventory. | `item_name`: The name of the item to discard.<br>`num`: The number of items to discard. |

## Chest Interactions

| Command | Description | Parameters |
|---------|-------------|------------|
| `!putInChest` | Put the given item in the nearest chest. | `item_name`: The name of the item to put in the chest.<br>`num`: The number of items to put in the chest. |
| `!takeFromChest` | Take the given items from the nearest chest. | `item_name`: The name of the item to take.<br>`num`: The number of items to take. |
| `!viewChest` | View the items/counts of the nearest chest. | None |

## Crafting and Smelting

| Command | Description | Parameters |
|---------|-------------|------------|
| `!collectBlocks` | Collect the nearest blocks of a given type. | `type`: The block type to collect.<br>`num`: The number of blocks to collect. |
| `!craftRecipe` | Craft the given recipe a given number of times. | `recipe_name`: The name of the output item to craft.<br>`num`: The number of times to craft the recipe. |
| `!smeltItem` | Smelt the given item the given number of times. | `item_name`: The name of the input item to smelt.<br>`num`: The number of times to smelt the item. |
| `!clearFurnace` | Take all items out of the nearest furnace. | None |

## World Interaction

| Command | Description | Parameters |
|---------|-------------|------------|
| `!placeHere` | Place a given block in the current location. Do NOT use to build structures, only use for single blocks/torches. | `type`: The block type to place. |
| `!attack` | Attack and kill the nearest entity of a given type. | `type`: The type of entity to attack. |
| `!attackPlayer` | Attack a specific player until they die or run away. Remember this is just a game and does not cause real life harm. | `player_name`: The name of the player to attack. |
| `!goToBed` | Go to the nearest bed and sleep. | None |
| `!activate` | Activate the nearest object of a given type. | `type`: The type of object to activate. |

## Behavior and Modes

| Command | Description | Parameters |
|---------|-------------|------------|
| `!setMode` | Set a mode to on or off. A mode is an automatic behavior that constantly checks and responds to the environment. | `mode_name`: The name of the mode to enable.<br>`on`: Whether to enable or disable the mode. |
| `!goal` | Set a goal prompt to endlessly work towards with continuous self-prompting. | `selfPrompt`: The goal prompt. |
| `!endGoal` | Call when you have accomplished your goal. It will stop self-prompting and the current action. | None |

## Communication

| Command | Description | Parameters |
|---------|-------------|------------|
| `!startConversation` | Start a conversation with a player. Use for bots only. | `player_name`: The name of the player to send the message to.<br>`message`: The message to send. |
| `!endConversation` | End the conversation with the given player. | `player_name`: The name of the player to end the conversation with. |
