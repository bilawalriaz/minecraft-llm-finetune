import json
import os
from unified_dataset import generate_instruction_pair, create_instruction_prompt

# Load wiki data
def load_wiki_data():
    all_data = []
    data_path = "raw_data/all_minecraft_data.json"
    
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            all_data = json.load(f)
        print(f"Loaded Minecraft wiki data with {len(all_data)} total articles")
    else:
        print("Error: Wiki data file not found")
        return []
    
    return all_data

def test_response_styles():
    # Load wiki data
    wiki_data = load_wiki_data()
    if not wiki_data:
        return
    
    # Test conversation types
    conversation_types = [
        "mining_and_resources",
        "crafting_and_recipes", 
        "survival_scenarios",
        "resource_chains",
        "mob_knowledge"
    ]
    
    # Generate and save examples
    examples = []
    
    print("Generating test examples with concise, internet-mature responses...")
    for i, conv_type in enumerate(conversation_types):
        print(f"\nGenerating example for {conv_type}...")
        
        # Test both with and without thinking
        include_thinking = i % 2 == 0  # Alternate between with and without thinking
        example = generate_instruction_pair(wiki_data, conv_type, model="llama3.2:latest", include_thinking=include_thinking)
        
        if example:
            examples.append(example)
            # Print the raw example to see its structure
            print("Example structure:")
            for key, value in example.items():
                if isinstance(value, str):
                    print(f"{key}: {value[:100]}..." if len(value) > 100 else f"{key}: {value}")
                else:
                    print(f"{key}: {value}")
    
    # Save examples to file
    with open("test_internet_mature_responses.json", "w") as f:
        json.dump(examples, f, indent=2)
    
    print(f"\nSaved {len(examples)} test examples to test_internet_mature_responses.json")

if __name__ == "__main__":
    test_response_styles()
