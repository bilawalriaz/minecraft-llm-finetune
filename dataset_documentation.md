# Minecraft Fine-Tuning Datasets Documentation

## 1. Command Intent Dataset (`minecraft_command_intent_dataset.jsonl`)

**Format**: JSON Lines (Each line is a separate JSON object)

**Purpose**: Training intent classification models to map natural language commands to Minecraft command syntax

**Example Structure**:
```json
{
  "command": "/give @p diamond_sword 1",
  "intent": "Get a diamond sword",
  "parameters": {
    "item": "diamond_sword",
    "quantity": 1,
    "recipient": "@p"
  },
  "variations": [
    "Can I have a diamond sword?",
    "Give me a sharp diamond blade"
  ]
}
```

## 2. Unified Interaction Dataset (`unified_minecraft_dataset.json`)

**Format**: JSON array of interaction objects  
**Purpose**: Multi-task training for complex reasoning and contextual responses

**Example Structure**:
```json
{
  "instruction": "What's the most efficient way to farm gold nuggets from Piglins?",
  "input": "",
  "output": "Use bartering with gold ingots - throw them near Piglins while wearing gold armor...",
  "source": "minecraft_wiki_Mobs_Piglin",
  "conversation_type": "gameplay_strategy",
  "thinking": "User needs non-combat gold farming method..."
},
{
  "instruction": "How do I craft a brightening cauldron?",
  "input": "",
  "output": "Requires 4 iron ingots arranged in square pattern...",
  "source": "minecraft_wiki_Blocks_Cauldron",
  "conversation_type": "crafting_and_recipes"
}
```

**Key Fields**:
- `thinking`: Internal reasoning process (when available)
- `source`: Knowledge source for fact verification
- `conversation_type": Context category (22 types including crafting, mobs, redstone)

## Relationship Between Datasets

- The Command Intent Dataset focuses specifically on command surface forms
- The Unified Dataset provides broader contextual knowledge for complex interactions
- Both are used together in the fine-tuning pipeline

## Usage Statistics

| Dataset | Estimated Entries | Avg. Tokens/Entry |
|---------|-------------------|-------------------|
| Command Intent | 15,000+ | 85-120 |
| Unified | 50,000+ | 150-200 |
