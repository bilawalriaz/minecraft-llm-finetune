#!/usr/bin/env python3
import json
import os
import random
import re
import requests
import time
from tqdm import tqdm

# Initialize LLM API endpoint
LLM_API = "http://localhost:11434/api/generate"
LLM_MODEL = "llama3.2"  # Update this with your preferred model

# Constants
OUTPUT_FILE = "minecraft_command_intent_dataset.json"
JSONL_OUTPUT_FILE = "minecraft_command_intent_dataset.jsonl"
BOT_COMMANDS_FILE = "bot-commands-summary.md"
BOT_PROFILE_FILE = "minecraft-finetune-bot-framework/profiles/andy_npc.json"

# Command categories from the command summary
COMMAND_CATEGORIES = {
    "action_commands": ["newAction", "stop", "stfu", "restart", "clearChat"],
    "movement_commands": ["goToPlayer", "followPlayer", "goToCoordinates", "searchForBlock", 
                         "searchForEntity", "moveAway", "stay"],
    "memory_locations": ["rememberHere", "goToRememberedPlace"],
    "inventory_management": ["givePlayer", "consume", "equip", "discard"],
    "chest_interactions": ["putInChest", "takeFromChest", "viewChest"],
    "crafting_smelting": ["collectBlocks", "craftRecipe", "smeltItem", "clearFurnace"],
    "world_interaction": ["placeHere", "attack", "attackPlayer", "goToBed", "activate"],
    "behavior_modes": ["setMode", "goal", "endGoal"],
    "communication": ["startConversation", "endConversation"]
}

def llm_generate(prompt, model=LLM_MODEL, temp=0.7, max_tokens=2048):
    """Generate text using local LLM API with streaming"""
    try:
        # Use streaming to handle the response properly
        response = requests.post(
            LLM_API,
            json={
                "model": model,
                "prompt": prompt,
                "temperature": temp,
                "max_tokens": max_tokens,
                "stream": True  # Enable streaming to read line by line
            },
            stream=True,  # Enable HTTP streaming
            timeout=120
        )
        
        # Check response
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            return ""
        
        # Read the streaming response line by line
        full_response = ""
        for line in response.iter_lines():
            if not line:
                continue
            
            try:
                # Parse JSON from the line
                line_json = json.loads(line.decode('utf-8'))
                
                # Extract response portion and append
                if 'response' in line_json:
                    full_response += line_json['response']
                
                # Check if done
                if line_json.get('done', False):
                    break
            except json.JSONDecodeError:
                print(f"Error decoding JSON from line: {line.decode('utf-8')[:100]}")
        
        return full_response
    except Exception as e:
        print(f"Error generating from LLM: {e}")
        return ""

def load_bot_commands():
    """Parse the bot-commands-summary.md file to extract command information"""
    commands = {}
    
    try:
        with open(BOT_COMMANDS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract sections based on markdown headers
        sections = re.split(r'## ', content)
        for section in sections[1:]:  # Skip the introduction
            lines = section.strip().split('\n')
            category = lines[0].strip()
            
            # Find the command tables in this section
            table_pattern = r'\| `!([\w]+)` \| (.*?) \| (.*?) \|'
            for match in re.finditer(table_pattern, section):
                cmd_name = match.group(1)
                description = match.group(2).strip()
                params_text = match.group(3).strip()
                
                # Parse parameters
                params = {}
                if params_text and params_text != "None":
                    param_pattern = r'`([\w_]+)`:\s*(.*?)(?:<br>|$)'
                    for param_match in re.finditer(param_pattern, params_text):
                        param_name = param_match.group(1)
                        param_desc = param_match.group(2).strip()
                        params[param_name] = {
                            "description": param_desc
                        }
                
                commands[cmd_name] = {
                    "name": f"!{cmd_name}",
                    "description": description,
                    "params": params,
                    "category": category
                }
    except Exception as e:
        print(f"Error loading bot commands: {e}")
    
    return commands

def load_bot_profile():
    """Load the bot profile to extract conversation examples and personality"""
    try:
        with open(BOT_PROFILE_FILE, 'r', encoding='utf-8') as f:
            profile = json.load(f)
        
        return {
            "name": profile.get("name", "andy"),
            "conversing_prompt": profile.get("conversing", ""),
            "conversation_examples": profile.get("conversation_examples", [])
        }
    except Exception as e:
        print(f"Error loading bot profile: {e}")
        return {
            "name": "andy",
            "conversing_prompt": "",
            "conversation_examples": []
        }

def extract_command_examples_from_profile(conversation_examples, cmd_name=None):
    """Extract examples of command usage from the profile's conversation examples"""
    command_examples = []
    
    for conversation in conversation_examples:
        messages = []
        cmd_found = False
        
        for msg in conversation:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "user":
                user_msg = content
            elif role == "assistant" and "!" in content:
                # Look for commands in the assistant's messages
                cmd_pattern = r'!([\w]+)(?:\(([^)]*)\))?'
                for match in re.finditer(cmd_pattern, content):
                    found_cmd = match.group(1)
                    if cmd_name is None or found_cmd == cmd_name:
                        cmd_found = True
                        messages.append({
                            "user": user_msg,
                            "bot": content,
                            "command": found_cmd,
                            "thinking": f"User asked: '{user_msg}'. This requires the {found_cmd} command because..."
                        })
        
        if cmd_found:
            command_examples.extend(messages)
    
    return command_examples

def generate_command_intent_prompt(bot_name, cmd_name, cmd_info, examples):
    """Generate a prompt for creating user-bot conversations for a specific command"""
    
    # Format examples for the prompt
    example_text = ""
    for i, ex in enumerate(examples[:3]):
        user_msg = ex.get("user", "")
        bot_msg = ex.get("bot", "")
        thinking = ex.get("thinking", "").replace("...", f"I need to interpret what the user wants. They seem to need the {cmd_name} command because {cmd_info['description'].lower()}. This is the appropriate command for this situation.")
        
        example_text += f"Example {i+1}:\n"
        example_text += f"USER: {user_msg}\n"
        example_text += f"THINKING: {thinking}\n"
        example_text += f"BOT: {bot_msg}\n\n"
    
    # If no examples, create a generic one
    if not example_text:
        params = []
        for param_name, param_info in cmd_info["params"].items():
            if "string" in param_info.get("description", "").lower():
                params.append(f"'{param_name}'")
            else:
                params.append(f"{param_name}")
        
        param_str = ", ".join(params)
        example_text = f"""Example 1:
USER: Can you {cmd_name.lower().replace('_', ' ')}?
THINKING: The user wants me to use the {cmd_name} command. This command {cmd_info['description'].lower()}, so it's appropriate for their request.
BOT: Sure thing! !{cmd_name}({param_str})

"""
    
    # Format parameters
    params_text = ""
    for param_name, param_info in cmd_info["params"].items():
        params_text += f"- {param_name}: {param_info['description']}\n"
    
    # Build the prompt
    prompt = f"""Generate 1 realistic conversation between a Minecraft player and the bot named {bot_name}, focusing specifically on the !{cmd_name} command.

COMMAND INFORMATION:
Command: !{cmd_name}
Description: {cmd_info['description']}
Parameters:
{params_text}

BOT PERSONALITY:
{bot_name} is a playful Minecraft bot that acts like a typical Minecraft player rather than an AI. The bot is friendly but slightly aloof and always to-the-point with brief responses (under 15 words).

FORMAT THE RESPONSE EXACTLY LIKE THIS:
USER: [Player message - very brief, 5-20 words maximum]
THINKING: [Bot analyzes user intent and explains why !{cmd_name} is the right command]
BOT: [Bot response with !{cmd_name} command - concise, under 15 words]

EXAMPLES OF CORRECT FORMAT:
{example_text}

GUIDELINES:
1. The player message should be casual, brief, and realistic for a Minecraft player
2. The thinking section should analyze the actual intent behind the user's message
3. The bot response must include the !{cmd_name} command with appropriate parameters
4. Vary the player's request style (direct, indirect, question, statement)
5. The bot's response should solve the player's actual need
"""
    return prompt

def parse_generated_conversation(text):
    """Parse the LLM output to extract a single conversation"""
    conversation = {}
    
    user_match = re.search(r'USER:\s*(.*?)(?=THINKING:|$)', text, re.DOTALL)
    thinking_match = re.search(r'THINKING:\s*(.*?)(?=BOT:|$)', text, re.DOTALL)
    bot_match = re.search(r'BOT:\s*(.*?)(?=$)', text, re.DOTALL)
    
    if user_match:
        conversation['user'] = user_match.group(1).strip()
    if thinking_match:
        conversation['thinking'] = thinking_match.group(1).strip()
    if bot_match:
        conversation['bot'] = bot_match.group(1).strip()
    
    # Only return if we have all components
    if 'user' in conversation and 'thinking' in conversation and 'bot' in conversation:
        return conversation
    return None

def identify_command_in_response(response, cmd_name):
    """Identify if the specified command is used in the bot's response"""
    pattern = r'!' + re.escape(cmd_name) + r'(?:\(([^)]*)\))?'
    match = re.search(pattern, response)
    if match:
        return match.group(0)
    return None

def generate_examples_for_commands(commands, examples_from_profile):
    """Generate examples for each command individually"""
    print("Generating command examples...")
    
    all_conversations = []
    
    # Get a flattened list of all commands
    all_command_names = []
    for cmd_list in COMMAND_CATEGORIES.values():
        all_command_names.extend(cmd_list)
    
    # Generate examples for each command
    for cmd_name in tqdm(all_command_names):
        if cmd_name not in commands:
            continue
            
        cmd_info = commands[cmd_name]
        
        # Get existing examples for this command
        cmd_examples = [ex for ex in examples_from_profile if ex.get("command") == cmd_name]
        
        # Find which category this command belongs to
        category = None
        for cat, cmds in COMMAND_CATEGORIES.items():
            if cmd_name in cmds:
                category = cat
                break
        
        cmd_conversations = []  # Keep track of conversations for this command
        
        # Generate 3 examples per command
        for i in range(3):
            print(f"Generating example {i+1} for {cmd_name}...")
            
            # Create the prompt
            prompt = generate_command_intent_prompt("andy", cmd_name, cmd_info, cmd_examples)
            
            # Generate the conversation
            response = llm_generate(prompt, temp=0.75, max_tokens=1024)
            
            if response:
                # Parse the conversation
                conversation = parse_generated_conversation(response)
                
                if conversation:
                    # Verify the command is in the response
                    cmd_text = identify_command_in_response(conversation["bot"], cmd_name)
                    
                    if cmd_text:
                        conversation["command"] = cmd_name
                        conversation["command_text"] = cmd_text
                        conversation["category"] = category
                        cmd_conversations.append(conversation)
                        all_conversations.append(conversation)
                        print(f"Generated valid example for {cmd_name}")
                    else:
                        print(f"Command {cmd_name} not found in response, skipping")
                else:
                    print(f"Could not parse conversation for {cmd_name}")
            else:
                print(f"No response generated for {cmd_name}")
        
        # Save the examples for this command incrementally
        if cmd_conversations:
            # Format samples for this command
            cmd_samples = format_as_training_samples(cmd_conversations)
            
            # Save incrementally
            save_samples_incrementally(cmd_samples, JSONL_OUTPUT_FILE)
            
            # Also update the JSON file with all examples so far
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                all_samples = format_as_training_samples(all_conversations)
                json.dump(all_samples, f, indent=2)
            
            print(f"Saved {len(cmd_samples)} samples for command {cmd_name}")
    
    print(f"Generated {len(all_conversations)} valid command conversations")
    
    # Save the final dataset with proper JSONL format
    save_to_jsonl(all_conversations, JSONL_OUTPUT_FILE)
    
    return all_conversations

def format_as_training_samples(conversations):
    """Format conversations as training samples with thinking steps as a separate key"""
    samples = []
    
    for convo in conversations:
        # Create a single sample with thinking as a separate key
        sample = {
            "instruction": convo["user"],
            "input": "",
            "output": convo["bot"],
            "thinking": convo["thinking"],
            "conversation_type": convo.get("category", "general_conversation")
        }
        
        if "command" in convo:
            sample["command_used"] = convo["command"]
        
        samples.append(sample)
    
    return samples

def save_samples(samples, json_file, jsonl_file):
    """Save samples to both JSON and JSONL formats"""
    # Also save incrementally as we go
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(samples, f, indent=2)
    
    with open(jsonl_file, 'w', encoding='utf-8') as f:
        for sample in samples:
            f.write(json.dumps(sample) + '\n')
    
    print(f"Saved {len(samples)} samples to {json_file} and {jsonl_file}")

def save_samples_incrementally(samples, jsonl_file, append=True):
    """Save samples incrementally to a JSONL file"""
    mode = 'a' if append else 'w'
    with open(jsonl_file, mode, encoding='utf-8') as f:
        for sample in samples:
            f.write(json.dumps(sample) + '\n')
    
    print(f"Saved {len(samples)} samples incrementally to {jsonl_file}")

def save_to_jsonl(samples, filename):
    """Save samples to a JSONL file"""
    with open(filename, 'w', encoding='utf-8') as f:
        for sample in samples:
            # Create a copy of the sample to modify for JSONL format
            jsonl_sample = sample.copy()
            
            # If there's a thinking key, incorporate it into the output for JSONL format
            if "thinking" in jsonl_sample:
                thinking = jsonl_sample.pop("thinking")
                jsonl_sample["output"] = f"<thinking>\n{thinking}\n</thinking>\n\n{jsonl_sample['output']}"
            
            f.write(json.dumps(jsonl_sample) + '\n')

def main():
    """Main function to generate the dataset"""
    print("Generating command intent dataset...")
    
    # Load commands
    print("Loading bot commands...")
    commands = load_bot_commands()
    
    # Load profile
    print("Loading bot profile...")
    profile_data = load_bot_profile()
    
    # Extract examples from profile
    print("Extracting command examples from profile...")
    examples_from_profile = extract_command_examples_from_profile(profile_data["conversation_examples"])
    
    # Generate examples for each command
    conversations = generate_examples_for_commands(commands, examples_from_profile)
    
    # Format as training samples
    samples = format_as_training_samples(conversations)
    
    # Save the dataset
    with open("minecraft_command_intent_dataset.json", 'w', encoding='utf-8') as f:
        json.dump(samples, f, indent=2)
    
    # Save as JSONL
    save_to_jsonl(samples, "minecraft_command_intent_dataset.jsonl")
    
    print(f"Generated {len(samples)} samples for {len(commands)} commands")
    print("Dataset saved to minecraft_command_intent_dataset.json and minecraft_command_intent_dataset.jsonl")

if __name__ == "__main__":
    main()
