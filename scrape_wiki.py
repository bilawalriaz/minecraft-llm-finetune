import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re
from tqdm import tqdm

# Function to clean text content
def clean_text(text):
    # First, normalize all whitespace (convert all whitespace sequences to a single space)
    text = re.sub(r'\s+', ' ', text)
    
    # Then reintroduce paragraph breaks where appropriate (double newlines)
    text = re.sub(r'\.(\s+)', '.\n\n', text)  # Add paragraph breaks after periods
    text = re.sub(r'\!(\s+)', '!\n\n', text)  # Add paragraph breaks after exclamation marks
    text = re.sub(r'\?(\s+)', '?\n\n', text)  # Add paragraph breaks after question marks
    
    # Remove zero-width characters and other invisible Unicode characters
    text = re.sub(r'[\u200b-\u200f\u2028-\u202f\u2060-\u206f\ufeff]', '', text)
    
    # Remove square brackets with only spaces inside
    text = re.sub(r'\[\s*\]', '', text)
    
    # Clean up "only" tags like [JE only], [BE only]
    #text = re.sub(r'\[\s*(JE|BE|Bedrock|Java)\s*(?:Edition)?\s*only\s*\]', r'(\1)', text)
    
    # Fix spacing around punctuation
    text = re.sub(r'\s+([.,;:!?)])', r'\1', text)  # Remove space before punctuation
    text = re.sub(r'([([{])\s+', r'\1', text)      # Remove space after opening brackets
    
    # Fix common issues with game terms
    text = re.sub(r'(Bedrock|Java)\s+Edition', r'\1 Edition', text)
    
    # Consolidate multiple paragraph breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Final cleanup
    text = text.strip()
    
    return text

# Function to save data incrementally
def save_data(data, category, is_final=False):
    # Save category data
    json_path = f'raw_data/{category.lower()}.json'
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    # If this is the final save, also update the combined data file
    if is_final:
        # Load all categories to create the combined file
        all_data = {}
        categories = ["Blocks", "Items", "Brewing", "Mechanics", "Mobs", "Crafting"]
        for cat in categories:
            cat_path = f'raw_data/{cat.lower()}.json'
            if os.path.exists(cat_path):
                try:
                    with open(cat_path, 'r') as f:
                        all_data[cat] = json.load(f)
                except:
                    print(f"Error loading {cat} for combined data")
        
        # Save combined data
        with open('raw_data/all_minecraft_data.json', 'w') as f:
            json.dump(all_data, f, indent=2)
        
        print(f"Saved combined data with {sum(len(articles) for articles in all_data.values())} total articles")
    else:
        # Don't print this when using tqdm as it will interfere with the progress bar
        pass

# Function to scrape a Minecraft Wiki category
def scrape_category(category_name, max_pages=2000, existing_data=None):
    print(f"Scraping category: {category_name}")
    
    # Initialize existing URLs set to avoid duplicates
    existing_urls = set()
    if existing_data:
        for article in existing_data:
            existing_urls.add(article['url'])
        print(f"  Found {len(existing_urls)} existing articles to skip")
    
    url = f"https://minecraft.fandom.com/wiki/Category:{category_name}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Get all pages in this category - updated selector for the new wiki structure
    article_links = []
    
    # Find all direct article links in the category
    print("  Finding articles in main category page...")
    for link in soup.select('#mw-pages .mw-category a'):
        article_url = 'https://minecraft.fandom.com' + link['href']
        # Skip if already scraped
        if article_url in existing_urls:
            continue
            
        article_links.append({
            'title': link.text.strip(),
            'url': article_url
        })
        if len(article_links) >= max_pages:
            break
    
    # If we need more articles, also check subcategories
    if len(article_links) < max_pages:
        subcategories = soup.select('.mw-category .CategoryTreeItem > a')
        if subcategories:
            print(f"  Checking {len(subcategories)} subcategories for more articles...")
            
        for subcat_link in tqdm(subcategories, desc="  Subcategories", disable=len(subcategories) == 0):
            # Skip if we already have enough links
            if len(article_links) >= max_pages:
                break
                
            # Get the subcategory page
            subcat_url = 'https://minecraft.fandom.com' + subcat_link['href']
            try:
                subcat_response = requests.get(subcat_url)
                subcat_soup = BeautifulSoup(subcat_response.content, 'html.parser')
                
                # Get articles from this subcategory
                for link in subcat_soup.select('#mw-pages .mw-category a'):
                    article_url = 'https://minecraft.fandom.com' + link['href']
                    # Skip if already scraped
                    if article_url in existing_urls:
                        continue
                        
                    article_links.append({
                        'title': link.text.strip(),
                        'url': article_url
                    })
                    if len(article_links) >= max_pages:
                        break
                
                # Avoid overloading the server
                time.sleep(0.25)
            except Exception as e:
                print(f"Error scraping subcategory {subcat_link.text}: {e}")
    
    # If no new articles to scrape, return existing data
    if not article_links and existing_data:
        print(f"  No new articles to scrape for {category_name}")
        return existing_data
    
    # Scrape each article
    articles = existing_data or []
    save_counter = 0
    save_frequency = 5  # Save after every 5 articles
    
    print(f"  Found {len(article_links)} new articles to scrape")
    
    # Use tqdm for progress monitoring
    for i, article in enumerate(tqdm(article_links, desc=f"  Scraping {category_name}", unit="article")):
        try:
            article_response = requests.get(article['url'])
            article_soup = BeautifulSoup(article_response.content, 'html.parser')
            
            # Get main content - updated selector for the new wiki structure
            content = article_soup.select_one('.mw-parser-output')
            if content:
                # Remove navigation elements
                for nav in content.select('.navbox, .toc, .infobox, .wikitable, .mw-editsection, .mw-headline'):
                    nav.decompose()
                
                # Improve paragraph handling by adding explicit newlines
                for p in content.find_all('p'):
                    # Add newlines after paragraphs to preserve structure
                    if p.next_sibling:
                        p.append('\n\n')
                
                # Handle lists better
                for ul in content.find_all(['ul', 'ol']):
                    # Add newlines before and after lists
                    if ul.previous_sibling:
                        ul.insert_before('\n')
                    if ul.next_sibling:
                        ul.append('\n')
                    
                    # Add newlines after list items
                    for li in ul.find_all('li'):
                        if li.next_sibling:
                            li.append('\n')
                
                # Handle headings better
                for heading in content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    # Add newlines before and after headings
                    if heading.previous_sibling:
                        heading.insert_before('\n\n')
                    if heading.next_sibling:
                        heading.append('\n\n')
                
                # Extract text
                text = content.get_text(separator=' ')
                
                # Clean the text content
                cleaned_text = clean_text(text)
                
                articles.append({
                    'title': article['title'],
                    'url': article['url'],
                    'content': cleaned_text,
                    'category': category_name
                })
                
                # Increment save counter
                save_counter += 1
                
                # Save progress incrementally
                if save_counter >= save_frequency:
                    save_data(articles, category_name)
                    save_counter = 0
            
            # Avoid overloading the server
            time.sleep(0.25)
        except Exception as e:
            tqdm.write(f"Error scraping {article['title']}: {e}")
            # Save on error to preserve progress
            save_data(articles, category_name)
    
    # Final save for this category
    save_data(articles, category_name)
    print(f"  Completed scraping {len(article_links)} new articles for {category_name}")
    print(f"  Total articles for {category_name}: {len(articles)}")
    
    return articles

# Function to scrape special pages that don't have category pages
def scrape_special_pages(category_name, existing_data=None):
    print(f"Scraping special category: {category_name}")
    
    # Initialize existing URLs set to avoid duplicates
    existing_urls = set()
    if existing_data:
        for article in existing_data:
            existing_urls.add(article['url'])
        print(f"  Found {len(existing_urls)} existing articles to skip")
    
    # Define direct URLs for special categories
    special_pages = {
        "Brewing": [
            {"title": "Brewing", "url": "https://minecraft.fandom.com/wiki/Brewing"},
            {"title": "Brewing Stand", "url": "https://minecraft.fandom.com/wiki/Brewing_Stand"},
            {"title": "Potion", "url": "https://minecraft.fandom.com/wiki/Potion"},
            {"title": "Splash Potion", "url": "https://minecraft.fandom.com/wiki/Splash_Potion"},
            {"title": "Lingering Potion", "url": "https://minecraft.fandom.com/wiki/Lingering_Potion"},
            {"title": "Cauldron", "url": "https://minecraft.fandom.com/wiki/Cauldron"},
            {"title": "Fermented Spider Eye", "url": "https://minecraft.fandom.com/wiki/Fermented_Spider_Eye"},
            {"title": "Blaze Powder", "url": "https://minecraft.fandom.com/wiki/Blaze_Powder"},
            {"title": "Nether Wart", "url": "https://minecraft.fandom.com/wiki/Nether_Wart"},
            {"title": "Glistering Melon", "url": "https://minecraft.fandom.com/wiki/Glistering_Melon"},
            {"title": "Brewing recipes", "url": "https://minecraft.fandom.com/wiki/Brewing/Recipes"}
        ],
        "Crafting": [
            {"title": "Crafting", "url": "https://minecraft.fandom.com/wiki/Crafting"},
            {"title": "Crafting Table", "url": "https://minecraft.fandom.com/wiki/Crafting_Table"},
            {"title": "Recipe", "url": "https://minecraft.fandom.com/wiki/Recipe"},
            {"title": "Recipe Book", "url": "https://minecraft.fandom.com/wiki/Recipe_Book"},
            {"title": "Crafting recipes", "url": "https://minecraft.fandom.com/wiki/Crafting/Recipes"},
            {"title": "Crafting/Complete list", "url": "https://minecraft.fandom.com/wiki/Crafting/Complete_list"}
        ]
    }
    
    # Get the list of pages for this category
    article_links = []
    if category_name in special_pages:
        for page in special_pages[category_name]:
            if page["url"] not in existing_urls:
                article_links.append(page)
    else:
        print(f"  No special handling defined for category: {category_name}")
        return existing_data or []
    
    # If no new articles to scrape, return existing data
    if not article_links and existing_data:
        print(f"  No new articles to scrape for {category_name}")
        return existing_data
    
    # Scrape each article
    articles = existing_data or []
    save_counter = 0
    save_frequency = 5  # Save after every 5 articles
    
    print(f"  Found {len(article_links)} new articles to scrape")
    
    # Use tqdm for progress monitoring
    for i, article in enumerate(tqdm(article_links, desc=f"  Scraping {category_name}", unit="article")):
        try:
            article_response = requests.get(article['url'])
            article_soup = BeautifulSoup(article_response.content, 'html.parser')
            
            # Get main content - updated selector for the new wiki structure
            content = article_soup.select_one('.mw-parser-output')
            if content:
                # Remove navigation elements
                for nav in content.select('.navbox, .toc, .infobox, .wikitable, .mw-editsection, .mw-headline'):
                    nav.decompose()
                
                # Improve paragraph handling by adding explicit newlines
                for p in content.find_all('p'):
                    # Add newlines after paragraphs to preserve structure
                    if p.next_sibling:
                        p.append('\n\n')
                
                # Handle lists better
                for ul in content.find_all(['ul', 'ol']):
                    # Add newlines before and after lists
                    if ul.previous_sibling:
                        ul.insert_before('\n')
                    if ul.next_sibling:
                        ul.append('\n')
                    
                    # Add newlines after list items
                    for li in ul.find_all('li'):
                        if li.next_sibling:
                            li.append('\n')
                
                # Handle headings better
                for heading in content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    # Add newlines before and after headings
                    if heading.previous_sibling:
                        heading.insert_before('\n\n')
                    if heading.next_sibling:
                        heading.append('\n\n')
                
                # Extract text
                text = content.get_text(separator=' ')
                
                # Clean the text content
                cleaned_text = clean_text(text)
                
                articles.append({
                    'title': article['title'],
                    'url': article['url'],
                    'content': cleaned_text,
                    'category': category_name
                })
                
                # Increment save counter
                save_counter += 1
                
                # Save progress incrementally
                if save_counter >= save_frequency:
                    save_data(articles, category_name)
                    save_counter = 0
            
            # Avoid overloading the server
            time.sleep(0.25)
        except Exception as e:
            tqdm.write(f"Error scraping {article['title']}: {e}")
            # Save on error to preserve progress
            save_data(articles, category_name)
    
    # Final save for this category
    save_data(articles, category_name)
    print(f"  Completed scraping {len(article_links)} new articles for {category_name}")
    print(f"  Total articles for {category_name}: {len(articles)}")
    
    return articles

# Function to clean existing data
def clean_existing_data(data):
    if not data:
        return data
    
    print("Cleaning existing data...")
    cleaned_count = 0
    for article in tqdm(data, desc="  Cleaning articles", unit="article"):
        if 'content' in article:
            old_content = article['content']
            article['content'] = clean_text(old_content)
            if old_content != article['content']:
                cleaned_count += 1
    
    print(f"  Cleaned {cleaned_count} articles that needed improvement")
    return data

# Main scraping function
def build_minecraft_dataset():
    # Categories to scrape - include all categories
    categories = ["Blocks", "Items", "Brewing", "Mechanics", "Mobs", "Crafting"]
    
    # Special categories that need direct page scraping instead of category pages
    special_categories = ["Brewing", "Crafting"]
    
    all_data = {}
    
    # Create directory
    os.makedirs('raw_data', exist_ok=True)
    
    # Scrape each category
    for category in tqdm(categories, desc="Categories", unit="category"):
        tqdm.write(f"\nProcessing category: {category}")
        
        # Load existing data if available
        existing_data = []
        json_path = f'raw_data/{category.lower()}.json'
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    existing_data = json.load(f)
                tqdm.write(f"  Loaded {len(existing_data)} existing articles for {category}")
                
                # Clean existing data
                existing_data = clean_existing_data(existing_data)
            except json.JSONDecodeError:
                tqdm.write(f"  Error loading existing data for {category}, starting fresh")
        
        # Scrape category with existing data to avoid duplicates
        try:
            if category in special_categories:
                articles = scrape_special_pages(category, existing_data=existing_data)
            else:
                articles = scrape_category(category, existing_data=existing_data)
            
            all_data[category] = articles
            
            # Final save for this category (already done in scrape_category)
            tqdm.write(f"  Completed {len(articles)} total articles for {category}")
        except Exception as e:
            tqdm.write(f"Error processing category {category}: {e}")
            # If we have existing data, use that
            if existing_data:
                all_data[category] = existing_data
                tqdm.write(f"  Using {len(existing_data)} existing articles for {category}")
            else:
                tqdm.write(f"  No data available for {category}")
    
    # Save combined data (mark as final)
    save_data([], "", is_final=True)
    
    # Count total articles
    total_articles = sum(len(articles) for articles in all_data.values())
    print(f"\nData scraping complete! Total articles: {total_articles}")


def remove_minecraft_earth():
    # Path to the JSON file
    input_file = "raw_data/all_minecraft_data.json"
    backup_file = "raw_data/all_minecraft_data_backup.json"
    output_file = "raw_data/all_minecraft_data.json"

    print(f"Loading JSON data from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Create a backup of the original file
    print(f"Creating backup at {backup_file}...")
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(data, f)
        
    print(f"Backup created successfully.")

    # Count total objects and objects to be removed
    total_objects = sum(len(category_items) for category_items in data.values())
    objects_to_remove = 0
    print(f"Found {total_objects} total objects across {len(data)} categories.")

    # Filter out objects with content starting with the specified string
    filtered_data = {}
    removed_by_category = {}

    for category, items in tqdm(data.items(), desc="Processing categories"):
        filtered_items = []
        category_removed = 0
        
        for item in items:
            content = item.get("content", "")
            if not content.startswith("Minecraft Earth was discontinued due to outdoor restrictions"):
                filtered_items.append(item)
            else:
                objects_to_remove += 1
                category_removed += 1
        
        filtered_data[category] = filtered_items
        removed_by_category[category] = category_removed

    # Save the filtered data
    print(f"Saving filtered data to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f)

    print(f"\nRemoved {objects_to_remove} objects out of {total_objects} total objects.")

    # Print breakdown by category
    print("\nBreakdown of removed objects by category:")
    for category, count in removed_by_category.items():
        if count > 0:
            print(f"  - {category}: {count} objects removed")

    print(f"\nFiltered data saved to {output_file}")


# Run the scraper
if __name__ == "__main__":
    build_minecraft_dataset()
    remove_minecraft_earth()
