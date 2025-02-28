#!/usr/bin/env python3
import json
import os
import random
import requests
import time
from tqdm import tqdm

# Initialize Ollama API endpoint
OLLAMA_API = "http://localhost:11434/api/generate"

# Define the categories of conversations we want to generate
CONVERSATION_TYPES = [
    "mining_and_resources",          # Questions about how to mine/collect resources
    "crafting_and_recipes",          # Questions about how to craft items
    "mob_knowledge",                 # Questions about various mobs (hostile/passive)
    "game_mechanics",                # Questions about game mechanics (redstone, enchanting, etc.)
    "navigation_and_biomes",         # Questions about biomes and navigation
    "survival_scenarios",            # Questions about handling urgent survival situations
    "resource_chains",               # Questions about efficient resource acquisition chains
    "gameplay_strategy",             # Questions about strategic gameplay approaches
   # "building_techniques",           # Questions about building structures
   # "technical_minecraft",           # Questions about technical aspects (farms, redstone)
   # "lore_and_history",              # Questions about Minecraft lore/history
   # "problem_solving",               # Complex problem-solving scenarios
    "multi_step_explanations"        # Complex multi-step explanations
]

def load_wiki_data():
    """Load the Minecraft wiki data from JSON files"""
    all_data = {}
    data_path = os.path.join("raw_data", "all_minecraft_data.json")
    
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
            
        # Remove any empty categories
        filtered_data = {k: v for k, v in all_data.items() if v and len(v) > 0}
        
        print(f"Loaded Minecraft wiki data with {sum(len(articles) for category, articles in filtered_data.items())} total articles")
        return filtered_data
    except Exception as e:
        print(f"Error loading wiki data: {e}")
        return None

def ollama_generate(prompt, model="llama3.2:latest", temp=0.7, max_tokens=512, context_window=50000):
    """Generate text using Ollama API"""
    try:
        data = {
            "model": model,
            "prompt": prompt,
            "temperature": temp,
            "max_tokens": max_tokens,
            "stream": False,
            "options": {
                "num_ctx": context_window  # This is the correct parameter name for context window size
            }
        }
        
        response = requests.post(OLLAMA_API, json=data)
        if response.status_code == 200:
            print(response.json()["response"])
            return response.json()["response"]
        else:
            print(f"Error from Ollama API: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        return None

def create_instruction_prompt(wiki_data, conversation_type, include_thinking=False):
    """Create a system prompt for Ollama to generate an instruction-response pair"""
    
    # Select a random category from the wiki data (ensuring it's not empty)
    categories = [k for k, v in wiki_data.items() if v and len(v) > 0]
    if not categories:
        raise ValueError("No valid categories with content found in wiki data")
        
    selected_category = random.choice(categories)
    
    # Select a random article from that category
    articles = wiki_data[selected_category]
    selected_article = random.choice(articles)
    article_content = selected_article.get("content", "")
    article_title = selected_article.get("title", "Unknown")
    
    # Limit content length to avoid token issues
    if len(article_content) > 40000:
        article_content = article_content[:40000] + "..."
    
    # Create system prompt based on conversation type
    system_prompts = {
        "mining_and_resources": f"Based on this Minecraft wiki article about '{article_title}', create a question from a player asking how to obtain this resource or similar resources. Then create a concise, helpful response that accurately explains the process without unnecessary fluff.",
        
        "crafting_and_recipes": f"""Based on this Minecraft wiki article about '{article_title}', create a question from a player asking how to craft this item or a related item. 
        For your response, include:
        1. The exact materials needed with quantities
        2. The precise crafting grid pattern where relevant
        3. Any special conditions needed (e.g., specific crafting station)
        4. Common mistakes to avoid
        5. Alternative crafting methods if they exist
        Keep the response concise and to the point, like an experienced player sharing knowledge efficiently.""", 

        "survival_scenarios": f"""Based on this Minecraft wiki article about '{article_title}', create a realistic survival scenario where a player is in danger or needs resources urgently (e.g., 'I'm trapped in a cave with zombies and only have 3 hearts left, what should I do?'). 
        Then create a helpful response that gives practical, immediate advice that considers:
        1. The immediate threat management
        2. Resource utilization and prioritization
        3. Step-by-step instructions for survival
        4. Alternative solutions based on possible inventory items
        Be direct and efficient with your advice, like an experienced player who's been in this situation before.""",   

        "resource_chains": f"""Based on this Minecraft wiki article about '{article_title}', create a question from a player asking about efficiently acquiring this resource or item from scratch (starting with basic tools). 
        Then create a detailed response that:
        1. Outlines the complete resource chain from basic materials to final product
        2. Provides time-saving techniques and shortcuts
        3. Mentions tool requirements for each step
        4. Suggests alternative paths based on different starting conditions
        5. Includes efficiency tips that experienced players would know
        Keep it concise and practical, like advice from a veteran player who knows how to explain things clearly without unnecessary words.""",

        "mob_knowledge": f"Based on this Minecraft wiki article about '{article_title}', create a question from a player asking about this mob's behavior, drops, or how to defeat/tame it. Then create a concise response with accurate information, written in a straightforward style that gets to the point.",
        
        "game_mechanics": f"Based on this Minecraft wiki article about '{article_title}', create a question from a player asking about how this game mechanic works. Then create a clear, concise response that accurately explains the mechanic without unnecessary elaboration.",
        
        "navigation_and_biomes": f"Based on this Minecraft wiki article about '{article_title}', create a question from a player asking about finding this biome, navigating through it, or what resources it contains. Then create a helpful, to-the-point response with accurate information.",
        
        "building_techniques": f"Based on this Minecraft wiki article about '{article_title}', create a question from a player asking for advice on building with these materials or in this style. Then create a response with practical building tips, written concisely like advice from an experienced builder.",
        
        "technical_minecraft": f"Based on this Minecraft wiki article about '{article_title}', create a question from a player asking about an advanced technical aspect of Minecraft, such as farm designs, redstone contraptions, or game optimization. Then create a detailed technical response that's clear and efficient, like advice from a redstone expert who knows how to explain complex concepts simply.",
        
        "lore_and_history": f"Based on this Minecraft wiki article about '{article_title}', create a question from a player asking about the lore or history behind this element of Minecraft. Then create a response that shares accurate information about its background in a concise, interesting way.",
        
        "problem_solving": f"Based on this Minecraft wiki article about '{article_title}', create a complex problem scenario that a player might face. Then create a response that walks through the solution in a clear, step-by-step way without unnecessary explanation.",
        
        "gameplay_strategy": f"""Based on this Minecraft wiki article about '{article_title}', create a question asking about effective strategies for using this item/resource/mob for survival advantage. 
        Then create a detailed response that includes:
        1. Non-obvious uses for the item/resource/mob
        2. How to leverage it for survival efficiency
        3. Common strategic mistakes to avoid
        4. Advanced techniques that experienced players use
        Keep it concise and practical, like advice from a veteran player who knows how to get to the point."""
    }
    
    # Choose the appropriate prompt for the selected conversation type
    system_prompt = system_prompts.get(conversation_type, system_prompts["game_mechanics"])
    
    # Add instruction for thinking step if requested
    if include_thinking:
        system_prompt += " Before giving the final answer, include a 'thinking' step where you reason through the information to arrive at the accurate answer."
    
    # Build the complete prompt
    prompt = f"""You are an expert machine learning dataset creator. I'll provide you with an article from the Minecraft Wiki, and I want you to help generate a question and answer pair that mimics a conversation between a Minecraft player and a in-world Minecraft bot.
    The bot's personality is like a seasoned IRC/forum user - knowledgeable, concise, and casually cool without trying too hard. They use occasional internet shorthand (like "tbh", "imo", "afaik", "lmao") but never overdo it. Their humor is dry and understated, sometimes self-deprecating, but never forced. They get straight to the point without unnecessary fluff, but still manage to be helpful and approachable. They're the kind of person who's been playing Minecraft since alpha and has seen it all, but isn't elitist about it. They offer practical advice efficiently, occasionally dropping in a relevant personal experience when it adds value.

ARTICLE TITLE: {article_title}
CATEGORY: {selected_category}

ARTICLE CONTENT:
{article_content.strip()}

INSTRUCTION:
{system_prompt}

Format your response EXACTLY as follows:
```
PLAYER_QUESTION: [The player's question]

{f"THINKING: [Your step-by-step reasoning process]" if include_thinking else ""}

ASSISTANT_RESPONSE: [The bot's response - make sure you do not start by repeating the player's question. For crafting recipes, be specific about materials, quantities, and grid patterns. For resource acquisition, provide complete step-by-step instructions. Keep it concise and internet-mature, like a seasoned Minecraft player who's helpful without being verbose or cringey.]
```

DO NOT include any explanations or additional text outside of the specified format.
IMPORTANT: Do not use backticks, markdown formatting, or any other characters in your response except what is shown in the template above.
STRICTLY follow the format shown above with the exact section headers and no additional text.
"""
    
    return prompt, article_title, selected_category

def validate_response_quality(response, conversation_type):
    """Validate that the response meets quality standards for the given conversation type"""
    
    # Check for minimum length
    if len(response) < 50:
        return False, "Response too short"
    
    # Check for maximum length (to avoid extremely verbose responses)
    if len(response) > 2000:
        return False, "Response too long"
    
    # Check for basic helpfulness
    if "I don't know" in response.lower() or "I'm not sure" in response.lower():
        # Only reject if this is the primary content
        if len(response) < 100:
            return False, "Response lacks helpful information"
    
    # Specific checks based on conversation type
    if conversation_type == "crafting_and_recipes":
        # Check for specific crafting information
        if not any(term in response.lower() for term in ["need", "require", "use", "place", "craft", "recipe", "grid", "pattern", "shaped", "shapeless"]):
            return False, "Crafting response doesn't describe the recipe pattern"
    
    elif conversation_type == "survival_scenarios":
        # Check for actionable advice
        if not any(term in response.lower() for term in ["should", "could", "try", "do", "don't", "avoid", "use", "find", "craft", "build", "run", "hide", "fight"]):
            return False, "Survival response doesn't provide actionable advice"
    
    elif conversation_type == "resource_chains":
        # Check for step-by-step instructions
        if not any(term in response.lower() for term in ["first", "then", "next", "after", "finally", "step", "process", "start", "begin"]):
            return False, "Resource chain response doesn't provide sequential steps"
    
    # Check for internet-mature style (some shorthand, casual but not overly so)
    internet_style_markers = ["tbh", "imo", "afaik", "fwiw", "btw", "iirc", "ymmv", "tl;dr"]
    casual_markers = ["pretty", "basically", "actually", "just", "really", "honestly", "generally", "typically"]
    
    # The response should have some casual markers but not be too formal
    has_casual_style = any(marker in response.lower() for marker in casual_markers)
    
    # Ideally would have some internet shorthand, but not required
    has_internet_style = any(marker in response.lower() for marker in internet_style_markers)
    
    # No need to reject based on style alone, as the main priority is accurate information
    
    return True, "Response meets quality standards"

def generate_instruction_pair(wiki_data, conversation_type, model="mistral-small", include_thinking=True):
    """Generate an instruction-response pair using Ollama"""
    
    try:
        # Create the instruction prompt
        prompt, article_title, selected_category = create_instruction_prompt(wiki_data, conversation_type, include_thinking=include_thinking)
        
        # Generate response using Ollama API
        response_text = ollama_generate(prompt, model=model)
        
        if not response_text:
            print("Failed to generate response")
            return None
        
        # Extract player question and assistant response
        player_question = None
        assistant_response = None
        thinking = None
        
        # Clean response by removing any markdown code block formatting
        response_text = response_text.replace("```", "").strip()
        
        if "PLAYER_QUESTION:" in response_text:
            player_question_part = response_text.split("PLAYER_QUESTION:")[1]
            player_question_end = min(
                [player_question_part.find(f"\n\n{marker}") for marker in ["THINKING:", "ASSISTANT_RESPONSE:"] 
                if player_question_part.find(f"\n\n{marker}") != -1] or [len(player_question_part)]
            )
            player_question = player_question_part[:player_question_end].strip()
        
        if include_thinking and "THINKING:" in response_text:
            thinking_part = response_text.split("THINKING:")[1]
            thinking_end = thinking_part.find("\n\nASSISTANT_RESPONSE:")
            if thinking_end != -1:
                thinking = thinking_part[:thinking_end].strip()
        
        if "ASSISTANT_RESPONSE:" in response_text:
            assistant_response = response_text.split("ASSISTANT_RESPONSE:")[1].strip()
        
        # If we couldn't extract properly, return None
        if not player_question or not assistant_response:
            print("Could not properly extract question and response")
            print(f"Raw response: {response_text}")
            return None
            
        # Validate response quality
        is_valid, validation_message = validate_response_quality(assistant_response, conversation_type)
        if not is_valid:
            print(f"Invalid response: {validation_message}")
            return None
        
        # Create the instruction-response pair
        instruction_pair = {
            "instruction": player_question,
            "input": "",
            "output": assistant_response,
            "source": f"minecraft_wiki_{selected_category}_{article_title}",
            "conversation_type": conversation_type
        }
        
        # Add thinking if applicable
        if include_thinking and thinking:
            instruction_pair["thinking"] = thinking
            
        return instruction_pair
        
    except Exception as e:
        print(f"Error in generate_instruction_pair: {e}")
        return None

def create_unified_dataset(num_examples=200, include_thinking_ratio=0.3, model="mistral-small"):
    """Create a unified dataset combining synthetic and wiki-based examples"""
    
    # Load wiki data
    wiki_data = []
    data_path = "raw_data/all_minecraft_data.json"
    
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            wiki_data = json.load(f)
        print(f"Loaded Minecraft wiki data with {len(wiki_data)} total articles")
    else:
        print("Error: Wiki data file not found")
        return
    
    # Load existing dataset if available
    existing_data = []
    dataset_path = "unified_minecraft_dataset.json"
    
    if os.path.exists(dataset_path):
        try:
            with open(dataset_path, 'r') as f:
                existing_data = json.load(f)
            print(f"Loaded existing dataset with {len(existing_data)} examples")
        except json.JSONDecodeError:
            print("Error loading existing dataset, starting fresh")
    
    # Determine how many new examples to generate
    num_to_generate = max(0, num_examples - len(existing_data))
    
    if num_to_generate > 0:
        print(f"Generating {num_to_generate} new examples based on wiki data...")
        
        # List of conversation types to sample from
        conversation_types = [
            "mining_and_resources", 
            "crafting_and_recipes", 
            "survival_scenarios",
            "resource_chains",
            "mob_knowledge",
            "game_mechanics",
            "navigation_and_biomes",
           # "building_techniques",
           # "technical_minecraft",
           # "lore_and_history",
           # "problem_solving",
            "gameplay_strategy"
        ]
        
        # Generate new examples with progress bar
        new_examples = []
        for i in tqdm(range(num_to_generate)):
            # Randomly select conversation type
            conversation_type = random.choice(conversation_types)
            
            # Determine if this example should include thinking
            include_thinking = random.random() < include_thinking_ratio
            
            # Generate example
            example = generate_instruction_pair(wiki_data, conversation_type, model=model, include_thinking=include_thinking)
            
            if example:
                new_examples.append(example)
                
                # Save progress every 10 examples
                if (i + 1) % 10 == 0:
                    temp_dataset = existing_data + new_examples
                    with open(dataset_path, 'w') as f:
                        json.dump(temp_dataset, f, indent=2)
        
        # Combine with existing data
        unified_dataset = existing_data + new_examples
    else:
        print("No new examples needed")
        unified_dataset = existing_data
    
    # Save final dataset
    with open(dataset_path, 'w') as f:
        json.dump(unified_dataset, f, indent=2)
    
    print(f"Saved unified dataset with {len(unified_dataset)} examples")
    return unified_dataset

if __name__ == "__main__":
    # Create the unified dataset
    print("Creating unified Minecraft dataset with wiki-based examples...")
    create_unified_dataset(num_examples=10000, model="llama3.2:latest")
