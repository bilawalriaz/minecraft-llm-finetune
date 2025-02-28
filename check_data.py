import json
import sys

def check_file(filename):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            print(f"Number of articles in {filename}: {len(data)}")
            print("Titles:")
            for item in data:
                print(f"- {item['title']}")
    except Exception as e:
        print(f"Error reading {filename}: {e}")

if __name__ == "__main__":
    check_file("raw_data/brewing.json")
    print("\n" + "-"*50 + "\n")
    check_file("raw_data/crafting.json")
