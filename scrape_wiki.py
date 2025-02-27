import requests
from bs4 import BeautifulSoup
import json
import time
import os

# Function to scrape a Minecraft Wiki category
def scrape_category(category_name, max_pages=20):
    print(f"Scraping category: {category_name}")
    url = f"https://minecraft.fandom.com/wiki/Category:{category_name}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Get all pages in this category
    article_links = []
    for link in soup.select('.category-page__member-link'):
        article_links.append({
            'title': link.text.strip(),
            'url': 'https://minecraft.fandom.com' + link['href']
        })
        if len(article_links) >= max_pages:
            break
    
    # Scrape each article
    articles = []
    for i, article in enumerate(article_links):
        print(f"  Scraping {i+1}/{len(article_links)}: {article['title']}")
        try:
            article_response = requests.get(article['url'])
            article_soup = BeautifulSoup(article_response.content, 'html.parser')
            
            # Get main content
            content = article_soup.select_one('.mw-parser-output')
            if content:
                # Remove navigation elements
                for nav in content.select('.navbox, .toc'):
                    nav.decompose()
                
                # Extract text
                text = content.get_text(separator='\n')
                
                articles.append({
                    'title': article['title'],
                    'url': article['url'],
                    'content': text,
                    'category': category_name
                })
            
            # Avoid overloading the server
            time.sleep(1)
        except Exception as e:
            print(f"Error scraping {article['title']}: {e}")
    
    return articles

# Main scraping function
def build_minecraft_dataset():
    # Categories to scrape
    categories = ["Blocks", "Items", "Brewing", "Mechanics", "Mobs", "Crafting"]
    all_data = {}
    
    # Create directory
    os.makedirs('raw_data', exist_ok=True)
    
    # Scrape each category
    for category in categories:
        articles = scrape_category(category)
        all_data[category] = articles
        
        # Save data for this category
        with open(f'raw_data/{category.lower()}.json', 'w') as f:
            json.dump(articles, f, indent=2)
    
    # Save combined data
    with open('raw_data/all_minecraft_data.json', 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print("Data scraping complete!")

# Run the scraper
build_minecraft_dataset()
