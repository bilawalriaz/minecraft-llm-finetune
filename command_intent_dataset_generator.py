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
OUTPUT_DIR = "training_data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "minecraft_command_intent_dataset.json")
JSONL_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "minecraft_command_intent_dataset.jsonl")
BOT_COMMANDS_FILE = "bot-commands-summary.md"
BOT_PROFILE_FILE = "minecraft-finetune-bot-framework/profiles/defaults/_default.json"

# Configuration for commands to ignore
# Same as COMMAND_CATEGORIES but normal capitalised words - TODO fix
IGNORE_COMMANDS = {
    "Action Commands": ["newAction", "stop", "stfu", "restart", "clearChat"],
    "Movement Commands": ["goToPlayer", "followPlayer", "goToCoordinates", "searchForBlock", "searchForEntity", "moveAway"]
}

# Command categories from the command summary
COMMAND_CATEGORIES = {
    "action_commands": ["newAction", "stop", "stfu", "restart", "clearChat"],
    "movement_commands": ["goToPlayer", "followPlayer", "goToCoordinates", "searchForBlock", 
                         "searchForEntity", "moveAway", "stay"],
    "memory_locations": ["stay", "rememberHere", "goToRememberedPlace"],
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
                "options": {
                    "num_ctx": 50000  # Set the context window size
                },
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

def save_single_sample(sample, json_file, jsonl_file):
    """Save a single sample to both JSON and JSONL formats immediately"""
    # Make sure the output directory exists
    os.makedirs(os.path.dirname(json_file), exist_ok=True)
    
    print(f"DEBUG: Saving to JSON file: {json_file}")
    print(f"DEBUG: Saving to JSONL file: {jsonl_file}")
    
    # For JSONL, we can directly append
    with open(jsonl_file, 'a', encoding='utf-8') as f:
        # Create a copy of the sample to modify for JSONL format
        jsonl_sample = sample.copy()
        
        # If there's a thinking key, incorporate it into the output for JSONL format
        if "thinking" in jsonl_sample:
            thinking = jsonl_sample.pop("thinking")
            # Check if we're dealing with a raw conversation or a formatted sample
            if "bot" in jsonl_sample:
                jsonl_sample["bot"] = f"<thinking>\n{thinking}\n</thinking>\n\n{jsonl_sample['bot']}"
            elif "output" in jsonl_sample:
                jsonl_sample["output"] = f"<thinking>\n{thinking}\n</thinking>\n\n{jsonl_sample['output']}"
        
        f.write(json.dumps(jsonl_sample) + '\n')
    
    # For JSON, we need to load, append, and save
    try:
        # Read the current JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                print(f"DEBUG: Loaded {len(data)} existing samples from JSON file")
            except json.JSONDecodeError:
                # If the file is empty or invalid, start with an empty list
                data = []
                print(f"DEBUG: JSON file was empty or invalid, starting with empty list")
        
        # Append the new sample
        data.append(sample)
        
        # Write back to the file
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"DEBUG: Saved new sample to {json_file} and {jsonl_file}")
        print(f"DEBUG: JSON file now has {len(data)} samples")
        
        # Verify the file was updated
        if os.path.exists(json_file):
            print(f"DEBUG: JSON file exists and is {os.path.getsize(json_file)} bytes")
        else:
            print(f"DEBUG: JSON file does not exist after save!")
            
    except Exception as e:
        print(f"ERROR updating JSON file: {e}")

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

def generate_examples_for_command(bot_name, cmd_name, cmd_info, examples_from_profile, max_examples=20, 
                                  json_file=None, jsonl_file=None, existing_inputs=None):
    """Generate examples for a single command"""
    print(f"Generating examples for {cmd_name}...")
    
    # Get existing examples for this command
    cmd_examples = [ex for ex in examples_from_profile if ex.get("command") == cmd_name]
    
    # Find which category this command belongs to
    category = None
    for cat, cmds in COMMAND_CATEGORIES.items():
        if cmd_name in cmds:
            category = cat
            break
    
    cmd_conversations = []  # Keep track of conversations for this command
    total_saved = 0
    
    # Generate examples for this command
    for i in range(max_examples):
        print(f"  Generating example {i+1} of {max_examples}...")
        
        # Create the prompt
        prompt = generate_command_intent_prompt(bot_name, cmd_name, cmd_info, cmd_examples)
        
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
                    
                    # Format and save this example immediately if requested
                    if json_file and jsonl_file and existing_inputs is not None:
                        # Format as training sample
                        sample = {
                            "instruction": conversation["user"],
                            "input": "",
                            "output": conversation["bot"],
                            "thinking": conversation["thinking"],
                            "conversation_type": category or "general_conversation",
                            "command_used": cmd_name
                        }
                        
                        sample_input = sample.get("instruction", "")
                        print(f"DEBUG: Generated sample with instruction: {sample_input[:50]}...")
                        
                        if sample_input not in existing_inputs:
                            # Save immediately
                            save_single_sample(sample, json_file, jsonl_file)
                            existing_inputs.add(sample_input)
                            total_saved += 1
                            print(f"  Saved new example #{total_saved} for {cmd_name}")
                        else:
                            print(f"  Duplicate sample found, skipping")
                    
                    print(f"  Generated valid example for {cmd_name}")
                else:
                    print(f"  Command {cmd_name} not found in response, skipping")
            else:
                print(f"  Could not parse conversation for {cmd_name}")
        else:
            print(f"  No response generated for {cmd_name}")
    
    return cmd_conversations, total_saved

def main():
    """Main function to generate the dataset"""
    print("Generating command intent dataset...")
    
    # Make sure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"DEBUG: Output directory: {OUTPUT_DIR}")
    print(f"DEBUG: JSON output file: {OUTPUT_FILE}")
    print(f"DEBUG: JSONL output file: {JSONL_OUTPUT_FILE}")
    
    # Load commands
    print("Loading bot commands...")
    commands = load_bot_commands()
    
    # Load profile
    print("Loading bot profile...")
    profile_data = load_bot_profile()
    
    # Load existing dataset from JSON if it exists
    existing_samples = []
    existing_inputs = set()
    
    if os.path.exists(OUTPUT_FILE):
        print(f"Loading existing dataset from {OUTPUT_FILE}...")
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                existing_samples = json.load(f)
            print(f"Loaded {len(existing_samples)} existing samples from JSON.")
            
            # Create a set of existing inputs to check for duplicates
            for sample in existing_samples:
                existing_inputs.add(sample.get("input", ""))
                
        except json.JSONDecodeError:
            print(f"Error loading {OUTPUT_FILE}, starting with empty dataset.")
    else:
        print(f"DEBUG: Output file {OUTPUT_FILE} does not exist yet.")
    
    # Extract command examples from profile
    print("Extracting command examples from profile...")
    examples_from_profile = extract_command_examples_from_profile(profile_data["conversation_examples"])
    
    # Make sure the output files exist and are properly initialized
    if not os.path.exists(OUTPUT_FILE):
        print(f"DEBUG: Creating empty JSON file at {OUTPUT_FILE}")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
    
    if not os.path.exists(JSONL_OUTPUT_FILE):
        print(f"DEBUG: Creating empty JSONL file at {JSONL_OUTPUT_FILE}")
        open(JSONL_OUTPUT_FILE, 'w').close()
    
    # Generate examples for each command
    print("Generating examples for commands...")
    total_new_samples = 0
    
    # Process each command
    for cmd_name, cmd_info in commands.items():
        print(f"Processing command: {cmd_name}")
        print(cmd_info)
        print(IGNORE_COMMANDS.get(cmd_info["category"], []))
        if cmd_name in IGNORE_COMMANDS.get(cmd_info["category"], []):
            print(f"Skipping command {cmd_name} as it is in the ignore list")
            continue
        
        # Generate conversations for this command and save them immediately
        _, cmd_saved = generate_examples_for_command(
            profile_data["name"], 
            cmd_name, 
            cmd_info, 
            examples_from_profile,
            json_file=OUTPUT_FILE,
            jsonl_file=JSONL_OUTPUT_FILE,
            existing_inputs=existing_inputs
        )
        
        total_new_samples += cmd_saved
        print(f"Saved {cmd_saved} new samples for {cmd_name}")
        print(f"Total new samples so far: {total_new_samples}")
    
    print(f"Generated {total_new_samples} new unique samples")
    print(f"Total dataset size: {len(existing_inputs)} samples")

if __name__ == "__main__":
    main()
